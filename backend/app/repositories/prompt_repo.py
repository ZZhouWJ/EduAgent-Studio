"""
提示词模板 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
软删除为主，不物理删除。

事务说明：
- 纯查询函数使用 get_db_cursor()（自动提交）
- 写操作函数支持可选 conn 参数，由 service 层传入显式事务连接
- repository 方法不擅自 commit
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pymysql.connections import Connection

from app.database import get_db_cursor


# =============================================================================
# 任务类型查询
# =============================================================================

def list_task_types(status_only_active: bool = True) -> List[Dict[str, Any]]:
    """
    查询任务类型列表。

    Args:
        status_only_active: 是否只返回 active 状态，默认 True

    Returns:
        任务类型列表
    """
    if status_only_active:
        sql = """
            SELECT task_type_id, type_name, type_code, description,
                   default_template_id, status,
                   created_at, updated_at
            FROM task_types
            WHERE is_deleted = 0 AND status = 'active'
            ORDER BY created_at ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    else:
        sql = """
            SELECT task_type_id, type_name, type_code, description,
                   default_template_id, status,
                   created_at, updated_at
            FROM task_types
            WHERE is_deleted = 0
            ORDER BY created_at ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


def get_task_type_by_id(task_type_id: int) -> Optional[Dict[str, Any]]:
    """按 ID 查询任务类型。"""
    sql = """
        SELECT task_type_id, type_name, type_code, description,
               default_template_id, status,
               created_at, updated_at
        FROM task_types
        WHERE task_type_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (task_type_id,))
        return cursor.fetchone()


# =============================================================================
# 提示词模板查询
# =============================================================================

def get_template_by_id(template_id: int) -> Optional[Dict[str, Any]]:
    """
    按 template_id 查询模板详情。

    Returns:
        模板 dict（含当前版本内容）或 None
    """
    sql = """
        SELECT pt.template_id, pt.template_name, pt.task_type_id,
               pt.description, pt.current_version_id, pt.is_active,
               pt.created_at, pt.created_by, pt.updated_at, pt.updated_by,
               tt.type_name, tt.type_code,
               u.username AS creator_username, u.real_name AS creator_real_name,
               pv.version_no AS current_version_no,
               pv.prompt_content AS current_prompt_content
        FROM prompt_templates pt
        INNER JOIN task_types tt ON pt.task_type_id = tt.task_type_id
            AND tt.is_deleted = 0
        LEFT JOIN users u ON pt.created_by = u.user_id AND u.is_deleted = 0
        LEFT JOIN prompt_versions pv ON pt.current_version_id = pv.prompt_version_id
            AND pv.is_deleted = 0
        WHERE pt.template_id = %s AND pt.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (template_id,))
        return cursor.fetchone()


def list_templates(
    task_type_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    分页查询提示词模板列表。

    Returns:
        (模板列表, 总数)
    """
    offset = (page - 1) * page_size

    base_where = "pt.is_deleted = 0"

    if task_type_id is not None:
        task_type_filter = " AND pt.task_type_id = %s"
        task_type_param = task_type_id
    else:
        task_type_filter = ""
        task_type_param = None

    if keyword:
        like = f"%{keyword}%"
        keyword_filter = " AND pt.template_name LIKE %s"
    else:
        like = None
        keyword_filter = ""

    where_clause = base_where + task_type_filter + keyword_filter

    if task_type_param and like:
        count_params = [task_type_param, like]
        data_params = [task_type_param, like, page_size, offset]
    elif task_type_param:
        count_params = [task_type_param]
        data_params = [task_type_param, page_size, offset]
    elif like:
        count_params = [like]
        data_params = [like, page_size, offset]
    else:
        count_params = []
        data_params = [page_size, offset]

    count_sql = f"SELECT COUNT(*) AS total FROM prompt_templates pt WHERE {where_clause}"

    data_sql = f"""
        SELECT pt.template_id, pt.template_name, pt.task_type_id,
               pt.description, pt.current_version_id, pt.is_active,
               pt.created_at, pt.created_by, pt.updated_at,
               tt.type_name, tt.type_code,
               u.username AS creator_username, u.real_name AS creator_real_name,
               pv.version_no AS current_version_no
        FROM prompt_templates pt
        INNER JOIN task_types tt ON pt.task_type_id = tt.task_type_id
            AND tt.is_deleted = 0
        LEFT JOIN users u ON pt.created_by = u.user_id AND u.is_deleted = 0
        LEFT JOIN prompt_versions pv ON pt.current_version_id = pv.prompt_version_id
            AND pv.is_deleted = 0
        WHERE {where_clause}
        ORDER BY pt.created_at DESC
        LIMIT %s OFFSET %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, count_params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, data_params)
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# 提示词模板写操作
# =============================================================================

def create_template(
    template_name: str,
    task_type_id: int,
    description: Optional[str],
    created_by: int,
    is_active: bool = False,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建提示词模板。

    Returns:
        新模板 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO prompt_templates
            (template_name, task_type_id, description,
             is_active, current_version_id,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, NULL, 0, %s, %s)
    """
    params = (
        template_name,
        task_type_id,
        description,
        1 if is_active else 0,
        now,
        created_by,
    )
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid


