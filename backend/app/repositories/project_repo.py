"""
项目 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
不返回 password_hash。
软删除为主，不物理删除。

事务说明：
- 纯查询函数使用 get_db_cursor()（自动提交）
- 写操作函数支持可选 conn 参数，由 service 层传入显式事务连接，
  以保证业务 SQL 和 operation_logs 在同一事务中。
- 若 conn=None，则函数内部创建独立事务（向后兼容）
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pymysql
from pymysql.connections import Connection

from app.database import get_connection, get_db_cursor

# =============================================================================
# 项目基础查询（不使用事务，自动提交）
# =============================================================================

def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """按 project_id 查询项目详情（不含软删除）。"""
    sql = """
        SELECT p.project_id, p.project_name, p.project_type, p.description,
               p.owner_id, p.status,
               p.created_at, p.created_by, p.updated_at, p.updated_by,
               u.username AS owner_username, u.real_name AS owner_real_name
        FROM projects p
        LEFT JOIN users u ON p.owner_id = u.user_id AND u.is_deleted = 0
        WHERE p.project_id = %s AND p.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id,))
        return cursor.fetchone()


def list_projects_for_user(
    user_id: int,
    is_admin: bool,
    is_teacher: bool,
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """按用户权限分页查询项目列表。"""
    offset = (page - 1) * page_size

    base_where = "p.is_deleted = 0"

    if keyword:
        like = f"%{keyword}%"
        keyword_filter = " AND (p.project_name LIKE %s OR p.description LIKE %s)"
    else:
        like = None
        keyword_filter = ""

    if status:
        status_filter = " AND p.status = %s"
    else:
        status_filter = ""

    if is_admin:
        where_clause = base_where + keyword_filter + status_filter
        params = ([like, like, status] if keyword and status else
                  [like, like] if keyword else
                  [status] if status else [])

    elif is_teacher:
        where_clause = (
            base_where + keyword_filter + status_filter +
            " AND p.project_id IN ("
            "  SELECT pm.project_id FROM project_members pm"
            "  WHERE pm.is_deleted = 0"
            "    AND pm.user_id = %s"
            "    AND pm.project_role = 'teacher'"
            ")"
        )
        params = ([like, like, status, user_id] if keyword and status else
                  [like, like, user_id] if keyword else
                  [status, user_id] if status else
                  [user_id])

    else:
        where_clause = (
            base_where + keyword_filter + status_filter +
            " AND p.project_id IN ("
            "  SELECT project_id FROM project_members"
            "  WHERE is_deleted = 0 AND user_id = %s"
            ")"
        )
        params = ([like, like, status, user_id] if keyword and status else
                  [like, like, user_id] if keyword else
                  [status, user_id] if status else
                  [user_id])

    count_sql = f"SELECT COUNT(*) AS total FROM projects p WHERE {where_clause}"

    data_sql = f"""
        SELECT p.project_id, p.project_name, p.project_type, p.description,
               p.owner_id, p.status,
               p.created_at, p.created_by,
               u.username AS owner_username, u.real_name AS owner_real_name
        FROM projects p
        LEFT JOIN users u ON p.owner_id = u.user_id AND u.is_deleted = 0
        WHERE {where_clause}
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# 项目创建（内部独立事务，或由 service 层传入 conn）
# =============================================================================

def create_project(
    project_name: str,
    project_type: str,
    description: Optional[str],
    owner_id: int,
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建项目并在同一事务中将创建人写入 project_members。

    Args:
        conn: 可选，外部传入的数据库连接（用于显式事务）
              若为 None，则内部创建独立事务

    Returns:
        新项目 ID
    """
    now = datetime.now()
    internal_conn = False

    if conn is None:
        conn = get_connection()
        internal_conn = True
        conn.autocommit(False)

    cursor = None
    try:
        cursor = conn.cursor()

        # 1. 插入项目
        cursor.execute(
            """
            INSERT INTO projects
                (project_name, project_type, description, owner_id,
                 status, is_deleted, created_at, created_by)
            VALUES
                (%s, %s, %s, %s, 'active', 0, %s, %s)
            """,
            (project_name, project_type, description, owner_id, now, created_by),
        )
        project_id = cursor.lastrowid

        # 2. 将创建人写入项目成员
        cursor.execute(
            """
            INSERT INTO project_members
                (project_id, user_id, project_role, joined_at,
                 status, is_deleted, created_at, created_by)
            VALUES
                (%s, %s, 'leader', %s, 'active', 0, %s, %s)
            """,
            (project_id, owner_id, now, now, created_by),
        )

        if internal_conn:
            conn.commit()

        return project_id

    except Exception:
        if internal_conn and conn is not None:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if internal_conn and conn is not None:
            conn.close()


# =============================================================================
# 项目更新
# =============================================================================

def update_project(
    project_id: int,
    project_name: Optional[str] = None,
    project_type: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    updated_by: Optional[int] = None,
    conn: Optional[Connection] = None,
) -> int:
    """
    更新项目字段。

    Returns:
        affected_rows（0 表示未更新，可能是项目不存在或无权）
    """
    fields = []
    params: list = []

    if project_name is not None:
        fields.append("project_name = %s")
        params.append(project_name)
    if project_type is not None:
        fields.append("project_type = %s")
        params.append(project_type)
    if description is not None:
        fields.append("description = %s")
        params.append(description)
    if status is not None:
        fields.append("status = %s")
        params.append(status)

    if not fields:
        return 0

    fields.append("updated_at = %s")
    params.append(datetime.now())

    if updated_by is not None:
        fields.append("updated_by = %s")
        params.append(updated_by)

    params.append(project_id)

    sql = (
        f"UPDATE projects SET {', '.join(fields)} "
        f"WHERE project_id = %s AND is_deleted = 0"
    )

    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount


# =============================================================================
# 项目软删除
# =============================================================================

def soft_delete_project(
    project_id: int,
    deleted_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    软删除项目。

    Returns:
        affected_rows
    """
    sql = """
        UPDATE projects
        SET is_deleted = 1,
            deleted_at = %s,
            deleted_by = %s
        WHERE project_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (datetime.now(), deleted_by, project_id))
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (datetime.now(), deleted_by, project_id))
            return cursor.rowcount


