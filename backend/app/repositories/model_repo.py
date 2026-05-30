"""
模型管理 Repository 层。

处理模型供应商、AI模型、API配置相关数据库操作。
所有数据库操作使用参数化 SQL，不拼接用户输入。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pymysql.connections import Connection

from app.database import get_db_cursor


# =============================================================================
# 模型供应商查询
# =============================================================================

def get_provider_by_id(provider_id: int) -> Optional[Dict[str, Any]]:
    """按 ID 查询模型供应商。"""
    sql = """
        SELECT provider_id, provider_name, provider_code, base_url,
               website, description, status,
               created_at, updated_at
        FROM model_providers
        WHERE provider_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (provider_id,))
        return cursor.fetchone()


def list_providers(
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    查询模型供应商列表。

    Args:
        status: 可选，状态过滤

    Returns:
        供应商列表
    """
    if status:
        sql = """
            SELECT provider_id, provider_name, provider_code, base_url,
                   website, description, status,
                   created_at, updated_at
            FROM model_providers
            WHERE is_deleted = 0 AND status = %s
            ORDER BY created_at ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (status,))
            return cursor.fetchall()
    else:
        sql = """
            SELECT provider_id, provider_name, provider_code, base_url,
                   website, description, status,
                   created_at, updated_at
            FROM model_providers
            WHERE is_deleted = 0
            ORDER BY created_at ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


def is_provider_code_exists(provider_code: str) -> bool:
    """检查 provider_code 是否已存在。"""
    sql = "SELECT 1 FROM model_providers WHERE provider_code = %s AND is_deleted = 0"
    with get_db_cursor() as cursor:
        cursor.execute(sql, (provider_code,))
        return cursor.fetchone() is not None


# =============================================================================
# 模型供应商写操作
# =============================================================================

def create_provider(
    provider_name: str,
    provider_code: str,
    base_url: str,
    website: Optional[str],
    description: Optional[str],
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建模型供应商。

    Returns:
        新供应商 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO model_providers
            (provider_name, provider_code, base_url, website, description,
             status, is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, 'active', 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                provider_name, provider_code, base_url,
                website, description, now, created_by,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                provider_name, provider_code, base_url,
                website, description, now, created_by,
            ))
            return cursor.lastrowid


# =============================================================================
# AI 模型查询
# =============================================================================

def get_model_by_id(model_id: int) -> Optional[Dict[str, Any]]:
    """按 ID 查询 AI 模型。"""
    sql = """
        SELECT m.model_id, m.provider_id, m.model_name, m.display_name,
               m.capability_tags, m.max_context,
               m.input_price, m.output_price, m.price_unit,
               m.status, m.is_deleted,
               m.created_at, m.updated_at,
               p.provider_name, p.provider_code
        FROM ai_models m
        INNER JOIN model_providers p ON m.provider_id = p.provider_id
            AND p.is_deleted = 0
        WHERE m.model_id = %s AND m.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (model_id,))
        return cursor.fetchone()


def list_models(
    provider_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询 AI 模型列表。

    Returns:
        (模型列表, 总数)
    """
    offset = (page - 1) * page_size

    base_where = "m.is_deleted = 0"

    filters = []
    params: list = []

    if provider_id is not None:
        filters.append("m.provider_id = %s")
        params.append(provider_id)

    if status:
        filters.append("m.status = %s")
        params.append(status)

    if keyword:
        like = f"%{keyword}%"
        filters.append("(m.model_name LIKE %s OR m.display_name LIKE %s)")
        params.extend([like, like])

    where_parts = [base_where] + filters
    where_clause = " AND ".join(where_parts)

    count_sql = f"SELECT COUNT(*) AS total FROM ai_models m WHERE {where_clause}"

    data_sql = f"""
        SELECT m.model_id, m.provider_id, m.model_name, m.display_name,
               m.capability_tags, m.max_context,
               m.input_price, m.output_price, m.price_unit,
               m.status, m.created_at,
               p.provider_name, p.provider_code
        FROM ai_models m
        INNER JOIN model_providers p ON m.provider_id = p.provider_id
            AND p.is_deleted = 0
        WHERE {where_clause}
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


def is_model_name_exists_in_provider(provider_id: int, model_name: str) -> bool:
    """检查同一供应商下 model_name 是否重复。"""
    sql = """
        SELECT 1 FROM ai_models
        WHERE provider_id = %s AND model_name = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (provider_id, model_name))
        return cursor.fetchone() is not None


# =============================================================================
# AI 模型写操作
# =============================================================================

def create_model(
    provider_id: int,
    model_name: str,
    display_name: str,
    capability_tags: Optional[str],
    max_context: int,
    input_price: float,
    output_price: float,
    price_unit: str,
    status: str,
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建 AI 模型。

    Returns:
        新模型 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO ai_models
            (provider_id, model_name, display_name, capability_tags,
             max_context, input_price, output_price, price_unit,
             status, is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                provider_id, model_name, display_name, capability_tags,
                max_context, input_price, output_price, price_unit,
                status, now, created_by,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                provider_id, model_name, display_name, capability_tags,
                max_context, input_price, output_price, price_unit,
                status, now, created_by,
            ))
            return cursor.lastrowid


# =============================================================================
# API 配置查询
# =============================================================================

def list_api_configs(
    provider_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    查询 API 配置列表（不返回加密字段）。

    Returns:
        (配置列表, 总数)
    """
    offset = (page - 1) * page_size

    if provider_id is not None:
        where_clause = "c.is_deleted = 0 AND c.provider_id = %s"
        params = [provider_id]
    else:
        where_clause = "c.is_deleted = 0"
        params = []

    count_sql = f"SELECT COUNT(*) AS total FROM api_configs c WHERE {where_clause}"

    data_sql = f"""
        SELECT c.api_config_id, c.provider_id, c.config_name,
               c.key_mask, c.key_version,
               c.status, c.quota_limit, c.used_quota,
               c.created_at, c.updated_at,
               p.provider_name, p.provider_code
        FROM api_configs c
        INNER JOIN model_providers p ON c.provider_id = p.provider_id
            AND p.is_deleted = 0
        WHERE {where_clause}
        ORDER BY c.created_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# API 配置写操作
# =============================================================================

def create_api_config(
    provider_id: int,
    config_name: str,
    encrypted_api_key: str,
    key_iv: str,
    key_tag: str,
    key_version: int,
    key_mask: str,
    quota_limit: int,
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建 API 配置（加密字段，值为 Base64 字符串）。

    Returns:
        新配置 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO api_configs
            (provider_id, config_name, encrypted_api_key, key_iv, key_tag,
             key_version, key_mask,
             status, quota_limit, used_quota,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, 'active', %s, 0, 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                provider_id, config_name,
                encrypted_api_key, key_iv, key_tag, key_version, key_mask,
                quota_limit, now, created_by,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                provider_id, config_name,
                encrypted_api_key, key_iv, key_tag, key_version, key_mask,
                quota_limit, now, created_by,
            ))
            return cursor.lastrowid


def get_api_config_by_id(config_id: int) -> Optional[Dict[str, Any]]:
    """按 ID 查询 API 配置（含加密字段，供解密使用）。"""
    sql = """
        SELECT api_config_id, provider_id, config_name,
               encrypted_api_key, key_iv, key_tag, key_version, key_mask,
               status, quota_limit, used_quota,
               created_at, created_by
        FROM api_configs
        WHERE api_config_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (config_id,))
        return cursor.fetchone()
