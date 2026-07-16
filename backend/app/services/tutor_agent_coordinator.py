"""
Tutor Agent 编排器

负责：
1. 意图识别 - 决定生成哪些资源类型
2. 主讲解生成 - LLM 直接生成 Markdown 讲义
3. 资源生成 - 复用 ResourceGenerationAgent 按类型生成
4. 结果组装 - 组装 content_blocks 返回
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.llm.gateway import LLMGateway
from app.llm.runtime import get_runtime_llm_gateway

logger = logging.getLogger(__name__)

# 意图识别 Prompt
INTENT_RECOGNITION_PROMPT = """你是一个学习辅导意图识别智能体。请分析学生问题，判断需要生成哪些类型的学习资源。

## 学生问题
{question}

## 学生画像
- 当前水平：{current_level}
- 薄弱知识点：{weak_points}
- 资源偏好：{resource_preferences}

## 可选资源类型（选1-3种，按需组合）
- lecture: 知识点讲义（理论讲解）
- mindmap: 思维导图（知识结构化）
- quiz: 分层练习题
- code_case: 代码实操案例
- ppt: PPT 大纲
- video_script: 视频/动画脚本
- experiment_report: 实验报告
- error_analysis: 错题解析
- learning_card: 学习卡片

## 判断规则
- 简单概念问题 → lecture
- 需要动手实践 → lecture + code_case
- 需要巩固练习 → lecture + quiz
- 需要理解结构关系 → lecture + mindmap
- 复杂综合问题 → lecture + mindmap + code_case + quiz

## 输出要求
只输出 JSON，不要其他内容：
{{
  "primary_intent": "explanation/practice/review/code_demo/mixed",
  "resource_types": ["lecture", "mindmap"],
  "kp_ids": [],
  "difficulty": "basic/intermediate/advanced",
  "reasoning": "不超过30字"
}}"""

# 主讲解生成 Prompt
MAIN_EXPLANATION_PROMPT = """你是一个耐心的 AI 学习辅导老师。请根据学生的问题和背景知识，给出清晰、全面的讲解。

## 学生问题
{question}

## 学生背景
- 当前课程：{course_name}
- 当前水平：{current_level}
- 薄弱知识点：{weak_points}

## 参考知识库内容
{context}

## 要求
1. 用 Markdown 格式回答，包含代码示例和图示说明
2. 难度要适配学生的当前水平
3. 在适当位置用 [引用:chunk_id] 标注知识库来源
4. 生成完毕后，如果生成了练习题，在最后列出 2-3 道巩固练习

