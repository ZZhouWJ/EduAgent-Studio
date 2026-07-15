import unittest

from app.services.agent_service import _extract_save_payload


class ExtractSavePayloadTests(unittest.TestCase):
    def test_accepts_streamed_workflow_result(self):
        result = {
            "resource": {
                "title": "事务隔离级别讲义",
                "type": "lecture",
                "content": "不可重复读与幻读的区别",
                "difficulty": "intermediate",
                "knowledge_points": [7],
            },
            "evidence_links": [{"chunk_id": 12, "quote_text": "隔离级别定义"}],
            "trustworthiness": "high",
            "metadata": {
                "quality_score": 8.6,
                "step_history": [{"step": "generation", "status": "success"}],
            },
        }

        payload = _extract_save_payload(result)

        self.assertEqual(payload["resource"]["content"], "不可重复读与幻读的区别")
        self.assertEqual(payload["evidence_links"][0]["chunk_id"], 12)
        self.assertEqual(payload["trustworthiness"], "high")
        self.assertEqual(payload["quality_score"], 8.6)

    def test_prefers_synchronous_raw_result(self):
        result = {
            "resource": {"content": "mapped"},
            "_raw": {
                "generated_resource": {"content": "raw"},
                "trustworthiness": "medium",
            },
        }

        payload = _extract_save_payload(result)

        self.assertEqual(payload["resource"]["content"], "raw")
        self.assertEqual(payload["trustworthiness"], "medium")


if __name__ == "__main__":
    unittest.main()
