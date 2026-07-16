import unittest
from unittest.mock import patch

from app.services import auth_service, user_service
from app.utils.exceptions import ForbiddenException, ValidationException


ROLES = [
    {"role_id": 1, "role_code": "student_member"},
    {"role_id": 2, "role_code": "project_leader"},
    {"role_id": 3, "role_code": "teacher"},
    {"role_id": 4, "role_code": "admin"},
]


class RoleSecurityTests(unittest.TestCase):
    @patch("app.services.auth_service.user_repo.list_roles", return_value=ROLES)
    def test_public_role_list_only_contains_student(self, _list_roles):
        roles = auth_service.list_roles_public()
        self.assertEqual([role["role_code"] for role in roles], ["student_member"])
        self.assertEqual(roles[0]["description"], "使用个性化辅导、学习路径、任务、资源与学习反馈。")

    @patch("app.services.auth_service.user_repo.list_roles", return_value=ROLES)
    def test_public_registration_cannot_select_teacher(self, _list_roles):
        with self.assertRaises(ValidationException):
            auth_service._validate_role_ids_for_user(  # noqa: SLF001
                [3], auth_service.PUBLIC_REGISTRATION_ROLE_CODES
            )

    @patch("app.services.auth_service.user_repo.list_roles", return_value=ROLES)
    def test_admin_cannot_assign_legacy_project_role(self, _list_roles):
        with self.assertRaises(ValidationException):
            auth_service._validate_role_ids_for_user(  # noqa: SLF001
                [2], auth_service.PLATFORM_ROLE_CODES
            )

    @patch("app.services.auth_service.get_current_user", return_value={"user_id": 7})
    def test_user_cannot_change_own_role(self, _get_current_user):
        with self.assertRaises(ForbiddenException):
            auth_service.update_my_roles("token", [3])

    @patch("app.services.user_service.user_repo.update_user_roles")
    @patch("app.services.user_service.user_repo.list_roles", return_value=ROLES)
    @patch("app.services.user_service.user_repo.get_user_by_id", return_value={"user_id": 9})
    def test_admin_role_update_rejects_legacy_role(
        self, _get_user, _list_roles, update_roles
    ):
        with self.assertRaises(ValidationException):
            user_service.update_user_roles_service(9, [2], actor_user_id=1)
        update_roles.assert_not_called()

    @patch("app.services.user_service.user_repo.update_user_roles")
    @patch("app.services.user_service.user_repo.get_user_roles", return_value=["admin"])
    @patch("app.services.user_service.user_repo.list_roles", return_value=ROLES)
    @patch("app.services.user_service.user_repo.get_user_by_id", return_value={"user_id": 4})
    def test_admin_cannot_remove_own_admin_role(
        self, _get_user, _list_roles, _get_roles, update_roles
    ):
        with self.assertRaisesRegex(ValidationException, "当前登录账号"):
            user_service.update_user_roles_service(4, [3], actor_user_id=4)

        update_roles.assert_not_called()

    @patch("app.services.user_service.user_repo.update_user_roles")
    @patch(
        "app.services.user_service.user_repo.count_active_users_with_role",
        return_value=1,
    )
    @patch("app.services.user_service.user_repo.get_user_roles", return_value=["admin"])
    @patch("app.services.user_service.user_repo.list_roles", return_value=ROLES)
    @patch("app.services.user_service.user_repo.get_user_by_id", return_value={"user_id": 4})
    def test_last_admin_role_cannot_be_removed(
        self, _get_user, _list_roles, _get_roles, _count_admins, update_roles
    ):
        with self.assertRaisesRegex(ValidationException, "至少一个启用的管理员"):
            user_service.update_user_roles_service(4, [3], actor_user_id=1)

        update_roles.assert_not_called()

    def test_capabilities_match_current_education_product(self):
        capabilities = user_service.list_permissions_service()
        codes = {item["permission_code"] for item in capabilities}
        self.assertIn("tutor:chat", codes)
        self.assertIn("resource:generate", codes)
        self.assertIn("content:govern", codes)
        self.assertFalse(any(code.startswith("project:") for code in codes))

    @patch(
        "app.services.user_service.user_repo.get_user_roles",
        return_value=["teacher"],
    )
    def test_user_permissions_are_derived_from_platform_role(self, _get_roles):
        permissions = user_service.get_user_permissions_service(7)
        self.assertIn("resource:generate", permissions)
        self.assertNotIn("user:manage", permissions)


if __name__ == "__main__":
    unittest.main()
