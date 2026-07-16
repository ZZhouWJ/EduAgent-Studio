import asyncio
import unittest
from contextlib import contextmanager
from unittest.mock import Mock, patch

from app.repositories import statistics_repo
from app.repositories.statistics_learning_repo import StatisticsLearningRepository
from app.routers import statistics as statistics_router
from app.services import statistics_service
from app.utils.exceptions import ForbiddenException


class FakeCursor:
    def __init__(self, responses):
        self._responses = iter(responses)
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchone(self):
        return next(self._responses)

    def fetchall(self):
        return next(self._responses)


class PlatformStatisticsTests(unittest.TestCase):
    def test_cost_statistics_apply_every_filter_to_every_breakdown(self):
        cursor = FakeCursor([
            {
                "total_cost": 0.25,
                "input_cost": 0.1,
                "output_cost": 0.15,
                "total_tokens": 1200,
            },
            [{"model_id": 7, "model_name": "model", "total_cost": 0.25}],
            [{"project_id": 36, "project_name": "project", "total_cost": 0.25, "call_count": 2}],
            [{"user_id": 1, "real_name": "admin", "total_cost": 0.25}],
            [{"date": "2026-07-16", "call_count": 2, "total_tokens": 1200, "total_cost": 0.25}],
        ])

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(statistics_repo, "get_db_cursor", fake_cursor):
            result = statistics_repo.get_cost_stats(
                is_admin=True,
                user_id=1,
                project_id=36,
                model_id=7,
                date_from="2026-07-10",
                date_to="2026-07-16",
            )

        self.assertEqual(result["cost_trend"][0]["date"], "2026-07-16")
        expected_params = [36, "2026-07-10", "2026-07-16 23:59:59", 7]
        self.assertEqual(len(cursor.queries), 5)
        for query, params in cursor.queries:
            self.assertIn("cr.project_id = %s", query)
            self.assertIn("cr.model_id = %s", query)
            self.assertIn("cr.created_at >= %s", query)
            self.assertIn("cr.created_at <= %s", query)
            self.assertEqual(params, expected_params)
        trend_query = cursor.queries[-1][0]
        self.assertIn("GROUP BY DATE_FORMAT(cr.created_at", trend_query)
        self.assertIn("ORDER BY date ASC", trend_query)

    @patch("app.services.statistics_service.statistics_repo.get_cost_stats", return_value={})
    @patch("app.services.statistics_service._require_auth", return_value={"user_id": 1, "roles": ["admin"]})
    def test_cost_service_forwards_model_filter(self, _require_auth, get_cost_stats):
        statistics_service.get_cost_stats(
            token="token",
            project_id=36,
            model_id=7,
            date_from="2026-07-10",
            date_to="2026-07-16",
        )

        get_cost_stats.assert_called_once_with(
            is_admin=True,
            user_id=1,
            project_id=36,
            model_id=7,
            date_from="2026-07-10",
            date_to="2026-07-16",
        )

    @patch("app.routers.statistics.statistics_service.get_cost_stats", return_value={})
    def test_cost_route_forwards_model_filter(self, get_cost_stats):
        asyncio.run(statistics_router.get_cost_stats(
            authorization="Bearer token",
            project_id=36,
            model_id=7,
            date_from="2026-07-10",
            date_to="2026-07-16",
        ))

        get_cost_stats.assert_called_once_with(
            token="token",
            project_id=36,
            model_id=7,
            date_from="2026-07-10",
            date_to="2026-07-16",
        )

    def test_platform_statistics_use_audit_table_schema(self):
        cursor = FakeCursor([
            {
                "invocation_count": 12,
                "total_tokens": 3456,
                "today_invocations": 3,
                "avg_latency_ms": 251.456,
                "success_rate": 0.91666,
            },
            {"total": 1.2345678},
            {"resource_count": 9, "pending_resources": 2},
            {"student_count": 4, "course_count": 3},
        ])

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(statistics_repo, "get_db_cursor", fake_cursor):
            result = statistics_repo.get_platform_stats()

        self.assertEqual(result["invocation_count"], 12)
        self.assertEqual(result["student_count"], 4)
        self.assertEqual(result["total_cost"], 1.234568)
        self.assertEqual(result["avg_latency_ms"], 251.46)
        self.assertEqual(result["success_rate"], 0.9167)
        combined_queries = " ".join(query for query, _ in cursor.queries)
        self.assertNotIn("cost_records WHERE is_deleted", combined_queries)
        self.assertNotIn("FROM ai_invocations WHERE is_deleted", combined_queries)
        self.assertIn("SUM(status = 'success')", combined_queries)
        self.assertIn(
            "INNER JOIN users u ON u.user_id = sp.student_id AND u.is_deleted = 0",
            combined_queries,
        )

    def test_cost_by_model_does_not_soft_delete_audit_rows(self):
        cursor = FakeCursor([[
            {
                "model": "Mock Writer",
                "call_count": 2,
                "total_tokens": 1200,
                "total_cost": 0.02,
            },
        ]])

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(statistics_repo, "get_db_cursor", fake_cursor):
            result = statistics_repo.get_cost_by_model()

        self.assertEqual(result[0]["model"], "Mock Writer")
        self.assertNotIn("cr.is_deleted", cursor.queries[0][0])

    def test_rag_hit_rate_uses_resource_evidence_links(self):
        cursor = FakeCursor([{"cnt": 20}, {"cnt": 5}])

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(statistics_repo, "get_db_cursor", fake_cursor):
            result = statistics_repo.get_rag_hit_rate()

        self.assertEqual(result["referenced_chunks"], 5)
        self.assertEqual(result["hit_rate"], 0.25)
        self.assertIn("resource_evidence_links", cursor.queries[1][0])
        self.assertIn("DISTINCT chunk_id", cursor.queries[1][0])

    def test_student_learning_overview_scopes_every_query(self):
        cursor = FakeCursor([
            {"cnt": 1},
            {"cnt": 1},
            {"cnt": 3},
            {"cnt": 3},
            {"avg_mastery": 0.42},
            {"cnt": 2},
            {"cnt": 4},
            {"cnt": 5},
        ])

        @contextmanager
        def fake_cursor():
            yield cursor

        repo = StatisticsLearningRepository()
        with patch("app.repositories.statistics_learning_repo.get_db_cursor", fake_cursor):
            result = repo.get_overview(scope="student", user_id=42)

        self.assertEqual(result["student_count"], 1)
        self.assertEqual(len(cursor.queries), 8)
        for query, params in cursor.queries:
            self.assertEqual(params, (42,))
            self.assertTrue(
                "student_id = %s" in query
                or "assignee_id = %s" in query
                or "created_by = %s" in query
            )
        resource_queries = [query for query, _ in cursor.queries if "learning_resources lr" in query]
        self.assertEqual(len(resource_queries), 2)
        self.assertTrue(all("lr.status = 'approved'" in query for query in resource_queries))
        profile_queries = [query for query, _ in cursor.queries if "student_profiles sp" in query]
        self.assertTrue(profile_queries)
        self.assertTrue(all("INNER JOIN users u" in query for query in profile_queries))

    def test_teacher_weak_points_are_scoped_to_owned_courses(self):
        cursor = FakeCursor([[]])

        @contextmanager
        def fake_cursor():
            yield cursor

        repo = StatisticsLearningRepository()
        with patch("app.repositories.statistics_learning_repo.get_db_cursor", fake_cursor):
            repo.get_weak_knowledge_points(scope="teacher", user_id=7, top_n=5)

        query, params = cursor.queries[0]
        self.assertIn("c.teacher_id = %s", query)
        self.assertIn("INNER JOIN users u", query)
        self.assertEqual(params, (7, 5))

    @patch("app.services.statistics_service._require_auth")
    @patch("app.services.statistics_service._get_learning_repo")
    def test_student_learning_service_forwards_personal_scope(self, get_repo, require_auth):
        require_auth.return_value = {"user_id": 42, "roles": ["student_member"]}
        repo = Mock()
        repo.get_overview.return_value = {}
        get_repo.return_value = repo

        statistics_service.get_learning_overview("token")

        repo.get_overview.assert_called_once_with(scope="student", user_id=42)

    @patch("app.services.statistics_service._require_auth")
    def test_student_cannot_read_course_review_rates(self, require_auth):
        require_auth.return_value = {"user_id": 42, "roles": ["student_member"]}

        with self.assertRaises(ForbiddenException):
            statistics_service.get_review_rate_by_course("token")

    @patch("app.services.statistics_service._require_auth")
    def test_non_admin_cannot_read_platform_overview(self, require_auth):
        require_auth.return_value = {"user_id": 7, "roles": ["teacher"]}

        with self.assertRaises(ForbiddenException):
            statistics_service.get_platform_overview("token")


if __name__ == "__main__":
    unittest.main()
