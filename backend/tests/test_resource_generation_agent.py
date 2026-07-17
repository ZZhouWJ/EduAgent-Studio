import unittest
from unittest.mock import Mock, patch

from app.agents.resource_generation_agent import ResourceGenerationAgent


class ResourceGenerationContractTests(unittest.TestCase):
    @patch("app.rag.retriever.search_knowledge")
    @patch("app.repositories.evidence_repo.EvidenceRepository")
    def test_evidence_retrieval_uses_course_search_fallback(
        self,
        evidence_repo_type,
        search_knowledge,
    ):
        evidence_repo = Mock()
        evidence_repo.get_confirmed_kp_chunk_links.return_value = []
        evidence_repo.get_kp_by_id.return_value = {"kp_id": 7, "kp_name": "事务隔离"}
        evidence_repo_type.return_value = evidence_repo
        search_knowledge.return_value = [{
            "chunk_id": 12,
            "title": "隔离级别",
            "content": "事务隔离级别包括读未提交、读已提交、可重复读和串行化。",
            "bm25_score": 1.25,
        }]

        result = ResourceGenerationAgent()._retrieve_evidence([7], course_id=3)

        search_knowledge.assert_called_once_with(
            query="事务隔离",
            course_id=3,
            top_k=5,
        )
        self.assertEqual(result["coverage"], {7: 1})
        self.assertEqual(result["evidence_chunks"][0]["chunk_id"], 12)
        self.assertIn("chunk_id: 12", result["context_text"])

    def test_generated_resource_uses_persistable_type_code(self):
        agent = ResourceGenerationAgent()
        agent._retrieve_evidence = Mock(return_value={
            "context_text": "",
            "evidence_chunks": [],
            "has_confirmed_knowledge": False,
        })
        agent._call_llm = Mock(return_value="# 事务隔离讲义\n\n正文")
        agent._retrieve_rag_for_check = Mock(return_value="")

        result = agent.run(
            learning_path=[{
                "kp_id": 7,
                "kp_name": "事务隔离",
                "resource_type": "讲义",
                "estimated_time": "30分钟",
                "priority": "high",
            }],
            resource_type="lecture",
            difficulty="intermediate",
            student_profile={"student_name": "测试学生"},
            course_id=3,
        )

        self.assertEqual(result["type"], "lecture")
        self.assertEqual(result["type_label"], "知识点讲义")
        self.assertEqual(result["knowledge_points"], [7])


if __name__ == "__main__":
    unittest.main()
