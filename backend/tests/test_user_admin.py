import unittest
from unittest.mock import patch

from app.routers.users import CreateUserBody, create_user, list_roles
from app.services.user_service import update_user_status_service


class AdminUserTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.routers.users.auth_service.register")
    async def test_admin_create_records_authenticated_creator(self, register):
        register.return_value = {"user_id": 9, "username": "new_user"}

        response = await create_user(
            CreateUserBody(
                username="new_user",
                password="Pass@1234",
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
    def test_disabled_status_matches_database_contract(self, update_status):
        update_status.return_value = 1

        update_user_status_service(9, "disabled")

        update_status.assert_called_once_with(9, "disabled")


if __name__ == "__main__":
    unittest.main()
