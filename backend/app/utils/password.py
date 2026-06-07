"""
密码哈希工具。

使用 bcrypt 对密码进行哈希和校验，不允许明文比对。
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行哈希。

    Args:
        plain_password: 用户输入的明文密码

    Returns:
        bcrypt 哈希后的密码字符串
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码与哈希值是否匹配。

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的 bcrypt 哈希值

    Returns:
        匹配返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)
