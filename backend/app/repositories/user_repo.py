"""
用户 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
不返回 password_hash。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db_cursor


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    按用户名查询用户（包含 password_hash 用于登录校验）。

    Args:
        username: 用户名

    Returns:
        用户 dict 或 None
    """
    sql = """
        SELECT user_id, username, password_hash, real_name, student_no,
               email, phone, status, last_login_at,
               created_at, created_by, updated_at, updated_by
        FROM users
        WHERE username = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (username,))
        return cursor.fetchone()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    按 user_id 查询用户详情（不含 password_hash）。

    Args:
        user_id: 用户 ID

    Returns:
        用户 dict 或 None
    """
    sql = """
        SELECT user_id, username, real_name, student_no,
               email, phone, status, last_login_at,
               created_at, created_by, updated_at, updated_by
        FROM users
        WHERE user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()


def update_user_last_login(user_id: int) -> None:
    """更新用户最后登录时间。"""
    sql = "UPDATE users SET last_login_at = %s WHERE user_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(sql, (datetime.now(), user_id))
        cursor.fetchone()


def get_user_roles(user_id: int) -> List[str]:
    """
    获取用户角色代码列表。

    Args:
        user_id: 用户 ID

    Returns:
        role_code 列表，如 ['admin'] 或 ['student_member', 'project_leader']
    """
    sql = """
        SELECT r.role_code
        FROM roles r
        INNER JOIN user_roles ur ON r.role_id = ur.role_id
        WHERE ur.user_id = %s
          AND r.is_deleted = 0
          AND ur.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return [row["role_code"] for row in rows]


def get_user_permissions(user_id: int) -> List[str]:
    """
    获取用户权限代码列表。

    Args:
        user_id: 用户 ID

    Returns:
        permission_code 列表，如 ['project:view', 'user:manage']
    """
    sql = """
        SELECT DISTINCT p.permission_code
        FROM permissions p
        INNER JOIN role_permissions rp ON p.permission_id = rp.permission_id
        INNER JOIN user_roles ur ON rp.role_id = ur.role_id
        WHERE ur.user_id = %s
          AND p.is_deleted = 0
          AND rp.is_deleted = 0
          AND ur.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return [row["permission_code"] for row in rows]


def is_admin(user_id: int) -> bool:
    """判断用户是否为管理员。"""
    roles = get_user_roles(user_id)
    return "admin" in roles


def insert_login_log(
    user_id: Optional[int],
    username: str,
    login_status: str,
    failure_reason: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    写入登录日志。

    Args:
        user_id: 登录用户 ID（失败时可能为 None）
        username: 登录用户名
        login_status: 'success' 或 'failed'
        failure_reason: 失败原因
        ip_address: 客户端 IP
        user_agent: 客户端 UA
    """
    sql = """
        INSERT INTO login_logs
            (user_id, username, login_status, failure_reason, ip_address, user_agent, login_time)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (
            user_id,
            username,
            login_status,
            failure_reason,
            ip_address,
            user_agent,
            datetime.now(),
        ))


def insert_operation_log(
    user_id: int,
    action_type: str,
    action_desc: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    写入操作日志（独立事务）。

    Args:
        user_id: 操作人
        action_type: 操作类型，如 'login', 'logout', 'user:create'
        action_desc: 操作描述
        target_type: 目标资源类型
        target_id: 目标资源 ID
        project_id: 关联项目 ID
        task_id: 关联任务 ID
        ip_address: 客户端 IP
        user_agent: 客户端 UA
    """
    sql = """
        INSERT INTO operation_logs
            (user_id, project_id, task_id, target_type, target_id,
             action_type, action_desc, ip_address, user_agent, created_at)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (
            user_id,
            project_id,
            task_id,
            target_type,
            target_id,
            action_type,
            action_desc,
            ip_address,
            user_agent,
            datetime.now(),
        ))


def insert_operation_log_with_conn(
    user_id: int,
    action_type: str,
    action_desc: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    conn=None,
) -> None:
    """
    写入操作日志（支持外部传入事务连接）。

    用于与业务操作在同一事务内写入日志。

    Args:
        conn: 外部传入的数据库连接（pymysql Connection）
              若为 None，则内部创建独立事务
    """
    sql = """
        INSERT INTO operation_logs
            (user_id, project_id, task_id, target_type, target_id,
             action_type, action_desc, ip_address, user_agent, created_at)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        user_id,
        project_id,
        task_id,
        target_type,
        target_id,
        action_type,
        action_desc,
        ip_address,
        user_agent,
        datetime.now(),
    )

    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)


def list_users(
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询用户列表（不含 password_hash）。

    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        keyword: 可选，模糊搜索 username / real_name / student_no / email

    Returns:
        (用户列表, 总数)
    """
    offset = (page - 1) * page_size

    if keyword:
        like_pattern = f"%{keyword}%"
        count_sql = """
            SELECT COUNT(*) AS total
            FROM users
            WHERE is_deleted = 0
              AND (username LIKE %s OR real_name LIKE %s
                   OR student_no LIKE %s OR email LIKE %s)
        """
        data_sql = """
            SELECT user_id, username, real_name, student_no,
                   email, phone, status, last_login_at,
                   created_at, created_by
            FROM users
            WHERE is_deleted = 0
              AND (username LIKE %s OR real_name LIKE %s
                   OR student_no LIKE %s OR email LIKE %s)
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(count_sql, (like_pattern, like_pattern, like_pattern, like_pattern))
            total = cursor.fetchone()["total"]
            cursor.execute(data_sql, (
                like_pattern, like_pattern, like_pattern, like_pattern,
                page_size, offset,
            ))
            rows = cursor.fetchall()
    else:
        count_sql = "SELECT COUNT(*) AS total FROM users WHERE is_deleted = 0"
        data_sql = """
            SELECT user_id, username, real_name, student_no,
                   email, phone, status, last_login_at,
                   created_at, created_by
            FROM users
            WHERE is_deleted = 0
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(count_sql)
            total = cursor.fetchone()["total"]
            cursor.execute(data_sql, (page_size, offset))
            rows = cursor.fetchall()

    return rows, total


def list_roles() -> List[Dict[str, Any]]:
    """
    查询所有可用角色（不含软删除）。

    Returns:
        角色列表
    """
    sql = """
        SELECT role_id, role_name, role_code, description, status,
               created_at, updated_at
        FROM roles
        WHERE is_deleted = 0
        ORDER BY created_at ASC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def list_permissions() -> List[Dict[str, Any]]:
    """
    查询所有可用权限（不含软删除）。

    Returns:
        权限列表
    """
    sql = """
        SELECT permission_id, permission_name, permission_code,
               module_name, description, created_at, updated_at
        FROM permissions
        WHERE is_deleted = 0
        ORDER BY module_name ASC, permission_code ASC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()
