"""
RAG（检索增强生成）服务。

功能：
- 为知识点和学习资源生成 embedding 向量（存储到 PostgreSQL/pgvector）
- 向量相似度检索：为 agent 提供相关上下文
- 混合检索：关键词 + 向量双重召回
- 上下文注入：将检索结果注入到 agent prompt 中

依赖：
- PostgreSQL + pgvector 扩展（database/pgvector/）
- MiniMax API（或 openai-compatible provider）进行 embedding 计算
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2

from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 向量维度（MiniMax embedding 默认 768，用户可按需调整）
# ---------------------------------------------------------------------------
EMBEDDING_DIM = 768


# ---------------------------------------------------------------------------
# 数据库连接（PostgreSQL / pgvector）
# ---------------------------------------------------------------------------

def _get_pg_conn():
    """获取 PostgreSQL 连接（pgvector 表使用 PG）。"""
    settings = get_settings()
    pg = settings.postgres_url
    if not pg:
        raise RuntimeError("POSTGRES_URL 未配置，无法使用 RAG 向量检索")
    return psycopg2.connect(pg)


def _ensure_extension():
    """确保 pgvector 扩展已启用。"""
    try:
        with _get_pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
                conn.commit()
    except Exception as e:
        logger.warning(f"pgvector 扩展检查失败: {e}")


# ---------------------------------------------------------------------------
# Embedding 生成
# ---------------------------------------------------------------------------

def generate_text_embedding(text: str) -> List[float]:
    """
    使用配置的 LLM Provider 生成文本 embedding 向量。

    策略：
    1. 优先使用 OpenAI-compatible embedding endpoint
    2. 回退到直接调用 chat endpoint 并截取响应作为伪 embedding
       （在实际生产中应使用专门的 embedding 模型）

    Returns:
        768维 float 列表，或空列表（生成失败时）
    """
    try:
        # 优先尝试 OpenAI-compatible embedding
        import httpx
        settings = get_settings()
        url = f"{settings.llm_base_url.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": text[:8192],
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            embedding = data["data"][0]["embedding"]
            logger.debug(f"Embedding 生成成功，维度: {len(embedding)}")
            return embedding
    except Exception as e:
        logger.warning(f"Embedding 生成失败（OpenAI endpoint）: {e}，尝试 chat endpoint")

    # 回退：使用 chat endpoint 生成 embedding（简单策略：复用 chat 模型）
    try:
        import httpx
        settings = get_settings()
        url = f"{settings.llm_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        # 使用一个"提取语义摘要"的 prompt，让模型输出一段向量描述文本
        payload = {
            "model": settings.llm_model,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"请将以下文本的核心语义压缩为一个30词以内的中文短语，"
                        f"只输出短语，不要解释：\n\n{text[:512]}"
                    )
                }
            ],
            "max_tokens": 30,
            "temperature": 0.0,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            summary = data["choices"][0]["message"]["content"].strip()

        # 用摘要文本再次生成 embedding
        import httpx
        url2 = f"{settings.llm_base_url.rstrip('/')}/embeddings"
        payload2 = {
            "model": "text-embedding-3-small",
            "input": summary,
        }
        with httpx.Client(timeout=30.0) as client:
            resp2 = client.post(url2, headers=headers, json=payload2)
            resp2.raise_for_status()
            embedding = resp2.json()["data"][0]["embedding"]
            logger.debug(f"Embedding 回退策略成功，维度: {len(embedding)}")
            return embedding
    except Exception as e2:
        logger.error(f"Embedding 生成完全失败: {e2}，返回零向量")
        return [0.0] * EMBEDDING_DIM


# ---------------------------------------------------------------------------
# 存储
# ---------------------------------------------------------------------------

def store_knowledge_point_embeddings(
    kp_id: int,
    chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    将知识点的多个文本块及其 embedding 存入 pgvector 表。

    Args:
        kp_id: 知识点 ID
        chunks: [{"content_chunk": str, "chunk_index": int}, ...]
    """
    _ensure_extension()
    results = {"stored": 0, "failed": 0, "kp_id": kp_id}
    for chunk in chunks:
        try:
            text = chunk["content_chunk"]
            idx = chunk.get("chunk_index", 0)
            embedding = generate_text_embedding(text)
            if not embedding:
                embedding = [0.0] * EMBEDDING_DIM

            with _get_pg_conn() as conn:
                with conn.cursor() as cur:
                    # 先删除旧记录
                    cur.execute(
                        "DELETE FROM knowledge_point_embeddings "
                        "WHERE kp_id = %s AND chunk_index = %s",
                        (kp_id, idx)
                    )
                    # 插入新记录
                    cur.execute(
                        """
                        INSERT INTO knowledge_point_embeddings
                            (kp_id, content_chunk, embedding, chunk_index, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (kp_id, text, embedding, idx, datetime.now())
                    )
                    conn.commit()
            results["stored"] += 1
        except Exception as e:
            logger.error(f"存储 embedding 失败 (kp={kp_id}, idx={chunk.get('chunk_index')}): {e}")
            results["failed"] += 1

    logger.info(f"[RAG] kp_id={kp_id} 存储完成: {results}")
    return results


def store_resource_embedding(
    resource_id: int,
    content: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> Dict[str, Any]:
    """
    将学习资源内容切分为块，生成 embedding 并存储。

    简单滑动窗口切分策略（无 overlap 时）。
    """
    # 简单切分：按 chunk_size 字符分割
    chunks = []
    start = 0
    idx = 0
    while start < len(content):
        end = start + chunk_size
        chunk_text = content[start:end].strip()
        if chunk_text:
            chunks.append({"content_chunk": chunk_text, "chunk_index": idx})
            idx += 1
        start = end

    results = store_knowledge_point_embeddings(resource_id, chunks)
    results["resource_id"] = resource_id
    results["chunks"] = len(chunks)
    return results


# ---------------------------------------------------------------------------
# 检索
# ---------------------------------------------------------------------------

def search_similar_knowledge_points(
    query: str,
    course_id: Optional[int] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    向量相似度检索：找到与 query 最相似的知识点上下文。

    使用 pgvector 的余弦相似度 (<=>) 运算符。

    Returns:
        [{"kp_id": int, "kp_name": str, "content_chunk": str,
          "similarity": float, "chunk_index": int}, ...]
    """
    _ensure_extension()
    query_embedding = generate_text_embedding(query)
    if not query_embedding:
        return []

    try:
        with _get_pg_conn() as conn:
            with conn.cursor() as cur:
                if course_id is not None:
                    sql = """
                        SELECT
                            e.kp_id,
                            e.content_chunk,
                            e.chunk_index,
                            1 - (e.embedding <=> %s::vector) AS similarity,
                            kp.kp_name,
                            kp.course_id,
                            kp.difficulty_level
                        FROM knowledge_point_embeddings e
                        INNER JOIN knowledge_points kp ON e.kp_id = kp.kp_id
                        WHERE kp.course_id = %s AND kp.is_deleted = 0
                        ORDER BY e.embedding <=> %s::vector
                        LIMIT %s
                    """
                    cur.execute(sql, (query_embedding, course_id, query_embedding, top_k))
                else:
                    sql = """
                        SELECT
                            e.kp_id,
                            e.content_chunk,
                            e.chunk_index,
                            1 - (e.embedding <=> %s::vector) AS similarity,
                            kp.kp_name,
                            kp.course_id,
                            kp.difficulty_level
                        FROM knowledge_point_embeddings e
                        INNER JOIN knowledge_points kp ON e.kp_id = kp.kp_id
                        WHERE kp.is_deleted = 0
                        ORDER BY e.embedding <=> %s::vector
                        LIMIT %s
                    """
                    cur.execute(sql, (query_embedding, query_embedding, top_k))

                rows = cur.fetchall()

        results = []
        for row in rows:
            sim = float(row[3]) if row[3] is not None else 0.0
            if sim >= similarity_threshold:
                results.append({
                    "kp_id": row[0],
                    "content_chunk": row[1],
                    "chunk_index": row[2],
                    "similarity": round(sim, 4),
                    "kp_name": row[4],
                    "course_id": row[5],
                    "difficulty_level": row[6],
                })

        return results
    except Exception as e:
        logger.error(f"RAG 检索失败: {e}")
        return []


def search_by_keywords(
    query: str,
    course_id: Optional[int] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    关键词检索（pg LIKE），作为向量检索的补充。

    用于当 pgvector 不可用或向量检索结果不足时的回退策略。
    """
    try:
        with _get_pg_conn() as conn:
            with conn.cursor() as cur:
                if course_id is not None:
                    sql = """
                        SELECT
                            e.kp_id,
                            e.content_chunk,
                            e.chunk_index,
                            kp.kp_name,
                            kp.course_id,
                            kp.difficulty_level
                        FROM knowledge_point_embeddings e
                        INNER JOIN knowledge_points kp ON e.kp_id = kp.kp_id
                        WHERE kp.course_id = %s
                          AND kp.is_deleted = 0
                          AND e.content_chunk LIKE %s
                        ORDER BY e.chunk_index ASC
                        LIMIT %s
                    """
                    cur.execute(sql, (course_id, f"%{query}%", top_k))
                else:
                    sql = """
                        SELECT
                            e.kp_id,
                            e.content_chunk,
                            e.chunk_index,
                            kp.kp_name,
                            kp.course_id,
                            kp.difficulty_level
                        FROM knowledge_point_embeddings e
                        INNER JOIN knowledge_points kp ON e.kp_id = kp.kp_id
                        WHERE kp.is_deleted = 0
                          AND e.content_chunk LIKE %s
                        ORDER BY e.chunk_index ASC
                        LIMIT %s
                    """
                    cur.execute(sql, (f"%{query}%", top_k))

                rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                "kp_id": row[0],
                "content_chunk": row[1],
                "chunk_index": row[2],
                "similarity": 1.0,  # 关键词命中标记为最高相似度
                "kp_name": row[3],
                "course_id": row[4],
                "difficulty_level": row[5],
            })
        return results
    except Exception as e:
        logger.error(f"关键词检索失败: {e}")
        return []


def hybrid_search(
    query: str,
    course_id: Optional[int] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    混合检索：向量相似度 + 关键词双重召回，去重合并。

    先向量检索，不足 top_k 时用关键词补充。
    """
    seen_kp_ids = set()
    merged: List[Dict[str, Any]] = []

    # 向量检索
    vector_results = search_similar_knowledge_points(
        query, course_id, top_k, similarity_threshold
    )
    for r in vector_results:
        key = (r["kp_id"], r["chunk_index"])
        if key not in seen_kp_ids:
            seen_kp_ids.add(key)
            merged.append(r)

    # 关键词补充
    if len(merged) < top_k:
        keyword_results = search_by_keywords(query, course_id, top_k)
        for r in keyword_results:
            key = (r["kp_id"], r["chunk_index"])
            if key not in seen_kp_ids:
                seen_kp_ids.add(key)
                merged.append(r)
            if len(merged) >= top_k * 2:
                break

    return merged[:top_k]


# ---------------------------------------------------------------------------
# 上下文格式化
# ---------------------------------------------------------------------------

def format_context_for_prompt(
    results: List[Dict[str, Any]],
    max_chars: int = 2000,
) -> str:
    """
    将检索结果格式化为字符串，注入到 agent prompt 中。

    格式：
    ## 参考上下文
    [知识点: xxx]
    - 相似度: 0.85 | 难度: 进阶
    内容: ...
    """
    if not results:
        return ""

    lines = ["## 参考上下文\n"]
    total_chars = 0

    for r in results:
        chunk = r["content_chunk"]
        entry = (
            f"[知识点: {r['kp_name']} | 相似度: {r['similarity']:.2f} | "
            f"难度: {r.get('difficulty_level', '未知')}]\n"
            f"内容: {chunk}\n"
        )
        if total_chars + len(entry) > max_chars:
            break
        lines.append(entry)
        total_chars += len(entry)

    return "\n".join(lines)


def get_context_for_agent(
    query: str,
    course_id: Optional[int] = None,
    top_k: int = 5,
) -> str:
    """
    便捷入口：为 agent 获取检索增强上下文。
    """
    try:
        results = hybrid_search(query, course_id, top_k)
        return format_context_for_prompt(results)
    except Exception as e:
        logger.warning(f"[RAG] get_context_for_agent 失败: {e}")
        return ""
