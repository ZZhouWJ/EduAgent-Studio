"""
调用日志与输出 Repository 层。

处理 AI 调用记录、任务输出、成本记录相关数据库操作。
所有数据库操作使用参数化 SQL，不拼接用户输入。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pymysql.connections import Connection

from app.database import get_db_cursor


# =============================================================================
# AI 调用记录查询
# =============================================================================

def get_invocation_by_id(invocation_id: int) -> Optional[Dict[str, Any]]:
    """
    按 invocation_id 查询调用详情。

    Returns:
        调用详情 dict（含模型名、任务名等）或 None
    """
    sql = """
        SELECT i.invocation_id, i.project_id, i.task_id, i.branch_id,
               i.model_id, i.prompt_version_id,
               i.input_text, i.output_text, i.error_message,
               i.input_tokens, i.output_tokens, i.latency_ms,
               i.status, i.created_by, i.created_at,
               m.model_name, m.display_name AS model_display_name,
               p.provider_name,
               t.title AS task_title,
               b.branch_name,
               u.username AS creator_username, u.real_name AS creator_real_name
        FROM ai_invocations i
        LEFT JOIN ai_models m ON i.model_id = m.model_id
        LEFT JOIN model_providers p ON m.provider_id = p.provider_id
        LEFT JOIN project_tasks t ON i.task_id = t.task_id
        LEFT JOIN task_branches b ON i.branch_id = b.branch_id
        LEFT JOIN users u ON i.created_by = u.user_id AND u.is_deleted = 0
        WHERE i.invocation_id = %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (invocation_id,))
        return cursor.fetchone()


def list_invocations(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    model_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询调用记录列表。

    Args:
        is_admin: 是否为管理员（admin 查全部）
        user_id: 当前用户 ID（用于限制非 admin 只能查自己有权限项目的记录）

    Returns:
        (调用列表, 总数)
    """
    offset = (page - 1) * page_size

    filters = []
    params: list = []

    if project_id is not None:
        filters.append("i.project_id = %s")
        params.append(project_id)

    if task_id is not None:
        filters.append("i.task_id = %s")
        params.append(task_id)

    if model_id is not None:
        filters.append("i.model_id = %s")
        params.append(model_id)

    if status:
        filters.append("i.status = %s")
        params.append(status)

    if not is_admin:
        filters.append("""
            i.task_id IN (
                SELECT task_id FROM project_tasks pt
                INNER JOIN project_members pm ON pt.project_id = pm.project_id
                WHERE pm.user_id = %s AND pm.is_deleted = 0 AND pt.is_deleted = 0
            )
        """)
        params.append(user_id)

    where_clause = " AND ".join(filters) if filters else "1=1"

    count_sql = f"SELECT COUNT(*) AS total FROM ai_invocations i WHERE {where_clause}"

    data_sql = f"""
        SELECT i.invocation_id, i.project_id, i.task_id, i.branch_id,
               i.model_id, i.status,
               i.input_tokens, i.output_tokens, i.latency_ms,
               i.created_by, i.created_at,
               m.model_name, m.display_name AS model_display_name,
               p.provider_name,
               t.title AS task_title,
               b.branch_name,
               u.username AS creator_username
        FROM ai_invocations i
        LEFT JOIN ai_models m ON i.model_id = m.model_id
        LEFT JOIN model_providers p ON m.provider_id = p.provider_id
        LEFT JOIN project_tasks t ON i.task_id = t.task_id
        LEFT JOIN task_branches b ON i.branch_id = b.branch_id
        LEFT JOIN users u ON i.created_by = u.user_id AND u.is_deleted = 0
        WHERE {where_clause}
        ORDER BY i.created_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# AI 调用记录写操作
# =============================================================================

def create_invocation(
    project_id: int,
    task_id: int,
    branch_id: Optional[int],
    model_id: int,
    prompt_version_id: Optional[int],
    input_text: str,
    output_text: Optional[str],
    error_message: Optional[str],
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    status: str,
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建 AI 调用记录。

    Returns:
        新调用记录 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO ai_invocations
            (project_id, task_id, branch_id, model_id, prompt_version_id,
             input_text, output_text, error_message,
             input_tokens, output_tokens, latency_ms,
             status, created_by, created_at)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                project_id, task_id, branch_id, model_id, prompt_version_id,
                input_text, output_text, error_message,
                input_tokens, output_tokens, latency_ms,
                status, created_by, now,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                project_id, task_id, branch_id, model_id, prompt_version_id,
                input_text, output_text, error_message,
                input_tokens, output_tokens, latency_ms,
                status, created_by, now,
            ))
            return cursor.lastrowid


# =============================================================================
# 任务输出（生成结果）写操作
# =============================================================================

def get_next_output_version_no_for_update(
    task_id: int,
    conn: Connection,
) -> int:
    """
    在事务内生成下一个版本号（带 FOR UPDATE 锁）。

    对 task_outputs 表加读锁，确保并发安全。
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


def create_task_output(
    task_id: int,
    branch_id: Optional[int],
    invocation_id: Optional[int],
    version_no: int,
    output_title: str,
    content: str,
    source_type: str,
    parent_output_id: Optional[int],
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建任务输出（由 AI 生成）。

    Returns:
        新输出 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO task_outputs
            (task_id, branch_id, invocation_id, version_no, output_title, content,
             source_type, parent_output_id,
             lock_version, last_modified_at, last_modified_by,
             is_final_candidate, status,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, 0, 'draft', 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                task_id, branch_id, invocation_id, version_no,
                output_title, content, source_type, parent_output_id,
                now, created_by, now, created_by,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                task_id, branch_id, invocation_id, version_no,
                output_title, content, source_type, parent_output_id,
                now, created_by, now, created_by,
            ))
            return cursor.lastrowid


# =============================================================================
# 成本记录写操作
# =============================================================================

def create_cost_record(
    invocation_id: int,
    project_id: int,
    task_id: int,
    model_id: int,
    user_id: int,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    input_cost: float,
    output_cost: float,
    total_cost: float,
    currency: str,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建成本记录。

    Returns:
        新成本记录 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO cost_records
            (invocation_id, project_id, task_id, model_id, user_id,
             input_tokens, output_tokens, total_tokens,
             input_cost, output_cost, total_cost, currency,
             created_at)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                invocation_id, project_id, task_id, model_id, user_id,
                input_tokens, output_tokens, total_tokens,
                input_cost, output_cost, total_cost, currency, now,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                invocation_id, project_id, task_id, model_id, user_id,
                input_tokens, output_tokens, total_tokens,
                input_cost, output_cost, total_cost, currency, now,
            ))
            return cursor.lastrowid
