"""
资源规划智能体

根据诊断结果生成学习路径和资源组合方案。
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_PLANNING = """你是一个专业的学习规划智能体。请根据以下诊断结果，为学生设计个性化学习路径。

## 学生信息
- 姓名：{student_name}
- 当前水平：{current_level}
- 学习目标：{learning_goal}
- 综合掌握度：{mastery_score}

## 课程知识点
{course_outline}

## 薄弱知识点（优先攻克）
{weak_points}

## 资源类型说明
- 讲义：理论概念讲解，适合打基础
- 案例：实际应用举例，帮助理解
- 习题：练习巩固，检验掌握
- 代码：动手实践，提升动手能力

请以 JSON 格式输出学习规划：
{{
  "learning_path": [
    {{
      "order": 1,
      "kp_id": 5,
      "kp_name": "SQL多表连接",
      "estimated_time": "30分钟",
      "resource_type": "讲义+案例+习题",
      "priority": "high",
      "learning_objective": "理解并熟练使用INNER JOIN和LEFT JOIN"
    }}
  ],
  "resource_combination": ["讲义×2", "案例×1", "习题×3"],
  "learning_sequence": "由浅入深，先理解基础概念再掌握实际应用",
  "estimated_total_time": "约3小时"
}}

要求：
- learning_path 按 priority 从高到低排序（high/medium/low）
- 每个步骤需包含：kp_id、estimated_time、resource_type、learning_objective
- resource_type 从"讲义/案例/习题/代码"中选择 1-3 种组合
- learning_sequence 描述整体学习策略（不超过 50 字）
- 只输出 JSON，不要有其他内容
"""


class PlanningAgent:
    """资源规划智能体"""

    AGENT_NAME = "planning_agent"
    AGENT_DESC = "资源规划智能体 — 生成个性化学习路径"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        diagnosis: Dict[str, Any],
        learning_goal: str,
        course_outline: List[Dict[str, Any]],
        student_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成学习路径规划"""
        logger.info(f"[{self.AGENT_NAME}] 规划学习路径")
        if student_profile is None:
            student_profile = {}

        outline_text = "\n".join(
            f"- [kp_id:{kp.get('kp_id', kp.get('id', 0))}] {kp.get('name', '')}"
            for kp in course_outline
        ) or "（暂无课程大纲）"

        weak_points = diagnosis.get("weak_points", [])
        wp_text = "\n".join(
            f"- [kp_id:{wp.get('kp_id', 0)}] {wp.get('name', '')} | "
            f"掌握度 {wp.get('mastery_level', 0):.0%}"
            for wp in weak_points
        ) or "（无薄弱知识点）"

        messages = [
            {
                "role": "user",
                "content": PROMPT_PLANNING.format(
                    student_name=student_profile.get("student_name", "同学"),
                    current_level=student_profile.get("current_level", "未知"),
                    mastery_score=student_profile.get("mastery_score", 0),
                    learning_goal=learning_goal or "暂无",
                    course_outline=outline_text,
                    weak_points=wp_text,
                )
            }
        ]

        result = self._call_llm(messages)
        if result:
            return result
        return self._fallback(weak_points, diagnosis)

    def _call_llm(self, messages: List[Dict[str, str]]) -> Dict[str, Any] | None:
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
            data["plan_id"] = f"plan-{uuid.uuid4().hex[:8]}"
            logger.info(f"[{self.AGENT_NAME}] LLM 规划完成: {len(data.get('learning_path', []))} 个步骤")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"[{self.AGENT_NAME}] JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"[{self.AGENT_NAME}] LLM 调用异常: {e}")
        return None

    def _fallback(self, weak_points: List[Dict], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
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
