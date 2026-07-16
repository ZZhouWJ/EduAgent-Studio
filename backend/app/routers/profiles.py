"""学生画像 API"""
from fastapi import APIRouter, Depends, Path, Query
from typing import Optional
from pydantic import BaseModel, Field
from app.utils.dependencies import get_current_user_dep, require_role
from app.services.profile_service import ProfileService
from app.services.profile_dialog_service import ProfileDialogService

router = APIRouter(prefix="/profiles", tags=["学生画像"])


class UpdateMasteryRequest(BaseModel):
    kp_id: int = Field(..., gt=0)
    mastery: float = Field(..., ge=0, le=1)
    update_reason: Optional[str] = Field(None, max_length=500)


@router.get("/me")
async def get_my_profile(user: dict = Depends(get_current_user_dep)):
    """获取当前登录用户自己的学生画像（所有角色均可访问）"""
    service = ProfileService()
    return service.get_my_profile(user)


@router.get("/")
async def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    keyword: Optional[str] = None,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """获取学生画像列表（教师/管理员可访问，学生应使用 /profiles/me）"""
    service = ProfileService()
    return service.list_profiles(user, page, page_size, course_id, keyword)


@router.get("/{profile_id}")
async def get_profile(profile_id: int, user: dict = Depends(get_current_user_dep)):
    """获取学生画像详情（登录用户均可访问）"""
    service = ProfileService()
    return service.get_profile(profile_id, user)


@router.get("/{profile_id}/feedback-history")
async def get_profile_feedback_history(
    profile_id: int = Path(..., gt=0, description="画像 ID"),
    limit: int = Query(20, ge=1, le=50, description="返回条数限制"),
    user: dict = Depends(get_current_user_dep),
):
    """获取画像更新记录（学习反馈历史）"""
    ProfileService().require_profile_access(profile_id, user)
    from app.repositories.learning_feedback_repo import LearningFeedbackRepository
    repo = LearningFeedbackRepository()
    items = repo.get_feedback_history_by_profile(profile_id, limit)
    return {"code": 0, "message": "success", "data": items}


@router.put("/{profile_id}")
async def update_profile(
    profile_id: int,
    data: dict,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """更新学生画像（仅教师/管理员可操作）"""
    service = ProfileService()
    return service.update_profile(profile_id, data, user)


@router.post("/{profile_id}/mastery")
async def update_mastery(
    profile_id: int,
    data: UpdateMasteryRequest,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """更新知识点掌握度（仅教师/管理员可操作）"""
    service = ProfileService()
    return service.update_mastery(profile_id, data.model_dump(), user)


@router.get("/{profile_id}/dialog")
async def get_dialog_history(
    profile_id: int = Path(..., gt=0, description="画像 ID"),
    limit: int = Query(50, ge=1, le=100, description="返回条数限制"),
    user: dict = Depends(get_current_user_dep),
):
    """获取对话历史（登录用户均可访问）"""
    ProfileService().require_profile_access(profile_id, user)
    service = ProfileDialogService()
    return service.get_dialog_history(profile_id, limit)


@router.post("/{profile_id}/dialog")
async def send_dialog_message(
    profile_id: int = Path(..., gt=0, description="画像 ID"),
    data: dict = None,
    user: dict = Depends(get_current_user_dep),
):
    """
    发送对话消息并获取回复。

    请求体：
    {
        "message": "学生输入的自然语言描述"
    }

    返回：
    {
        "reply": "助手回复",
        "extracted": {...},  # 抽取的结构化数据
        "profile_patch": {...},  # 建议的画像更新
        "pending_changes": [...]  # 待确认的变更列表
    }
    """
    if data is None:
        data = {}
    message = data.get("message", "")
    if not message or not message.strip():
        return {"code": 400, "message": "消息不能为空", "data": None}

    ProfileService().require_profile_access(profile_id, user)
    service = ProfileDialogService()
    return service.chat(profile_id, message.strip(), user)


@router.post("/{profile_id}/apply-extraction")
async def apply_extraction(
    profile_id: int = Path(..., gt=0, description="画像 ID"),
    data: dict = None,
    user: dict = Depends(require_role("teacher", "admin", "student_member")),
):
    """
    应用抽取结果到画像。

    请求体：
    {
        "message_id": 123  # 包含抽取结果的消息 ID
    }

    只有消息的发送者或教师/管理员可以应用。
    """
    if data is None:
        data = {}
    message_id = data.get("message_id")
    if not message_id:
        return {"code": 400, "message": "message_id 不能为空", "data": None}

    ProfileService().require_profile_access(profile_id, user)
    service = ProfileDialogService()
    return service.apply_extraction(profile_id, message_id)
