import asyncio
import json
import os
import tempfile
import unittest
from uuid import UUID
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.routers.storage import download_resource
from app.services import storage_service


FILE_ID = UUID("1b6b2a6d-8fe0-4d36-93fd-0af76721bb80")


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

        response = asyncio.run(download_resource(FILE_ID, user=user))

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
                    FILE_ID,
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
                    FILE_ID,
                    user={"user_id": 1, "roles": ["admin"]},
                )
            )

        self.assertEqual(context.exception.status_code, 404)
        access_type.assert_not_called()


class StorageContentTests(unittest.TestCase):
    def setUp(self):
        storage_service._storage_index = {}
        storage_service._index_loaded = False

    def tearDown(self):
        storage_service._storage_index = {}
        storage_service._index_loaded = False

    def test_saved_resource_can_be_resolved_for_download(self):
        with tempfile.TemporaryDirectory() as data_dir, patch.object(
            storage_service, "_get_data_dir", return_value=data_dir
        ):
            saved = storage_service.save_resource_content(
                title="事务隔离",
                content="课程内容",
                resource_type="lecture",
                course_id=3,
            )

            loaded = storage_service.get_resource_content(saved["file_id"])

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["content"], "课程内容")
        self.assertTrue(loaded["file_path"].endswith(f"{saved['file_id']}.json"))

    def test_tampered_index_cannot_read_outside_storage_root(self):
        with tempfile.TemporaryDirectory() as data_dir, patch.object(
            storage_service, "_get_data_dir", return_value=data_dir
        ):
            outside_path = os.path.join(data_dir, "outside.json")
            with open(outside_path, "w", encoding="utf-8") as file:
                json.dump({"course_id": 3, "content": "secret"}, file)
            storage_service._storage_index = {
                str(FILE_ID): {
                    "file_path": outside_path,
                    "deleted": False,
                }
            }
            storage_service._index_loaded = True

            loaded = storage_service.get_resource_content(str(FILE_ID))

        self.assertIsNone(loaded)


if __name__ == "__main__":
    unittest.main()
