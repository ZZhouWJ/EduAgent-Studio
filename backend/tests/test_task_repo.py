import unittest
from contextlib import contextmanager
from unittest.mock import patch

from app.repositories import task_repo


class FakeCursor:
    def __init__(self, rows):
        self._rows = iter(rows)
        self.params = []

    def execute(self, query, params=None):
        self.params.append(params)
        self.query = query

    def fetchone(self):
        return next(self._rows)


class TaskRepositoryTests(unittest.TestCase):
    def test_output_timeline_walks_parent_chain_without_recursive_cte(self):
        cursor = FakeCursor([
            {"output_id": 30, "parent_output_id": 20, "version_no": 3},
            {"output_id": 20, "parent_output_id": 10, "version_no": 2},
            {"output_id": 10, "parent_output_id": None, "version_no": 1},
        ])

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(task_repo, "get_db_cursor", fake_cursor):
            timeline = task_repo.get_output_parent_chain(30)

        self.assertEqual([row["output_id"] for row in timeline], [10, 20, 30])
        self.assertEqual(cursor.params, [(30,), (20,), (10,)])
        self.assertNotIn("WITH RECURSIVE", cursor.query)

    def test_output_timeline_stops_on_cycle(self):
        cursor = FakeCursor([
            {"output_id": 2, "parent_output_id": 1, "version_no": 2},
            {"output_id": 1, "parent_output_id": 2, "version_no": 1},
        ])

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(task_repo, "get_db_cursor", fake_cursor):
            timeline = task_repo.get_output_parent_chain(2)

        self.assertEqual([row["output_id"] for row in timeline], [1, 2])


if __name__ == "__main__":
    unittest.main()
