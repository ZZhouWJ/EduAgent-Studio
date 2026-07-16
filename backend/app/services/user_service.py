"""
用户 Service 层。

处理用户、角色、权限相关业务逻辑。
"""

from typing import Any, Dict, List, Optional, Tuple

from app.repositories import user_repo
from app.utils.exceptions import NotFoundException, ValidationException
from app.utils.roles import (
    PLATFORM_ROLE_CODES,
    filter_platform_roles,
    list_platform_capabilities,
    permissions_for_roles,
)


def get_user_detail(user_id: int) -> Optional[Dict[str, Any]]:
    """
    获取用户详情（不含 password_hash）。

    Args:
        user_id: 用户 ID

    Returns:
        用户信息 dict 或 None
    """
    user = user_repo.get_user_by_id(user_id)
    if not user:
        return None

    roles = user_repo.get_user_roles(user_id)
    permissions = permissions_for_roles(roles)

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "real_name": user["real_name"],
        "student_no": user["student_no"],
        "email": user["email"],
        "phone": user["phone"],
        "status": user["status"],
        "last_login_at": user.get("last_login_at"),
        "created_at": user["created_at"],
        "roles": roles,
        "permissions": permissions,
    }


def list_users_service(
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    分页查询用户列表。

    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        keyword: 搜索关键字
        status: 按状态过滤（active/inactive/suspended）

    Returns:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "page_size": 10
        }
    """
    rows, total = user_repo.list_users(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )

    items = []
    for row in rows:
        item = {
            "user_id": row["user_id"],
            "username": row["username"],
            "real_name": row["real_name"],
            "student_no": row["student_no"],
            "email": row["email"],
            "phone": row["phone"],
            "status": row["status"],
            "last_login_at": row.get("last_login_at"),
            "created_at": row["created_at"],
            "roles": user_repo.get_user_roles(row["user_id"]),
        }
        items.append(item)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def update_user_status_service(
    user_id: int,
    new_status: str,
    actor_user_id: int,
) -> None:
    """
    更新用户状态。

    Args:
        user_id: 要更新的用户 ID
        new_status: 新状态（active/inactive/suspended）
    """
    valid_statuses = {"active", "disabled"}
    if new_status not in valid_statuses:
        raise ValidationException(
            message=f"无效的状态: {new_status}，允许值: {', '.join(valid_statuses)}"
        )

    target = user_repo.get_user_by_id(user_id)
    if not target:
        raise NotFoundException(message="用户不存在")
    if new_status == "disabled":
        if user_id == actor_user_id:
            raise ValidationException(message="不能停用当前登录账号")
        if (
            "admin" in user_repo.get_user_roles(user_id)
            and user_repo.count_active_users_with_role("admin") <= 1
        ):
            raise ValidationException(message="平台必须保留至少一个启用的管理员")

    affected = user_repo.update_user_status(user_id, new_status)
    if affected == 0:
        raise NotFoundException(message="用户不存在或无权更新")


def update_user_roles_service(
    user_id: int,
    role_ids: List[int],
    actor_user_id: int,
) -> None:
    """
    更新用户角色。

    Args:
        user_id: 要更新的用户 ID
        role_ids: 新的角色 ID 列表
    """
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise NotFoundException(message="用户不存在")

    roles_by_id = {
        int(role["role_id"]): role for role in filter_platform_roles(user_repo.list_roles())
    }
    if not role_ids:
        raise ValidationException(message="用户至少需要一个角色")
    new_role_codes = set()
    for role_id in role_ids:
        role = roles_by_id.get(int(role_id))
        if (
            role is None
            or role.get("status", "active") != "active"
            or role["role_code"] not in PLATFORM_ROLE_CODES
        ):
            raise ValidationException(message="选择的角色不存在或不可分配")
        new_role_codes.add(role["role_code"])

    current_role_codes = set(user_repo.get_user_roles(user_id))
    removes_admin = "admin" in current_role_codes and "admin" not in new_role_codes
    if removes_admin and user_id == actor_user_id:
        raise ValidationException(message="不能移除当前登录账号的管理员角色")
    if removes_admin and user_repo.count_active_users_with_role("admin") <= 1:
        raise ValidationException(message="平台必须保留至少一个启用的管理员")

    user_repo.update_user_roles(user_id, role_ids)


def list_roles_service() -> List[Dict[str, Any]]:
    """
    获取角色列表。

    Returns:
        角色列表
    """
    return filter_platform_roles(user_repo.list_roles())


def list_permissions_service() -> List[Dict[str, Any]]:
    """
    获取权限列表。

    Returns:
        权限列表
    """
    return list_platform_capabilities()


def get_user_roles_service(user_id: int) -> List[str]:
    """获取用户角色代码列表。"""
    return user_repo.get_user_roles(user_id)


def get_user_permissions_service(user_id: int) -> List[str]:
    """获取用户在当前教育平台中的能力代码列表。"""
    return permissions_for_roles(user_repo.get_user_roles(user_id))


def list_operation_logs_service(
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
        user_id: 按用户 ID 过滤
        target_type: 按目标类型过滤
        action_type: 按操作类型过滤
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        {"items": [...], "total": int, "page": int, "page_size": int}
    """
    result = user_repo.list_operation_logs(
        page=page,
        page_size=page_size,
        user_id=user_id,
        target_type=target_type,
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
    )
    return {
        "items": result["items"],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }


def list_login_logs_service(
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
        user_id: 按用户 ID 过滤
        login_status: 按登录状态过滤
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        {"items": [...], "total": int, "page": int, "page_size": int}
    """
    result = user_repo.list_login_logs(
        page=page,
        page_size=page_size,
        user_id=user_id,
        login_status=login_status,
        start_date=start_date,
        end_date=end_date,
    )
    return {
        "items": result["items"],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }
