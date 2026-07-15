import json
import unittest
from decimal import Decimal
from unittest.mock import Mock

from app.repositories.profile_dialog_repo import _json_default
from app.services.profile_dialog_service import ProfileDialogService


class ProfileDialogPatchTests(unittest.TestCase):
    def setUp(self):
        self.service = ProfileDialogService()

    def test_maps_all_persisted_profile_dimensions(self):
        patch = self.service._build_profile_patch(
            {
                "learning_goal": "通过期末考试",
                "knowledge_base": "掌握 Python 基础",
                "current_level": "一般",
                "cognitive_style": "例题驱动",
                "time_constraints": "工作日晚间",
                "practice_level": "能完成基础项目",
                "motivation": "准备软件杯",
                "interests": ["数据分析", "智能体"],
                "resource_preferences": ["代码案例", "思维导图"],
                "weekly_hours": 6,
                "error_prone_points": ["边界条件", "事务回滚"],
            }
        )

        self.assertEqual(patch["weekly_hours"], 6)
        self.assertEqual(patch["interests"], "数据分析,智能体")
        self.assertEqual(patch["resource_preferences"], "代码案例,思维导图")
        self.assertEqual(
            json.loads(patch["error_prone_points"]),
            ["边界条件", "事务回滚"],
        )
        self.assertEqual(patch["cognitive_style"], "例题驱动")

    def test_clamps_weekly_hours_to_valid_range(self):
        self.assertEqual(
            self.service._build_profile_patch({"weekly_hours": 200})["weekly_hours"],
            168,
        )

    def test_apply_extraction_delegates_to_atomic_repository_operation(self):
        self.service._repo = Mock()
        self.service._profile_repo = Mock()
        self.service._repo.get_pending_extractions.return_value = [
            {
                "message_id": 9,
                "extracted_json": {"learning_goal": "通过期末考试"},
            }
        ]
        self.service._repo.apply_profile_patch.return_value = True
        self.service._profile_repo.get_profile.return_value = {
            "profile_id": 3,
            "learning_goal": "通过期末考试",
        }

        result = self.service.apply_extraction(profile_id=3, message_id=9)

        self.assertEqual(result["code"], 0)
        self.service._repo.apply_profile_patch.assert_called_once_with(
            profile_id=3,
            message_id=9,
            profile_patch={"learning_goal": "通过期末考试"},
            change_summary="更新学习目标: 通过期末考试",
        )

    def test_repository_history_serializer_handles_decimal_values(self):
        self.assertEqual(_json_default(Decimal("0.350")), 0.35)


if __name__ == "__main__":
    unittest.main()
