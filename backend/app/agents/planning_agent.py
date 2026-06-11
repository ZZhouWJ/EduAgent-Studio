"""
资源规划智能体

根据诊断结果生成学习路径和资源组合方案。
"""
import logging
import uuid
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PlanningAgent:
    """资源规划智能体"""

    AGENT_NAME = "planning_agent"
    AGENT_DESC = "资源规划智能体 — 生成个性化学习路径"

    def run(
        self,
        diagnosis: Dict[str, Any],
        learning_goal: str,
        course_outline: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """生成学习路径规划"""
        logger.info(f"[{self.AGENT_NAME}] 规划学习路径")

        weak_points = diagnosis.get("weak_points", [])
        suggested_difficulty = diagnosis.get("suggested_difficulty", "intermediate")
        base_times = {"basic": 20, "intermediate": 40, "advanced": 60}

        learning_path = []
        order = 1
        for wp in weak_points:
            kp_name = wp.get("name", "")
            minutes = base_times.get(suggested_difficulty, 40)
            resource_type = "讲义"
            if "连接" in kp_name or "查询" in kp_name:
                resource_type = "讲义+案例"
            learning_path.append({
                "order": order,
                "kp_id": wp.get("kp_id", 0),
                "kp_name": kp_name,
                "estimated_time": f"{minutes}分钟",
                "resource_type": resource_type,
                "priority": "high" if order <= 2 else "medium"
            })
            order += 1

        return {
            "plan_id": f"plan-{uuid.uuid4().hex[:8]}",
            "learning_path": learning_path,
            "resource_combination": ["讲义×2", "案例×1", "习题×3"],
            "learning_sequence": "由浅入深，先理解基础概念再掌握实际应用",
            "estimated_total_time": f"约{sum(base_times.values()) // len(base_times)}分钟"
        }
