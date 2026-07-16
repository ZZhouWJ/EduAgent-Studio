import json
import unittest
from unittest.mock import Mock, patch

from app.routers.learning import CreateLearningTaskRequest, create_learning_task
from app.routers import feedbacks
from app.routers.auth import get_me
from app.services import auth_service


class ActiveSessionTests(unittest.TestCase):
    def test_disabled_user_cannot_restore_an_existing_session(self):
        user = {
            "user_id": 42,
            "username": "disabled-user",
            "real_name": "Disabled User",
            "student_no": None,
            "email": None,
            "phone": None,
            "status": "disabled",
            "last_login_at": None,
        }

        with patch.object(
            auth_service,
            "decode_access_token",
            return_value={"user_id": 42, "jti": "session-42"},
        ), patch.object(
            auth_service.user_repo,
            "get_user_by_id",
            return_value=user,
        ), patch.object(
            auth_service.user_repo,
            "get_user_roles",
        ) as get_roles:
            result = auth_service.get_current_user("existing-token")

        self.assertIsNone(result)
        get_roles.assert_not_called()

    def test_revoked_session_cannot_restore_an_active_user(self):
        user = {
            "user_id": 42,
            "username": "active-user",
            "real_name": "Active User",
            "student_no": None,
            "email": None,
            "phone": None,
            "status": "active",
            "last_login_at": None,
        }

        with patch.object(
            auth_service,
            "decode_access_token",
            return_value={"user_id": 42, "jti": "revoked-session"},
        ), patch.object(
            auth_service.user_repo,
            "get_user_by_id",
            return_value=user,
        ), patch.object(
            auth_service.user_repo,
            "is_auth_session_active",
            return_value=False,
        ), patch.object(
            auth_service.user_repo,
            "get_user_roles",
        ) as get_roles:
            result = auth_service.get_current_user("revoked-token")

        self.assertIsNone(result)
        get_roles.assert_not_called()

    @patch.object(auth_service.user_repo, "insert_operation_log")
    @patch.object(auth_service.user_repo, "revoke_auth_session")
    @patch.object(
        auth_service,
        "decode_access_token",
        return_value={"user_id": 42, "jti": "session-42"},
    )
    def test_logout_revokes_current_session(self, _decode, revoke, _log):
        auth_service.logout(token="access-token", user_id=42)

        revoke.assert_called_once_with("session-42", 42, reason="logout")


class AuthenticatedContextTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.routers.auth.auth_service.get_current_user", return_value=None)
    async def test_invalid_session_returns_http_401(self, _get_current_user):
        response = await get_me("Bearer revoked-token")
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["code"], 4002)

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
                student_id=None,
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
                student_id=None,
                feedback_type=None,
                user={"user_id": 7, "roles": ["teacher"]},
            )

        self.assertIsNone(query.call_args.kwargs["student_id"])
        access.require_course_access.assert_called_once()


if __name__ == "__main__":
    unittest.main()
