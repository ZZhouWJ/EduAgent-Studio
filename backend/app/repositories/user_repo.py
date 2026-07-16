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


def get_user_by_id_with_password(user_id: int) -> Optional[Dict[str, Any]]:
    """
    按 user_id 查询用户详情（含 password_hash，用于密码校验）。

    Args:
        user_id: 用户 ID

    Returns:
        用户 dict（含 password_hash）或 None
    """
    sql = """
        SELECT user_id, username, password_hash, real_name, student_no,
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
          AND r.status = 'active'
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


def count_recent_failed_login_attempts(
    username: str,
    ip_address: str,
    since: datetime,
) -> int:
    """Count credential failures for one username from one client address."""
    sql = """
        SELECT COUNT(*) AS total
        FROM login_logs
        WHERE username = %s
          AND ip_address = %s
          AND login_status = 'failed'
          AND COALESCE(failure_reason, '') <> '登录尝试过于频繁'
          AND login_time >= %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (username, ip_address, since))
        row = cursor.fetchone()
        return int((row or {}).get("total") or 0)


def count_recent_failed_login_attempts_by_ip(ip_address: str, since: datetime) -> int:
    """Count all credential failures from one client address."""
    sql = """
        SELECT COUNT(*) AS total
        FROM login_logs
        WHERE ip_address = %s
          AND login_status = 'failed'
          AND COALESCE(failure_reason, '') <> '登录尝试过于频繁'
          AND login_time >= %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (ip_address, since))
        row = cursor.fetchone()
        return int((row or {}).get("total") or 0)


def create_auth_session(
    session_id: str,
    user_id: int,
    expires_at: datetime,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Persist a revocable access-token session."""
    now = datetime.now()
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM auth_sessions WHERE expires_at <= %s", (now,))
        cursor.execute(
            """
            INSERT INTO auth_sessions
                (session_id, user_id, expires_at, ip_address, user_agent, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                session_id,
                user_id,
                expires_at,
                ip_address,
                user_agent[:500] if user_agent else None,
                now,
            ),
        )


def is_auth_session_active(session_id: str, user_id: int) -> bool:
    """Return whether a token session exists, is unexpired, and is not revoked."""
    sql = """
        SELECT 1 AS active
        FROM auth_sessions
        WHERE session_id = %s
          AND user_id = %s
          AND revoked_at IS NULL
          AND expires_at > %s
        LIMIT 1
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (session_id, user_id, datetime.now()))
        return cursor.fetchone() is not None


def revoke_auth_session(session_id: str, user_id: int, reason: str = "logout") -> int:
    """Revoke one active token session."""
    sql = """
        UPDATE auth_sessions
        SET revoked_at = %s, revoke_reason = %s
        WHERE session_id = %s AND user_id = %s AND revoked_at IS NULL
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (datetime.now(), reason, session_id, user_id))
        return cursor.rowcount


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
    status: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询用户列表（不含 password_hash）。

    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        keyword: 可选，模糊搜索 username / real_name / student_no / email
        status: 可选，按状态过滤（active/inactive/suspended）

    Returns:
        (用户列表, 总数)
    """
    offset = (page - 1) * page_size

    filters = ["is_deleted = 0"]

    if keyword:
        like_pattern = f"%{keyword}%"
        filters.append(
            "(username LIKE %s OR real_name LIKE %s OR student_no LIKE %s OR email LIKE %s)"
        )

    if status:
        filters.append("status = %s")

    where_clause = " AND ".join(filters)

    if keyword and status:
        count_sql = f"SELECT COUNT(*) AS total FROM users WHERE {where_clause}"
        data_sql = f"""
            SELECT user_id, username, real_name, student_no,
                   email, phone, status, last_login_at,
                   created_at, created_by
            FROM users
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(count_sql, (like_pattern, like_pattern, like_pattern, like_pattern, status))
            total = cursor.fetchone()["total"]
            cursor.execute(data_sql, (
                like_pattern, like_pattern, like_pattern, like_pattern, status,
                page_size, offset,
            ))
            rows = cursor.fetchall()
    elif keyword:
        count_sql = f"SELECT COUNT(*) AS total FROM users WHERE {where_clause}"
        data_sql = f"""
            SELECT user_id, username, real_name, student_no,
                   email, phone, status, last_login_at,
                   created_at, created_by
            FROM users
            WHERE {where_clause}
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
    elif status:
        count_sql = f"SELECT COUNT(*) AS total FROM users WHERE {where_clause}"
        data_sql = f"""
            SELECT user_id, username, real_name, student_no,
                   email, phone, status, last_login_at,
                   created_at, created_by
            FROM users
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(count_sql, (status,))
            total = cursor.fetchone()["total"]
            cursor.execute(data_sql, (status, page_size, offset))
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


def list_roles(include_admin: bool = True) -> List[Dict[str, Any]]:
    """
    查询所有可用角色（不含软删除）。

    Args:
        include_admin: 是否包含 admin 角色，默认 True。
    """
    if include_admin:
        where_clause = "is_deleted = 0"
    else:
        where_clause = "is_deleted = 0 AND role_code != 'admin'"
    sql = f"""
        SELECT role_id, role_name, role_code, description, status,
               created_at, updated_at
        FROM roles
        WHERE {where_clause}
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


