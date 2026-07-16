import asyncio
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.routers.storage import download_resource


class StorageAccessTests(unittest.TestCase):
    @patch("app.routers.storage.CourseAccessService")
    @patch("app.routers.storage.get_resource_content")
    def test_download_checks_owning_course_before_serving(self, get_content, access_type):
        get_content.return_value = {
            "course_id": 3,
            "file_path": __file__,
            "title": "课程资源",
        }
        access = Mock()
        access_type.return_value = access
        user = {"user_id": 7, "roles": ["teacher"]}

        response = asyncio.run(download_resource("file-1", user=user))

        access.require_course_access.assert_called_once_with(3, user)
        self.assertEqual(response.path, __file__)

    @patch("app.routers.storage.CourseAccessService")
    @patch("app.routers.storage.get_resource_content")
    def test_download_stops_when_course_access_is_denied(self, get_content, access_type):
        get_content.return_value = {
            "course_id": 3,
            "file_path": __file__,
            "title": "课程资源",
        }
        access = Mock()
        access.require_course_access.side_effect = RuntimeError("denied")
        access_type.return_value = access

        with self.assertRaisesRegex(RuntimeError, "denied"):
            asyncio.run(
                download_resource(
                    "file-1",
                    user={"user_id": 8, "roles": ["teacher"]},
                )
            )

    @patch("app.routers.storage.CourseAccessService")
    @patch("app.routers.storage.get_resource_content")
    def test_download_hides_files_without_course_metadata(self, get_content, access_type):
        get_content.return_value = {"file_path": __file__, "title": "异常资源"}

        with self.assertRaises(HTTPException) as context:
            asyncio.run(
                download_resource(
                    "file-1",
                    user={"user_id": 1, "roles": ["admin"]},
                )
            )

        self.assertEqual(context.exception.status_code, 404)
        access_type.assert_not_called()


if __name__ == "__main__":
    unittest.main()
