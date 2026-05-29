"""
项目 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
不返回 password_hash。
软删除为主，不物理删除。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db_cursor


# =============================================================================
# 项目基础查询
# =============================================================================

def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """
    按 project_id 查询项目详情（不含软删除）。

    Returns:
        项目 dict 或 None
    """
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
    """
    按用户权限查询项目列表。

    Args:
        user_id: 当前用户 ID
        is_admin: 是否为管理员
        is_teacher: 是否为教师
        page: 页码
        page_size: 每页条数
        keyword: 搜索关键字
        status: 状态过滤

    Returns:
        (项目列表, 总数)
    """
    offset = (page - 1) * page_size

    # 基础查询片段：仅查未删除项目
    base_where = "p.is_deleted = 0"

    if keyword:
        like = f"%{keyword}%"
        keyword_filter = f" AND (p.project_name LIKE %s OR p.description LIKE %s)"
    else:
        like = None
        keyword_filter = ""

    if status:
        status_filter = " AND p.status = %s"
    else:
        status_filter = ""

    # 权限过滤逻辑
    if is_admin:
        where_clause = base_where + keyword_filter + status_filter
        params = [like, like, status] if keyword and status else \
                 [like, like] if keyword else \
                 [status] if status else []
    elif is_teacher:
        # 教师：查看自己作为 teacher 角色的项目成员对应的项目
        where_clause = (
            base_where + keyword_filter + status_filter +
            " AND p.project_id IN ("
            "  SELECT pm.project_id FROM project_members pm"
            "  INNER JOIN user_roles ur ON pm.user_id = ur.user_id"
            "  INNER JOIN roles r ON ur.role_id = r.role_id"
            "  WHERE pm.is_deleted = 0"
            "    AND r.is_deleted = 0 AND r.role_code = 'teacher'"
            "    AND pm.user_id = %s"
            ")"
        )
        params = ([like, like, status, user_id] if keyword and status else
                  [like, like, user_id] if keyword else
                  [status, user_id] if status else
                  [user_id])
    else:
        # 普通成员：只看自己参与的项目
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

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM projects p
        WHERE {where_clause}
    """

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

    final_params = params + [page_size, offset]

    with get_db_cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        cursor.execute(data_sql, final_params)
        rows = cursor.fetchall()

    return rows, total


# =============================================================================
# 项目创建（事务）
# =============================================================================

def create_project(
    project_name: str,
    project_type: str,
    description: Optional[str],
    owner_id: int,
    created_by: int,
) -> int:
    """
    创建项目，并在同一事务中将创建人写入 project_members。

    Args:
        project_name: 项目名称
        project_type: 项目类型
        description: 描述
        owner_id: 所有者用户 ID
        created_by: 创建操作人 ID

    Returns:
        新项目 ID

    Raises:
        Exception: 事务失败时抛出
    """
    now = datetime.now()

    with get_db_cursor() as cursor:
        # 1. 插入项目
        insert_project_sql = """
            INSERT INTO projects
                (project_name, project_type, description, owner_id,
                 status, is_deleted, created_at, created_by)
            VALUES
                (%s, %s, %s, %s, 'active', 0, %s, %s)
        """
        cursor.execute(insert_project_sql, (
            project_name, project_type, description, owner_id, now, created_by,
        ))
        project_id = cursor.lastrowid

        # 2. 将创建人写入项目成员，角色为 leader
        insert_member_sql = """
            INSERT INTO project_members
                (project_id, user_id, project_role, joined_at,
                 status, is_deleted, created_at, created_by)
            VALUES
                (%s, %s, 'leader', %s, 'active', 0, %s, %s)
        """
        cursor.execute(insert_member_sql, (
            project_id, owner_id, now, now, created_by,
        ))


def update_project(
    project_id: int,
    project_name: Optional[str] = None,
    project_type: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    updated_by: Optional[int] = None,
) -> bool:
    """
    更新项目字段（仅更新非 None 的字段）。

    Returns:
        是否有字段被更新
    """
    fields = []
    params = []

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
        return False

    fields.append("updated_at = %s")
    params.append(datetime.now())

    if updated_by is not None:
        fields.append("updated_by = %s")
        params.append(updated_by)

    params.append(project_id)

    sql = f"UPDATE projects SET {', '.join(fields)} WHERE project_id = %s AND is_deleted = 0"

    with get_db_cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.rowcount > 0


def soft_delete_project(
    project_id: int,
    deleted_by: int,
) -> bool:
    """
    软删除项目。

    Returns:
        是否成功（项目是否存在且未删除）
    """
    sql = """
        UPDATE projects
        SET is_deleted = 1,
            deleted_at = %s,
            deleted_by = %s
        WHERE project_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (datetime.now(), deleted_by, project_id))
        return cursor.rowcount > 0


def archive_project(
    project_id: int,
    updated_by: int,
) -> bool:
    """
    归档项目（将状态设为 archived）。

    Returns:
        是否成功
    """
    sql = """
        UPDATE projects
        SET status = 'archived',
            updated_at = %s,
            updated_by = %s
        WHERE project_id = %s AND is_deleted = 0 AND status != 'archived'
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (datetime.now(), updated_by, project_id))
        return cursor.rowcount > 0


# =============================================================================
# 项目成员查询
# =============================================================================

def list_project_members(project_id: int) -> List[Dict[str, Any]]:
    """
    查询项目成员列表（不含软删除，不含 password_hash）。

    Returns:
        成员列表，每条含用户信息和 project_role
    """
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


def get_project_member_by_user(project_id: int, user_id: int) -> Optional[Dict[str, Any]]:
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


def is_user_in_project(project_id: int, user_id: int) -> bool:
    """判断用户是否为项目成员。"""
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


def add_project_member(
    project_id: int,
    user_id: int,
    project_role: str,
    created_by: int,
) -> int:
    """
    添加项目成员。

    Returns:
        新增 member_id

    Raises:
        Exception: 成员已存在或用户不存在时抛出
    """
    now = datetime.now()
    sql = """
        INSERT INTO project_members
            (project_id, user_id, project_role, joined_at,
             status, is_deleted, created_at, created_by)
        VALUES
            (%s, %s, %s, %s, 'active', 0, %s, %s)
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (
            project_id, user_id, project_role, now, now, created_by,
        ))
        return cursor.lastrowid


def update_project_member_role(
    member_id: int,
    project_role: str,
    updated_by: int,
) -> bool:
    """
    修改项目成员角色。

    Returns:
        是否成功
    """
    sql = """
        UPDATE project_members
        SET project_role = %s,
            updated_at = %s,
            updated_by = %s
        WHERE member_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_role, datetime.now(), updated_by, member_id))
        return cursor.rowcount > 0


def soft_delete_project_member(
    member_id: int,
    deleted_by: int,
) -> bool:
    """
    软删除项目成员（移除成员）。

    Returns:
        是否成功
    """
    sql = """
        UPDATE project_members
        SET is_deleted = 1,
            deleted_at = %s,
            deleted_by = %s
        WHERE member_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (datetime.now(), deleted_by, member_id))
        return cursor.rowcount > 0