# =============================================================================
# 用户注册与修改
# =============================================================================

def create_user(
    username: str,
    password_hash: str,
    real_name: str,
    student_no: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    created_by: Optional[int] = None,
) -> int:
    """
    创建新用户。

    Args:
        username: 用户名（唯一）
        password_hash: bcrypt 哈希后的密码
        real_name: 真实姓名
        student_no: 学号（可选）
        email: 邮箱（可选）
        phone: 手机号（可选）
        created_by: 创建人 ID（可选）

    Returns:
        新用户 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO users
            (username, password_hash, real_name, student_no, email, phone,
             status, is_deleted, created_at, updated_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, 'active', 0, %s, %s, %s)
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (
            username,
            password_hash,
            real_name,
            student_no,
            email,
            phone,
            now,
            now,
            created_by,
        ))
        return cursor.lastrowid


def create_user_with_conn(
    conn,
    username: str,
    password_hash: str,
    real_name: str,
    student_no: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    created_by: Optional[int] = None,
) -> int:
    """
    创建新用户（在外部事务中执行）。

    Args:
        conn: 外部传入的数据库连接
        username: 用户名（唯一）
        password_hash: bcrypt 哈希后的密码
        real_name: 真实姓名
        student_no: 学号（可选）
        email: 邮箱（可选）
        phone: 手机号（可选）
        created_by: 创建人 ID（可选）

    Returns:
        新用户 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO users
            (username, password_hash, real_name, student_no, email, phone,
             status, is_deleted, created_at, updated_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, 'active', 0, %s, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (
            username,
            password_hash,
            real_name,
            student_no,
            email,
            phone,
            now,
            now,
            created_by,
        ))
        return cursor.lastrowid
    finally:
        cursor.close()


