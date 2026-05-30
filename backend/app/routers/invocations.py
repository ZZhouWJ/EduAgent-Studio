"""
调用日志与生成路由。

POST   /api/tasks/{task_id}/generate
GET    /api/invocations
GET    /api/invocations/{invocation_id}
"""

from typing import List, Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

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


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =============================================================================
# 请求体模型
# =============================================================================

class GenerateRequest(BaseModel):
    model_ids: List[int] = Field(..., min_length=1)
    branch_id: Optional[int] = Field(None, gt=0)
    prompt_version_id: Optional[int] = Field(None, gt=0)
    input_text: str = Field(..., min_length=1)


# =============================================================================
# 任务模型生成
# =============================================================================

@router.post("/api/tasks/{task_id}/generate")
async def generate_task_outputs(
    request: Request,
    task_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: GenerateRequest = Body(...),
) -> dict:
    """
    任务模型生成（调用 Mock 模型）。

    支持批量模型调用，每个模型单独记录调用结果。
    """
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    results = invocation_service.generate_task_outputs(
        token=token,
        task_id=task_id,
        model_ids=body.model_ids,
        input_text=body.input_text,
        branch_id=body.branch_id,
        prompt_version_id=body.prompt_version_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=results)


# =============================================================================
# 调用日志
# =============================================================================

@router.get("/api/invocations")
async def list_invocations(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    project_id: Optional[int] = Query(None, gt=0),
    task_id: Optional[int] = Query(None, gt=0),
    model_id: Optional[int] = Query(None, gt=0),
    status: Optional[str] = Query(None, max_length=20),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
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


@router.get("/api/invocations/{invocation_id}")
async def get_invocation_detail(
    request: Request,
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
