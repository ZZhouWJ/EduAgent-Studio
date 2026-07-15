import unittest
from unittest.mock import Mock, patch

from app.routers import feedbacks
from app.routers.feedbacks import SubmitFeedbackRequest
from app.utils.exceptions import ValidationException


class FeedbackIntegrityTests(unittest.IsolatedAsyncioTestCase):
    async def test_feedback_rejects_resource_course_mismatch(self):
        access = Mock()
        access.require_resource_access.return_value = 2
        user = {"user_id": 12, "roles": ["student_member"]}

        with patch("app.routers.feedbacks.CourseAccessService", return_value=access):
            with self.assertRaises(ValidationException):
                await feedbacks.submit_feedback(
                    SubmitFeedbackRequest(course_id=1, resource_id=9), user
                )

    async def test_self_mastery_is_normalized_and_uses_real_previous_value(self):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1]
        access.require_resource_access.return_value = 1
        profile = Mock()
        profile.get_profile_id_by_student_and_course.return_value = 22
        profile.get_mastery_level.return_value = 0.4
        profile.update_mastery.return_value = {
            "kp_id": 4,
            "kp_name": "事务",
            "mastery_level": 2 / 3,
        }
        profile.get_profile.return_value = {"profile_id": 22}
        resource = Mock()
        resource.get_resource.return_value = {"target_kp_ids": [4]}
        repo = Mock()
        repo.create_feedback.return_value = {"feedback_id": 5, "course_id": 1}
        learning = Mock()
        learning.recommend_resources.return_value = []
        user = {"user_id": 12, "roles": ["student_member"]}

        with patch("app.routers.feedbacks.CourseAccessService", return_value=access), patch.object(
            feedbacks, "_profile_repo", profile
        ), patch.object(feedbacks, "_resource_repo", resource), patch.object(
            feedbacks, "_repo", repo
        ), patch.object(feedbacks, "_learning_service", learning):
            response = await feedbacks.submit_feedback(
                SubmitFeedbackRequest(resource_id=9, self_mastery=2), user
            )

        profile.update_mastery.assert_called_once_with(
            22, 4, 2 / 3, "自评掌握度 2/3"
        )
        payload = __import__("json").loads(response.body)
        change = payload["data"]["mastery_changes"][0]
        self.assertEqual(change["before"], 0.4)
        self.assertEqual(change["after"], 0.67)


if __name__ == "__main__":
    unittest.main()
