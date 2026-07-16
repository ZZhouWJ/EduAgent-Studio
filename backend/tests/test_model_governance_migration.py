import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ModelGovernanceMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = (
            ROOT / "database/30_remove_demo_model_configs.sql"
        ).read_text(encoding="utf-8")

    def test_known_seed_credentials_are_soft_deleted(self):
        self.assertIn("sk-****test", self.sql)
        self.assertIn("sk-****dsk", self.sql)
        self.assertIn("ac.is_deleted = 1", self.sql)
        self.assertNotIn("DELETE FROM API_CONFIGS", self.sql.upper())

    def test_mock_provider_and_models_are_soft_deleted(self):
        self.assertIn("provider.provider_code = 'mock'", self.sql)
        self.assertIn("model.is_deleted = 1", self.sql)
        self.assertIn("WHERE provider_code = 'mock'", self.sql)
        self.assertIn("is_deleted = 1", self.sql)


if __name__ == "__main__":
    unittest.main()
