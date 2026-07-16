import unittest
from unittest.mock import Mock

from pydantic import ValidationError

from app.routers.tutor import ChatRequest, FeedbackRequest
from app.services.tutor_service import TutorService


class TutorAccessTests(unittest.TestCase):
    def setUp(self):
        self.service = TutorService()
        self.service._access = Mock()
        self.service._profile_repo = Mock()
        self.service._knowledge_repo = Mock()
        self.user = {"user_id": 12, "roles": ["student_member"]}

    def test_chat_checks_profile_course_before_loading_data(self):
        self.service._access.require_profile_course.side_effect = RuntimeError("denied")

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.chat(22, 3, "question", self.user)

        self.service._profile_repo.get_profile.assert_not_called()

    def test_feedback_checks_session_before_update(self):
        self.service._access.require_tutor_session_access.side_effect = RuntimeError(
            "denied"
        )

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.submit_feedback(5, True, user=self.user)

    def test_session_history_checks_profile_access(self):
        self.service._access.require_profile_access.side_effect = RuntimeError("denied")

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.get_sessions(22, user=self.user)

    def test_suggestions_check_profile_course(self):
        self.service._access.require_profile_course.side_effect = RuntimeError("denied")

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.get_suggestions(3, profile_id=22, user=self.user)


class TutorRequestValidationTests(unittest.TestCase):
    def test_chat_normalizes_question_and_accepts_supported_content(self):
        request = ChatRequest(
            profile_id=3,
            course_id=5,
            question="  解释事务隔离级别  ",
            requested_content_types=["mindmap", "quiz"],
        )

        self.assertEqual(request.question, "解释事务隔离级别")

    def test_chat_rejects_unbounded_or_unknown_prompt_content(self):
        with self.assertRaises(ValidationError):
            ChatRequest(profile_id=3, course_id=5, question="x" * 4001)
        with self.assertRaises(ValidationError):
            ChatRequest(
                profile_id=3,
                course_id=5,
                question="测试",
                requested_content_types=["executable_html"],
            )
        with self.assertRaises(ValidationError):
            ChatRequest(profile_id=0, course_id=5, question="测试")

    def test_feedback_rejects_invalid_session_and_oversized_follow_up(self):
        with self.assertRaises(ValidationError):
            FeedbackRequest(session_id=0, helpful=True)
        with self.assertRaises(ValidationError):
            FeedbackRequest(session_id=1, helpful=False, follow_up="x" * 2001)


if __name__ == "__main__":
    unittest.main()
