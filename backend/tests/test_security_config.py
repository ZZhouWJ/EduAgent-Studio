import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.config import Settings
from app.utils.token import create_access_token, decode_access_token


class SecurityConfigTests(unittest.TestCase):
    def test_normalizes_and_deduplicates_cors_origins(self):
        settings = Settings(
            _env_file=None,
            CORS_ORIGINS="https://studio.example.com/, https://api.example.com,https://studio.example.com",
        )

        self.assertEqual(
            settings.cors_origin_list,
            ["https://studio.example.com", "https://api.example.com"],
        )

    def test_rejects_weak_production_jwt_secret(self):
        with self.assertRaises(ValidationError):
            Settings(
                _env_file=None,
                APP_ENV="production",
                JWT_SECRET_KEY="change_me",
                CORS_ORIGINS="https://studio.example.com",
            )

    def test_rejects_wildcard_production_cors(self):
        with self.assertRaises(ValidationError):
            Settings(
                _env_file=None,
                APP_ENV="production",
                JWT_SECRET_KEY="a" * 64,
                CORS_ORIGINS="*",
            )

    def test_rejects_mock_provider_in_production(self):
        with self.assertRaises(ValidationError):
            Settings(
                _env_file=None,
                APP_ENV="production",
                JWT_SECRET_KEY="a" * 64,
                CORS_ORIGINS="https://studio.example.com",
                LLM_PROVIDER="mock",
                LLM_API_KEY="development-only",
            )

    def test_rejects_missing_model_credentials_in_production(self):
        with self.assertRaises(ValidationError):
            Settings(
                _env_file=None,
                APP_ENV="production",
                JWT_SECRET_KEY="a" * 64,
                CORS_ORIGINS="https://studio.example.com",
                LLM_PROVIDER="deepseek",
                LLM_API_KEY="",
            )

    def test_accepts_configured_real_provider_in_production(self):
        settings = Settings(
            _env_file=None,
            APP_ENV="production",
            JWT_SECRET_KEY="a" * 64,
            CORS_ORIGINS="https://studio.example.com",
            LLM_PROVIDER="deepseek",
            LLM_API_KEY="configured-secret",
        )

        self.assertEqual(settings.llm_provider, "deepseek")

    def test_token_round_trip_uses_managed_settings(self):
        settings = Settings(
            _env_file=None,
            JWT_SECRET_KEY="b" * 64,
            JWT_ALGORITHM="HS256",
            JWT_EXPIRE_MINUTES=30,
        )

        with patch("app.utils.token.get_settings", return_value=settings):
            token = create_access_token({"user_id": 7, "roles": ["student"]})
            payload = decode_access_token(token)

        self.assertIsNotNone(payload)
        self.assertEqual(payload["user_id"], 7)
        self.assertEqual(payload["roles"], ["student"])


if __name__ == "__main__":
    unittest.main()
