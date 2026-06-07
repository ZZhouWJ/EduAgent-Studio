"""
审核中心 Service 层。

处理审核提交、待审核列表、审核详情、完成审核相关业务逻辑。
所有写操作使用 get_db_transaction() 保证与 operation_logs 同一事务。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_db_transaction
from app.repositories import review_repo, user_repo
from app.utils.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


# =============================================================================
# 权限辅助函数
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
    from app.repositories import user_repo as ur
    user = ur.get_user_by_id(user_id)
    if user is None:
        return False
    return "admin" in user.get("roles", [])


def _can_access_project(project_id: int, user_id: int) -> bool:
    if _is_admin_user(user_id):
        return True
    return review_repo.is_user_in_project(project_id, user_id)


def _get_project_role(project_id: int, user_id: int) -> Optional[str]:
    """获取用户在指定项目内的 project_role（来自 project_members）。"""
    return review_repo.get_project_member_role(project_id, user_id)


# =============================================================================
# 提交审核
# POST /api/outputs/{output_id}/submit-review
# =============================================================================

def submit_for_review(
    token: str,
    output_id: int,
    reviewer_id: Optional[int] = None,
    submit_note: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    提交输出到审核。

    Fix: reviewer_id 校验 + affected_rows 检查

    事务：
    1. 校验 output 存在、未删除、未归档
    2. 校验当前用户有项目访问权限
    3. 校验 reviewer_id（如传入）：存在、是项目成员或 admin、不是本人
    4. 校验不存在 pending 审核请求
    5. 插入 review_requests
    6. 更新 task_outputs.status = 'submitted'（检查 affected_rows）
    7. 更新 project_tasks.status = 'submitted'（检查 affected_rows）
    8. 写入 operation_logs
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    output = review_repo.get_output_by_id(output_id)
    if output is None:
        raise NotFoundException(message="输出版本不存在")

    project_id = output["project_id"]
    task_id = output["task_id"]

    if not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权为此输出版本提交审核")

    if output.get("output_status") == "archived":
        raise ValidationException(message="已归档的输出不能提交审核")

    # Fix 1: 校验 reviewer_id
    if reviewer_id is not None:
        reviewer = review_repo.get_user_basic_by_id(reviewer_id)
        if reviewer is None:
            raise NotFoundException(message="指定的审核人不存在")

        if reviewer_id == user_id:
            raise ValidationException(message="不能指定自己为审核人")

        if _is_admin_user(reviewer_id):
            pass
        elif not review_repo.is_user_in_project(project_id, reviewer_id):
            raise ValidationException(message="指定的审核人必须是项目成员或管理员")

    with get_db_transaction() as conn:
        has_pending = review_repo.has_pending_request(output_id, conn)
        if has_pending:
            conn.rollback()
            raise ConflictException(message="该输出已存在待审核请求，请勿重复提交")

        request_id = review_repo.create_review_request(
            output_id=output_id,
            task_id=task_id,
            project_id=project_id,
            submitter_id=user_id,
            reviewer_id=reviewer_id,
            submit_note=submit_note,
            conn=conn,
        )

        # Fix 6: 检查 affected_rows
        affected = review_repo.update_output_status(
            output_id=output_id,
            status="submitted",
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="输出版本不存在或无权更新状态")

        affected = review_repo.update_task_status(
            task_id=task_id,
            status="submitted",
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="任务不存在或无权更新状态")

        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="review:submit",
            action_desc=f"提交审核: output={output_id}",
            target_type="output",
            target_id=output_id,
            project_id=project_id,
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {"request_id": request_id}


# =============================================================================
# 待审核列表
# GET /api/reviews/pending
# =============================================================================

def list_pending_reviews(
    token: str,
    project_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """
    分页查询待审核列表。

    Fix: 普通 member 被指定为 reviewer_id 时可查看分配给自己的请求

    权限规则：
    - admin：查看全部
    - 非 admin：查看（项目内 leader/teacher/reviewer 的项目 OR reviewer_id = 当前用户）的 pending
    """
    user = _require_auth(token)
    user_id = user["user_id"]
    is_admin = _is_admin(user)

    rows, total = review_repo.list_pending_reviews(
        is_admin=is_admin,
        user_id=user_id,
        project_id=project_id,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [_review_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# =============================================================================
# 审核详情
# GET /api/reviews/{request_id}
# =============================================================================

def get_review_detail(
    token: str,
    request_id: int,
) -> Dict[str, Any]:
    """
    获取审核详情。

    权限规则（与待审核列表/完成审核保持一致）：
    - admin：可查看任意
    - 项目内 leader/teacher/reviewer：可查看本项目
    - 指定 reviewer：可查看分配给自己的
    - 提交者：可查看自己提交的
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    ctx = review_repo.get_request_project_context(request_id)
    if ctx is None:
        raise NotFoundException(message="审核请求不存在")

    project_id = ctx["project_id"]
    is_admin_flag = _is_admin(user)
    project_role = _get_project_role(project_id, user_id)

    can_view = False
    if is_admin_flag:
        can_view = True
    elif project_role in ("leader", "teacher", "reviewer"):
        can_view = True
    elif ctx.get("reviewer_id") == user_id:
        can_view = True
    elif ctx.get("submitter_id") == user_id:
        can_view = True

    if not can_view:
        raise ForbiddenException(message="无权查看此审核请求")

    request = review_repo.get_review_request_by_id(request_id)
    return _review_detail_to_dict(request)


