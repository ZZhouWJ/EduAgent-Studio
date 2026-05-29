"""
认证 Service 层。

处理登录、登出、Token 生成与解析。
"""

from typing import Any, Dict, Optional

from app.repositories import user_repo
from app.utils.password import verify_password
from app.utils.token import create_access_token, decode_access_token


def login(
    username: str,
    password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    用户登录。

    流程：
    1. 按用户名查询用户
    2. 校验用户状态
    3. 校验密码
    4. 更新最后登录时间
    5. 生成 JWT token
    6. 写入登录日志

    Args:
        username: 用户名
        password: 明文密码
        ip_address: 客户端 IP
        user_agent: 客户端 UA

    Returns:
        成功：{"success": True, "token": "...", "user": {...}}
        失败：{"success": False, "reason": "..."}
    """
    user = user_repo.get_user_by_username(username)

    if user is None:
        user_repo.insert_login_log(
            user_id=None,
            username=username,
            login_status="failed",
            failure_reason="用户名不存在",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return {"success": False, "reason": "用户名或密码错误"}

    if user["status"] != "active":
        user_repo.insert_login_log(
            user_id=user["user_id"],
            username=username,
            login_status="failed",
            failure_reason=f"账户状态异常: {user['status']}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return {"success": False, "reason": "账户已被禁用，请联系管理员"}

    password_correct = verify_password(password, user["password_hash"])
    if not password_correct:
        user_repo.insert_login_log(
            user_id=user["user_id"],
            username=username,
            login_status="failed",
            failure_reason="密码错误",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return {"success": False, "reason": "用户名或密码错误"}

    user_repo.update_user_last_login(user["user_id"])

    roles = user_repo.get_user_roles(user["user_id"])
    token = create_access_token(data={
        "user_id": user["user_id"],
        "username": user["username"],
        "roles": roles,
    })

    user_repo.insert_login_log(
        user_id=user["user_id"],
        username=username,
        login_status="success",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return {
        "success": True,
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "real_name": user["real_name"],
            "roles": roles,
        },
    }


def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    根据 JWT token 获取当前用户信息。

    Args:
        token: JWT 字符串

    Returns:
        用户信息 dict 或 None（token 无效或过期）
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

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
        "roles": roles,
        "permissions": permissions,
    }


def logout(
    user_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    用户登出。

    课程版不实现 token 黑名单，仅写入操作日志。

    Args:
        user_id: 当前用户 ID
        ip_address: 客户端 IP
        user_agent: 客户端 UA
    """
    user_repo.insert_operation_log(
        user_id=user_id,
        action_type="logout",
        action_desc="用户登出",
        ip_address=ip_address,
        user_agent=user_agent,
    )
