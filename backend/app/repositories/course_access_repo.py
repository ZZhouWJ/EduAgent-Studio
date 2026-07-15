"""课程级数据访问上下文查询。"""

from typing import Any, Dict, List, Optional

from app.database import get_db_cursor


class CourseAccessRepository:
    def list_accessible_course_ids(
        self,
        user_id: int,
        is_teacher: bool,
        is_student: bool,
    ) -> List[int]:
        conditions = []
        params = []
        if is_teacher:
            conditions.append("c.teacher_id = %s")
            params.append(user_id)
        if is_student:
            conditions.append(
                "EXISTS (SELECT 1 FROM student_profiles sp "
                "WHERE sp.course_id = c.course_id AND sp.student_id = %s "
                "AND sp.is_deleted = 0)"
            )
            params.append(user_id)
        if not conditions:
            return []

        sql = f"""
            SELECT c.course_id
            FROM courses c
            WHERE c.is_deleted = 0 AND ({' OR '.join(conditions)})
            ORDER BY c.course_id
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
        return [int(row["course_id"]) for row in rows]

    def get_course_teacher_id(self, course_id: int) -> Optional[int]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT teacher_id FROM courses WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            row = cursor.fetchone()
        return int(row["teacher_id"]) if row else None

    def is_student_enrolled(self, course_id: int, student_id: int) -> bool:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM student_profiles
                WHERE course_id = %s AND student_id = %s AND is_deleted = 0
                LIMIT 1
                """,
                (course_id, student_id),
            )
            return cursor.fetchone() is not None

    def get_student_profile_id(
        self, course_id: int, student_id: int
    ) -> Optional[int]:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT profile_id
                FROM student_profiles
                WHERE course_id = %s
                  AND student_id = %s
                  AND is_deleted = 0
                LIMIT 1
                """,
                (course_id, student_id),
            )
            row = cursor.fetchone()
        return int(row["profile_id"]) if row else None

    def list_knowledge_point_courses(
        self, kp_ids: List[int]
    ) -> Dict[int, int]:
        if not kp_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(kp_ids))
        with get_db_cursor() as cursor:
            cursor.execute(
                f"""
                SELECT kp_id, course_id
                FROM knowledge_points
                WHERE kp_id IN ({placeholders}) AND is_deleted = 0
                """,
                tuple(kp_ids),
            )
            rows = cursor.fetchall()
        return {int(row["kp_id"]): int(row["course_id"]) for row in rows}

    def list_material_chunk_courses(
        self, chunk_ids: List[int]
    ) -> Dict[int, int]:
        if not chunk_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(chunk_ids))
        with get_db_cursor() as cursor:
            cursor.execute(
                f"""
                SELECT chunk_id, course_id
                FROM course_material_chunks
                WHERE chunk_id IN ({placeholders}) AND is_deleted = 0
                """,
                tuple(chunk_ids),
            )
            rows = cursor.fetchall()
        return {int(row["chunk_id"]): int(row["course_id"]) for row in rows}

    def get_material_course_id(self, material_id: int) -> Optional[int]:
        return self._single_course_id(
            "SELECT course_id FROM course_materials WHERE material_id = %s AND is_deleted = 0",
            material_id,
        )

    def get_resource_course_id(self, resource_id: int) -> Optional[int]:
        return self._single_course_id(
            "SELECT course_id FROM learning_resources WHERE resource_id = %s AND is_deleted = 0",
            resource_id,
        )

    def get_profile_course_id(self, profile_id: int) -> Optional[int]:
        return self._single_course_id(
            "SELECT course_id FROM student_profiles WHERE profile_id = %s AND is_deleted = 0",
            profile_id,
        )

    def get_profile_access_context(
        self, profile_id: int
    ) -> Optional[Dict[str, Any]]:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT student_id, course_id
                FROM student_profiles
                WHERE profile_id = %s AND is_deleted = 0
                """,
                (profile_id,),
            )
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "student_id": int(row["student_id"]),
            "course_id": int(row["course_id"]),
        }

    def get_task_course_id(self, task_id: int) -> Optional[int]:
        return self._single_course_id(
            "SELECT course_id FROM learning_tasks WHERE task_id = %s AND is_deleted = 0",
            task_id,
        )

    def get_tutor_session_context(
        self, session_id: int
    ) -> Optional[Dict[str, Any]]:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT ts.profile_id,
                       ts.course_id,
                       sp.course_id AS profile_course_id
                FROM tutor_sessions ts
                INNER JOIN student_profiles sp
                    ON ts.profile_id = sp.profile_id AND sp.is_deleted = 0
                WHERE ts.session_id = %s AND ts.is_deleted = 0
                """,
                (session_id,),
            )
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "profile_id": int(row["profile_id"]),
            "course_id": int(row["course_id"]),
            "profile_course_id": int(row["profile_course_id"]),
        }

    def get_kp_link_course_id(self, link_id: int) -> Optional[int]:
        return self._single_course_id(
            """
            SELECT chunks.course_id
            FROM kp_chunk_links links
            JOIN course_material_chunks chunks
              ON links.chunk_id = chunks.chunk_id AND chunks.is_deleted = 0
            WHERE links.link_id = %s
            """,
            link_id,
        )

    def get_evidence_link_course_id(self, link_id: int) -> Optional[int]:
        return self._single_course_id(
            """
            SELECT resources.course_id
            FROM resource_evidence_links links
            JOIN learning_resources resources
              ON links.resource_id = resources.resource_id AND resources.is_deleted = 0
            WHERE links.link_id = %s
            """,
            link_id,
        )

    def _single_course_id(self, sql: str, entity_id: int) -> Optional[int]:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (entity_id,))
            row = cursor.fetchone()
        return int(row["course_id"]) if row else None
