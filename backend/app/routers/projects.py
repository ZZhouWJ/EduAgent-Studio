"""
项目空间管理路由。

GET    /api/projects
POST   /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}
POST   /api/projects/{project_id}/archive
GET    /api/projects/{project_id}/members
POST   /api/projects/{project_id}/members
PUT    /api/projects/{project_id}/members/{member_id}
DELETE /api/projects/{project_id}/members/{member_id}
"""

from typing import Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import project_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/projects", tags=["项目管理"])


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

class CreateProjectRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    project_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)


class UpdateProjectRequest(BaseModel):
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    project_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None)


class AddMemberRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    project_role: str = Field(..., min_length=1, max_length=20)


class UpdateMemberRoleRequest(BaseModel):
    project_role: str = Field(..., min_length=1, max_length=20)


# =============================================================================
# 项目列表
# =============================================================================

@router.get("")
async def list_projects(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
    keyword: Optional[str] = Query(None, max_length=100),
    status: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
) -> dict:
    """获取项目列表（分页 + 搜索 + 状态过滤）。"""
    token = _extract_token(authorization)

    result = project_service.list_projects(
        token=token,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success_response(data=result)


# =============================================================================
# 创建项目
# =============================================================================

@router.post("")
async def create_project(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateProjectRequest = Body(...),
) -> dict:
    """创建新项目。创建人自动成为 owner 和 leader。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = project_service.create_project(
        token=token,
        project_name=body.project_name,
        project_type=body.project_type,
        description=body.description,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 项目详情
# =============================================================================

@router.get("/{project_id:int}")
async def get_project(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取项目详情（需有权限）。"""
    token = _extract_token(authorization)

    result = project_service.get_project_detail(
        token=token,
        project_id=project_id,
    )
    return success_response(data=result)


# =============================================================================
# 更新项目
# =============================================================================

@router.put("/{project_id:int}")
async def update_project(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: UpdateProjectRequest = Body(...),
) -> dict:
    """更新项目信息（仅 admin / owner / leader 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = project_service.update_project(
        token=token,
        project_id=project_id,
        project_name=body.project_name,
        project_type=body.project_type,
        description=body.description,
        status=body.status,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 删除项目（软删除）
# =============================================================================

@router.delete("/{project_id:int}")
async def delete_project(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """软删除项目（仅 admin / owner / leader 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    project_service.delete_project(
        token=token,
        project_id=project_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data={})


# =============================================================================
# 项目归档
# =============================================================================

@router.post("/{project_id:int}/archive")
async def archive_project(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """归档项目（仅 admin / owner / leader 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = project_service.archive_project(
        token=token,
        project_id=project_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 项目成员列表
# =============================================================================

@router.get("/{project_id:int}/members")
async def list_project_members(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取项目成员列表（需有权限）。"""
    token = _extract_token(authorization)

    result = project_service.list_project_members(
        token=token,
        project_id=project_id,
    )
    return success_response(data=result)


# =============================================================================
# 添加项目成员
# =============================================================================

@router.post("/{project_id:int}/members")
async def add_project_member(
    request: Request,
    project_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: AddMemberRequest = Body(...),
) -> dict:
    """添加项目成员（仅 admin / owner / leader 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = project_service.add_project_member(
        token=token,
        project_id=project_id,
        user_id=body.user_id,
        project_role=body.project_role,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 修改项目成员角色
# =============================================================================

@router.put("/{project_id:int}/members/{member_id:int}")
async def update_project_member_role(
    request: Request,
    project_id: int = Path(..., gt=0),
    member_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: UpdateMemberRoleRequest = Body(...),
) -> dict:
    """修改项目成员角色（仅 admin / owner / leader 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = project_service.update_project_member_role(
        token=token,
        project_id=project_id,
        member_id=member_id,
        project_role=body.project_role,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 移除项目成员
# =============================================================================

@router.delete("/{project_id:int}/members/{member_id:int}")
async def remove_project_member(
    request: Request,
    project_id: int = Path(..., gt=0),
    member_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """移除项目成员（仅 admin / owner / leader 可操作，软删除）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    project_service.remove_project_member(
        token=token,
        project_id=project_id,
        member_id=member_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data={})
