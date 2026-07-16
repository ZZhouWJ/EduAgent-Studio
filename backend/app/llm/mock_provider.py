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
            return self._mock_diagnosis(input_text)
        if "专业的教育资源生成智能体" in input_text or (
            "教材原文依据" in input_text and "直接输出 Markdown" in input_text
        ):
            return self._mock_resource(input_text, model_name)
        if "专业的学习规划智能体" in input_text:
            return self._mock_planning(input_text)
        if "专业的学习评测反馈智能体" in input_text:
            return self._mock_assessment()
        if "专业的教学审核辅助智能体" in input_text:
            return self._mock_teacher_review()
        if "诊断" in normalized_input or "薄弱" in normalized_input:
            return self._mock_diagnosis(input_text)
        if "规划" in normalized_input or "路径" in normalized_input:
            return self._mock_planning(input_text)
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

    def _mock_diagnosis(self, prompt: str = "") -> str:
        knowledge_points = self._extract_prompt_knowledge_points(
            prompt, "课程知识点掌握情况", "最近学习任务", include_mastery=True
        )
        if not knowledge_points:
            knowledge_points = [
                {"kp_id": 5, "name": "SQL多表连接", "mastery_level": 0.3},
                {"kp_id": 8, "name": "事务隔离级别", "mastery_level": 0.2},
                {"kp_id": 2, "name": "SQL基本查询", "mastery_level": 0.85},
            ]

        weak_points = [
            {
                **kp,
                "reason": f"当前掌握度仅{kp['mastery_level']:.0%}，需要优先补强",
            }
            for kp in knowledge_points if kp["mastery_level"] < 0.5
        ]
        strength_points = [
            kp for kp in knowledge_points if kp["mastery_level"] >= 0.5
        ]
        focus_names = "、".join(kp["name"] for kp in weak_points[:3]) or "当前知识点"
        result = {
            "diagnosis_id": f"mock-{uuid.uuid4().hex[:8]}",
            "weak_points": weak_points,
            "strength_points": strength_points,
            "learning_difficulties": [
                f"{focus_names}的概念边界需要进一步澄清",
                f"需要通过案例巩固{focus_names}的应用条件",
            ],
            "resource_needs": ["图文并茂的讲义", "具体案例演示", "补充练习题"],
            "suggested_difficulty": "intermediate",
        }
        return json.dumps(result, ensure_ascii=False)

    def _mock_planning(self, prompt: str = "") -> str:
        knowledge_points = self._extract_prompt_knowledge_points(
            prompt, "薄弱知识点（优先攻克）", "资源类型说明", include_mastery=True
        )
        if not knowledge_points:
            knowledge_points = self._extract_prompt_knowledge_points(
                prompt, "课程知识点", "薄弱知识点（优先攻克）", include_mastery=False
            )
        if not knowledge_points:
            knowledge_points = [
                {"kp_id": 5, "name": "SQL多表连接", "mastery_level": 0.3}
            ]

        learning_path = []
        for index, kp in enumerate(knowledge_points, start=1):
            resource_type = "讲义+案例+习题" if any(
                marker in kp["name"] for marker in ("事务", "锁", "查询", "连接", "代码")
            ) else "讲义+习题"
            learning_path.append({
                "order": index,
                "kp_id": kp["kp_id"],
                "kp_name": kp["name"],
                "estimated_time": "40分钟",
                "resource_type": resource_type,
                "priority": "high" if index <= 2 else "medium",
                "learning_objective": f"理解{kp['name']}并能够完成基础应用",
            })

        result = {
            "plan_id": f"mock-{uuid.uuid4().hex[:8]}",
            "learning_path": learning_path,
            "resource_combination": ["讲义×1", "案例×1", "习题×3"],
            "learning_sequence": "先澄清核心概念，再通过案例和练习完成迁移应用",
            "estimated_total_time": f"约{len(learning_path) * 40}分钟",
        }
        return json.dumps(result, ensure_ascii=False)

    def _extract_prompt_knowledge_points(
        self,
        prompt: str,
        start_heading: str,
        end_heading: str,
        include_mastery: bool,
    ) -> List[Dict[str, Any]]:
        section_match = re.search(
            rf"##\s*{re.escape(start_heading)}\s*(.*?)\s*##\s*{re.escape(end_heading)}",
            prompt,
            re.DOTALL,
        )
        if not section_match:
            return []

        section = section_match.group(1)
        pattern = r"-\s*\[kp_id:(\d+)\]\s*([^|\n]+)"
        if include_mastery:
            pattern += r"\s*\|\s*掌握度\s*(\d+(?:\.\d+)?)%"

        points = []
        for match in re.finditer(pattern, section):
            mastery = float(match.group(3)) / 100 if include_mastery else 0.5
            points.append({
                "kp_id": int(match.group(1)),
                "name": match.group(2).strip(),
                "mastery_level": mastery,
            })
        return points

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
