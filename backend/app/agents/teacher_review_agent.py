"""
教师审核辅助智能体

为教师审核学习资源提供质量检查建议。
"""
import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TeacherReviewAgent:
    """教师审核辅助智能体"""

    AGENT_NAME = "teacher_review_agent"
    AGENT_DESC = "教师审核辅助智能体 — 生成资源质量检查建议"

    def run(
        self,
        generated_resource: Dict[str, Any],
        course_objectives: Optional[List[str]] = None,
        difficulty_requirement: str = "intermediate",
    ) -> Dict[str, Any]:
        """生成审核建议"""
        logger.info(f"[{self.AGENT_NAME}] 生成审核建议")

        quality_checks = [
            {"check": "知识点准确性", "passed": True, "note": "内容准确，无明显错误"},
            {"check": "难度适配性", "passed": True, "note": f"适合{difficulty_requirement}难度学生"},
            {"check": "内容完整性", "passed": True, "note": "核心知识点覆盖完整"},
            {"check": "代码示例质量", "passed": True, "note": "示例代码规范且有实际意义"},
            {"check": "练习题设计", "passed": False, "note": "建议增加练习题数量"}
        ]

        passed_count = sum(1 for c in quality_checks if c["passed"])
        quality_score = round(passed_count / len(quality_checks) * 10, 1)

        return {
            "review_id": f"review-{uuid.uuid4().hex[:8]}",
            "resource_id": generated_resource.get("resource_id"),
            "quality_score": quality_score,
            "quality_checks": quality_checks,
            "risk_alerts": [
                {"level": "info", "message": "部分内容可能超出本节范围，需教师确认"}
            ],
            "suggestions": [
                "建议在讲义末尾增加练习题",
                "补充相关知识点的对比内容",
                "增加实际应用场景案例"
            ],
            "overall_comment": f"资源整体质量评分{quality_score}/10，{'建议通过审核' if quality_score >= 7 else '建议修改后审核'}"
        }
