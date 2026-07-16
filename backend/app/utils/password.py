"""
密码哈希工具。

使用 bcrypt 对密码进行哈希和校验，不允许明文比对。
"""

import bcrypt


MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_BYTES = 72


def get_password_policy_error(plain_password: str) -> str | None:
    """Return a user-facing validation error when a new password is unsafe."""
    if len(plain_password) < MIN_PASSWORD_LENGTH:
        return f"密码至少需要 {MIN_PASSWORD_LENGTH} 个字符"
    if len(plain_password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return "密码过长，请缩短后重试（中文字符可能占用多个字节）"
    return None


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行哈希。

    Args:
        plain_password: 用户输入的明文密码

    Returns:
        bcrypt 哈希后的密码字符串
    """
    policy_error = get_password_policy_error(plain_password)
    if policy_error:
        raise ValueError(policy_error)
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码与哈希值是否匹配。

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的 bcrypt 哈希值

    Returns:
        匹配返回 True，否则返回 False
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False
