import unittest

from app.services import prompt_service


class PromptContractTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
