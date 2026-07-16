"""
MiniMax API 提供商

支持 MiniMax 全系列模型（MiniMax-M3 / M2.7 / M2.5 等），
接口与 OpenAI Chat Completions 完全兼容。
"""
import logging
import time
from typing import Any, Dict, List
import httpx

logger = logging.getLogger(__name__)


class MiniMaxProvider:
    """MiniMax API 提供商（OpenAI-compatible 格式）"""

    def __init__(
        self,
        model_name: str = "MiniMax-M3",
        base_url: str = "https://api.minimax.io/v1",
        api_key: str = "",
        **kwargs,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(timeout=120.0)

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: Any,
        **kwargs,
    ) -> Dict[str, Any]:
        """调用 MiniMax Chat Completions API"""
        base_url = (config.base_url or self.base_url).rstrip("/")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.api_key or self.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": kwargs.get("model_name", config.model_name),
            "messages": messages,
        }

        # Tool Calling 支持
        if config.tools:
            payload["tools"] = config.tools
            if config.tool_choice:
                payload["tool_choice"] = config.tool_choice

        # MiniMax 支持 temperature 和 max_tokens
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        elif config.temperature != 0.7:
            payload["temperature"] = config.temperature

        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        elif config.max_tokens != 2048:
            payload["max_tokens"] = config.max_tokens

        start_time = time.time()
        try:
            response = self._client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            message = data["choices"][0]["message"]
            content = message.get("content") or ""
            tool_calls = message.get("tool_calls") or []
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # MiniMax 计费：按 token 数计费，粗略估算
            cost = (input_tokens + output_tokens) * 0.000_001

            return {
                "content": content,
                "tool_calls": tool_calls,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model": self.model_name,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except httpx.HTTPStatusError as e:
            logger.error("MiniMax API HTTP error: %s", e.response.status_code)
            raise
        except Exception as e:
            logger.error("MiniMax API call failed (%s)", type(e).__name__)
            raise
