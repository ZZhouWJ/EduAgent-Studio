"""
用户 Service 层。

处理用户、角色、权限相关业务逻辑。
"""

from typing import Any, Dict, List, Optional, Tuple

from app.repositories import user_repo


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
    permissions = user_repo.get_user_permissions(user_id)

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
) -> Dict[str, Any]:
    """
    分页查询用户列表。

    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        keyword: 搜索关键字

    Returns:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "page_size": 10
        }
    """
    rows, total = user_repo.list_users(page=page, page_size=page_size, keyword=keyword)

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


def list_roles_service() -> List[Dict[str, Any]]:
    """
    获取角色列表。

    Returns:
        角色列表
    """
    return user_repo.list_roles()


def list_permissions_service() -> List[Dict[str, Any]]:
    """
    获取权限列表。

    Returns:
        权限列表
    """
    return user_repo.list_permissions()


def get_user_roles_service(user_id: int) -> List[str]:
    """获取用户角色代码列表。"""
    return user_repo.get_user_roles(user_id)


def get_user_permissions_service(user_id: int) -> List[str]:
    """获取用户权限代码列表。"""
    return user_repo.get_user_permissions(user_id)
