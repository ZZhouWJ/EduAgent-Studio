import asyncio
import json
import unittest
from unittest.mock import Mock, patch

from app.routers.auth import LoginRequest, login as login_route
from app.services import auth_service
from app.utils.exceptions import ValidationException
from app.utils.password import MAX_PASSWORD_BYTES, get_password_policy_error, hash_password


class LoginRateLimitTests(unittest.TestCase):
    def test_successful_login_persists_the_token_session(self):
        user = {
            "user_id": 7,
            "username": "student",
            "real_name": "Student",
            "status": "active",
            "password_hash": "stored-hash",
        }
        settings = Mock(jwt_expire_minutes=30)

        with patch.object(
            auth_service.user_repo,
            "count_recent_failed_login_attempts",
            return_value=0,
        ), patch.object(
            auth_service.user_repo,
            "get_user_by_username",
            return_value=user,
        ), patch.object(
            auth_service,
            "verify_password",
            return_value=True,
        ), patch.object(
            auth_service.user_repo,
            "update_user_last_login",
        ), patch.object(
            auth_service.user_repo,
            "get_user_roles",
            return_value=["student_member"],
        ), patch.object(
            auth_service,
            "get_settings",
            return_value=settings,
        ), patch.object(
            auth_service,
            "uuid4",
            return_value=Mock(hex="session-7"),
        ), patch.object(
            auth_service,
            "create_access_token",
            return_value="access-token",
        ) as create_token, patch.object(
            auth_service.user_repo,
            "create_auth_session",
        ) as create_session, patch.object(
            auth_service.user_repo,
            "insert_login_log",
        ):
            result = auth_service.login("student", "valid-password")

        self.assertTrue(result["success"])
        self.assertEqual(
            create_token.call_args.kwargs["data"]["jti"],
            "session-7",
        )
        self.assertEqual(create_session.call_args.kwargs["session_id"], "session-7")
        self.assertEqual(create_session.call_args.kwargs["user_id"], 7)

    @patch.object(auth_service.user_repo, "insert_login_log")
    @patch.object(auth_service.user_repo, "get_user_by_username")
    @patch.object(auth_service.user_repo, "count_recent_failed_login_attempts")
    def test_service_blocks_repeated_failures_before_password_lookup(
        self,
        count_failures,
        get_user,
        insert_log,
    ):
        count_failures.return_value = auth_service.MAX_FAILED_LOGIN_ATTEMPTS

        result = auth_service.login("  student_zhang  ", "wrong-password")

        self.assertFalse(result["success"])
        self.assertTrue(result["rate_limited"])
        self.assertEqual(result["retry_after_seconds"], 15 * 60)
        count_failures.assert_called_once()
        self.assertEqual(count_failures.call_args.kwargs["username"], "student_zhang")
        get_user.assert_not_called()
        insert_log.assert_called_once()

    @patch("app.routers.auth.auth_service.login")
    def test_route_returns_http_429_and_retry_after(self, service_login):
        service_login.return_value = {
            "success": False,
            "reason": "登录尝试过多，请 15 分钟后重试",
            "rate_limited": True,
            "retry_after_seconds": 900,
        }
        request = Mock()
        request.headers = {}
        request.client = None

        response = asyncio.run(
            login_route(request, LoginRequest(username="student", password="wrong"))
        )
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "900")
        self.assertEqual(payload["code"], 4290)


class PasswordBoundaryTests(unittest.TestCase):
    def test_new_password_requires_eight_characters(self):
        self.assertEqual(
            get_password_policy_error("Abc123!"),
            "密码至少需要 8 个字符",
        )

    def test_new_password_enforces_bcrypt_utf8_byte_limit(self):
        password = "学" * 25

        self.assertGreater(len(password.encode("utf-8")), MAX_PASSWORD_BYTES)
        self.assertIn("密码过长", get_password_policy_error(password) or "")
        with self.assertRaises(ValueError):
            hash_password(password)

    @patch.object(auth_service.user_repo, "check_username_exists", return_value=False)
    def test_registration_rejects_overlong_utf8_password(self, _username_exists):
        password = "学" * 25

        with self.assertRaisesRegex(ValidationException, "密码过长"):
            auth_service.register(
                username="new_student",
                password=password,
                confirm_password=password,
                real_name="新学生",
            )

    @patch.object(auth_service.user_repo, "insert_login_log")
    @patch.object(auth_service.user_repo, "get_user_by_username")
    @patch.object(auth_service.user_repo, "count_recent_failed_login_attempts", return_value=0)
    def test_login_treats_overlong_utf8_password_as_invalid(
        self,
        _count_failures,
        get_user,
        insert_log,
    ):
        get_user.return_value = {
            "user_id": 7,
            "username": "student",
            "status": "active",
            "password_hash": hash_password("Valid-Pass-123"),
        }

        result = auth_service.login("student", "学" * 25)

        self.assertEqual(result, {"success": False, "reason": "用户名或密码错误"})
        insert_log.assert_called_once()


if __name__ == "__main__":
    unittest.main()
