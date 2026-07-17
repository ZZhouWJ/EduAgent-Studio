"""
课程知识库检索器。

轻量实现：基于关键词权重（TF-IDF-like）的 BM25 检索，无需外部 embedding API。

优先查询数据库 course_material_chunks 表，为空时 fallback 到内置 COURSE_MATERIALS。

用法：
    retriever = CourseMaterialRetriever()
    results = retriever.search(query="SQL多表连接内连接外连接", top_k=3, kp_name_filter=None)
"""

import logging
import re
import math
from typing import List, Dict, Any, Optional

from app.database import get_db_cursor
from .document_loader import get_all_chunks, COURSE_MATERIALS

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> List[str]:
    """轻量中文分词：中文字符 n-gram + 英文/数字词元。"""
    STOP_WORDS = {
        "的", "了", "在", "是", "我", "有", "和", "就",
        "不", "人", "都", "一", "一个", "上", "也", "很",
        "到", "说", "要", "去", "你", "会", "着", "没有",
        "看", "好", "自己", "这", "那", "它", "什么",
    }
    tokens: List[str] = []
    segments = re.findall(r"[一-鿿]+|[a-zA-Z0-9]+", text.lower())
    for segment in segments:
        if re.fullmatch(r"[一-鿿]+", segment):
            if len(segment) == 1:
                if segment not in STOP_WORDS:
                    tokens.append(segment)
                continue

            # 不依赖外部分词库，同时兼容“事务与 ACID”和“事务隔离”这类表述差异。
            for size in range(2, min(4, len(segment)) + 1):
                tokens.extend(
                    segment[index:index + size]
                    for index in range(len(segment) - size + 1)
                )
        elif len(segment) >= 2 and segment not in STOP_WORDS:
            tokens.append(segment)
    return tokens


