import unittest

from pydantic import ValidationError

from app.routers.profiles import (
    ApplyExtractionRequest,
    DialogMessageRequest,
    UpdateMasteryRequest,
    UpdateProfileRequest,
    _profile_update_payload,
)


class ProfileValidationTests(unittest.TestCase):
    def test_mastery_accepts_normalized_score(self):
        request = UpdateMasteryRequest(
            kp_id=7,
            mastery=0.75,
            update_reason="阶段测验更新",
        )

        self.assertEqual(request.mastery, 0.75)

    def test_mastery_rejects_scores_outside_zero_to_one(self):
        for score in (-0.01, 1.01, 75):
            with self.subTest(score=score), self.assertRaises(ValidationError):
                UpdateMasteryRequest(kp_id=7, mastery=score)

    def test_mastery_rejects_invalid_knowledge_point(self):
        with self.assertRaises(ValidationError):
            UpdateMasteryRequest(kp_id=0, mastery=0.5)

    def test_profile_update_rejects_unknown_and_out_of_range_fields(self):
        with self.assertRaises(ValidationError):
            UpdateProfileRequest(weekly_hours=169)
        with self.assertRaises(ValidationError):
            UpdateProfileRequest(is_admin=True)

    def test_profile_update_serializes_list_fields_for_mysql(self):
        payload = _profile_update_payload(
            UpdateProfileRequest(
                error_prone_points=["混淆左连接", "遗漏空值"],
                interests=["数据库", "分布式系统"],
                resource_preferences=["案例", "练习"],
            )
        )

        self.assertEqual(payload["interests"], "数据库,分布式系统")
        self.assertEqual(payload["resource_preferences"], "案例,练习")
        self.assertIn("混淆左连接", payload["error_prone_points"])

    def test_profile_dialog_contract_bounds_untrusted_content(self):
        self.assertEqual(DialogMessageRequest(message="  学习目标  ").message, "学习目标")
        with self.assertRaises(ValidationError):
            DialogMessageRequest(message="x" * 4001)
        with self.assertRaises(ValidationError):
            ApplyExtractionRequest(message_id=0)


if __name__ == "__main__":
    unittest.main()
