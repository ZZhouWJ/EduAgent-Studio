"""
学生画像对话 Repository

负责 profile_dialog_messages 和 profile_update_history 表的数据访问。
所有 SQL 使用参数化查询，不拼接用户输入。
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.database import get_db_cursor, get_db_transaction
from app.repositories.profile_repo import PROFILE_MUTABLE_FIELDS


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


class ProfileDialogRepository:
    """学生画像对话数据访问层。"""

    def create_message(
        self,
        profile_id: int,
        role: str,
        content: str,
        extracted_json: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        创建对话消息记录。

        Args:
            profile_id: 画像 ID
            role: 角色，student 或 assistant
            content: 消息内容
            extracted_json: 抽取的结构化数据（可选）

        Returns:
            新创建的消息 ID
        """
        sql = """
            INSERT INTO profile_dialog_messages
                (profile_id, role, content, extracted_json, is_applied)
            VALUES (%s, %s, %s, %s, 0)
        """
        extracted_str = json.dumps(extracted_json) if extracted_json is not None else None
        with get_db_cursor() as cursor:
            cursor.execute(sql, (profile_id, role, content, extracted_str))
            return cursor.lastrowid

    def get_dialog_history(
        self, profile_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史。

        Args:
            profile_id: 画像 ID
            limit: 返回条数限制

        Returns:
            对话消息列表（按时间正序）
        """
        sql = """
            SELECT
                message_id,
                profile_id,
                role,
                content,
                extracted_json,
                is_applied,
                created_at
            FROM profile_dialog_messages
            WHERE profile_id = %s AND is_deleted = 0
            ORDER BY created_at ASC
            LIMIT %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (profile_id, limit))
            rows = cursor.fetchall()

        result = []
        for row in rows:
            extracted = None
            if row.get("extracted_json"):
                try:
                    extracted = json.loads(row["extracted_json"])
                except Exception:
                    pass

            result.append({
                "message_id": row["message_id"],
                "profile_id": row["profile_id"],
                "role": row["role"],
                "content": row["content"],
                "extracted_json": extracted,
                "is_applied": bool(row["is_applied"]),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            })
        return result

    def mark_as_applied(self, message_id: int) -> bool:
        """
        标记消息为已应用。

        Args:
            message_id: 消息 ID

        Returns:
            是否更新成功
        """
        sql = """
            UPDATE profile_dialog_messages
            SET is_applied = 1
            WHERE message_id = %s AND is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (message_id,))
            return cursor.rowcount > 0

    def get_pending_extractions(self, profile_id: int) -> List[Dict[str, Any]]:
        """
        获取未应用的抽取结果。

        Args:
            profile_id: 画像 ID

        Returns:
            未应用的消息列表
        """
        sql = """
            SELECT
                message_id,
                profile_id,
                role,
                content,
                extracted_json,
                is_applied,
                created_at
            FROM profile_dialog_messages
            WHERE profile_id = %s
              AND is_deleted = 0
              AND is_applied = 0
              AND extracted_json IS NOT NULL
            ORDER BY created_at ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (profile_id,))
            rows = cursor.fetchall()

        result = []
        for row in rows:
            extracted = None
            if row.get("extracted_json"):
                try:
                    extracted = json.loads(row["extracted_json"])
                except Exception:
                    pass

            result.append({
                "message_id": row["message_id"],
                "profile_id": row["profile_id"],
                "role": row["role"],
                "content": row["content"],
                "extracted_json": extracted,
                "is_applied": bool(row["is_applied"]),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            })
        return result

    def create_update_history(
        self,
        profile_id: int,
        update_type: str,
        before_json: Dict[str, Any],
        after_json: Dict[str, Any],
        change_summary: Optional[str] = None,
    ) -> int:
        """
        创建画像更新历史记录。

        Args:
            profile_id: 画像 ID
            update_type: 更新类型（dialog/self_report/quiz_result）
            before_json: 更新前的画像数据
            after_json: 更新后的画像数据
            change_summary: 变更摘要

        Returns:
            新创建的历史记录 ID
        """
        sql = """
            INSERT INTO profile_update_history
                (profile_id, update_type, before_json, after_json, change_summary)
            VALUES (%s, %s, %s, %s, %s)
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (
                profile_id,
                update_type,
                json.dumps(before_json),
                json.dumps(after_json),
                change_summary,
            ))
            return cursor.lastrowid

    def apply_profile_patch(
        self,
        profile_id: int,
        message_id: int,
        profile_patch: Dict[str, Any],
        change_summary: str,
    ) -> bool:
        """原子应用对话抽取结果，并同步写入画像历史。"""
        fields = [
            field
            for field in PROFILE_MUTABLE_FIELDS
            if field in profile_patch and profile_patch[field] is not None
        ]
        snapshot_fields = ", ".join(PROFILE_MUTABLE_FIELDS)

        with get_db_transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT message_id
                    FROM profile_dialog_messages
                    WHERE message_id = %s
                      AND profile_id = %s
                      AND is_deleted = 0
                      AND is_applied = 0
                      AND extracted_json IS NOT NULL
                    FOR UPDATE
                    """,
                    (message_id, profile_id),
                )
                if cursor.fetchone() is None:
                    return False

                cursor.execute(
                    f"""
                    SELECT {snapshot_fields}
                    FROM student_profiles
                    WHERE profile_id = %s AND is_deleted = 0
                    FOR UPDATE
                    """,
                    (profile_id,),
                )
                before_json = cursor.fetchone()
                if before_json is None:
                    return False

                if fields:
                    assignments = ", ".join(f"{field} = %s" for field in fields)
                    params = [profile_patch[field] for field in fields]
                    params.append(profile_id)
                    cursor.execute(
                        f"""
                        UPDATE student_profiles
                        SET {assignments}, updated_at = NOW()
                        WHERE profile_id = %s AND is_deleted = 0
                        """,
                        params,
                    )

                cursor.execute(
                    f"""
                    SELECT {snapshot_fields}
                    FROM student_profiles
                    WHERE profile_id = %s AND is_deleted = 0
                    """,
                    (profile_id,),
                )
                after_json = cursor.fetchone()

                cursor.execute(
                    """
                    INSERT INTO profile_update_history
                        (profile_id, update_type, before_json, after_json, change_summary)
                    VALUES (%s, 'dialog', %s, %s, %s)
                    """,
                    (
                        profile_id,
                        json.dumps(before_json, ensure_ascii=False, default=_json_default),
                        json.dumps(after_json, ensure_ascii=False, default=_json_default),
                        change_summary,
                    ),
                )
                cursor.execute(
                    """
                    UPDATE profile_dialog_messages
                    SET is_applied = 1
                    WHERE message_id = %s
                      AND profile_id = %s
                      AND is_deleted = 0
                      AND is_applied = 0
                    """,
                    (message_id, profile_id),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("画像确认状态更新失败")

        return True

    def get_update_history(
        self, profile_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取画像更新历史。

        Args:
            profile_id: 画像 ID
            limit: 返回条数限制

        Returns:
            更新历史列表（按时间倒序）
        """
        sql = """
            SELECT
                history_id,
                profile_id,
                update_type,
                before_json,
                after_json,
                change_summary,
                created_at
            FROM profile_update_history
            WHERE profile_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (profile_id, limit))
            rows = cursor.fetchall()

        result = []
        for row in rows:
            before = None
            after = None
            try:
                if row.get("before_json"):
                    before = json.loads(row["before_json"])
                if row.get("after_json"):
                    after = json.loads(row["after_json"])
            except Exception:
                pass

            result.append({
                "history_id": row["history_id"],
                "profile_id": row["profile_id"],
                "update_type": row["update_type"],
                "before_json": before,
                "after_json": after,
                "change_summary": row.get("change_summary") or "",
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            })
        return result
