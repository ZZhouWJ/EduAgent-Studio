"""
认证 Service 层。

处理登录、登出、Token 生成与解析、用户注册。
"""

from typing import Any, Dict, Optional

from app.repositories import user_repo
from app.utils.exceptions import ConflictException, UnauthorizedException, ValidationException
from app.utils.password import hash_password, verify_password
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


def register(
    username: str,
    password: str,
    confirm_password: str,
    real_name: str,
    student_no: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    用户注册（事务保证 users/user_roles/operation_logs 原子性）。

    流程：
    1. 校验两次密码一致
    2. 校验参数（username 非空，password 至少 6 字符）
    3. 检查用户名是否已存在
    4. bcrypt 哈希密码
    5. 在同一事务内：创建用户 -> 分配默认角色 -> 写入操作日志
    6. 事务失败整体回滚

    Args:
        username: 用户名
        password: 明文密码（至少 6 字符）
        confirm_password: 确认密码（必须与 password 一致）
        real_name: 真实姓名
        student_no: 学号（可选）
        email: 邮箱（可选）
        phone: 手机号（可选）
        ip_address: 客户端 IP
        user_agent: 客户端 UA

    Returns:
        新用户信息（不含 password_hash）
    """
    if password != confirm_password:
        raise ValidationException(message="两次输入的密码不一致")

    if not username or not username.strip():
        raise ValidationException(message="用户名不能为空")

    if not password or len(password) < 6:
        raise ValidationException(message="密码至少需要 6 个字符")

    if not real_name or not real_name.strip():
        raise ValidationException(message="真实姓名不能为空")

    username = username.strip()
    real_name = real_name.strip()

    if user_repo.check_username_exists(username):
        raise ConflictException(message="用户名已存在")

    password_hash = hash_password(password)

    from app.database import get_db_transaction
    with get_db_transaction() as conn:
        user_id = user_repo.create_user_with_conn(
            conn=conn,
            username=username,
            password_hash=password_hash,
            real_name=real_name,
            student_no=(student_no.strip() if student_no else None),
            email=(email.strip() if email else None),
            phone=(phone.strip() if phone else None),
            created_by=None,
        )

        user_repo.assign_default_role_with_conn(conn=conn, user_id=user_id)

        user_repo.insert_operation_log_with_conn(
            conn=conn,
            user_id=user_id,
            action_type="register",
            action_desc=f"用户注册: {username}",
            target_type="user",
            target_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    return {
        "user_id": user_id,
        "username": username,
        "real_name": real_name,
        "student_no": student_no,
        "email": email,
        "phone": phone,
    }


def update_password(
    token: str,
    old_password: str,
    new_password: str,
) -> None:
    """
    更新当前用户密码。

    流程：
    1. 解析 token 获取当前用户
    2. 校验旧密码
    3. 新密码至少 6 字符
    4. 哈希新密码并更新

    Args:
        token: 当前用户的 JWT token
        old_password: 旧密码
        new_password: 新密码（至少 6 字符）

    Raises:
        UnauthorizedException: token 无效或过期
        ValidationException: 旧密码错误或新密码不符合要求
    """
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")

    user_id = user["user_id"]

    user_record = user_repo.get_user_by_id_with_password(user_id)
    if user_record is None:
        raise UnauthorizedException(message="用户不存在")

    if not verify_password(old_password, user_record["password_hash"]):
        raise ValidationException(message="旧密码错误")

    if not new_password or len(new_password) < 6:
        raise ValidationException(message="新密码至少需要 6 个字符")

    new_hash = hash_password(new_password)
    user_repo.update_password(user_id, new_hash)
