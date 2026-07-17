import unittest
from unittest.mock import patch

from app.rag.retriever import _tokenize, search_knowledge


class RagRetrieverTests(unittest.TestCase):
    def test_chinese_phrases_share_semantic_ngrams(self):
        query_tokens = set(_tokenize("事务与 ACID"))
        document_tokens = set(_tokenize("事务与并发控制中的 ACID 特性"))

        self.assertIn("事务", query_tokens)
        self.assertIn("acid", query_tokens)
        self.assertTrue(query_tokens & document_tokens)

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
