"""
任务 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
不返回 password_hash。
软删除为主，不物理删除。

事务说明：
- 纯查询函数使用 get_db_cursor()（自动提交）
- 写操作函数支持可选 conn 参数，由 service 层传入显式事务连接
- repository 方法不擅自 commit
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pymysql.connections import Connection

from app.database import get_connection, get_db_cursor

VALID_TASK_STATUS = {"draft", "running", "generated", "submitted",
                     "approved", "rejected", "revision_required",
                     "adopted", "archived", "conflict_pending"}
VALID_BRANCH_STATUS = {"active", "merged", "closed", "conflict_pending"}
VALID_SOURCE_TYPE = {"ai_generated", "manual_edit", "hybrid", "manual_merge"}


# =============================================================================
# 任务基础查询
# =============================================================================

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """
    按 task_id 查询任务详情。

    Returns:
        任务 dict（含 project_name、creator_username、assignee_username）或 None
    """
    sql = """
        SELECT t.task_id, t.project_id, t.task_type_id, t.title, t.description,
               t.creator_id, t.assignee_id, t.status, t.priority, t.due_date,
               t.created_at, t.created_by, t.updated_at, t.updated_by,
               p.project_name,
               c.username AS creator_username, c.real_name AS creator_real_name,
               a.username AS assignee_username, a.real_name AS assignee_real_name,
               tt.type_name, tt.type_code
        FROM project_tasks t
        INNER JOIN projects p ON t.project_id = p.project_id AND p.is_deleted = 0
        LEFT JOIN users c ON t.creator_id = c.user_id AND c.is_deleted = 0
        LEFT JOIN users a ON t.assignee_id = a.user_id AND a.is_deleted = 0
        LEFT JOIN task_types tt ON t.task_type_id = tt.task_type_id AND tt.is_deleted = 0
        WHERE t.task_id = %s AND t.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (task_id,))
        return cursor.fetchone()


def list_tasks_for_project(
    project_id: int,
    is_admin: bool,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询项目任务列表。

    Args:
        project_id: 项目 ID
        is_admin: 是否为管理员
        page: 页码
        page_size: 每页条数
        status: 状态过滤
        keyword: 搜索关键字

    Returns:
        (任务列表, 总数)
    """
    offset = (page - 1) * page_size

    base_where = "t.project_id = %s AND t.is_deleted = 0"

    if keyword:
        like = f"%{keyword}%"
        keyword_filter = " AND (t.title LIKE %s OR t.description LIKE %s)"
    else:
        like = None
        keyword_filter = ""

    if status:
        status_filter = " AND t.status = %s"
    else:
        status_filter = ""

    where_clause = base_where + keyword_filter + status_filter
    params = ([project_id, like, like, status] if keyword and status else
              [project_id, like, like] if keyword else
              [project_id, status] if status else
              [project_id])

    count_sql = f"SELECT COUNT(*) AS total FROM project_tasks t WHERE {where_clause}"

    data_sql = f"""
        SELECT t.task_id, t.project_id, t.task_type_id, t.title, t.description,
               t.creator_id, t.assignee_id, t.status, t.priority, t.due_date,
               t.created_at, t.created_by,
               c.username AS creator_username, c.real_name AS creator_real_name,
               a.username AS assignee_username, a.real_name AS assignee_real_name,
               tt.type_name
        FROM project_tasks t
        LEFT JOIN users c ON t.creator_id = c.user_id AND c.is_deleted = 0
        LEFT JOIN users a ON t.assignee_id = a.user_id AND a.is_deleted = 0
        LEFT JOIN task_types tt ON t.task_type_id = tt.task_type_id AND tt.is_deleted = 0
        WHERE {where_clause}
        ORDER BY t.created_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# 任务写操作
# =============================================================================

def create_task(
    project_id: int,
    task_type_id: int,
    title: str,
    description: Optional[str],
    creator_id: int,
    assignee_id: Optional[int],
    priority: Optional[str],
    due_date: Optional[str],
    conn: Optional[Connection] = None,
) -> int:
    """创建任务。Returns: 新任务 ID"""
    now = datetime.now()
    sql = """
        INSERT INTO project_tasks
            (project_id, task_type_id, title, description, creator_id,
             assignee_id, status, priority, due_date,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, 'draft', %s, %s, 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                project_id, task_type_id, title, description, creator_id,
                assignee_id, priority, due_date, now, creator_id,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                project_id, task_type_id, title, description, creator_id,
                assignee_id, priority, due_date, now, creator_id,
            ))
            return cursor.lastrowid


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    updated_by: Optional[int] = None,
    conn: Optional[Connection] = None,
) -> int:
    """更新任务字段（仅更新非 None 的字段）。Returns: affected_rows"""
    fields = []
    params: list = []

    if title is not None:
        fields.append("title = %s")
        params.append(title)
    if description is not None:
        fields.append("description = %s")
        params.append(description)
    if assignee_id is not None:
        fields.append("assignee_id = %s")
        params.append(assignee_id)
    if status is not None:
        fields.append("status = %s")
        params.append(status)
    if priority is not None:
        fields.append("priority = %s")
        params.append(priority)
    if due_date is not None:
        fields.append("due_date = %s")
        params.append(due_date)

    if not fields:
        return 0

    fields.append("updated_at = %s")
    params.append(datetime.now())

    if updated_by is not None:
        fields.append("updated_by = %s")
        params.append(updated_by)

    params.append(task_id)

    sql = (
        f"UPDATE project_tasks SET {', '.join(fields)} "
        f"WHERE task_id = %s AND is_deleted = 0"
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


def soft_delete_task(
    task_id: int,
    deleted_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """软删除任务。Returns: affected_rows"""
    sql = """
        UPDATE project_tasks
        SET is_deleted = 1,
            deleted_at = %s,
            deleted_by = %s
        WHERE task_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (datetime.now(), deleted_by, task_id))
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (datetime.now(), deleted_by, task_id))
            return cursor.rowcount


