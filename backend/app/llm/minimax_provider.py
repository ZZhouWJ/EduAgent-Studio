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
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key or config.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": kwargs.get("model_name", config.model_name),
            "messages": messages,
        }

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

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # MiniMax 计费：按 token 数计费，粗略估算
            cost = (input_tokens + output_tokens) * 0.000_001

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model": self.model_name,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"MiniMax API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"MiniMax API call failed: {e}")
            raise
