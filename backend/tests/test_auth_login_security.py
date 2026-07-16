import asyncio
import json
import unittest
from unittest.mock import Mock, patch

from app.routers.auth import LoginRequest, login as login_route
from app.services import auth_service


class LoginRateLimitTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
