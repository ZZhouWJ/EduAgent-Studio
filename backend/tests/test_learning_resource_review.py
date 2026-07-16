import unittest
from contextlib import contextmanager
from unittest.mock import Mock, patch

from app.services.learning_resource_review_service import LearningResourceReviewService
from app.utils.exceptions import ConflictException, ForbiddenException, ValidationException


@contextmanager
def transaction(connection):
    yield connection


class LearningResourceReviewServiceTests(unittest.TestCase):
    def setUp(self):
        self.repo = Mock()
        self.access = Mock()
        self.access.require_resource_access.return_value = 3
        self.connection = Mock()
        self.service = LearningResourceReviewService(self.repo, self.access)
        self.teacher = {"user_id": 7, "roles": ["teacher"]}

    def test_student_cannot_submit_resource_for_review(self):
        with self.assertRaisesRegex(ForbiddenException, "教师或管理员"):
            self.service.submit_for_review(
                9, {"user_id": 8, "roles": ["student_member"]}
            )
        self.access.require_resource_access.assert_not_called()

    @patch("app.services.learning_resource_review_service.user_repo.insert_operation_log_with_conn")
    @patch("app.services.learning_resource_review_service.get_db_transaction")
    def test_submit_updates_status_and_audit_in_same_transaction(self, get_tx, log):
        get_tx.return_value = transaction(self.connection)
        self.repo.get_resource_for_update.return_value = {
            "resource_id": 9,
            "status": "draft",
            "content": "完整资源正文",
        }
        self.repo.create_review_request.return_value = 31
        self.repo.update_resource_status.return_value = 1

        result = self.service.submit_for_review(9, self.teacher, "请复核事实")

        self.assertEqual(result["status"], "pending_review")
        self.assertEqual(result["review_id"], 31)
        self.repo.update_resource_status.assert_called_once_with(
            resource_id=9,
            expected_statuses=["draft"],
            status="pending_review",
            conn=self.connection,
        )
        self.assertIs(log.call_args.kwargs["conn"], self.connection)

    @patch("app.services.learning_resource_review_service.get_db_transaction")
    def test_duplicate_submit_is_rejected_by_locked_status(self, get_tx):
        get_tx.return_value = transaction(self.connection)
        self.repo.get_resource_for_update.return_value = {
            "resource_id": 9,
            "status": "pending_review",
            "content": "正文",
        }

        with self.assertRaisesRegex(ConflictException, "草稿或被退回"):
            self.service.submit_for_review(9, self.teacher)

        self.repo.create_review_request.assert_not_called()

    def test_rejection_requires_comment(self):
        with self.assertRaisesRegex(ValidationException, "必须填写审核意见"):
            self.service.complete_review(9, self.teacher, "rejected", review_comment=" ")

    @patch("app.services.learning_resource_review_service.user_repo.insert_operation_log_with_conn")
    @patch("app.services.learning_resource_review_service.get_db_transaction")
    def test_approval_closes_review_and_publishes_resource(self, get_tx, log):
        get_tx.return_value = transaction(self.connection)
        self.repo.get_resource_for_update.return_value = {
            "resource_id": 9,
            "status": "pending_review",
            "content": "正文",
        }
        self.repo.get_pending_review_for_update.return_value = {"review_id": 31}
        self.repo.complete_review_request.return_value = 1
        self.repo.update_resource_status.return_value = 1

        result = self.service.complete_review(
            9,
            self.teacher,
            "approved",
            accuracy_score=9,
            completeness_score=8,
            logic_score=9,
            format_score=8,
            usability_score=9,
            review_comment="审核通过",
        )

        self.assertEqual(result["status"], "approved")
        self.repo.complete_review_request.assert_called_once()
        self.repo.update_resource_status.assert_called_once_with(
            resource_id=9,
            expected_statuses=["pending_review"],
            status="approved",
            conn=self.connection,
        )
        self.assertIs(log.call_args.kwargs["conn"], self.connection)


if __name__ == "__main__":
    unittest.main()
