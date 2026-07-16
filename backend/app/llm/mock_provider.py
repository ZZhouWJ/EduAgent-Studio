"""
Mock LLM 提供商 — 用于测试和演示

返回结构化的模拟数据，不产生真实 API 调用。
"""
import uuid
import time
import random
import logging
import json
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MockProvider:
    """Mock LLM 提供商"""

    def __init__(self, model_name: str = "mock-gpt", base_url: str = "", api_key: str = "", **kwargs):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock 生成接口"""
        user_input = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_input = msg.get("content", "")
                break

        input_tokens = max(len(" ".join([m.get("content", "") for m in messages])) // 4, 10)

        response_content = self._generate_response(user_input, config.model_name)
        output_tokens = max(len(response_content) // 4, 10)
        total_cost = (input_tokens + output_tokens) * 0.000001

        return {
            "content": response_content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
            "model": self.model_name,
        }

    def _generate_response(self, input_text: str, model_name: str) -> str:
        """根据输入生成 Mock 响应"""
        time.sleep(random.uniform(0.5, 1.5))
        normalized_input = input_text.lower()

        if "学生学习画像分析助手" in input_text:
            return self._mock_profile_extraction(input_text)
        if "专业的学习诊断智能体" in input_text:
            return self._mock_diagnosis()
        if "专业的教育资源生成智能体" in input_text or (
            "教材原文依据" in input_text and "直接输出 Markdown" in input_text
        ):
            return self._mock_resource(input_text, model_name)
        if "专业的学习规划智能体" in input_text:
            return self._mock_planning()
        if "专业的学习评测反馈智能体" in input_text:
            return self._mock_assessment()
        if "专业的教学审核辅助智能体" in input_text:
            return self._mock_teacher_review()
        if "诊断" in normalized_input or "薄弱" in normalized_input:
            return self._mock_diagnosis()
        if "规划" in normalized_input or "路径" in normalized_input:
            return self._mock_planning()
        if "评测" in normalized_input or "反馈" in normalized_input:
            return self._mock_assessment()
        if "审核" in normalized_input or "质量" in normalized_input:
            return self._mock_teacher_review()
        else:
            return f"""# 个性化学习资源

根据您的学习需求，系统生成了以下学习内容。

## 学习目标
掌握相关知识点，建立系统的知识体系。

## 学习路径
1. 理解基础概念
2. 掌握核心原理
3. 实践应用
4. 综合练习

---
*本资源由 {model_name} 生成 | EduAgent Studio*
"""

    def _mock_resource(self, prompt: str, model_name: str) -> str:
        """Return representative Markdown for the explicit development provider."""
        resource_match = re.search(r"资源类型[：:]\s*([^\n]+)", prompt)
        resource_type = resource_match.group(1).strip() if resource_match else "学习资源"
        topics = list(dict.fromkeys(
            topic.strip()
            for topic in re.findall(r"^\d+\.\s*\[([^\]]+)\]", prompt, re.MULTILINE)
            if topic.strip()
        ))
        topic = "、".join(topics[:3]) or "课程重点"
        chunk_ids = list(dict.fromkeys(re.findall(r"\[chunk_id:\s*(\d+)\]", prompt)))
        citation = f" [引用:{chunk_ids[0]}]" if chunk_ids else " [草稿:缺乏充分教材依据]"

        return f"""# {topic}专题{resource_type}

## 学习目标

- 理解 {topic} 的核心概念与适用场景
- 能够结合示例完成基础分析与实践
- 识别常见误区并完成自测

## 核心概念

{topic} 是本阶段学习路径中的重点内容。学习时应先建立概念边界，再通过实例验证理解。{citation}

## 示例

以课程中的典型问题为例，先明确输入条件，再分步骤写出推理过程，最后核对结果是否符合约束。对于不确定的结论，应回到教材原文进行复核。

## 常见错误

1. 只记忆结论，忽略结论成立的前提。
2. 混淆相近概念，导致分析范围不准确。
3. 完成操作后没有验证结果。

## 练习与解析

**练习 1：** 用自己的语言说明 {topic} 的关键作用。

**参考解析：** 回答应包含定义、适用条件和一个课程内示例。

**练习 2：** 列出一个常见错误，并说明如何验证和修正。

**参考解析：** 先定位错误前提，再使用教材定义或可执行示例复核。

---

