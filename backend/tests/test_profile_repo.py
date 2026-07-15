import json
import unittest

from app.repositories.profile_repo import _serialize_profile


class ProfileSerializationTests(unittest.TestCase):
    def test_preserves_structured_weak_point_details(self):
        raw = {
            "profile_id": 1,
            "student_id": 2,
            "course_id": 3,
            "weak_points": json.dumps(
                [
                    {
                        "kp_id": 4,
                        "kp_name": "事务隔离级别",
                        "mastery": 0.35,
                        "mastery_level": 0.35,
                        "reason": "幻读与不可重复读混淆",
                    }
                ]
            ),
        }

        profile = _serialize_profile(raw)

        self.assertEqual(profile["weak_points"][0]["kp_name"], "事务隔离级别")
        self.assertEqual(profile["weak_points"][0]["mastery"], 0.35)
        self.assertEqual(
            profile["weak_points"][0]["reason"],
            "幻读与不可重复读混淆",
        )


if __name__ == "__main__":
    unittest.main()
