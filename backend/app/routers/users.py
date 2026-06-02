"""
用户管理路由。

GET /api/users       - 用户列表（分页 + 搜索）
PUT /api/users/{user_id}/status - 更新用户状态
PUT /api/users/{user_id}/roles  - 更新用户角色
GET /api/roles       - 角色列表
GET /api/permissions - 权限列表

注意：本阶段只实现查询，PUT/DELETE 等修改操作在后续阶段实现。
"""

from typing import Optional

from fastapi import APIRouter, Body, Header, Path, Query
from pydantic import BaseModel, Field

from app.repositories import user_repo
from app.services import auth_service, user_service
from app.utils.exceptions import ForbiddenException, UnauthorizedException
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/api", tags=["用户与权限"])


def _resolve_current_user(authorization: Optional[str]) -> dict:
    """从 Authorization 头解析当前用户，未登录则抛出异常。"""
    if not authorization:
        raise UnauthorizedException(message="未登录")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="认证信息格式错误")
    user = auth_service.get_current_user(parts[1])
    if user is None:
        raise UnauthorizedException(message="Token 无效或已过期")
    return user


def _check_admin(user: dict) -> None:
    """检查用户是否为管理员，非管理员抛出权限不足异常。"""
    if "admin" not in user.get("roles", []):
        raise ForbiddenException(message="需要管理员权限")


class UpdateStatusBody(BaseModel):
    status: str = Field(..., description="新状态（active/inactive/suspended）")


class UpdateRolesBody(BaseModel):
    role_ids: list[int] = Field(..., description="角色 ID 列表")


@router.get("/users")
async def list_users(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="按状态过滤（active/inactive/suspended）"),
) -> dict:
    """
    获取用户列表（分页 + 关键字搜索 + 状态过滤）。

    仅管理员可访问。
    返回用户列表、角色，不返回 password_hash。
    """
    try:
        current_user = _resolve_current_user(authorization)
        _check_admin(current_user)
    except (UnauthorizedException, ForbiddenException):
        raise

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
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    启用或禁用用户账户（仅管理员可操作）。

    Args:
        user_id: 用户 ID
        body: 包含新状态
    """
    try:
        current_user = _resolve_current_user(authorization)
        _check_admin(current_user)
    except (UnauthorizedException, ForbiddenException):
        raise

    user_service.update_user_status_service(user_id=user_id, new_status=body.status)
    return success_response(data={})


@router.put("/users/{user_id}/roles")
async def update_user_roles(
    user_id: int = Path(..., gt=0),
    body: UpdateRolesBody = Body(...),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    更新用户角色（仅管理员可操作）。

    Args:
        user_id: 用户 ID
        body: 包含新的角色 ID 列表
    """
    try:
        current_user = _resolve_current_user(authorization)
        _check_admin(current_user)
    except (UnauthorizedException, ForbiddenException):
        raise

    user_service.update_user_roles_service(user_id=user_id, role_ids=body.role_ids)
    return success_response(data={})


@router.get("/roles")
async def list_roles(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    获取角色列表。

    登录用户均可访问。
    """
    try:
        current_user = _resolve_current_user(authorization)
    except (UnauthorizedException, ForbiddenException):
        raise

    roles = user_service.list_roles_service()
    return success_response(data=roles)


@router.get("/permissions")
async def list_permissions(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    获取权限列表。

    登录用户均可访问。
    """
    try:
        current_user = _resolve_current_user(authorization)
    except (UnauthorizedException, ForbiddenException):
        raise

    permissions = user_service.list_permissions_service()
    return success_response(data=permissions)
