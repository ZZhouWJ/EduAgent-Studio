import unittest
from unittest.mock import Mock

from app.agents.resource_generation_agent import ResourceGenerationAgent


class ResourceGenerationContractTests(unittest.TestCase):
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