def update_template(
    template_id: int,
    template_name: Optional[str] = None,
    task_type_id: Optional[int] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    updated_by: Optional[int] = None,
    conn: Optional[Connection] = None,
) -> int:
    """
    更新提示词模板字段。

    Returns:
        affected_rows
    """
    fields = []
    params: list = []

    if template_name is not None:
        fields.append("template_name = %s")
        params.append(template_name)
    if task_type_id is not None:
        fields.append("task_type_id = %s")
        params.append(task_type_id)
    if description is not None:
        fields.append("description = %s")
        params.append(description)
    if is_active is not None:
        fields.append("is_active = %s")
        params.append(1 if is_active else 0)

    if not fields:
        return 0

    fields.append("updated_at = %s")
    params.append(datetime.now())

    if updated_by is not None:
        fields.append("updated_by = %s")
        params.append(updated_by)

    params.append(template_id)

    sql = (
        f"UPDATE prompt_templates SET {', '.join(fields)} "
        f"WHERE template_id = %s AND is_deleted = 0"
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


def soft_delete_template(
    template_id: int,
    deleted_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    软删除提示词模板。

    Returns:
        affected_rows
    """
    sql = """
        UPDATE prompt_templates
        SET is_deleted = 1,
            deleted_at = %s,
            deleted_by = %s
        WHERE template_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (datetime.now(), deleted_by, template_id))
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (datetime.now(), deleted_by, template_id))
            return cursor.rowcount


def set_current_version(
    template_id: int,
    version_id: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    设置模板的当前活动版本。

    Returns:
        affected_rows
    """
    sql = """
        UPDATE prompt_templates
        SET current_version_id = %s,
            updated_at = %s
        WHERE template_id = %s AND is_deleted = 0
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (version_id, datetime.now(), template_id))
            return cursor.rowcount
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (version_id, datetime.now(), template_id))
            return cursor.rowcount


# =============================================================================
# 提示词版本查询
# =============================================================================

def list_template_versions(template_id: int) -> List[Dict[str, Any]]:
    """
    查询模板的版本列表。

    Returns:
        版本列表（按 created_at DESC）
    """
    sql = """
        SELECT pv.prompt_version_id, pv.template_id, pv.version_no,
               pv.prompt_content, pv.change_note,
               pv.created_at, pv.created_by,
               (pt.current_version_id = pv.prompt_version_id) AS is_active,
               u.username AS creator_username, u.real_name AS creator_real_name
        FROM prompt_versions pv
        INNER JOIN prompt_templates pt ON pv.template_id = pt.template_id
            AND pt.is_deleted = 0
        LEFT JOIN users u ON pv.created_by = u.user_id AND u.is_deleted = 0
        WHERE pv.template_id = %s AND pv.is_deleted = 0
        ORDER BY pv.created_at DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (template_id,))
        return cursor.fetchall()


def get_version_by_id(version_id: int) -> Optional[Dict[str, Any]]:
    """按 version_id 查询版本。"""
    sql = """
        SELECT pv.prompt_version_id, pv.template_id, pv.version_no,
               pv.prompt_content, pv.change_note,
               pv.created_at, pv.created_by, pv.updated_at,
               (pt.current_version_id = pv.prompt_version_id) AS is_active,
               u.username AS creator_username, u.real_name AS creator_real_name
        FROM prompt_versions pv
        INNER JOIN prompt_templates pt ON pv.template_id = pt.template_id
            AND pt.is_deleted = 0
        LEFT JOIN users u ON pv.created_by = u.user_id AND u.is_deleted = 0
        WHERE pv.prompt_version_id = %s AND pv.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (version_id,))
        return cursor.fetchone()


def get_version_by_template_and_id(
    version_id: int,
    template_id: int,
) -> Optional[Dict[str, Any]]:
    """确认版本属于指定模板。"""
    sql = """
        SELECT prompt_version_id FROM prompt_versions
        WHERE prompt_version_id = %s AND template_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (version_id, template_id))
        return cursor.fetchone()


def get_next_version_no(template_id: int) -> int:
    """
    生成下一个版本号。

    策略：取当前最大版本号 + 1（按字符串排序取最大值）
    """
    sql = """
        SELECT version_no FROM prompt_versions
        WHERE template_id = %s AND is_deleted = 0
        ORDER BY created_at DESC
        LIMIT 1
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (template_id,))
        row = cursor.fetchone()
        if row is None:
            return 1
        return int(row["version_no"]) + 1


def get_template_created_by(template_id: int) -> Optional[int]:
    """获取模板创建人 user_id。"""
    sql = "SELECT created_by FROM prompt_templates WHERE template_id = %s AND is_deleted = 0"
    with get_db_cursor() as cursor:
        cursor.execute(sql, (template_id,))
        row = cursor.fetchone()
        return row["created_by"] if row else None


# =============================================================================
# 提示词版本写操作
# =============================================================================

def create_version(
    template_id: int,
    version_no: str,
    prompt_content: str,
    change_note: Optional[str],
    created_by: int,
    conn: Optional[Connection] = None,
) -> int:
    """
    创建提示词版本。

    Returns:
        新版本 ID
    """
    now = datetime.now()
    sql = """
        INSERT INTO prompt_versions
            (template_id, version_no, prompt_content, change_note,
             is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, 0, %s, %s)
    """
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (template_id, version_no, prompt_content, change_note, now, created_by))
            return cursor.lastrowid
        finally:
            cursor.close()
    else:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (template_id, version_no, prompt_content, change_note, now, created_by))
            return cursor.lastrowid
