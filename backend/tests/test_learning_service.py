import unittest
from unittest.mock import Mock

from app.services.learning_service import LearningService


class LearningServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = LearningService()
        self.service._repo = Mock()
        self.service._access = Mock()
        self.service._repo.list_tasks.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
        }

    def test_task_list_is_scoped_to_accessible_courses(self):
        user = {"user_id": 12, "roles": ["student_member"]}
        self.service._access.list_accessible_course_ids.return_value = [1]

        self.service.list_tasks(user=user)

        self.service._repo.list_tasks.assert_called_once_with(
            page=1,
            page_size=20,
            course_id=None,
            course_ids=[1],
            status=None,
        )

    def test_explicit_task_course_requires_access(self):
        user = {"user_id": 7, "roles": ["teacher"]}
        self.service._access.list_accessible_course_ids.return_value = [3]

        self.service.list_tasks(user=user, course_id=3)

        self.service._access.require_course_access.assert_called_once_with(3, user)


if __name__ == "__main__":
    unittest.main()
