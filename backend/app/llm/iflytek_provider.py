"""
讯飞星火大模型 Provider（Spark Open API）

使用 HMAC-SHA256 签名认证，请求/响应体与 OpenAI Chat Completions 兼容。

文档：https://www.xfyun.cn/doc/spark/
"""

import base64
import hashlib
import hmac
import logging
import time
from datetime import timezone
from email.utils import formatdate
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

# 讯飞 Spark Open API 端点
IFLYTEK_API_HOST = "spark-api-open.xf-yun.com"
IFLYTEK_API_PATH = "/v1/chat/completions"
IFLYTEK_API_URL = f"https://{IFLYTEK_API_HOST}{IFLYTEK_API_PATH}"


class IFlyTekProvider:
    """
    讯飞星火大模型 Provider。

    使用 HMAC-SHA256 签名认证（host + date + request-line），
    请求/响应体与 OpenAI Chat Completions 兼容。
    """

    def __init__(
        self,
        model_name: str = "generalv3.5",
        base_url: str = IFLYTEK_API_URL,
        api_key: str = "",
        api_secret: str = "",
        app_id: str = "",
        **kwargs,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret
        self.app_id = app_id
        self._client = httpx.Client(timeout=120.0)

    # -------------------------------------------------------------------------
    # 讯飞 HMAC-SHA256 签名
    # -------------------------------------------------------------------------

    def _generate_auth_header(self) -> tuple[str, str]:
        """
        生成讯飞 Spark Open API 的 Authorization 头和 Date 值。

        签名原文：host + date + request-line
        签名算法：HMAC-SHA256

        Returns:
            tuple: (Authorization header value, date string for Date header)
        """
        date_str = formatdate(time.time(), usegmt=True)
        request_line = f"POST {IFLYTEK_API_PATH} HTTP/1.1"
        sign_string = f"host: {IFLYTEK_API_HOST}\ndate: {date_str}\n{request_line}"

        signature_raw = hmac.new(
            self.api_secret.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_raw).decode("utf-8")

        auth = (
            f'api_key="{self.api_key}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature}"'
        )
        return auth, date_str

    # -------------------------------------------------------------------------
    # LLM 调用
    # -------------------------------------------------------------------------

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: Any,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        调用讯飞星火 Spark Open API（OpenAI 兼容格式）。

        请求体为标准 Chat Completions 格式，响应体同样是 OpenAI 兼容格式。
        """
        auth_header, date_str = self._generate_auth_header()

        temperature = kwargs.get(
            "temperature",
            config.temperature if hasattr(config, "temperature") else 0.5,
        )
        max_tokens = kwargs.get(
            "max_tokens",
            config.max_tokens if hasattr(config, "max_tokens") else 2048,
        )

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
            "Date": date_str,
            "Host": IFLYTEK_API_HOST,
        }

        start_time = time.time()
        try:
            response = self._client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # OpenAI 兼容响应格式：choices[0].message.content
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")

            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
            cost = total_tokens * 0.000001  # 粗估

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model": self.model_name,
                "latency_ms": int((time.time() - start_time) * 1000),
            }

        except httpx.HTTPStatusError as e:
            logger.error(
                f"[IFlyTek] HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"[IFlyTek] API call failed: {e}")
            raise
