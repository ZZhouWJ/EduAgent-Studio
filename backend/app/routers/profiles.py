"""学生画像 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.utils.dependencies import get_current_user_dep, require_role
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["学生画像"])


@router.get("/")
async def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    keyword: Optional[str] = None,
    user: dict = Depends(get_current_user_dep),
):
    """获取学生画像列表（登录用户均可访问）"""
    service = ProfileService()
    return service.list_profiles(user, page, page_size, course_id, keyword)


@router.get("/{profile_id}")
async def get_profile(profile_id: int, user: dict = Depends(get_current_user_dep)):
    """获取学生画像详情（登录用户均可访问）"""
    service = ProfileService()
    return service.get_profile(profile_id, user)


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
    data: dict,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """更新知识点掌握度（仅教师/管理员可操作）"""
    service = ProfileService()
    return service.update_mastery(profile_id, data, user)
