"""
课程知识库检索器。

轻量实现：基于关键词权重（TF-IDF-like）的 BM25 检索，无需外部 embedding API。

用法：
    retriever = CourseMaterialRetriever()
    results = retriever.search(query="SQL多表连接内连接外连接", top_k=3, kp_name_filter=None)
"""

import re
import math
from typing import List, Dict, Any, Optional
from .document_loader import get_all_chunks, COURSE_MATERIALS


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
    """

    STOP_WORDS = {
        "的", "了", "在", "是", "我", "有", "和", "就",
        "不", "人", "都", "一", "一个", "上", "也", "很",
        "到", "说", "要", "去", "你", "会", "着", "没有",
        "看", "好", "自己", "这", "那", "它", "什么",
    }

    def __init__(self, k: float = 1.5, b: float = 0.75):
        """
        Args:
            k: BM25 参数，控制词频饱和速度
            b: BM25 参数，控制文档长度归一化
        """
        self.k = k
        self.b = b
        self._index: Dict[str, List[Dict[str, Any]]] = {}
        self._avgdl = 0.0
        self._N = 0
        self._doc_freqs: Dict[str, int] = {}  # term -> doc frequency
        self._build_index()

    # ------------------------------------------------------------------
    # 索引构建
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        """简单中文分词：正则提取词 + 过滤停用词。"""
        words = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9]+", text.lower())
        return [w for w in words if w not in self.STOP_WORDS and len(w) >= 2]

    def _build_index(self) -> None:
        """构建倒排索引和 BM25 参数。"""
        all_tokens: List[List[str]] = []
        self._doc_freqs.clear()

        for chunk in COURSE_MATERIALS:
            text = f"{chunk['title']} {chunk['kp_name']} {chunk['content']}"
            tokens = self._tokenize(text)
            all_tokens.append(tokens)

            for term in set(tokens):
                self._doc_freqs[term] = self._doc_freqs.get(term, 0) + 1

        self._N = len(all_tokens)
        if self._N == 0:
            return

        total_len = sum(len(t) for t in all_tokens)
        self._avgdl = total_len / self._N

        for i, chunk in enumerate(COURSE_MATERIALS):
            tokens = all_tokens[i]
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self._index[chunk["chunk_id"]] = {
                "tokens": tokens,
                "tf": tf,
                "dl": len(tokens),
                "chunk": chunk,
            }

    # ------------------------------------------------------------------
    # BM25 核心
    # ------------------------------------------------------------------

    def _bm25_score(self, query_tokens: List[str], doc_id: str) -> float:
        """计算单个文档对查询的 BM25 得分。"""
        if doc_id not in self._index:
            return 0.0
        entry = self._index[doc_id]
        dl = entry["dl"]
        tf_map = entry["tf"]
        score = 0.0
        for term in query_tokens:
            if term not in tf_map:
                continue
            tf = tf_map[term]
            df = self._doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log((self._N - df + 0.5) / (df + 0.5) + 1)
            tf_component = (tf * (self.k + 1)) / (tf + self.k * (1 - self.b + self.b * dl / self._avgdl))
            score += idf * tf_component
        return score

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
        if not query or not query.strip():
            return []

        query_tokens = self._tokenize(query)

        # 构建候选集（按知识点过滤）
        candidate_ids = [
            doc_id for doc_id, entry in self._index.items()
            if kp_name_filter is None
            or kp_name_filter in entry["chunk"].get("kp_name", "")
        ]

        # 计算 BM25 得分
        scored = []
        for doc_id in candidate_ids:
            score = self._bm25_score(query_tokens, doc_id)
            if score > 0:
                chunk = self._index[doc_id]["chunk"].copy()
                chunk["bm25_score"] = round(score, 4)
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

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
