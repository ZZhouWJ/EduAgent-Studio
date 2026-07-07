"""
Tutor API 路由

提供独立学习辅导答疑接口：
- POST /api/tutor/chat - 答疑
- POST /api/tutor/feedback - 反馈
- GET /api/tutor/sessions - 会话历史
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.services.auth_service import get_current_user_dependency as get_current_user
from app.services.tutor_service import TutorService
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/tutor", tags=["学习辅导"])


class ChatRequest(BaseModel):
    profile_id: int
    course_id: int
    question: str


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
    token: str = Depends(get_current_user),
):
    """
    学生答疑接口。

    结合学生画像和课程知识库，生成个性化的答疑回答。

    Request:
        - profile_id: 学生画像 ID
        - course_id: 课程 ID
        - question: 学生问题

    Response:
        - session_id: 会话 ID
        - answer: Markdown 格式的回答
        - explanation_level: 解释级别（basic/intermediate/advanced）
        - citations: 引用来源列表
        - diagram: Mermaid 格式图表（可选）
        - code_example: 代码示例（可选）
        - practice_questions: 练习题列表
        - recommended_resources: 推荐资源列表
    """
    service = _get_tutor_service()
    result = service.chat(
        profile_id=data.profile_id,
        course_id=data.course_id,
        question=data.question,
    )

    if result.get("code") != 0:
        return error_response(
            message=result.get("message", "答疑失败"),
            code=result.get("code", 500),
        )

    return success_response(data=result.get("data"), message=result.get("message", "答疑成功"))


@router.post("/feedback")
async def tutor_feedback(
    data: FeedbackRequest,
    token: str = Depends(get_current_user),
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
    token: str = Depends(get_current_user),
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
    )

    if result.get("code") != 0:
        return error_response(
            message=result.get("message", "获取会话历史失败"),
            code=result.get("code", 500),
        )

    return success_response(data=result.get("data"), message=result.get("message", "success"))
