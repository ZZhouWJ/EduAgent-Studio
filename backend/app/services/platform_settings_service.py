"""平台级配置服务。"""

from typing import Any, Dict, Optional

from app.database import get_db_transaction
from app.repositories import user_repo
from app.repositories.platform_settings_repo import PlatformSettingsRepository
from app.services.content_safety_service import content_safety_policy

GOVERNANCE_SETTING_KEY = "governance.rules"
GOVERNANCE_DESCRIPTION = "内容治理阈值、调用限制与敏感内容检测配置"
BUDGET_ALERT_SETTING_KEY = "cost.budget_alert"
BUDGET_ALERT_DESCRIPTION = "平台月度模型调用预算与提醒阈值"

DEFAULT_GOVERNANCE_SETTINGS: Dict[str, Any] = {
    "fact_consistency_threshold": 80,
    "citation_coverage_threshold": 75,
    "hourly_call_limit": 50,
    "sensitive_content_enabled": True,
}

DEFAULT_BUDGET_ALERT_SETTINGS: Dict[str, Any] = {
    "monthly_budget": 10000.0,
    "alert_threshold_percent": 80,
    "enabled": True,
}


class PlatformSettingsService:
    def __init__(self) -> None:
        self._repo = PlatformSettingsRepository()

    def get_governance(self) -> Dict[str, Any]:
        setting = self._repo.get_setting(GOVERNANCE_SETTING_KEY)
        if setting is None:
            value = {
                **DEFAULT_GOVERNANCE_SETTINGS,
                "updated_by": None,
                "updated_at": None,
            }
            content_safety_policy.set_enabled(value["sensitive_content_enabled"])
            return value

        value = self._normalize_governance(setting.get("value"))
        result = {
            **value,
            "updated_by": setting.get("updated_by"),
            "updated_at": setting.get("updated_at"),
        }
        content_safety_policy.set_enabled(result["sensitive_content_enabled"])
        return result

    def update_governance(
        self,
        user: Dict[str, Any],
        fact_consistency_threshold: int,
        citation_coverage_threshold: int,
        hourly_call_limit: int,
        sensitive_content_enabled: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        value = {
            "fact_consistency_threshold": fact_consistency_threshold,
            "citation_coverage_threshold": citation_coverage_threshold,
            "hourly_call_limit": hourly_call_limit,
            "sensitive_content_enabled": sensitive_content_enabled,
        }
        with get_db_transaction() as conn:
            self._repo.upsert_setting(
                setting_key=GOVERNANCE_SETTING_KEY,
                value=value,
                description=GOVERNANCE_DESCRIPTION,
                updated_by=int(user["user_id"]),
                conn=conn,
            )
            user_repo.insert_operation_log_with_conn(
                user_id=int(user["user_id"]),
                action_type="governance:update",
                action_desc=(
                    "更新内容治理规则: "
                    f"事实一致性 {fact_consistency_threshold}%, "
                    f"引用覆盖率 {citation_coverage_threshold}%, "
                    f"调用上限 {hourly_call_limit} 次/小时, "
                    f"敏感检测 {'启用' if sensitive_content_enabled else '停用'}"
                ),
                target_type="platform_setting",
                target_id=None,
                project_id=None,
                task_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                conn=conn,
            )
        content_safety_policy.set_enabled(sensitive_content_enabled)
        return value

    def get_budget_alert(self) -> Dict[str, Any]:
        setting = self._repo.get_setting(BUDGET_ALERT_SETTING_KEY)
        if setting is None:
            return {
                **DEFAULT_BUDGET_ALERT_SETTINGS,
                "updated_by": None,
                "updated_at": None,
            }

        value = self._normalize_budget_alert(setting.get("value"))
        return {
            **value,
            "updated_by": setting.get("updated_by"),
            "updated_at": setting.get("updated_at"),
        }

    def update_budget_alert(
        self,
        user: Dict[str, Any],
        monthly_budget: float,
        alert_threshold_percent: int,
        enabled: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        value = {
            "monthly_budget": float(monthly_budget),
            "alert_threshold_percent": alert_threshold_percent,
            "enabled": enabled,
        }
        with get_db_transaction() as conn:
            self._repo.upsert_setting(
                setting_key=BUDGET_ALERT_SETTING_KEY,
                value=value,
                description=BUDGET_ALERT_DESCRIPTION,
                updated_by=int(user["user_id"]),
                conn=conn,
            )
            user_repo.insert_operation_log_with_conn(
                user_id=int(user["user_id"]),
                action_type="cost_budget:update",
                action_desc=(
                    "更新成本预算提醒: "
                    f"月度预算 ¥{monthly_budget:.2f}, "
                    f"阈值 {alert_threshold_percent}%, "
                    f"提醒 {'启用' if enabled else '停用'}"
                ),
                target_type="platform_setting",
                target_id=None,
                project_id=None,
                task_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                conn=conn,
            )
        return value

    @staticmethod
    def _normalize_governance(value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            return dict(DEFAULT_GOVERNANCE_SETTINGS)

        normalized = dict(DEFAULT_GOVERNANCE_SETTINGS)
        fact_threshold = value.get("fact_consistency_threshold")
        citation_threshold = value.get("citation_coverage_threshold")
        hourly_limit = value.get("hourly_call_limit")
        sensitive_enabled = value.get("sensitive_content_enabled")

        if isinstance(fact_threshold, int) and 0 <= fact_threshold <= 100:
            normalized["fact_consistency_threshold"] = fact_threshold
        if isinstance(citation_threshold, int) and 0 <= citation_threshold <= 100:
            normalized["citation_coverage_threshold"] = citation_threshold
        if isinstance(hourly_limit, int) and 1 <= hourly_limit <= 10000:
            normalized["hourly_call_limit"] = hourly_limit
        if isinstance(sensitive_enabled, bool):
            normalized["sensitive_content_enabled"] = sensitive_enabled
        return normalized

    @staticmethod
    def _normalize_budget_alert(value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            return dict(DEFAULT_BUDGET_ALERT_SETTINGS)

        normalized = dict(DEFAULT_BUDGET_ALERT_SETTINGS)
        monthly_budget = value.get("monthly_budget")
        alert_threshold = value.get("alert_threshold_percent")
        enabled = value.get("enabled")

        if (
            isinstance(monthly_budget, (int, float))
            and not isinstance(monthly_budget, bool)
            and 0 < monthly_budget <= 1_000_000_000
        ):
            normalized["monthly_budget"] = float(monthly_budget)
        if (
            isinstance(alert_threshold, int)
            and not isinstance(alert_threshold, bool)
            and 1 <= alert_threshold <= 100
        ):
            normalized["alert_threshold_percent"] = alert_threshold
        if isinstance(enabled, bool):
            normalized["enabled"] = enabled
        return normalized
