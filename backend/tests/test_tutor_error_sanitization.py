import asyncio
import unittest
from unittest.mock import Mock, patch

from app.services.profile_dialog_service import ProfileDialogService
from app.services.tool_registry import ToolRegistry
from app.services.tutor_service import TutorService
from app.llm.gateway import LLMConfig, LLMGateway


SECRET = "sk-sensitive-provider-token"


class TutorErrorSanitizationTests(unittest.TestCase):
    def test_tutor_chat_hides_internal_failure(self):
        service = TutorService()
        service._access = Mock()
        service._profile_repo = Mock()
        service._profile_repo.get_profile.side_effect = RuntimeError(SECRET)

        result = service.chat(
            22,
            3,
            "question",
            {"user_id": 12, "roles": ["student_member"]},
        )

        self.assertEqual(result["code"], 500)
        self.assertNotIn(SECRET, result["message"])

    def test_profile_dialog_hides_repository_failure(self):
        service = ProfileDialogService()
        service._repo = Mock()
        service._repo.get_dialog_history.side_effect = RuntimeError(SECRET)

        result = service.get_dialog_history(22)

        self.assertEqual(result["code"], 500)
        self.assertNotIn(SECRET, result["message"])

    def test_tool_registry_hides_handler_failure(self):
        registry = ToolRegistry()
        registry._handlers = {"broken": Mock(side_effect=RuntimeError(SECRET))}

        result = asyncio.run(registry.execute("broken", {}))

        self.assertNotIn(SECRET, result["error"])

    def test_llm_gateway_hides_provider_failure(self):
        provider = Mock()
        provider.generate.side_effect = RuntimeError(SECRET)
        gateway = LLMGateway()
        gateway.register_provider("test", provider)
        config = LLMConfig(model_id=1, model_name="test", provider="test")

        result = gateway.generate([{"role": "user", "content": "hello"}], config)

        self.assertEqual(result.status, "failed")
        self.assertNotIn(SECRET, result.error)


if __name__ == "__main__":
    unittest.main()
