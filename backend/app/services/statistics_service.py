"""
统计看板 Service 层。

处理 7 个统计接口的业务逻辑：
1. 首页统计概览
2. 项目统计
3. 模型调用统计
4. 成本统计
5. 审核质量统计
6. 成员贡献统计
7. 最近操作动态

Service 层不直接写 SQL，所有数据操作委托给 repository。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.repositories import statistics_repo
from app.utils.exceptions import ForbiddenException, ValidationException


# =============================================================================
# 权限辅助
# =============================================================================

def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise ForbiddenException(message="未登录或登录已过期")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


# =============================================================================
# 首页统计概览
# GET /api/statistics/overview
# =============================================================================

def get_overview(token: str) -> Dict[str, Any]:
    """
    首页统计概览。

    - admin 返回全局统计
    - 非 admin 返回用户参与项目的范围内统计
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    stats = statistics_repo.get_overview_stats(is_admin, user_id)
    return stats


# =============================================================================
# 项目统计
# GET /api/statistics/projects
# =============================================================================

def list_project_stats(
    token: str,
    project_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    项目维度统计列表。

    - admin 可查看所有项目
    - 非 admin 只能查看自己参与的项目
    - 如指定 project_id，需校验访问权限
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目统计")
        return [statistics_repo.get_project_stats_by_id(project_id)] if statistics_repo.get_project_stats_by_id(project_id) else []

    return statistics_repo.list_project_stats(is_admin, user_id)


# =============================================================================
# 模型调用统计
# GET /api/statistics/model-calls
# =============================================================================

def get_model_call_stats(
    token: str,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    模型调用统计。

    - admin 可查看全部
    - 非 admin 只能查看自己参与项目
    - 如指定 project_id，需校验访问权限
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if date_from:
        _validate_date(date_from, "date_from")
    if date_to:
        _validate_date(date_to, "date_to")

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目统计")

    return statistics_repo.get_model_call_stats(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
    )


# =============================================================================
# 成本统计
# GET /api/statistics/costs
# =============================================================================

def get_cost_stats(
    token: str,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    成本统计。

    - admin 可查看全部
    - 非 admin 只能查看自己参与项目
    - 如指定 project_id，需校验访问权限
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if date_from:
        _validate_date(date_from, "date_from")
    if date_to:
        _validate_date(date_to, "date_to")

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目统计")

    return statistics_repo.get_cost_stats(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
    )


# =============================================================================
# 审核质量统计
# GET /api/statistics/reviews
# =============================================================================

def get_review_stats(
    token: str,
    project_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    审核质量统计。

    - admin 可查看全部
    - 非 admin 只能查看自己参与项目
    - 如指定 project_id，需校验访问权限
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目统计")

    return statistics_repo.get_review_stats(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
    )


# =============================================================================
# 成员贡献统计
# GET /api/statistics/member-contributions
# =============================================================================

def get_member_contribution_stats(
    token: str,
    project_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    成员贡献统计。

    - admin 可查看全部
    - 非 admin 只能查看自己参与项目的成员贡献
    - 如指定 project_id，需校验访问权限
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目统计")

    return statistics_repo.get_member_contribution_stats(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
    )


# =============================================================================
# 最近操作动态
# GET /api/statistics/recent-activities
# =============================================================================

def get_recent_activities(
    token: str,
    project_id: Optional[int] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    最近操作动态。

    - admin 可查看全部
    - 非 admin 只能查看自己参与项目
    - 如指定 project_id，需校验访问权限
    - limit 最大 100
    """
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if limit < 1:
        raise ValidationException(message="limit 必须 >= 1")
    if limit > 100:
        limit = 100

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目操作动态")

    return statistics_repo.get_recent_activities(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
        limit=limit,
    )


# =============================================================================
# 参数校验
# =============================================================================

def _validate_date(date_str: str, field_name: str) -> None:
    """校验日期格式是否为 YYYY-MM-DD。"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationException(
            message=f"{field_name} 格式错误，应为 YYYY-MM-DD，例如 2025-01-15"
        )
