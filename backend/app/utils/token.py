"""
JWT Token 工具。

提供 access_token 创建和解析，从环境变量读取密钥和过期时间。
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.config import get_settings


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建 JWT access_token。

    Args:
        data: 写入 token payload 的数据（建议包含 user_id、username）
        expires_delta: 可选，过期时间增量，默认 1440 分钟（1 天）

    Returns:
        JWT 字符串
    """
    to_encode = data.copy()
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解析 JWT token，验证签名和过期时间。

    Args:
        token: JWT 字符串

    Returns:
        解析成功返回 payload dict；token 无效或过期返回 None
    """
    try:
        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except (ExpiredSignatureError, InvalidTokenError):
        return None
