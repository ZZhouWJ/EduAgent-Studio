"""Resolve the active LLM configuration from encrypted platform settings."""

import logging
from typing import Any, Optional

from app.llm.gateway import LLMConfig
from app.repositories import model_repo
from app.utils.crypto import decrypt_api_key

logger = logging.getLogger(__name__)


def _environment_config(settings: Any, model_name: Optional[str]) -> LLMConfig:
    return LLMConfig(
        model_id=0,
        model_name=model_name or settings.llm_model,
        provider=settings.llm_provider,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.7,
        max_tokens=2048,
        timeout=60,
        api_secret=settings.iflytek_api_secret,
        app_id=settings.iflytek_app_id,
    )


def resolve_runtime_llm_config(
    settings: Any,
    model_name: Optional[str] = None,
) -> LLMConfig:
    """Prefer an active database model and credential, then fall back to env."""
    preferred_model = model_name or settings.llm_model
    try:
        row = model_repo.get_runtime_model_config(
            preferred_provider=settings.llm_provider,
            preferred_model=preferred_model,
        )
        if not row:
            return _environment_config(settings, model_name)

        api_key = decrypt_api_key(
            row["encrypted_api_key"],
            row["key_iv"],
            row["key_tag"],
        )
        return LLMConfig(
            model_id=int(row["model_id"]),
            model_name=str(row["model_name"]),
            provider=str(row["provider_code"]),
            api_key=api_key,
            base_url=row.get("base_url") or settings.llm_base_url,
            temperature=0.7,
            max_tokens=min(int(row.get("max_context") or 2048), 4096),
            timeout=60,
        )
    except Exception as exc:
        logger.warning(
            "Unable to load the database model configuration; using environment settings: %s",
            type(exc).__name__,
        )
        return _environment_config(settings, model_name)
