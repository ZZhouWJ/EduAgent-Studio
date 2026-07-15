import unittest
from unittest.mock import Mock

from app.services.course_access_service import CourseAccessService
from app.utils.exceptions import ForbiddenException, NotFoundException


class CourseAccessTests(unittest.TestCase):
    def setUp(self):
        self.service = CourseAccessService()
        self.service._repo = Mock()
        self.service._repo.get_course_teacher_id.return_value = 7

    def test_admin_can_access_any_existing_course(self):
        self.service.require_course_access(3, {"user_id": 1, "roles": ["admin"]})

    def test_teacher_can_only_access_owned_course(self):
        self.service.require_course_access(3, {"user_id": 7, "roles": ["teacher"]})
        with self.assertRaises(ForbiddenException):
            self.service.require_course_access(3, {"user_id": 8, "roles": ["teacher"]})

    def test_student_must_be_enrolled_in_course(self):
        self.service._repo.is_student_enrolled.return_value = True
        self.service.require_course_access(
            3, {"user_id": 12, "roles": ["student_member"]}
        )
        self.service._repo.is_student_enrolled.return_value = False
        with self.assertRaises(ForbiddenException):
            self.service.require_course_access(
                3, {"user_id": 12, "roles": ["student_member"]}
            )

    def test_missing_course_returns_not_found(self):
        self.service._repo.get_course_teacher_id.return_value = None
        with self.assertRaises(NotFoundException):
            self.service.require_course_access(99, {"user_id": 1, "roles": ["admin"]})

    def test_material_access_delegates_to_owning_course(self):
        self.service._repo.get_material_course_id.return_value = 3
        self.service.require_material_access(15, {"user_id": 7, "roles": ["teacher"]})
        self.service._repo.get_material_course_id.assert_called_once_with(15)

    def test_admin_course_list_is_unrestricted(self):
        self.assertIsNone(
            self.service.list_accessible_course_ids({"user_id": 1, "roles": ["admin"]})
        )

    def test_member_course_list_uses_all_relevant_roles(self):
        self.service._repo.list_accessible_course_ids.return_value = [2, 4]
        result = self.service.list_accessible_course_ids(
            {"user_id": 12, "roles": ["teacher", "student_member"]}
        )
        self.assertEqual(result, [2, 4])
        self.service._repo.list_accessible_course_ids.assert_called_once_with(
            user_id=12,
            is_teacher=True,
            is_student=True,
        )

    def test_profile_must_belong_to_requested_course(self):
        self.service._repo.get_profile_course_id.return_value = 4
        with self.assertRaises(ForbiddenException):
            self.service.require_profile_course(
                22, 3, {"user_id": 7, "roles": ["teacher"]}
            )

    def test_profile_owner_and_admin_can_access(self):
        self.service._repo.get_profile_access_context.return_value = {
            "student_id": 12,
            "course_id": 3,
        }
        self.assertEqual(
            self.service.require_profile_access(
                22, {"user_id": 12, "roles": ["student_member"]}
            ),
            3,
        )
        self.assertEqual(
            self.service.require_profile_access(
                22, {"user_id": 1, "roles": ["admin"]}
            ),
            3,
        )

    def test_teacher_profile_access_is_limited_to_owned_course(self):
        self.service._repo.get_profile_access_context.return_value = {
            "student_id": 12,
            "course_id": 3,
        }
        self.service.require_profile_access(22, {"user_id": 7, "roles": ["teacher"]})
        with self.assertRaises(ForbiddenException):
            self.service.require_profile_access(
                22, {"user_id": 8, "roles": ["teacher"]}
            )

    def test_missing_profile_access_context_returns_not_found(self):
        self.service._repo.get_profile_access_context.return_value = None
        with self.assertRaises(NotFoundException):
            self.service.require_profile_access(
                22, {"user_id": 12, "roles": ["student_member"]}
            )

    def test_task_access_delegates_to_owning_course(self):
        self.service._repo.get_task_course_id.return_value = 3
        course_id = self.service.require_task_access(
            19, {"user_id": 7, "roles": ["teacher"]}
        )
        self.assertEqual(course_id, 3)
        self.service._repo.get_task_course_id.assert_called_once_with(19)


if __name__ == "__main__":
    unittest.main()
