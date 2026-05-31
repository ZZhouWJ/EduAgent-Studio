"""
审核中心 Repository 层。

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

VALID_REVIEW_STATUS = {"pending", "approved", "rejected", "revision_required"}
VALID_TASK_STATUS_FROM_REVIEW = {"submitted", "approved", "rejected", "revision_required"}
# 完成审核时只允许这三种结论状态，不得使用 pending
VALID_COMPLETE_REVIEW_STATUS = {"approved", "rejected", "revision_required"}


# =============================================================================
# 审核请求查询
# =============================================================================

def get_review_request_by_id(request_id: int) -> Optional[Dict[str, Any]]:
    """
    按 request_id 查询审核请求详情。

    Returns:
        审核请求 dict（含 project_name、task_title、output_title 等联表字段）
    """
    sql = """
        SELECT r.request_id, r.output_id, r.task_id, r.project_id,
               r.submitter_id, r.reviewer_id, r.request_status,
               r.submit_note, r.reviewed_at,
               r.is_deleted, r.created_at, r.created_by,
               p.project_name,
               t.title AS task_title,
               o.output_title, o.version_no, o.content AS output_content,
               o.status AS output_status,
               s.username AS submitter_username,
               s.real_name AS submitter_real_name,
               rv.username AS reviewer_username,
               rv.real_name AS reviewer_real_name
        FROM review_requests r
        INNER JOIN projects p ON r.project_id = p.project_id AND p.is_deleted = 0
        INNER JOIN project_tasks t ON r.task_id = t.task_id AND t.is_deleted = 0
        INNER JOIN task_outputs o ON r.output_id = o.output_id AND o.is_deleted = 0
        LEFT JOIN users s ON r.submitter_id = s.user_id AND s.is_deleted = 0
        LEFT JOIN users rv ON r.reviewer_id = rv.user_id AND rv.is_deleted = 0
        WHERE r.request_id = %s AND r.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (request_id,))
        return cursor.fetchone()


def get_request_project_context(request_id: int) -> Optional[Dict[str, Any]]:
    """
    通过 request_id 查询审核请求关联的项目上下文。

    用于权限判断：获取 request_id、output_id、task_id、project_id、submitter_id、reviewer_id、request_status。

    Returns:
        dict 或 None
    """
    sql = """
        SELECT
            r.request_id,
            r.output_id,
            r.task_id,
            r.project_id,
            r.submitter_id,
            r.reviewer_id,
            r.request_status
        FROM review_requests r
        WHERE r.request_id = %s AND r.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (request_id,))
        return cursor.fetchone()


# =============================================================================
# 待审核列表查询
# =============================================================================

def list_pending_reviews(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询待审核列表（request_status = pending）。

    权限规则：
    - admin：查看全部
    - 非 admin：可查看（项目内 leader/teacher/reviewer 的项目 OR reviewer_id = 当前用户）的 pending 请求

    Args:
        is_admin: 是否为管理员（可查看全部）
        user_id: 当前用户 ID
        project_id: 可选的项目过滤

    Returns:
        (待审核列表, 总数)
    """
    offset = (page - 1) * page_size

    base_where = "r.is_deleted = 0 AND r.request_status = 'pending'"
    params: list = []

    if project_id is not None:
        base_where += " AND r.project_id = %s"
        params.append(project_id)

    if not is_admin:
        # 非 admin：查看本项目内 leader/teacher/reviewer 的 pending，
        # 或者 reviewer_id = 当前用户（允许普通 member 查看分配给自己的请求）
        member_filter = """
            AND (
                r.project_id IN (
                    SELECT pm.project_id FROM project_members pm
                    WHERE pm.user_id = %s AND pm.is_deleted = 0
                      AND pm.project_role IN ('leader', 'teacher', 'reviewer')
                )
                OR r.reviewer_id = %s
            )
        """
        base_where += member_filter
        params.append(user_id)
        params.append(user_id)

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM review_requests r
        WHERE {base_where}
    """

    data_sql = f"""
        SELECT r.request_id, r.output_id, r.task_id, r.project_id,
               r.submitter_id, r.reviewer_id, r.request_status,
               r.submit_note, r.created_at,
               p.project_name,
               t.title AS task_title,
               o.output_title, o.version_no,
               s.username AS submitter_username,
               s.real_name AS submitter_real_name,
               rv.username AS reviewer_username,
               rv.real_name AS reviewer_real_name
        FROM review_requests r
        INNER JOIN projects p ON r.project_id = p.project_id AND p.is_deleted = 0
        INNER JOIN project_tasks t ON r.task_id = t.task_id AND t.is_deleted = 0
        INNER JOIN task_outputs o ON r.output_id = o.output_id AND o.is_deleted = 0
        LEFT JOIN users s ON r.submitter_id = s.user_id AND s.is_deleted = 0
        LEFT JOIN users rv ON r.reviewer_id = rv.user_id AND rv.is_deleted = 0
        WHERE {base_where}
        ORDER BY r.created_at ASC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# 输出版本与项目上下文查询
