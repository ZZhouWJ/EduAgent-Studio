"""课程级数据访问上下文查询。"""

from typing import Optional

from app.database import get_db_cursor


class CourseAccessRepository:
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
