"""
任务 Service 层。

处理任务、任务分支、输出版本相关业务逻辑。
复用 project_service / project_repo 中的项目权限判断。
"""

from typing import Any, Dict, List, Optional

from app.database import get_db_transaction
from app.repositories import project_repo, task_repo, user_repo
from app.utils.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)

VALID_TASK_STATUS = {"draft", "running", "generated", "submitted",
                     "approved", "rejected", "revision_required",
                     "adopted", "archived", "conflict_pending"}
VALID_PRIORITY = {"low", "normal", "high", "urgent"}
VALID_SOURCE_TYPE = {"ai_generated", "manual_edit", "hybrid", "manual_merge"}


# =============================================================================
# 权限辅助函数（复用 project_repo）
# =============================================================================

def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def _can_access_project(project_id: int, user_id: int) -> bool:
    """判断用户是否有权访问指定项目。"""
    if user_repo.is_admin(user_id):
        return True
    return project_repo.is_user_in_project(project_id, user_id)


def _can_manage_project(project_id: int, user_id: int) -> bool:
    """判断用户是否有权管理项目（admin 或 owner 或 leader）。"""
    if user_repo.is_admin(user_id):
        return True
    return (
        project_repo.is_user_project_owner(project_id, user_id) or
        project_repo.is_user_project_leader(project_id, user_id)
    )


def _can_create_task(project_id: int, user: Dict[str, Any]) -> bool:
    """只有项目成员才能创建任务。"""
    if _is_admin(user):
        return True
    return project_repo.is_user_in_project(project_id, user["user_id"])


def _can_update_task(task: Dict[str, Any], user: Dict[str, Any]) -> bool:
    """更新任务：admin / 项目 owner / leader / 任务创建人 / 任务负责人。"""
    if _is_admin(user):
        return True
    user_id = user["user_id"]
    project_id = task["project_id"]
    if project_repo.is_user_project_owner(project_id, user_id):
        return True
    if project_repo.is_user_project_leader(project_id, user_id):
        return True
    if task.get("creator_id") == user_id:
        return True
    if task.get("assignee_id") == user_id:
        return True
    return False


def _can_delete_task(task: Dict[str, Any], user: Dict[str, Any]) -> bool:
    """删除任务：admin / 项目 owner / leader / 任务创建人。"""
    if _is_admin(user):
        return True
    user_id = user["user_id"]
    project_id = task["project_id"]
    if project_repo.is_user_project_owner(project_id, user_id):
        return True
    if project_repo.is_user_project_leader(project_id, user_id):
        return True
    if task.get("creator_id") == user_id:
        return True
    return False


# =============================================================================
# 任务列表
# =============================================================================

