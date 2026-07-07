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

from app.services.auth_service import _extract_token_from_header as _extract_token_from_auth
from app.services import statistics_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

def _extract_token(authorization):
    """从 Authorization 头解析 token（兼容旧代码行为）。"""
    result = _extract_token_from_auth(authorization)
    if not result:
        raise UnauthorizedException(message="未登录")
    return result

router = APIRouter(tags=["统计看板"])


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
    limit: int = Query(20, ge=1, le=500),
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


# =============================================================================
# A3 学习分析统计
# GET /api/statistics/learning-overview
# GET /api/statistics/mastery-distribution
# GET /api/statistics/weak-knowledge-points
# GET /api/statistics/resource-type-distribution
# GET /api/statistics/invocation-trend
# GET /api/statistics/review-rate-by-course
# GET /api/statistics/cost-distribution
# =============================================================================

@router.get("/api/statistics/learning-overview")
async def get_learning_overview(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_learning_overview(token or "")
    return success_response(data=result)


@router.get("/api/statistics/mastery-distribution")
async def get_mastery_distribution(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_mastery_distribution(token or "")
    return success_response(data=result)


@router.get("/api/statistics/weak-knowledge-points")
async def get_weak_knowledge_points(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    top_n: int = Query(10, ge=1, le=50),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_weak_knowledge_points(token or "", top_n)
    return success_response(data=result)


@router.get("/api/statistics/resource-type-distribution")
async def get_resource_type_distribution(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_resource_type_distribution(token or "")
    return success_response(data=result)


@router.get("/api/statistics/invocation-trend")
async def get_invocation_trend(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    days: int = Query(14, ge=7, le=30),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_invocation_trend(token or "", days)
    return success_response(data=result)


@router.get("/api/statistics/review-rate-by-course")
async def get_review_rate_by_course(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_review_rate_by_course(token or "")
    return success_response(data=result)


@router.get("/api/statistics/cost-distribution")
async def get_cost_distribution(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_cost_distribution(token or "")
    return success_response(data=result)


# =============================================================================
# Module 8: 平台全局统计 (管理端指标真实化)
# GET /api/statistics/platform
# GET /api/statistics/cost-by-model
# GET /api/statistics/resources
# =============================================================================

@router.get("/api/statistics/platform")
async def get_platform_overview(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    平台总览 (Module 8)。

    返回平台全局运营指标：调用次数、Token消耗、成本、学生数、课程数等。
    """
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_platform_overview(token or "")
    return success_response(data=result)


@router.get("/api/statistics/cost-by-model")
async def get_cost_by_model(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    按模型成本统计 (Module 8)。

    返回各模型的调用次数、Token消耗和成本。
    """
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_cost_by_model_api(token or "")
    return success_response(data=result)


@router.get("/api/statistics/resources")
async def get_resource_stats(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    资源统计 (Module 8)。

    返回资源的审核状态分布和通过率。
    """
    token = _extract_token(authorization) if authorization else None
    result = statistics_service.get_resource_stats_api(token or "")
    return success_response(data=result)