# =============================================================================
# 项目归档（优先调用存储过程）
# =============================================================================

def archive_project_with_procedure(
    project_id: int,
    operator_id: int,
    conn: Optional[Connection] = None,
) -> Tuple[int, str]:
    """
    优先调用存储过程 sp_archive_project 归档项目。

    PyMySQL OUT 参数读取方式：
      1. 先用 SET 初始化会话变量
      2. 用 cursor.execute() 调用存储过程（不用 callproc）
      3. 再用 SELECT 读取会话变量

    会话变量方式可以正确读取 OUT 参数，而 cursor.callproc() + fetchall()
    在存储过程无 SELECT 结果集时无法读取。

    存储过程 sp_archive_project 签名（来自 database/06_create_stored_procedures.sql）：
      IN  p_project_id       INT UNSIGNED
      IN  p_operator_id      INT UNSIGNED
      OUT p_result_code      INT
      OUT p_result_message   VARCHAR(255)

    Returns:
        (result_code, result_message)
        - result_code=0: 成功
        - result_code=404: 项目不存在
        - result_code=500: 归档失败
    """
    internal_conn = False

    if conn is None:
        conn = get_connection()
        internal_conn = True
        conn.autocommit(False)

    cursor = None
    try:
        cursor = conn.cursor()

        # 步骤1：初始化会话变量（OUT 参数接收器）
        cursor.execute("SET @p_result_code = 0, @p_result_msg = ''")

        # 步骤2：调用存储过程，会话变量在过程内部被 SET 赋值
        # 注意：不能用 cursor.callproc()，因为 callproc 不支持 OUT 参数读取
        cursor.execute(
            "CALL sp_archive_project(%s, %s, @p_result_code, @p_result_msg)",
            (project_id, operator_id),
        )

        # 步骤3：读取会话变量（OUT 参数值）
        cursor.execute("SELECT @p_result_code AS result_code, @p_result_msg AS result_message")
        row = cursor.fetchone()

        if row is None:
            # 会话变量查询返回空，说明无法确认归档结果，视为失败
            if internal_conn:
                conn.commit()
            return 500, "归档结果未知（无法读取存储过程返回码）"

        result_code = int(row["result_code"])
        result_message = str(row["result_message"])

        if internal_conn:
            conn.commit()

        return result_code, result_message

    except Exception:
        if internal_conn and conn is not None:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if internal_conn and conn is not None:
            conn.close()


