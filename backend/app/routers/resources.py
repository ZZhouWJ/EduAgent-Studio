"""学习资源 API"""
from typing import Literal, Optional

from fastapi import APIRouter, Body, Depends, Query, Request
from pydantic import BaseModel, Field

from app.repositories.learning_resource_repo import LearningResourceRepository
from app.services.auth_service import get_current_user_dependency as get_current_user
from app.services.course_access_service import CourseAccessService
from app.services.learning_resource_review_service import LearningResourceReviewService
from app.utils.exceptions import NotFoundException
from app.utils.response import success_response

router = APIRouter(prefix="/learning", tags=["学习资源"])
_repo = LearningResourceRepository()
_review_service = LearningResourceReviewService(_repo)


class SubmitResourceReviewRequest(BaseModel):
    submit_note: Optional[str] = Field(None, max_length=500)


class CompleteResourceReviewRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    accuracy_score: Optional[float] = Field(None, ge=0, le=10)
    completeness_score: Optional[float] = Field(None, ge=0, le=10)
    logic_score: Optional[float] = Field(None, ge=0, le=10)
    format_score: Optional[float] = Field(None, ge=0, le=10)
    usability_score: Optional[float] = Field(None, ge=0, le=10)
    review_comment: Optional[str] = Field(None, max_length=2000)


def _client_context(request: Request) -> tuple[str, str]:
    forwarded = request.headers.get("X-Forwarded-For")
    ip_address = (
        forwarded.split(",")[0].strip()
        if forwarded
        else request.client.host if request.client else "unknown"
    )
    return ip_address, request.headers.get("User-Agent", "")


def _is_student_only(user: dict) -> bool:
    roles = set(user.get("roles", []))
    return "student_member" in roles and not roles.intersection({"teacher", "admin"})


@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    type: Optional[str] = None,
    kp_id: Optional[int] = Query(None, gt=0),
    status: Optional[Literal["draft", "pending_review", "approved", "rejected", "archived"]] = None,
    user: dict = Depends(get_current_user),
):
    access = CourseAccessService()
    course_ids = access.list_accessible_course_ids(user)
    if course_id is not None:
        access.require_course_access(course_id, user)
        if kp_id is not None:
            access.require_knowledge_points_course(course_id, [kp_id])
    result = _repo.list_resources(
        page=page,
        page_size=page_size,
        course_id=course_id,
        resource_type=type,
        knowledge_point_id=kp_id,
        status="approved" if _is_student_only(user) else status,
        course_ids=course_ids if course_id is None else None,
    )
    if _is_student_only(user):
        result = {
            **result,
            "items": [
                {key: value for key, value in item.items() if key != "review_submitted_at"}
                for item in result["items"]
            ],
        }
    return success_response(data=result)


@router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    user: dict = Depends(get_current_user),
):
    CourseAccessService().require_resource_access(resource_id, user)
    detail = _repo.get_resource(resource_id)
    if detail is None or (_is_student_only(user) and detail.get("status") != "approved"):
        raise NotFoundException("资源不存在")
    if _is_student_only(user):
        detail = {
            key: value
            for key, value in detail.items()
            if key not in {"review_history", "reviewer_comment"}
        }
    return success_response(data=detail)


@router.post("/resources/{resource_id}/submit-review")
async def submit_resource_review(
    request: Request,
    resource_id: int,
    body: SubmitResourceReviewRequest = Body(...),
    user: dict = Depends(get_current_user),
):
    ip_address, user_agent = _client_context(request)
    result = _review_service.submit_for_review(
        resource_id=resource_id,
        user=user,
        submit_note=body.submit_note,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return success_response(data=result, message="资源已提交审核")


@router.post("/resources/{resource_id}/review")
async def complete_resource_review(
    request: Request,
    resource_id: int,
    body: CompleteResourceReviewRequest = Body(...),
    user: dict = Depends(get_current_user),
):
    ip_address, user_agent = _client_context(request)
    result = _review_service.complete_review(
        resource_id=resource_id,
        user=user,
        decision=body.decision,
        accuracy_score=body.accuracy_score,
        completeness_score=body.completeness_score,
        logic_score=body.logic_score,
        format_score=body.format_score,
        usability_score=body.usability_score,
        review_comment=body.review_comment,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return success_response(data=result, message="资源审核已完成")
