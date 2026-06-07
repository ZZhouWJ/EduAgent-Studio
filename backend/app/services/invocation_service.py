"""
调用日志 Service 层。

处理 AI 模型调用、输出版本写入，成本记录相关业务逻辑。
"""

from typing import Any, Dict, List, Optional

from app.adapters import get_adapter_by_model_name
from app.database import get_db_transaction
from app.repositories import invocation_repo, model_repo, project_repo, task_repo, user_repo
from app.utils.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


# =============================================================================
# 权限辅助
# =============================================================================

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


# =============================================================================
# 任务模型生成
# =============================================================================

def generate_task_outputs(
    token: str,
    task_id: int,
    model_ids: List[int],
    input_text: str,
    branch_id: Optional[int] = None,
    prompt_version_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    任务模型生成（调用 Mock 模型，批量）。

    每个模型的调用流程（同一事务内）：
    1. 校验模型
    2. 调用 Mock Adapter
    3. 先插入 ai_invocations，获取 invocation_id
    4. 成功后插入 task_outputs（关联 invocation_id）
    5. 成功后插入 cost_records
    6. 失败时也插入 cost_records（成本为 0）

    单个模型失败不影响其他模型结果。

    Returns:
        每个模型的调用结果列表
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise NotFoundException(message="任务不存在")

    project_id = task["project_id"]

    if not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权为此任务生成内容")

    if not model_ids:
        raise ValidationException(message="model_ids 不能为空")

    if not input_text or not input_text.strip():
        raise ValidationException(message="输入内容不能为空")

    if branch_id is not None:
        branch = task_repo.get_branch_by_id_and_task(branch_id, task_id)
        if branch is None:
            raise ValidationException(message="分支不属于当前任务")

    prompt_content: Optional[str] = None
    if prompt_version_id is not None:
        from app.repositories import prompt_repo
        version = prompt_repo.get_version_by_id(prompt_version_id)
        if version is None:
            raise NotFoundException(message="提示词版本不存在")
        prompt_content = version.get("prompt_content")

    results: List[Dict[str, Any]] = []

    with get_db_transaction() as conn:
        for model_id in model_ids:
            model = model_repo.get_model_by_id(model_id)
            if model is None or model.get("status") != "active":
                invocation_id = invocation_repo.create_invocation(
                    project_id=project_id,
                    task_id=task_id,
                    branch_id=branch_id,
                    model_id=model_id,
                    prompt_version_id=prompt_version_id,
                    input_text=input_text.strip(),
                    output_text=None,
                    error_message="模型不存在或未激活",
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=0,
                    status="failed",
                    created_by=user_id,
                    conn=conn,
                )
                invocation_repo.create_cost_record(
                    invocation_id=invocation_id,
                    project_id=project_id,
                    task_id=task_id,
                    model_id=model_id,
                    user_id=user_id,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    input_cost=0.0,
                    output_cost=0.0,
                    total_cost=0.0,
                    currency="CNY",
                    conn=conn,
                )
                results.append({
                    "model_id": model_id,
                    "invocation_id": invocation_id,
                    "status": "failed",
                    "error_message": "模型不存在或未激活",
                })
                continue

            model_name = model["model_name"]

            try:
                adapter = get_adapter_by_model_name(model_name)
            except ValueError as e:
                invocation_id = invocation_repo.create_invocation(
                    project_id=project_id,
                    task_id=task_id,
                    branch_id=branch_id,
                    model_id=model_id,
                    prompt_version_id=prompt_version_id,
                    input_text=input_text.strip(),
                    output_text=None,
                    error_message=str(e),
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=0,
                    status="failed",
                    created_by=user_id,
                    conn=conn,
                )
                invocation_repo.create_cost_record(
                    invocation_id=invocation_id,
                    project_id=project_id,
                    task_id=task_id,
                    model_id=model_id,
                    user_id=user_id,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    input_cost=0.0,
                    output_cost=0.0,
                    total_cost=0.0,
                    currency="CNY",
                    conn=conn,
                )
                results.append({
                    "model_id": model_id,
                    "model_name": model_name,
                    "invocation_id": invocation_id,
                    "status": "failed",
                    "error_message": str(e),
                })
                continue

            model_result = adapter.generate(
                input_text=input_text.strip(),
                prompt_content=prompt_content,
            )

            if model_result.status == "success":
                output_title = f"AI 生成结果 - {model.get('display_name', model_name)}"
                next_version = invocation_repo.get_next_output_version_no_for_update(
                    task_id=task_id,
                    conn=conn,
                )

                # 先插入 ai_invocations，获取 invocation_id
                invocation_id = invocation_repo.create_invocation(
                    project_id=project_id,
                    task_id=task_id,
                    branch_id=branch_id,
                    model_id=model_id,
                    prompt_version_id=prompt_version_id,
                    input_text=input_text.strip(),
                    output_text=model_result.output_text,
                    error_message=None,
                    input_tokens=model_result.input_tokens,
                    output_tokens=model_result.output_tokens,
                    latency_ms=model_result.latency_ms,
                    status="success",
                    created_by=user_id,
                    conn=conn,
                )

                # 再插入 task_outputs，关联 invocation_id
                output_id = invocation_repo.create_task_output(
                    task_id=task_id,
                    branch_id=branch_id,
                    invocation_id=invocation_id,
                    version_no=next_version,
                    output_title=output_title,
                    content=model_result.output_text,
                    source_type="ai_generated",
                    parent_output_id=None,
                    created_by=user_id,
                    conn=conn,
                )

                input_cost = (
                    model_result.input_tokens / 1000.0 * float(model.get("input_price", 0))
                )
                output_cost = (
                    model_result.output_tokens / 1000.0 * float(model.get("output_price", 0))
                )
                total_cost = input_cost + output_cost

                invocation_repo.create_cost_record(
                    invocation_id=invocation_id,
                    project_id=project_id,
                    task_id=task_id,
                    model_id=model_id,
                    user_id=user_id,
                    input_tokens=model_result.input_tokens,
                    output_tokens=model_result.output_tokens,
                    total_tokens=model_result.input_tokens + model_result.output_tokens,
                    input_cost=input_cost,
                    output_cost=output_cost,
                    total_cost=total_cost,
                    currency="CNY",
                    conn=conn,
                )

                results.append({
                    "model_id": model_id,
                    "model_name": model_name,
                    "invocation_id": invocation_id,
                    "output_id": output_id,
                    "version_no": next_version,
                    "status": "success",
                    "input_tokens": model_result.input_tokens,
                    "output_tokens": model_result.output_tokens,
                    "latency_ms": model_result.latency_ms,
                })

            else:
                invocation_id = invocation_repo.create_invocation(
                    project_id=project_id,
                    task_id=task_id,
                    branch_id=branch_id,
                    model_id=model_id,
                    prompt_version_id=prompt_version_id,
                    input_text=input_text.strip(),
                    output_text=None,
                    error_message=model_result.error_message,
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=model_result.latency_ms,
                    status="failed",
                    created_by=user_id,
                    conn=conn,
                )
                invocation_repo.create_cost_record(
                    invocation_id=invocation_id,
                    project_id=project_id,
                    task_id=task_id,
                    model_id=model_id,
                    user_id=user_id,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    input_cost=0.0,
                    output_cost=0.0,
                    total_cost=0.0,
                    currency="CNY",
                    conn=conn,
                )
                results.append({
                    "model_id": model_id,
                    "model_name": model_name,
                    "invocation_id": invocation_id,
                    "status": "failed",
                    "error_message": model_result.error_message,
                })

        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="task:generate",
            action_desc=f"调用模型生成任务输出: task={task_id}, models={model_ids}",
            target_type="task",
            target_id=task_id,
            project_id=project_id,
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return results


# =============================================================================
# 调用日志列表
# =============================================================================

def list_invocations(
    token: str,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    model_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """分页查询调用日志列表。"""
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
        "items": [_invocation_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# =============================================================================
# 调用详情
# =============================================================================

def get_invocation_detail(
    token: str,
    invocation_id: int,
) -> Dict[str, Any]:
    """获取调用详情。"""
    user = _require_auth(token)

    invocation = invocation_repo.get_invocation_by_id(invocation_id)
    if invocation is None:
        raise NotFoundException(message="调用记录不存在")

    if invocation.get("task_id"):
        task = task_repo.get_task_by_id(invocation["task_id"])
        if task:
            if not _can_access_project(task["project_id"], user["user_id"]):
                raise ForbiddenException(message="无权查看此调用记录")

    return _invocation_detail_to_dict(invocation)


# =============================================================================
# 数据转换
# =============================================================================

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