def assign_default_role_with_conn(
    conn,
    user_id: int,
) -> None:
    """
    为新用户分配默认角色 student_member（在外部事务中执行）。

    Args:
        conn: 外部传入的数据库连接
        user_id: 用户 ID
    """
    sql = """
        SELECT role_id FROM roles
        WHERE role_code = 'student_member' AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            role_id = row["role_id"]
            insert_sql = """
                INSERT INTO user_roles (user_id, role_id, is_deleted, created_at)
                VALUES (%s, %s, 0, %s)
            """
            cursor.execute(insert_sql, (user_id, role_id, datetime.now()))
    finally:
        cursor.close()


def assign_roles_with_conn(
    conn,
    user_id: int,
    role_ids: Optional[list[int]] = None,
) -> None:
    """
    为新用户分配角色（在外部事务中执行）。

    若 role_ids 为 None，则分配默认角色 student_member。

    Args:
        conn: 外部传入的数据库连接
        user_id: 用户 ID
        role_ids: 角色 ID 列表（不含 admin），或 None 表示默认角色
    """
    if role_ids is None or len(role_ids) == 0:
        assign_default_role_with_conn(conn, user_id)
        return

    now = datetime.now()
    cursor = conn.cursor()
    try:
        for role_id in role_ids:
            cursor.execute(
                """
                INSERT INTO user_roles (user_id, role_id, is_deleted, created_at)
                VALUES (%s, %s, 0, %s)
                """,
                (user_id, role_id, now),
            )
    finally:
        cursor.close()


def check_username_exists(username: str) -> bool:
    """
    检查用户名是否已存在。

    Args:
        username: 用户名

    Returns:
        True 表示已存在，False 表示可用
    """
    sql = "SELECT 1 FROM users WHERE username = %s AND is_deleted = 0"
    with get_db_cursor() as cursor:
        cursor.execute(sql, (username,))
        return cursor.fetchone() is not None


def assign_default_role(user_id: int) -> None:
    """
    为新用户分配默认角色 student_member。

    Args:
        user_id: 用户 ID
    """
    sql = """
        SELECT role_id FROM roles
        WHERE role_code = 'student_member' AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            role_id = row["role_id"]
            insert_sql = """
                INSERT INTO user_roles (user_id, role_id, is_deleted, created_at)
                VALUES (%s, %s, 0, %s)
            """
            cursor.execute(insert_sql, (user_id, role_id, datetime.now()))


def update_user_status(user_id: int, status: str) -> int:
    """
    更新用户状态。

    Args:
        user_id: 用户 ID
        status: 新状态（如 'active', 'inactive', 'suspended'）

    Returns:
        affected_rows
    """
    sql = """
        UPDATE users
        SET status = %s, updated_at = %s
        WHERE user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (status, datetime.now(), user_id))
        affected = cursor.rowcount
        if affected and status == "disabled":
            cursor.execute(
                """
                UPDATE auth_sessions
                SET revoked_at = %s, revoke_reason = 'account_disabled'
                WHERE user_id = %s AND revoked_at IS NULL
                """,
                (datetime.now(), user_id),
            )
        return affected


def update_user_profile(
    user_id: int,
    real_name: str,
    student_no: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> bool:
    """
    更新用户基本信息（用户名不可修改）。

    Args:
        user_id: 用户 ID
        real_name: 真实姓名
        student_no: 学号（可选）
        email: 邮箱（可选）
        phone: 手机号（可选）

    Returns:
        True 表示更新成功，False 表示无记录被更新
    """
    sql = """
        UPDATE users
        SET real_name = %s, student_no = %s, email = %s, phone = %s, updated_at = %s
        WHERE user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (
            real_name,
            student_no,
            email,
            phone,
            datetime.now(),
            user_id,
        ))
        return cursor.rowcount > 0


def update_user_roles(user_id: int, role_ids: List[int]) -> None:
    """
    更新用户角色（先删后增）。

    Args:
        user_id: 用户 ID
        role_ids: 新的角色 ID 列表
    """
    now = datetime.now()
    with get_db_cursor() as cursor:
        cursor.execute(
            "UPDATE user_roles SET is_deleted = 1, deleted_at = %s WHERE user_id = %s",
            (now, user_id),
        )
        for role_id in role_ids:
            cursor.execute(
                """
                INSERT INTO user_roles (user_id, role_id, is_deleted, created_at)
                VALUES (%s, %s, 0, %s)
                """,
                (user_id, role_id, now),
            )


