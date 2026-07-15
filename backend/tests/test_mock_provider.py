import json
import unittest

from app.llm.mock_provider import MockProvider


class MockProfileExtractionTests(unittest.TestCase):
    def test_extracts_profile_dialog_fields(self):
        prompt = """
你是一个学生学习画像分析助手。
学生描述：
我学过 SQL 基础，学习目标是掌握事务，喜欢案例和视频，每周晚上学习 6 小时。
请抽取以下字段（只返回 JSON）
"""

        result = json.loads(MockProvider()._mock_profile_extraction(prompt))

        self.assertEqual(result["current_level"], "一般")
        self.assertEqual(result["learning_goal"], "掌握事务")
        self.assertEqual(result["weekly_hours"], 6)
        self.assertEqual(result["cognitive_style"], "视觉化理解")
        self.assertEqual(result["resource_preferences"], ["视频", "案例"])
        self.assertIn("SQL", result["knowledge_base"])


if __name__ == "__main__":
    unittest.main()
