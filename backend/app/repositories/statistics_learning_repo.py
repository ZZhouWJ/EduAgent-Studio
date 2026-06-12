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
from typing import Any, Dict, List

from app.database import get_db_cursor


class StatisticsLearningRepository:
    """A3 学习分析统计 Repository。"""

    # -------------------------------------------------------------------------
    # get_learning_overview
    # -------------------------------------------------------------------------

    def get_overview(self) -> Dict[str, Any]:
        """返回全局学习概览统计。"""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM courses WHERE is_deleted = 0")
            course_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(DISTINCT profile_id) AS cnt FROM student_profiles WHERE is_deleted = 0"
            )
            student_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM learning_resources WHERE is_deleted = 0"
            )
            resource_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM learning_resources WHERE status = 'approved' AND is_deleted = 0"
            )
            approved_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT AVG(skm.mastery_level) AS avg_mastery "
                "FROM student_knowledge_mastery skm "
                "INNER JOIN student_profiles sp ON skm.profile_id = sp.profile_id AND sp.is_deleted = 0 "
                "WHERE skm.is_deleted = 0"
            )
            row = cursor.fetchone()
            avg_mastery = round(row["avg_mastery"], 3) if row["avg_mastery"] else 0.0

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM learning_feedbacks WHERE is_deleted = 0"
            )
            feedback_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM learning_tasks "
                "WHERE is_deleted = 0 AND status IN ('assigned', 'in_progress')"
            )
            active_tasks = cursor.fetchone()["cnt"]

            review_pass_rate = (
                round(approved_count / resource_count, 3) if resource_count > 0 else 0.0
            )

        return {
            "course_count": course_count,
            "student_count": student_count,
            "resource_count": resource_count,
            "invocation_count": 0,
            "avg_mastery": avg_mastery,
            "review_pass_rate": review_pass_rate,
            "feedback_count": feedback_count,
            "active_tasks": active_tasks,
        }

    # -------------------------------------------------------------------------
    # get_mastery_distribution
    # -------------------------------------------------------------------------

    def get_mastery_distribution(self) -> List[Dict[str, Any]]:
        """
        返回学生掌握度分布桶：0-20%, 20-40%, 40-60%, 60-80%, 80-100%。

        基于 student_knowledge_mastery 的 mastery_level 分布，
        按 profile 维度聚合（每学生取平均 mastery_score）。
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT AVG(skm.mastery_level) AS avg_mastery
                FROM student_knowledge_mastery skm
                INNER JOIN student_profiles sp ON skm.profile_id = sp.profile_id AND sp.is_deleted = 0
                WHERE skm.is_deleted = 0
                GROUP BY sp.profile_id
            """)
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

    def get_weak_knowledge_points(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        薄弱知识点 TOP N：按课程+知识点聚合，取平均 mastery_level 最低的。
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    kp.kp_id,
                    kp.kp_name,
                    kp.course_id,
                    AVG(skm.mastery_level) AS avg_mastery
                FROM student_knowledge_mastery skm
                INNER JOIN knowledge_points kp ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                INNER JOIN courses c ON kp.course_id = c.course_id AND c.is_deleted = 0
                WHERE skm.is_deleted = 0
                GROUP BY kp.kp_id, kp.kp_name, kp.course_id
                ORDER BY avg_mastery ASC
                LIMIT %s
            """, (top_n,))
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

    def get_resource_type_distribution(self) -> List[Dict[str, Any]]:
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
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT resource_type, COUNT(*) AS cnt
                FROM learning_resources
                WHERE is_deleted = 0
                GROUP BY resource_type
                ORDER BY cnt DESC
            """)
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

    def get_invocation_trend(self, days: int = 14) -> List[Dict[str, Any]]:
        """近 N 天智能体调用趋势。"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    DATE(created_at) AS call_date,
                    COUNT(*) AS invocation_count,
                    SUM(input_tokens) AS total_input_tokens,
                    SUM(output_tokens) AS total_output_tokens,
                    SUM(cost) AS total_cost
                FROM invocations
                WHERE is_deleted = 0
                  AND created_at >= %s
                  AND created_at <= %s
                GROUP BY DATE(created_at)
                ORDER BY call_date ASC
            """, (start_date, end_date + timedelta(days=1)))
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

    def get_review_rate_by_course(self) -> List[Dict[str, Any]]:
        """各课程资源审核通过率。"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    c.course_id,
                    c.course_name,
                    COUNT(lr.resource_id) AS total,
                    SUM(CASE WHEN lr.status = 'approved' THEN 1 ELSE 0 END) AS approved
                FROM courses c
                LEFT JOIN learning_resources lr
                    ON c.course_id = lr.course_id AND lr.is_deleted = 0
                WHERE c.is_deleted = 0
                GROUP BY c.course_id, c.course_name
                ORDER BY c.course_id ASC
            """)
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
        """Token 消耗占比（按智能体分类）。"""
        AGENT_NAMES = {
            "diagnosis_agent": "学习诊断",
            "planning_agent": "资源规划",
            "resource_generation_agent": "资源生成",
            "assessment_agent": "评测反馈",
            "teacher_review_agent": "教师审核辅助",
        }
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    agent_name,
                    SUM(input_tokens + output_tokens) AS total_tokens,
                    SUM(cost) AS total_cost
                FROM invocations
                WHERE is_deleted = 0
                GROUP BY agent_name
                ORDER BY total_tokens DESC
            """)
            rows = cursor.fetchall()

        total_tokens = sum((row["total_tokens"] or 0) for row in rows)
        result = []
        for row in rows:
            tokens = row["total_tokens"] or 0
            result.append({
                "agent": row["agent_name"] or "unknown",
                "agent_name": AGENT_NAMES.get(row["agent_name"] or "", row["agent_name"] or ""),
                "tokens": tokens,
                "ratio": round(tokens / total_tokens, 4) if total_tokens > 0 else 0.0,
            })

        return result
