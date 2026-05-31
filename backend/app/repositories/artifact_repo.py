"""
成果库与分支合并 Repository 层。

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

# =============================================================================
# 常量
# =============================================================================

VALID_MERGE_STRATEGIES = {"adopt_source", "adopt_target", "manual_merge", "adopt_separately"}
ADOPTABLE_OUTPUT_STATUS = {"approved"}


# =============================================================================
# adopted_outputs 查询
# =============================================================================

def get_output_for_adoption(output_id: int) -> Optional[Dict[str, Any]]:
    """
    查询输出及其所属项目上下文，用于成果采用校验。

    Returns:
        dict（含 output_id, task_id, project_id, status, content）或 None
    """
    sql = """
        SELECT o.output_id, o.task_id, o.content, o.status AS output_status,
               t.project_id, t.title AS task_title
        FROM task_outputs o
        INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
        WHERE o.output_id = %s AND o.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id,))
        return cursor.fetchone()


def has_adopted_output(output_id: int, conn: Optional[Connection] = None) -> bool:
    """
    检查指定 output 是否已被采用。

    Returns:
        True 表示已采用，False 表示未采用
    """
    sql = """
        SELECT 1 FROM adopted_outputs
        WHERE output_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (output_id,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (output_id,))
            return cursor.fetchone() is not None


def get_adopted_output_by_id(adopted_id: int) -> Optional[Dict[str, Any]]:
    """
    按 adopted_id 查询成果详情（含联表信息）。
    """
    sql = """
        SELECT a.adopted_id, a.project_id, a.task_id, a.output_id,
               a.artifact_title, a.artifact_type, a.release_version,
               a.adopted_by, a.adopted_at,
               p.project_name,
               t.title AS task_title,
               o.output_title, o.version_no, o.content AS output_content,
               o.status AS output_status,
               u.username AS adopted_by_username,
               u.real_name AS adopted_by_real_name,
               a.created_at, a.created_by, a.updated_at, a.updated_by
        FROM adopted_outputs a
        INNER JOIN projects p ON a.project_id = p.project_id AND p.is_deleted = 0
        INNER JOIN project_tasks t ON a.task_id = t.task_id AND t.is_deleted = 0
        INNER JOIN task_outputs o ON a.output_id = o.output_id AND o.is_deleted = 0
        LEFT JOIN users u ON a.adopted_by = u.user_id AND u.is_deleted = 0
        WHERE a.adopted_id = %s AND a.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (adopted_id,))
        return cursor.fetchone()


def list_project_artifacts(
    is_admin: bool,
    user_id: int,
    project_id: int,
    artifact_type: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询项目成果列表。

    Args:
        is_admin: 是否为管理员
        user_id: 当前用户 ID
        project_id: 项目 ID
        artifact_type: 可选的类型过滤
        keyword: 可选的标题模糊搜索
        page: 页码
        page_size: 每页条数

    Returns:
        (成果列表, 总数)
    """
    offset = (page - 1) * page_size
    params: list = []

    base_where = "a.is_deleted = 0 AND a.project_id = %s"
    params.append(project_id)

    if artifact_type:
        base_where += " AND a.artifact_type = %s"
        params.append(artifact_type)

    if keyword:
        base_where += " AND a.artifact_title LIKE %s"
        params.append(f"%{keyword}%")

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM adopted_outputs a
        WHERE {base_where}
    """

    data_sql = f"""
        SELECT a.adopted_id, a.project_id, a.task_id, a.output_id,
               a.artifact_title, a.artifact_type, a.release_version,
               a.adopted_by, a.adopted_at,
               t.title AS task_title,
               o.output_title, o.version_no,
               u.username AS adopted_by_username,
               u.real_name AS adopted_by_real_name
        FROM adopted_outputs a
        INNER JOIN project_tasks t ON a.task_id = t.task_id AND t.is_deleted = 0
        INNER JOIN task_outputs o ON a.output_id = o.output_id AND o.is_deleted = 0
        LEFT JOIN users u ON a.adopted_by = u.user_id AND u.is_deleted = 0
        WHERE {base_where}
        ORDER BY a.adopted_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# task_branches 查询
# =============================================================================

def get_branch_context(branch_id: int) -> Optional[Dict[str, Any]]:
    """
    查询分支上下文（用于分支合并校验）。

    Returns:
        dict（含 branch_id, task_id, project_id, status）或 None
    """
    sql = """
        SELECT b.branch_id, b.task_id, b.project_id, b.branch_name,
               b.base_output_id, b.status AS branch_status,
               t.title AS task_title
        FROM task_branches b
        INNER JOIN project_tasks t ON b.task_id = t.task_id AND t.is_deleted = 0
        WHERE b.branch_id = %s AND b.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (branch_id,))
        return cursor.fetchone()


