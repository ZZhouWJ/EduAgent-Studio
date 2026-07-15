import unittest
from io import BytesIO
from zipfile import ZipFile

from app.services.ppt_export_service import build_presentation


class PptExportTests(unittest.TestCase):
    def test_builds_editable_pptx_with_cover_and_content_slides(self):
        output = build_presentation(
            "数据库事务",
            [
                {
                    "title": "ACID 特性",
                    "points": ["原子性", "一致性", "隔离性", "持久性"],
                    "notes": "结合转账案例讲解",
                }
            ],
        )

        self.assertTrue(output.getvalue().startswith(b"PK"))
        with ZipFile(BytesIO(output.getvalue())) as archive:
            names = archive.namelist()
            self.assertIn("ppt/slides/slide1.xml", names)
            self.assertIn("ppt/slides/slide2.xml", names)
