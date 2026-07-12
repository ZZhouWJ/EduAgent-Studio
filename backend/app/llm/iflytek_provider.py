"""
讯飞星火大模型 Provider

支持星火 V3.5（domain=general），接口与 OpenAI Chat Completions 兼容。
认证方式：HMAC-SHA1 签名（不同于 OpenAI Bearer Token）。

文档：https://www.xfyun.cn/doc/spark/
"""

import base64
import hashlib
import hmac
import logging
import time
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

# 讯飞 V3.5 API 地址
IFLYTEK_API_URL = "https://spark-api.xf-yun.com/v3.1/chat"


class IFlyTekProvider:
    """
    讯飞星火大模型 Provider（V3.5）。

    使用 HMAC-SHA1 签名认证，请求/响应体与 OpenAI 不兼容，需要转换。
    """

    def __init__(
        self,
        model_name: str = "general",
        base_url: str = IFLYTEK_API_URL,
        api_key: str = "",
        api_secret: str = "",
        app_id: str = "",
        **kwargs,
    ):
        self.model_name = model_name          # 星火 domain，如 "general"
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret
        self.app_id = app_id
        self._client = httpx.Client(timeout=120.0)

    # -------------------------------------------------------------------------
    # 讯飞认证签名
    # -------------------------------------------------------------------------

    def _generate_auth(self) -> Dict[str, str]:
        """
        生成讯飞认证参数。

        讯飞使用 HMAC-SHA1 签名：
          sign = base64(HMAC-SHA1(api_secret, f"{app_id}{timestamp}"))

        Returns:
            dict: {"header": {"app_id": ..., "timestamp": ..., "sign": ...}}
        """
        timestamp = str(int(time.time()))
        # 签名原文：app_id + timestamp
        sign_str = f"{self.app_id}{timestamp}"
        sign = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                sign_str.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("utf-8")

        return {
            "app_id": self.app_id,
            "timestamp": timestamp,
            "sign": sign,
        }

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
        调用讯飞星火 V3.5 chat API。

        请求体需要转换为讯飞格式（header/parameter/payload 三层），
        响应体再从讯飞格式转回 OpenAI 兼容格式。
        """
        auth = self._generate_auth()

        # 将 OpenAI 格式 messages 转为讯飞格式
        # 讯飞只支持 user/assistant 角色，且 content 在 payload.message.text 数组中
        text_messages = self._convert_messages(messages)

        temperature = kwargs.get("temperature", config.temperature if hasattr(config, "temperature") else 0.5)
        max_tokens = kwargs.get("max_tokens", config.max_tokens if hasattr(config, "max_tokens") else 2048)

        payload = {
            "header": {
                "app_id": auth["app_id"],
                "timestamp": auth["timestamp"],
                "sign": auth["sign"],
            },
            "parameter": {
                "chat": {
                    "domain": self.model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": text_messages,
                }
            },
        }

        url = f"{self.base_url}/chat"
        headers = {"Content-Type": "application/json"}

        start_time = time.time()
        try:
            response = self._client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # 解析讯飞响应
            content = self._parse_response(data)
            usage = data.get("payload", {}).get("usage", {})

            input_tokens = usage.get("text", [{}])[0].get("role_tokens", 0) or len(str(messages)) // 4
            output_tokens = usage.get("text", [{}])[0].get("role_tokens", 0) or len(content) // 4
            cost = (input_tokens + output_tokens) * 0.000001  # 讯飞按token计费，粗估

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model": self.model_name,
                "latency_ms": int((time.time() - start_time) * 1000),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"[IFlyTek] HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[IFlyTek] API call failed: {e}")
            raise

    # -------------------------------------------------------------------------
    # 消息格式转换（OpenAI → 讯飞）
    # -------------------------------------------------------------------------

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        将 OpenAI 格式 messages 转为讯飞格式。

        讯飞 text 数组格式：{"role": "user"/"assistant", "content": "..."}
        只支持 user/assistant/system，系统提示合并到首条 user 消息。
        """
        text_messages: List[Dict[str, str]] = []
        system_prompt = ""

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_prompt = content
            elif role == "user":
                text_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                text_messages.append({"role": "assistant", "content": content})
            else:
                # 其他角色统一当 user 处理
                text_messages.append({"role": "user", "content": f"[{role}]: {content}"})

        # 如果有系统提示，合并到首条 user 消息
        if system_prompt and text_messages:
            first = text_messages[0]
            first["content"] = f"[系统提示]\n{system_prompt}\n\n[用户问题]\n{first['content']}"

        return text_messages

    # -------------------------------------------------------------------------
    # 响应解析（讯飞 → 标准）
    # -------------------------------------------------------------------------

    def _parse_response(self, data: Dict[str, Any]) -> str:
        """从讯飞响应体中提取文本内容。"""
        header = data.get("header", {})
        code = header.get("code", 0)
        if code != 0:
            error_msg = header.get("message", "unknown error")
            logger.error(f"[IFlyTek] API error code={code}: {error_msg}")
            raise RuntimeError(f"IFlyTek API error: {error_msg} (code={code})")

        choices = data.get("payload", {}).get("choices", {})
        texts = choices.get("text", [])
        if texts:
            return texts[0].get("content", "")

        # 备选：直接取 audit 文本
        audit_text = data.get("payload", {}).get("audit", {}).get("text", "")
        if audit_text:
            return audit_text

        raise RuntimeError(f"IFlyTek response has no content: {data}")
