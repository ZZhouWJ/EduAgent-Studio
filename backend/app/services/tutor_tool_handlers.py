"""
Tutor 工具处理器

每个工具/Agent/Skill 的具体实现。
所有处理器都遵循统一的 async def handler(...) 签名。
"""

import logging
from typing import Any, Dict, List, Optional

from app.llm.gateway import LLMGateway, llm_gateway as _default_llm
from app.repositories.knowledge_repo import KnowledgeRepository
from app.repositories.profile_repo import ProfileRepository

logger = logging.getLogger(__name__)


def _get_llm() -> Optional[LLMGateway]:
    try:
        return _default_llm
    except Exception:
        return None


# =============================================================================
# Tool 实现
# =============================================================================


async def retrieve_knowledge(
    course_id: int,
    query: str,
    limit: int = 5,
) -> Dict[str, Any]:
    """检索课程知识库"""
    try:
        repo = KnowledgeRepository()
        chunks = repo.search_chunks(course_id=course_id, query=query, limit=limit)
        return {
            "chunks": [
                {
                    "chunk_id": c.get("chunk_id", 0),
                    "content": c.get("content", "")[:200],
                    "source": c.get("source_page") or c.get("source_paragraph") or "教材",
                    "title": c.get("title", ""),
                }
                for c in chunks
            ],
            "count": len(chunks),
        }
    except Exception as e:
        logger.error(f"retrieve_knowledge failed: {e}")
        return {"chunks": [], "count": 0, "error": str(e)}


# =============================================================================
# Agent 实现
# =============================================================================


