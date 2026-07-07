"""
用户管理路由。

GET /api/users       - 用户列表（分页 + 搜索）
PUT /api/users/{user_id}/status - 更新用户状态
PUT /api/users/{user_id}/roles  - 更新用户角色
GET /api/roles       - 角色列表
GET /api/permissions - 权限列表
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import BaseModel, Field

from app.services import auth_service, user_service
from app.utils.dependencies import get_current_user_dep, require_role
from app.utils.response import success_response

router = APIRouter(prefix="", tags=["用户与权限"])


class UpdateStatusBody(BaseModel):
    status: str = Field(..., description="新状态（active/inactive/suspended）")


class UpdateRolesBody(BaseModel):
    role_ids: list[int] = Field(..., description="角色 ID 列表")


@router.get("/users")
async def list_users(
    user: dict = Depends(require_role("admin")),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="按状态过滤（active/inactive/suspended）"),
) -> dict:
    """获取用户列表（分页 + 关键字搜索 + 状态过滤）。仅管理员可访问。"""
    result = user_service.list_users_service(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success_response(data=result)


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int = Path(..., gt=0),
    body: UpdateStatusBody = Body(...),
    user: dict = Depends(require_role("admin")),
) -> dict:
    """启用或禁用用户账户（仅管理员可操作）。"""
    user_service.update_user_status_service(user_id=user_id, new_status=body.status)
    return success_response(data={})


@router.put("/users/{user_id}/roles")
async def update_user_roles(
    user_id: int = Path(..., gt=0),
    body: UpdateRolesBody = Body(...),
    user: dict = Depends(require_role("admin")),
) -> dict:
    """更新用户角色（仅管理员可操作）。"""
    user_service.update_user_roles_service(user_id=user_id, role_ids=body.role_ids)
    return success_response(data={})


@router.get("/roles")
async def list_roles(
    user: dict = Depends(get_current_user_dep),
) -> dict:
    """获取角色列表（不含 admin）。登录用户均可访问。"""
    roles = auth_service.list_roles_public()
    return success_response(data=roles)


@router.get("/permissions")
async def list_permissions(
    user: dict = Depends(get_current_user_dep),
) -> dict:
    """获取权限列表。登录用户均可访问。"""
    permissions = user_service.list_permissions_service()
    return success_response(data=permissions)
