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

    def test_stream_session_checks_profile_course_before_saving(self):
        self.service._access.require_profile_course.side_effect = RuntimeError("denied")
        self.service._save_session = Mock()

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.save_stream_session(22, 3, "question", "answer", self.user)

        self.service._save_session.assert_not_called()

    def test_stream_session_persists_final_answer(self):
        self.service._save_session = Mock(return_value=91)

        session_id = self.service.save_stream_session(
            22,
            3,
            "question",
            "grounded answer",
            self.user,
        )

        self.assertEqual(session_id, 91)
        self.service._save_session.assert_called_once_with(
            profile_id=22,
            course_id=3,
            question="question",
            answer_data={"answer": "grounded answer", "explanation_level": "intermediate"},
        )

    def test_session_history_checks_profile_access(self):
        self.service._access.require_profile_access.side_effect = RuntimeError("denied")

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.get_sessions(22, user=self.user)

    def test_suggestions_check_profile_course(self):
        self.service._access.require_profile_course.side_effect = RuntimeError("denied")

        with self.assertRaisesRegex(RuntimeError, "denied"):
            self.service.get_suggestions(3, profile_id=22, user=self.user)

    def test_suggestions_fall_back_when_model_returns_invalid_json(self):
        self.service._get_course_knowledge_points = Mock(return_value=[
            {"kp_id": 1, "name": "事务隔离"},
            {"kp_id": 2, "name": "并发控制"},
        ])
        self.service._profile_repo.get_profile.return_value = {"weak_points": []}
        self.service._llm_gateway = Mock()
        self.service._llm_gateway.generate.return_value = Mock(
            content="[事务隔离怎么学？, 并发控制怎么学？]",
        )

        result = self.service.get_suggestions(3, profile_id=22, user=self.user)

        self.assertEqual(result["code"], 0)
        self.assertEqual(len(result["data"]["suggestions"]), 4)
        self.assertIn("事务隔离", result["data"]["suggestions"][0])


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
