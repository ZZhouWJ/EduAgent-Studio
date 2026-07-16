import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class EducationPromptMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = (
            ROOT / "database/29_align_education_prompt_templates.sql"
        ).read_text(encoding="utf-8")

    def test_legacy_seed_templates_are_soft_deleted(self):
        self.assertIn("is_deleted = 1", self.sql)
        self.assertIn("项目需求分析生成", self.sql)
        self.assertIn("函数级代码注释生成", self.sql)
        self.assertNotIn("DELETE FROM PROMPT_TEMPLATES", self.sql.upper())

    def test_education_workflow_prompt_types_are_seeded(self):
        for type_code in (
            "lecture",
            "quiz",
            "case",
            "review",
            "summary",
            "profile_diagnosis",
            "tutor_answer",
            "evidence_check",
        ):
            self.assertIn(f"'{type_code}'", self.sql)

    def test_templates_cover_generation_diagnosis_tutoring_and_grounding(self):
        for template_name in (
            "个性化课程讲义生成",
            "分层练习与答案生成",
            "真实情境案例资源生成",
            "教师内容审核清单",
            "个性化学习总结生成",
            "学习画像诊断",
            "循证学习答疑",
            "事实与证据一致性校验",
        ):
            self.assertIn(template_name, self.sql)


if __name__ == "__main__":
    unittest.main()
