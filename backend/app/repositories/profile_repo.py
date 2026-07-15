"""学生画像 Repository"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db_cursor


def _serialize_profile(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    将数据库原始行转换为前端期望的 profile 字典结构。
    """
    resource_prefs = _split_field(raw.get("resource_preferences"))
    interests = _split_field(raw.get("interests"))
    weak_points = _parse_json_list(raw.get("weak_points"))
    strong_points = _parse_json_list(raw.get("strong_points"))
    recent_tasks = _parse_json_list(raw.get("recent_tasks"))
    recent_tests = _parse_json_list(raw.get("recent_tests"))
    error_prone_points = _parse_json_list(raw.get("error_prone_points"))

    updated_at = raw.get("updated_at") or raw.get("created_at")
    if isinstance(updated_at, datetime):
        last_updated = updated_at.strftime("%Y-%m-%d")
    elif updated_at:
        last_updated = str(updated_at)[:10]
    else:
        last_updated = ""

    return {
        "profile_id": raw["profile_id"],
        "student_id": raw["student_id"],
        "student_name": raw.get("student_name", ""),
        "course_id": raw["course_id"],
        "course_name": raw.get("course_name", ""),
        "learning_goal": raw.get("learning_goal") or "",
        "knowledge_base": raw.get("knowledge_base") or "",
        "current_level": raw.get("current_level") or "",
        "cognitive_style": raw.get("cognitive_style") or "",
        "time_constraints": raw.get("time_constraints") or "",
        "practice_level": raw.get("practice_level") or "",
        "motivation": raw.get("motivation") or "",
        "error_prone_points": error_prone_points,
        "weak_points": weak_points,
        "preferences": resource_prefs,
        "mastery_score": raw.get("mastery_score") or 0.0,
        "last_updated": last_updated,
        "student_no": raw.get("student_no") or "",
        "interests": interests,
        "resource_preferences": resource_prefs,
        "weekly_hours": raw.get("weekly_hours") or 0,
        "ai_suggestions": "建议根据个人学习情况，合理规划复习时间。",
        "strong_points": strong_points,
        "recent_tasks": recent_tasks,
        "recent_tests": recent_tests,
    }


def _split_field(value: Any) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _parse_json_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if not value:
        return []
    import json as _json

    try:
        return _json.loads(value)
    except Exception:
        return []


