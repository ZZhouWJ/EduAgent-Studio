import unittest
from unittest.mock import MagicMock, Mock, patch

from app.services.platform_settings_service import (
    BUDGET_ALERT_DESCRIPTION,
    BUDGET_ALERT_SETTING_KEY,
    DEFAULT_BUDGET_ALERT_SETTINGS,
    DEFAULT_GOVERNANCE_SETTINGS,
    GOVERNANCE_DESCRIPTION,
    GOVERNANCE_SETTING_KEY,
    PlatformSettingsService,
)


class PlatformSettingsServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = PlatformSettingsService()
        self.service._repo = Mock()

    def test_governance_defaults_are_returned_when_setting_is_missing(self):
        self.service._repo.get_setting.return_value = None

        result = self.service.get_governance()

        for key, value in DEFAULT_GOVERNANCE_SETTINGS.items():
            self.assertEqual(result[key], value)
        self.assertIsNone(result["updated_at"])

    def test_invalid_stored_values_fall_back_to_safe_defaults(self):
        self.service._repo.get_setting.return_value = {
            "value": {
                "fact_consistency_threshold": 150,
                "citation_coverage_threshold": "75",
                "hourly_call_limit": 0,
                "sensitive_content_enabled": "true",
            },
            "updated_by": 1,
            "updated_at": "2026-07-16 12:00:00",
        }

        result = self.service.get_governance()

        for key, value in DEFAULT_GOVERNANCE_SETTINGS.items():
            self.assertEqual(result[key], value)

    @patch(
        "app.services.platform_settings_service."
        "user_repo.insert_operation_log_with_conn"
    )
    @patch("app.services.platform_settings_service.get_db_transaction")
    def test_governance_update_is_persisted_and_audited(
        self, get_transaction, insert_log
    ):
        transaction = MagicMock()
        conn = transaction.__enter__.return_value
        get_transaction.return_value = transaction
        user = {"user_id": 1, "roles": ["admin"]}
        expected = {
            "fact_consistency_threshold": 85,
            "citation_coverage_threshold": 78,
            "hourly_call_limit": 60,
            "sensitive_content_enabled": False,
        }

        result = self.service.update_governance(user=user, **expected)

        self.service._repo.upsert_setting.assert_called_once_with(
            setting_key=GOVERNANCE_SETTING_KEY,
            value=expected,
            description=GOVERNANCE_DESCRIPTION,
            updated_by=1,
            conn=conn,
        )
        self.assertEqual(insert_log.call_args.kwargs["action_type"], "governance:update")
        self.assertEqual(insert_log.call_args.kwargs["conn"], conn)
        self.assertEqual(result, expected)

    def test_budget_alert_defaults_are_returned_when_setting_is_missing(self):
        self.service._repo.get_setting.return_value = None

        result = self.service.get_budget_alert()

        for key, value in DEFAULT_BUDGET_ALERT_SETTINGS.items():
            self.assertEqual(result[key], value)
        self.assertIsNone(result["updated_at"])

    @patch(
        "app.services.platform_settings_service."
        "user_repo.insert_operation_log_with_conn"
    )
    @patch("app.services.platform_settings_service.get_db_transaction")
    def test_budget_alert_update_is_persisted_and_audited(
        self, get_transaction, insert_log
    ):
        transaction = MagicMock()
        conn = transaction.__enter__.return_value
        get_transaction.return_value = transaction
        user = {"user_id": 1, "roles": ["admin"]}
        expected = {
            "monthly_budget": 12000.0,
            "alert_threshold_percent": 75,
            "enabled": False,
        }

        result = self.service.update_budget_alert(user=user, **expected)

        self.service._repo.upsert_setting.assert_called_once_with(
            setting_key=BUDGET_ALERT_SETTING_KEY,
            value=expected,
            description=BUDGET_ALERT_DESCRIPTION,
            updated_by=1,
            conn=conn,
        )
        self.assertEqual(
            insert_log.call_args.kwargs["action_type"], "cost_budget:update"
        )
        self.assertEqual(insert_log.call_args.kwargs["conn"], conn)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
