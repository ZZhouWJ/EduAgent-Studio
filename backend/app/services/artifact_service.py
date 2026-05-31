"""
成果库与分支合并 Service 层。

处理成果采用、成果列表、成果详情、分支合并相关业务逻辑。
所有写操作使用 get_db_transaction() 保证与 operation_logs 同一事务。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_db_transaction
from app.repositories import artifact_repo, user_repo
from app.utils.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


# =============================================================================
# 权限辅助
# =============================================================================

def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def _is_admin_user(user_id: int) -> bool:
    return artifact_repo.is_user_admin(user_id)


def _can_access_project(project_id: int, user_id: int) -> bool:
    if _is_admin_user(user_id):
        return True
    return artifact_repo.is_user_in_project(project_id, user_id)


def _can_adopt_or_merge(project_id: int, user_id: int) -> bool:
    """判断用户是否可以采用成果或执行分支合并。"""
    if _is_admin_user(user_id):
        return True
    if artifact_repo.is_user_project_leader(project_id, user_id):
        return True
    if artifact_repo.is_user_project_teacher(project_id, user_id):
        return True
    return False


def _get_project_id_from_adopted(adopted_id: int) -> Optional[int]:
    """从 adopted_id 获取项目 ID。"""
    ctx = artifact_repo.get_adopted_output_project_context(adopted_id)
    return ctx["project_id"] if ctx else None


# =============================================================================
# 采用成果
# POST /api/outputs/{output_id}/adopt
# =============================================================================

def adopt_output(
    token: str,
    output_id: int,
    artifact_title: str,
    artifact_type: str,
    release_version: str,
    adopt_note: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    采用输出作为成果。

    事务：
    1. 校验 output 存在、未删除
    2. 校验当前用户有项目访问权限
    3. 校验当前用户有成果采用权限（admin/leader/teacher）
    4. 校验 output 状态为 approved
    5. 校验 output 未被重复采用
    6. 插入 adopted_outputs
    7. 更新 task_outputs.status = 'adopted'（检查 affected_rows）
    8. 更新 project_tasks.status = 'adopted'（检查 affected_rows）
    9. 写入 operation_logs
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    output = artifact_repo.get_output_for_adoption(output_id)
    if output is None:
        raise NotFoundException(message="输出版本不存在")

    project_id = output["project_id"]
    task_id = output["task_id"]

    if not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权访问该输出版本所属项目")

    if not _can_adopt_or_merge(project_id, user_id):
        raise ForbiddenException(message="只有管理员、项目负责人或指导教师可以采用成果")

    if output.get("output_status") != "approved":
        raise ValidationException(
            message=f"只有审核通过的输出才能采用，当前状态: {output.get('output_status')}"
        )

    with get_db_transaction() as conn:
        adopted = artifact_repo.has_adopted_output(output_id, conn)
        if adopted:
            conn.rollback()
            raise ConflictException(message="该输出已被采用，不能重复采用")

        adopted_id = artifact_repo.create_adopted_output(
            project_id=project_id,
            task_id=task_id,
            output_id=output_id,
            artifact_title=artifact_title,
            artifact_type=artifact_type,
            release_version=release_version,
            adopted_by=user_id,
            conn=conn,
        )

        affected = artifact_repo.update_output_status_adopted(output_id, conn)
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="输出版本不存在或无权更新状态")

        affected = artifact_repo.update_task_status_adopted(task_id, conn)
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="任务不存在或无权更新状态")

        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="artifact:adopt",
            action_desc=f"采用成果: output={output_id}, artifact={artifact_title}",
            target_type="output",
            target_id=output_id,
            project_id=project_id,
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {"adopted_id": adopted_id}


# =============================================================================
# 项目成果列表
# GET /api/projects/{project_id}/artifacts
# =============================================================================

def list_project_artifacts(
    token: str,
    project_id: int,
    artifact_type: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """
    分页查询项目成果列表。

    - admin 查看全部
    - 项目成员查看本项目
    - 非项目成员无权查看
    """
    user = _require_auth(token)
    user_id = user["user_id"]
    is_admin = _is_admin(user)

    if not is_admin and not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权查看该项目成果")

    rows, total = artifact_repo.list_project_artifacts(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
        artifact_type=artifact_type,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [_artifact_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# =============================================================================
# 成果详情
# GET /api/artifacts/{adopted_id}
# =============================================================================

def get_artifact_detail(
    token: str,
    adopted_id: int,
) -> Dict[str, Any]:
    """
    获取成果详情。

    - admin 可查看任意
    - 项目成员可查看本项目
    - 非项目成员无权查看
    """
    user = _require_auth(token)
    user_id = user["user_id"]
    is_admin = _is_admin(user)

    ctx = _get_project_id_from_adopted(adopted_id)
    if ctx is None:
        raise NotFoundException(message="成果不存在")

    project_id = ctx

    if not is_admin and not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权查看此成果")

    row = artifact_repo.get_adopted_output_by_id(adopted_id)
    if row is None:
        raise NotFoundException(message="成果不存在")

    return _artifact_detail_to_dict(row)


# =============================================================================
# 分支合并
# POST /api/tasks/{task_id}/branches/merge
# =============================================================================

def merge_branches(
    token: str,
    task_id: int,
    source_branch_id: int,
    target_branch_id: int,
    source_output_id: Optional[int] = None,
    target_output_id: Optional[int] = None,
    merge_strategy: str = "manual_merge",
    merged_output_title: Optional[str] = None,
    merged_content: Optional[str] = None,
    merge_note: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    执行分支合并。

    事务：
    1. 校验 task 存在、未删除
    2. 校验 source_branch 和 target_branch 属于该 task
    3. 校验 source_output/target_output（如传入）属于该 task
    4. 校验当前用户有合并权限（admin/leader/teacher）
    5. 校验 merge_strategy
    6. 写入 merge_records
    7. 根据策略处理：
       - adopt_source：source_output 状态更新为 adopted
       - adopt_target：target_output 状态更新为 adopted
       - manual_merge：创建新 output，更新两个分支状态
       - adopt_separately：记录即可
    8. 更新 task_branches 状态
    9. 写入 operation_logs
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    if merge_strategy not in artifact_repo.VALID_MERGE_STRATEGIES:
        raise ValidationException(
            message=f"无效的合并策略: {merge_strategy}，允许值: {', '.join(artifact_repo.VALID_MERGE_STRATEGIES)}"
        )

    task_ctx = artifact_repo.get_task_context(task_id)
    if task_ctx is None:
        raise NotFoundException(message="任务不存在")

    project_id = task_ctx["project_id"]

    if not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权访问该任务所属项目")

    if not _can_adopt_or_merge(project_id, user_id):
        raise ForbiddenException(message="只有管理员、项目负责人或指导教师可以执行分支合并")

    source_branch = artifact_repo.get_branch_context(source_branch_id)
    if source_branch is None or source_branch["task_id"] != task_id:
        raise NotFoundException(message="源分支不存在或不属于该任务")

    target_branch = artifact_repo.get_branch_context(target_branch_id)
    if target_branch is None or target_branch["task_id"] != task_id:
        raise NotFoundException(message="目标分支不存在或不属于该任务")

    base_output_id = source_branch.get("base_output_id")

    source_output_id_resolved: Optional[int] = None
    target_output_id_resolved: Optional[int] = None

    if source_output_id is not None:
        ctx = artifact_repo.get_output_context(source_output_id)
        if ctx is None or ctx["task_id"] != task_id:
            raise NotFoundException(message="源输出不存在或不属于该任务")
        source_output_id_resolved = source_output_id

    if target_output_id is not None:
        ctx = artifact_repo.get_output_context(target_output_id)
        if ctx is None or ctx["task_id"] != task_id:
            raise NotFoundException(message="目标输出不存在或不属于该任务")
        target_output_id_resolved = target_output_id

    if merge_strategy == "manual_merge":
        if not merged_output_title or not merged_output_title.strip():
            raise ValidationException(message="manual_merge 策略必须提供 merged_output_title")
        if not merged_content:
            raise ValidationException(message="manual_merge 策略必须提供 merged_content")

    now = datetime.now()

    with get_db_transaction() as conn:
        merged_output_id: Optional[int] = None

        if merge_strategy == "adopt_source":
            if source_output_id_resolved is not None:
                affected = artifact_repo.update_output_status(
                    source_output_id_resolved, "adopted", conn
                )
                if affected == 0:
                    conn.rollback()
                    raise NotFoundException(message="源输出不存在或无权更新状态")

        elif merge_strategy == "adopt_target":
            if target_output_id_resolved is not None:
                affected = artifact_repo.update_output_status(
                    target_output_id_resolved, "adopted", conn
                )
                if affected == 0:
                    conn.rollback()
                    raise NotFoundException(message="目标输出不存在或无权更新状态")

        elif merge_strategy == "manual_merge":
            merged_output_id = artifact_repo.create_task_output(
                task_id=task_id,
                output_title=merged_output_title.strip(),
                content=merged_content,
                source_type="manual_merge",
                parent_output_id=target_output_id_resolved,
                created_by=user_id,
                conn=conn,
            )
            artifact_repo.update_branch_status(source_branch_id, "merged", conn)
            artifact_repo.update_branch_status(target_branch_id, "active", conn)

        elif merge_strategy == "adopt_separately":
            artifact_repo.update_branch_status(source_branch_id, "merged", conn)

        merge_id = artifact_repo.create_merge_record(
            project_id=project_id,
            task_id=task_id,
            base_output_id=base_output_id,
            source_output_id=source_output_id_resolved,
            target_output_id=target_output_id_resolved,
            merged_output_id=merged_output_id,
            merge_strategy=merge_strategy,
            merge_comment=merge_note,
            merged_by=user_id,
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="branch:merge",
            action_desc=f"分支合并: task={task_id}, strategy={merge_strategy}, merge_id={merge_id}",
            target_type="task",
            target_id=task_id,
            project_id=project_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {
        "merge_id": merge_id,
        "merged_output_id": merged_output_id,
    }


# =============================================================================
# 数据转换
# =============================================================================

def _artifact_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """成果列表行。"""
    if row is None:
        return {}
    return {
        "adopted_id": row["adopted_id"],
        "project_id": row["project_id"],
        "task_id": row["task_id"],
        "output_id": row["output_id"],
        "artifact_title": row["artifact_title"],
        "artifact_type": row["artifact_type"],
        "release_version": row["release_version"],
        "adopted_by": row["adopted_by"],
        "adopted_by_name": row.get("adopted_by_real_name") or row.get("adopted_by_username"),
        "adopted_at": row["adopted_at"],
        "task_title": row.get("task_title"),
        "output_title": row.get("output_title"),
        "version_no": row.get("version_no"),
    }


def _artifact_detail_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """成果详情。"""
    if row is None:
        return {}
    return {
        "adopted_id": row["adopted_id"],
        "project_id": row["project_id"],
        "project_name": row.get("project_name"),
        "task_id": row["task_id"],
        "task_title": row.get("task_title"),
        "output_id": row["output_id"],
        "output_title": row.get("output_title"),
        "version_no": row.get("version_no"),
        "output_content": row.get("output_content"),
        "output_status": row.get("output_status"),
        "artifact_title": row["artifact_title"],
        "artifact_type": row["artifact_type"],
        "release_version": row["release_version"],
        "adopted_by": row["adopted_by"],
        "adopted_by_username": row.get("adopted_by_username"),
        "adopted_by_real_name": row.get("adopted_by_real_name"),
        "adopted_at": row["adopted_at"],
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
