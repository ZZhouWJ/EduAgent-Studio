"""
加密工具模块。

提供 API Key 的 AES-256-GCM 加密解密功能。
加密主密钥从环境变量 API_KEY_SECRET 读取，不硬编码。

AES-GCM 为带认证的加密模式，同时保证机密性和完整性。
"""

import os
import secrets
from typing import Tuple

from cryptography.hazmat.backends import default_backend
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
            f"请在 .env 文件中设置 API_KEY_SECRET=<32字节十六进制字符串或随机密钥>"
        )
    secret_bytes = secret.encode("utf-8")
    if len(secret_bytes) < 16:
        raise RuntimeError(
            f"环境变量 {_SECRET_ENV_VAR} 太短（至少需要 32 字符）。"
            f"请使用随机密钥，例如：openssl rand -hex 32"
        )
    key = secret_bytes[:32] if len(secret_bytes) >= 32 else secret_bytes.ljust(32, b'\0')
    return key


def encrypt_api_key(plaintext: str) -> Tuple[bytes, bytes, bytes, int]:
    """
    使用 AES-256-GCM 加密 API Key。

    Args:
        plaintext: 明文 API Key

    Returns:
        (encrypted_data, iv, tag, key_version)
        - encrypted_data: 密文（bytes）
        - iv: 初始化向量（12 字节随机值）
        - tag: 认证标签（16 字节）
        - key_version: 密钥版本号（当前固定为 1）
    """
    key = _get_master_key()
    aesgcm = AESGCM(key)
    iv = secrets.token_bytes(12)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
    encrypted_data = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    return encrypted_data, iv, tag, _KEY_VERSION


def decrypt_api_key(encrypted_data: bytes, iv: bytes, tag: bytes) -> str:
    """
    解密 API Key。

    Args:
        encrypted_data: 密文
        iv: 初始化向量
        tag: 认证标签

    Returns:
        明文 API Key
    """
    key = _get_master_key()
    aesgcm = AESGCM(key)
    ciphertext_with_tag = encrypted_data + tag
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
