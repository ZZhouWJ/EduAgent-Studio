"""
课程知识库 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
软删除为主，不物理删除。

Tables:
- course_materials: material_id, course_id, filename, file_type, storage_path, status, error_message, total_chunks, created_by, created_at, updated_at, is_deleted
- course_material_chunks: chunk_id, material_id, course_id, kp_id, title, content, source_page, source_paragraph, bm25_terms, chunk_index, created_at, is_deleted
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db_cursor


class KnowledgeRepository:
    """课程知识库数据访问层。"""

    # BM25 参数
    BM25_K = 1.5
    BM25_B = 0.75

    def upload_material(
        self,
        course_id: int,
        filename: str,
        file_type: str,
        storage_path: str,
        created_by: int,
    ) -> int:
        """
        创建课程资料记录。

        Args:
            course_id: 课程 ID
            filename: 原始文件名
            file_type: 文件类型 (pdf/markdown/word/ppt/txt)
            storage_path: 存储路径
            created_by: 创建用户 ID

        Returns:
            material_id: 新创建的记录 ID
        """
        sql = """
            INSERT INTO course_materials
                (course_id, filename, file_type, storage_path, status, created_by)
            VALUES (%s, %s, %s, %s, 'pending', %s)
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (course_id, filename, file_type, storage_path, created_by))
            return cursor.lastrowid

    def update_material_status(
        self,
        material_id: int,
        status: str,
        error_message: Optional[str] = None,
        total_chunks: Optional[int] = None,
    ) -> bool:
        """
        更新资料状态。

        Args:
            material_id: 资料 ID
            status: 新状态 (pending/parsing/parsed/failed)
            error_message: 错误信息（解析失败时填写）
            total_chunks: 生成的 chunks 总数（解析成功时填写）

        Returns:
            是否更新成功
        """
        sql = """
            UPDATE course_materials
            SET status = %s
        """
        params: List[Any] = [status]

        if error_message is not None:
            sql += ", error_message = %s"
            params.append(error_message)

        if total_chunks is not None:
            sql += ", total_chunks = %s"
            params.append(total_chunks)

        sql += " WHERE material_id = %s AND is_deleted = 0"
        params.append(material_id)

        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount > 0

    def list_materials(self, course_id: int) -> List[Dict[str, Any]]:
        """
        获取课程的所有资料列表。

        Args:
            course_id: 课程 ID

        Returns:
            资料列表（按创建时间倒序）
        """
        sql = """
            SELECT
                cm.material_id,
                cm.course_id,
                cm.filename,
                cm.file_type,
                cm.status,
                cm.error_message,
                cm.total_chunks,
                cm.created_by,
                cm.created_at,
                cm.updated_at,
                u.real_name AS creator_name
            FROM course_materials cm
            LEFT JOIN users u ON cm.created_by = u.user_id AND u.is_deleted = 0
            WHERE cm.course_id = %s AND cm.is_deleted = 0
            ORDER BY cm.created_at DESC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (course_id,))
            rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "material_id": row["material_id"],
                "course_id": row["course_id"],
                "filename": row["filename"],
                "file_type": row["file_type"],
                "status": row["status"],
                "error_message": row["error_message"],
                "total_chunks": row["total_chunks"],
                "created_by": row["created_by"],
                "creator_name": row.get("creator_name") or "",
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "updated_at": str(row["updated_at"]) if row["updated_at"] else None,
            })
        return result

    def get_material(self, material_id: int) -> Optional[Dict[str, Any]]:
        """
        获取资料详情。

        Args:
            material_id: 资料 ID

        Returns:
            资料详情字典，或 None
        """
        sql = """
            SELECT
                cm.material_id,
                cm.course_id,
                cm.filename,
                cm.file_type,
                cm.storage_path,
                cm.status,
                cm.error_message,
                cm.total_chunks,
                cm.created_by,
                cm.created_at,
                cm.updated_at,
                u.real_name AS creator_name,
                c.course_name
            FROM course_materials cm
            LEFT JOIN users u ON cm.created_by = u.user_id AND u.is_deleted = 0
            LEFT JOIN courses c ON cm.course_id = c.course_id AND c.is_deleted = 0
            WHERE cm.material_id = %s AND cm.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (material_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "material_id": row["material_id"],
            "course_id": row["course_id"],
            "course_name": row.get("course_name") or "",
            "filename": row["filename"],
            "file_type": row["file_type"],
            "storage_path": row["storage_path"],
            "status": row["status"],
            "error_message": row["error_message"],
            "total_chunks": row["total_chunks"],
            "created_by": row["created_by"],
            "creator_name": row.get("creator_name") or "",
            "created_at": str(row["created_at"]) if row["created_at"] else None,
            "updated_at": str(row["updated_at"]) if row["updated_at"] else None,
        }

    def insert_chunks(
        self,
        material_id: int,
        course_id: int,
        chunks: List[Dict[str, Any]],
    ) -> int:
        """
        批量插入文档 chunks。

        Args:
            material_id: 资料 ID
            course_id: 课程 ID
            chunks: chunks 列表，每项包含 title, content, source_page, source_paragraph, bm25_terms

        Returns:
            插入的 chunk 数量
        """
        if not chunks:
            return 0

        sql = """
            INSERT INTO course_material_chunks
                (material_id, course_id, title, content, source_page, source_paragraph, bm25_terms, chunk_index)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        with get_db_cursor() as cursor:
            for idx, chunk in enumerate(chunks):
                cursor.execute(sql, (
                    material_id,
                    course_id,
                    chunk.get("title", ""),
                    chunk.get("content", ""),
                    chunk.get("source_page"),
                    chunk.get("source_paragraph"),
                    chunk.get("bm25_terms", ""),
                    idx,
                ))
            return len(chunks)

    def search_chunks(
        self,
        course_id: int,
        query: str,
        kp_id: Optional[int] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        BM25 检索 chunks。

        Args:
            course_id: 课程 ID
            query: 查询文本
            kp_id: 可选，限定知识点 ID
            limit: 返回数量限制

        Returns:
            按 BM25 得分降序排列的 chunks
        """
        if not query or not query.strip():
            return []

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

        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        if not rows:
            return []

        # 构建 BM25 索引
        index, doc_freqs, avgdl, N = self._build_bm25_index(rows, query)

        # 分词查询
        query_tokens = self._tokenize(query)

        # 计算每个文档的 BM25 得分
        scored = []
        for row in rows:
            chunk_id = str(row["chunk_id"])
            if chunk_id not in index:
                continue

            entry = index[chunk_id]
            score = self._bm25_score(query_tokens, entry["tf"], entry["dl"], doc_freqs, avgdl, N)
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
                    "bm25_terms": row["bm25_terms"],
                    "chunk_index": row["chunk_index"],
                    "bm25_score": round(score, 4),
                }
                scored.append((score, result))

        # 排序并返回 top-k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

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

    def _build_bm25_index(
        self,
        rows: List[Dict[str, Any]],
        query: str,
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, int], float, int]:
        """
        构建 BM25 倒排索引。

        Returns:
            (index, doc_freqs, avgdl, N)
        """
        index: Dict[str, Dict[str, Any]] = {}
        doc_freqs: Dict[str, int] = {}
        all_tokens: List[List[str]] = []

        # 合并 title + content + bm25_terms 进行分词
        for row in rows:
            text = f"{row.get('title', '')} {row.get('bm25_terms', '')} {row.get('content', '')}"
            tokens = self._tokenize(text)
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

        return index, doc_freqs, avgdl, N

    def _bm25_score(
        self,
        query_tokens: List[str],
        tf_map: Dict[str, int],
        dl: int,
        doc_freqs: Dict[str, int],
        avgdl: float,
        N: int,
    ) -> float:
        """计算单个文档的 BM25 得分。"""
        score = 0.0
        for term in query_tokens:
            if term not in tf_map:
                continue
            tf = tf_map[term]
            df = doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            tf_component = (tf * (self.BM25_K + 1)) / (tf + self.BM25_K * (1 - self.BM25_B + self.BM25_B * dl / avgdl))
            score += idf * tf_component
        return score

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 chunk_id 获取详情。

        Args:
            chunk_id: chunk ID

        Returns:
            chunk 详情字典
        """
        sql = """
            SELECT
                cmc.chunk_id,
                cmc.material_id,
                cmc.course_id,
                cmc.kp_id,
                cmc.title,
                cmc.content,
                cmc.source_page,
                cmc.source_paragraph,
                cmc.bm25_terms,
                cmc.chunk_index,
                cmc.created_at,
                cm.filename AS material_filename,
                c.course_name
            FROM course_material_chunks cmc
            LEFT JOIN course_materials cm ON cmc.material_id = cm.material_id AND cm.is_deleted = 0
            LEFT JOIN courses c ON cmc.course_id = c.course_id AND c.is_deleted = 0
            WHERE cmc.chunk_id = %s AND cmc.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (chunk_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "chunk_id": row["chunk_id"],
            "material_id": row["material_id"],
            "course_id": row["course_id"],
            "kp_id": row["kp_id"],
            "title": row["title"],
            "content": row["content"],
            "source_page": row["source_page"],
            "source_paragraph": row["source_paragraph"],
            "bm25_terms": row["bm25_terms"],
            "chunk_index": row["chunk_index"],
            "created_at": str(row["created_at"]) if row["created_at"] else None,
            "material_filename": row.get("material_filename") or "",
            "course_name": row.get("course_name") or "",
        }

    def delete_material(self, material_id: int) -> bool:
        """
        软删除资料及其关联的 chunks。

        Args:
            material_id: 资料 ID

        Returns:
            是否删除成功
        """
        with get_db_cursor() as cursor:
            # 软删除 chunks
            cursor.execute(
                "UPDATE course_material_chunks SET is_deleted = 1 WHERE material_id = %s AND is_deleted = 0",
                (material_id,),
            )
            # 软删除 material
            cursor.execute(
                "UPDATE course_materials SET is_deleted = 1 WHERE material_id = %s AND is_deleted = 0",
                (material_id,),
            )
            return cursor.rowcount > 0

    def get_chunks_by_material(self, material_id: int) -> List[Dict[str, Any]]:
        """
        获取某资料的所有 chunks。

        Args:
            material_id: 资料 ID

        Returns:
            chunks 列表
        """
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
                chunk_index,
                created_at
            FROM course_material_chunks
            WHERE material_id = %s AND is_deleted = 0
            ORDER BY chunk_index ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (material_id,))
            rows = cursor.fetchall()

        return [
            {
                "chunk_id": row["chunk_id"],
                "material_id": row["material_id"],
                "course_id": row["course_id"],
                "kp_id": row["kp_id"],
                "title": row["title"],
                "content": row["content"],
                "source_page": row["source_page"],
                "source_paragraph": row["source_paragraph"],
                "bm25_terms": row["bm25_terms"],
                "chunk_index": row["chunk_index"],
                "created_at": str(row["created_at"]) if row["created_at"] else None,
            }
            for row in rows
        ]
