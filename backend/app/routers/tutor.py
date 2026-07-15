"""
Tutor API 路由

提供独立学习辅导答疑接口：
- POST /api/tutor/chat - 答疑（阻塞）
- POST /api/tutor/chat/stream - 答疑（SSE 流式）
- POST /api/tutor/feedback - 反馈
- GET /api/tutor/sessions - 会话历史
"""

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.auth_service import get_current_user_dependency as get_current_user
from app.services.tutor_service import TutorService
from app.services.tutor_supervisor import TutorSupervisor
from app.services.course_access_service import CourseAccessService
from app.repositories.profile_repo import ProfileRepository
from app.repositories.knowledge_repo import KnowledgeRepository
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/tutor", tags=["学习辅导"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    profile_id: int
    course_id: int
    question: str
    requested_content_types: Optional[list[str]] = None  # 学生指定的内容类型


class FeedbackRequest(BaseModel):
    session_id: int
    helpful: bool
    follow_up: Optional[str] = None


def _get_tutor_service() -> TutorService:
    """获取 TutorService 实例"""
    return TutorService()


@router.post("/chat")
async def tutor_chat(
    data: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    学生答疑接口。

    结合学生画像和课程知识库，生成个性化的答疑回答。
    支持多智能体协作生成多模态内容（思维导图/练习题/代码案例等）。

    Request:
        - profile_id: 学生画像 ID
        - course_id: 课程 ID
        - question: 学生问题
        - requested_content_types: 指定生成的内容类型（可选）

    Response:
        - session_id: 会话 ID
        - answer: Markdown 格式的回答
        - explanation_level: 解释级别
        - citations: 引用来源列表
        - content_blocks: 多模态内容块列表（思维导图/练习题等）
        - intent: 意图识别结果
        - practice_questions: 练习题列表
        - recommended_resources: 推荐资源列表
    """
    service = _get_tutor_service()
    result = service.chat(
        profile_id=data.profile_id,
        course_id=data.course_id,
        question=data.question,
        user=user,
        requested_content_types=data.requested_content_types,
    )

    if result.get("code") != 0:
        return error_response(
            message=result.get("message", "答疑失败"),
            code=result.get("code", 500),
        )

    return success_response(data=result.get("data"), message=result.get("message", "答疑成功"))


@router.post("/chat/stream")
async def tutor_chat_stream(
    data: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    学生答疑接口（SSE 流式版本）。

    实时推送执行事件：工具启动 / 工具完成 / Agent 执行 / 最终回答。
    前端可以展示 AI 的思考过程和执行轨迹。

    事件类型：
    - supervisor.started：开始执行
    - supervisor.tool_choice：模型选择了哪些工具
    - tool.started：工具开始执行
    - tool.completed / tool.error：工具完成/失败
    - supervisor.final：最终回答
    - supervisor.max_steps：达到最大步数
    """
    CourseAccessService().require_profile_course(
        data.profile_id, data.course_id, user
    )

    async def event_stream():
        try:
            profile_repo = ProfileRepository()
            knowledge_repo = KnowledgeRepository()

            # 获取学生画像
            profile = profile_repo.get_profile(data.profile_id) if data.profile_id else None

            course_id = data.course_id or (profile.get("course_id") if profile else None) or 1

            # 检索知识库作为上下文
            chunks = knowledge_repo.search_chunks(course_id=course_id, query=data.question, limit=3)
            context_parts = []
            for i, c in enumerate(chunks, 1):
                content = c.get("content", "")[:200]
                context_parts.append(f"[{i}] {c.get('title', '')}：{content}...")
            knowledge_context = "\n".join(context_parts) or "（暂无相关知识库内容）"

            # 执行 Supervisor 流式循环（profile 可能为 None，supervisor 内部做兜底）
            supervisor = TutorSupervisor()
            async for sse_line in supervisor.run_stream(
                question=data.question,
                profile=profile,
                course_id=course_id,
                knowledge_context=knowledge_context,
            ):
                yield sse_line

        except Exception:
            logger.exception("流式答疑失败")
            yield f"data: {json.dumps({'type': 'error', 'message': '答疑失败，请稍后重试'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/suggestions")
async def get_suggestions(
    course_id: int = Query(..., description="课程 ID"),
    profile_id: Optional[int] = Query(None, description="学生画像 ID（可选）"),
    user: dict = Depends(get_current_user),
):
    """
    根据学生画像和课程知识点，动态生成学习建议问题。

    读取学生的薄弱点和课程知识点列表，由 LLM 生成 4 条针对性强的问题。
    """
    from app.services.tutor_service import TutorService

    service = TutorService()
    result = service.get_suggestions(
        course_id=course_id, profile_id=profile_id, user=user
    )

    if result.get("code") != 0:
        return error_response(message=result.get("message", "获取建议失败"), code=result.get("code", 500))

    return success_response(data=result.get("data"), message="success")


@router.post("/feedback")
async def tutor_feedback(
    data: FeedbackRequest,
    user: dict = Depends(get_current_user),
):
    """
    提交答疑反馈。

    用于评价答疑质量，如果回答不被理解，会自动降低解释难度。

    Request:
        - session_id: 会话 ID
        - helpful: 是否有用
        - follow_up: 追问内容（可选）
    """
    service = _get_tutor_service()
    result = service.submit_feedback(
        session_id=data.session_id,
        helpful=data.helpful,
        follow_up=data.follow_up,
        user=user,
    )

    if result.get("code") != 0:
        return error_response(
            message=result.get("message", "反馈提交失败"),
            code=result.get("code", 500),
        )

    return success_response(data=result.get("data"), message=result.get("message", "反馈已提交"))


@router.get("/sessions")
async def get_tutor_sessions(
    profile_id: int = Query(..., description="学生画像 ID"),
    course_id: Optional[int] = Query(None, description="课程 ID（可选）"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    user: dict = Depends(get_current_user),
):
    """
    获取答疑会话历史。

    Query:
        - profile_id: 学生画像 ID
        - course_id: 课程 ID（可选）
        - limit: 返回数量，默认 20
    """
    service = _get_tutor_service()
    result = service.get_sessions(
        profile_id=profile_id,
        course_id=course_id,
        limit=limit,
        user=user,
    )

    if result.get("code") != 0:
        return error_response(
            message=result.get("message", "获取会话历史失败"),
            code=result.get("code", 500),
        )

    return success_response(data=result.get("data"), message=result.get("message", "success"))
