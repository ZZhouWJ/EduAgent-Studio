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

from app.database import get_db_cursor


class LearningResourceRepository:
    """学习资源数据访问层。"""

    def list_resources(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        resource_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        分页查询学习资源列表。

        Returns:
            {"items": [...], "total": int, "page": int, "page_size": int}
        """
        offset = (page - 1) * page_size

        filters = ["lr.is_deleted = 0"]
        params: List[Any] = []

        if course_id is not None:
            filters.append("lr.course_id = %s")
            params.append(course_id)
        if resource_type:
            filters.append("lr.resource_type = %s")
            params.append(resource_type)

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
                    lr.generation_agent
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
            "reviewer_comment": None,
            "version": 1,
        }

    def create_resource(
        self,
        data: Dict[str, Any],
        created_by: int,
    ) -> Dict[str, Any]:
        """创建新学习资源。"""
        target_kp_ids = data.get("target_kp_ids") or []
        target_kp_ids_str = ",".join(str(x) for x in target_kp_ids) if isinstance(target_kp_ids, list) else str(target_kp_ids)

        now = datetime.now()
        with get_db_cursor() as cursor:
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
            resource_id = cursor.lastrowid

        return self.get_resource(resource_id) or {"resource_id": resource_id}
