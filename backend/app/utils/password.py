"""
密码哈希工具。

使用 bcrypt 对密码进行哈希和校验，不允许明文比对。
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行哈希。

    Args:
        plain_password: 用户输入的明文密码

    Returns:
        bcrypt 哈希后的密码字符串
    """
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
