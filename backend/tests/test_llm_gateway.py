import unittest
from unittest.mock import Mock

from app.llm.gateway import LLMConfig, LLMGateway


class LLMGatewayTests(unittest.TestCase):
    def test_unknown_provider_never_falls_back_to_mock(self):
        gateway = LLMGateway()
        mock_provider = Mock()
        gateway.register_provider("mock", mock_provider)

        result = gateway.generate(
            [{"role": "user", "content": "test"}],
            LLMConfig(model_id=1, model_name="test", provider="unknown"),
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error, "模型服务不可用")
        mock_provider.generate.assert_not_called()

    def test_explicit_provider_is_called(self):
        gateway = LLMGateway()
        provider = Mock()
        provider.generate.return_value = {
            "content": "ok",
            "input_tokens": 2,
            "output_tokens": 3,
            "cost": 0.01,
        }
        gateway.register_provider("openai_compatible", provider)

        result = gateway.generate(
            [{"role": "user", "content": "test"}],
            LLMConfig(
                model_id=1,
                model_name="test",
                provider="openai_compatible",
            ),
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.content, "ok")
        self.assertEqual(result.total_tokens, 5)
        provider.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
