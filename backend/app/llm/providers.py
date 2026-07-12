"""LLM 供应商管理"""
import logging
from typing import Any, Dict
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.minimax_provider import MiniMaxProvider
from app.llm.iflytek_provider import IFlyTekProvider

logger = logging.getLogger(__name__)

_PROVIDER_REGISTRY: Dict[str, type] = {
    "mock": MockProvider,
    "openai": OpenAICompatibleProvider,
    "openai_compatible": OpenAICompatibleProvider,
    "minimax": MiniMaxProvider,
}


def get_provider(name: str, **kwargs) -> Any:
    """获取供应商实例"""
    provider_cls = _PROVIDER_REGISTRY.get(name.lower())
    if provider_cls is None:
        logger.warning(f"Unknown provider '{name}', falling back to MockProvider")
        return MockProvider(**kwargs)
    return provider_cls(**kwargs)


def register_provider(name: str, provider_cls: type) -> None:
    """注册新的供应商"""
    _PROVIDER_REGISTRY[name.lower()] = provider_cls
    logger.info(f"Registered provider: {name}")
