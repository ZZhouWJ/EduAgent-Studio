import unittest
from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch
from zipfile import ZIP_DEFLATED, ZipFile

from app.routers.knowledge import upload_material
from app.services.knowledge_service import (
    MAX_MATERIAL_SIZE,
    validate_material_upload,
)


def office_archive(entry: str) -> bytes:
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr(entry, "<xml />")
    return output.getvalue()


class KnowledgeUploadValidationTests(unittest.TestCase):
    def test_strips_path_components_from_filename(self):
        safe_name = validate_material_upload(
            "课程内容".encode(), "../../materials/lesson.txt", "text"
        )
        self.assertEqual(safe_name, "lesson.txt")

    def test_rejects_oversized_upload(self):
        with self.assertRaisesRegex(ValueError, "20MB"):
            validate_material_upload(
                b"x" * (MAX_MATERIAL_SIZE + 1), "lesson.txt", "text"
            )

    def test_rejects_disguised_office_file(self):
        with self.assertRaisesRegex(ValueError, "格式"):
            validate_material_upload(b"not-a-zip", "lesson.docx", "word")

    def test_rejects_binary_content_in_txt_upload(self):
        with self.assertRaisesRegex(ValueError, "二进制"):
            validate_material_upload(b"lesson\x00payload", "lesson.txt", "txt")

    def test_distinguishes_word_and_powerpoint_archives(self):
        word = office_archive("word/document.xml")
        self.assertEqual(
            validate_material_upload(word, "lesson.docx", "word"),
            "lesson.docx",
        )
        with self.assertRaisesRegex(ValueError, "扩展名"):
            validate_material_upload(word, "lesson.pptx", "ppt")


class KnowledgeUploadRouteTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.routers.knowledge.knowledge_service.KnowledgeService")
    @patch("app.routers.knowledge.CourseAccessService")
    async def test_route_uses_a_bounded_file_read(self, access_service, service_class):
        upload = Mock(filename="lesson.txt")
        upload.read = AsyncMock(return_value="课程内容".encode())
        service_class.return_value.upload_material.return_value = {
            "code": 0,
            "message": "文件上传成功",
            "data": {"material_id": 9},
        }

        result = await upload_material(
            course_id=3,
            file=upload,
            user={"user_id": 7, "roles": ["teacher"]},
        )

        self.assertEqual(result["code"], 0)
        upload.read.assert_awaited_once_with(MAX_MATERIAL_SIZE + 1)
        access_service.return_value.require_course_access.assert_called_once()


if __name__ == "__main__":
    unittest.main()
