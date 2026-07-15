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

    def fetchall(self):
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


if __name__ == "__main__":
    unittest.main()
