"""
学习诊断智能体

分析学生画像、课程知识点和历史反馈，识别薄弱知识点和学习难点。
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_DIAGNOSIS = """你是一个专业的学习诊断智能体。请根据以下学生信息，分析其薄弱知识点。

## 学生画像
- 姓名：{student_name}
- 学号：{student_no}
- 学习目标：{learning_goal}
- 当前基础：{current_level}
- AI 建议：{ai_suggestions}

## 相关知识上下文（RAG 检索结果）
{context}

## 课程知识点掌握情况
{knowledge_points}

## 最近学习任务
{recent_tasks}

请以 JSON 格式输出诊断结果：
{{
  "weak_points": [
    {{"kp_id": 3, "name": "SQL多表连接", "mastery_level": 0.3, "reason": "诊断理由"}}
  ],
  "strength_points": [
    {{"kp_id": 7, "name": "数据库设计基础", "mastery_level": 0.85}}
  ],
  "learning_difficulties": ["学习困难1", "学习困难2"],
  "resource_needs": ["讲义", "练习题", "案例分析"],
  "suggested_difficulty": "intermediate"
}}

要求：
- weak_points：mastery_level < 0.5 的知识点，必填 kp_id 和 reason
- strength_points：mastery_level >= 0.5 的知识点
- learning_difficulties：2-3 个具体学习困难描述
- resource_needs：2-3 种资源类型（讲义/习题/案例/代码/视频）
- suggested_difficulty："basic" / "intermediate" / "advanced"
- 只输出 JSON，不要有其他内容
"""


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

        kp_text = "\n".join(
            f"- [kp_id:{kp.get('kp_id', kp.get('id', 0))}] {kp.get('name', '')} | "
            f"掌握度 {kp.get('mastery_level', kp.get('mastery', 0)):.0%}"
            for kp in knowledge_points
        ) or "（暂无知识点数据）"

        recent_tasks = student_profile.get("recent_tasks", []) or []
        task_text = "\n".join(
            f"- {t.get('title', '')} [状态: {t.get('status', '')}]"
            for t in recent_tasks[:5]
        ) or "（暂无学习任务记录）"

        rag_context = self._retrieve_rag_context(student_profile, knowledge_points)

        messages = [
            {
                "role": "user",
                "content": PROMPT_DIAGNOSIS.format(
                    student_name=student_profile.get("student_name", "未知"),
                    student_no=student_profile.get("student_no", ""),
                    learning_goal=student_profile.get("learning_goal", "未设置"),
                    current_level=student_profile.get("current_level", "未知"),
                    ai_suggestions=student_profile.get("ai_suggestions", "暂无"),
                    context=rag_context,
                    knowledge_points=kp_text,
                    recent_tasks=task_text,
                )
            }
        ]

        result = self._call_llm(messages)

        if result:
            return result

        return self._fallback(knowledge_points)

    def _retrieve_rag_context(
        self,
        student_profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
    ) -> str:
        try:
            from app.services.rag_service import get_context_for_agent

            course_id = student_profile.get("course_id")
            weak_names = [
                kp.get("name", "") for kp in knowledge_points
                if kp.get("mastery_level", 1.0) < 0.5
            ]
            query = "、".join(weak_names[:3]) if weak_names else (
                student_profile.get("learning_goal") or student_profile.get("student_name", "")
            )

            if not query:
                return "（暂无相关知识点上下文）"

            context = get_context_for_agent(query=query, course_id=course_id, top_k=5)
            if context:
                logger.info(f"[{self.AGENT_NAME}] RAG 检索到 {len(context.splitlines())} 行上下文")
                return context
            return "（RAG 检索结果为空）"
        except Exception as e:
            logger.warning(
                "[%s] RAG 检索失败，回退到无上下文 (%s)",
                self.AGENT_NAME,
                type(e).__name__,
            )
            return "（RAG 检索暂不可用）"

    def _call_llm(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        if self.llm_gateway is None:
            logger.warning(f"[{self.AGENT_NAME}] llm_gateway 未注入，使用规则回退")
            return None

        try:
            settings = get_settings()
            config = settings.llm_config()
            llm_result = self.llm_gateway.generate(messages, config)
            if llm_result.status == "failed":
                logger.error("[%s] LLM 调用失败", self.AGENT_NAME)
                return None
            content = llm_result.content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:] if lines[0].startswith("```json") else lines)
                content = content.replace("```", "").strip()
            data = json.loads(content)
            data["diagnosis_id"] = f"diag-{uuid.uuid4().hex[:8]}"
            logger.info(f"[{self.AGENT_NAME}] LLM 诊断完成: {len(data.get('weak_points', []))} 个薄弱点")
            return data
        except json.JSONDecodeError as e:
            logger.error(
                "[%s] LLM 返回 JSON 解析失败 (%s)",
                self.AGENT_NAME,
                type(e).__name__,
            )
        except Exception as e:
            logger.error("[%s] LLM 调用异常 (%s)", self.AGENT_NAME, type(e).__name__)
        return None

    def _fallback(self, knowledge_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        weak_points = []
        strong_points = []

        for kp in knowledge_points:
            mastery = kp.get("mastery_level", kp.get("mastery", 0.5))
            if mastery < 0.5:
                weak_points.append({
                    "kp_id": kp.get("kp_id", kp.get("id", 0)),
                    "name": kp.get("name", ""),
                    "mastery_level": mastery,
                    "reason": f"掌握度 {mastery:.0%}，低于阈值"
                })
            else:
                strong_points.append({
                    "kp_id": kp.get("kp_id", kp.get("id", 0)),
                    "name": kp.get("name", ""),
                    "mastery_level": mastery
                })

        return {
            "diagnosis_id": f"diag-{uuid.uuid4().hex[:8]}",
            "weak_points": weak_points,
            "strength_points": strong_points,
            "learning_difficulties": ["多表连接时条件判断容易混淆", "子查询嵌套层次过深难以理解"],
            "resource_needs": ["图文并茂的讲义", "具体案例演示", "补充练习题"],
            "suggested_difficulty": "intermediate"
        }
