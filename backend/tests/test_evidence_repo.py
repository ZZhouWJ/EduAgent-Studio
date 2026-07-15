import unittest
from contextlib import contextmanager
from unittest.mock import patch

from app.repositories import evidence_repo


class FakeCursor:
    def __init__(self):
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchall(self):
        return []


class EvidenceRepositoryTests(unittest.TestCase):
    def test_resource_evidence_reads_filename_from_material(self):
        cursor = FakeCursor()

        @contextmanager
        def fake_cursor():
            yield cursor

        with patch.object(evidence_repo, "get_db_cursor", fake_cursor):
            evidence_repo.EvidenceRepository().get_evidence_by_resource(10)

        query = cursor.queries[0][0]
        self.assertIn("m.filename AS material_filename", query)
        self.assertNotIn("c.filename,", query)

    def test_pending_evidence_always_joins_material_metadata(self):
        cursor = FakeCursor()

        @contextmanager
        def fake_cursor():
            yield cursor

        repository = evidence_repo.EvidenceRepository()
        with patch.object(evidence_repo, "get_db_cursor", fake_cursor):
            repository.get_pending_evidence_for_review(course_id=1)
            repository.get_pending_evidence_for_review()

        for query, _ in cursor.queries:
            self.assertIn("JOIN course_materials c", query)
            self.assertIn("c.filename AS material_filename", query)


if __name__ == "__main__":
    unittest.main()