def _search_db_chunks(
    course_id: int,
    query: str,
    kp_id: Optional[int] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    从数据库 course_material_chunks 表检索。

    Returns:
        按 BM25 得分降序排列的 chunks
    """
    # 先获取该课程的所有 chunks
    sql = """
        SELECT
            chunk_id,
            material_id,
            course_id,
            kp_id,
            title,
            content,
            source_page,
            source_paragraph,
            bm25_terms,
            chunk_index
        FROM course_material_chunks
        WHERE course_id = %s AND is_deleted = 0
    """
    params: List[Any] = [course_id]

    if kp_id is not None:
        sql += " AND kp_id = %s"
        params.append(kp_id)

    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
    except Exception as e:
        logger.warning("查询数据库 chunks 失败 (%s)", type(e).__name__)
        return []

    if not rows:
        return []

    # 构建 BM25 索引
    index: Dict[str, Dict[str, Any]] = {}
    doc_freqs: Dict[str, int] = {}
    all_tokens: List[List[str]] = []

    for row in rows:
        text = f"{row.get('title', '')} {row.get('bm25_terms', '')} {row.get('content', '')}"
        tokens = _tokenize(text)
        all_tokens.append(tokens)

        for term in set(tokens):
            doc_freqs[term] = doc_freqs.get(term, 0) + 1

    N = len(all_tokens)
    avgdl = sum(len(t) for t in all_tokens) / N if N > 0 else 0

    for i, row in enumerate(rows):
        chunk_id = str(row["chunk_id"])
        tokens = all_tokens[i]
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        index[chunk_id] = {
            "tokens": tokens,
            "tf": tf,
            "dl": len(tokens),
        }

    # 分词查询
    query_tokens = _tokenize(query)
    k = 1.5
    b = 0.75

    # 计算每个文档的 BM25 得分
    scored = []
    for row in rows:
        chunk_id = str(row["chunk_id"])
        if chunk_id not in index:
            continue

        entry = index[chunk_id]
        tf_map = entry["tf"]
        dl = entry["dl"]

        score = 0.0
        for term in query_tokens:
            if term not in tf_map:
                continue
            tf_val = tf_map[term]
            df = doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            tf_component = (tf_val * (k + 1)) / (tf_val + k * (1 - b + b * dl / avgdl))
            score += idf * tf_component

        if score > 0:
            result = {
                "chunk_id": row["chunk_id"],
                "material_id": row["material_id"],
                "course_id": row["course_id"],
                "kp_id": row["kp_id"],
                "title": row["title"],
                "content": row["content"],
                "source_page": row["source_page"],
                "source_paragraph": row["source_paragraph"],
                "bm25_score": round(score, 4),
                "source": f"DB chunk #{row['chunk_id']}",
                "kp_name": "",
            }
            scored.append((score, result))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]


def _search_static_chunks(
    query: str,
    top_k: int = 3,
    kp_name_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    从内置 COURSE_MATERIALS 检索（fallback）。

    Returns:
        按 BM25 得分降序排列的 chunks
    """
    all_chunks = get_all_chunks()
    if not all_chunks:
        return []

    # 构建索引
    index: Dict[str, Dict[str, Any]] = {}
    doc_freqs: Dict[str, int] = {}
    all_tokens: List[List[str]] = []

    for chunk in all_chunks:
        text = f"{chunk['title']} {chunk.get('kp_name', '')} {chunk['content']}"
        tokens = _tokenize(text)
        all_tokens.append(tokens)

        for term in set(tokens):
            doc_freqs[term] = doc_freqs.get(term, 0) + 1

    N = len(all_tokens)
    avgdl = sum(len(t) for t in all_tokens) / N if N > 0 else 0
    k = 1.5
    b = 0.75

    for i, chunk in enumerate(all_chunks):
        tokens = all_tokens[i]
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        index[chunk["chunk_id"]] = {
            "tokens": tokens,
            "tf": tf,
            "dl": len(tokens),
            "chunk": chunk,
        }

    query_tokens = _tokenize(query)

    # 构建候选集（按知识点过滤）
    candidate_ids = [
        doc_id for doc_id, entry in index.items()
        if kp_name_filter is None
        or kp_name_filter in entry["chunk"].get("kp_name", "")
    ]

    scored = []
    for doc_id in candidate_ids:
        entry = index[doc_id]
        tf_map = entry["tf"]
        dl = entry["dl"]

        score = 0.0
        for term in query_tokens:
            if term not in tf_map:
                continue
            tf_val = tf_map[term]
            df = doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            tf_component = (tf_val * (k + 1)) / (tf_val + k * (1 - b + b * dl / avgdl))
            score += idf * tf_component

        if score > 0:
            chunk = entry["chunk"].copy()
            chunk["bm25_score"] = round(score, 4)
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def search_knowledge(
    query: str,
    course_id: int,
    top_k: int = 3,
    kp_id: Optional[int] = None,
    kp_name_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    检索最相关的课程文档片段。

    优先从数据库 course_material_chunks 表检索；
    数据库为空时 fallback 到内置 COURSE_MATERIALS。

    Args:
        query: 自然语言查询（如 "SQL多表连接 内连接 左连接"）
        course_id: 课程 ID
        top_k: 返回的最相关片段数量
        kp_id: 可选，限定知识点 ID（仅限数据库检索）
        kp_name_filter: 可选，限定知识点名称（仅限静态检索）

    Returns:
        按 BM25 得分降序排列的片段列表
    """
    if not query or not query.strip():
        return []

    # 优先查数据库
    db_results = _search_db_chunks(course_id, query, kp_id=kp_id, limit=top_k)

    if db_results:
        logger.debug("数据库检索返回 %d 条结果", len(db_results))
        return db_results

    # Fallback 到静态 COURSE_MATERIALS
    logger.debug("数据库为空，fallback 到静态 COURSE_MATERIALS")
    return _search_static_chunks(query, top_k=top_k, kp_name_filter=kp_name_filter)


class CourseMaterialRetriever:
    """
    轻量 BM25 检索器。

    原理：对文档片段和查询都进行中文分词，计算 TF-IDF 权重，
    用 BM25 公式对每个文档片段打分，返回 Top-K 最相关片段。

    优势：
    - 不依赖外部 embedding API
    - 无需 pgvector/向量数据库
    - 可按知识点（kp_name）过滤
    - 轻量、快速，适合 Demo

    注意：此类保持向后兼容。新代码建议使用 search_knowledge 函数。
    """

    def __init__(self, k: float = 1.5, b: float = 0.75):
        """
        Args:
            k: BM25 参数，控制词频饱和速度
            b: BM25 参数，控制文档长度归一化
        """
        self.k = k
        self.b = b

    def search(
        self,
        query: str,
        top_k: int = 3,
        kp_name_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        检索最相关的课程文档片段。

        Args:
            query: 自然语言查询（如 "SQL多表连接 内连接 左连接"）
            top_k: 返回的最相关片段数量
            kp_name_filter: 可选，限定知识点名称（如 "事务隔离级别"）

        Returns:
            按 BM25 得分降序排列的片段列表
        """
        return _search_static_chunks(query, top_k=top_k, kp_name_filter=kp_name_filter)

    def search_by_kp(self, kp_name: str, query: str = "", top_k: int = 2) -> List[Dict[str, Any]]:
        """按知识点检索，支持额外查询过滤。"""
        return self.search(query=query or kp_name, top_k=top_k, kp_name_filter=kp_name)

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        将检索结果格式化为 LLM prompt 可用的上下文文本。

        格式：
        ## [chunk_id] 来源：xxx
        知识点：xxx
        内容摘要：
        ...
        ---
        """
        if not chunks:
            return "（未检索到相关课程知识库文档）"
        lines = []
        for i, chunk in enumerate(chunks, 1):
            score_note = f"[BM25={chunk.get('bm25_score', 0):.2f}]" if "bm25_score" in chunk else ""
            lines.append(f"## 参考文档 {i} {score_note}")
            lines.append(f"来源：{chunk.get('source', '未知')}")
            lines.append(f"知识点：{chunk.get('kp_name', '')}")
            lines.append(f"标题：{chunk.get('title', '')}")
            lines.append(f"内容：\n{chunk.get('content', '')}")
            lines.append("---")
        return "\n".join(lines)
