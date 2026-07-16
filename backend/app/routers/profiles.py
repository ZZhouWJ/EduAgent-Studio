"""学生画像 API"""
import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from app.utils.dependencies import get_current_user_dep, require_role
from app.services.profile_service import ProfileService
from app.services.profile_dialog_service import ProfileDialogService

router = APIRouter(prefix="/profiles", tags=["学生画像"])


class UpdateMasteryRequest(BaseModel):
    kp_id: int = Field(..., gt=0)
    mastery: float = Field(..., ge=0, le=1)
    update_reason: Optional[str] = Field(None, max_length=500)


ShortProfileText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    learning_goal: Optional[str] = Field(None, max_length=5000)
    knowledge_base: Optional[str] = Field(None, max_length=5000)
    current_level: Optional[str] = Field(None, max_length=2000)
    cognitive_style: Optional[str] = Field(None, max_length=100)
    time_constraints: Optional[str] = Field(None, max_length=255)
    practice_level: Optional[str] = Field(None, max_length=100)
    motivation: Optional[str] = Field(None, max_length=255)
    error_prone_points: Optional[list[ShortProfileText]] = Field(None, max_length=50)
    interests: Optional[list[ShortProfileText]] = Field(None, max_length=20)
    resource_preferences: Optional[list[ShortProfileText]] = Field(None, max_length=20)
    weekly_hours: Optional[int] = Field(None, ge=0, le=168)
    mastery_score: Optional[float] = Field(None, ge=0, le=1)


class DialogMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)
    ]


class ApplyExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: int = Field(..., gt=0)


def _profile_update_payload(data: UpdateProfileRequest) -> dict:
    payload = data.model_dump(exclude_unset=True)
    if isinstance(payload.get("error_prone_points"), list):
        payload["error_prone_points"] = json.dumps(
            payload["error_prone_points"], ensure_ascii=False
        )
    for field in ("interests", "resource_preferences"):
        if isinstance(payload.get(field), list):
            payload[field] = ",".join(payload[field])
    return payload


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
    data: UpdateProfileRequest,
    profile_id: int = Path(..., gt=0),
    user: dict = Depends(require_role("teacher", "admin")),
):
    """更新学生画像（仅教师/管理员可操作）"""
    service = ProfileService()
    return service.update_profile(profile_id, _profile_update_payload(data), user)


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
    data: DialogMessageRequest,
    profile_id: int = Path(..., gt=0, description="画像 ID"),
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
    ProfileService().require_profile_access(profile_id, user)
    service = ProfileDialogService()
    return service.chat(profile_id, data.message, user)


@router.post("/{profile_id}/apply-extraction")
async def apply_extraction(
    data: ApplyExtractionRequest,
    profile_id: int = Path(..., gt=0, description="画像 ID"),
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
    ProfileService().require_profile_access(profile_id, user)
    service = ProfileDialogService()
    return service.apply_extraction(profile_id, data.message_id)