# =============================================================================
# 任务分支查询
# =============================================================================

def list_task_branches(task_id: int) -> List[Dict[str, Any]]:
    """查询任务分支列表（不含软删除）。"""
    sql = """
        SELECT b.branch_id, b.project_id, b.task_id, b.branch_name,
               b.base_output_id, b.created_by, b.status,
               b.created_at, b.updated_at,
               c.username AS creator_username, c.real_name AS creator_real_name,
               o.output_title AS base_output_title
        FROM task_branches b
        LEFT JOIN users c ON b.created_by = c.user_id AND c.is_deleted = 0
        LEFT JOIN task_outputs o ON b.base_output_id = o.output_id AND o.is_deleted = 0
        WHERE b.task_id = %s AND b.is_deleted = 0
        ORDER BY b.created_at ASC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (task_id,))
        return cursor.fetchall()


def get_branch_by_id(branch_id: int) -> Optional[Dict[str, Any]]:
    """按 branch_id 查询分支。"""
    sql = """
        SELECT branch_id, project_id, task_id, branch_name,
               base_output_id, created_by, status,
               created_at, updated_at
        FROM task_branches
        WHERE branch_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (branch_id,))
        return cursor.fetchone()


def is_branch_name_exists_in_task(task_id: int, branch_name: str) -> bool:
    """检查同一任务下分支名是否已存在。"""
    sql = """
        SELECT 1 FROM task_branches
        WHERE task_id = %s AND branch_name = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (task_id, branch_name))
        return cursor.fetchone() is not None


# =============================================================================
# 任务分支写操作
# =============================================================================

def create_task_branch(
    task_id: int,
    project_id: int,
    branch_name: str,
    base_output_id: Optional[int],
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """创建任务分支。Returns: 新分支 ID"""
    now = datetime.now()
    sql = """
        INSERT INTO task_branches
            (project_id, task_id, branch_name, base_output_id, created_by,
             status, is_deleted, created_at)
        VALUES
            (%s, %s, %s, %s, %s, 'active', 0, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (project_id, task_id, branch_name, base_output_id, created_by, now))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (project_id, task_id, branch_name, base_output_id, created_by, now))
            return cursor.lastrowid


# =============================================================================
# 输出版本查询
# =============================================================================

def list_task_outputs(task_id: int) -> List[Dict[str, Any]]:
    """查询任务输出版本列表（不含软删除，不返回完整 content）。"""
    sql = """
        SELECT o.output_id, o.task_id, o.branch_id, o.invocation_id,
               o.version_no, o.output_title, o.source_type,
               o.parent_output_id, o.is_final_candidate, o.status,
               o.created_by, o.created_at, o.last_modified_at,
               b.branch_name,
               c.username AS creator_username, c.real_name AS creator_real_name
        FROM task_outputs o
        LEFT JOIN task_branches b ON o.branch_id = b.branch_id AND b.is_deleted = 0
        LEFT JOIN users c ON o.created_by = c.user_id AND c.is_deleted = 0
        WHERE o.task_id = %s AND o.is_deleted = 0
        ORDER BY o.version_no ASC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (task_id,))
        return cursor.fetchall()


def get_output_by_id(output_id: int) -> Optional[Dict[str, Any]]:
    """
    按 output_id 查询输出版本详情。

    Returns:
        输出版本 dict（含完整 content）或 None
    """
    sql = """
        SELECT o.output_id, o.task_id, o.branch_id, o.invocation_id,
               o.version_no, o.output_title, o.content, o.source_type,
               o.parent_output_id, o.lock_version,
               o.last_modified_at, o.last_modified_by,
               o.edit_summary, o.is_final_candidate, o.status,
               o.created_at, o.created_by,
               t.title AS task_title,
               c.username AS creator_username, c.real_name AS creator_real_name
        FROM task_outputs o
        INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
        LEFT JOIN users c ON o.created_by = c.user_id AND c.is_deleted = 0
        WHERE o.output_id = %s AND o.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id,))
        return cursor.fetchone()


