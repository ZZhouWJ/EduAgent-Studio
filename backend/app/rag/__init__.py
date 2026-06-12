"""
RAG 模块 — 课程知识库检索。

架构：
- document_loader: 加载课程 Markdown 文档
- retriever    : 轻量 BM25 检索（无需外部 embedding API）

依赖关系：
  diagnosis_agent._retrieve_rag_context() → retriever.search() → document_loader.get_chunks()
"""

from .retriever import CourseMaterialRetriever

__all__ = ["CourseMaterialRetriever"]
