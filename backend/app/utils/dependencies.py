"""
FastAPI 通用 RBAC 依赖。

提供 require_role / require_permission 两个依赖工厂，
用于路由层的角色和权限校验。
"""

from typing import List

from fastapi import Depends, Header, Request
from fastapi.exceptions import HTTPException

from app.services.auth_service import get_current_user
from app.utils.exceptions import ForbiddenException, UnauthorizedException


def _extract_token(request: Request) -> str:
    """从 Authorization header 提取 Bearer token。"""
    auth = request.headers.get("Authorization")
    if not auth:
        raise UnauthorizedException(message="缺少认证信息")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="认证信息格式错误")
    return parts[1]


def _get_current_user_dependency(request: Request) -> dict:
    """FastAPI 依赖：从请求中解析当前登录用户。"""
    token = _extract_token(request)
    user = get_current_user(token)
    if not user:
        raise UnauthorizedException(message="Token 无效或已过期")
    return user


# 公开别名，用于端点只需登录不限制角色的场景
get_current_user_dep = _get_current_user_dependency


def require_role(*roles: str):
    """
    角色校验依赖工厂。

    Usage:
        @router.get("/admin/users")
        async def list_users(user: dict = Depends(require_role("admin"))):
            ...

    可传多个角色，满足其一即可：
        Depends(require_role("teacher", "admin"))
    """

    def _check(user: dict = Depends(_get_current_user_dependency)) -> dict:
        user_roles = user.get("roles", [])
        if not any(r in user_roles for r in roles):
            raise ForbiddenException(message=f"需要以下角色之一: {', '.join(roles)}")
        return user

    return _check


def require_permission(*permissions: str):
    """
    权限校验依赖工厂。

    Usage:
        @router.post("/api/projects")
        async def create_project(user: dict = Depends(require_permission("project:create"))):
            ...

    可传多个权限，满足其一即可。
    """

    def _check(user: dict = Depends(_get_current_user_dependency)) -> dict:
        user_perms = set(user.get("permissions", []))
        if not any(p in user_perms for p in permissions):
            raise ForbiddenException(message=f"需要以下权限之一: {', '.join(permissions)}")
        return user

    return _check
