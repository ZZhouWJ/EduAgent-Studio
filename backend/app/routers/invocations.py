"""
调用日志与生成路由。

GET    /api/invocations
GET    /api/invocations/{invocation_id}
"""

from typing import Optional

from fastapi import APIRouter, Header, Path, Query

from app.services import invocation_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(tags=["AI 调用与日志"])


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise UnauthorizedException(message="未登录")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="认证信息格式错误")
    return parts[1]


# =============================================================================
# 调用日志
# =============================================================================

@router.get("/invocations")
async def list_invocations(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
    task_id: Optional[int] = Query(None, gt=0),
    model_id: Optional[int] = Query(None, gt=0),
    status: Optional[str] = Query(None, max_length=20),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
) -> dict:
    """
    分页查询调用日志列表。

    admin 可查看全部，普通成员只能查看自己有权限项目内的记录。
    """
    token = _extract_token(authorization)

    result = invocation_service.list_invocations(
        token=token,
        project_id=project_id,
        task_id=task_id,
        model_id=model_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


@router.get("/invocations/{invocation_id}")
async def get_invocation_detail(
    invocation_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取调用详情（需有项目访问权限）。"""
    token = _extract_token(authorization)

    result = invocation_service.get_invocation_detail(
        token=token,
        invocation_id=invocation_id,
    )
    return success_response(data=result)