def get_task_context(task_id: int) -> Optional[Dict[str, Any]]:
    """
    查询任务上下文。
    """
    sql = """
        SELECT task_id, project_id, title AS task_title
        FROM project_tasks
        WHERE task_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (task_id,))
        return cursor.fetchone()


def get_output_context(output_id: int) -> Optional[Dict[str, Any]]:
    """
    查询输出上下文。
    """
    sql = """
        SELECT o.output_id, o.task_id, o.status AS output_status
        FROM task_outputs o
        WHERE o.output_id = %s AND o.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id,))
        return cursor.fetchone()


# =============================================================================
# adopted_outputs 写操作
# =============================================================================

def create_adopted_output(
    project_id: int,
    task_id: int,
    output_id: int,
    artifact_title: str,
    artifact_type: str,
    release_version: str,
    adopted_by: int,
    conn: Connection,
) -> int:
    """
    创建成果采用记录。

    Returns:
        新 adopted_id
    """
    now = datetime.now()
    sql = """
        INSERT INTO adopted_outputs
            (project_id, task_id, output_id,
             artifact_title, artifact_type, release_version,
             adopted_by, adopted_at,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s,
             %s, %s, %s,
             %s, %s,
             0, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (
            project_id, task_id, output_id,
            artifact_title, artifact_type, release_version,
            adopted_by, now,
            now, adopted_by,
        ))
        return cursor.lastrowid
    finally:
        cursor.close()


def update_output_status_adopted(
    output_id: int,
    conn: Connection,
) -> int:
    """
    将输出版本状态更新为 adopted。

    Returns:
        affected_rows
    """
    now = datetime.now()
    sql = """
        UPDATE task_outputs
        SET status = 'adopted',
            updated_at = %s
        WHERE output_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (now, output_id))
        return cursor.rowcount
    finally:
        cursor.close()


def update_task_status_adopted(
    task_id: int,
    conn: Connection,
) -> int:
    """
    将任务状态更新为 adopted。

    Returns:
        affected_rows
    """
    now = datetime.now()
    sql = """
        UPDATE project_tasks
        SET status = 'adopted',
            updated_at = %s
        WHERE task_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (now, task_id))
        return cursor.rowcount
    finally:
        cursor.close()


# =============================================================================
# task_outputs 写操作（分支合并相关）
# =============================================================================

def get_next_version_no(task_id: int, conn: Connection) -> int:
    """
    在事务内为指定 task 生成下一个 version_no。

    Returns:
        新的 version_no（整数）
    """
    sql = """
        SELECT COALESCE(MAX(version_no), 0) + 1 AS next_version
        FROM task_outputs
        WHERE task_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (task_id,))
        row = cursor.fetchone()
        return row["next_version"] if row else 1
    finally:
        cursor.close()


