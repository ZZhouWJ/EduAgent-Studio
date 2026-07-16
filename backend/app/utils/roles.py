"""平台角色常量与校验辅助。"""

PLATFORM_ROLE_CODES = frozenset({"student_member", "teacher", "admin"})
PUBLIC_REGISTRATION_ROLE_CODES = frozenset({"student_member"})


def filter_platform_roles(roles: list[dict]) -> list[dict]:
    """只返回当前教育平台实际支持的角色。"""
    return [role for role in roles if role.get("role_code") in PLATFORM_ROLE_CODES]