def get_output_task_id(output_id: int) -> Optional[int]:
    """从 output_id 查询所属 task_id。"""
    sql = "SELECT task_id FROM task_outputs WHERE output_id = %s AND is_deleted = 0"
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id,))
        row = cursor.fetchone()
        return row["task_id"] if row else None


def get_output_by_id_and_task(output_id: int, task_id: int) -> Optional[Dict[str, Any]]:
    """确认 output 属于指定 task。"""
    sql = """
        SELECT output_id FROM task_outputs
        WHERE output_id = %s AND task_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id, task_id))
        return cursor.fetchone()


def get_branch_by_id_and_task(branch_id: int, task_id: int) -> Optional[Dict[str, Any]]:
    """确认分支属于指定 task。"""
    sql = """
        SELECT branch_id FROM task_branches
        WHERE branch_id = %s AND task_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (branch_id, task_id))
        return cursor.fetchone()


# =============================================================================
# 版本时间线查询（修复：从 output_id 向上追溯父版本链）
# =============================================================================

def get_output_parent_chain(output_id: int) -> List[Dict[str, Any]]:
    """
    查询指定 output_id 的父版本链（从最早父版本到当前版本）。

    使用 WITH RECURSIVE，从目标 output_id 开始，递归向上找 parent_output_id。
    结果按 depth 升序排列（0=当前版本，越大=越早的父版本）。

    最终 service 层反转顺序返回：最早版本 -> ... -> 当前版本。

    Args:
        output_id: 目标输出 ID

    Returns:
        父版本链列表（含 output_id, parent_output_id, version_no, ...）
    """
    timeline_sql = """
        WITH RECURSIVE parent_chain AS (
            -- 锚点：当前 output
            SELECT
                o.output_id,
                o.parent_output_id,
                o.task_id,
                o.version_no,
                o.output_title,
                o.source_type,
                o.created_by,
                o.created_at,
                0 AS depth
            FROM task_outputs o
            WHERE o.output_id = %s AND o.is_deleted = 0

            UNION ALL

            -- 递归：找父版本
            SELECT
                p.output_id,
                p.parent_output_id,
                p.task_id,
                p.version_no,
                p.output_title,
                p.source_type,
                p.created_by,
                p.created_at,
                pc.depth + 1 AS depth
            FROM task_outputs p
            INNER JOIN parent_chain pc ON p.output_id = pc.parent_output_id
            WHERE p.is_deleted = 0
        )
        SELECT
            pc.output_id,
            pc.parent_output_id,
            pc.version_no,
            pc.output_title,
            pc.source_type,
            pc.created_by,
            pc.created_at,
            pc.depth,
            u.username AS creator_username,
            u.real_name AS creator_real_name
        FROM parent_chain pc
        LEFT JOIN users u ON pc.created_by = u.user_id AND u.is_deleted = 0
        ORDER BY pc.depth DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(timeline_sql, (output_id,))
        return cursor.fetchall()


# =============================================================================
# 版本号生成（事务内，带 FOR UPDATE 锁）
# =============================================================================

def get_next_version_no_for_update(
    task_id: int,
    conn: Connection,
) -> int:
    """
    在事务内生成下一个版本号（带 FOR UPDATE 锁）。

    通过对 task_outputs 表加读锁（SELECT ... FOR UPDATE）确保并发安全。
    返回当前 task 下最大 version_no + 1。

    此函数必须在 service 层已开启事务（conn 已传入）后调用。

    Args:
        task_id: 任务 ID
        conn: 已开启事务的数据库连接

    Returns:
        下一个版本号
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT MAX(version_no) AS max_ver FROM task_outputs
            WHERE task_id = %s AND is_deleted = 0
            FOR UPDATE
            """,
            (task_id,),
        )
        row = cursor.fetchone()
        max_ver = row["max_ver"] if row and row["max_ver"] is not None else 0
        return max_ver + 1
    finally:
        cursor.close()


# =============================================================================
# 输出版本写操作
# =============================================================================

def create_manual_output(
    task_id: int,
    branch_id: Optional[int],
    version_no: int,
    output_title: str,
    content: str,
    source_type: str,
    parent_output_id: Optional[int],
    edit_summary: Optional[str],
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建人工输出版本。

    Args:
        edit_summary: 编辑说明（可为 None 或空字符串）

    Returns:
        新输出 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO task_outputs
            (task_id, branch_id, version_no, output_title, content,
             source_type, parent_output_id,
             lock_version, last_modified_at, last_modified_by,
             edit_summary, is_final_candidate, status,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s,
             0, %s, %s,
             %s, 0, 'draft',
             0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                task_id, branch_id, version_no, output_title, content,
                source_type, parent_output_id,
                now, created_by,
                edit_summary,
                now, created_by,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                task_id, branch_id, version_no, output_title, content,
                source_type, parent_output_id,
                now, created_by,
                edit_summary,
                now, created_by,
            ))
            return cursor.lastrowid
