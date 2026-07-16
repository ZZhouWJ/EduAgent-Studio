"""
加密工具模块。

提供 API Key 的 AES-256-GCM 加密解密功能。
加密主密钥从环境变量 API_KEY_SECRET 读取，不硬编码。

所有加密结果均以 Base64 字符串形式返回/入库，与数据库 TEXT/VARCHAR 字段兼容。
"""

import base64
import os
import secrets
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_SECRET_ENV_VAR = "API_KEY_SECRET"
_KEY_VERSION = 1


def _get_master_key() -> bytes:
    """
    从环境变量获取 AES-256 主密钥。

    密钥必须为 32 字节（256 bit）。

    Returns:
        32 字节密钥

    Raises:
        RuntimeError: 环境变量不存在或密钥长度不正确
    """
    secret = os.environ.get(_SECRET_ENV_VAR)
    if not secret:
        raise RuntimeError(
            f"环境变量 {_SECRET_ENV_VAR} 未设置。"
            f"请在 .env 文件中设置 API_KEY_SECRET=<随机密钥>"
        )
    secret_bytes = secret.encode("utf-8")
    if len(secret_bytes) < 32:
        raise RuntimeError(
            f"环境变量 {_SECRET_ENV_VAR} 太短（至少需要 32 字符）。"
            f"请使用随机密钥，例如：openssl rand -hex 32"
        )
    return secret_bytes[:32]


def encrypt_api_key(plaintext: str) -> Tuple[str, str, str, int]:
    """
    使用 AES-256-GCM 加密 API Key，结果以 Base64 字符串形式返回。

    Args:
        plaintext: 明文 API Key

    Returns:
        (encrypted_base64, iv_base64, tag_base64, key_version)
        - encrypted_base64: 密文（Base64 字符串）
        - iv_base64: 初始化向量（Base64 字符串）
        - tag_base64: 认证标签（Base64 字符串）
        - key_version: 密钥版本号（当前固定为 1）
    """
    key = _get_master_key()
    aesgcm = AESGCM(key)
    iv = secrets.token_bytes(12)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    encrypted_b64 = base64.b64encode(ciphertext).decode("utf-8")
    iv_b64 = base64.b64encode(iv).decode("utf-8")
    tag_b64 = base64.b64encode(tag).decode("utf-8")
    return encrypted_b64, iv_b64, tag_b64, _KEY_VERSION


def decrypt_api_key(encrypted_base64: str, iv_base64: str, tag_base64: str) -> str:
    """
    解密 API Key（接受 Base64 字符串）。

    Args:
        encrypted_base64: 密文（Base64 字符串）
        iv_base64: 初始化向量（Base64 字符串）
        tag_base64: 认证标签（Base64 字符串）

    Returns:
        明文 API Key
    """
    key = _get_master_key()
    aesgcm = AESGCM(key)
    ciphertext = base64.b64decode(encrypted_base64)
    iv = base64.b64decode(iv_base64)
    tag = base64.b64decode(tag_base64)
    ciphertext_with_tag = ciphertext + tag
    plaintext_bytes = aesgcm.decrypt(iv, ciphertext_with_tag, None)
    return plaintext_bytes.decode("utf-8")


def mask_api_key(api_key: str) -> str:
    """
    生成 API Key 脱敏掩码。

    保留前 4 位和后 4 位，中间用 **** 替换。

    Args:
        api_key: 明文 API Key

    Returns:
        脱敏后的字符串，如 "sk-****3456"
    """
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}****{api_key[-4:]}"


def generate_random_secret(length: int = 32) -> str:
    """
    生成随机密钥（供设置环境变量时使用）。

    Returns:
        十六进制随机字符串
    """
    return secrets.token_hex(length)
