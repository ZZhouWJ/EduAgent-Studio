import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.config import Settings
from app.utils.crypto import decrypt_api_key, encrypt_api_key
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
            API_KEY_SECRET="c" * 32,
        )

        self.assertEqual(settings.llm_provider, "deepseek")

    def test_rejects_weak_production_api_key_secret(self):
        with self.assertRaises(ValidationError):
            Settings(
                _env_file=None,
                APP_ENV="production",
                JWT_SECRET_KEY="a" * 64,
                API_KEY_SECRET="short-secret",
                CORS_ORIGINS="https://studio.example.com",
                LLM_PROVIDER="deepseek",
                LLM_API_KEY="configured-secret",
            )

    def test_crypto_rejects_short_master_key(self):
        with patch.dict(os.environ, {"API_KEY_SECRET": "a" * 16}):
            with self.assertRaises(RuntimeError):
                encrypt_api_key("provider-secret")

    def test_crypto_round_trip_accepts_32_character_master_key(self):
        with patch.dict(os.environ, {"API_KEY_SECRET": "b" * 32}):
            encrypted, iv, tag, _ = encrypt_api_key("provider-secret")
            self.assertEqual(decrypt_api_key(encrypted, iv, tag), "provider-secret")

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
