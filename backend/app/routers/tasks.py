"""
任务与版本管理路由。

项目任务相关：
GET    /api/projects/{project_id}/tasks
POST   /api/projects/{project_id}/tasks

任务相关：
GET    /api/tasks/{task_id}
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}

任务分支相关：
GET    /api/tasks/{task_id}/branches
POST   /api/tasks/{task_id}/branches

输出版本相关：
GET    /api/tasks/{task_id}/outputs
GET    /api/outputs/{output_id}
GET    /api/outputs/{output_id}/timeline
POST   /api/tasks/{task_id}/outputs/manual
"""

from typing import Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import task_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(tags=["任务与版本管理"])


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

class CreateTaskRequest(BaseModel):
    task_type_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    assignee_id: Optional[int] = Field(None, gt=0)
    priority: Optional[str] = Field(None, max_length=20)
    due_date: Optional[str] = Field(None)


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    assignee_id: Optional[int] = Field(None)
    status: Optional[str] = Field(None, max_length=30)
    priority: Optional[str] = Field(None, max_length=20)
    due_date: Optional[str] = Field(None)


class CreateBranchRequest(BaseModel):
    branch_name: str = Field(..., min_length=1, max_length=100)
    base_output_id: Optional[int] = Field(None, gt=0)


class CreateManualOutputRequest(BaseModel):
    branch_id: Optional[int] = Field(None, gt=0)
    parent_output_id: Optional[int] = Field(None, gt=0)
    output_title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(...)
    edit_summary: Optional[str] = Field(None, max_length=500)


# =============================================================================
# 项目任务列表
# =============================================================================

@router.get("/api/projects/{project_id}/tasks")
async def list_project_tasks(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None, max_length=100),
) -> dict:
    """获取项目任务列表（分页 + 搜索 + 状态过滤）。"""
    token = _extract_token(authorization)

    result = task_service.list_project_tasks(
        token=token,
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=status,
        keyword=keyword,
    )
    return success_response(data=result)


# =============================================================================
# 创建项目任务
# =============================================================================

@router.post("/api/projects/{project_id}/tasks")
async def create_task(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateTaskRequest = Body(...),
) -> dict:
    """创建项目任务，自动创建默认主分支。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = task_service.create_task(
        token=token,
        project_id=project_id,
        task_type_id=body.task_type_id,
        title=body.title,
        description=body.description,
        assignee_id=body.assignee_id,
        priority=body.priority,
        due_date=body.due_date,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 任务详情
# =============================================================================

@router.get("/api/tasks/{task_id}")
async def get_task_detail(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取任务详情（需有权限）。"""
    token = _extract_token(authorization)

    result = task_service.get_task_detail(
        token=token,
        task_id=task_id,
    )
    return success_response(data=result)


# =============================================================================
# 更新任务
# =============================================================================

@router.put("/api/tasks/{task_id}")
async def update_task(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: UpdateTaskRequest = Body(...),
) -> dict:
    """更新任务信息（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = task_service.update_task(
        token=token,
        task_id=task_id,
        title=body.title,
        description=body.description,
        assignee_id=body.assignee_id,
        status=body.status,
        priority=body.priority,
        due_date=body.due_date,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 删除任务（软删除）
# =============================================================================

@router.delete("/api/tasks/{task_id}")
async def delete_task(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """软删除任务（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    task_service.delete_task(
        token=token,
        task_id=task_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data={})


# =============================================================================
# 任务分支列表
# =============================================================================

@router.get("/api/tasks/{task_id}/branches")
async def list_task_branches(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取任务分支列表（需有权限）。"""
    token = _extract_token(authorization)

    result = task_service.list_task_branches(
        token=token,
        task_id=task_id,
    )
    return success_response(data=result)


# =============================================================================
# 创建任务分支
# =============================================================================

@router.post("/api/tasks/{task_id}/branches")
async def create_task_branch(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateBranchRequest = Body(...),
) -> dict:
    """创建任务分支（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = task_service.create_task_branch(
        token=token,
        task_id=task_id,
        branch_name=body.branch_name,
        base_output_id=body.base_output_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 输出版本列表
# =============================================================================

@router.get("/api/tasks/{task_id}/outputs")
async def list_task_outputs(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取任务输出版本列表（需有权限）。"""
    token = _extract_token(authorization)

    result = task_service.list_task_outputs(
        token=token,
        task_id=task_id,
    )
    return success_response(data=result)


# =============================================================================
# 输出版本详情
# =============================================================================

@router.get("/api/outputs/{output_id}")
async def get_output_detail(
    request: Request,
    output_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取输出版本详情（含完整 content，需有权限）。"""
    token = _extract_token(authorization)

    result = task_service.get_output_detail(
        token=token,
        output_id=output_id,
    )
    return success_response(data=result)


# =============================================================================
# 输出版本时间线
# =============================================================================

@router.get("/api/outputs/{output_id}/timeline")
async def get_output_timeline(
    request: Request,
    output_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取输出版本时间线（基于 parent_output_id，需有权限）。"""
    token = _extract_token(authorization)

    result = task_service.get_output_timeline(
        token=token,
        output_id=output_id,
    )
    return success_response(data=result)


# =============================================================================
# 创建人工输出版本
# =============================================================================

@router.post("/api/tasks/{task_id}/outputs/manual")
async def create_manual_output(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateManualOutputRequest = Body(...),
) -> dict:
    """创建人工输出版本（需有权限）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = task_service.create_manual_output(
        token=token,
        task_id=task_id,
        output_title=body.output_title,
        content=body.content,
        branch_id=body.branch_id,
        parent_output_id=body.parent_output_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)
