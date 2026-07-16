import unittest
from unittest.mock import patch

from app.routers.users import CreateUserBody, create_user, list_roles
from app.services.user_service import update_user_status_service
from app.utils.exceptions import ValidationException


class AdminUserTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.routers.users.auth_service.register")
    async def test_admin_create_records_authenticated_creator(self, register):
        register.return_value = {"user_id": 9, "username": "new_user"}

        response = await create_user(
            CreateUserBody(
                username="new_user",
                password="Test-Only-Password-123!",
                real_name="新用户",
                role_ids=[2],
            ),
            {"user_id": 1, "roles": ["admin"]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(register.call_args.kwargs["created_by"], 1)
        self.assertTrue(register.call_args.kwargs["allow_admin_role"])

    @patch("app.routers.users.user_service.list_roles_service")
    async def test_admin_role_list_includes_all_roles(self, list_all):
        list_all.return_value = [{"role_code": "admin"}]

        response = await list_roles({"user_id": 1, "roles": ["admin"]})

        self.assertEqual(response.status_code, 200)
        list_all.assert_called_once_with()

    @patch("app.services.user_service.user_repo.update_user_status")
    @patch("app.services.user_service.user_repo.get_user_roles", return_value=[])
    @patch("app.services.user_service.user_repo.get_user_by_id", return_value={"user_id": 9})
    def test_disabled_status_matches_database_contract(
        self, _get_user, _get_roles, update_status
    ):
        update_status.return_value = 1

        update_user_status_service(9, "disabled", actor_user_id=1)

        update_status.assert_called_once_with(9, "disabled")

    @patch("app.services.user_service.user_repo.update_user_status")
    @patch("app.services.user_service.user_repo.get_user_by_id", return_value={"user_id": 1})
    def test_admin_cannot_disable_current_account(self, _get_user, update_status):
        with self.assertRaisesRegex(ValidationException, "当前登录账号"):
            update_user_status_service(1, "disabled", actor_user_id=1)

        update_status.assert_not_called()

    @patch("app.services.user_service.user_repo.update_user_status")
    @patch(
        "app.services.user_service.user_repo.count_active_users_with_role",
        return_value=1,
    )
    @patch("app.services.user_service.user_repo.get_user_roles", return_value=["admin"])
    @patch("app.services.user_service.user_repo.get_user_by_id", return_value={"user_id": 9})
    def test_last_admin_cannot_be_disabled(
        self, _get_user, _get_roles, _count_admins, update_status
    ):
        with self.assertRaisesRegex(ValidationException, "至少一个启用的管理员"):
            update_user_status_service(9, "disabled", actor_user_id=1)

        update_status.assert_not_called()


if __name__ == "__main__":
    unittest.main()
