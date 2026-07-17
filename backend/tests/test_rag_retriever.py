import unittest
from unittest.mock import MagicMock, patch

from app.repositories.knowledge_repo import KnowledgeRepository
from app.rag.retriever import _tokenize, search_knowledge


class RagRetrieverTests(unittest.TestCase):
    def test_chinese_phrases_share_semantic_ngrams(self):
        query_tokens = set(_tokenize("事务与 ACID"))
        document_tokens = set(_tokenize("事务与并发控制中的 ACID 特性"))

        self.assertIn("事务", query_tokens)
        self.assertIn("acid", query_tokens)
        self.assertTrue(query_tokens & document_tokens)

    @patch("app.repositories.knowledge_repo.get_db_cursor")
    def test_teacher_search_uses_same_chinese_ngrams(self, get_cursor):
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            {
                "chunk_id": 9,
                "material_id": 4,
                "course_id": 1,
                "kp_id": 58,
                "title": "事务与并发控制中的 ACID 特性",
                "content": "事务具有原子性、一致性、隔离性和持久性。",
                "source_page": None,
                "source_paragraph": 0,
                "bm25_terms": "事务,ACID,并发控制",
                "chunk_index": 5,
            }
        ]
        get_cursor.return_value.__enter__.return_value = cursor

        results = KnowledgeRepository().search_chunks(
            course_id=1,
            query="事务与 ACID",
            limit=3,
        )

        self.assertEqual(results[0]["chunk_id"], 9)
        self.assertGreater(results[0]["bm25_score"], 0)

    @patch("app.rag.retriever._search_db_chunks", return_value=[])
    def test_seeded_course_topics_retrieve_static_materials(self, _search_db):
        topics = [
            "数据库基本概念",
            "关系模型",
            "SQL 基本查询",
            "多表连接与子查询",
            "索引与查询优化",
            "事务与 ACID",
            "并发控制与锁",
            "范式与反范式",
            "数据库设计 (E-R)",
        ]

        for topic in topics:
            with self.subTest(topic=topic):
                self.assertTrue(search_knowledge(topic, course_id=1, top_k=3))


if __name__ == "__main__":
    unittest.main()
