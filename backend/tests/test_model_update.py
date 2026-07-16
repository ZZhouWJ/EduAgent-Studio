import unittest
from unittest.mock import MagicMock, patch

from app.services import model_service
from app.utils.exceptions import ValidationException


class ModelUpdateTests(unittest.TestCase):
    @patch("app.services.model_service._require_auth", return_value={"user_id": 1, "roles": ["admin"]})
    @patch("app.services.model_service.model_repo.get_model_by_id", return_value={"model_id": 5})
    @patch("app.services.model_service.user_repo.insert_operation_log_with_conn")
    @patch("app.services.model_service.model_repo.update_model", return_value=1)
    @patch("app.services.model_service.get_db_transaction")
    def test_admin_update_is_persisted_and_audited(
        self,
        transaction,
        update_model,
        insert_log,
        _get_model,
        _require_auth,
    ):
        conn = MagicMock()
        transaction.return_value.__enter__.return_value = conn

        result = model_service.update_model(
            token="token",
            model_id=5,
            display_name="星火 Max",
            capability_tags="文本生成,教学问答",
            max_context=32768,
            input_price=0.01,
            output_price=0.02,
            price_unit="1K_TOKENS",
            status="active",
        )

        self.assertEqual(result, {"model_id": 5})
        update_model.assert_called_once()
        insert_log.assert_called_once()
        conn.commit.assert_called_once()

    @patch("app.services.model_service._require_auth", return_value={"user_id": 1, "roles": ["admin"]})
    @patch("app.services.model_service.model_repo.get_model_by_id", return_value={"model_id": 5})
    def test_invalid_status_is_rejected(self, _get_model, _require_auth):
        with self.assertRaises(ValidationException):
            model_service.update_model(
                token="token",
                model_id=5,
                display_name="模型",
                capability_tags=None,
                max_context=4096,
                input_price=0,
                output_price=0,
                price_unit="1K_TOKENS",
                status="inactive",
            )


if __name__ == "__main__":
    unittest.main()
