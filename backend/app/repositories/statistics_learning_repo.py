"""
A3 学习分析统计 Repository 层。

Tables:
- courses: course_id, course_name, status, is_deleted
- knowledge_points: kp_id, course_id, kp_name, is_deleted
- student_profiles: profile_id, student_id, course_id, mastery_score, is_deleted
- student_knowledge_mastery: mastery_id, profile_id, kp_id, mastery_level, is_deleted
- learning_resources: resource_id, course_id, resource_type, status, is_deleted, created_at
- learning_tasks: task_id, course_id, status, is_deleted
- learning_feedbacks: feedback_id, profile_id, is_deleted, created_at
- invocations: invocation_id, model_name, agent_name, input_tokens, output_tokens, cost, created_at, is_deleted
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Tuple

from app.database import get_db_cursor

LearningScope = Literal["admin", "teacher", "student"]


def _course_scope(alias: str, scope: LearningScope, user_id: int) -> Tuple[str, tuple]:
    if scope == "teacher":
        return f"{alias}.teacher_id = %s", (user_id,)
    if scope == "student":
        return (
            f"EXISTS (SELECT 1 FROM student_profiles scoped_sp "
            f"WHERE scoped_sp.course_id = {alias}.course_id "
            "AND scoped_sp.student_id = %s AND scoped_sp.is_deleted = 0)",
            (user_id,),
        )
    return "1 = 1", ()


def _profile_scope(
    profile_alias: str,
    course_alias: str,
    scope: LearningScope,
    user_id: int,
) -> Tuple[str, tuple]:
    if scope == "teacher":
        return f"{course_alias}.teacher_id = %s", (user_id,)
    if scope == "student":
        return f"{profile_alias}.student_id = %s", (user_id,)
    return "1 = 1", ()


def _invocation_scope(alias: str, scope: LearningScope, user_id: int) -> Tuple[str, tuple]:
    if scope == "admin":
        return "1 = 1", ()
    return f"{alias}.created_by = %s", (user_id,)


class StatisticsLearningRepository:
    """A3 学习分析统计 Repository。"""

    # -------------------------------------------------------------------------
    # get_learning_overview
    # -------------------------------------------------------------------------

    def get_overview(self, scope: LearningScope, user_id: int) -> Dict[str, Any]:
        """返回当前角色数据范围内的学习概览统计。"""
        course_filter, course_params = _course_scope("c", scope, user_id)
        profile_filter, profile_params = _profile_scope("sp", "c", scope, user_id)
        invocation_filter, invocation_params = _invocation_scope("ai", scope, user_id)

        with get_db_cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM courses c "
                f"WHERE c.is_deleted = 0 AND {course_filter}",
                course_params,
            )
            course_count = cursor.fetchone()["cnt"]

            cursor.execute(
                f"SELECT COUNT(DISTINCT sp.student_id) AS cnt "
                f"FROM student_profiles sp "
                f"INNER JOIN users u ON u.user_id = sp.student_id AND u.is_deleted = 0 "
                f"INNER JOIN courses c ON c.course_id = sp.course_id AND c.is_deleted = 0 "
                f"WHERE sp.is_deleted = 0 AND {profile_filter}",
                profile_params,
            )
            student_count = cursor.fetchone()["cnt"]

            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM learning_resources lr "
                f"INNER JOIN courses c ON c.course_id = lr.course_id AND c.is_deleted = 0 "
                f"WHERE lr.is_deleted = 0 "
                f"AND {course_filter} "
                f"{'AND lr.status = \'approved\'' if scope == 'student' else ''}",
                course_params,
            )
            resource_count = cursor.fetchone()["cnt"]

            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM learning_resources lr "
                f"INNER JOIN courses c ON c.course_id = lr.course_id AND c.is_deleted = 0 "
                f"WHERE lr.status = 'approved' AND lr.is_deleted = 0 AND {course_filter}",
                course_params,
            )
            approved_count = cursor.fetchone()["cnt"]

            cursor.execute(
                f"SELECT AVG(skm.mastery_level) AS avg_mastery "
                f"FROM student_knowledge_mastery skm "
                f"INNER JOIN student_profiles sp ON skm.profile_id = sp.profile_id AND sp.is_deleted = 0 "
                f"INNER JOIN users u ON u.user_id = sp.student_id AND u.is_deleted = 0 "
                f"INNER JOIN courses c ON c.course_id = sp.course_id AND c.is_deleted = 0 "
                f"WHERE skm.is_deleted = 0 AND {profile_filter}",
                profile_params,
            )
            row = cursor.fetchone()
            avg_mastery = round(row["avg_mastery"], 3) if row["avg_mastery"] else 0.0

            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM learning_feedbacks lf "
                f"INNER JOIN student_profiles sp ON sp.profile_id = lf.profile_id AND sp.is_deleted = 0 "
                f"INNER JOIN users u ON u.user_id = sp.student_id AND u.is_deleted = 0 "
                f"INNER JOIN courses c ON c.course_id = sp.course_id AND c.is_deleted = 0 "
                f"WHERE lf.is_deleted = 0 AND {profile_filter}",
                profile_params,
            )
            feedback_count = cursor.fetchone()["cnt"]

            task_filter = course_filter
            task_params = course_params
            if scope == "student":
                task_filter = "lt.assignee_id = %s"
                task_params = (user_id,)
            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM learning_tasks lt "
                f"INNER JOIN courses c ON c.course_id = lt.course_id AND c.is_deleted = 0 "
                f"WHERE lt.is_deleted = 0 AND lt.status IN ('assigned', 'in_progress') "
                f"AND {task_filter}",
                task_params,
            )
            active_tasks = cursor.fetchone()["cnt"]

            review_pass_rate = (
                round(approved_count / resource_count, 3) if resource_count > 0 else 0.0
            )

            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM ai_invocations ai "
                f"WHERE ai.is_deleted = 0 AND {invocation_filter}",
                invocation_params,
            )
            invocation_count = cursor.fetchone()["cnt"]

        return {
            "course_count": course_count,
            "student_count": student_count,
            "resource_count": resource_count,
            "invocation_count": invocation_count,
            "avg_mastery": avg_mastery,
            "review_pass_rate": review_pass_rate,
            "feedback_count": feedback_count,
            "active_tasks": active_tasks,
        }

    # -------------------------------------------------------------------------
    # get_mastery_distribution
    # -------------------------------------------------------------------------

    def get_mastery_distribution(
        self,
        scope: LearningScope,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        返回学生掌握度分布桶：0-20%, 20-40%, 40-60%, 60-80%, 80-100%。

        基于 student_knowledge_mastery 的 mastery_level 分布，
        按 profile 维度聚合（每学生取平均 mastery_score）。
        """
        profile_filter, params = _profile_scope("sp", "c", scope, user_id)
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                SELECT AVG(skm.mastery_level) AS avg_mastery
                FROM student_knowledge_mastery skm
                INNER JOIN student_profiles sp ON skm.profile_id = sp.profile_id AND sp.is_deleted = 0
                INNER JOIN users u ON u.user_id = sp.student_id AND u.is_deleted = 0
                INNER JOIN courses c ON c.course_id = sp.course_id AND c.is_deleted = 0
                WHERE skm.is_deleted = 0 AND {profile_filter}
                GROUP BY sp.profile_id
            """, params)
            rows = cursor.fetchall()

        buckets = {"0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0}
        for row in rows:
            avg = row["avg_mastery"] or 0
            if avg < 0.2:
                buckets["0-20%"] += 1
            elif avg < 0.4:
                buckets["20-40%"] += 1
            elif avg < 0.6:
                buckets["40-60%"] += 1
            elif avg < 0.8:
                buckets["60-80%"] += 1
            else:
                buckets["80-100%"] += 1

        return [{"range": k, "count": v} for k, v in buckets.items()]

    # -------------------------------------------------------------------------
    # get_weak_knowledge_points
    # -------------------------------------------------------------------------

    def get_weak_knowledge_points(
        self,
        scope: LearningScope,
        user_id: int,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        薄弱知识点 TOP N：按课程+知识点聚合，取平均 mastery_level 最低的。
        """
        profile_filter, params = _profile_scope("sp", "c", scope, user_id)
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    kp.kp_id,
                    kp.kp_name,
                    kp.course_id,
                    AVG(skm.mastery_level) AS avg_mastery
                FROM student_knowledge_mastery skm
                INNER JOIN student_profiles sp ON skm.profile_id = sp.profile_id AND sp.is_deleted = 0
                INNER JOIN users u ON u.user_id = sp.student_id AND u.is_deleted = 0
                INNER JOIN knowledge_points kp ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                INNER JOIN courses c ON kp.course_id = c.course_id AND c.is_deleted = 0
                WHERE skm.is_deleted = 0 AND {profile_filter}
                GROUP BY kp.kp_id, kp.kp_name, kp.course_id
                ORDER BY avg_mastery ASC
                LIMIT %s
            """, (*params, top_n))
            rows = cursor.fetchall()

        return [
            {
                "kp_id": row["kp_id"],
                "kp_name": row["kp_name"],
                "course_id": row["course_id"],
                "avg_mastery": round(row["avg_mastery"], 3) if row["avg_mastery"] else 0.0,
            }
            for row in rows
        ]

    # -------------------------------------------------------------------------
    # get_resource_type_distribution
    # -------------------------------------------------------------------------

    def get_resource_type_distribution(
        self,
        scope: LearningScope,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """学习资源类型分布。"""
        TYPE_NAMES = {
            "lecture": "知识点讲义",
            "ppt": "PPT大纲",
            "quiz": "习题与答案",
            "case": "案例材料",
            "review": "复习计划",
            "test": "阶段测验",
            "other": "其他",
        }
        course_filter, params = _course_scope("c", scope, user_id)
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                SELECT lr.resource_type, COUNT(*) AS cnt
                FROM learning_resources lr
                INNER JOIN courses c ON c.course_id = lr.course_id AND c.is_deleted = 0
                WHERE lr.is_deleted = 0
                  AND {course_filter}
                  {'AND lr.status = \'approved\'' if scope == 'student' else ''}
                GROUP BY lr.resource_type
                ORDER BY cnt DESC
            """, params)
            rows = cursor.fetchall()

        return [
            {
                "resource_type": row["resource_type"] or "other",
                "type_name": TYPE_NAMES.get(row["resource_type"] or "other", "其他"),
                "count": row["cnt"],
            }
            for row in rows
        ]

    # -------------------------------------------------------------------------
    # get_invocation_trend
    # -------------------------------------------------------------------------

    def get_invocation_trend(
        self,
        scope: LearningScope,
        user_id: int,
        days: int = 14,
    ) -> List[Dict[str, Any]]:
        """近 N 天智能体调用趋势。"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        invocation_filter, scope_params = _invocation_scope("ai", scope, user_id)
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    DATE(ai.created_at) AS call_date,
                    COUNT(*) AS invocation_count,
                    COALESCE(SUM(ai.input_tokens), 0) AS total_input_tokens,
                    COALESCE(SUM(ai.output_tokens), 0) AS total_output_tokens,
                    COALESCE(SUM(cr.total_cost), 0) AS total_cost
                FROM ai_invocations ai
                LEFT JOIN cost_records cr ON ai.invocation_id = cr.invocation_id
                WHERE ai.created_at >= %s
                  AND ai.created_at <= %s
                  AND {invocation_filter}
                GROUP BY DATE(ai.created_at)
                ORDER BY call_date ASC
            """, (start_date, end_date + timedelta(days=1), *scope_params))
            rows = cursor.fetchall()

        trends_map = {row["call_date"]: row for row in rows}
        trends = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            if d in trends_map:
                r = trends_map[d]
                trends.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "invocation_count": r["invocation_count"],
                    "total_tokens": (r["total_input_tokens"] or 0) + (r["total_output_tokens"] or 0),
                    "total_cost": round(r["total_cost"] or 0.0, 6),
                })
            else:
                trends.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "invocation_count": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                })

        return trends

    # -------------------------------------------------------------------------
    # get_review_rate_by_course
    # -------------------------------------------------------------------------

    def get_review_rate_by_course(
        self,
        scope: LearningScope,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """各课程资源审核通过率。"""
        course_filter, params = _course_scope("c", scope, user_id)
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    c.course_id,
                    c.course_name,
                    COUNT(lr.resource_id) AS total,
                    SUM(CASE WHEN lr.status = 'approved' THEN 1 ELSE 0 END) AS approved
                FROM courses c
                LEFT JOIN learning_resources lr
                    ON c.course_id = lr.course_id AND lr.is_deleted = 0
                WHERE c.is_deleted = 0 AND {course_filter}
                GROUP BY c.course_id, c.course_name
                ORDER BY c.course_id ASC
            """, params)
            rows = cursor.fetchall()

        result = []
        for row in rows:
            total = row["total"] or 0
            approved = row["approved"] or 0
            pass_rate = round(approved / total, 3) if total > 0 else 0.0
            result.append({
                "course_id": row["course_id"],
                "course_name": row["course_name"],
                "total": total,
                "approved": approved,
                "pass_rate": pass_rate,
            })

        return result

    # -------------------------------------------------------------------------
    # get_cost_distribution
    # -------------------------------------------------------------------------

    def get_cost_distribution(self) -> List[Dict[str, Any]]:
        """Token 消耗占比（按模型分类）。"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    COALESCE(am.display_name, am.model_name) AS agent,
                    COALESCE(SUM(cr.total_tokens), 0) AS total_tokens,
                    COALESCE(SUM(cr.total_cost), 0) AS total_cost
                FROM cost_records cr
                INNER JOIN ai_models am ON cr.model_id = am.model_id AND am.is_deleted = 0
                GROUP BY am.model_id, am.display_name, am.model_name
                ORDER BY total_tokens DESC
            """)
            rows = cursor.fetchall()

        total_tokens = sum((row["total_tokens"] or 0) for row in rows)
        if total_tokens == 0:
            total_tokens = 1  # avoid division by zero
        result = []
        for row in rows:
            tokens = row["total_tokens"] or 0
            agent_name = row["agent"] or "unknown"
            result.append({
                "agent": agent_name,
                "agent_name": agent_name,
                "tokens": tokens,
                "ratio": round(tokens / total_tokens, 4),
            })

        return result
