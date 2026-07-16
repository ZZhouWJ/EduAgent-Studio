"""
提示词模板管理路由。

任务类型相关：
GET /api/task-types

提示词模板相关：
GET    /api/prompt-templates
POST   /api/prompt-templates
GET    /api/prompt-templates/{template_id}
PUT    /api/prompt-templates/{template_id}
DELETE /api/prompt-templates/{template_id}

提示词版本相关：
GET    /api/prompt-templates/{template_id}/versions
POST   /api/prompt-templates/{template_id}/versions
POST   /api/prompt-templates/{template_id}/versions/{version_id}/activate
"""

from typing import Dict, Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import prompt_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(tags=["提示词模板管理"])


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

class CreateTemplateRequest(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=200)
    task_type_id: int = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    initial_prompt_content: Optional[str] = Field(None, max_length=200_000)
    change_note: Optional[str] = Field(None, max_length=500)
    activate: bool = Field(False)


class UpdateTemplateRequest(BaseModel):
    template_name: Optional[str] = Field(None, min_length=1, max_length=200)
    task_type_id: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)


class CreateVersionRequest(BaseModel):
    version_no: Optional[str] = Field(None, max_length=20)
    prompt_content: str = Field(..., min_length=1)
    change_note: Optional[str] = Field(None, max_length=500)


class RenderTemplateRequest(BaseModel):
    version_id: Optional[int] = Field(None, gt=0)
    variables: Dict[str, str] = Field(default_factory=dict)


# =============================================================================
# 任务类型列表
# =============================================================================

@router.get("/task-types")
async def list_task_types(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """查询任务类型列表（已登录用户均可查看）。"""
    token = _extract_token(authorization)

    result = prompt_service.list_task_types(token=token)
    return success_response(data=result)


# =============================================================================
# 提示词模板列表
# =============================================================================

@router.get("/prompt-templates")
async def list_templates(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    task_type_id: Optional[int] = Query(None, gt=0),
    keyword: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
) -> dict:
    """分页查询提示词模板列表（已登录用户均可查看）。"""
    token = _extract_token(authorization)

    result = prompt_service.list_templates(
        token=token,
        task_type_id=task_type_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


# =============================================================================
# 创建提示词模板
# =============================================================================

@router.post("/prompt-templates")
async def create_template(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateTemplateRequest = Body(...),
) -> dict:
    """创建提示词模板（admin / teacher / project_leader 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = prompt_service.create_template(
        token=token,
        template_name=body.template_name,
        task_type_id=body.task_type_id,
        description=body.description,
        initial_prompt_content=body.initial_prompt_content,
        change_note=body.change_note,
        activate=body.activate,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 提示词模板详情
# =============================================================================

@router.get("/prompt-templates/{template_id}")
async def get_template_detail(
    request: Request,
    template_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """获取模板详情（已登录用户均可查看）。"""
    token = _extract_token(authorization)

    result = prompt_service.get_template_detail(
        token=token,
        template_id=template_id,
    )
    return success_response(data=result)


# =============================================================================
# 更新提示词模板
# =============================================================================

@router.put("/prompt-templates/{template_id}")
async def update_template(
    request: Request,
    template_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: UpdateTemplateRequest = Body(...),
) -> dict:
    """更新提示词模板（admin / teacher / project_leader / 模板创建人可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = prompt_service.update_template(
        token=token,
        template_id=template_id,
        template_name=body.template_name,
        task_type_id=body.task_type_id,
        description=body.description,
        is_active=body.is_active,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 软删除提示词模板
# =============================================================================

@router.delete("/prompt-templates/{template_id}")
async def delete_template(
    request: Request,
    template_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """软删除提示词模板（admin / teacher / project_leader / 模板创建人可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    prompt_service.delete_template(
        token=token,
        template_id=template_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data={})


# =============================================================================
# 提示词版本列表
# =============================================================================

@router.get("/prompt-templates/{template_id}/versions")
async def list_template_versions(
    request: Request,
    template_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """查询模板的版本列表（已登录用户均可查看）。"""
    token = _extract_token(authorization)

    result = prompt_service.list_template_versions(
        token=token,
        template_id=template_id,
    )
    return success_response(data=result)


# =============================================================================
# 渲染提示词预览
# =============================================================================

@router.post("/prompt-templates/{template_id}/render")
async def render_template(
    request: Request,
    template_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: RenderTemplateRequest = Body(...),
) -> dict:
    """使用受控变量替换渲染提示词，不执行模型调用。"""
    token = _extract_token(authorization)
    result = prompt_service.render_template(
        token=token,
        template_id=template_id,
        version_id=body.version_id,
        variables=body.variables,
    )
    return success_response(data=result)


# =============================================================================
# 创建提示词版本
# =============================================================================

@router.post("/prompt-templates/{template_id}/versions")
async def create_version(
    request: Request,
    template_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateVersionRequest = Body(...),
) -> dict:
    """创建提示词版本（admin / teacher / project_leader / 模板创建人可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = prompt_service.create_version(
        token=token,
        template_id=template_id,
        version_no=body.version_no,
        prompt_content=body.prompt_content,
        change_note=body.change_note,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# 启用提示词版本
# =============================================================================

@router.post("/prompt-templates/{template_id}/versions/{version_id}/activate")
async def activate_version(
    request: Request,
    template_id: int = Path(..., gt=0),
    version_id: int = Path(..., gt=0),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """启用指定版本为模板当前活动版本（admin / teacher / project_leader / 模板创建人可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = prompt_service.activate_version(
        token=token,
        template_id=template_id,
        version_id=version_id,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)