def archive_project_fallback(
    project_id: int,
    operator_id: int,
    conn: Optional[Connection] = None,
) -> Tuple[int, str]:
    """
    纯 SQL 模拟归档行为（当存储过程不可用时的回退方案）。

    在同一事务中：
    1. 检查项目是否存在
    2. 更新 projects.status = 'archived'
    3. 更新 project_tasks.status = 'archived'
    4. 更新 task_branches.status = 'closed'
    5. 写入 operation_logs

    Returns:
        (result_code, result_message)
    """
    internal_conn = False

    if conn is None:
        conn = get_connection()
        internal_conn = True
        conn.autocommit(False)

    cursor = None
    try:
        cursor = conn.cursor()

        now = datetime.now()

        cursor.execute(
            "SELECT project_name FROM projects WHERE project_id = %s AND is_deleted = 0 FOR UPDATE",
            (project_id,),
        )
        row = cursor.fetchone()
        if not row:
            # 项目不存在，回滚事务，不算作成功
            if internal_conn:
                conn.rollback()
            return 404, "项目不存在"

        project_name = row["project_name"]

        cursor.execute(
            """
            UPDATE projects
            SET status = 'archived', updated_at = %s, updated_by = %s
            WHERE project_id = %s AND is_deleted = 0
            """,
            (now, operator_id, project_id),
        )

        cursor.execute(
            """
            UPDATE project_tasks
            SET status = 'archived', updated_at = %s, updated_by = %s
            WHERE project_id = %s AND is_deleted = 0
            """,
            (now, operator_id, project_id),
        )

        cursor.execute(
            """
            UPDATE task_branches
            SET status = 'closed', updated_at = %s, updated_by = %s
            WHERE project_id = %s AND is_deleted = 0
            """,
            (now, operator_id, project_id),
        )

        cursor.execute(
            """
            INSERT INTO operation_logs
                (user_id, project_id, target_type, target_id,
                 action_type, action_desc, old_value, new_value, created_at)
            VALUES
                (%s, %s, 'projects', %s, 'project_archive',
                 %s,
                 '{"status":"active"}',
                 '{"status":"archived","archived_tasks":0,"archived_branches":0}',
                 %s)
            """,
            (
                operator_id, project_id, project_id,
                f"项目归档：{project_name}",
                now,
            ),
        )

        if internal_conn:
            conn.commit()

        return 0, f"项目归档成功"

    except Exception:
        if internal_conn and conn is not None:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if internal_conn and conn is not None:
            conn.close()


# =============================================================================
# 项目成员查询（不使用事务）
# =============================================================================

def list_project_members(project_id: int) -> List[Dict[str, Any]]:
    """查询项目成员列表（不含软删除，不含 password_hash）。"""
    sql = """
        SELECT pm.member_id, pm.project_id, pm.user_id, pm.project_role,
               pm.joined_at, pm.status,
               u.username, u.real_name, u.email, u.phone,
               pm.created_at, pm.created_by
        FROM project_members pm
        INNER JOIN users u ON pm.user_id = u.user_id AND u.is_deleted = 0
        WHERE pm.project_id = %s AND pm.is_deleted = 0
        ORDER BY pm.joined_at ASC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id,))
        return cursor.fetchall()


def get_project_member(project_id: int, member_id: int) -> Optional[Dict[str, Any]]:
    """按 member_id 查询单个项目成员。"""
    sql = """
        SELECT pm.member_id, pm.project_id, pm.user_id, pm.project_role,
               pm.joined_at, pm.status,
               u.username, u.real_name,
               pm.created_at, pm.created_by
        FROM project_members pm
        INNER JOIN users u ON pm.user_id = u.user_id AND u.is_deleted = 0
        WHERE pm.member_id = %s AND pm.project_id = %s AND pm.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (member_id, project_id))
        return cursor.fetchone()


def get_project_member_by_user(
    project_id: int, user_id: int,
) -> Optional[Dict[str, Any]]:
    """按 (project_id, user_id) 查询项目成员。"""
    sql = """
        SELECT pm.member_id, pm.project_id, pm.user_id, pm.project_role,
               pm.joined_at, pm.status
        FROM project_members pm
        WHERE pm.project_id = %s AND pm.user_id = %s AND pm.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone()


def is_user_project_owner(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目 owner。"""
    sql = """
        SELECT 1 FROM projects
        WHERE project_id = %s AND owner_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_project_leader(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目 leader。"""
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s
          AND project_role IN ('leader')
          AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_project_teacher(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目内 teacher。"""
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s
          AND project_role = 'teacher'
          AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_project_reviewer(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目内 reviewer。"""
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s
          AND project_role = 'reviewer'
          AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_in_project(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目成员。"""
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


# =============================================================================
# 项目成员写操作
# =============================================================================

def add_project_member(
    project_id: int,
    user_id: int,
    project_role: str,
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    添加项目成员。

    Returns:
        新增 member_id
    """
    now = datetime.now()
    sql = """
        INSERT INTO project_members
            (project_id, user_id, project_role, joined_at,
             status, is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, 'active', 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (project_id, user_id, project_role, now, now, created_by))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (project_id, user_id, project_role, now, now, created_by))
            return cursor.lastrowid


def update_project_member_role(
    member_id: int,
    project_role: str,
    updated_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    修改项目成员角色。

    Returns:
        affected_rows
    """
    sql = """
        UPDATE project_members
        SET project_role = %s,
            updated_at = %s,
            updated_by = %s
        WHERE member_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (project_role, datetime.now(), updated_by, member_id))
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (project_role, datetime.now(), updated_by, member_id))
            return cursor.rowcount


def soft_delete_project_member(
    member_id: int,
    deleted_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    软删除项目成员（移除成员）。

    Returns:
        affected_rows
    """
    sql = """
        UPDATE project_members
        SET is_deleted = 1,
            deleted_at = %s,
            deleted_by = %s
        WHERE member_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (datetime.now(), deleted_by, member_id))
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (datetime.now(), deleted_by, member_id))
            return cursor.rowcount
