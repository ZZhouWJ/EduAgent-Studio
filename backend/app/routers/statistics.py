"""
统计看板路由。

首页统计概览：
GET /api/statistics/overview

项目统计：
GET /api/statistics/projects

模型调用统计：
GET /api/statistics/model-calls

成本统计：
GET /api/statistics/costs

审核质量统计：
GET /api/statistics/reviews

成员贡献统计：
GET /api/statistics/member-contributions

最近操作动态：
GET /api/statistics/recent-activities
"""

from typing import Optional

from fastapi import APIRouter, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import statistics_service
from app.utils.response import success_response

router = APIRouter(tags=["统计看板"])


def _extract_token(authorization: Optional[str]) -> str:
    """从 Authorization 头解析 Bearer token。"""
    if not authorization:
        from app.utils.exceptions import UnauthorizedException
        raise UnauthorizedException(message="未登录")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        from app.utils.exceptions import UnauthorizedException
        raise UnauthorizedException(message="认证信息格式错误")
    return parts[1]


# =============================================================================
# 首页统计概览
# GET /api/statistics/overview
# =============================================================================

@router.get("/api/statistics/overview")
async def get_overview(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    首页统计概览。

    - admin 返回全局统计
    - 非 admin 返回用户参与项目范围内统计
    """
    token = _extract_token(authorization)
    result = statistics_service.get_overview(token)
    return success_response(data=result)


# =============================================================================
# 项目统计
# GET /api/statistics/projects
# =============================================================================

@router.get("/api/statistics/projects")
async def list_project_stats(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
) -> dict:
    """
    项目维度统计列表。

    - admin 可查看所有项目
    - 非 admin 只能查看自己参与的项目
    - 传入 project_id 时返回单个项目统计
    """
    token = _extract_token(authorization)
    result = statistics_service.list_project_stats(
        token=token,
        project_id=project_id,
    )
    return success_response(data=result)


# =============================================================================
# 模型调用统计
# GET /api/statistics/model-calls
# =============================================================================

@router.get("/api/statistics/model-calls")
async def get_model_call_stats(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
    date_from: Optional[str] = Query(None, max_length=10),
    date_to: Optional[str] = Query(None, max_length=10),
) -> dict:
    """
    模型调用统计。

    支持 project_id 和日期范围过滤。
    """
    token = _extract_token(authorization)
    result = statistics_service.get_model_call_stats(
        token=token,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
    )
    return success_response(data=result)


# =============================================================================
# 成本统计
# GET /api/statistics/costs
# =============================================================================

@router.get("/api/statistics/costs")
async def get_cost_stats(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
    date_from: Optional[str] = Query(None, max_length=10),
    date_to: Optional[str] = Query(None, max_length=10),
) -> dict:
    """
    成本统计。

    支持 project_id 和日期范围过滤。
    """
    token = _extract_token(authorization)
    result = statistics_service.get_cost_stats(
        token=token,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
    )
    return success_response(data=result)


# =============================================================================
# 审核质量统计
# GET /api/statistics/reviews
# =============================================================================

@router.get("/api/statistics/reviews")
async def get_review_stats(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
) -> dict:
    """
    审核质量统计。

    支持 project_id 过滤。
    """
    token = _extract_token(authorization)
    result = statistics_service.get_review_stats(
        token=token,
        project_id=project_id,
    )
    return success_response(data=result)


# =============================================================================
# 成员贡献统计
# GET /api/statistics/member-contributions
# =============================================================================

@router.get("/api/statistics/member-contributions")
async def get_member_contribution_stats(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
) -> dict:
    """
    成员贡献统计。

    支持 project_id 过滤。
    """
    token = _extract_token(authorization)
    result = statistics_service.get_member_contribution_stats(
        token=token,
        project_id=project_id,
    )
    return success_response(data=result)


# =============================================================================
# 最近操作动态
# GET /api/statistics/recent-activities
# =============================================================================

@router.get("/api/statistics/recent-activities")
async def get_recent_activities(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """
    最近操作动态。

    - limit 默认 20，最大 100
    """
    token = _extract_token(authorization)
    result = statistics_service.get_recent_activities(
        token=token,
        project_id=project_id,
        limit=limit,
    )
    return success_response(data=result)
