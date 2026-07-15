import unittest
from unittest.mock import Mock

from app.services.profile_service import ProfileService


class ProfileAccessTests(unittest.TestCase):
    def setUp(self):
        self.service = ProfileService()
        self.service._repo = Mock()
        self.service._access = Mock()

    def test_owner_can_access_profile(self):
        self.service.require_profile_access(
            7,
            {"user_id": 42, "roles": ["student_member"]},
        )
        self.service._access.require_profile_access.assert_called_once()

    def test_profile_list_uses_accessible_course_scope(self):
        self.service._access.list_accessible_course_ids.return_value = [2, 4]
        self.service._repo.list_profiles.return_value = ([], 0)

        result = self.service.list_profiles(
            {"user_id": 3, "roles": ["teacher"]}, page=1, page_size=20
        )

        self.assertEqual(result["code"], 0)
        self.service._repo.list_profiles.assert_called_once_with(
            page=1,
            page_size=20,
            course_id=None,
            keyword=None,
            course_ids=[2, 4],
        )

    def test_profile_list_checks_explicit_course(self):
        self.service._access.list_accessible_course_ids.return_value = [2]
        self.service._repo.list_profiles.return_value = ([], 0)
        user = {"user_id": 3, "roles": ["teacher"]}

        self.service.list_profiles(user, course_id=2)

        self.service._access.require_course_access.assert_called_once_with(2, user)

    def test_profile_update_checks_access_before_write(self):
        self.service._repo.update_profile.return_value = {"profile_id": 7}
        user = {"user_id": 3, "roles": ["teacher"]}

        result = self.service.update_profile(7, {"learning_goal": "test"}, user)

        self.assertEqual(result["code"], 0)
        self.service._access.require_profile_access.assert_called_once_with(7, user)

    def test_mastery_update_checks_access_before_write(self):
        self.service._repo.update_mastery.return_value = {
            "kp_id": 2,
            "kp_name": "索引",
            "mastery_level": 0.8,
        }
        user = {"user_id": 3, "roles": ["teacher"]}

        result = self.service.update_mastery(
            7, {"kp_id": 2, "mastery": 0.8}, user
        )

        self.assertEqual(result["code"], 0)
        self.service._access.require_profile_access.assert_called_once_with(7, user)


if __name__ == "__main__":
    unittest.main()
