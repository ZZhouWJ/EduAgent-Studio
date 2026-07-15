import unittest
from contextlib import contextmanager
from unittest.mock import patch

from app.repositories import statistics_repo


class FakeCursor:
    def __init__(self, responses):
        self._responses = iter(responses)
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchone(self):
        return next(self._responses)


class PlatformStatisticsTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