请开始回答："""


class TutorAgentCoordinator:
    """Tutor 多智能体编排器"""

    def __init__(self, llm_gateway: Optional[LLMGateway] = None):
        self._llm = llm_gateway or get_runtime_llm_gateway()

    async def orchestrate(
        self,
        question: str,
        profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        context: str,
        requested_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        编排多智能体生成内容。

        Returns: {
            "intent": IntentResult dict,
            "content_blocks": List[ContentBlock dict],
            "main_answer": str (Markdown 主讲解),
            "citations": List[Citation dict],
        }
        """
        # 1. 意图识别
        intent = await self._recognize_intent(question, profile, knowledge_points, requested_types)
        resource_types = intent.get("resource_types", ["lecture"])

        # 2. 生成主讲解
        main_result = await self._generate_main_explanation(
            question, profile, knowledge_points, context
        )
        main_answer = main_result.get("answer", "")
        citations = main_result.get("citations", [])

        # 3. 并发生成其他资源类型（lecture 已在主讲解中）
        content_blocks = []
        other_types = [rt for rt in resource_types if rt != "lecture"]

        if other_types:
            tasks = [
                self._generate_resource_block(rt, intent, profile, knowledge_points)
                for rt in other_types
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, Exception):
                    logger.error(f"Resource generation error: {r}")
                else:
                    content_blocks.append(r)

        return {
            "intent": intent,
            "content_blocks": content_blocks,
            "main_answer": main_answer,
            "citations": citations,
        }

    async def _recognize_intent(
        self,
        question: str,
        profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        requested_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """意图识别 - 调用 LLM 判断需要生成哪些资源"""
        # 如果学生明确指定了类型，直接用
        if requested_types:
            return {
                "primary_intent": "mixed",
                "resource_types": requested_types[:3],
                "kp_ids": [],
                "difficulty": "intermediate",
                "reasoning": "学生指定",
            }

        weak_points = profile.get("weak_points", [])
        weak_kp_names = [wp.get("kp_name", "") if isinstance(wp, dict) else str(wp) for wp in weak_points[:3]]
        resource_prefs = profile.get("resource_preferences", [])

        prompt = INTENT_RECOGNITION_PROMPT.format(
            question=question,
            current_level=profile.get("current_level", "大二"),
            weak_points=", ".join(weak_kp_names) or "暂无记录",
            resource_preferences=", ".join(resource_prefs) or "暂无偏好",
        )

        try:
            config = get_settings().llm_config()
            config.temperature = 0.3
            config.max_tokens = 300
            result = self._llm.generate(
                messages=[{"role": "user", "content": prompt}],
                config=config,
            )
            text = result.content.strip() if hasattr(result, "content") else str(result)

            # 提取 JSON
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                intent_data = json.loads(json_match.group())
                return intent_data
        except Exception as e:
            logger.warning("意图识别失败，使用默认策略 (%s)", type(e).__name__)

        # Fallback：默认生成讲义 + 练习题
        return {
            "primary_intent": "mixed",
            "resource_types": ["lecture", "quiz"],
            "kp_ids": [],
            "difficulty": "intermediate",
            "reasoning": "默认策略",
        }

    async def _generate_main_explanation(
        self,
        question: str,
        profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        context: str,
    ) -> Dict[str, Any]:
        """生成主讲解 Markdown"""
        prompt = MAIN_EXPLANATION_PROMPT.format(
            question=question,
            course_name=profile.get("course_name", "课程"),
            current_level=profile.get("current_level", "大二"),
            weak_points=", ".join([
                wp.get("kp_name", "") if isinstance(wp, dict) else str(wp)
                for wp in profile.get("weak_points", [])[:3]
            ]) or "暂无",
            context=context or "无参考内容",
        )

        try:
            config = get_settings().llm_config()
            config.temperature = 0.7
            config.max_tokens = 2000
            result = self._llm.generate(
                messages=[{"role": "user", "content": prompt}],
                config=config,
            )
            text = result.content if hasattr(result, "content") else str(result)

            # 提取引用
            citations = []
            chunk_pattern = re.compile(r"\[引用:(\d+)\]")
            for match in chunk_pattern.finditer(text):
                chunk_id = int(match.group(1))
                citations.append({
                    "chunk_id": chunk_id,
                    "content": f"知识点 ID {chunk_id} 相关内容",
                    "source": "课程知识库",
                })

            return {"answer": text, "citations": citations}
        except Exception as e:
            logger.error("主讲解生成失败 (%s)", type(e).__name__)
            return {"answer": f"抱歉，无法回答该问题：{question}", "citations": []}

    async def _generate_resource_block(
        self,
        resource_type: str,
        intent: Dict[str, Any],
        profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """调用 ResourceGenerationAgent 生成单个资源块"""
        try:
            from app.agents.resource_generation_agent import ResourceGenerationAgent

            agent = ResourceGenerationAgent(self._llm)
            difficulty = intent.get("difficulty", "intermediate")

            # 构建 learning_path（只用知识点基本信息）
            learning_path = [
                {
                    "kp_id": kp.get("id", 0),
                    "kp_name": kp.get("name", ""),
                    "mastery_level": kp.get("mastery_avg", 0.5),
                }
                for kp in knowledge_points
            ]

            result = agent.run(
                learning_path=learning_path,
                resource_type=resource_type,
                difficulty=difficulty,
                student_profile=profile,
                course_id=profile.get("course_id"),
            )

            block_id = f"block_{resource_type}_{profile.get('profile_id', 0)}"
            return {
                "block_id": block_id,
                "block_type": resource_type,
                "title": self._type_to_title(resource_type),
                "content": result.get("content", ""),
                "metadata": {
                    "quality_score": result.get("quality_score", 0.7),
                },
                "quality_score": result.get("quality_score", 0.7),
                "trustworthiness": result.get("trustworthiness", "medium"),
            }
        except Exception as e:
            logger.error("资源生成失败 [%s] (%s)", resource_type, type(e).__name__)
            return {
                "block_id": f"block_{resource_type}_error",
                "block_type": resource_type,
                "title": self._type_to_title(resource_type),
                "content": "生成失败，请稍后重试",
                "metadata": {"error": "resource_generation_failed"},
                "quality_score": 0,
                "trustworthiness": "draft",
            }

    def _type_to_title(self, resource_type: str) -> str:
        titles = {
            "lecture": "知识讲义",
            "mindmap": "思维导图",
            "quiz": "练习题",
            "code_case": "代码案例",
            "ppt": "PPT 大纲",
            "video_script": "视频脚本",
            "experiment_report": "实验报告",
            "error_analysis": "错题解析",
            "learning_card": "学习卡片",
        }
        return titles.get(resource_type, resource_type)
