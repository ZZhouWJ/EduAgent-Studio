import unittest
from unittest.mock import MagicMock, Mock, patch

from app.services.learning_service import LearningService
from app.utils.exceptions import ForbiddenException


class LearningServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = LearningService()
        self.service._repo = Mock()
        self.service._access = Mock()
        self.service._repo.list_tasks.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
        }

    def test_task_list_is_scoped_to_accessible_courses(self):
        user = {"user_id": 12, "roles": ["student_member"]}
        self.service._access.list_accessible_course_ids.return_value = [1]

        self.service.list_tasks(user=user)

        self.service._repo.list_tasks.assert_called_once_with(
            page=1,
            page_size=20,
            course_id=None,
            course_ids=[1],
            status=None,
            assignee_user_id=12,
            visible_statuses=["assigned", "in_progress", "completed"],
        )

    def test_explicit_task_course_requires_access(self):
        user = {"user_id": 7, "roles": ["teacher"]}
        self.service._access.list_accessible_course_ids.return_value = [3]

        self.service.list_tasks(user=user, course_id=3)

        self.service._access.require_course_access.assert_called_once_with(3, user)

    @patch("app.services.learning_service.user_repo.insert_operation_log_with_conn")
    @patch("app.services.learning_service.get_db_transaction")
    def test_student_completion_is_persisted_with_audit_log(
        self, get_transaction, insert_log
    ):
        user = {"user_id": 12, "roles": ["student_member"]}
        task = {"id": 19, "status": "assigned", "title": "事务练习"}
        self.service._repo.get_task.return_value = task
        self.service._repo.update_task_progress.return_value = 1
        transaction = MagicMock()
        conn = transaction.__enter__.return_value
        get_transaction.return_value = transaction

        result = self.service.update_task_status(user, 19, "completed")

        self.service._access.require_task_update_access.assert_called_once_with(19, user)
        self.service._repo.get_task.assert_called_once_with(19, student_id=12)
        self.service._repo.update_task_progress.assert_called_once_with(
            19, 12, "completed", conn=conn
        )
        insert_log.assert_called_once_with(
            user_id=12,
            action_type="learning_task:update_status",
            action_desc="学习任务状态: assigned -> completed",
            target_type="learning_task",
            target_id=19,
            project_id=None,
            task_id=None,
            conn=conn,
        )
        self.assertEqual(result["data"]["status"], "completed")

    def test_student_cannot_reverse_completed_task(self):
        user = {"user_id": 12, "roles": ["student_member"]}
        self.service._repo.get_task.return_value = {
            "id": 19,
            "status": "completed",
        }

        with self.assertRaises(ForbiddenException):
            self.service.update_task_status(user, 19, "in_progress")

        self.service._repo.update_task_progress.assert_not_called()


if __name__ == "__main__":
    unittest.main()
