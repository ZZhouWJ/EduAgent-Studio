"""
RAG Service — 对外统一的检索接口。

将轻量 BM25 检索器封装为 service 层，供 diagnosis_agent 等调用。
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


def get_context_for_agent(
    query: str,
    course_id: Optional[int] = None,
    kp_name: Optional[str] = None,
    top_k: int = 3,
) -> str:
    """
    获取 RAG 上下文，用于注入 LLM Agent 的 prompt。

    Args:
        query: 检索查询（通常为薄弱知识点名称拼接）
        course_id: 课程 ID（目前支持 course_id=1，即数据库系统原理）
        kp_name: 可选，限定在特定知识点范围内检索
        top_k: 返回的片段数量

    Returns:
        格式化后的上下文字符串，可直接注入 prompt。
        失败时返回空字符串。
    """
    try:
        retriever = _get_retriever()
        chunks = retriever.search(query=query, top_k=top_k * 3, kp_name_filter=kp_name)
        # 按 course_id 过滤
        if course_id is not None:
            chunks = [c for c in chunks if c.get("course_id") == course_id]
        chunks = chunks[:top_k]
        if not chunks:
            logger.info(f"[RAG] 检索 query='{query}' 无结果")
            return ""
        context = retriever.format_context(chunks)
        logger.info(f"[RAG] 检索 query='{query}' 返回 {len(chunks)} 个片段")
        return context
    except Exception as e:
        logger.warning(f"[RAG] 检索异常，回退到空字符串: {e}")
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
        logger.warning(f"[RAG] 检索异常: {e}")
        return []
