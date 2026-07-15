import asyncio
import unittest
from unittest.mock import Mock, patch

from app.routers.resources import get_resource, list_resources


class ResourceAccessTests(unittest.TestCase):
    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_resource_list_uses_accessible_course_scope(self, access_type, repo):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1, 3]
        access_type.return_value = access
        repo.list_resources.return_value = {"items": [], "total": 0}
        user = {"user_id": 7, "roles": ["teacher"]}

        response = asyncio.run(list_resources(page=1, page_size=20, user=user))

        self.assertEqual(response.status_code, 200)
        repo.list_resources.assert_called_once_with(
            page=1,
            page_size=20,
            course_id=None,
            resource_type=None,
            course_ids=[1, 3],
        )

    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_resource_detail_authorizes_before_read(self, access_type, repo):
        access = Mock()
        access.require_resource_access.side_effect = RuntimeError("denied")
        access_type.return_value = access

        with self.assertRaisesRegex(RuntimeError, "denied"):
            asyncio.run(
                get_resource(
                    9, user={"user_id": 7, "roles": ["teacher"]}
                )
            )

        repo.get_resource.assert_not_called()


if __name__ == "__main__":
    unittest.main()
