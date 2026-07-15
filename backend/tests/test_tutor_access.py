import unittest
from unittest.mock import Mock

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


if __name__ == "__main__":
    unittest.main()
