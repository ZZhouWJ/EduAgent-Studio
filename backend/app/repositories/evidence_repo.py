"""
证据链路 Repository 层。

Tables:
- kp_chunk_links: link_id, chunk_id, kp_id, match_method, relevance_score, status, verified_by, verified_at, match_version, created_at
- resource_evidence_links: link_id, resource_id, chunk_id, kp_id, quote_text, relevance_score, usage_type, verified_status, verified_by, verified_at, source_page, source_paragraph, created_at
"""

import math
import re
from typing import Any, Dict, List, Optional

from app.database import get_db_cursor


class EvidenceRepository:
    """证据链路数据访问层。"""

    BM25_K = 1.5
    BM25_B = 0.75

    # ==========================================================
    # kp_chunk_links 操作
    # ==========================================================

    def upsert_kp_chunk_links(
        self,
        links: List[Dict[str, Any]],
    ) -> int:
        """
        批量插入或更新 kp_chunk_links。

        Args:
            links: [{"chunk_id": int, "kp_id": int, "match_method": str,
                     "relevance_score": float, "status": str, "match_version": int}, ...]

        Returns:
            插入/更新数量
        """
        if not links:
            return 0

        sql = """
            INSERT INTO kp_chunk_links
                (chunk_id, kp_id, match_method, relevance_score, status, match_version)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                match_method = VALUES(match_method),
                relevance_score = VALUES(relevance_score),
                status = VALUES(status),
                match_version = VALUES(match_version)
        """
        with get_db_cursor() as cursor:
            for link in links:
                cursor.execute(sql, (
                    link["chunk_id"],
                    link["kp_id"],
                    link["match_method"],
                    link["relevance_score"],
                    link["status"],
                    link["match_version"],
                ))
            return len(links)

    def get_confirmed_kp_chunk_links(
        self,
        kp_ids: List[int],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        获取已确认的 kp-chunk 关联。

        Args:
            kp_ids: 知识点 ID 列表
            limit: 每个 kp 最多返回多少 chunks

        Returns:
            chunks 列表（含关联信息）
        """
        if not kp_ids:
            return []

        placeholders = ",".join(["%s"] * len(kp_ids))
        sql = f"""
            SELECT
                l.link_id,
                l.chunk_id,
                l.kp_id,
                l.match_method,
                l.relevance_score,
                l.status,
                l.match_version,
                c.title,
                c.content,
                c.source_page,
                c.source_paragraph,
                c.chunk_index,
                c.bm25_terms,
                c.material_id,
                m.filename
            FROM kp_chunk_links l
            JOIN course_material_chunks c ON l.chunk_id = c.chunk_id AND c.is_deleted = 0
            JOIN course_materials m ON c.material_id = m.material_id AND m.is_deleted = 0
            WHERE l.kp_id IN ({placeholders})
              AND l.status = 'confirmed'
            ORDER BY l.relevance_score DESC
        """
        params = kp_ids
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        result = []
        seen_chunks = set()
        kp_count: Dict[int, int] = {}

        for row in rows:
            kp_id = row["kp_id"]
            chunk_id = row["chunk_id"]

            # 每个 kp 限制返回数量
            if kp_count.get(kp_id, 0) >= limit:
                continue

            if chunk_id in seen_chunks:
                continue

            seen_chunks.add(chunk_id)
            kp_count[kp_id] = kp_count.get(kp_id, 0) + 1

            result.append({
                "link_id": row["link_id"],
                "chunk_id": chunk_id,
                "kp_id": kp_id,
                "match_method": row["match_method"],
                "relevance_score": float(row["relevance_score"]),
                "status": row["status"],
                "match_version": row["match_version"],
                "title": row["title"],
                "content": row["content"],
                "source_page": row["source_page"],
                "source_paragraph": row["source_paragraph"],
                "chunk_index": row["chunk_index"],
                "bm25_terms": row["bm25_terms"],
                "material_id": row["material_id"],
                "filename": row["filename"],
            })

        return result

    def get_pending_kp_chunk_links(
        self,
        course_id: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取待审核的 kp-chunk 匹配（视图 v_pending_kp_chunk_links）。

        Args:
            course_id: 可选，限定课程
            limit: 返回数量

        Returns:
            待审核匹配列表
        """
        if course_id is not None:
            sql = """
                SELECT * FROM v_pending_kp_chunk_links
                WHERE material_course_id = %s
                ORDER BY relevance_score DESC
                LIMIT %s
            """
            params = (course_id, limit)
        else:
            sql = """
                SELECT * FROM v_pending_kp_chunk_links
                ORDER BY relevance_score DESC
                LIMIT %s
            """
            params = (limit,)

        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def verify_kp_chunk_link(
        self,
        link_id: int,
        status: str,
        verified_by: int,
    ) -> bool:
        """
        审核（确认/拒绝）一条 kp-chunk 匹配。

        Args:
            link_id: 关联记录 ID
            status: 'confirmed' 或 'rejected'
            verified_by: 审核教师 ID

        Returns:
            是否更新成功
        """
        sql = """
            UPDATE kp_chunk_links
            SET status = %s, verified_by = %s, verified_at = NOW()
            WHERE link_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (status, verified_by, link_id))
            return cursor.rowcount > 0

    def delete_kp_chunk_links_by_material(self, material_id: int) -> int:
        """
        删除某资料的所有 kp_chunk_links 关联。

        Args:
            material_id: 资料 ID

        Returns:
            删除数量
        """
        sql = """
            DELETE l FROM kp_chunk_links l
            JOIN course_material_chunks c ON l.chunk_id = c.chunk_id
            WHERE c.material_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (material_id,))
            return cursor.rowcount

    def get_kps_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        """
        获取课程的所有知识点。

        Args:
            course_id: 课程 ID

        Returns:
            知识点列表
        """
        sql = """
            SELECT
                kp_id,
                course_id,
                kp_name,
                kp_code,
                parent_kp_id,
                difficulty_level,
                description
            FROM knowledge_points
            WHERE course_id = %s AND is_deleted = 0
            ORDER BY kp_code
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (course_id,))
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_kp_by_id(self, kp_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个知识点。

        Args:
            kp_id: 知识点 ID

        Returns:
            知识点详情
        """
        sql = """
            SELECT
                kp_id,
                course_id,
                kp_name,
                kp_code,
                parent_kp_id,
                difficulty_level,
                description
            FROM knowledge_points
            WHERE kp_id = %s AND is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (kp_id,))
            row = cursor.fetchone()

        return dict(row) if row else None

    # ==========================================================
    # resource_evidence_links 操作
    # ==========================================================

    def insert_resource_evidence_links(
        self,
        links: List[Dict[str, Any]],
    ) -> int:
        """
        批量插入资源-证据关联。

        Args:
            links: [{
                "resource_id": int,
                "chunk_id": int,
                "kp_id": int,
                "quote_text": str,
                "relevance_score": float,
                "usage_type": str,
                "source_page": int | None,
                "source_paragraph": int | None,
            }, ...]

        Returns:
            插入数量
        """
        if not links:
            return 0

        sql = """
            INSERT INTO resource_evidence_links
                (resource_id, chunk_id, kp_id, quote_text, relevance_score, usage_type, source_page, source_paragraph)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        with get_db_cursor() as cursor:
            for link in links:
                cursor.execute(sql, (
                    link["resource_id"],
                    link["chunk_id"],
                    link["kp_id"],
                    link["quote_text"],
                    link["relevance_score"],
                    link["usage_type"],
                    link.get("source_page"),
                    link.get("source_paragraph"),
                ))
            return len(links)

    def get_evidence_by_resource(
        self,
        resource_id: int,
    ) -> List[Dict[str, Any]]:
        """
        获取某资源的所有证据关联。

        Args:
            resource_id: 资源 ID

        Returns:
            证据列表
        """
        sql = """
            SELECT
                rel.link_id,
                rel.resource_id,
                rel.chunk_id,
                rel.kp_id,
                rel.quote_text,
                rel.relevance_score,
                rel.usage_type,
                rel.verified_status,
                rel.verified_by,
                rel.verified_at,
                rel.source_page,
                rel.source_paragraph,
                rel.created_at,
                kp.kp_name,
                c.title AS chunk_title,
                c.content AS chunk_content,
                m.filename AS material_filename
            FROM resource_evidence_links rel
            JOIN knowledge_points kp ON rel.kp_id = kp.kp_id AND kp.is_deleted = 0
            JOIN course_material_chunks c ON rel.chunk_id = c.chunk_id AND c.is_deleted = 0
            JOIN course_materials m ON c.material_id = m.material_id AND m.is_deleted = 0
            WHERE rel.resource_id = %s
            ORDER BY rel.relevance_score DESC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (resource_id,))
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def verify_resource_evidence_link(
        self,
        link_id: int,
        status: str,
        verified_by: int,
    ) -> bool:
        """
        审核（确认/拒绝/替换）一条资源证据。

        Args:
            link_id: 证据关联 ID
            status: 'verified' / 'rejected' / 'replaced'
            verified_by: 审核教师 ID

        Returns:
            是否更新成功
        """
        sql = """
            UPDATE resource_evidence_links
            SET verified_status = %s, verified_by = %s, verified_at = NOW()
            WHERE link_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (status, verified_by, link_id))
            return cursor.rowcount > 0

    def update_evidence_quote(
        self,
        link_id: int,
        new_quote_text: str,
        new_chunk_id: int,
        new_relevance_score: float,
    ) -> bool:
        """
        替换证据引用的原文片段（教师审核时可能替换证据）。

        Args:
            link_id: 证据关联 ID
            new_quote_text: 新的引用文本
            new_chunk_id: 新的 chunk ID
            new_relevance_score: 新的相关度分数

        Returns:
            是否更新成功
        """
        sql = """
            UPDATE resource_evidence_links
            SET quote_text = %s,
                chunk_id = %s,
                relevance_score = %s,
                verified_status = 'pending',
                verified_by = NULL,
                verified_at = NULL
            WHERE link_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (new_quote_text, new_chunk_id, new_relevance_score, link_id))
            return cursor.rowcount > 0

    def delete_evidence_by_resource(self, resource_id: int) -> int:
        """
        删除某资源的所有证据关联（软删除标记为 replaced）。

        Args:
            resource_id: 资源 ID

        Returns:
            更新数量
        """
        sql = """
            UPDATE resource_evidence_links
            SET verified_status = 'replaced'
            WHERE resource_id = %s AND verified_status != 'replaced'
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (resource_id,))
            return cursor.rowcount

    def get_pending_evidence_for_review(
        self,
        course_id: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取待审核的资源证据。

        Args:
            course_id: 可选，限定课程
            limit: 返回数量

        Returns:
            待审核证据列表
        """
        if course_id is not None:
            sql = """
                SELECT
                    rel.link_id,
                    rel.resource_id,
                    rr.resource_title,
                    rr.resource_type,
                    kp.kp_name,
                    c.filename AS material_filename,
                    rel.quote_text,
                    rel.usage_type,
                    rel.relevance_score,
                    rel.verified_status,
                    rel.created_at
                FROM resource_evidence_links rel
                JOIN learning_resources rr ON rel.resource_id = rr.resource_id AND rr.is_deleted = 0
                JOIN knowledge_points kp ON rel.kp_id = kp.kp_id AND kp.is_deleted = 0
                JOIN course_material_chunks cc ON rel.chunk_id = cc.chunk_id AND cc.is_deleted = 0
                JOIN course_materials c ON cc.material_id = c.material_id AND c.is_deleted = 0
                WHERE rel.verified_status = 'pending'
                  AND rr.course_id = %s
                ORDER BY rel.relevance_score DESC
                LIMIT %s
            """
            params = (course_id, limit)
        else:
            sql = """
                SELECT
                    rel.link_id,
                    rel.resource_id,
                    rr.resource_title,
                    rr.resource_type,
                    kp.kp_name,
                    c.filename AS material_filename,
                    rel.quote_text,
                    rel.usage_type,
                    rel.relevance_score,
                    rel.verified_status,
                    rel.created_at
                FROM resource_evidence_links rel
                JOIN learning_resources rr ON rel.resource_id = rr.resource_id AND rr.is_deleted = 0
                JOIN knowledge_points kp ON rel.kp_id = kp.kp_id AND kp.is_deleted = 0
                JOIN course_material_chunks cc ON rel.chunk_id = cc.chunk_id AND cc.is_deleted = 0
                JOIN course_materials c ON cc.material_id = c.material_id AND c.is_deleted = 0
                WHERE rel.verified_status = 'pending'
                ORDER BY rel.relevance_score DESC
                LIMIT %s
            """
            params = (limit,)

        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # ==========================================================
    # BM25 辅助方法
    # ==========================================================

    def _tokenize(self, text: str) -> List[str]:
        """简单中文分词。"""
        STOP_WORDS = {
            "的", "了", "在", "是", "我", "有", "和", "就",
            "不", "人", "都", "一", "一个", "上", "也", "很",
            "到", "说", "要", "去", "你", "会", "着", "没有",
            "看", "好", "自己", "这", "那", "它", "什么",
        }
        words = re.findall(r"[一-鿿]+|[a-zA-Z0-9]+", text.lower())
        return [w for w in words if w not in STOP_WORDS and len(w) >= 2]

    def match_kps_to_chunks(
        self,
        chunks: List[Dict[str, Any]],
        kps: List[Dict[str, Any]],
        match_version: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        用 BM25 将 chunks 与同课程的 knowledge_points 做匹配。

        Args:
            chunks: [{"chunk_id": int, "bm25_terms": str, "content": str}, ...]
            kps: [{"kp_id": int, "kp_name": str, "description": str}, ...]
            match_version: 当前匹配版本号

        Returns:
            kp_chunk_links 记录列表
        """
        if not chunks or not kps:
            return []

        # 构建知识点的 BM25 索引（用 kp_name + description 分词）
        kp_texts = [
            f"{kp.get('kp_name', '')} {kp.get('description', '')}"
            for kp in kps
        ]
        kp_tokenized = [self._tokenize(t) for t in kp_texts]

        links = []
        for chunk in chunks:
            chunk_terms = self._tokenize(chunk.get("bm25_terms", ""))
            if not chunk_terms:
                # fallback：用 content 前 200 字分词
                chunk_terms = self._tokenize(chunk.get("content", "")[:200])

            if not chunk_terms:
                continue

            # 计算每个 kp 的 BM25 得分
            kp_doc_freqs: Dict[str, int] = {}
            for tokens in kp_tokenized:
                for t in set(tokens):
                    kp_doc_freqs[t] = kp_doc_freqs.get(t, 0) + 1

            N = len(kps)
            avgdl = sum(len(t) for t in kp_tokenized) / N if N > 0 else 0

            scored_kps = []
            for idx, kp_tokens in enumerate(kp_tokenized):
                if not kp_tokens:
                    continue
                tf_map: Dict[str, int] = {}
                for t in kp_tokens:
                    tf_map[t] = tf_map.get(t, 0) + 1

                score = 0.0
                for term in chunk_terms:
                    if term not in tf_map:
                        continue
                    tf = tf_map[term]
                    df = kp_doc_freqs.get(term, 0)
                    if df == 0:
                        continue
                    idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                    tf_component = (tf * (self.BM25_K + 1)) / (tf + self.BM25_K * (1 - self.BM25_B + self.BM25_B * len(kp_tokens) / max(avgdl, 1)))
                    score += idf * tf_component

                if score > 0.05:  # 阈值可调
                    scored_kps.append((idx, score))

            # 取 top-3
            scored_kps.sort(key=lambda x: x[1], reverse=True)
            for idx, score in scored_kps[:3]:
                links.append({
                    "chunk_id": chunk["chunk_id"],
                    "kp_id": kps[idx]["kp_id"],
                    "match_method": "bm25",
                    "relevance_score": min(round(score, 4), 1.0),
                    "status": "pending",
                    "match_version": match_version,
                })

        return links
