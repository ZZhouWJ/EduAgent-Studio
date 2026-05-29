"""
项目 Service 层。

处理项目与项目成员相关业务逻辑。
复用 auth_service.get_current_user() 和 user_repo 中的工具。
"""

from typing import Any, Dict, List, Optional

from app.repositories import project_repo, user_repo
from app.utils.exceptions import (
    AppException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)

# 允许的项目成员角色
VALID_PROJECT_ROLES = {"member", "leader", "reviewer", "teacher"}
# 允许的项目状态
VALID_PROJECT_STATUS = {"active", "archived", "suspended"}


def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户，失败抛出 Unauthorized。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise ForbiddenException(message="未登录或登录已过期")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def _is_project_manager(project_id: int, user_id: int) -> bool:
    """判断用户是否有权管理指定项目（admin 或 owner 或 leader）。"""
    if user_repo.is_admin(user_id):
        return True
    return (
        project_repo.is_user_project_owner(project_id, user_id) or
        project_repo.is_user_project_leader(project_id, user_id)
    )


def _can_access_project(project_id: int, user: Dict[str, Any]) -> bool:
    """判断用户是否有权访问指定项目。"""
    user_id = user["user_id"]
    if _is_admin(user):
        return True
    return project_repo.is_user_in_project(project_id, user_id)


# =============================================================================
# 项目列表
# =============================================================================

