"""平台级配置数据访问。"""

import json
from typing import Any, Dict, Optional

from pymysql.connections import Connection

from app.database import get_db_cursor


class PlatformSettingsRepository:
    def get_setting(self, setting_key: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT setting_key, setting_value, description, updated_by, updated_at
            FROM platform_settings
            WHERE setting_key = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (setting_key,))
            row = cursor.fetchone()
        if row is None:
            return None

        value = row["setting_value"]
        if isinstance(value, str):
            value = json.loads(value)
        return {
            "setting_key": row["setting_key"],
            "value": value,
            "description": row["description"],
            "updated_by": row["updated_by"],
            "updated_at": row["updated_at"],
        }

    def upsert_setting(
        self,
        setting_key: str,
        value: Dict[str, Any],
        description: str,
        updated_by: int,
        conn: Connection,
    ) -> None:
        sql = """
            INSERT INTO platform_settings
                (setting_key, setting_value, description, updated_by, updated_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                setting_value = VALUES(setting_value),
                description = VALUES(description),
                updated_by = VALUES(updated_by),
                updated_at = NOW()
        """
        cursor = conn.cursor()
        try:
            cursor.execute(
                sql,
                (
                    setting_key,
                    json.dumps(value, ensure_ascii=False),
                    description,
                    updated_by,
                ),
            )
        finally:
            cursor.close()
