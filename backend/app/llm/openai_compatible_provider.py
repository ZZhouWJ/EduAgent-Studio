"""
OpenAI-compatible API 提供商

支持任何兼容 OpenAI API 格式的服务：
- OpenAI GPT 系列
- Qwen (阿里云通义千问)
- DeepSeek
- GLM (智谱华章)
- 本地部署的 vLLM / Ollama 等
"""
import logging
import time
from typing import Any, Dict, List
import httpx

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """OpenAI 兼容接口提供商"""

    def __init__(
        self,
        model_name: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        **kwargs
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(timeout=60.0)

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """调用 OpenAI-compatible API"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key or config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", config.temperature),
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
        }

        start_time = time.time()
        try:
            response = self._client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cost = (input_tokens * 0.000001 + output_tokens * 0.000002)

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model": config.model_name,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
