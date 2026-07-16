import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.llm.gateway import LLMConfig
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.services.runtime_model_config_service import resolve_runtime_llm_config


def make_settings():
    return SimpleNamespace(
        llm_provider="mock",
        llm_model="mock-model",
        llm_api_key="env-key",
        llm_base_url="https://env.example/v1",
        iflytek_api_secret="",
        iflytek_app_id="",
    )


class RuntimeModelConfigTest(unittest.TestCase):
    @patch("app.services.runtime_model_config_service.decrypt_api_key")
    @patch("app.services.runtime_model_config_service.model_repo.get_runtime_model_config")
    def test_database_configuration_takes_precedence(self, get_config, decrypt):
        get_config.return_value = {
            "model_id": 42,
            "model_name": "deepseek-chat",
            "max_context": 8192,
            "provider_code": "deepseek",
            "base_url": "https://api.deepseek.com/v1",
            "encrypted_api_key": "ciphertext",
            "key_iv": "iv",
            "key_tag": "tag",
        }
        decrypt.return_value = "database-key"

        config = resolve_runtime_llm_config(make_settings())

        self.assertEqual(config.model_id, 42)
        self.assertEqual(config.model_name, "deepseek-chat")
        self.assertEqual(config.provider, "deepseek")
        self.assertEqual(config.api_key, "database-key")
        self.assertEqual(config.base_url, "https://api.deepseek.com/v1")
        self.assertEqual(config.max_tokens, 4096)

    @patch("app.services.runtime_model_config_service.model_repo.get_runtime_model_config")
    def test_environment_configuration_is_used_when_database_has_none(self, get_config):
        get_config.return_value = None

        config = resolve_runtime_llm_config(make_settings(), "fallback-model")

        self.assertEqual(config.model_id, 0)
        self.assertEqual(config.model_name, "fallback-model")
        self.assertEqual(config.provider, "mock")
        self.assertEqual(config.api_key, "env-key")


class OpenAICompatibleProviderConfigTest(unittest.TestCase):
    def test_call_uses_runtime_url_and_key(self):
        captured = {}

        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "choices": [{"message": {"content": "ok"}}],
                    "usage": {"prompt_tokens": 2, "completion_tokens": 1},
                }

        class Client:
            def post(self, url, headers, json):
                captured.update(url=url, headers=headers, payload=json)
                return Response()

        provider = OpenAICompatibleProvider(
            base_url="https://environment.example/v1",
            api_key="environment-key",
        )
        provider._client.close()
        provider._client = Client()
        config = LLMConfig(
            model_id=42,
            model_name="deepseek-chat",
            provider="deepseek",
            api_key="database-key",
            base_url="https://database.example/v1",
        )

        result = provider.generate([{"role": "user", "content": "hello"}], config)

        self.assertEqual(captured["url"], "https://database.example/v1/chat/completions")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer database-key")
        self.assertEqual(captured["payload"]["model"], "deepseek-chat")
        self.assertEqual(result["content"], "ok")

    @patch("app.services.runtime_model_config_service.decrypt_api_key")
    @patch("app.services.runtime_model_config_service.model_repo.get_runtime_model_config")
    def test_invalid_database_credential_falls_back_without_leaking(self, get_config, decrypt):
        get_config.return_value = {
            "model_id": 42,
            "model_name": "deepseek-chat",
            "provider_code": "deepseek",
            "encrypted_api_key": "ciphertext",
            "key_iv": "iv",
            "key_tag": "tag",
        }
        decrypt.side_effect = ValueError("invalid authentication tag")

        config = resolve_runtime_llm_config(make_settings())

        self.assertEqual(config.provider, "mock")
        self.assertEqual(config.api_key, "env-key")


if __name__ == "__main__":
    unittest.main()
