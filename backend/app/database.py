"""
数据库连接管理模块。

使用 PyMySQL 连接 MySQL 8.0，不使用 ORM。
配置从环境变量读取，不硬编码密码。
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

import pymysql
from pymysql.cursors import DictCursor

from app.config import get_settings

logger = logging.getLogger(__name__)

_connection_params: Optional[Dict[str, Any]] = None


def _get_connection_params() -> Dict[str, Any]:
    """延迟获取连接参数（仅在首次调用时从配置读取）。"""
    global _connection_params
    if _connection_params is None:
        settings = get_settings()
        _connection_params = settings.db_url
    return _connection_params


def get_connection():
    """
    获取一个新的数据库连接。

    调用方负责在使用完毕后调用 connection.close() 释放连接。
    推荐配合 with 或 contextmanager 使用。

    Returns:
        pymysql.connections.Connection

    Raises:
        pymysql.Error: 连接失败时抛出
    """
    params = _get_connection_params()
    params["charset"] = "utf8mb4"
    return pymysql.connect(**params, cursorclass=DictCursor, autocommit=False)


@contextmanager
def get_db_cursor() -> Generator[DictCursor, None, None]:
    """
    上下文管理器：自动获取连接、创建字典游标、执行后提交或回滚。

    用法示例：
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 AS result")
            row = cursor.fetchone()

    Yields:
        pymysql.cursors.DictCursor
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(DictCursor)
        yield cursor
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            cursor.close()
            conn.close()


@contextmanager
def get_db_transaction():
    """
    显式事务上下文管理器。

    调用方获取连接后手动控制 commit / rollback。
    适合需要在一个事务内执行多条 SQL（含日志写入）的场景。

    用法示例：
        with get_db_transaction() as conn:
            cursor = conn.cursor(DictCursor)
            cursor.execute("INSERT ...", (...))
            cursor.execute("INSERT INTO operation_logs ...", (...))
            conn.commit()
        # 或异常时自动 rollback

    Yields:
        pymysql.connections.Connection
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()   # 正常结束时提交事务
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


def test_connection() -> Dict[str, Any]:
    """
    轻量级数据库健康检查。

    执行 SELECT 1，验证数据库是否可达。

    Returns:
        dict: {
            "connected": True/False,
            "message": str,
            "server_version": str or None
        }
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS health_check")
                cursor.fetchone()
            return {
                "connected": True,
                "message": "数据库连接正常",
                "server_version": conn.server_version or None,
            }
        finally:
            conn.close()
    except pymysql.Error as e:
        logger.warning("数据库连接测试失败: %s", e)
        return {
            "connected": False,
            "message": f"数据库连接失败: {e.args[1] if len(e.args) > 1 else str(e)}",
            "server_version": None,
        }
    except Exception as e:
        logger.warning("数据库连接测试异常: %s", e)
        return {
            "connected": False,
            "message": f"数据库连接异常: {str(e)}",
            "server_version": None,
        }