def list_projects(
    token: str,
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    分页查询项目列表（按权限过滤）。

    Args:
        token: JWT token
        page: 页码
        page_size: 每页条数
        keyword: 搜索关键字
        status: 项目状态过滤

    Returns:
        {"items": [...], "total": N, "page": ..., "page_size": ...}
    """
    user = _require_auth(token)
    user_id = user["user_id"]
    is_admin = _is_admin(user)
    is_teacher = "teacher" in user.get("roles", [])

    # 校验 status 参数
    if status is not None and status not in VALID_PROJECT_STATUS:
        raise ValidationException(
            message=f"无效的项目状态: {status}，允许值: {', '.join(VALID_PROJECT_STATUS)}"
        )

    rows, total = project_repo.list_projects_for_user(
        user_id=user_id,
        is_admin=is_admin,
        is_teacher=is_teacher,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )

    items = [_project_row_to_dict(r) for r in rows]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# =============================================================================
# 项目创建
# =============================================================================

def create_project(
    token: str,
    project_name: str,
    project_type: str,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建项目。

    自动将创建人写入 project_members（角色为 leader）。
    写入 operation_logs。

    Returns:
        新项目详情 dict
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    if not project_name or not project_name.strip():
        raise ValidationException(message="项目名称不能为空")

    project_id = project_repo.create_project(
        project_name=project_name.strip(),
        project_type=project_type,
        description=(description.strip() if description else None),
        owner_id=user_id,
        created_by=user_id,
    )

    user_repo.insert_operation_log(
        user_id=user_id,
        action_type="project:create",
        action_desc=f"创建项目: {project_name.strip()}",
        target_type="project",
        target_id=project_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    project = project_repo.get_project_by_id(project_id)
    return _project_row_to_dict(project)


# =============================================================================
# 项目详情
# =============================================================================

def get_project_detail(
    token: str,
    project_id: int,
) -> Dict[str, Any]:
    """获取项目详情（需有权限）。"""
    user = _require_auth(token)

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _can_access_project(project_id, user):
        raise ForbiddenException(message="无权访问此项目")

    return _project_row_to_dict(project)


# =============================================================================
# 项目更新
# =============================================================================

def update_project(
    token: str,
    project_id: int,
    project_name: Optional[str] = None,
    project_type: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """更新项目（仅 admin/owner/leader 可操作）。"""
    user = _require_auth(token)
    user_id = user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _is_project_manager(project_id, user_id):
        raise ForbiddenException(message="无权修改此项目")

    if project_name is not None and not project_name.strip():
        raise ValidationException(message="项目名称不能为空")

    if status is not None and status not in VALID_PROJECT_STATUS:
        raise ValidationException(
            message=f"无效的项目状态: {status}，允许值: {', '.join(VALID_PROJECT_STATUS)}"
        )

    project_repo.update_project(
        project_id=project_id,
        project_name=(project_name.strip() if project_name else None),
        project_type=project_type,
        description=description,
        status=status,
        updated_by=user_id,
    )

    user_repo.insert_operation_log(
        user_id=user_id,
        action_type="project:update",
        action_desc=f"更新项目: {project_id}",
        target_type="project",
        target_id=project_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    updated = project_repo.get_project_by_id(project_id)
    return _project_row_to_dict(updated)


# =============================================================================
# 项目软删除
# =============================================================================

def delete_project(
    token: str,
    project_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """软删除项目（仅 admin/owner/leader 可操作）。"""
    user = _require_auth(token)
    user_id = user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _is_project_manager(project_id, user_id):
        raise ForbiddenException(message="无权删除此项目")

    project_repo.soft_delete_project(project_id=project_id, deleted_by=user_id)

    user_repo.insert_operation_log(
        user_id=user_id,
        action_type="project:delete",
        action_desc=f"删除项目: {project_id}",
        target_type="project",
        target_id=project_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


# =============================================================================
# 项目归档
# =============================================================================

def archive_project(
    token: str,
    project_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """归档项目（仅 admin/owner/leader 可操作）。"""
    user = _require_auth(token)
    user_id = user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _is_project_manager(project_id, user_id):
        raise ForbiddenException(message="无权归档此项目")

    if project["status"] == "archived":
        raise ValidationException(message="项目已归档")

    project_repo.archive_project(project_id=project_id, updated_by=user_id)

    user_repo.insert_operation_log(
        user_id=user_id,
        action_type="project:archive",
        action_desc=f"归档项目: {project_id}",
        target_type="project",
        target_id=project_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    updated = project_repo.get_project_by_id(project_id)
    return _project_row_to_dict(updated)


# =============================================================================
# 项目成员管理
# =============================================================================

def list_project_members(
    token: str,
    project_id: int,
) -> List[Dict[str, Any]]:
    """查询项目成员列表（需有权限）。"""
    user = _require_auth(token)

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _can_access_project(project_id, user):
        raise ForbiddenException(message="无权访问此项目")

    members = project_repo.list_project_members(project_id)
    return [_member_row_to_dict(m) for m in members]


def add_project_member(
    token: str,
    project_id: int,
    user_id: int,
    project_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """添加项目成员（仅 admin/owner/leader 可操作）。"""
    current_user = _require_auth(token)
    current_user_id = current_user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _is_project_manager(project_id, current_user_id):
        raise ForbiddenException(message="无权添加项目成员")

    if project_role not in VALID_PROJECT_ROLES:
        raise ValidationException(
            message=f"无效的角色: {project_role}，允许值: {', '.join(VALID_PROJECT_ROLES)}"
        )

    # 检查目标用户是否存在
    target_user = user_repo.get_user_by_id(user_id)
    if target_user is None:
        raise NotFoundException(message="要添加的用户不存在")

    # 检查是否已存在未删除成员
    existing = project_repo.get_project_member_by_user(project_id, user_id)
    if existing is not None:
        raise ValidationException(message="该用户已是项目成员")

    member_id = project_repo.add_project_member(
        project_id=project_id,
        user_id=user_id,
        project_role=project_role,
        created_by=current_user_id,
    )

    user_repo.insert_operation_log(
        user_id=current_user_id,
        action_type="project:add_member",
        action_desc=f"添加项目成员: user_id={user_id}, role={project_role}",
        target_type="project_member",
        target_id=member_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    member = project_repo.get_project_member(project_id, member_id)
    return _member_row_to_dict(member)


def update_project_member_role(
    token: str,
    project_id: int,
    member_id: int,
    project_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """修改项目成员角色（仅 admin/owner/leader 可操作）。"""
    current_user = _require_auth(token)
    current_user_id = current_user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _is_project_manager(project_id, current_user_id):
        raise ForbiddenException(message="无权修改项目成员角色")

    if project_role not in VALID_PROJECT_ROLES:
        raise ValidationException(
            message=f"无效的角色: {project_role}，允许值: {', '.join(VALID_PROJECT_ROLES)}"
        )

    member = project_repo.get_project_member(project_id, member_id)
    if member is None:
        raise NotFoundException(message="项目成员不存在")

    # 禁止将 owner 对应的成员角色降级为 member
    if member["user_id"] == project["owner_id"] and project_role != "leader":
        raise ForbiddenException(message="不能修改项目所有者的成员角色")

    project_repo.update_project_member_role(
        member_id=member_id,
        project_role=project_role,
        updated_by=current_user_id,
    )

    user_repo.insert_operation_log(
        user_id=current_user_id,
        action_type="project:update_member",
        action_desc=f"修改项目成员角色: member_id={member_id}, role={project_role}",
        target_type="project_member",
        target_id=member_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    updated = project_repo.get_project_member(project_id, member_id)
    return _member_row_to_dict(updated)


def remove_project_member(
    token: str,
    project_id: int,
    member_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """移除项目成员（仅 admin/owner/leader 可操作，软删除）。"""
    current_user = _require_auth(token)
    current_user_id = current_user["user_id"]

    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise NotFoundException(message="项目不存在")

    if not _is_project_manager(project_id, current_user_id):
        raise ForbiddenException(message="无权移除项目成员")

    member = project_repo.get_project_member(project_id, member_id)
    if member is None:
        raise NotFoundException(message="项目成员不存在")

    # 禁止移除 owner
    if member["user_id"] == project["owner_id"]:
        raise ForbiddenException(message="不能移除项目所有者")

    project_repo.soft_delete_project_member(
        member_id=member_id,
        deleted_by=current_user_id,
    )

    user_repo.insert_operation_log(
        user_id=current_user_id,
        action_type="project:remove_member",
        action_desc=f"移除项目成员: member_id={member_id}",
        target_type="project_member",
        target_id=member_id,
        project_id=project_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


# =============================================================================
# 数据转换辅助函数
# =============================================================================

def _project_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """将项目数据库行转为 API 响应 dict。"""
    if row is None:
        return {}
    return {
        "project_id": row["project_id"],
        "project_name": row["project_name"],
        "project_type": row["project_type"],
        "description": row["description"],
        "owner_id": row["owner_id"],
        "owner_username": row.get("owner_username"),
        "owner_real_name": row.get("owner_real_name"),
        "status": row["status"],
        "created_at": row["created_at"],
        "created_by": row.get("created_by"),
        "updated_at": row.get("updated_at"),
        "updated_by": row.get("updated_by"),
    }


def _member_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """将项目成员数据库行转为 API 响应 dict。"""
    if row is None:
        return {}
    return {
        "member_id": row["member_id"],
        "project_id": row["project_id"],
        "user_id": row["user_id"],
        "username": row.get("username"),
        "real_name": row.get("real_name"),
        "email": row.get("email"),
        "phone": row.get("phone"),
        "project_role": row["project_role"],
        "joined_at": row.get("joined_at"),
        "status": row.get("status"),
        "created_at": row.get("created_at"),
        "created_by": row.get("created_by"),
    }
