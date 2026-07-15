import unittest
from unittest.mock import Mock, patch

from app.routers.learning import CreateLearningTaskRequest, create_learning_task
from app.services.learning_service import LearningService


class TaskIntegrityTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_validates_kps_and_assignee_before_write(self):
        access = Mock()
        service = Mock()
        service.create_task.return_value = {"code": 0, "data": {"id": 5}}
        user = {"user_id": 7, "roles": ["teacher"]}
        body = CreateLearningTaskRequest(
            course_id=3,
            title="任务",
            target_kp_ids=[4, 5],
            assignee_id=12,
            due_date="2026-07-20T18:30",
        )

        with patch("app.routers.learning.CourseAccessService", return_value=access), patch(
            "app.routers.learning.learning_service.LearningService",
            return_value=service,
        ):
            await create_learning_task(body, user)

        access.require_knowledge_points_course.assert_called_once_with(3, [4, 5])
        access.require_student_course.assert_called_once_with(3, 12)
        self.assertEqual(
            service.create_task.call_args.kwargs["due_date"],
            "2026-07-20 18:30:00",
        )

    def test_student_task_list_filters_private_assignees(self):
        service = LearningService()
        service._access = Mock()
        service._access.list_accessible_course_ids.return_value = [3]
        service._repo = Mock()
        service._repo.list_tasks.return_value = {"items": []}

        service.list_tasks({"user_id": 12, "roles": ["student_member"]})

        self.assertEqual(
            service._repo.list_tasks.call_args.kwargs["assignee_user_id"], 12
        )


if __name__ == "__main__":
    unittest.main()
