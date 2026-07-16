"""Learning-resource review lifecycle with transactional audit logging."""

from typing import Any, Dict, Optional

from app.database import get_db_transaction
from app.repositories import user_repo
from app.repositories.learning_resource_repo import LearningResourceRepository
from app.services.course_access_service import CourseAccessService
from app.utils.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)


class LearningResourceReviewService:
    def __init__(
        self,
        repository: Optional[LearningResourceRepository] = None,
        access_service: Optional[CourseAccessService] = None,
    ) -> None:
        self._repo = repository or LearningResourceRepository()
        self._access = access_service or CourseAccessService()

    @staticmethod
    def _require_review_role(user: Dict[str, Any]) -> None:
        if not set(user.get("roles", [])).intersection({"teacher", "admin"}):
            raise ForbiddenException("只有教师或管理员可以管理资源审核")

    def submit_for_review(
        self,
        resource_id: int,
        user: Dict[str, Any],
        submit_note: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_review_role(user)
        course_id = self._access.require_resource_access(resource_id, user)
        user_id = int(user["user_id"])

        with get_db_transaction() as conn:
            resource = self._repo.get_resource_for_update(resource_id, conn)
            if resource is None:
                raise NotFoundException("资源不存在")
            if resource["status"] not in {"draft", "rejected"}:
                raise ConflictException("只有草稿或被退回的资源可以提交审核")
            if not str(resource.get("content") or "").strip():
                raise ValidationException("资源正文为空，无法提交审核")

            review_id = self._repo.create_review_request(
                resource_id=resource_id,
                submitter_id=user_id,
                submit_note=submit_note,
                conn=conn,
            )
            affected = self._repo.update_resource_status(
                resource_id=resource_id,
                expected_statuses=[resource["status"]],
                status="pending_review",
                conn=conn,
            )
            if affected != 1:
                raise ConflictException("资源状态已变化，请刷新后重试")

            user_repo.insert_operation_log_with_conn(
                user_id=user_id,
                action_type="resource:submit_review",
                action_desc=f"提交学习资源审核: resource={resource_id}",
                target_type="learning_resource",
                target_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                conn=conn,
            )

        return {
            "resource_id": resource_id,
            "review_id": review_id,
            "status": "pending_review",
            "course_id": course_id,
        }

    def complete_review(
        self,
        resource_id: int,
        user: Dict[str, Any],
        decision: str,
        accuracy_score: Optional[float] = None,
        completeness_score: Optional[float] = None,
        logic_score: Optional[float] = None,
        format_score: Optional[float] = None,
        usability_score: Optional[float] = None,
        review_comment: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_review_role(user)
        course_id = self._access.require_resource_access(resource_id, user)
        if decision not in {"approved", "rejected"}:
            raise ValidationException("审核结论只能是 approved 或 rejected")
        if decision == "rejected" and not str(review_comment or "").strip():
            raise ValidationException("退回资源时必须填写审核意见")
        if decision == "approved" and any(
            score is None
            for score in (
                accuracy_score,
                completeness_score,
                logic_score,
                format_score,
            )
        ):
            raise ValidationException("审核通过时必须完成四项质量评分")

        user_id = int(user["user_id"])
        with get_db_transaction() as conn:
            resource = self._repo.get_resource_for_update(resource_id, conn)
            if resource is None:
                raise NotFoundException("资源不存在")
            if resource["status"] != "pending_review":
                raise ConflictException("只有待审核资源可以完成审核")

            review = self._repo.get_pending_review_for_update(resource_id, conn)
            if review is None:
                raise ConflictException("资源缺少有效的待审核记录")

            affected = self._repo.complete_review_request(
                review_id=int(review["review_id"]),
                reviewer_id=user_id,
                decision=decision,
                accuracy_score=accuracy_score,
                completeness_score=completeness_score,
                logic_score=logic_score,
                format_score=format_score,
                usability_score=usability_score,
                review_comment=review_comment,
                conn=conn,
            )
            if affected != 1:
                raise ConflictException("审核记录已被处理，请刷新后重试")

            affected = self._repo.update_resource_status(
                resource_id=resource_id,
                expected_statuses=["pending_review"],
                status=decision,
                conn=conn,
            )
            if affected != 1:
                raise ConflictException("资源状态已变化，请刷新后重试")

            user_repo.insert_operation_log_with_conn(
                user_id=user_id,
                action_type=f"resource:review_{decision}",
                action_desc=f"完成学习资源审核: resource={resource_id}, decision={decision}",
                target_type="learning_resource",
                target_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                conn=conn,
            )

        return {
            "resource_id": resource_id,
            "review_id": int(review["review_id"]),
            "status": decision,
            "course_id": course_id,
        }
