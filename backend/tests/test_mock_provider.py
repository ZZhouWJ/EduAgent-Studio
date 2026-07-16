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

    def test_resource_prompt_is_not_misclassified_as_planning_json(self):
        prompt = """
## 学习路径
1. [事务隔离] 讲义 | 预计 30分钟
## 资源类型：课程讲义
## 教材原文依据（务必引用，chunk_id 格式为数字）
（当前课程暂无教材依据）
## 输出要求
- 直接输出 Markdown 格式学习资源内容
"""

        result = MockProvider()._generate_response(prompt, "mock-model")

        self.assertTrue(result.startswith("# 事务隔离专题课程讲义"))
        self.assertIn("## 核心概念", result)
        self.assertIn("[草稿:缺乏充分教材依据]", result)
        self.assertNotIn('"learning_path"', result)

    def test_teacher_review_is_not_misclassified_by_embedded_resource(self):
        prompt = """你是一个专业的教学审核辅助智能体。请进行质量评估。

## 资源正文（仅供审核，不要照抄）：
# 事务隔离专题讲义
## 学习路径
1. 理解并发控制
## 学习反馈
请根据反馈调整练习。
"""

        result = json.loads(MockProvider()._generate_response(prompt, "mock-model"))

        self.assertEqual(result["quality_score"], 8.5)
        self.assertIn("quality_checks", result)
        self.assertNotIn("learning_path", result)

    def test_diagnosis_and_plan_follow_selected_knowledge_points(self):
        diagnosis_prompt = """你是一个专业的学习诊断智能体。
## 课程知识点掌握情况
- [kp_id:6] 事务与 ACID | 掌握度 35%
- [kp_id:7] 并发控制与锁 | 掌握度 42%
## 最近学习任务
（暂无）
"""
        provider = MockProvider()
        diagnosis = json.loads(provider._generate_response(diagnosis_prompt, "mock-model"))

        self.assertEqual(
            [point["name"] for point in diagnosis["weak_points"]],
            ["事务与 ACID", "并发控制与锁"],
        )
        self.assertEqual([point["kp_id"] for point in diagnosis["weak_points"]], [6, 7])

        planning_prompt = """你是一个专业的学习规划智能体。
## 课程知识点
- [kp_id:6] 事务与 ACID
- [kp_id:7] 并发控制与锁
## 薄弱知识点（优先攻克）
- [kp_id:6] 事务与 ACID | 掌握度 35%
- [kp_id:7] 并发控制与锁 | 掌握度 42%
## 资源类型说明
- 讲义
"""
        planning = json.loads(provider._generate_response(planning_prompt, "mock-model"))

        self.assertEqual(
            [step["kp_name"] for step in planning["learning_path"]],
            ["事务与 ACID", "并发控制与锁"],
        )
        self.assertEqual([step["kp_id"] for step in planning["learning_path"]], [6, 7])


if __name__ == "__main__":
    unittest.main()
