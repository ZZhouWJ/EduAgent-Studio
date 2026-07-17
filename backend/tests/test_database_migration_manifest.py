from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_SQL = {
    "07_test_queries.sql",
    "08_insert_prompt_templates.sql",
    "11_postgresql_migration.sql",
}


class DatabaseMigrationManifestTests(unittest.TestCase):
    def test_compose_mounts_every_mysql_migration_in_order(self):
        expected = sorted(
            path.name
            for path in (ROOT / "database").glob("[0-9][0-9]_*.sql")
            if path.name not in EXCLUDED_SQL
        )
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        mounted = re.findall(
            r"\./database/([^:]+\.sql):/docker-entrypoint-initdb\.d/[^:]+:ro",
            compose,
        )

        self.assertEqual(mounted, expected)

    def test_documentation_includes_latest_migrations(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        database_readme = (ROOT / "database/README_A3.md").read_text(
            encoding="utf-8"
        )

        for migration_number in ("27", "28", "29", "30", "31", "32"):
            self.assertIn(migration_number, readme)
        for migration in (
            "27_create_learning_task_progress.sql",
            "28_cleanup_orphan_learning_profiles.sql",
            "29_align_education_prompt_templates.sql",
            "30_remove_demo_model_configs.sql",
            "31_create_auth_sessions.sql",
            "32_seed_course_knowledge_base.sql",
        ):
            self.assertIn(migration, database_readme)

    def test_seeded_course_knowledge_base_covers_every_cs301_topic(self):
        migration = (ROOT / "database" / "32_seed_course_knowledge_base.sql").read_text(
            encoding="utf-8"
        )
        fixture = (
            ROOT / "database" / "fixtures" / "database_system_principles.md"
        ).read_text(encoding="utf-8")

        for code in (
            "kp_db_intro",
            "kp_relational_model",
            "kp_sql_basic",
            "kp_sql_join",
            "kp_index",
            "kp_transaction",
            "kp_concurrency",
            "kp_norm",
            "kp_design",
        ):
            self.assertIn(code, migration)
        self.assertEqual(fixture.count("\n## "), 9)
        self.assertIn("status=VALUES(status)", migration)


if __name__ == "__main__":
    unittest.main()