class ProfileRepository:
    """学生画像数据访问层。"""

    def list_profiles(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        offset = (page - 1) * page_size

        count_sql = """
            SELECT COUNT(*) AS total
            FROM student_profiles sp
            INNER JOIN courses c ON sp.course_id = c.course_id AND c.is_deleted = 0
            INNER JOIN users u ON sp.student_id = u.user_id AND u.is_deleted = 0
            WHERE sp.is_deleted = 0
        """
        count_params: List[Any] = []

        if course_id is not None:
            count_sql += " AND sp.course_id = %s"
            count_params.append(course_id)

        if keyword:
            count_sql += " AND (u.real_name LIKE %s OR u.student_no LIKE %s)"
            like = f"%{keyword}%"
            count_params.extend([like, like])

        data_sql = f"""
            SELECT
                sp.profile_id,
                sp.student_id,
                u.real_name                              AS student_name,
                sp.course_id,
                c.course_name,
                sp.learning_goal,
                sp.knowledge_base,
                sp.current_level,
                sp.cognitive_style,
                sp.time_constraints,
                sp.practice_level,
                sp.motivation,
                sp.error_prone_points,
                sp.mastery_score,
                sp.updated_at,
                sp.created_at,
                u.student_no,
                sp.interests,
                sp.resource_preferences,
                sp.weekly_hours,

                (
                    SELECT JSON_ARRAYAGG(kp.kp_name)
                    FROM student_knowledge_mastery skm
                    INNER JOIN knowledge_points kp
                        ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                    WHERE skm.profile_id = sp.profile_id
                      AND skm.is_deleted = 0
                      AND skm.mastery_level < 0.5
                ) AS weak_points,

                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT('kp_id', kp.kp_id,
                                    'kp_name', kp.kp_name,
                                    'mastery', skm.mastery_level)
                    )
                    FROM student_knowledge_mastery skm
                    INNER JOIN knowledge_points kp
                        ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                    WHERE skm.profile_id = sp.profile_id
                      AND skm.is_deleted = 0
                      AND skm.mastery_level >= 0.5
                ) AS strong_points,

                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'task_id', t.task_id,
                            'title', t.title,
                            'status', t.status,
                            'completed_at',
                                IF(t.status = 'completed',
                                   DATE_FORMAT(t.updated_at, '%%Y-%%m-%%d'), '')
                        )
                    )
                    FROM learning_tasks t
                    WHERE t.course_id = sp.course_id
                      AND t.is_deleted = 0
                    ORDER BY t.updated_at DESC
                    LIMIT 3
                ) AS recent_tasks,

                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'test_id', lf.feedback_id,
                            'accuracy', IF(lf.quiz_score IS NOT NULL, lf.quiz_score / 100, NULL),
                            'date', DATE_FORMAT(lf.created_at, '%%Y-%%m-%%d')
                        )
                    )
                    FROM learning_feedbacks lf
                    WHERE lf.profile_id = sp.profile_id
                      AND lf.feedback_type = 'quiz'
                      AND lf.is_deleted = 0
                    ORDER BY lf.created_at DESC
                    LIMIT 3
                ) AS recent_tests

            FROM student_profiles sp
            INNER JOIN courses c ON sp.course_id = c.course_id AND c.is_deleted = 0
            INNER JOIN users u ON sp.student_id = u.user_id AND u.is_deleted = 0
            WHERE sp.is_deleted = 0
        """

        data_params: List[Any] = []

        if course_id is not None:
            data_sql += " AND sp.course_id = %s"
            data_params.append(course_id)

        if keyword:
            data_sql += " AND (u.real_name LIKE %s OR u.student_no LIKE %s)"
            like = f"%{keyword}%"
            data_params.extend([like, like])

        data_sql += """
            ORDER BY sp.updated_at DESC
            LIMIT %s OFFSET %s
        """
        data_params.extend([page_size, offset])

        with get_db_cursor() as cursor:
            cursor.execute(count_sql, count_params)
            total = cursor.fetchone()["total"]

            cursor.execute(data_sql, data_params)
            rows = cursor.fetchall()

        profiles = [_serialize_profile(row) for row in rows]
        return profiles, total

    def get_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT
                sp.profile_id,
                sp.student_id,
                u.real_name                              AS student_name,
                sp.course_id,
                c.course_name,
                sp.learning_goal,
                sp.knowledge_base,
                sp.current_level,
                sp.cognitive_style,
                sp.time_constraints,
                sp.practice_level,
                sp.motivation,
                sp.error_prone_points,
                sp.mastery_score,
                sp.updated_at,
                sp.created_at,
                u.student_no,
                sp.interests,
                sp.resource_preferences,
                sp.weekly_hours,

                (
                    SELECT JSON_ARRAYAGG(kp.kp_name)
                    FROM student_knowledge_mastery skm
                    INNER JOIN knowledge_points kp
                        ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                    WHERE skm.profile_id = sp.profile_id
                      AND skm.is_deleted = 0
                      AND skm.mastery_level < 0.5
                ) AS weak_points,

                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT('kp_id', kp.kp_id,
                                    'kp_name', kp.kp_name,
                                    'mastery', skm.mastery_level)
                    )
                    FROM student_knowledge_mastery skm
                    INNER JOIN knowledge_points kp
                        ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                    WHERE skm.profile_id = sp.profile_id
                      AND skm.is_deleted = 0
                      AND skm.mastery_level >= 0.5
                ) AS strong_points,

                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'task_id', t.task_id,
                            'title', t.title,
                            'status', t.status,
                            'completed_at',
                                IF(t.status = 'completed',
                                   DATE_FORMAT(t.updated_at, '%%Y-%%m-%%d'), '')
                        )
                    )
                    FROM learning_tasks t
                    WHERE t.course_id = sp.course_id
                      AND t.is_deleted = 0
                    ORDER BY t.updated_at DESC
                    LIMIT 3
                ) AS recent_tasks,

                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'test_id', lf.feedback_id,
                            'accuracy', IF(lf.quiz_score IS NOT NULL, lf.quiz_score / 100, NULL),
                            'date', DATE_FORMAT(lf.created_at, '%%Y-%%m-%%d')
                        )
                    )
                    FROM learning_feedbacks lf
                    WHERE lf.profile_id = sp.profile_id
                      AND lf.feedback_type = 'quiz'
                      AND lf.is_deleted = 0
                    ORDER BY lf.created_at DESC
                    LIMIT 3
                ) AS recent_tests

            FROM student_profiles sp
            INNER JOIN courses c ON sp.course_id = c.course_id AND c.is_deleted = 0
            INNER JOIN users u ON sp.student_id = u.user_id AND u.is_deleted = 0
            WHERE sp.profile_id = %s AND sp.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (profile_id,))
            row = cursor.fetchone()

        if not row:
            return None
        return _serialize_profile(row)

    def get_profile_by_student_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT profile_id FROM student_profiles WHERE student_id = %s AND is_deleted = 0 LIMIT 1",
                (student_id,),
            )
            row = cursor.fetchone()
        if not row:
            return None
        return self.get_profile(row["profile_id"])

    def get_profile_owner_id(self, profile_id: int) -> Optional[int]:
        """返回画像所属学生 ID，不加载画像聚合详情。"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT student_id
                FROM student_profiles
                WHERE profile_id = %s AND is_deleted = 0
                """,
                (profile_id,),
            )
            row = cursor.fetchone()
        return int(row["student_id"]) if row else None

    def update_profile(self, profile_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "learning_goal",
            "knowledge_base",
            "current_level",
            "cognitive_style",
            "time_constraints",
            "practice_level",
            "motivation",
            "error_prone_points",
            "interests",
            "resource_preferences",
            "weekly_hours",
            "mastery_score",
        }
        fields = []
        params: List[Any] = []

        for field in allowed_fields:
            if field in data and data[field] is not None:
                fields.append(f"{field} = %s")
                params.append(data[field])

        if not fields:
            return self.get_profile(profile_id)

        fields.append("updated_at = %s")
        params.append(datetime.now())
        params.append(profile_id)

        sql = f"""
            UPDATE student_profiles
            SET {', '.join(fields)}
            WHERE profile_id = %s AND is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)

        return self.get_profile(profile_id)

    def update_mastery(
        self,
        profile_id: int,
        kp_id: int,
        mastery_level: float,
        update_reason: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        now = datetime.now()

        update_sql = """
            UPDATE student_knowledge_mastery
            SET mastery_level = %s,
                last_test_score = %s,
                last_test_date = %s,
                update_reason = %s,
                updated_at = %s
            WHERE profile_id = %s AND kp_id = %s AND is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                update_sql,
                (mastery_level, int(mastery_level * 100), now, update_reason, now, profile_id, kp_id),
            )
            updated = cursor.rowcount

        if updated == 0:
            insert_sql = """
                INSERT INTO student_knowledge_mastery
                    (profile_id, kp_id, mastery_level, last_test_score,
                     last_test_date, update_reason, is_deleted, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s)
            """
            with get_db_cursor() as cursor:
                cursor.execute(
                    insert_sql,
                    (
                        profile_id, kp_id, mastery_level,
                        int(mastery_level * 100), now,
                        update_reason, now, now,
                    ),
                )

        avg_sql = """
            UPDATE student_profiles
            SET mastery_score = (
                SELECT AVG(skm.mastery_level)
                FROM student_knowledge_mastery skm
                WHERE skm.profile_id = %s AND skm.is_deleted = 0
            ),
            updated_at = %s
            WHERE profile_id = %s AND is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(avg_sql, (profile_id, now, profile_id))

        result_sql = """
            SELECT skm.mastery_id, skm.profile_id, skm.kp_id,
                   skm.mastery_level, skm.last_test_score,
                   skm.last_test_date, skm.update_reason,
                   kp.kp_name
            FROM student_knowledge_mastery skm
            INNER JOIN knowledge_points kp ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
            WHERE skm.profile_id = %s AND skm.kp_id = %s AND skm.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(result_sql, (profile_id, kp_id))
            return cursor.fetchone()
