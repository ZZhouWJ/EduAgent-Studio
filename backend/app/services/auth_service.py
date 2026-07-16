"""
认证 Service 层。

处理登录、登出、Token 生成与解析、用户注册。
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Header

from app.repositories import user_repo
from app.utils.exceptions import ConflictException, ForbiddenException, UnauthorizedException, ValidationException
from app.utils.password import get_password_policy_error, hash_password, verify_password
from app.utils.roles import (
    PLATFORM_ROLE_CODES,
    PUBLIC_REGISTRATION_ROLE_CODES,
    filter_platform_roles,
    permissions_for_roles,
)
from app.utils.token import create_access_token, decode_access_token


MAX_FAILED_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW_MINUTES = 15


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
    username = username.strip()
    failed_since = datetime.now() - timedelta(minutes=LOGIN_ATTEMPT_WINDOW_MINUTES)
    failed_attempts = user_repo.count_recent_failed_login_attempts(
        username=username,
        since=failed_since,
    )
    if failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        user_repo.insert_login_log(
            user_id=None,
            username=username,
            login_status="failed",
            failure_reason="登录尝试过于频繁",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return {
            "success": False,
            "reason": "登录尝试过多，请 15 分钟后重试",
            "rate_limited": True,
            "retry_after_seconds": LOGIN_ATTEMPT_WINDOW_MINUTES * 60,
        }

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
    if not user or user.get("status") != "active":
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
    role_ids: Optional[list[int]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    created_by: Optional[int] = None,
    allow_admin_role: bool = False,
) -> Dict[str, Any]:
    """
    用户注册（事务保证 users/user_roles/operation_logs 原子性）。

    流程：
    1. 校验两次密码一致
    2. 校验参数（username 非空，password 符合统一安全策略）
    3. 检查用户名是否已存在
    4. 校验角色是否符合注册来源的授权范围
    5. bcrypt 哈希密码
    6. 在同一事务内：创建用户 -> 分配角色 -> 写入操作日志
    7. 事务失败整体回滚

    Args:
        username: 用户名
        password: 明文密码（至少 8 字符且不超过 bcrypt 字节上限）
        confirm_password: 确认密码（必须与 password 一致）
        real_name: 真实姓名
        student_no: 学号（可选）
        email: 邮箱（可选）
        phone: 手机号（可选）
        role_ids: 公开注册仅允许学生角色；管理员创建时可指定平台角色
        ip_address: 客户端 IP
        user_agent: 客户端 UA

    Returns:
        新用户信息（不含 password_hash）
    """
    if password != confirm_password:
        raise ValidationException(message="两次输入的密码不一致")

    if not username or not username.strip():
        raise ValidationException(message="用户名不能为空")

    password_error = get_password_policy_error(password)
    if password_error:
        raise ValidationException(message=password_error)

    if not real_name or not real_name.strip():
        raise ValidationException(message="真实姓名不能为空")

    username = username.strip()
    real_name = real_name.strip()

    if user_repo.check_username_exists(username):
        raise ConflictException(message="用户名已存在")

    if role_ids is not None:
        allowed_role_codes = (
            PLATFORM_ROLE_CODES
            if allow_admin_role
            else PUBLIC_REGISTRATION_ROLE_CODES
        )
        _validate_role_ids_for_user(role_ids, allowed_role_codes)

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
            created_by=created_by,
        )

        user_repo.assign_roles_with_conn(
            conn=conn,
            user_id=user_id,
            role_ids=role_ids,
        )

        user_repo.insert_operation_log_with_conn(
            conn=conn,
            user_id=created_by or user_id,
            action_type="user:create" if created_by else "register",
            action_desc=f"创建用户: {username}" if created_by else f"用户注册: {username}",
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
    3. 校验新密码安全策略
    4. 哈希新密码并更新

    Args:
        token: 当前用户的 JWT token
        old_password: 旧密码
        new_password: 新密码（至少 8 字符且不超过 bcrypt 字节上限）

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

    password_error = get_password_policy_error(new_password)
    if password_error:
        raise ValidationException(message=password_error)

    new_hash = hash_password(new_password)
    user_repo.update_password(user_id, new_hash)


def list_roles_public() -> list[dict]:
    """获取公开注册可选角色；当前仅允许学生。"""
    return [
        role
        for role in filter_platform_roles(user_repo.list_roles(include_admin=False))
        if role["role_code"] in PUBLIC_REGISTRATION_ROLE_CODES
    ]


# =============================================================================
# 用户自主角色与资料管理
# =============================================================================

def _validate_role_ids_for_user(
    role_ids: list[int], allowed_role_codes: frozenset[str]
) -> None:
    """
    校验角色存在且属于当前操作允许分配的角色集合。

    Raises:
        ValidationException: 角色不存在或超出可分配范围
    """
    all_roles = user_repo.list_roles()
    roles_by_id = {int(role["role_id"]): role for role in all_roles}
    for rid in role_ids:
        role = roles_by_id.get(int(rid))
        if role is None:
            raise ValidationException(message="选择的角色不存在")
        if role.get("status", "active") != "active":
            raise ValidationException(message="选择的角色已停用")
        if role["role_code"] not in allowed_role_codes:
            raise ValidationException(message="无法分配该角色")


def update_my_profile(
    token: str,
    real_name: str,
    student_no: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    当前用户修改自己的基本信息（用户名不可修改）。

    Args:
        token: 当前用户的 JWT token
        real_name: 真实姓名
        student_no: 学号（可选）
        email: 邮箱（可选）
        phone: 手机号（可选）
        ip_address: 客户端 IP
        user_agent: 客户端 UA

    Returns:
        更新后的用户信息
    """
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")

    if not real_name or not real_name.strip():
        raise ValidationException(message="真实姓名不能为空")

    user_id = user["user_id"]

    updated = user_repo.update_user_profile(
        user_id=user_id,
        real_name=real_name.strip(),
        student_no=(student_no.strip() if student_no else None),
        email=(email.strip() if email else None),
        phone=(phone.strip() if phone else None),
    )

    if not updated:
        raise UnauthorizedException(message="用户不存在或无权更新")

    user_repo.insert_operation_log(
        user_id=user_id,
        action_type="profile:update",
        action_desc="更新个人基本信息",
        target_type="user",
        target_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return {
        "user_id": user_id,
        "real_name": real_name.strip(),
        "student_no": (student_no.strip() if student_no else None),
        "email": (email.strip() if email else None),
        "phone": (phone.strip() if phone else None),
    }


def update_my_roles(
    token: str,
    role_ids: list[int],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    拒绝用户自行修改角色。

    Args:
        token: 当前用户的 JWT token
        role_ids: 客户端请求的角色 ID 列表（不会执行修改）
        ip_address: 客户端 IP
        user_agent: 客户端 UA

    Raises:
        UnauthorizedException: 未登录或 token 无效
        ForbiddenException: 当前用户无权修改自己的角色
    """
    if get_current_user(token) is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")
    raise ForbiddenException(message="角色只能由系统管理员分配")


def _extract_token_from_header(authorization: str) -> str:
    """从 Authorization: Bearer <token> 提取 token。"""
    if not authorization:
        return ""
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() in ("bearer", "token"):
        return parts[1]
    return authorization


def get_current_user_dependency(authorization: Optional[str] = Header(None, alias="Authorization")) -> Dict[str, Any]:
    """
    FastAPI 依赖：从 Authorization: Bearer <token> 提取并验证用户。

    用法（路由函数参数）：
        @router.get("/xxx")
        async def xxx(user: dict = Depends(get_current_user_dependency)):
            ...

    FastAPI 会自动从请求头注入 authorization 参数。
    """
    token = _extract_token_from_header(authorization or "")
    if not token:
        raise UnauthorizedException("缺少认证信息")
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException("Token 无效或已过期")
    return user
