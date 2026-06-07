"""
模型管理路由。

模型供应商相关：
GET    /api/model-providers
POST   /api/model-providers

AI 模型相关：
GET    /api/ai-models
POST   /api/ai-models

API 配置相关：
GET    /api/api-configs
POST   /api/api-configs
"""

from typing import Optional

from fastapi import APIRouter, Body, Header, Path, Query, Request
from pydantic import BaseModel, Field

from app.services import model_service
from app.utils.exceptions import UnauthorizedException
from app.utils.response import success_response

router = APIRouter(tags=["模型管理"])


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

class CreateProviderRequest(BaseModel):
    provider_name: str = Field(..., min_length=1, max_length=100)
    provider_code: str = Field(..., min_length=1, max_length=50)
    base_url: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class CreateModelRequest(BaseModel):
    provider_id: int = Field(..., gt=0)
    model_name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    capability_tags: Optional[str] = Field(None, max_length=200)
    max_context: int = Field(4096, ge=1)
    input_price: float = Field(0.0, ge=0)
    output_price: float = Field(0.0, ge=0)
    price_unit: str = Field("1K_TOKENS", max_length=20)
    status: str = Field("active", max_length=20)


class CreateApiConfigRequest(BaseModel):
    provider_id: int = Field(..., gt=0)
    config_name: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1)
    quota_limit: int = Field(..., ge=0)


# =============================================================================
# 模型供应商
# =============================================================================

@router.get("/api/model-providers")
async def list_providers(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    status: Optional[str] = Query(None, max_length=20),
) -> dict:
    """查询模型供应商列表（已登录用户均可查看）。"""
    token = _extract_token(authorization)

    result = model_service.list_providers(token=token, status=status)
    return success_response(data=result)


@router.post("/api/model-providers")
async def create_provider(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateProviderRequest = Body(...),
) -> dict:
    """创建模型供应商（仅 admin 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = model_service.create_provider(
        token=token,
        provider_name=body.provider_name,
        provider_code=body.provider_code,
        base_url=body.base_url,
        website=body.website,
        description=body.description,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# AI 模型
# =============================================================================

@router.get("/api/ai-models")
async def list_models(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    provider_id: Optional[int] = Query(None, gt=0),
    status: Optional[str] = Query(None, max_length=20),
    keyword: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
) -> dict:
    """分页查询 AI 模型列表（已登录用户均可查看）。"""
    token = _extract_token(authorization)

    result = model_service.list_models(
        token=token,
        provider_id=provider_id,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


@router.post("/api/ai-models")
async def create_model(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateModelRequest = Body(...),
) -> dict:
    """创建 AI 模型（仅 admin 可操作）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = model_service.create_model(
        token=token,
        provider_id=body.provider_id,
        model_name=body.model_name,
        display_name=body.display_name,
        capability_tags=body.capability_tags,
        max_context=body.max_context,
        input_price=body.input_price,
        output_price=body.output_price,
        price_unit=body.price_unit,
        status=body.status,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)


# =============================================================================
# API 配置
# =============================================================================

@router.get("/api/api-configs")
async def list_api_configs(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    provider_id: Optional[int] = Query(None, gt=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
) -> dict:
    """查询 API 配置列表（仅 admin 可查看，不返回加密字段）。"""
    token = _extract_token(authorization)

    result = model_service.list_api_configs(
        token=token,
        provider_id=provider_id,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


@router.post("/api/api-configs")
async def create_api_config(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    body: CreateApiConfigRequest = Body(...),
) -> dict:
    """创建 API 配置（仅 admin 可操作，API Key 加密保存）。"""
    token = _extract_token(authorization)
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")

    result = model_service.create_api_config(
        token=token,
        provider_id=body.provider_id,
        config_name=body.config_name,
        api_key=body.api_key,
        quota_limit=body.quota_limit,
        ip_address=ip,
        user_agent=ua,
    )
    return success_response(data=result)
