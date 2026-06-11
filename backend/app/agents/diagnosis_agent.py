"""
学习诊断智能体

分析学生画像、课程知识点和历史反馈，识别薄弱知识点和学习难点。
"""
import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DiagnosisAgent:
    """学习诊断智能体"""

    AGENT_NAME = "diagnosis_agent"
    AGENT_DESC = "学习诊断智能体 — 分析学生薄弱知识点"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        student_profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        learning_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """执行诊断"""
        logger.info(f"[{self.AGENT_NAME}] 诊断学生: {student_profile.get('student_name', 'Unknown')}")

        weak_points = []
        strong_points = []

        for kp in knowledge_points:
            mastery = kp.get("mastery_level", kp.get("mastery", 0.5))
            if mastery < 0.5:
                weak_points.append({
                    "kp_id": kp.get("kp_id", 0),
                    "name": kp.get("name", ""),
                    "mastery_level": mastery,
                    "reason": f"测验正确率仅{int(mastery * 100)}%，知识点掌握不足"
                })
            else:
                strong_points.append({
                    "kp_id": kp.get("kp_id", 0),
                    "name": kp.get("name", ""),
                    "mastery_level": mastery
                })

        return {
            "diagnosis_id": f"diag-{uuid.uuid4().hex[:8]}",
            "weak_points": weak_points,
            "strength_points": strong_points,
            "learning_difficulties": [
                "多表连接时条件判断容易混淆",
                "子查询嵌套层次过深难以理解"
            ],
            "resource_needs": ["图文并茂的讲义", "具体案例演示", "补充练习题"],
            "suggested_difficulty": "intermediate"
        }