async def quiz_agent(
    course_id: int,
    knowledge_point_ids: List[int],
    question_count: int = 3,
    difficulty: str = "intermediate",
    student_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """自适应题库生成 Agent"""
    try:
        from app.agents.resource_generation_agent import ResourceGenerationAgent

        llm = _get_llm()
        agent = ResourceGenerationAgent(llm)

        learning_path = [
            {"kp_id": kpid, "kp_name": f"kp#{kpid}", "mastery_level": 0.5}
            for kpid in knowledge_point_ids
        ]

        result = agent.run(
            learning_path=learning_path,
            resource_type="quiz",
            difficulty=difficulty,
            student_profile=student_profile or {},
            course_id=course_id,
        )

        return {
            "content": result.get("content", ""),
            "quality_score": result.get("quality_score", 0.7),
            "trustworthiness": result.get("trustworthiness", "medium"),
            "questions": _extract_questions(result.get("content", "")),
        }
    except Exception as e:
        logger.error(f"quiz_agent failed: {e}")
        return {"content": f"题目生成失败：{e}", "questions": [], "quality_score": 0}


async def code_case_agent(
    course_id: int,
    knowledge_point_ids: List[int],
    language: str = "Python",
    student_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """代码案例生成 Agent"""
    try:
        from app.agents.resource_generation_agent import ResourceGenerationAgent

        llm = _get_llm()
        agent = ResourceGenerationAgent(llm)

        learning_path = [
            {"kp_id": kpid, "kp_name": f"kp#{kpid}", "mastery_level": 0.5}
            for kpid in knowledge_point_ids
        ]

        result = agent.run(
            learning_path=learning_path,
            resource_type="code_case",
            difficulty="intermediate",
            student_profile=student_profile or {},
            course_id=course_id,
        )

        return {
            "content": result.get("content", ""),
            "language": language,
            "quality_score": result.get("quality_score", 0.7),
            "trustworthiness": result.get("trustworthiness", "medium"),
        }
    except Exception as e:
        logger.error(f"code_case_agent failed: {e}")
        return {"content": f"代码案例生成失败：{e}", "language": language, "quality_score": 0}


async def mindmap_agent(
    course_id: int,
    knowledge_point_ids: List[int],
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """思维导图生成 Agent"""
    try:
        from app.agents.resource_generation_agent import ResourceGenerationAgent

        llm = _get_llm()
        agent = ResourceGenerationAgent(llm)

        learning_path = [
            {"kp_id": kpid, "kp_name": f"kp#{kpid}", "mastery_level": 0.5}
            for kpid in knowledge_point_ids
        ]

        result = agent.run(
            learning_path=learning_path,
            resource_type="mindmap",
            difficulty="intermediate",
            student_profile={},
            course_id=course_id,
        )

        return {
            "content": result.get("content", ""),
            "quality_score": result.get("quality_score", 0.7),
            "trustworthiness": result.get("trustworthiness", "medium"),
        }
    except Exception as e:
        logger.error(f"mindmap_agent failed: {e}")
        return {"content": f"思维导图生成失败：{e}", "quality_score": 0}


async def planning_agent(
    course_id: int,
    target_kp_ids: List[int],
    student_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """学习路径规划 Agent"""
    try:
        from app.agents.planning_agent import PlanningAgent
        from app.agents.diagnosis_agent import DiagnosisAgent

        llm = _get_llm()
        profile_repo = ProfileRepository()

        # 获取学生画像
        profile = student_profile
        if not profile and student_profile:
            pid = student_profile.get("profile_id")
            if pid:
                profile = profile_repo.get_profile(pid)

        # 获取知识点
        knowledge_points = _get_course_kps(course_id)

        # 先诊断
        diagnosis_agent = DiagnosisAgent(llm)
        diagnosis = diagnosis_agent.run(
            student_profile=profile or {},
            knowledge_points=knowledge_points,
        )

        # 再规划
        planning_agent_inst = PlanningAgent(llm)
        plan = planning_agent_inst.run(
            diagnosis=diagnosis,
            learning_goal=profile.get("learning_goal", "") if profile else "",
            course_outline=knowledge_points,
            student_profile=profile,
        )

        return {
            "content": _format_learning_path(plan.get("learning_path", [])),
            "diagnosis_summary": diagnosis.get("summary", ""),
            "quality_score": 0.8,
            "trustworthiness": "high",
        }
    except Exception as e:
        logger.error(f"planning_agent failed: {e}")
        return {"content": f"学习路径规划失败：{e}", "quality_score": 0}


async def error_analysis_agent(
    student_profile: Optional[Dict[str, Any]] = None,
    error_description: str = "",
    related_kp_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """错因分析 Agent"""
    if not error_description:
        return {"content": "请提供错题描述", "error_type": "unknown", "suggestions": []}

    try:
        llm = _get_llm()
        if not llm:
            return {
                "content": f"【错因分析】\n\n错误描述：{error_description}\n\n可能的原因：概念理解偏差 / 编码习惯错误 / 边界条件遗漏",
                "error_type": "analysis_failed",
                "suggestions": ["请查看相关知识点讲解"],
            }

        prompt = f"""你是一个专业的错因分析辅导老师。请分析以下错误的根本原因。

## 错误描述
{error_description}

## 学生背景
学生姓名：{student_profile.get('student_name', '未知') if student_profile else '未知'}
当前水平：{student_profile.get('current_level', '未知') if student_profile else '未知'}

## 分析要求
1. 判断错误类型：概念错误 / 计算错误 / 边界错误 / 编码习惯错误
2. 给出正确思路
3. 提供一道变式题

请用 Markdown 格式输出。
"""
        result = llm.generate(
            messages=[{"role": "user", "content": prompt}],
            config={"temperature": 0.7, "max_tokens": 1000},
        )
        content = result.content if hasattr(result, "content") else str(result)
        return {
            "content": content,
            "error_type": "conceptual",  # 简化，实际可解析
            "suggestions": ["查看讲解", "做变式题"],
        }
    except Exception as e:
        logger.error(f"error_analysis_agent failed: {e}")
        return {"content": f"错因分析失败：{e}", "error_type": "unknown", "suggestions": []}


# =============================================================================
# Skill 实现
# =============================================================================


async def explanation_skill(
    concept: str,
    student_level: str = "intermediate",
    context: str = "",
) -> Dict[str, Any]:
    """自适应讲解 Skill"""
    try:
        llm = _get_llm()
        if not llm:
            return {"content": f"【{concept}】的讲解...\n\n（LLM 不可用）", "quality_score": 0}

        prompt = f"""你是一个耐心的 AI 辅导老师。请用清晰易懂的方式解释以下概念。

## 概念
{concept}

## 学生水平
{student_level}

## 相关上下文
{context or "无"}

## 要求
1. 用生活类比或实例帮助理解
2. 适当使用代码示例或图示说明
3. 分层次解释（简单 → 深入）
4. 难度适配学生水平

请用 Markdown 格式输出。
"""
        result = llm.generate(
            messages=[{"role": "user", "content": prompt}],
            config={"temperature": 0.7, "max_tokens": 1500},
        )
        content = result.content if hasattr(result, "content") else str(result)
        return {"content": content, "quality_score": 0.8}
    except Exception as e:
        logger.error(f"explanation_skill failed: {e}")
        return {"content": f"讲解生成失败：{e}", "quality_score": 0}


# =============================================================================
# Multimodal 实现
# =============================================================================


async def tts_tool(
    text: str,
    voice: str = "xiaoyan",
) -> Dict[str, Any]:
    """语音合成工具 — 接入讯飞 TTS API"""
    try:
        from app.config import get_settings
        settings = get_settings()

        if not settings.iflytek_app_id or not settings.iflytek_api_key:
            logger.warning("[tts_tool] 讯飞凭证未配置")
            return {"audio_url": "", "text_length": len(text), "error": "语音合成服务未配置"}

        from app.services.iflytek_multimodal import text_to_speech
        audio_bytes = text_to_speech(
            text=text,
            voice=voice,
            app_id=settings.iflytek_app_id,
            api_key=settings.iflytek_api_key,
            api_secret=settings.iflytek_api_secret,
        )

        if not audio_bytes:
            return {"audio_url": "", "text_length": len(text), "error": "语音合成失败（讯飞返回空）"}

        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode()
        data_url = f"data:audio/mpeg;base64,{audio_b64}"
        return {"audio_url": data_url, "text_length": len(text), "voice": voice}
    except Exception as e:
        logger.error(f"tts_tool failed: {e}")
        return {"audio_url": "", "text_length": len(text), "error": str(e)}


async def ppt_agent(
    course_id: int,
    topic: str,
    audience: str = "学生",
    slide_count: int = 8,
) -> Dict[str, Any]:
    """PPT 生成 Agent — 生成结构化课件大纲（JSON 格式）"""
    try:
        from app.config import get_settings
        from app.llm.gateway import LLMGateway

        settings = get_settings()
        llm = LLMGateway()

        prompt = f"""你是一个专业的课件设计师。请为"{topic}"生成一份 PPT 大纲。

## 要求
- 受众：{audience}
- 幻灯片数量：{slide_count} 页
- 每页结构：标题 + 要点（3-5条）+ 备注（讲解要点）

## 输出格式（严格 JSON）
[
  {{
    "slide_number": 1,
    "title": "封面标题",
    "bullets": ["要点1", "要点2", ...],
    "notes": "讲解备注"
  }},
  ...
]

只输出 JSON，不要有其他文字。
"""
        messages = [{"role": "user", "content": prompt}]
        result = llm.generate(
            messages=messages,
            config=settings.llm_config(),
        )
        content = result.content if hasattr(result, "content") else ""
        # 尝试解析 JSON
        import json
        try:
            # 去掉可能的 markdown 代码块
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            slides_data = json.loads(content.strip())
        except Exception:
            slides_data = [{"slide_number": 1, "title": topic, "bullets": [content[:200]], "notes": ""}]

        return {
            "content": json.dumps(slides_data, ensure_ascii=False),
            "slide_count": len(slides_data) if isinstance(slides_data, list) else 0,
            "topic": topic,
            "quality_score": 0.8,
        }
    except Exception as e:
        logger.error(f"ppt_agent failed: {e}")
        return {"content": f"PPT 生成失败：{e}", "slide_count": 0, "topic": topic, "quality_score": 0}


async def image_agent(
    prompt: str,
    style: str = "教学插画",
) -> Dict[str, Any]:
    """图片生成 Agent — 接入讯飞多模态生成 API"""
    try:
        from app.config import get_settings
        settings = get_settings()

        if not settings.iflytek_app_id or not settings.iflytek_api_key:
            logger.warning("[image_agent] 讯飞凭证未配置")
            return {
                "image_url": "",
                "prompt": prompt,
                "error": "图片生成服务未配置（讯飞凭证缺失）",
            }

        from app.services.iflytek_multimodal import generate_image
        img_base64 = generate_image(
            prompt=prompt,
            style=style,
            resolution="1024*1024",
            app_id=settings.iflytek_app_id,
            api_key=settings.iflytek_api_key,
            api_secret=settings.iflytek_api_secret,
        )

        if not img_base64:
            return {
                "image_url": "",
                "prompt": prompt,
                "error": "图片生成失败（讯飞返回空）",
            }

        # 转为 data URL 供前端直接渲染
        data_url = f"data:image/png;base64,{img_base64}"
        return {
            "image_url": data_url,
            "prompt": prompt,
            "style": style,
        }
    except Exception as e:
        logger.error(f"image_agent failed: {e}")
        return {"image_url": "", "prompt": prompt, "error": str(e)}


# =============================================================================
# 辅助函数
# =============================================================================

def _get_course_kps(course_id: int) -> List[Dict[str, Any]]:
    try:
        from app.database import get_db_cursor
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT kp_id, kp_name, difficulty_level FROM knowledge_points WHERE course_id=%s AND is_deleted=0",
                (course_id,),
            )
            rows = cursor.fetchall()
            return [
                {"kp_id": r["kp_id"], "name": r["kp_name"], "difficulty": r["difficulty_level"]}
                for r in rows
            ]
    except Exception:
        return []


def _extract_questions(content: str) -> List[Dict[str, str]]:
    """从 Markdown 内容中提题目"""
    import re
    questions = []
    # 简化实现：找 ## 题目 或 ## 练习 后面的内容块
    parts = re.split(r"(?=^#{1,3}\s*题)", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = [l.strip() for l in part.split("\n") if l.strip()]
        if lines:
            questions.append({"question": "\n".join(lines[:3]), "answer": ""})
    return questions[:5]


def _format_learning_path(learning_path: List[Dict[str, Any]]) -> str:
    """将学习路径格式化为 Markdown"""
    if not learning_path:
        return "暂无学习路径数据"
    lines = ["## 学习路径\n"]
    for i, step in enumerate(learning_path, 1):
        kp_name = step.get("kp_name") or step.get("name", f"知识点{i}")
        duration = step.get("estimated_hours", 1)
        lines.append(f"{i}. **{kp_name}**（约 {duration}h）")
    return "\n".join(lines)