def list_project_tasks(
    token: str,
    project_id: int,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """分页查询项目任务列表（需有权限）。"""
    user = _require_auth(token)

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _can_access_project(project_id, user["user_id"]):
        raise ForbiddenException(message="无权访问此项目")

    if status is not None and status not in VALID_TASK_STATUS:
        raise ValidationException(
            message=f"无效的任务状态: {status}，允许值: {', '.join(VALID_TASK_STATUS)}"
        )

    rows, total = task_repo.list_tasks_for_project(
        project_id=project_id,
        is_admin=_is_admin(user),
        page=page,
        page_size=page_size,
        status=status,
        keyword=keyword,
    )

    return {
        "items": [_task_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# =============================================================================
# 创建任务（事务：INSERT task + INSERT branch + INSERT operation_logs）
# =============================================================================

def create_task(
    token: str,
    project_id: int,
    task_type_id: int,
    title: str,
    description: Optional[str] = None,
    assignee_id: Optional[int] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    create_default_branch: bool = True,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建项目任务，自动创建默认主分支。"""
    user = _require_auth(token)
    user_id = user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _can_create_task(project_id, user):
        raise ForbiddenException(message="无权在此项目创建任务")

    if not title or not title.strip():
        raise ValidationException(message="任务标题不能为空")

    if priority is not None and priority not in VALID_PRIORITY:
        raise ValidationException(
            message=f"无效的优先级: {priority}，允许值: {', '.join(VALID_PRIORITY)}"
        )

    task_id: int = 0
    branch_id: Optional[int] = None

    with get_db_transaction() as conn:
        # 1. 创建任务
        task_id = task_repo.create_task(
            project_id=project_id,
            task_type_id=task_type_id,
            title=title.strip(),
            description=(description.strip() if description else None),
            creator_id=user_id,
            assignee_id=assignee_id,
            priority=priority,
            due_date=due_date,
            conn=conn,
        )

        # 2. 创建默认主分支（主分支名固定为 main）
        if create_default_branch:
            branch_id = task_repo.create_task_branch(
                task_id=task_id,
                project_id=project_id,
                branch_name="main",
                base_output_id=None,
                created_by=user_id,
                conn=conn,
            )

        # 3. 写入操作日志
        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="task:create",
            action_desc=f"创建任务: {title.strip()}",
            target_type="task",
            target_id=task_id,
            project_id=project_id,
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    task = task_repo.get_task_by_id(task_id)
    result = _task_row_to_dict(task)
    if branch_id:
        result["default_branch_id"] = branch_id
    return result


# =============================================================================
# 任务详情
# =============================================================================

def get_task_detail(token: str, task_id: int) -> Dict[str, Any]:
    """获取任务详情（需有权限）。"""
    user = _require_auth(token)

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_access_project(task["project_id"], user["user_id"]):
        raise ForbiddenException(message="无权访问此任务")

    return _task_row_to_dict(task)


# =============================================================================
# 更新任务（事务：UPDATE task + INSERT operation_logs）
# =============================================================================

def update_task(
    token: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """更新任务（需有权限）。"""
    user = _require_auth(token)

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_update_task(task, user):
        raise ForbiddenException(message="无权修改此任务")

    if title is not None and not title.strip():
        raise ValidationException(message="任务标题不能为空")

    if status is not None and status not in VALID_TASK_STATUS:
        raise ValidationException(
            message=f"无效的任务状态: {status}，允许值: {', '.join(VALID_TASK_STATUS)}"
        )

    if priority is not None and priority not in VALID_PRIORITY:
        raise ValidationException(
            message=f"无效的优先级: {priority}，允许值: {', '.join(VALID_PRIORITY)}"
        )

    with get_db_transaction() as conn:
        affected = task_repo.update_task(
            task_id=task_id,
            title=(title.strip() if title else None),
            description=description,
            assignee_id=assignee_id,
            status=status,
            priority=priority,
            due_date=due_date,
            updated_by=user["user_id"],
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="任务不存在或无权更新")

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="task:update",
            action_desc=f"更新任务: {task_id}",
            target_type="task",
            target_id=task_id,
            project_id=task["project_id"],
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    updated = task_repo.get_task_by_id(task_id)
    return _task_row_to_dict(updated)


# =============================================================================
# 删除任务（事务：UPDATE task + INSERT operation_logs）
# =============================================================================

def delete_task(
    token: str,
    task_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """软删除任务（需有权限）。"""
    user = _require_auth(token)

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_delete_task(task, user):
        raise ForbiddenException(message="无权删除此任务")

    with get_db_transaction() as conn:
        affected = task_repo.soft_delete_task(
            task_id=task_id,
            deleted_by=user["user_id"],
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="任务不存在或无权删除")

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="task:delete",
            action_desc=f"删除任务: {task_id}",
            target_type="task",
            target_id=task_id,
            project_id=task["project_id"],
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()


# =============================================================================
# 任务分支列表
# =============================================================================

def list_task_branches(
    token: str,
    task_id: int,
) -> List[Dict[str, Any]]:
    """查询任务分支列表（需有权限）。"""
    user = _require_auth(token)

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_access_project(task["project_id"], user["user_id"]):
        raise ForbiddenException(message="无权访问此任务")

    branches = task_repo.list_task_branches(task_id)
    return [_branch_row_to_dict(b) for b in branches]


# =============================================================================
# 创建任务分支（事务：INSERT branch + INSERT operation_logs）
# =============================================================================

def create_task_branch(
    token: str,
    task_id: int,
    branch_name: str,
    base_output_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建任务分支（需有权限）。"""
    user = _require_auth(token)

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_access_project(task["project_id"], user["user_id"]):
        raise ForbiddenException(message="无权为此任务创建分支")

    if not branch_name or not branch_name.strip():
        raise ValidationException(message="分支名称不能为空")

    if task_repo.is_branch_name_exists_in_task(task_id, branch_name.strip()):
        raise ValidationException(message="该任务下已存在同名分支")

    if base_output_id is not None:
        output = task_repo.get_output_by_id_and_task(base_output_id, task_id)
        if output is None:
            raise ValidationException(message="基准版本不属于当前任务")

    with get_db_transaction() as conn:
        branch_id = task_repo.create_task_branch(
            task_id=task_id,
            project_id=task["project_id"],
            branch_name=branch_name.strip(),
            base_output_id=base_output_id,
            created_by=user["user_id"],
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="task:create_branch",
            action_desc=f"创建任务分支: {branch_name.strip()}",
            target_type="branch",
            target_id=branch_id,
            project_id=task["project_id"],
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    branch = task_repo.get_branch_by_id(branch_id)
    return _branch_row_to_dict(branch)


# =============================================================================
# 输出版本列表
# =============================================================================

def list_task_outputs(
    token: str,
    task_id: int,
) -> List[Dict[str, Any]]:
    """查询任务输出版本列表（需有权限）。"""
    user = _require_auth(token)

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_access_project(task["project_id"], user["user_id"]):
        raise ForbiddenException(message="无权访问此任务")

    outputs = task_repo.list_task_outputs(task_id)
    return [_output_row_to_dict(o) for o in outputs]


# =============================================================================
# 输出版本详情
# =============================================================================

def get_output_detail(token: str, output_id: int) -> Dict[str, Any]:
    """获取输出版本详情（需有权限）。"""
    user = _require_auth(token)

    output = task_repo.get_output_by_id(output_id)
    if output is None:
        raise NotFoundException(message="输出版本不存在")

    task = task_repo.get_task_by_id(output["task_id"])
    if task is None:
        raise NotFoundException(message="关联任务不存在")

    if not _can_access_project(task["project_id"], user["user_id"]):
        raise ForbiddenException(message="无权访问此输出版本")

    return _output_detail_to_dict(output)


# =============================================================================
# 输出版本时间线
# =============================================================================

def get_output_timeline(token: str, output_id: int) -> List[Dict[str, Any]]:
    """
    获取输出版本时间线（基于 parent_output_id）。

    优先使用 MySQL WITH RECURSIVE CTE 实现递归查询。
    """
    user = _require_auth(token)

    output = task_repo.get_output_by_id(output_id)
    if output is None:
        raise NotFoundException(message="输出版本不存在")

    task = task_repo.get_task_by_id(output["task_id"])
    if task is None:
        raise NotFoundException(message="关联任务不存在")

    if not _can_access_project(task["project_id"], user["user_id"]):
        raise ForbiddenException(message="无权访问此输出版本")

    from app.database import get_db_cursor

    timeline_sql = """
        WITH RECURSIVE output_tree AS (
            -- 基础版本：从最早的没有父版本的版本开始（parent_output_id IS NULL）
            SELECT o.output_id, o.parent_output_id, o.version_no,
                   o.output_title, o.source_type, o.created_by,
                   o.created_at, 0 AS depth
            FROM task_outputs o
            WHERE o.task_id = %s
              AND o.is_deleted = 0
              AND o.parent_output_id IS NULL

            UNION ALL

            -- 递归：找到子版本
            SELECT o.output_id, o.parent_output_id, o.version_no,
                   o.output_title, o.source_type, o.created_by,
                   o.created_at, ot.depth + 1
            FROM task_outputs o
            INNER JOIN output_tree ot ON o.parent_output_id = ot.output_id
            WHERE o.task_id = %s
              AND o.is_deleted = 0
        )
        SELECT ot.output_id, ot.parent_output_id, ot.version_no,
               ot.output_title, ot.source_type,
               ot.created_by, ot.created_at, ot.depth,
               u.username AS creator_username, u.real_name AS creator_real_name
        FROM output_tree ot
        LEFT JOIN users u ON ot.created_by = u.user_id AND u.is_deleted = 0
        ORDER BY ot.depth ASC, ot.created_at ASC
    """

    with get_db_cursor() as cursor:
        cursor.execute(timeline_sql, (output["task_id"], output["task_id"]))
        rows = cursor.fetchall()

    return [_timeline_item_to_dict(r) for r in rows]


# =============================================================================
# 创建人工输出版本（事务：INSERT output + INSERT operation_logs）
# =============================================================================

def create_manual_output(
    token: str,
    task_id: int,
    output_title: str,
    content: str,
    branch_id: Optional[int] = None,
    parent_output_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建人工输出版本。"""
    user = _require_auth(token)
    user_id = user["user_id"]

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    if not _can_access_project(task["project_id"], user_id):
        raise ForbiddenException(message="无权为此任务创建输出版本")

    if not output_title or not output_title.strip():
        raise ValidationException(message="版本标题不能为空")

    # 校验分支
    if branch_id is not None:
        branch = task_repo.get_branch_by_id_and_task(branch_id, task_id)
        if branch is None:
            raise ValidationException(message="分支不属于当前任务")

    # 校验父版本
    if parent_output_id is not None:
        parent = task_repo.get_output_by_id_and_task(parent_output_id, task_id)
        if parent is None:
            raise ValidationException(message="父版本不属于当前任务")
        source_type = "hybrid"
    else:
        source_type = "manual_edit"

    # 生成版本号
    next_version = task_repo.get_next_version_no(task_id, branch_id)

    with get_db_transaction() as conn:
        output_id = task_repo.create_manual_output(
            task_id=task_id,
            branch_id=branch_id,
            version_no=next_version,
            output_title=output_title.strip(),
            content=content,
            source_type=source_type,
            parent_output_id=parent_output_id,
            created_by=user_id,
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="task:create_output",
            action_desc=f"创建人工输出版本: {output_title.strip()}",
            target_type="output",
            target_id=output_id,
            project_id=task["project_id"],
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    output = task_repo.get_output_by_id(output_id)
    return _output_detail_to_dict(output)


# =============================================================================
# 数据转换辅助函数
# =============================================================================

def _task_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "task_id": row["task_id"],
        "project_id": row["project_id"],
        "project_name": row.get("project_name"),
        "task_type_id": row.get("task_type_id"),
        "type_name": row.get("type_name"),
        "type_code": row.get("type_code"),
        "title": row["title"],
        "description": row.get("description"),
        "creator_id": row.get("creator_id"),
        "creator_username": row.get("creator_username"),
        "creator_real_name": row.get("creator_real_name"),
        "assignee_id": row.get("assignee_id"),
        "assignee_username": row.get("assignee_username"),
        "assignee_real_name": row.get("assignee_real_name"),
        "status": row["status"],
        "priority": row.get("priority"),
        "due_date": row.get("due_date"),
        "created_at": row["created_at"],
        "created_by": row.get("created_by"),
        "updated_at": row.get("updated_at"),
        "updated_by": row.get("updated_by"),
    }


def _branch_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "branch_id": row["branch_id"],
        "project_id": row["project_id"],
        "task_id": row["task_id"],
        "branch_name": row["branch_name"],
        "base_output_id": row.get("base_output_id"),
        "base_output_title": row.get("base_output_title"),
        "status": row["status"],
        "creator_username": row.get("creator_username"),
        "creator_real_name": row.get("creator_real_name"),
        "created_at": row.get("created_at"),
        "created_by": row.get("created_by"),
    }


def _output_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """输出版本列表（不含 content）。"""
    if row is None:
        return {}
    return {
        "output_id": row["output_id"],
        "task_id": row["task_id"],
        "branch_id": row.get("branch_id"),
        "branch_name": row.get("branch_name"),
        "version_no": row["version_no"],
        "output_title": row["output_title"],
        "source_type": row["source_type"],
        "parent_output_id": row.get("parent_output_id"),
        "is_final_candidate": row.get("is_final_candidate"),
        "status": row.get("status"),
        "creator_username": row.get("creator_username"),
        "creator_real_name": row.get("creator_real_name"),
        "created_at": row.get("created_at"),
        "created_by": row.get("created_by"),
    }


def _output_detail_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """输出版本详情（含 content）。"""
    if row is None:
        return {}
    result = _output_row_to_dict(row)
    result["content"] = row.get("content")
    result["lock_version"] = row.get("lock_version")
    result["last_modified_at"] = row.get("last_modified_at")
    result["last_modified_by"] = row.get("last_modified_by")
    result["edit_summary"] = row.get("edit_summary")
    result["task_title"] = row.get("task_title")
    return result


def _timeline_item_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "output_id": row["output_id"],
        "parent_output_id": row.get("parent_output_id"),
        "version_no": row["version_no"],
        "output_title": row["output_title"],
        "source_type": row["source_type"],
        "creator_username": row.get("creator_username"),
        "creator_real_name": row.get("creator_real_name"),
        "created_at": row.get("created_at"),
        "created_by": row.get("created_by"),
        "depth": row.get("depth", 0),
    }
