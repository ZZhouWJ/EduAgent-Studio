"""
学习反馈 Repository 层。

Tables:
- learning_feedbacks: feedback_id, profile_id, resource_id, course_id,
                       feedback_type, content, quiz_score, self_mastery,
                       difficulty_rating, is_deleted, created_at, updated_at
- student_profiles: profile_id, student_id, course_id, is_deleted
- users: user_id, real_name, is_deleted
- courses: course_id, course_name, is_deleted
- learning_resources: resource_id, resource_title, is_deleted
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_db_cursor


class LearningFeedbackRepository:
    """学习反馈数据访问层。"""

    def list_feedbacks(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        feedback_type: Optional[str] = None,
        student_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        分页查询学习反馈列表。

        Returns:
            {"items": [...], "total": int, "page": int, "page_size": int}
        """
        offset = (page - 1) * page_size

        filters = ["lf.is_deleted = 0"]
        params: List[Any] = []

        if course_id is not None:
            filters.append("lf.course_id = %s")
            params.append(course_id)
        if feedback_type:
            filters.append("lf.feedback_type = %s")
            params.append(feedback_type)
        if student_id is not None:
            filters.append(
                "EXISTS (SELECT 1 FROM student_profiles owner_sp "
                "WHERE owner_sp.profile_id = lf.profile_id "
                "AND owner_sp.student_id = %s AND owner_sp.is_deleted = 0)"
            )
            params.append(student_id)

        where_clause = " AND ".join(filters)

        with get_db_cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) AS total FROM learning_feedbacks lf WHERE {where_clause}",
                params,
            )
            total = cursor.fetchone()["total"]

            sql = f"""
                SELECT
                    lf.feedback_id,
                    lf.profile_id,
                    u.real_name AS student_name,
                    lf.resource_id,
                    lr.resource_title,
                    lf.course_id,
                    c.course_name,
                    lf.feedback_type,
                    lf.content,
                    lf.quiz_score,
                    lf.self_mastery,
                    lf.difficulty_rating,
                    lf.created_at
                FROM learning_feedbacks lf
                INNER JOIN student_profiles sp ON lf.profile_id = sp.profile_id AND sp.is_deleted = 0
                INNER JOIN users u ON sp.student_id = u.user_id AND u.is_deleted = 0
                LEFT JOIN learning_resources lr ON lf.resource_id = lr.resource_id AND lr.is_deleted = 0
                INNER JOIN courses c ON lf.course_id = c.course_id AND c.is_deleted = 0
                WHERE {where_clause}
                ORDER BY lf.created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + [page_size, offset])
            rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append({
                "feedback_id": row["feedback_id"],
                "profile_id": row["profile_id"],
                "student_name": row["student_name"] or "",
                "resource_id": row["resource_id"],
                "resource_title": row["resource_title"],
                "course_id": row["course_id"],
                "course_name": row["course_name"] or "",
                "feedback_type": row["feedback_type"] or "self_report",
                "content": row["content"],
                "quiz_score": row["quiz_score"],
                "self_mastery": row["self_mastery"],
                "difficulty_rating": row["difficulty_rating"],
                "created_at": (
                    row["created_at"].isoformat()
                    if isinstance(row["created_at"], datetime)
                    else str(row["created_at"])
                ),
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_feedback_history_by_profile(
        self,
        profile_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        获取指定画像的学习反馈历史（用于展示画像更新记录）。

        Returns:
            反馈记录列表，每条包含 feedback_id, feedback_type, quiz_score,
            self_mastery, difficulty_rating, content, created_at, resource_title
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    lf.feedback_id,
                    lf.feedback_type,
                    lf.quiz_score,
                    lf.self_mastery,
                    lf.difficulty_rating,
                    lf.content,
                    lf.created_at,
                    lr.resource_title,
                    c.course_name
                FROM learning_feedbacks lf
                LEFT JOIN learning_resources lr ON lf.resource_id = lr.resource_id AND lr.is_deleted = 0
                INNER JOIN courses c ON lf.course_id = c.course_id AND c.is_deleted = 0
                WHERE lf.profile_id = %s AND lf.is_deleted = 0
                ORDER BY lf.created_at DESC
                LIMIT %s
            """, (profile_id, limit))
            rows = cursor.fetchall()

        items = []
        for row in rows:
            feedback_type_labels = {
                "quiz_result": "测验结果",
                "self_report": "自评反馈",
                "study_note": "学习笔记",
                "question": "问题提问",
            }
            items.append({
                "feedback_id": row["feedback_id"],
                "feedback_type": row["feedback_type"] or "self_report",
                "feedback_type_label": feedback_type_labels.get(row["feedback_type"], row["feedback_type"] or "反馈"),
                "quiz_score": row["quiz_score"],
                "self_mastery": row["self_mastery"],
                "difficulty_rating": row["difficulty_rating"],
                "content": row["content"],
                "created_at": (
                    row["created_at"].isoformat()
                    if isinstance(row["created_at"], datetime)
                    else str(row["created_at"])
                ),
                "resource_title": row["resource_title"],
                "course_name": row["course_name"] or "",
            })
        return items

    def create_feedback(
        self,
        data: Dict[str, Any],
        profile_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """创建新学习反馈。"""
        now = datetime.now()
        with get_db_cursor() as cursor:
            # 获取该 profile 对应的 course_id
            cursor.execute(
                "SELECT course_id FROM student_profiles WHERE profile_id = %s AND is_deleted = 0",
                (profile_id,),
            )
            profile_row = cursor.fetchone()
            course_id = profile_row["course_id"] if profile_row else (data.get("course_id") or 1)

            cursor.execute("""
                INSERT INTO learning_feedbacks
                    (profile_id, resource_id, course_id, feedback_type, content,
                     quiz_score, self_mastery, difficulty_rating,
                     is_deleted, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
            """, (
                profile_id,
                data.get("resource_id"),
                course_id,
                data.get("feedback_type", "self_report"),
                data.get("content"),
                data.get("quiz_score"),
                data.get("self_mastery"),
                data.get("difficulty_rating"),
                now, now,
            ))
            feedback_id = cursor.lastrowid

        # 查询完整记录
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    lf.feedback_id,
                    lf.profile_id,
                    u.real_name AS student_name,
                    lf.resource_id,
                    lr.resource_title,
                    lf.course_id,
                    c.course_name,
                    lf.feedback_type,
                    lf.content,
                    lf.quiz_score,
                    lf.self_mastery,
                    lf.difficulty_rating,
                    lf.created_at
                FROM learning_feedbacks lf
                INNER JOIN student_profiles sp ON lf.profile_id = sp.profile_id AND sp.is_deleted = 0
                INNER JOIN users u ON sp.student_id = u.user_id AND u.is_deleted = 0
                LEFT JOIN learning_resources lr ON lf.resource_id = lr.resource_id AND lr.is_deleted = 0
                INNER JOIN courses c ON lf.course_id = c.course_id AND c.is_deleted = 0
                WHERE lf.feedback_id = %s AND lf.is_deleted = 0
            """, (feedback_id,))
            row = cursor.fetchone()

        if not row:
            return {"feedback_id": feedback_id, "profile_id": profile_id}

        return {
            "feedback_id": row["feedback_id"],
            "profile_id": row["profile_id"],
            "student_name": row["student_name"] or "",
            "resource_id": row["resource_id"],
            "resource_title": row["resource_title"],
            "course_id": row["course_id"],
            "course_name": row["course_name"] or "",
            "feedback_type": row["feedback_type"] or "self_report",
            "content": row["content"],
            "quiz_score": row["quiz_score"],
            "self_mastery": row["self_mastery"],
            "difficulty_rating": row["difficulty_rating"],
            "created_at": (
                row["created_at"].isoformat()
                if isinstance(row["created_at"], datetime)
                else str(row["created_at"])
            ),
        }
