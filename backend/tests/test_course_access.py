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
        self.service._repo.get_task_access_context.return_value = {
            "course_id": 3,
            "assignee_id": None,
        }
        course_id = self.service.require_task_access(
            19, {"user_id": 7, "roles": ["teacher"]}
        )
        self.assertEqual(course_id, 3)
        self.service._repo.get_task_access_context.assert_called_once_with(19)

    def test_student_cannot_read_another_assignees_task(self):
        self.service._repo.get_task_access_context.return_value = {
            "course_id": 3,
            "assignee_id": 99,
        }
        self.service._repo.is_student_enrolled.return_value = True

        with self.assertRaises(ForbiddenException):
            self.service.require_task_access(
                19, {"user_id": 12, "roles": ["student_member"]}
            )

    def test_student_can_update_own_assigned_task(self):
        self.service._repo.get_task_access_context.return_value = {
            "course_id": 3,
            "assignee_id": 12,
        }
        self.service._repo.is_student_enrolled.return_value = True

        course_id = self.service.require_task_update_access(
            19, {"user_id": 12, "roles": ["student_member"]}
        )

        self.assertEqual(course_id, 3)

    def test_student_can_update_class_task(self):
        self.service._repo.get_task_access_context.return_value = {
            "course_id": 3,
            "assignee_id": None,
        }
        self.service._repo.is_student_enrolled.return_value = True

        course_id = self.service.require_task_update_access(
            19, {"user_id": 12, "roles": ["student_member"]}
        )

        self.assertEqual(course_id, 3)

    def test_student_cannot_update_another_students_task(self):
        self.service._repo.is_student_enrolled.return_value = True
        user = {"user_id": 12, "roles": ["student_member"]}
        self.service._repo.get_task_access_context.return_value = {
            "course_id": 3,
            "assignee_id": 99,
        }

        with self.assertRaises(ForbiddenException):
            self.service.require_task_update_access(19, user)

    def test_tutor_session_access_uses_owning_profile(self):
        self.service._repo.get_tutor_session_context.return_value = {
            "profile_id": 22,
            "course_id": 3,
            "profile_course_id": 3,
        }
        self.service._repo.get_profile_access_context.return_value = {
            "student_id": 12,
            "course_id": 3,
        }

        course_id = self.service.require_tutor_session_access(
            5, {"user_id": 12, "roles": ["student_member"]}
        )

        self.assertEqual(course_id, 3)

    def test_tutor_session_rejects_inconsistent_course(self):
        self.service._repo.get_tutor_session_context.return_value = {
            "profile_id": 22,
            "course_id": 4,
            "profile_course_id": 3,
        }
        with self.assertRaises(ForbiddenException):
            self.service.require_tutor_session_access(
                5, {"user_id": 12, "roles": ["student_member"]}
            )

    def test_generation_context_validates_student_and_knowledge_points(self):
        self.service._repo.get_student_profile_id.return_value = 22
        self.service._repo.list_knowledge_point_courses.return_value = {4: 3, 5: 3}

        profile_id = self.service.require_generation_context(
            3, 12, [4, 5], {"user_id": 7, "roles": ["teacher"]}
        )

        self.assertEqual(profile_id, 22)

    def test_generation_context_rejects_cross_course_knowledge_point(self):
        self.service._repo.get_student_profile_id.return_value = 22
        self.service._repo.list_knowledge_point_courses.return_value = {4: 3, 5: 9}

        with self.assertRaises(ForbiddenException):
            self.service.require_generation_context(
                3, 12, [4, 5], {"user_id": 7, "roles": ["teacher"]}
            )

    def test_material_chunks_must_match_resource_course(self):
        self.service._repo.list_material_chunk_courses.return_value = {8: 3, 9: 4}

        with self.assertRaises(ForbiddenException):
            self.service.require_material_chunks_course(3, [8, 9])

    def test_student_can_only_read_own_workflow(self):
        self.service._repo.is_student_enrolled.return_value = True
        with self.assertRaises(ForbiddenException):
            self.service.require_workflow_access(
                3, 99, {"user_id": 12, "roles": ["student_member"]}
            )


if __name__ == "__main__":
    unittest.main()
