import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.llm.gateway import LLMCallResult, LLMConfig, LLMGateway
from app.services.tutor_service import TutorService
from app.services.tutor_tool_handlers import ppt_agent


def runtime_settings():
    return SimpleNamespace(
        llm_model="mock-model",
        llm_base_url="http://localhost/mock",
        llm_api_key="",
        iflytek_app_id="",
        iflytek_api_key="",
        iflytek_api_secret="",
    )


class RuntimeGatewayTest(unittest.TestCase):
    def test_provider_registration_is_shared_and_idempotent(self):
        from app.llm import runtime

        gateway = LLMGateway()
        with patch.object(runtime, "llm_gateway", gateway), patch.object(
            runtime, "get_settings", return_value=runtime_settings()
        ):
            previous = runtime._registered
            runtime._registered = False
            try:
                first = runtime.get_runtime_llm_gateway()
                second = runtime.get_runtime_llm_gateway()
            finally:
                runtime._registered = previous

        self.assertIs(first, gateway)
        self.assertIs(second, gateway)
        self.assertEqual(
            set(gateway._providers),
            {"mock", "openai_compatible", "openai", "deepseek", "qwen", "minimax"},
        )
        for provider in set(gateway._providers.values()):
            client = getattr(provider, "_client", None)
            if client is not None:
                client.close()

    @patch("app.services.tutor_service.get_runtime_llm_gateway")
    def test_tutor_service_uses_runtime_gateway_by_default(self, get_gateway):
        gateway = LLMGateway()
        get_gateway.return_value = gateway

        service = TutorService()

        self.assertIs(service._llm_gateway, gateway)


class TutorToolGatewayTest(unittest.TestCase):
    def test_ppt_agent_uses_registered_gateway_and_typed_config(self):
        seen = {}

        class Gateway:
            def generate(self, messages, config):
                seen["config"] = config
                return LLMCallResult(
                    content='[{"slide_number":1,"title":"Intro","bullets":[],"notes":""}]',
                    model=config.model_name,
                    provider=config.provider,
                    input_tokens=1,
                    output_tokens=1,
                    total_tokens=2,
                    latency_ms=1,
                    cost=0,
                )

        settings = SimpleNamespace(
            llm_config=lambda: LLMConfig(
                model_id=0,
                model_name="mock-model",
                provider="mock",
            )
        )
        with patch(
            "app.services.tutor_tool_handlers._get_llm", return_value=Gateway()
        ), patch(
            "app.services.tutor_tool_handlers.get_settings", return_value=settings
        ):
            result = asyncio.run(ppt_agent(course_id=1, topic="Transactions"))

        self.assertIsInstance(seen["config"], LLMConfig)
        self.assertEqual(result["slide_count"], 1)
        self.assertEqual(result["quality_score"], 0.8)


if __name__ == "__main__":
    unittest.main()
