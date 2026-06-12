"""学习资源 API"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.repositories.learning_resource_repo import LearningResourceRepository
from app.services.auth_service import get_current_user_dependency as get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/learning", tags=["学习资源"])
_repo = LearningResourceRepository()


@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    type: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    result = _repo.list_resources(
        page=page,
        page_size=page_size,
        course_id=course_id,
        resource_type=type,
    )
    return success_response(data=result)


@router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    token: str = Depends(get_current_user),
):
    detail = _repo.get_resource(resource_id)
    if detail is None:
        from app.utils.response import error_response
        return error_response(message="资源不存在", code=404)
    return success_response(data=detail)
