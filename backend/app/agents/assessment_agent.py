"""
评测反馈智能体

分析测验结果或学习反馈，生成掌握度评价和改进建议。
"""
import logging
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AssessmentAgent:
    """评测反馈智能体"""

    AGENT_NAME = "assessment_agent"
    AGENT_DESC = "评测反馈智能体 — 分析学习效果并更新画像"

    def run(
        self,
        test_results: Optional[Dict[str, Any]] = None,
        learning_feedback: Optional[Dict[str, Any]] = None,
        generated_resource: Optional[Dict[str, Any]] = None,
        student_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成评测反馈"""
        logger.info(f"[{self.AGENT_NAME}] 生成评测反馈")

        accuracy = 0.7
        total = 10
        correct = 7

        if test_results:
            total = test_results.get("total_questions", 10)
            accuracy = test_results.get("accuracy_rate", 0.7)
            correct = int(total * accuracy)

        if accuracy >= 0.8:
            feedback = "掌握情况良好，建议进入下一阶段学习。"
            mastery_change = 0.15
        elif accuracy >= 0.6:
            feedback = "基本掌握，但仍有提升空间，建议加强练习。"
            mastery_change = 0.05
        else:
            feedback = "掌握不足，建议重新学习相关内容，增加练习量。"
            mastery_change = -0.1

        old_mastery = student_profile.get("mastery_score", 0.3) if student_profile else 0.3
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
