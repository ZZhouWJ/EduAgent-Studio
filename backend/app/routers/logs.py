"""
日志路由。

GET /api/logs/operation - 操作日志列表
GET /api/logs/login     - 登录日志列表
"""

from typing import Optional

from fastapi import APIRouter, Header, Query
from pydantic import BaseModel

from app.services import auth_service, user_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(prefix="", tags=["日志"])


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


@router.get("/logs/operation")
async def list_operation_logs(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    user_id: Optional[int] = Query(None, description="按用户 ID 过滤"),
    target_type: Optional[str] = Query(None, description="按目标类型过滤（project/task/output/review）"),
    action_type: Optional[str] = Query(None, description="按操作类型过滤"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
) -> dict:
    """
    获取操作日志列表（分页 + 多条件过滤）。

    仅登录用户可访问。
    """
    current_user = _resolve_current_user(authorization)

    result = user_service.list_operation_logs_service(
        page=page,
        page_size=page_size,
        user_id=user_id,
        target_type=target_type,
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
    )
    return success_response(data=result)


@router.get("/logs/login")
async def list_login_logs(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    user_id: Optional[int] = Query(None, description="按用户 ID 过滤"),
    login_status: Optional[str] = Query(None, description="按登录状态过滤（success/failed）"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
) -> dict:
    """
    获取登录日志列表（分页 + 多条件过滤）。

    仅登录用户可访问。
    """
    current_user = _resolve_current_user(authorization)

    result = user_service.list_login_logs_service(
        page=page,
        page_size=page_size,
        user_id=user_id,
        login_status=login_status,
        start_date=start_date,
        end_date=end_date,
    )
    return success_response(data=result)
