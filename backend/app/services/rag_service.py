"""
RAG Service — 对外统一的检索接口。

优先级：
1. 若配置了讯飞 ChatDoc（RAG_DOC_ID），优先走讯飞知识库
2. 否则使用本地 pgvector BM25 检索器
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        from app.rag import CourseMaterialRetriever
        _retriever = CourseMaterialRetriever()
    return _retriever


def _use_iflytek_rag() -> bool:
    """检查是否配置了讯飞 RAG。"""
    try:
        from app.config import get_settings
        s = get_settings()
        return bool(s.iflytek_doc_id and s.iflytek_app_id and s.iflytek_api_key)
    except Exception:
        return False


def get_context_for_agent(
    query: str,
    course_id: Optional[int] = None,
    kp_name: Optional[str] = None,
    top_k: int = 3,
) -> str:
    """
    获取 RAG 上下文，用于注入 LLM Agent 的 prompt。

    优先级：
    1. 讯飞 ChatDoc（若已配置 IFLYTEK_DOC_ID）
    2. 本地 pgvector BM25 检索器

    Args:
        query: 检索查询（通常为薄弱知识点名称拼接）
        course_id: 课程 ID（目前支持 course_id=1，即数据库系统原理）
        kp_name: 可选，限定在特定知识点范围内检索
        top_k: 返回的片段数量

    Returns:
        格式化后的上下文字符串，可直接注入 prompt。
        失败时返回空字符串。
    """
    # 优先讯飞 RAG
    if _use_iflytek_rag():
        return _iflytek_rag_context(query, course_id, kp_name, top_k)

    # 回退到本地 pgvector BM25
    try:
        retriever = _get_retriever()
        chunks = retriever.search(query=query, top_k=top_k * 3, kp_name_filter=kp_name)
        if course_id is not None:
            chunks = [c for c in chunks if c.get("course_id") == course_id]
        chunks = chunks[:top_k]
        if not chunks:
            logger.info("[RAG] local BM25 query returned no results")
            return ""
        context = retriever.format_context(chunks)
        logger.info("[RAG] local BM25 returned %s fragments", len(chunks))
        return context
    except Exception as e:
        logger.warning("[RAG] 本地检索异常，回退到空字符串 (%s)", type(e).__name__)
        return ""


def _iflytek_rag_context(
    query: str,
    course_id: Optional[int],
    kp_name: Optional[str],
    top_k: int,
) -> str:
    """讯飞 ChatDoc RAG 检索（优先）。"""
    try:
        from app.config import get_settings
        from app.services.iflytek_rag_service import chatdoc_retrieve
        s = get_settings()

        # 若有 kp_name 限制，拼接到 query
        search_query = query
        if kp_name:
            search_query = f"{kp_name}：{query}"

        result = chatdoc_retrieve(
            query=search_query,
            doc_id=s.iflytek_doc_id,
            app_id=s.iflytek_app_id,
            api_key=s.iflytek_api_key,
            api_secret=s.iflytek_api_secret,
            top_k=top_k,
        )
        if result:
            logger.info("[RAG] IFlyTek ChatDoc returned %s hundred characters", len(result) // 100)
        else:
            logger.info("[RAG] IFlyTek ChatDoc returned no results; using local BM25")
            # 无结果时回退到本地
            return _local_bm25_fallback(query, course_id, kp_name, top_k)
        return result
    except Exception as e:
        logger.warning("[RAG] IFlyTek ChatDoc 检索失败，回退到本地 (%s)", type(e).__name__)
        return _local_bm25_fallback(query, course_id, kp_name, top_k)


def _local_bm25_fallback(
    query: str,
    course_id: Optional[int],
    kp_name: Optional[str],
    top_k: int,
) -> str:
    """本地 BM25 fallback。"""
    try:
        retriever = _get_retriever()
        chunks = retriever.search(query=query, top_k=top_k, kp_name_filter=kp_name)
        if course_id is not None:
            chunks = [c for c in chunks if c.get("course_id") == course_id]
        chunks = chunks[:top_k]
        if not chunks:
            return ""
        context = retriever.format_context(chunks)
        logger.info("[RAG] BM25 fallback returned %s fragments", len(chunks))
        return context
    except Exception as e:
        logger.warning("[RAG] BM25 fallback 失败 (%s)", type(e).__name__)
        return ""


def search_materials(
    query: str,
    kp_name: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    直接检索课程文档片段，返回结构化结果。

    可用于：前端知识库浏览、证据来源展示。
    """
    try:
        retriever = _get_retriever()
        return retriever.search(query=query, top_k=top_k, kp_name_filter=kp_name)
    except Exception as e:
        logger.warning("[RAG] 检索异常 (%s)", type(e).__name__)
        return []
