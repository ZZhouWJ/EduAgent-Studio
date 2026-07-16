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

        for migration_number in ("27", "28", "29", "30"):
            self.assertIn(migration_number, readme)
        for migration in (
            "27_create_learning_task_progress.sql",
            "28_cleanup_orphan_learning_profiles.sql",
            "29_align_education_prompt_templates.sql",
            "30_remove_demo_model_configs.sql",
        ):
            self.assertIn(migration, database_readme)


if __name__ == "__main__":
    unittest.main()
