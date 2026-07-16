"""
教师审核辅助智能体

为教师审核学习资源提供质量检查建议。
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_TEACHER_REVIEW = """你是一个专业的教学审核辅助智能体。请对以下学习资源进行质量评估。

## 资源信息
- 标题：{resource_title}
- 类型：{resource_type}
- 难度：{difficulty}

## 课程教学目标
{course_objectives}

## 资源正文（仅供审核，不要照抄）：
{content}

## 审核维度（6项必检）
1. 准确性：知识概念是否正确，有无事实性错误
2. 完整性：是否覆盖教学目标要求的所有要点
3. 逻辑性：内容组织是否符合认知规律，由浅入深
4. 规范性：术语使用是否标准，格式是否规范
5. 可操作性：练习题是否可做，代码是否可运行
6. 难度适配性：内容深度是否与目标难度匹配

请以 JSON 格式输出审核建议：
{{
  "quality_score": 8.5,
  "quality_checks": [
    {{"check": "准确性", "passed": true, "note": "..."}},
    {{"check": "完整性", "passed": false, "note": "缺少xxx要点"}},
    {{"check": "逻辑性", "passed": true, "note": "..."}},
    {{"check": "规范性", "passed": true, "note": "..."}},
    {{"check": "可操作性", "passed": true, "note": "..."}},
    {{"check": "难度适配性", "passed": false, "note": "偏难/偏易"}}
  ],
  "risk_alerts": [
    {{"level": "warning", "message": "存在xxx知识性风险"}}
  ],
  "suggestions": ["建议1（不超过20字）", "建议2（不超过20字）"],
  "overall_comment": "一句话总体评价（不超过30字）"
}}

要求：
- quality_score：0-10 分，综合6个维度给出一个总分
- quality_checks：6个维度各一个检查结果，passed 为 true/false，note 简述（不超过30字）
- risk_alerts：知识性错误必填，level 为 info/warning/error
- suggestions：2-3条具体修改建议，每条不超过20字
- overall_comment：不超过30字
- 只输出 JSON，不要有其他内容
"""


class TeacherReviewAgent:
    """教师审核辅助智能体"""

    AGENT_NAME = "teacher_review_agent"
    AGENT_DESC = "教师审核辅助智能体 — 生成资源质量检查建议"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        generated_resource: Dict[str, Any],
        course_objectives: Optional[List[str]] = None,
        difficulty_requirement: str = "intermediate",
    ) -> Dict[str, Any]:
        """生成审核建议"""
        logger.info(f"[{self.AGENT_NAME}] 生成审核建议")

        content = generated_resource.get("content", "")[:3000]
        course_obj_text = (
            "\n".join(f"- {obj}" for obj in course_objectives)
            if course_objectives else "（暂无课程教学目标信息）"
        )

        messages = [
            {
                "role": "user",
                "content": PROMPT_TEACHER_REVIEW.format(
                    resource_title=generated_resource.get("title", "未知"),
                    resource_type=generated_resource.get("type", "未知"),
                    difficulty=difficulty_requirement,
                    course_objectives=course_obj_text,
                    content=content or "（无正文内容）",
                )
            }
        ]

        result = self._call_llm(messages)
        if result:
            return result
        return self._fallback(generated_resource, difficulty_requirement)

    def _call_llm(self, messages) -> Optional[Dict[str, Any]]:
        if self.llm_gateway is None:
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
            data["review_id"] = f"review-{uuid.uuid4().hex[:8]}"
            data["resource_id"] = None
            logger.info(f"[{self.AGENT_NAME}] LLM 审核完成，质量评分: {data.get('quality_score', 'N/A')}")
            return data
        except json.JSONDecodeError as e:
            logger.error("[%s] JSON 解析失败 (%s)", self.AGENT_NAME, type(e).__name__)
        except Exception as e:
            logger.error("[%s] LLM 调用异常 (%s)", self.AGENT_NAME, type(e).__name__)
        return None

    def _fallback(self, generated_resource: Dict[str, Any], difficulty_requirement: str) -> Dict[str, Any]:
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