# =============================================================================
# 完成审核
# POST /api/reviews/{request_id}/complete
# =============================================================================

def complete_review(
    token: str,
    request_id: int,
    review_status: str,
    accuracy_score: Optional[float] = None,
    completeness_score: Optional[float] = None,
    logic_score: Optional[float] = None,
    format_score: Optional[float] = None,
    usability_score: Optional[float] = None,
    risk_score: Optional[float] = None,
    review_comment: Optional[str] = None,
    issue_tag_ids: Optional[List[int]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    完成审核。

    Fix: VALID_COMPLETE_REVIEW_STATUS + affected_rows 检查 + 自审拦截 + 指定 reviewer 权限收紧

    事务：
    1. 校验请求存在、未删除
    2. 校验 request_status = pending
    3. 校验审核权限（自审拦截 + 指定 reviewer 权限收紧）
    4. 校验 review_status（只允许 approved/rejected/revision_required）
    5. 校验 issue_tag_ids（如有）
    6. 插入 output_reviews
    7. 更新 review_requests.request_status（检查 affected_rows）
    8. 更新 task_outputs.status（检查 affected_rows）
    9. 更新 project_tasks.status（检查 affected_rows）
    10. 写入 output_issue_relations（如有 issue_tag_ids）
    11. 写入 operation_logs
    """
    user = _require_auth(token)
    user_id = user["user_id"]

    # Fix 3: 只允许三种结论状态
    if review_status not in review_repo.VALID_COMPLETE_REVIEW_STATUS:
        raise ValidationException(
            message=f"无效的审核结论: {review_status}，允许值: {', '.join(review_repo.VALID_COMPLETE_REVIEW_STATUS)}"
        )

    ctx = review_repo.get_request_project_context(request_id)
    if ctx is None:
        raise NotFoundException(message="审核请求不存在")

    if ctx["request_status"] != "pending":
        raise ValidationException(message="只有待审核状态才能完成审核")

    project_id = ctx["project_id"]
    task_id = ctx["task_id"]
    output_id = ctx["output_id"]
    submitter_id = ctx["submitter_id"]
    reviewer_id = ctx.get("reviewer_id")

    if not _can_access_project(project_id, user_id):
        raise ForbiddenException(message="无权完成此审核")

    if not _can_complete_review(user, user_id, ctx, project_id):
        raise ForbiddenException(message="无权完成此审核")

    if issue_tag_ids:
        all_exist, _ = review_repo.check_issue_tags_exist(issue_tag_ids)
        if not all_exist:
            raise ValidationException(message="存在无效或已删除的问题标签")

    now = datetime.now()

    with get_db_transaction() as conn:
        review_id = review_repo.create_output_review(
            request_id=request_id,
            output_id=output_id,
            reviewer_id=user_id,
            review_status=review_status,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            logic_score=logic_score,
            format_score=format_score,
            usability_score=usability_score,
            risk_score=risk_score,
            review_comment=review_comment,
            created_by=user_id,
            conn=conn,
        )

        # Fix 6: 检查 affected_rows
        affected = review_repo.update_review_request_status(
            request_id=request_id,
            status=review_status,
            reviewed_at=now,
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="审核请求不存在或状态已变更")

        affected = review_repo.update_output_status(
            output_id=output_id,
            status=review_status,
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="输出版本不存在或无权更新状态")

        affected = review_repo.update_task_status(
            task_id=task_id,
            status=review_status,
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="任务不存在或无权更新状态")

        if issue_tag_ids:
            for tag_id in issue_tag_ids:
                review_repo.create_output_issue_relation(
                    output_id=output_id,
                    review_id=review_id,
                    tag_id=tag_id,
                    created_by=user_id,
                    conn=conn,
                )

        user_repo.insert_operation_log_with_conn(
            user_id=user_id,
            action_type="review:complete",
            action_desc=f"完成审核: request={request_id}, status={review_status}",
            target_type="output",
            target_id=output_id,
            project_id=project_id,
            task_id=task_id,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    return {"review_id": review_id}


def _can_complete_review(
    user: Dict[str, Any],
    user_id: int,
    ctx: Dict[str, Any],
    project_id: int,
) -> bool:
    """
    判断当前用户是否有完成审核权限。

    权限规则（按优先级）：

    1. admin 永远允许
    2. 非项目成员且不是指定 reviewer：不允许
    3. 自审拦截：只有 admin / 项目 leader / 项目 teacher 可以作为例外
       - admin 已在第 1 步 return True
       - 项目 leader 或 teacher 允许自审
       - 项目 reviewer 或普通 member 不能自审
    4. reviewer_id 不为空（指定审核人场景）：
       - 允许：指定 reviewer 本人 / 项目 leader / 项目 teacher
       - 禁止：项目内其他 reviewer / 普通 member
    5. reviewer_id 为空（未指定审核人场景）：
       - 允许：项目 leader / teacher / reviewer
       - 禁止：普通 member
    """
    submitter_id = ctx.get("submitter_id")
    reviewer_id = ctx.get("reviewer_id")

    # 1. admin 永远允许
    if _is_admin(user):
        return True

    # 获取当前用户在该项目内的 project_role
    project_role = _get_project_role(project_id, user_id)

    is_project_leader = (project_role == "leader")
    is_project_teacher = (project_role == "teacher")
    is_project_reviewer = (project_role == "reviewer")
    is_project_member = project_role in ("leader", "teacher", "reviewer", "member")

    is_assigned_reviewer = (reviewer_id is not None and reviewer_id == user_id)
    is_self_submit = (submitter_id == user_id)

    # 2. 非项目成员，且不是指定 reviewer：不允许
    if not is_project_member and not is_assigned_reviewer:
        return False

    # 3. 自审拦截
    # 只有 admin（已在第1步）/ 项目 leader / 项目 teacher 可以自审
    if is_self_submit:
        return is_project_leader or is_project_teacher

    # 4. 指定 reviewer 场景（reviewer_id 不为空）
    if reviewer_id is not None:
        # 允许：指定 reviewer 本人 / 项目 leader / 项目 teacher
        # 禁止：项目内其他 reviewer / 普通 member
        return is_assigned_reviewer or is_project_leader or is_project_teacher

    # 5. 未指定 reviewer 场景（reviewer_id 为空）
    # 允许：项目 leader / teacher / reviewer
    # 禁止：普通 member
    return is_project_leader or is_project_teacher or is_project_reviewer


# =============================================================================
# 问题标签列表
# GET /api/issue-tags
# =============================================================================

def list_issue_tags(token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    查询所有可用的问题标签。
    接受可选 token 参数以支持统一的认证风格。
    """
    if token:
        _require_auth(token)
    tags = review_repo.list_issue_tags()
    return [_tag_to_dict(t) for t in tags]


# =============================================================================
# 数据转换
# =============================================================================

def _review_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """待审核列表行。"""
    if row is None:
        return {}
    return {
        "request_id": row["request_id"],
        "output_id": row["output_id"],
        "task_id": row["task_id"],
        "project_id": row["project_id"],
        "project_name": row.get("project_name"),
        "task_title": row.get("task_title"),
        "output_title": row.get("output_title"),
        "version_no": row.get("version_no"),
        "submitter_id": row["submitter_id"],
        "submitter_username": row.get("submitter_username"),
        "submitter_real_name": row.get("submitter_real_name"),
        "reviewer_id": row.get("reviewer_id"),
        "reviewer_username": row.get("reviewer_username"),
        "reviewer_real_name": row.get("reviewer_real_name"),
        "request_status": row["request_status"],
        "submit_note": row.get("submit_note"),
        "created_at": row.get("created_at"),
    }


def _review_detail_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """审核详情。"""
    if row is None:
        return {}
    return {
        "request_id": row["request_id"],
        "output_id": row["output_id"],
        "task_id": row["task_id"],
        "project_id": row["project_id"],
        "project_name": row.get("project_name"),
        "task_title": row.get("task_title"),
        "output_title": row.get("output_title"),
        "version_no": row.get("version_no"),
        "output_content": row.get("output_content"),
        "output_status": row.get("output_status"),
        "submitter_id": row["submitter_id"],
        "submitter_username": row.get("submitter_username"),
        "submitter_real_name": row.get("submitter_real_name"),
        "reviewer_id": row.get("reviewer_id"),
        "reviewer_username": row.get("reviewer_username"),
        "reviewer_real_name": row.get("reviewer_real_name"),
        "request_status": row["request_status"],
        "submit_note": row.get("submit_note"),
        "reviewed_at": row.get("reviewed_at"),
        "created_at": row.get("created_at"),
    }


def _tag_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    """问题标签。"""
    return {
        "tag_id": row["tag_id"],
        "tag_name": row["tag_name"],
        "tag_code": row.get("tag_code"),
        "description": row.get("description"),
        "severity": row.get("severity"),
    }
