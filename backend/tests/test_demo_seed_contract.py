import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


class DemoSeedContractTests(unittest.TestCase):
    def test_seed_requires_an_explicit_password(self):
        env = os.environ.copy()
        env["DEMO_PASSWORD"] = ""
        result = subprocess.run(
            [sys.executable, str(ROOT / "database/seed_demo_data.py")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Set DEMO_PASSWORD", result.stderr)

    def test_demo_credentials_stay_out_of_the_login_page(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        login = (ROOT / "frontend/src/app/pages/Login.tsx").read_text(encoding="utf-8")
        seed = (ROOT / "database/seed_demo_data.py").read_text(encoding="utf-8")
        env_example = (ROOT / "backend/.env.example").read_text(encoding="utf-8")
        for username in ("admin", "teacher_li", "student_zhang"):
            self.assertIn(username, readme)
            self.assertIn(username, seed)
        for username in ("teacher_li", "student_zhang"):
            self.assertNotIn(username, login)
        self.assertNotIn('setUsername("admin")', login)
        self.assertIn('DEMO_PASSWORD = ENV.get("DEMO_PASSWORD", "")', seed)
        self.assertIn("DEMO_PASSWORD=", env_example)
        self.assertNotIn("Demo password:", seed)
        self.assertIn('os.path.join(BASE_DIR, "backend", ".env")', seed)
        self.assertNotIn("DELETE FROM users WHERE username", seed)

    def test_course_ownership_uses_seeded_teacher(self):
        sql = (ROOT / "database/10_insert_a3_initial_data.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("username = 'teacher_li'", sql)
        self.assertIn("'kp_db_intro'", sql)
        self.assertNotIn("'DB001'", sql)

    def test_initial_mastery_rows_are_course_aligned(self):
        sql = (ROOT / "database/10_insert_a3_initial_data.sql").read_text(
            encoding="utf-8"
        )
        mastery_section = sql.split(
            "INSERT INTO `student_knowledge_mastery`", 1
        )[1].split("-- 插入学习反馈示例", 1)[0]
        self.assertEqual(mastery_section.count("(1, 6,"), 1)
        self.assertNotIn("(1, 12,", mastery_section)
        self.assertIn("(3, 10,", mastery_section)

    def test_final_password_script_disables_canonical_accounts(self):
        sql = (ROOT / "database/18_update_user_passwords.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("teacher_li", sql)
        self.assertIn("student_zhang", sql)
        self.assertIn("status` = 'disabled'", sql)
        self.assertIn("!set-with-seed-script!", sql)
        self.assertNotIn("teacher01", sql)


if __name__ == "__main__":
    unittest.main()