def create_task_output(
    task_id: int,
    output_title: str,
    content: str,
    source_type: str,
    parent_output_id: Optional[int],
    branch_id: int,
    created_by: int,
    edit_summary: Optional[str],
    conn: Connection,
) -> int:
    """
    创建新的输出版本（用于 manual_merge）。

    写入字段：
    - task_id, output_title, content, source_type
    - parent_output_id, branch_id
    - status='generated', version_no（事务内生成）
    - lock_version=0, is_deleted=0
    - created_at, created_by
    - updated_at, updated_by, last_modified_at, last_modified_by
    - edit_summary

    Returns:
        新 output_id
    """
    now = datetime.now()
    version_no = get_next_version_no(task_id, conn)
    sql = """
        INSERT INTO task_outputs
            (task_id, output_title, content,
             source_type, parent_output_id, branch_id,
             status, version_no,
             lock_version,
             is_deleted,
             created_at, created_by,
             updated_at, updated_by,
             last_modified_at, last_modified_by,
             edit_summary)
        VALUES
            (%s, %s, %s,
             %s, %s, %s,
             'generated', %s,
             0,
             0,
             %s, %s,
             %s, %s,
             %s, %s,
             %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (
            task_id, output_title, content,
            source_type, parent_output_id, branch_id,
            version_no,
            now, created_by,
            now, created_by,
            now, created_by,
            edit_summary or "分支手动合并生成",
        ))
        return cursor.lastrowid
    finally:
        cursor.close()


def update_output_status(
    output_id: int,
    status: str,
    conn: Connection,
) -> int:
    """
    更新输出版本状态（用于分支合并后的状态更新）。

    Returns:
        affected_rows
    """
    now = datetime.now()
    sql = """
        UPDATE task_outputs
        SET status = %s,
            updated_at = %s
        WHERE output_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (status, now, output_id))
        return cursor.rowcount
    finally:
        cursor.close()


# =============================================================================
# task_branches 写操作
# =============================================================================

def update_branch_status(
    branch_id: int,
    status: str,
    conn: Connection,
) -> int:
    """
    更新分支状态。

    Returns:
        affected_rows
    """
    now = datetime.now()
    sql = """
        UPDATE task_branches
        SET status = %s,
            updated_at = %s
        WHERE branch_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (status, now, branch_id))
        return cursor.rowcount
    finally:
        cursor.close()


# =============================================================================
# merge_records 写操作
# =============================================================================

def create_merge_record(
    project_id: int,
    task_id: int,
    base_output_id: Optional[int],
    source_output_id: Optional[int],
    target_output_id: Optional[int],
    merged_output_id: Optional[int],
    merge_strategy: str,
    merge_comment: Optional[str],
    merged_by: int,
    conn: Connection,
) -> int:
    """
    创建分支合并记录。

    Returns:
        新 merge_id
    """
    now = datetime.now()
    sql = """
        INSERT INTO merge_records
            (project_id, task_id,
             base_output_id, source_output_id, target_output_id, merged_output_id,
             merge_strategy, merge_comment,
             merged_by, merged_at,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s,
             %s, %s, %s, %s,
             %s, %s,
             %s, %s,
             0, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (
            project_id, task_id,
            base_output_id, source_output_id, target_output_id, merged_output_id,
            merge_strategy, merge_comment,
            merged_by, now,
            now, merged_by,
        ))
        return cursor.lastrowid
    finally:
        cursor.close()


# =============================================================================
# 权限辅助
# =============================================================================

def is_user_project_leader(project_id: int, user_id: int) -> bool:
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s
          AND project_role = 'leader'
          AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_project_teacher(project_id: int, user_id: int) -> bool:
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s
          AND project_role = 'teacher'
          AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_in_project(project_id: int, user_id: int) -> bool:
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def is_user_admin(user_id: int) -> bool:
    """
    判断用户是否为管理员。

    基于冻结 Schema 通过 user_roles + roles 关联查询：
    - users.user_id = user_roles.user_id
    - user_roles.role_id = roles.role_id
    - roles.role_code = 'admin'
    """
    sql = """
        SELECT 1 FROM users u
        JOIN user_roles ur ON u.user_id = ur.user_id AND ur.is_deleted = 0
        JOIN roles r ON ur.role_id = r.role_id AND r.is_deleted = 0
        WHERE u.user_id = %s
          AND u.is_deleted = 0
          AND r.role_code = 'admin'
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (user_id,))
        return cursor.fetchone() is not None
        return cursor.fetchone() is not None


def get_adopted_output_project_context(adopted_id: int) -> Optional[Dict[str, Any]]:
    """通过 adopted_id 获取所属项目 ID（用于权限判断）。"""
    sql = """
        SELECT adopted_id, project_id
        FROM adopted_outputs
        WHERE adopted_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (adopted_id,))
        return cursor.fetchone()
