import unittest
from unittest.mock import Mock

from app.services.profile_service import ProfileService
from app.utils.exceptions import ForbiddenException, NotFoundException


class ProfileAccessTests(unittest.TestCase):
    def setUp(self):
        self.service = ProfileService()
        self.service._repo = Mock()

    def test_owner_can_access_profile(self):
        self.service._repo.get_profile_owner_id.return_value = 42

        self.service.require_profile_access(
            7,
            {"user_id": 42, "roles": ["student_member"]},
        )

    def test_staff_can_access_profile(self):
        self.service._repo.get_profile_owner_id.return_value = 42

        self.service.require_profile_access(
            7,
            {"user_id": 3, "roles": ["teacher"]},
        )

    def test_other_student_cannot_access_profile(self):
        self.service._repo.get_profile_owner_id.return_value = 42

        with self.assertRaises(ForbiddenException):
            self.service.require_profile_access(
                7,
                {"user_id": 99, "roles": ["student_member"]},
            )

    def test_missing_profile_returns_not_found(self):
        self.service._repo.get_profile_owner_id.return_value = None

        with self.assertRaises(NotFoundException):
            self.service.require_profile_access(
                7,
                {"user_id": 42, "roles": ["student_member"]},
            )


if __name__ == "__main__":
    unittest.main()
