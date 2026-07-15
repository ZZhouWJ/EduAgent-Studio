import unittest
from unittest.mock import Mock, patch

from app.routers.learning import CreateLearningTaskRequest, create_learning_task
from app.routers import feedbacks


class AuthenticatedContextTests(unittest.IsolatedAsyncioTestCase):
    async def test_learning_task_uses_authenticated_creator_id(self):
        service = Mock()
        service.create_task.return_value = {"code": 0, "data": {"task_id": 9}}

        with patch("app.routers.learning.CourseAccessService"), patch(
            "app.routers.learning.learning_service.LearningService",
            return_value=service,
        ):
            result = await create_learning_task(
                CreateLearningTaskRequest(course_id=1, title="事务练习"),
                {"user_id": 42, "roles": ["teacher"]},
            )

        self.assertEqual(result["code"], 0)
        self.assertEqual(service.create_task.call_args.kwargs["creator_id"], 42)

    async def test_student_feedback_list_is_scoped_to_authenticated_user(self):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1]
        with patch("app.routers.feedbacks.CourseAccessService", return_value=access), patch.object(
            feedbacks._repo, "list_feedbacks", return_value={"items": []}
        ) as query:
            await feedbacks.list_feedbacks(
                page=1,
                page_size=20,
                course_id=None,
                feedback_type=None,
                user={"user_id": 42, "roles": ["student_member"]},
            )

        self.assertEqual(query.call_args.kwargs["student_id"], 42)
        self.assertEqual(query.call_args.kwargs["course_ids"], [1])

    async def test_staff_feedback_list_can_cover_the_course(self):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1]
        with patch("app.routers.feedbacks.CourseAccessService", return_value=access), patch.object(
            feedbacks._repo, "list_feedbacks", return_value={"items": []}
        ) as query:
            await feedbacks.list_feedbacks(
                page=1,
                page_size=20,
                course_id=1,
                feedback_type=None,
                user={"user_id": 7, "roles": ["teacher"]},
            )

        self.assertIsNone(query.call_args.kwargs["student_id"])
        access.require_course_access.assert_called_once()


if __name__ == "__main__":
    unittest.main()
