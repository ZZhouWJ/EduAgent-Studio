"""Initialize and expose the shared, configured LLM gateway."""

import logging
from threading import Lock

from app.config import get_settings
from app.llm.gateway import LLMGateway, llm_gateway
from app.llm.iflytek_provider import IFlyTekProvider
from app.llm.minimax_provider import MiniMaxProvider
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider

logger = logging.getLogger(__name__)

_registration_lock = Lock()
_registered = False


def get_runtime_llm_gateway() -> LLMGateway:
    """Return the process-wide gateway after idempotent provider registration."""
    global _registered
    if _registered:
        return llm_gateway

    with _registration_lock:
        if _registered:
            return llm_gateway

        settings = get_settings()
        llm_gateway.register_provider("mock", MockProvider())

        compatible = OpenAICompatibleProvider(
            model_name=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
        for provider_code in ("openai_compatible", "openai", "deepseek", "qwen"):
            llm_gateway.register_provider(provider_code, compatible)

        llm_gateway.register_provider(
            "minimax",
            MiniMaxProvider(
                model_name=settings.llm_model,
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
            ),
        )
        if all(
            (
                settings.iflytek_app_id,
                settings.iflytek_api_key,
                settings.iflytek_api_secret,
            )
        ):
            llm_gateway.register_provider(
                "iflytek",
                IFlyTekProvider(
                    model_name=settings.llm_model,
                    api_key=settings.iflytek_api_key,
                    api_secret=settings.iflytek_api_secret,
                    app_id=settings.iflytek_app_id,
                ),
            )
            logger.info("IFlyTek provider registered for model=%s", settings.llm_model)

        _registered = True
        return llm_gateway
