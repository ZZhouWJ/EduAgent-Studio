import unittest

from pydantic import ValidationError

from app.routers.profiles import UpdateMasteryRequest


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


if __name__ == "__main__":
    unittest.main()