def update_password(user_id: int, new_password_hash: str) -> int:
    """
    更新用户密码。

    Args:
        user_id: 用户 ID
        new_password_hash: 新的 bcrypt 哈希密码

    Returns:
        affected_rows
    """
    sql = """
        UPDATE users
        SET password_hash = %s, updated_at = %s
        WHERE user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (new_password_hash, datetime.now(), user_id))
        affected = cursor.rowcount
        if affected:
            cursor.execute(
                """
                UPDATE auth_sessions
                SET revoked_at = %s, revoke_reason = 'password_changed'
                WHERE user_id = %s AND revoked_at IS NULL
                """,
                (datetime.now(), user_id),
            )
        return affected


# =============================================================================
# 日志查询
# =============================================================================

def list_operation_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    target_type: Optional[str] = None,
    action_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    分页查询操作日志。

    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        user_id: 按用户 ID 过滤（可选）
        target_type: 按目标类型过滤（project/task/output/review，可选）
        action_type: 按操作类型过滤（可选）
        start_date: 开始日期（YYYY-MM-DD，可选）
        end_date: 结束日期（YYYY-MM-DD，可选）

    Returns:
        {"items": [...], "total": int}
    """
    offset = (page - 1) * page_size

    filters = []
    params: list = []

    if user_id is not None:
        filters.append("o.user_id = %s")
        params.append(user_id)

    if target_type:
        filters.append("o.target_type = %s")
        params.append(target_type)

    if action_type:
        filters.append("o.action_type = %s")
        params.append(action_type)

    if start_date:
        filters.append("o.created_at >= %s")
        params.append(start_date)

    if end_date:
        filters.append("o.created_at < %s")
        params.append(f"{end_date} 23:59:59")

    where_clause = " AND ".join(filters) if filters else "1=1"

    count_sql = f"SELECT COUNT(*) AS total FROM operation_logs o WHERE {where_clause}"

    data_sql = f"""
        SELECT o.log_id, o.user_id, o.project_id, o.task_id,
               o.target_type, o.target_id, o.action_type, o.action_desc,
               o.ip_address, o.user_agent, o.created_at,
               u.username AS operator_username, u.real_name AS operator_real_name,
               GROUP_CONCAT(DISTINCT r.role_code ORDER BY r.role_code SEPARATOR ',') AS role_codes
        FROM operation_logs o
        LEFT JOIN users u ON o.user_id = u.user_id AND u.is_deleted = 0
        LEFT JOIN user_roles ur ON o.user_id = ur.user_id AND ur.is_deleted = 0
        LEFT JOIN roles r ON ur.role_id = r.role_id
            AND r.is_deleted = 0 AND r.status = 'active'
        WHERE {where_clause}
        GROUP BY o.log_id
        ORDER BY o.log_id DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return {"items": rows, "total": total}


def list_login_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    login_status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    分页查询登录日志。

    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        user_id: 按用户 ID 过滤（可选）
        login_status: 按登录状态过滤（success/failed，可选）
        start_date: 开始日期（YYYY-MM-DD，可选）
        end_date: 结束日期（YYYY-MM-DD，可选）

    Returns:
        {"items": [...], "total": int}
    """
    offset = (page - 1) * page_size

    filters = []
    params: list = []

    if user_id is not None:
        filters.append("l.user_id = %s")
        params.append(user_id)

    if login_status:
        filters.append("l.login_status = %s")
        params.append(login_status)

    if start_date:
        filters.append("l.login_time >= %s")
        params.append(start_date)

    if end_date:
        filters.append("l.login_time < %s")
        params.append(f"{end_date} 23:59:59")

    where_clause = " AND ".join(filters) if filters else "1=1"

    count_sql = f"SELECT COUNT(*) AS total FROM login_logs l WHERE {where_clause}"

    data_sql = f"""
        SELECT l.login_id, l.user_id, l.username, l.login_status,
               l.failure_reason, l.ip_address, l.user_agent, l.login_time,
               u.real_name AS real_name,
               GROUP_CONCAT(DISTINCT r.role_code ORDER BY r.role_code SEPARATOR ',') AS role_codes
        FROM login_logs l
        LEFT JOIN users u ON l.user_id = u.user_id AND u.is_deleted = 0
        LEFT JOIN user_roles ur ON l.user_id = ur.user_id AND ur.is_deleted = 0
        LEFT JOIN roles r ON ur.role_id = r.role_id
            AND r.is_deleted = 0 AND r.status = 'active'
        WHERE {where_clause}
        GROUP BY l.login_id
        ORDER BY l.login_id DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return {"items": rows, "total": total}