本资源由 {model_name} 开发模式生成，请由教师确认后发布。
"""

    def _mock_profile_extraction(self, prompt: str) -> str:
        """为本地开发提供可确认、可落库的画像抽取结果。"""
        message_match = re.search(
            r"学生描述：\s*(.*?)\s*请抽取以下字段",
            prompt,
            re.DOTALL,
        )
        message = message_match.group(1).strip() if message_match else prompt

        goal_match = re.search(
            r"(?:学习目标|目标|希望|想要|计划)(?:是|为)?[：:]?\s*([^，。；\n]+)",
            message,
        )
        hours_match = re.search(r"每周[^\d]{0,8}(\d+(?:\.\d+)?)\s*(?:小时|h)", message)

        current_level = None
        if any(keyword in message for keyword in ("零基础", "没学过", "刚入门")):
            current_level = "基础"
        elif any(keyword in message for keyword in ("熟练", "掌握较好", "有项目经验")):
            current_level = "较好"
        elif any(keyword in message for keyword in ("学过", "了解", "一般")):
            current_level = "一般"

        resource_keywords = (
            "视频", "动画", "图解", "讲义", "文档", "思维导图", "练习", "代码", "案例",
        )
        resource_preferences = [
            keyword for keyword in resource_keywords if keyword in message
        ]

        cognitive_style = None
        if any(keyword in message for keyword in ("图解", "动画", "视频", "可视化")):
            cognitive_style = "视觉化理解"
        elif any(keyword in message for keyword in ("案例", "例题", "代码")):
            cognitive_style = "案例与实践驱动"
        elif any(keyword in message for keyword in ("讲义", "文档", "阅读")):
            cognitive_style = "结构化阅读"

        time_markers = [
            marker for marker in ("工作日晚间", "晚上", "周末", "碎片时间")
            if marker in message
        ]
        extraction = {
            "knowledge_base": message if any(
                keyword in message for keyword in ("学过", "掌握", "了解", "零基础")
            ) else None,
            "current_level": current_level,
            "learning_goal": goal_match.group(1).strip() if goal_match else None,
            "weak_points": [],
            "error_prone_points": [],
            "interests": [],
            "resource_preferences": resource_preferences,
            "weekly_hours": float(hours_match.group(1)) if hours_match else None,
            "time_constraints": "、".join(time_markers) or None,
            "cognitive_style": cognitive_style,
            "practice_level": None,
            "motivation": goal_match.group(1).strip() if goal_match else None,
        }
        return json.dumps(extraction, ensure_ascii=False)

    def _mock_diagnosis(self) -> str:
        return f"""{{
  "diagnosis_id": "mock-{uuid.uuid4().hex[:8]}",
  "weak_points": [
    {{"kp_id": 5, "name": "SQL多表连接", "mastery_level": 0.3, "reason": "近3次测验中正确率仅30%"}},
    {{"kp_id": 8, "name": "事务隔离级别", "mastery_level": 0.2, "reason": "从未正确解答相关题目"}}
  ],
  "strength_points": [
    {{"kp_id": 2, "name": "SQL基本查询", "mastery_level": 0.85}}
  ],
  "learning_difficulties": ["多表连接时条件判断容易混淆", "子查询嵌套层次过深难以理解"],
  "resource_needs": ["图文并茂的讲义", "具体案例演示", "补充练习题"],
  "suggested_difficulty": "intermediate"
}}"""

    def _mock_planning(self) -> str:
        return f"""{{
  "plan_id": "mock-{uuid.uuid4().hex[:8]}",
  "learning_path": [
    {{"order": 1, "kp_id": 3, "kp_name": "理解INNER JOIN", "estimated_time": "30分钟", "resource_type": "讲义", "priority": "high"}},
    {{"order": 2, "kp_id": 5, "kp_name": "掌握OUTER JOIN", "estimated_time": "30分钟", "resource_type": "案例", "priority": "high"}},
    {{"order": 3, "kp_id": 5, "kp_name": "多表连接综合练习", "estimated_time": "45分钟", "resource_type": "习题", "priority": "high"}}
  ],
  "resource_combination": ["讲义×3", "案例×2", "习题×5"],
  "learning_sequence": "由浅入深，先掌握单表查询再扩展到多表连接",
  "estimated_total_time": "约3小时"
}}"""

    def _mock_assessment(self) -> str:
        return f"""{{
  "assessment_id": "mock-{uuid.uuid4().hex[:8]}",
  "test_results": {{"total_questions": 10, "correct_answers": 7, "accuracy_rate": 0.7}},
  "mastery_updates": [
    {{"kp_id": 5, "old_mastery": 0.3, "new_mastery": 0.55, "change_reason": "测验正确率70%，有明显提升"}}
  ],
  "feedback": "多表连接基本概念已掌握，INNER JOIN运用熟练，LEFT JOIN偶有混淆。",
  "suggestions": ["建议增加3道复杂嵌套查询的专项练习"],
  "next_resource_recommendation": "复杂SQL查询专题练习"
}}"""

    def _mock_teacher_review(self) -> str:
        return f"""{{
  "review_id": "mock-{uuid.uuid4().hex[:8]}",
  "quality_score": 8.5,
  "quality_checks": [
    {{"check": "知识点准确性", "passed": true, "note": "SQL连接语法正确，示例无错误"}},
    {{"check": "难度适配性", "passed": true, "note": "适合大二数据库课程学生"}},
    {{"check": "内容完整性", "passed": true, "note": "覆盖了INNER/LEFT/RIGHT/FULL四种连接"}},
    {{"check": "练习题设计", "passed": false, "note": "建议增加练习题数量"}}
  ],
  "risk_alerts": [
    {{"level": "info", "message": "全外连接在某些数据库中语法略有不同"}}
  ],
  "suggestions": ["建议在讲义末尾增加4道练习题"],
  "overall_comment": "资源整体质量良好，建议小幅修改后通过审核。"
}}"""
