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


def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise ForbiddenException(message="未登录或登录已过期")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def get_overview(token: str) -> Dict[str, Any]:
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]
    stats = statistics_repo.get_overview_stats(is_admin, user_id)
    return stats


def list_project_stats(
    token: str,
    project_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    user = _require_auth(token)
    is_admin = _is_admin(user)
    user_id = user["user_id"]

    if project_id is not None:
        can_access = statistics_repo.check_user_can_access_project(project_id, user_id, is_admin)
        if not can_access:
            raise ForbiddenException(message="无权访问该项目统计")
        return [statistics_repo.get_project_stats_by_id(project_id)] if statistics_repo.get_project_stats_by_id(project_id) else []

    return statistics_repo.list_project_stats(is_admin, user_id)


def get_model_call_stats(
    token: str,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
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


def get_cost_stats(
    token: str,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Dict[str, Any]:
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


def get_review_stats(
    token: str,
    project_id: Optional[int] = None,
) -> Dict[str, Any]:
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


def get_member_contribution_stats(
    token: str,
    project_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
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


def get_recent_activities(
    token: str,
    project_id: Optional[int] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
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


def _validate_date(date_str: str, field_name: str) -> None:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationException(
            message=f"{field_name} 格式错误，应为 YYYY-MM-DD，例如 2025-01-15"
        )


# =============================================================================
# A3 学习分析统计
# =============================================================================

_learning_repo = None


def _get_learning_repo():
    global _learning_repo
    if _learning_repo is None:
        from app.repositories.statistics_learning_repo import StatisticsLearningRepository
        _learning_repo = StatisticsLearningRepository()
    return _learning_repo


def get_learning_overview(user_token: str) -> dict:
    _require_auth(user_token)
    return _get_learning_repo().get_overview()


def get_mastery_distribution(user_token: str) -> list[dict]:
    _require_auth(user_token)
    return _get_learning_repo().get_mastery_distribution()


def get_weak_knowledge_points(user_token: str, top_n: int = 10) -> list[dict]:
    _require_auth(user_token)
    return _get_learning_repo().get_weak_knowledge_points(top_n)


def get_resource_type_distribution(user_token: str) -> list[dict]:
    _require_auth(user_token)
    return _get_learning_repo().get_resource_type_distribution()


def get_invocation_trend(user_token: str, days: int = 14) -> list[dict]:
    _require_auth(user_token)
    return _get_learning_repo().get_invocation_trend(days)


def get_review_rate_by_course(user_token: str) -> list[dict]:
    _require_auth(user_token)
    return _get_learning_repo().get_review_rate_by_course()


def get_cost_distribution(user_token: str) -> list[dict]:
    _require_auth(user_token)
    return _get_learning_repo().get_cost_distribution()


# =============================================================================
# Module 8: 平台全局统计 (管理端指标真实化)
# =============================================================================

def get_platform_overview(token: str) -> Dict[str, Any]:
    """平台总览"""
    _require_auth(token)
    return statistics_repo.get_platform_stats()


def get_cost_by_model_api(token: str) -> List[Dict[str, Any]]:
    """按模型成本 (Module 8)"""
    _require_auth(token)
    return statistics_repo.get_cost_by_model()


def get_resource_stats_api(token: str) -> Dict[str, Any]:
    """资源统计 (Module 8)"""
    _require_auth(token)
    return statistics_repo.get_resource_stats()
