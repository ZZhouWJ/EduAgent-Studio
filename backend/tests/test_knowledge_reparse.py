import unittest
from unittest.mock import MagicMock, Mock, patch

from app.repositories.knowledge_repo import KnowledgeRepository
from app.services.knowledge_service import KnowledgeService


class KnowledgeReparseTests(unittest.TestCase):
    def setUp(self):
        self.service = KnowledgeService()
        self.service._repo = Mock()
        self.service._evidence_repo = Mock()
        self.service._repo.get_material.return_value = {
            "material_id": 8,
            "course_id": 3,
            "status": "parsed",
            "storage_path": "/materials/lesson.txt",
            "file_type": "text",
            "material_version": 4,
        }

    @patch("app.services.knowledge_service.os.path.exists", return_value=True)
    @patch("app.services.knowledge_service.parse_document_file")
    def test_failed_reparse_preserves_previous_version(self, parser, _exists):
        parser.side_effect = RuntimeError("/private/server/path leaked")

        with self.assertLogs("app.services.knowledge_service", level="ERROR") as logs:
            result = self.service.reparse_material(8)

        self.assertEqual(result["message"], "重新解析失败，已保留上一版本")
        self.service._repo.replace_material_chunks.assert_not_called()
        self.service._repo.update_material_status.assert_any_call(
            8, "parsed", error_message="重新解析失败，已保留上一版本"
        )
        self.assertNotIn("/private", result["message"])
        self.assertNotIn("/private", "\n".join(logs.output))

    @patch("app.services.knowledge_service.os.path.exists", return_value=True)
    @patch("app.services.knowledge_service.parse_document_file")
    def test_successful_reparse_replaces_chunks_at_next_version(self, parser, _exists):
        parser.return_value = [{"title": "事务", "content": "事务保证原子性。"}]
        self.service._repo.replace_material_chunks.return_value = 1
        self.service._repo.get_chunks_by_material_version.return_value = []

        result = self.service.reparse_material(8)

        self.assertEqual(result["code"], 0)
        call = self.service._repo.replace_material_chunks.call_args.kwargs
        self.assertEqual(call["material_version"], 5)
        self.assertEqual(call["total_chars"], len("事务保证原子性。"))


class KnowledgeRepositoryReplacementTests(unittest.TestCase):
    @patch("app.repositories.knowledge_repo.get_db_cursor")
    def test_material_list_exposes_version_and_character_count(self, get_cursor):
        cursor = MagicMock()
        cursor.fetchall.return_value = [{
            "material_id": 8,
            "course_id": 3,
            "filename": "lesson.md",
            "file_type": "markdown",
            "status": "pending",
            "error_message": None,
            "total_chunks": 0,
            "material_version": 2,
            "total_chars": 1234,
            "last_reparse_at": None,
            "created_by": 7,
            "created_at": None,
            "updated_at": None,
            "creator_name": "Teacher",
        }]
        context = MagicMock()
        context.__enter__.return_value = cursor
        context.__exit__.return_value = False
        get_cursor.return_value = context

        materials = KnowledgeRepository().list_materials(3)

        self.assertEqual(materials[0]["material_version"], 2)
        self.assertEqual(materials[0]["total_chars"], 1234)

    @patch("app.repositories.knowledge_repo.get_db_transaction")
    def test_replacement_uses_one_transaction(self, transaction):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.rowcount = 1
        transaction.return_value.__enter__.return_value = connection

        inserted = KnowledgeRepository().replace_material_chunks(
            material_id=8,
            course_id=3,
            chunks=[{"title": "事务", "content": "原子性", "chunk_hash": "abc"}],
            material_version=5,
            total_chars=3,
        )

        self.assertEqual(inserted, 1)
        transaction.assert_called_once_with()
        self.assertEqual(cursor.execute.call_count, 5)


if __name__ == "__main__":
    unittest.main()
