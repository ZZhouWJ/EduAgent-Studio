import unittest
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

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

    def test_distinguishes_word_and_powerpoint_archives(self):
        word = office_archive("word/document.xml")
        self.assertEqual(
            validate_material_upload(word, "lesson.docx", "word"),
            "lesson.docx",
        )
        with self.assertRaisesRegex(ValueError, "扩展名"):
            validate_material_upload(word, "lesson.pptx", "ppt")


if __name__ == "__main__":
    unittest.main()
