import unittest
from unittest.mock import patch

from app.routers import logs
from app.utils.exceptions import ForbiddenException, UnauthorizedException


class LogAccessTests(unittest.TestCase):
    @patch("app.routers.logs.auth_service.get_current_user")
    def test_admin_can_access_audit_logs(self, get_current_user):
        admin = {"user_id": 1, "roles": ["admin"]}
        get_current_user.return_value = admin

        self.assertEqual(logs._resolve_admin_user("Bearer token"), admin)

    @patch("app.routers.logs.auth_service.get_current_user")
    def test_student_cannot_access_audit_logs(self, get_current_user):
        get_current_user.return_value = {
            "user_id": 2,
            "roles": ["student_member"],
        }

        with self.assertRaises(ForbiddenException):
            logs._resolve_admin_user("Bearer token")

    @patch("app.routers.logs.auth_service.get_current_user")
    def test_teacher_cannot_access_platform_audit_logs(self, get_current_user):
        get_current_user.return_value = {"user_id": 3, "roles": ["teacher"]}

        with self.assertRaises(ForbiddenException):
            logs._resolve_admin_user("Bearer token")

    def test_missing_token_is_rejected(self):
        with self.assertRaises(UnauthorizedException):
            logs._resolve_admin_user(None)


if __name__ == "__main__":
    unittest.main()
