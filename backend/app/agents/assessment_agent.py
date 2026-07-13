"""
评测反馈智能体

分析测验结果或学习反馈，生成掌握度评价和改进建议。
"""
import json
import logging
import uuid
from typing import Any, Dict, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_ASSESSMENT = """你是一个专业的学习评测反馈智能体。请根据以下信息，分析学生学习效果并给出改进建议。

## 学生信息
- 姓名：{student_name}
- 当前掌握度：{mastery_score:.0%}
- AI 建议：{ai_suggestions}

## 测验结果
{test_results}

## 学习反馈
{learning_feedback}

## 生成的资源
- 标题：{resource_title}

请以 JSON 格式输出评测反馈：
{{
  "test_results": {{"total_questions": 10, "correct_answers": 7, "accuracy_rate": 0.7}},
  "mastery_updates": [
    {{"kp_id": 5, "old_mastery": 0.3, "new_mastery": 0.55, "change_reason": "测验正确率70%，有明显提升"}}
  ],
  "feedback": "整体学习效果评语（30字以内）",
  "suggestions": ["建议1", "建议2", "建议3"],
  "next_resource_recommendation": "讲义|习题|案例|代码"
}}

要求：
- 若无真实测验数据，test_results 字段填 null，mastery_updates 也填 []
- suggestions：给出 2-3 条具体可行的改进建议（不超过 20 字/条）
- next_resource_recommendation：从"讲义/习题/案例/代码"中选最合适的类型
- 只输出 JSON，不要有其他内容
"""


class AssessmentAgent:
    """评测反馈智能体"""

    AGENT_NAME = "assessment_agent"
    AGENT_DESC = "评测反馈智能体 — 分析学习效果并更新画像"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        test_results: Optional[Dict[str, Any]] = None,
        learning_feedback: Optional[Dict[str, Any]] = None,
        generated_resource: Optional[Dict[str, Any]] = None,
        student_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成评测反馈"""
        logger.info(f"[{self.AGENT_NAME}] 生成评测反馈")

        if student_profile is None:
            student_profile = {}

        has_real_test_data = test_results and test_results.get("total_questions", 0) > 0

        if has_real_test_data:
            total = test_results.get("total_questions", 10)
            accuracy = test_results.get("accuracy_rate", 0.7)
            correct = int(total * accuracy)
            test_text = f"总题数：{total}，正确数：{correct}，正确率：{accuracy:.0%}"
        else:
            test_text = "（暂无测验数据，仅依据资源学习完成情况评估）"

        feedback_text = (
            learning_feedback.get("content", "")[:200]
            if learning_feedback else "（暂无学习反馈）"
        )

        messages = [
            {
                "role": "user",
                "content": PROMPT_ASSESSMENT.format(
                    student_name=student_profile.get("student_name", "未知"),
                    mastery_score=student_profile.get("mastery_score", 0.5),
                    ai_suggestions=student_profile.get("ai_suggestions", "暂无"),
                    test_results=test_text,
                    learning_feedback=feedback_text,
                    resource_title=generated_resource.get("title", "未知") if generated_resource else "未知",
                )
            }
        ]

        result = self._call_llm(messages)
        if result:
            return result
        return self._fallback(accuracy, total, correct, student_profile)

    def _call_llm(self, messages) -> Optional[Dict[str, Any]]:
        if self.llm_gateway is None:
            return None
        try:
            settings = get_settings()
            config = settings.llm_config()
            llm_result = self.llm_gateway.generate(messages, config)
            if llm_result.status == "failed":
                logger.error(f"[{self.AGENT_NAME}] LLM 调用失败: {llm_result.error}")
                return None
            content = llm_result.content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:] if lines[0].startswith("```json") else lines)
                content = content.replace("```", "").strip()
            data = json.loads(content)
            data["assessment_id"] = f"assess-{uuid.uuid4().hex[:8]}"
            logger.info(f"[{self.AGENT_NAME}] LLM 评测完成")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"[{self.AGENT_NAME}] JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"[{self.AGENT_NAME}] LLM 调用异常: {e}")
        return None

    def _fallback(self, accuracy: float, total: int, correct: int, student_profile: Dict) -> Dict[str, Any]:
        if accuracy >= 0.8:
            feedback = "掌握情况良好，建议进入下一阶段学习。"
            mastery_change = 0.15
        elif accuracy >= 0.6:
            feedback = "基本掌握，但仍有提升空间，建议加强练习。"
            mastery_change = 0.05
        else:
            feedback = "掌握不足，建议重新学习相关内容，增加练习量。"
            mastery_change = -0.1

        old_mastery = student_profile.get("mastery_score", 0.3)
        new_mastery = min(1.0, max(0.0, old_mastery + mastery_change))

        return {
            "assessment_id": f"assess-{uuid.uuid4().hex[:8]}",
            "test_results": {
                "total_questions": total,
                "correct_answers": correct,
                "accuracy_rate": accuracy,
            },
            "mastery_updates": [
                {
                    "kp_id": 5,
                    "old_mastery": old_mastery,
                    "new_mastery": new_mastery,
                    "change_reason": f"测验正确率{int(accuracy * 100)}%，{'有明显提升' if mastery_change > 0 else '需继续加强'}"
                }
            ],
            "feedback": feedback,
            "suggestions": [
                "建议增加相关知识点的专项练习",
                "可以观看配套视频教程加深理解",
                "尝试用实际项目来巩固知识"
            ],
            "next_resource_recommendation": "综合练习题或下一知识点讲义"
        }
