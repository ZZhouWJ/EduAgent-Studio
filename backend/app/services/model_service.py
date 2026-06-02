"""
模型管理 Service 层。

处理模型供应商、AI模型、API配置相关业务逻辑。
"""

from typing import Any, Dict, List, Optional

from app.database import get_db_transaction
from app.repositories import model_repo, user_repo
from app.utils.crypto import encrypt_api_key, mask_api_key
from app.utils.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


# =============================================================================
# 权限辅助
# =============================================================================

def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def _require_admin(user: Dict[str, Any]) -> None:
    if not _is_admin(user):
        raise ForbiddenException(message="只有管理员可以执行此操作")


# =============================================================================
# 模型供应商
# =============================================================================

def list_providers(
    token: str,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """查询模型供应商列表（已登录用户均可查看）。"""
    _require_auth(token)
    rows = model_repo.list_providers(status=status)
    return [_provider_row_to_dict(r) for r in rows]


def create_provider(
    token: str,
    provider_name: str,
    provider_code: str,
    base_url: str,
    website: Optional[str] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建模型供应商（仅 admin 可操作）。"""
    user = _require_auth(token)
    _require_admin(user)

    if not provider_name or not provider_name.strip():
        raise ValidationException(message="供应商名称不能为空")
    if not provider_code or not provider_code.strip():
        raise ValidationException(message="供应商代码不能为空")
    if not base_url or not base_url.strip():
        raise ValidationException(message="供应商地址不能为空")

    if model_repo.is_provider_code_exists(provider_code):
        raise ValidationException(message="供应商代码已存在")

    provider_id: int = 0

    with get_db_transaction() as conn:
        provider_id = model_repo.create_provider(
            provider_name=provider_name.strip(),
            provider_code=provider_code.strip(),
            base_url=base_url.strip(),
            website=(website.strip() if website else None),
            description=(description.strip() if description else None),
            created_by=user["user_id"],
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="model_provider:create",
            action_desc=f"创建模型供应商: {provider_name.strip()}",
            target_type="model_provider",
            target_id=provider_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {"provider_id": provider_id}


# =============================================================================
# AI 模型
# =============================================================================

def list_models(
    token: str,
    provider_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """分页查询 AI 模型列表（已登录用户均可查看）。"""
    _require_auth(token)

    rows, total = model_repo.list_models(
        provider_id=provider_id,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [_model_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def create_model(
    token: str,
    provider_id: int,
    model_name: str,
    display_name: str,
    capability_tags: Optional[str] = None,
    max_context: int = 4096,
    input_price: float = 0.0,
    output_price: float = 0.0,
    price_unit: str = "1K_TOKENS",
    status: str = "active",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建 AI 模型（仅 admin 可操作）。"""
    user = _require_auth(token)
    _require_admin(user)

    if not model_name or not model_name.strip():
        raise ValidationException(message="模型名称不能为空")
    if not display_name or not display_name.strip():
        raise ValidationException(message="模型显示名称不能为空")

    provider = model_repo.get_provider_by_id(provider_id)
    if provider is None:
        raise NotFoundException(message="模型供应商不存在")

    if model_repo.is_model_name_exists_in_provider(provider_id, model_name.strip()):
        raise ValidationException(message="该供应商下已存在同名模型")

    model_id: int = 0

    with get_db_transaction() as conn:
        model_id = model_repo.create_model(
            provider_id=provider_id,
            model_name=model_name.strip(),
            display_name=display_name.strip(),
            capability_tags=(capability_tags.strip() if capability_tags else None),
            max_context=max_context,
            input_price=input_price,
            output_price=output_price,
            price_unit=price_unit,
            status=status,
            created_by=user["user_id"],
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="ai_model:create",
            action_desc=f"创建 AI 模型: {display_name.strip()}",
            target_type="ai_model",
            target_id=model_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {"model_id": model_id}


# =============================================================================
# API 配置
# =============================================================================

def list_api_configs(
    token: str,
    provider_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """查询 API 配置列表（仅 admin 可查看，不返回加密字段）。"""
    user = _require_auth(token)
    _require_admin(user)

    rows, total = model_repo.list_api_configs(
        provider_id=provider_id,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [_api_config_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def create_api_config(
    token: str,
    provider_id: int,
    config_name: str,
    api_key: str,
    quota_limit: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建 API 配置（仅 admin 可操作，API Key 加密保存）。"""
    user = _require_auth(token)
    _require_admin(user)

    if not api_key or not api_key.strip():
        raise ValidationException(message="API Key 不能为空")

    provider = model_repo.get_provider_by_id(provider_id)
    if provider is None:
        raise NotFoundException(message="模型供应商不存在")

    encrypted_data, iv, tag, key_version = encrypt_api_key(api_key.strip())
    key_mask = mask_api_key(api_key.strip())

    config_id: int = 0

    with get_db_transaction() as conn:
        config_id = model_repo.create_api_config(
            provider_id=provider_id,
            config_name=config_name.strip(),
            encrypted_api_key=encrypted_data,
            key_iv=iv,
            key_tag=tag,
            key_version=key_version,
            key_mask=key_mask,
            quota_limit=quota_limit,
            created_by=user["user_id"],
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="api_config:create",
            action_desc=f"创建 API 配置: {config_name.strip()} (masked: {key_mask})",
            target_type="api_config",
            target_id=config_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {"api_config_id": config_id, "key_mask": key_mask}


# =============================================================================
# 数据转换
# =============================================================================

def _model_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "model_id": row["model_id"],
        "provider_id": row["provider_id"],
        "model_name": row["model_name"],
        "display_name": row["display_name"],
        "capability_tags": row.get("capability_tags"),
        "max_context": row.get("max_context"),
        "input_price": float(row["input_price"]) if row.get("input_price") is not None else 0.0,
        "output_price": float(row["output_price"]) if row.get("output_price") is not None else 0.0,
        "price_unit": row.get("price_unit"),
        "status": row["status"],
        "created_at": row.get("created_at"),
        "provider_name": row.get("provider_name"),
        "provider_code": row.get("provider_code"),
    }


def _provider_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """对供应商行数据做浅拷贝，直接返回（数据已是正确编码）。"""
    if row is None:
        return {}
    return dict(row)


def _api_config_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "api_config_id": row["api_config_id"],
        "provider_id": row["provider_id"],
        "config_name": row["config_name"],
        "key_mask": row["key_mask"],
        "key_version": row.get("key_version"),
        "status": row["status"],
        "quota_limit": row["quota_limit"],
        "used_quota": row.get("used_quota"),
        "created_at": row.get("created_at"),
        "provider_name": row.get("provider_name"),
    }
