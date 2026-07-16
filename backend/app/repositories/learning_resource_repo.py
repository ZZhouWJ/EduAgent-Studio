"""
学习资源 Repository 层。

Tables:
- learning_resources: resource_id, course_id, resource_title, resource_type, difficulty,
                    content, target_kp_ids, generation_model, generation_agent,
                    invocation_id, status, is_deleted, created_at, updated_at, created_by
- courses: course_id, course_name, is_deleted
- knowledge_points: kp_id, kp_name, is_deleted
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymysql.cursors import DictCursor

from app.database import get_db_cursor


class LearningResourceRepository:
    """学习资源数据访问层。"""

    def list_resources(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        course_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        分页查询学习资源列表。

        Returns:
            {"items": [...], "total": int, "page": int, "page_size": int}
        """
        if course_ids is not None and not course_ids:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

        offset = (page - 1) * page_size

        filters = ["lr.is_deleted = 0"]
        params: List[Any] = []

        if course_id is not None:
            filters.append("lr.course_id = %s")
            params.append(course_id)
        elif course_ids is not None:
            placeholders = ", ".join(["%s"] * len(course_ids))
            filters.append(f"lr.course_id IN ({placeholders})")
            params.extend(course_ids)
        if resource_type:
            filters.append("lr.resource_type = %s")
            params.append(resource_type)
        if status:
            filters.append("lr.status = %s")
            params.append(status)

        where_clause = " AND ".join(filters)

        with get_db_cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) AS total FROM learning_resources lr WHERE {where_clause}",
                params,
            )
            total = cursor.fetchone()["total"]

            sql = f"""
                SELECT
                    lr.resource_id,
                    lr.course_id,
                    c.course_name,
                    lr.resource_title,
                    lr.resource_type,
                    lr.difficulty,
                    lr.status,
                    lr.created_at,
                    lr.updated_at,
                    lr.generation_model,
                    lr.generation_agent,
                    (
                        SELECT rr.submitted_at
                        FROM learning_resource_reviews rr
                        WHERE rr.resource_id = lr.resource_id AND rr.is_deleted = 0
                        ORDER BY rr.review_id DESC
                        LIMIT 1
                    ) AS review_submitted_at
                FROM learning_resources lr
                INNER JOIN courses c ON lr.course_id = c.course_id AND c.is_deleted = 0
                WHERE {where_clause}
                ORDER BY lr.created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + [page_size, offset])
            rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append({
                "resource_id": row["resource_id"],
                "course_id": row["course_id"],
                "course_name": row["course_name"] or "",
                "resource_title": row["resource_title"] or "",
                "resource_type": row["resource_type"] or "other",
                "difficulty": row["difficulty"] or "intermediate",
                "status": row["status"] or "draft",
                "created_at": (
                    row["created_at"].isoformat()
                    if isinstance(row["created_at"], datetime)
                    else str(row["created_at"])
                ),
                "generation_model": row["generation_model"] or "",
                "generation_agent": row["generation_agent"] or "",
                "review_submitted_at": (
                    row["review_submitted_at"].isoformat()
                    if isinstance(row.get("review_submitted_at"), datetime)
                    else None
                ),
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_resource(self, resource_id: int) -> Optional[Dict[str, Any]]:
        """查询单个资源详情（含内容）。"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    lr.resource_id,
                    lr.course_id,
                    c.course_name,
                    lr.resource_title,
                    lr.resource_type,
                    lr.difficulty,
                    lr.content,
                    lr.target_kp_ids,
                    lr.generation_model,
                    lr.generation_agent,
                    lr.status,
                    lr.created_at,
                    lr.updated_at
                FROM learning_resources lr
                INNER JOIN courses c ON lr.course_id = c.course_id AND c.is_deleted = 0
                WHERE lr.resource_id = %s AND lr.is_deleted = 0
            """, (resource_id,))
            row = cursor.fetchone()

        if not row:
            return None

        # 解析 target_kp_ids
        target_ids_raw = row.get("target_kp_ids") or ""
        target_ids = [
            int(x.strip()) for x in target_ids_raw.split(",") if x.strip()
        ]

        # 获取知识点名称
        target_kp_names = []
        if target_ids:
            placeholders = ",".join(["%s"] * len(target_ids))
            with get_db_cursor() as cursor:
                cursor.execute(
                    f"SELECT kp_id, kp_name FROM knowledge_points "
                    f"WHERE kp_id IN ({placeholders}) AND is_deleted = 0",
                    target_ids,
                )
                for r in cursor.fetchall():
                    target_kp_names.append(r["kp_name"])

        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    rr.review_id,
                    rr.review_status,
                    rr.submit_note,
                    rr.accuracy_score,
                    rr.completeness_score,
                    rr.logic_score,
                    rr.format_score,
                    rr.usability_score,
                    rr.review_comment,
                    rr.submitted_at,
                    rr.reviewed_at,
                    COALESCE(submitter.real_name, submitter.username) AS submitter_name,
                    COALESCE(reviewer.real_name, reviewer.username) AS reviewer_name
                FROM learning_resource_reviews rr
                INNER JOIN users submitter
                    ON rr.submitter_id = submitter.user_id AND submitter.is_deleted = 0
                LEFT JOIN users reviewer
                    ON rr.reviewer_id = reviewer.user_id AND reviewer.is_deleted = 0
                WHERE rr.resource_id = %s AND rr.is_deleted = 0
                ORDER BY rr.review_id DESC
            """, (resource_id,))
            review_rows = cursor.fetchall()

        review_history = []
        for review in review_rows:
            review_history.append({
                "review_id": review["review_id"],
                "review_status": review["review_status"],
                "submit_note": review["submit_note"],
                "accuracy_score": float(review["accuracy_score"]) if review["accuracy_score"] is not None else None,
                "completeness_score": float(review["completeness_score"]) if review["completeness_score"] is not None else None,
                "logic_score": float(review["logic_score"]) if review["logic_score"] is not None else None,
                "format_score": float(review["format_score"]) if review["format_score"] is not None else None,
                "usability_score": float(review["usability_score"]) if review["usability_score"] is not None else None,
                "review_comment": review["review_comment"],
                "submitter_name": review["submitter_name"],
                "reviewer_name": review["reviewer_name"],
                "submitted_at": review["submitted_at"].isoformat(),
                "reviewed_at": review["reviewed_at"].isoformat() if review["reviewed_at"] else None,
            })

        return {
            "resource_id": row["resource_id"],
            "course_id": row["course_id"],
            "course_name": row["course_name"] or "",
            "resource_title": row["resource_title"] or "",
            "resource_type": row["resource_type"] or "other",
            "difficulty": row["difficulty"] or "intermediate",
            "content": row["content"] or "",
            "target_kp_ids": target_ids,
            "target_kp_names": target_kp_names,
            "generation_model": row["generation_model"] or "",
            "generation_agent": row["generation_agent"] or "",
            "status": row["status"] or "draft",
            "created_at": (
                row["created_at"].isoformat()
                if isinstance(row["created_at"], datetime)
                else str(row["created_at"])
            ),
            "updated_at": (
                row["updated_at"].isoformat()
                if isinstance(row["updated_at"], datetime)
                else str(row["updated_at"])
            ),
            "reviewer_comment": review_history[0]["review_comment"] if review_history else None,
            "review_history": review_history,
            "version": len(review_history) + 1,
        }

    def get_resource_for_update(self, resource_id: int, conn: Any) -> Optional[Dict[str, Any]]:
        """Lock one resource before a lifecycle state transition."""
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT resource_id, course_id, status, content
                FROM learning_resources
                WHERE resource_id = %s AND is_deleted = 0
                FOR UPDATE
            """, (resource_id,))
            return cursor.fetchone()

    def create_review_request(
        self,
        resource_id: int,
        submitter_id: int,
        submit_note: Optional[str],
        conn: Any,
    ) -> int:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                INSERT INTO learning_resource_reviews
                    (resource_id, submitter_id, review_status, submit_note,
                     submitted_at, created_at)
                VALUES (%s, %s, 'pending', %s, %s, %s)
            """, (resource_id, submitter_id, submit_note, datetime.now(), datetime.now()))
            return int(cursor.lastrowid)

    def update_resource_status(
        self,
        resource_id: int,
        expected_statuses: List[str],
        status: str,
        conn: Any,
    ) -> int:
        placeholders = ", ".join(["%s"] * len(expected_statuses))
        with conn.cursor(DictCursor) as cursor:
            cursor.execute(
                f"""
                    UPDATE learning_resources
                    SET status = %s, updated_at = %s
                    WHERE resource_id = %s AND is_deleted = 0
                      AND status IN ({placeholders})
                """,
                [status, datetime.now(), resource_id, *expected_statuses],
            )
            return int(cursor.rowcount)

    def get_pending_review_for_update(
        self, resource_id: int, conn: Any
    ) -> Optional[Dict[str, Any]]:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT review_id, submitter_id
                FROM learning_resource_reviews
                WHERE resource_id = %s AND review_status = 'pending' AND is_deleted = 0
                ORDER BY review_id DESC
                LIMIT 1
                FOR UPDATE
            """, (resource_id,))
            return cursor.fetchone()

    def complete_review_request(
        self,
        review_id: int,
        reviewer_id: int,
        decision: str,
        accuracy_score: Optional[float],
        completeness_score: Optional[float],
        logic_score: Optional[float],
        format_score: Optional[float],
        usability_score: Optional[float],
        review_comment: Optional[str],
        conn: Any,
    ) -> int:
        now = datetime.now()
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                UPDATE learning_resource_reviews
                SET review_status = %s,
                    reviewer_id = %s,
                    accuracy_score = %s,
                    completeness_score = %s,
                    logic_score = %s,
                    format_score = %s,
                    usability_score = %s,
                    review_comment = %s,
                    reviewed_at = %s,
                    updated_at = %s
                WHERE review_id = %s AND review_status = 'pending' AND is_deleted = 0
            """, (
                decision,
                reviewer_id,
                accuracy_score,
                completeness_score,
                logic_score,
                format_score,
                usability_score,
                review_comment,
                now,
                now,
                review_id,
            ))
            return int(cursor.rowcount)

    def create_resource(
        self,
        data: Dict[str, Any],
        created_by: int,
        conn: Any = None,
    ) -> Dict[str, Any]:
        """创建新学习资源。"""
        target_kp_ids = data.get("target_kp_ids") or []
        target_kp_ids_str = ",".join(str(x) for x in target_kp_ids) if isinstance(target_kp_ids, list) else str(target_kp_ids)

        def insert(cursor: Any) -> int:
            cursor.execute("""
                INSERT INTO learning_resources
                    (course_id, resource_title, resource_type, difficulty, content,
                     target_kp_ids, generation_model, generation_agent, status,
                     is_deleted, created_at, updated_at, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s)
            """, (
                data.get("course_id"),
                data.get("resource_title"),
                data.get("resource_type", "lecture"),
                data.get("difficulty", "intermediate"),
                data.get("content", ""),
                target_kp_ids_str,
                data.get("generation_model", ""),
                data.get("generation_agent", ""),
                data.get("status", "draft"),
                now, now, created_by,
            ))
            return int(cursor.lastrowid)

        now = datetime.now()
        if conn is not None:
            with conn.cursor(DictCursor) as cursor:
                return {"resource_id": insert(cursor)}

        with get_db_cursor() as cursor:
            resource_id = insert(cursor)

        return self.get_resource(resource_id) or {"resource_id": resource_id}
