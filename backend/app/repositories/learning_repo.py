"""
学习模块 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
软删除为主，不物理删除。

Tables:
- courses: course_id, course_name, course_code, description, teacher_id, status, is_deleted, created_at, updated_at
- knowledge_points: kp_id, course_id, kp_name, kp_code, parent_kp_id, difficulty_level, description, estimated_hours, is_deleted, created_at, updated_at
- learning_tasks: task_id, course_id, title, description, target_kp_ids, creator_id, assignee_id, status, due_date, is_deleted, created_at, updated_at
- users: user_id, username, real_name (teacher name)
- student_profiles: profile_id, student_id, course_id, is_deleted
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_db_cursor

COVER_COLORS = ["#409eff", "#67c23a", "#e6a23c", "#f56c6c", "#909399"]

DIFFICULTY_MAP = {
    "basic": "基础",
    "intermediate": "进阶",
    "advanced": "高级",
}


def _compute_cover_color(course_id: int) -> str:
    """根据 course_id 循环选择封面颜色。"""
    return COVER_COLORS[course_id % len(COVER_COLORS)]


def _map_difficulty(level: Optional[str]) -> str:
    """将 difficulty_level 映射为中文标签。"""
    if not level:
        return "基础"
    return DIFFICULTY_MAP.get(level.lower(), "基础")


class LearningRepository:
    """学习模块数据访问层。"""

    def list_courses(self) -> List[Dict[str, Any]]:
        """
        Returns list of course dicts with knowledge_points embedded.
        Shape matches _MOCK_COURSES exactly.
        """
        sql = """
            SELECT
                c.course_id,
                c.course_name,
                c.course_code,
                c.description,
                c.status,
                u.real_name AS teacher
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.user_id AND u.is_deleted = 0
            WHERE c.is_deleted = 0
            ORDER BY c.course_id ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            courses = cursor.fetchall()

        result = []
        for course in courses:
            course_id = course["course_id"]

            kp_sql = """
                SELECT kp_id, kp_name, difficulty_level
                FROM knowledge_points
                WHERE course_id = %s AND is_deleted = 0
                ORDER BY kp_id ASC
            """
            cursor.execute(kp_sql, (course_id,))
            kp_rows = cursor.fetchall()
            knowledge_points = [
                {
                    "id": row["kp_id"],
                    "name": row["kp_name"],
                    "mastery_avg": 0.5,
                    "difficulty": _map_difficulty(row["difficulty_level"]),
                }
                for row in kp_rows
            ]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM knowledge_points WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            kp_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM student_profiles WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            student_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM learning_tasks WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            task_count = cursor.fetchone()["cnt"]

            result.append(
                {
                    "id": course_id,
                    "name": course["course_name"],
                    "code": course["course_code"],
                    "description": course["description"],
                    "teacher": course["teacher"] or "",
                    "semester": "2025-2026学年春季学期",
                    "status": course["status"],
                    "knowledge_point_count": kp_count,
                    "student_count": student_count,
                    "task_count": task_count,
                    "cover_color": _compute_cover_color(course_id),
                    "tags": [],
                    "knowledge_points": knowledge_points,
                }
            )

        return result

    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Returns single course dict with full knowledge_points list."""
        sql = """
            SELECT
                c.course_id,
                c.course_name,
                c.course_code,
                c.description,
                c.status,
                u.real_name AS teacher
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.user_id AND u.is_deleted = 0
            WHERE c.course_id = %s AND c.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (course_id,))
            course = cursor.fetchone()

        if not course:
            return None

        kp_sql = """
            SELECT kp_id, kp_name, difficulty_level
            FROM knowledge_points
            WHERE course_id = %s AND is_deleted = 0
            ORDER BY kp_id ASC
        """
        cursor.execute(kp_sql, (course_id,))
        kp_rows = cursor.fetchall()
        knowledge_points = [
            {
                "id": row["kp_id"],
                "name": row["kp_name"],
                "mastery_avg": 0.5,
                "difficulty": _map_difficulty(row["difficulty_level"]),
            }
            for row in kp_rows
        ]

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM knowledge_points WHERE course_id = %s AND is_deleted = 0",
            (course_id,),
        )
        kp_count = cursor.fetchone()["cnt"]

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM student_profiles WHERE course_id = %s AND is_deleted = 0",
            (course_id,),
        )
        student_count = cursor.fetchone()["cnt"]

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM learning_tasks WHERE course_id = %s AND is_deleted = 0",
            (course_id,),
        )
        task_count = cursor.fetchone()["cnt"]

        return {
            "id": course["course_id"],
            "name": course["course_name"],
            "code": course["course_code"],
            "description": course["description"],
            "teacher": course["teacher"] or "",
            "semester": "2025-2026学年春季学期",
            "status": course["status"],
            "knowledge_point_count": kp_count,
            "student_count": student_count,
            "task_count": task_count,
            "cover_color": _compute_cover_color(course["course_id"]),
            "tags": [],
            "knowledge_points": knowledge_points,
        }

    def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns paginated task list:
        {
            "items": [{id, course_id, course_name, title, type, status, priority, due_date, description, student_count: 0, completion_rate: 0.0}, ...],
            "total": int,
            "page": int,
            "page_size": int
        }
        type comes from task title keyword detection (exercise/quiz/project/lecture/review), default "exercise"
        priority from due_date proximity (high if <7 days, medium if <14 days, else low)
        """
        offset = (page - 1) * page_size

        filters = ["t.is_deleted = 0"]
        params: List[Any] = []

        if course_id is not None:
            filters.append("t.course_id = %s")
            params.append(course_id)
        if status:
            filters.append("t.status = %s")
            params.append(status)

        where_clause = " AND ".join(filters)

        with get_db_cursor() as cursor:
            count_sql = f"SELECT COUNT(*) AS total FROM learning_tasks t WHERE {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"]

            data_sql = f"""
                SELECT
                    t.task_id,
                    t.course_id,
                    t.title,
                    t.description,
                    t.status,
                    t.due_date,
                    c.course_name
                FROM learning_tasks t
                INNER JOIN courses c ON t.course_id = c.course_id AND c.is_deleted = 0
                WHERE {where_clause}
                ORDER BY t.task_id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(data_sql, params + [page_size, offset])
            rows = cursor.fetchall()

        now = datetime.now()
        items = []
        for row in rows:
            due_date = row["due_date"]
            priority = self._compute_priority(due_date, now)
            task_type = self._detect_task_type(row["title"])

            items.append(
                {
                    "id": row["task_id"],
                    "course_id": row["course_id"],
                    "course_name": row["course_name"],
                    "title": row["title"],
                    "type": task_type,
                    "status": row["status"],
                    "priority": priority,
                    "due_date": row["due_date"].strftime("%Y-%m-%d") if isinstance(due_date, datetime) else str(due_date),
                    "description": row["description"] or "",
                    "student_count": 0,
                    "completion_rate": 0.0,
                }
            )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Returns single task dict with course_name, course_description."""
        sql = """
            SELECT
                t.task_id,
                t.course_id,
                t.title,
                t.description,
                t.status,
                t.due_date,
                c.course_name,
                c.description AS course_description
            FROM learning_tasks t
            INNER JOIN courses c ON t.course_id = c.course_id AND c.is_deleted = 0
            WHERE t.task_id = %s AND t.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (task_id,))
            row = cursor.fetchone()

        if not row:
            return None

        due_date = row["due_date"]
        now = datetime.now()
        priority = self._compute_priority(due_date, now)
        task_type = self._detect_task_type(row["title"])

        return {
            "id": row["task_id"],
            "course_id": row["course_id"],
            "course_name": row["course_name"],
            "course_description": row["course_description"] or "",
            "title": row["title"],
            "type": task_type,
            "status": row["status"],
            "priority": priority,
            "due_date": row["due_date"].strftime("%Y-%m-%d") if isinstance(due_date, datetime) else str(due_date),
            "description": row["description"] or "",
            "student_count": 0,
            "completion_rate": 0.0,
        }

    @staticmethod
    def _detect_task_type(title: str) -> str:
        """根据标题关键词检测任务类型。"""
        title_lower = title.lower()
        if "练习" in title or "exercise" in title_lower or "作业" in title:
            return "exercise"
        if "测验" in title or "quiz" in title_lower or "测试" in title:
            return "quiz"
        if "项目" in title or "project" in title_lower or "大作业" in title:
            return "project"
        if "讲义" in title or "lecture" in title_lower or "课程" in title:
            return "lecture"
        if "复习" in title or "review" in title_lower:
            return "review"
        return "exercise"

    @staticmethod
    def _compute_priority(due_date, now: datetime) -> str:
        """根据截止日期距离判断优先级。"""
        if due_date is None:
            return "low"
        if isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return "low"
        delta_days = (due_date - now).days
        if delta_days < 7:
            return "high"
        if delta_days < 14:
            return "medium"
        return "low"
