"""学生画像 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["学生画像"])


@router.get("/")
async def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    keyword: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    """获取学生画像列表"""
    service = ProfileService()
    return service.list_profiles(token, page, page_size, course_id, keyword)


@router.get("/{profile_id}")
async def get_profile(profile_id: int, token: str = Depends(get_current_user)):
    """获取学生画像详情"""
    service = ProfileService()
    return service.get_profile(profile_id, token)


@router.put("/{profile_id}")
async def update_profile(
    profile_id: int,
    data: dict,
    token: str = Depends(get_current_user),
):
    """更新学生画像"""
    service = ProfileService()
    return service.update_profile(profile_id, data, token)


@router.post("/{profile_id}/mastery")
async def update_mastery(
    profile_id: int,
    data: dict,
    token: str = Depends(get_current_user),
):
    """更新知识点掌握度"""
    service = ProfileService()
    return service.update_mastery(profile_id, data, token)
