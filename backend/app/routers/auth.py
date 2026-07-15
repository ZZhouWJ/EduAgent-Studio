"""
认证路由。

POST /api/auth/register - 用户注册
POST /api/auth/login   - 用户登录
GET  /api/auth/me      - 当前用户
PUT  /api/auth/me/password - 修改密码
POST /api/auth/logout  - 登出
"""

import logging
from typing import Optional

from fastapi import APIRouter, Body, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.services import auth_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/auth", tags=["认证"])
logger = logging.getLogger(__name__)


def _unexpected_auth_error(action: str, exc: Exception):
    logger.exception("认证操作失败: action=%s error=%s", action, exc)
    return error_response(
        message="操作失败，请稍后重试",
        code=5000,
        status_code=500,
    )


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=50)
    student_no: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_ids: Optional[list[int]] = Field(
        None,
        description="注册时选择的角色 ID 列表（不含 admin）",
    )


class UpdateProfileRequest(BaseModel):
    real_name: str = Field(..., min_length=1, max_length=50)
    student_no: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UpdateMyRolesRequest(BaseModel):
    role_ids: list[int] = Field(..., description="新的角色 ID 列表（不含 admin）")


class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)


def _extract_token(authorization: Optional[str]) -> str:
    """从 Authorization 头解析 Bearer token。"""
    if not authorization:
        raise UnauthorizedException(message="未提供认证信息")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="认证信息格式错误")
    return parts[1]


def _get_client_ip(request: Request) -> str:
    """提取客户端 IP 地址。"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login")
async def login(request: Request, body: LoginRequest) -> dict:
    """
    用户登录。

    成功返回 token 和用户基本信息。
    失败写入 login_logs，返回统一错误格式。
    """
    ip_address = _get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")

    result = auth_service.login(
        username=body.username,
        password=body.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    if not result["success"]:
        return error_response(
            message=result["reason"],
            code=4002,
        )

    return success_response(
        data={
            "token": result["token"],
            "user": result["user"],
        },
    )


@router.get("/me")
async def get_me(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    获取当前登录用户信息。

    从 Authorization: Bearer <token> 中解析用户。
    返回用户基本信息、角色列表、权限列表。
    不返回 password_hash。
    """
    token = _extract_token(authorization)
    user = auth_service.get_current_user(token)

    if user is None:
        return error_response(
            message="Token 无效或已过期",
            code=4002,
        )

    return success_response(data=user)


@router.post("/logout")
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    用户登出。

    课程版不实现 token 黑名单，仅写入操作日志后返回成功。
    """
    try:
        token = _extract_token(authorization)
    except UnauthorizedException:
        return success_response(data={})

    user = auth_service.get_current_user(token)
    if user:
        ip_address = _get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        auth_service.logout(
            user_id=user["user_id"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

    return success_response(data={})


@router.post("/register")
async def register(request: Request, body: RegisterRequest) -> dict:
    """
    用户注册。

    注册成功后返回新用户信息，不返回 token（需登录）。
    """
    ip_address = _get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")

    try:
        user = auth_service.register(
            username=body.username,
            password=body.password,
            confirm_password=body.confirm_password,
            real_name=body.real_name,
            student_no=body.student_no,
            email=body.email,
            phone=body.phone,
            role_ids=body.role_ids,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return success_response(data=user)
    except Exception as e:
        if hasattr(e, "code") and hasattr(e, "message"):
            return error_response(message=e.message, code=e.code)
        return _unexpected_auth_error("register", e)


@router.put("/me")
async def update_my_profile(
    request: Request,
    body: UpdateProfileRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    修改当前用户的基本信息（用户名不可修改）。

    需要提供有效的 token。
    """
    token = _extract_token(authorization)
    ip_address = _get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")

    try:
        updated_user = auth_service.update_my_profile(
            token=token,
            real_name=body.real_name,
            student_no=body.student_no,
            email=body.email,
            phone=body.phone,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return success_response(data=updated_user)
    except Exception as e:
        if hasattr(e, "code") and hasattr(e, "message"):
            return error_response(message=e.message, code=e.code)
        return _unexpected_auth_error("update_profile", e)


@router.patch("/me/roles")
async def update_my_roles(
    request: Request,
    body: UpdateMyRolesRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    当前用户修改自己的角色（不可选择 admin）。

    需要提供有效的 token。
    """
    token = _extract_token(authorization)
    ip_address = _get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")

    try:
        auth_service.update_my_roles(
            token=token,
            role_ids=body.role_ids,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return success_response(data={})
    except Exception as e:
        if hasattr(e, "code") and hasattr(e, "message"):
            return error_response(message=e.message, code=e.code)
        return _unexpected_auth_error("update_roles", e)


@router.put("/me/password")
async def update_my_password(
    request: Request,
    body: UpdatePasswordRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    修改当前用户密码。

    需要提供旧密码进行验证。
    """
    token = _extract_token(authorization)
    ip_address = _get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")

    try:
        auth_service.update_password(
            token=token,
            old_password=body.old_password,
            new_password=body.new_password,
        )
        return success_response(data={})
    except Exception as e:
        if hasattr(e, "code") and hasattr(e, "message"):
            return error_response(message=e.message, code=e.code)
        return _unexpected_auth_error("update_password", e)


@router.get("/roles")
async def list_my_roles() -> dict:
    """
    获取角色列表（不含 admin，用于个人中心等普通用户页面）。
    无需特殊权限。
    """
    roles = auth_service.list_roles_public()
    return success_response(data=roles)
