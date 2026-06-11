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


# =============================================================================
# A3 学习分析统计
# =============================================================================

def get_learning_overview(user_token: str) -> dict:
    """
    A3 学习分析概览。
    """
    return {
        "course_count": 3,
        "student_count": 12,
        "resource_count": 47,
        "invocation_count": 156,
        "avg_mastery": 0.52,
        "review_pass_rate": 0.85,
        "feedback_count": 23,
        "active_tasks": 8
    }


def get_mastery_distribution(user_token: str) -> list[dict]:
    """
    学生掌握度分布。
    """
    return [
        {"range": "0-20%", "count": 1},
        {"range": "20-40%", "count": 3},
        {"range": "40-60%", "count": 4},
        {"range": "60-80%", "count": 3},
        {"range": "80-100%", "count": 1},
    ]


def get_weak_knowledge_points(user_token: str, top_n: int = 10) -> list[dict]:
    """
    薄弱知识点 TOP N。
    """
    return [
        {"kp_id": 8, "kp_name": "事务隔离级别", "avg_mastery": 0.20},
        {"kp_id": 12, "kp_name": "数据库范式", "avg_mastery": 0.28},
        {"kp_id": 15, "kp_name": "索引与优化", "avg_mastery": 0.30},
        {"kp_id": 21, "kp_name": "函数参数传递", "avg_mastery": 0.35},
        {"kp_id": 22, "kp_name": "模块导入", "avg_mastery": 0.38},
        {"kp_id": 31, "kp_name": "UML建模", "avg_mastery": 0.42},
        {"kp_id": 23, "kp_name": "异常处理", "avg_mastery": 0.45},
        {"kp_id": 5, "kp_name": "SQL多表连接", "avg_mastery": 0.48},
        {"kp_id": 30, "kp_name": "需求分析", "avg_mastery": 0.52},
        {"kp_id": 25, "kp_name": "视图操作", "avg_mastery": 0.55},
    ][:top_n]


def get_resource_type_distribution(user_token: str) -> list[dict]:
    """
    学习资源类型分布。
    """
    return [
        {"resource_type": "lecture", "type_name": "知识点讲义", "count": 18},
        {"resource_type": "ppt", "type_name": "PPT大纲", "count": 8},
        {"resource_type": "quiz", "type_name": "习题与答案", "count": 12},
        {"resource_type": "case", "type_name": "案例材料", "count": 5},
        {"resource_type": "review", "type_name": "复习计划", "count": 3},
        {"resource_type": "test", "type_name": "阶段测验", "count": 1},
    ]


def get_invocation_trend(user_token: str, days: int = 14) -> list[dict]:
    """
    智能体调用趋势（近N天）。
    """
    from datetime import datetime, timedelta
    trends = []
    for i in range(days, 0, -1):
        d = datetime.now() - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        trends.append({
            "date": date_str,
            "invocation_count": 8 + i * 2,
            "total_tokens": 3200 + i * 800,
            "total_cost": round((3200 + i * 800) * 0.000001, 6)
        })
    return trends


def get_review_rate_by_course(user_token: str) -> list[dict]:
    """
    各课程审核通过率。
    """
    return [
        {"course_id": 1, "course_name": "数据库系统原理", "total": 20, "approved": 17, "pass_rate": 0.85},
        {"course_id": 2, "course_name": "Python程序设计", "total": 15, "approved": 13, "pass_rate": 0.87},
        {"course_id": 3, "course_name": "软件工程实践", "total": 10, "approved": 8, "pass_rate": 0.80},
    ]


def get_cost_distribution(user_token: str) -> list[dict]:
    """
    Token 消耗占比（按智能体分类）。
    """
    return [
        {"agent": "resource_generation_agent", "agent_name": "资源生成", "tokens": 45000, "ratio": 0.45},
        {"agent": "diagnosis_agent", "agent_name": "学习诊断", "tokens": 25000, "ratio": 0.25},
        {"agent": "planning_agent", "agent_name": "资源规划", "tokens": 15000, "ratio": 0.15},
        {"agent": "assessment_agent", "agent_name": "评测反馈", "tokens": 10000, "ratio": 0.10},
        {"agent": "teacher_review_agent", "agent_name": "教师审核辅助", "tokens": 5000, "ratio": 0.05},
    ]
