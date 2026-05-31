"""
成果库与分支合并路由。

采用成果：
POST /api/outputs/{output_id}/adopt

项目成果列表：
GET /api/projects/{project_id}/artifacts

成果详情：
GET /api/artifacts/{adopted_id}

分支合并：
POST /api/tasks/{task_id}/branches/merge
"""

from typing import Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import artifact_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(tags=["成果库"])


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

class AdoptOutputRequest(BaseModel):
    artifact_title: str = Field(..., min_length=1, max_length=200)
    artifact_type: str = Field(..., min_length=1, max_length=50)
    release_version: str = Field(..., min_length=1, max_length=50)
    adopt_note: Optional[str] = Field(None, max_length=500)


class MergeBranchesRequest(BaseModel):
    source_branch_id: int = Field(..., gt=0)
    target_branch_id: int = Field(..., gt=0)
    source_output_id: Optional[int] = Field(None, gt=0)
    target_output_id: Optional[int] = Field(None, gt=0)
    merge_strategy: str = Field(..., max_length=30)
    merged_output_title: Optional[str] = Field(None, max_length=200)
    merged_content: Optional[str] = Field(None)
    merge_note: Optional[str] = Field(None, max_length=500)


# =============================================================================
# 采用成果
# POST /api/outputs/{output_id}/adopt
# =============================================================================

@router.post("/api/outputs/{output_id}/adopt")
async def adopt_output(
    request: Request,
    output_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: AdoptOutputRequest = Body(...),
) -> dict:
    """采用输出作为项目成果（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = artifact_service.adopt_output(
        token=token,
        output_id=output_id,
        artifact_title=body.artifact_title,
        artifact_type=body.artifact_type,
        release_version=body.release_version,
        adopt_note=body.adopt_note,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 项目成果列表
# GET /api/projects/{project_id}/artifacts
# =============================================================================

@router.get("/api/projects/{project_id}/artifacts")
async def list_project_artifacts(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    artifact_type: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None, max_length=100),
) -> dict:
    """查询项目成果列表（分页，需有权限）。"""
    token = _extract_token(authorization)

    result = artifact_service.list_project_artifacts(
        token=token,
        project_id=project_id,
        artifact_type=artifact_type,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


# =============================================================================
# 成果详情
# GET /api/artifacts/{adopted_id}
# =============================================================================

@router.get("/api/artifacts/{adopted_id}")
async def get_artifact_detail(
    request: Request,
    adopted_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取成果详情（含完整内容，需有权限）。"""
    token = _extract_token(authorization)

    result = artifact_service.get_artifact_detail(
        token=token,
        adopted_id=adopted_id,
    )
    return success_response(data=result)


# =============================================================================
# 分支合并
# POST /api/tasks/{task_id}/branches/merge
# =============================================================================

@router.post("/api/tasks/{task_id}/branches/merge")
async def merge_branches(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: MergeBranchesRequest = Body(...),
) -> dict:
    """执行分支合并（需有权限：admin/leader/teacher）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = artifact_service.merge_branches(
        token=token,
        task_id=task_id,
        source_branch_id=body.source_branch_id,
        target_branch_id=body.target_branch_id,
        source_output_id=body.source_output_id,
        target_output_id=body.target_output_id,
        merge_strategy=body.merge_strategy,
        merged_output_title=body.merged_output_title,
        merged_content=body.merged_content,
        merge_note=body.merge_note,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)
