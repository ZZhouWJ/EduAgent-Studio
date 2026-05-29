"""
认证路由。

POST /api/auth/login   - 用户登录
GET  /api/auth/me      - 当前用户
POST /api/auth/logout  - 登出
"""

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.services import auth_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/api/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


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