# =============================================================================

def get_output_project_context(output_id: int) -> Optional[Dict[str, Any]]:
    """
    通过 output_id 查询所属项目上下文（用于权限判断）。

    Returns:
        dict（含 output_id, task_id, project_id, output_status）或 None
    """
    sql = """
        SELECT o.output_id, o.task_id, t.project_id, o.status AS output_status
        FROM task_outputs o
        INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
        WHERE o.output_id = %s AND o.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id,))
        return cursor.fetchone()


def get_output_by_id(output_id: int) -> Optional[Dict[str, Any]]:
    """
    按 output_id 查询输出版本（含 content）。
    """
    sql = """
        SELECT o.output_id, o.task_id, o.content, o.status AS output_status,
               t.project_id
        FROM task_outputs o
        INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
        WHERE o.output_id = %s AND o.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (output_id,))
        return cursor.fetchone()


# =============================================================================
# 用户查询
# =============================================================================

def get_user_basic_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    按 user_id 查询用户基本信息（不含 password_hash）。

    Returns:
        dict（含 user_id, username, roles）或 None
    """
    sql = """
        SELECT user_id, username, email, real_name, roles
        FROM users
        WHERE user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()


def get_project_member_role(project_id: int, user_id: int) -> Optional[str]:
    """
    查询用户在指定项目中的角色。

    Returns:
        project_role 字符串（'leader' / 'teacher' / 'reviewer' / 'member'）或 None（不在项目中）
    """
    sql = """
        SELECT project_role FROM project_members
        WHERE project_id = %s AND user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        row = cursor.fetchone()
        return row["project_role"] if row else None


# =============================================================================
# 项目成员权限查询
# =============================================================================

def is_user_project_leader(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目内 leader。"""
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
# 问题标签查询
# =============================================================================

def list_issue_tags() -> List[Dict[str, Any]]:
    """
    查询所有可用的问题标签（is_deleted = 0）。
    Returns:
        标签列表
    """
    sql = """
        SELECT tag_id, tag_name, tag_code, description, severity,
               created_at
        FROM issue_tags
        WHERE is_deleted = 0
        ORDER BY severity DESC, tag_id ASC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def check_issue_tags_exist(tag_ids: List[int]) -> Tuple[bool, List[int]]:
    """
    批量校验 issue_tags 是否存在且未删除。

    Returns:
        (全部存在, 存在的 tag_ids 列表)
    """
    if not tag_ids:
        return True, []
    placeholders = ",".join(["%s"] * len(tag_ids))
    sql = f"""
        SELECT tag_id FROM issue_tags
        WHERE tag_id IN ({placeholders}) AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, tag_ids)
        rows = cursor.fetchall()
        existing_ids = [r["tag_id"] for r in rows]
        return len(existing_ids) == len(tag_ids), existing_ids


