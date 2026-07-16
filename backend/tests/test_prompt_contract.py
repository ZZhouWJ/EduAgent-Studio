import unittest
from unittest.mock import patch

from app.services import prompt_service
from app.utils.exceptions import NotFoundException, ValidationException


class PromptContractTests(unittest.TestCase):
    @patch("app.services.prompt_service.user_repo.insert_operation_log_with_conn")
    @patch("app.services.prompt_service.prompt_repo.get_template_by_id")
    @patch("app.services.prompt_service.prompt_repo.set_current_version")
    @patch("app.services.prompt_service.prompt_repo.create_version")
    @patch("app.services.prompt_service.prompt_repo.create_template")
    @patch("app.services.prompt_service.prompt_repo.get_task_type_by_id")
    @patch("app.services.prompt_service.get_db_transaction")
    @patch("app.services.prompt_service._require_auth")
    def test_create_template_persists_initial_version_and_activation(
        self,
        require_auth,
        get_transaction,
        get_task_type,
        create_template,
        create_version,
        set_current_version,
        get_template,
        insert_log,
    ):
        require_auth.return_value = {"user_id": 1, "roles": ["admin"]}
        get_task_type.return_value = {"task_type_id": 3}
        transaction = get_transaction.return_value.__enter__.return_value
        create_template.return_value = 7
        create_version.return_value = 19
        get_template.return_value = {
            "template_id": 7,
            "template_name": "学习诊断",
            "task_type_id": 3,
            "is_active": 1,
        }

        prompt_service.create_template(
            token="token",
            template_name="  学习诊断  ",
            task_type_id=3,
            description="  诊断薄弱点  ",
            initial_prompt_content="  分析 {{profile}}  ",
            activate=True,
        )

        create_template.assert_called_once_with(
            template_name="学习诊断",
            task_type_id=3,
            description="诊断薄弱点",
            created_by=1,
            is_active=True,
            conn=transaction,
        )
        create_version.assert_called_once_with(
            template_id=7,
            version_no="1",
            prompt_content="分析 {{profile}}",
            change_note="初始版本",
            created_by=1,
            conn=transaction,
        )
        set_current_version.assert_called_once_with(
            template_id=7,
            version_id=19,
            conn=transaction,
        )
        self.assertEqual(insert_log.call_args.kwargs["conn"], transaction)
        transaction.commit.assert_called_once()

    @patch("app.services.prompt_service.prompt_repo.get_task_type_by_id")
    @patch("app.services.prompt_service._require_auth")
    def test_create_template_cannot_activate_without_version(
        self, require_auth, get_task_type
    ):
        require_auth.return_value = {"user_id": 1, "roles": ["admin"]}

        with self.assertRaises(ValidationException):
            prompt_service.create_template(
                token="token",
                template_name="空模板",
                task_type_id=3,
                activate=True,
            )

        get_task_type.assert_not_called()

    def test_template_row_exposes_current_version_and_update_time(self):
        result = prompt_service._template_row_to_dict({
            "template_id": 7,
            "template_name": "资源生成",
            "task_type_id": 2,
            "type_name": "资源生成",
            "type_code": "resource_generation",
            "current_version_id": 11,
            "current_version_no": "3",
            "is_active": 1,
            "created_at": "created",
            "updated_at": "updated",
            "created_by": 1,
        })

        self.assertEqual(result["current_version_id"], 11)
        self.assertEqual(result["current_version_no"], "3")
        self.assertEqual(result["updated_at"], "updated")

    def test_version_row_uses_database_version_identifier(self):
        result = prompt_service._version_row_to_dict({
            "prompt_version_id": 19,
            "template_id": 7,
            "version_no": "4",
            "is_active": 1,
        })

        self.assertEqual(result["prompt_version_id"], 19)
        self.assertTrue(result["is_active"])
        self.assertNotIn("version_id", result)

    @patch("app.services.prompt_service.prompt_repo.get_version_by_id")
    @patch("app.services.prompt_service.prompt_repo.get_template_by_id")
    @patch("app.services.prompt_service._require_auth")
    def test_render_template_replaces_declared_variables_only(
        self, require_auth, get_template, get_version
    ):
        get_template.return_value = {"current_version_id": 19}
        get_version.return_value = {
            "prompt_version_id": 19,
            "version_no": "4",
            "prompt_content": "课程：{{ course }}\n目标：{{goal}}\n重复：{{ goal }}",
        }

        result = prompt_service.render_template(
            token="token",
            template_id=7,
            variables={"course": "数据库", "goal": "掌握索引"},
        )

        require_auth.assert_called_once_with("token")
        self.assertEqual(result["required_variables"], ["course", "goal"])
        self.assertEqual(result["missing_variables"], [])
        self.assertEqual(result["rendered_content"], "课程：数据库\n目标：掌握索引\n重复：掌握索引")

    @patch("app.services.prompt_service.prompt_repo.get_version_by_id")
    @patch("app.services.prompt_service.prompt_repo.get_template_by_id")
    @patch("app.services.prompt_service._require_auth")
    def test_render_template_keeps_missing_placeholders(
        self, require_auth, get_template, get_version
    ):
        get_template.return_value = {"current_version_id": 19}
        get_version.return_value = {
            "prompt_version_id": 19,
            "version_no": "4",
            "prompt_content": "{{course}} / {{goal}}",
        }

        result = prompt_service.render_template(
            token="token",
            template_id=7,
            variables={"course": "数据库"},
        )

        self.assertEqual(result["missing_variables"], ["goal"])
        self.assertEqual(result["rendered_content"], "数据库 / {{goal}}")

    @patch("app.services.prompt_service.prompt_repo.get_version_by_id")
    @patch("app.services.prompt_service.prompt_repo.get_template_by_id")
    @patch("app.services.prompt_service._require_auth")
    def test_render_template_rejects_unknown_variables(
        self, require_auth, get_template, get_version
    ):
        get_template.return_value = {"current_version_id": 19}
        get_version.return_value = {
            "prompt_version_id": 19,
            "version_no": "4",
            "prompt_content": "{{course}}",
        }

        with self.assertRaises(ValidationException):
            prompt_service.render_template(
                token="token",
                template_id=7,
                variables={"typo": "数据库"},
            )

    @patch("app.services.prompt_service.prompt_repo.get_version_by_template_and_id")
    @patch("app.services.prompt_service.prompt_repo.get_template_by_id")
    @patch("app.services.prompt_service._require_auth")
    def test_render_template_rejects_version_from_another_template(
        self, require_auth, get_template, get_owned_version
    ):
        get_template.return_value = {"current_version_id": 19}
        get_owned_version.return_value = None

        with self.assertRaises(NotFoundException):
            prompt_service.render_template(
                token="token",
                template_id=7,
                version_id=23,
                variables={},
            )


if __name__ == "__main__":
    unittest.main()
