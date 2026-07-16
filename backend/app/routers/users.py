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
    status: str = Field(..., description="新状态（active/disabled）")


class UpdateRolesBody(BaseModel):
    role_ids: list[int] = Field(..., description="角色 ID 列表")


class CreateUserBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=50)
    role_ids: list[int] = Field(..., min_length=1, max_length=5)
    student_no: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


@router.get("/users")
async def list_users(
    user: dict = Depends(require_role("admin")),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="按状态过滤（active/disabled）"),
) -> dict:
    """获取用户列表（分页 + 关键字搜索 + 状态过滤）。仅管理员可访问。"""
    result = user_service.list_users_service(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success_response(data=result)


@router.post("/users")
async def create_user(
    body: CreateUserBody,
    user: dict = Depends(require_role("admin")),
) -> dict:
    """创建用户并分配角色。仅管理员可操作。"""
    created = auth_service.register(
        username=body.username,
        password=body.password,
        confirm_password=body.password,
        real_name=body.real_name,
        student_no=body.student_no,
        email=body.email,
        phone=body.phone,
        role_ids=body.role_ids,
        created_by=int(user["user_id"]),
        allow_admin_role=True,
    )
    return success_response(data=created, message="用户创建成功")


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
    """获取角色列表；管理员可查看全部角色。"""
    roles = (
        user_service.list_roles_service()
        if "admin" in user.get("roles", [])
        else auth_service.list_roles_public()
    )
    return success_response(data=roles)


@router.get("/permissions")
async def list_permissions(
    user: dict = Depends(get_current_user_dep),
) -> dict:
    """获取权限列表。登录用户均可访问。"""
    permissions = user_service.list_permissions_service()
    return success_response(data=permissions)
