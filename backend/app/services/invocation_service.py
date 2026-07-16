"""AI 调用审计查询服务。"""

from typing import Any, Dict, Optional

from app.repositories import invocation_repo, project_repo, task_repo, user_repo
from app.utils.exceptions import ForbiddenException, NotFoundException, UnauthorizedException


def _require_auth(token: str) -> Dict[str, Any]:
    from app.services.auth_service import get_current_user

    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def _can_access_project(project_id: int, user_id: int) -> bool:
    if user_repo.is_admin(user_id):
        return True
    return project_repo.is_user_in_project(project_id, user_id)


def list_invocations(
    token: str,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    model_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """分页查询调用日志。"""
    user = _require_auth(token)
    rows, total = invocation_repo.list_invocations(
        is_admin=_is_admin(user),
        user_id=user["user_id"],
        project_id=project_id,
        task_id=task_id,
        model_id=model_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [_invocation_row_to_dict(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_invocation_detail(token: str, invocation_id: int) -> Dict[str, Any]:
    """获取调用详情。"""
    user = _require_auth(token)
    invocation = invocation_repo.get_invocation_by_id(invocation_id)
    if invocation is None:
        raise NotFoundException(message="调用记录不存在")

    if invocation.get("task_id"):
        task = task_repo.get_task_by_id(invocation["task_id"])
        if task and not _can_access_project(task["project_id"], user["user_id"]):
            raise ForbiddenException(message="无权查看此调用记录")

    return _invocation_detail_to_dict(invocation)


def _invocation_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "invocation_id": row["invocation_id"],
        "project_id": row["project_id"],
        "task_id": row["task_id"],
        "branch_id": row.get("branch_id"),
        "model_id": row["model_id"],
        "model_name": row.get("model_name"),
        "model_display_name": row.get("model_display_name"),
        "provider_name": row.get("provider_name"),
        "task_title": row.get("task_title"),
        "branch_name": row.get("branch_name"),
        "status": row["status"],
        "input_tokens": row.get("input_tokens"),
        "output_tokens": row.get("output_tokens"),
        "latency_ms": row.get("latency_ms"),
        "created_by": row.get("created_by"),
        "creator_username": row.get("creator_username"),
        "created_at": row.get("created_at"),
    }


def _invocation_detail_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    result = _invocation_row_to_dict(row)
    result["input_text"] = row.get("input_text")
    result["output_text"] = row.get("output_text")
    result["error_message"] = row.get("error_message")
    result["creator_real_name"] = row.get("creator_real_name")
    return result
