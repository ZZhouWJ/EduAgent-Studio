"""学习资源 API"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.repositories.learning_resource_repo import LearningResourceRepository
from app.services.auth_service import get_current_user_dependency as get_current_user
from app.services.course_access_service import CourseAccessService
from app.utils.response import success_response

router = APIRouter(prefix="/learning", tags=["学习资源"])
_repo = LearningResourceRepository()


@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    type: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    access = CourseAccessService()
    course_ids = access.list_accessible_course_ids(user)
    if course_id is not None:
        access.require_course_access(course_id, user)
    result = _repo.list_resources(
        page=page,
        page_size=page_size,
        course_id=course_id,
        resource_type=type,
        course_ids=course_ids if course_id is None else None,
    )
    return success_response(data=result)


@router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    user: dict = Depends(get_current_user),
):
    CourseAccessService().require_resource_access(resource_id, user)
    detail = _repo.get_resource(resource_id)
    if detail is None:
        from app.utils.response import error_response
        return error_response(message="资源不存在", code=404)
    return success_response(data=detail)
