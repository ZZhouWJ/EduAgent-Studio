"""
审核中心路由。

输出提交审核：
POST /api/outputs/{output_id}/submit-review

待审核列表：
GET /api/reviews/pending

审核详情：
GET /api/reviews/{request_id}

完成审核：
POST /api/reviews/{request_id}/complete

问题标签：
GET /api/issue-tags
"""

from typing import Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import review_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(tags=["审核中心"])


def _extract_token(authorization: Optional[str]) -> str:
    """从 Authorization 头解析 Bearer token。"""
    if not authorization:
        raise UnauthorizedException(message="未登录")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="认证信息格式错误")
    return parts[1]


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =============================================================================
# 请求体模型
# =============================================================================

class SubmitReviewRequest(BaseModel):
    reviewer_id: Optional[int] = Field(None, gt=0)
    submit_note: Optional[str] = Field(None, max_length=500)


class CompleteReviewRequest(BaseModel):
    review_status: str = Field(..., max_length=30)
    accuracy_score: Optional[float] = Field(None, ge=0, le=10)
    completeness_score: Optional[float] = Field(None, ge=0, le=10)
    logic_score: Optional[float] = Field(None, ge=0, le=10)
    format_score: Optional[float] = Field(None, ge=0, le=10)
    usability_score: Optional[float] = Field(None, ge=0, le=10)
    risk_score: Optional[float] = Field(None, ge=0, le=10)
    review_comment: Optional[str] = Field(None, max_length=2000)
    issue_tag_ids: Optional[list[int]] = Field(None)


# =============================================================================
# 输出提交审核
# POST /api/outputs/{output_id}/submit-review
# =============================================================================

@router.post("/outputs/{output_id}/submit-review")
async def submit_for_review(
    request: Request,
    output_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: SubmitReviewRequest = Body(...),
) -> dict:
    """提交输出到审核（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = review_service.submit_for_review(
        token=token,
        output_id=output_id,
        reviewer_id=body.reviewer_id,
        submit_note=body.submit_note,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 待审核列表
# GET /api/reviews/pending
# =============================================================================

@router.get("/reviews/pending")
async def list_pending_reviews(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
    project_id: Optional[int] = Query(None, gt=0),
) -> dict:
    """查询待审核列表（分页，需有权限）。"""
    token = _extract_token(authorization)

    result = review_service.list_pending_reviews(
        token=token,
        project_id=project_id,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


# =============================================================================
# 审核详情
# GET /api/reviews/{request_id}
# =============================================================================

@router.get("/reviews/{request_id}")
async def get_review_detail(
    request: Request,
    request_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取审核详情（含完整输出内容，需有权限）。"""
    token = _extract_token(authorization)

    result = review_service.get_review_detail(
        token=token,
        request_id=request_id,
    )
    return success_response(data=result)


# =============================================================================
# 完成审核
# POST /api/reviews/{request_id}/complete
# =============================================================================

@router.post("/reviews/{request_id}/complete")
async def complete_review(
    request: Request,
    request_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CompleteReviewRequest = Body(...),
) -> dict:
    """完成审核（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = review_service.complete_review(
        token=token,
        request_id=request_id,
        review_status=body.review_status,
        accuracy_score=body.accuracy_score,
        completeness_score=body.completeness_score,
        logic_score=body.logic_score,
        format_score=body.format_score,
        usability_score=body.usability_score,
        risk_score=body.risk_score,
        review_comment=body.review_comment,
        issue_tag_ids=body.issue_tag_ids,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 问题标签列表
# GET /api/issue-tags
# =============================================================================

@router.get("/issue-tags")
async def list_issue_tags(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """查询所有可用的问题标签（需已登录）。"""
    token = _extract_token(authorization)
    result = review_service.list_issue_tags(token=token)
    return success_response(data=result)