# =============================================================================
# 审核请求写操作
# =============================================================================

def create_review_request(
    output_id: int,
    task_id: int,
    project_id: int,
    submitter_id: int,
    reviewer_id: Optional[int],
    submit_note: Optional[str],
    conn: Optional[Connection] = None,
) -> int:
    """
    创建审核请求。

    Returns:
        新请求 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO review_requests
            (output_id, task_id, project_id,
             submitter_id, reviewer_id,
             request_status, submit_note,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s,
             %s, %s,
             'pending', %s,
             0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                output_id, task_id, project_id,
                submitter_id, reviewer_id,
                submit_note,
                now, submitter_id,
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                output_id, task_id, project_id,
                submitter_id, reviewer_id,
                submit_note,
                now, submitter_id,
            ))
            return cursor.lastrowid


def has_pending_request(output_id: int, conn: Optional[Connection] = None) -> bool:
    """
    检查指定 output 是否存在 pending 状态的审核请求。

    Returns:
        True 表示存在，False 表示不存在
    """
    sql = """
        SELECT 1 FROM review_requests
        WHERE output_id = %s
          AND request_status = 'pending'
          AND is_deleted = 0
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


# =============================================================================
# 审核请求状态更新
# =============================================================================

def update_review_request_status(
    request_id: int,
    status: str,
    reviewed_at: datetime,
    conn: Connection,
) -> int:
    """
    更新审核请求状态。

    Returns:
        affected_rows
    """
    sql = """
        UPDATE review_requests
        SET request_status = %s,
            reviewed_at = %s
        WHERE request_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (status, reviewed_at, request_id))
        return cursor.rowcount
    finally:
        cursor.close()


# =============================================================================
# 输出版本状态更新
# =============================================================================

def update_output_status(
    output_id: int,
    status: str,
    conn: Connection,
) -> int:
    """
    更新输出版本状态。

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
# 任务状态更新
# =============================================================================

def update_task_status(
    task_id: int,
    status: str,
    conn: Connection,
) -> int:
    """
    更新项目任务状态。

    Returns:
        affected_rows
    """
    now = datetime.now()
    sql = """
        UPDATE project_tasks
        SET status = %s,
            updated_at = %s
        WHERE task_id = %s AND is_deleted = 0
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (status, now, task_id))
        return cursor.rowcount
    finally:
        cursor.close()


# =============================================================================
# 审核评分写操作
# =============================================================================

def create_output_review(
    request_id: int,
    output_id: int,
    reviewer_id: int,
    review_status: str,
    accuracy_score: Optional[float],
    completeness_score: Optional[float],
    logic_score: Optional[float],
    format_score: Optional[float],
    usability_score: Optional[float],
    risk_score: Optional[float],
    review_comment: Optional[str],
    created_by: int,
    conn: Connection,
) -> int:
    """
    创建审核评分记录。

    Returns:
        新评分 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO output_reviews
            (request_id, output_id, reviewer_id,
             accuracy_score, completeness_score, logic_score,
             format_score, usability_score, risk_score,
             review_status, review_comment,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s,
             %s, %s, %s,
             %s, %s, %s,
             %s, %s,
             0, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (
            request_id, output_id, reviewer_id,
            accuracy_score, completeness_score, logic_score,
            format_score, usability_score, risk_score,
            review_status, review_comment,
            now, created_by,
        ))
        return cursor.lastrowid
    finally:
        cursor.close()


# =============================================================================
# 问题标签关联写操作
# =============================================================================

def create_output_issue_relation(
    output_id: int,
    review_id: int,
    tag_id: int,
    created_by: int,
    conn: Connection,
) -> int:
    """
    创建输出与问题标签的关联记录。

    Returns:
        新关联 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO output_issue_relations
            (output_id, review_id, tag_id,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s,
             0, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (output_id, review_id, tag_id, now, created_by))
        return cursor.lastrowid
    finally:
        cursor.close()
