"""
LLM Gateway - 统一大模型接入网关

支持：
- OpenAI-compatible API 格式
- 本地 Mock 模型
- Qwen / DeepSeek / GLM 等国产模型
"""

import time
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMCallResult:
    """LLM 调用结果"""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    cost: float
    status: str = "success"
    error: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


@dataclass
class LLMConfig:
    """LLM 配置"""
    model_id: int
    model_name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 60
    api_secret: Optional[str] = None  # 讯飞星火认证用
    app_id: Optional[str] = None      # 讯飞星火认证用
    # Tool Calling 支持
    tools: Optional[List[Dict[str, Any]]] = None  # OpenAI tool schema 格式
    tool_choice: Optional[str] = None  # "auto" | "required" | None


class LLMGateway:
    """统一 LLM 网关"""

    def __init__(self):
        self._providers: Dict[str, Any] = {}

    def register_provider(self, name: str, provider: Any) -> None:
        """注册模型供应商"""
        self._providers[name] = provider
        logger.info(f"Registered LLM provider: {name}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: LLMConfig,
        **kwargs,
    ) -> LLMCallResult:
        """统一生成接口"""
        start_time = time.time()

        provider = self._providers.get(config.provider)
        if provider is None:
            logger.error("LLM provider is not registered: %s", config.provider)
            return LLMCallResult(
                content="", model=config.model_name, provider=config.provider,
                input_tokens=0, output_tokens=0, total_tokens=0,
                latency_ms=0, cost=0.0, status="failed",
                error="模型服务不可用",
            )

        try:
            result = provider.generate(messages, config, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)
            return LLMCallResult(
                content=result.get("content", ""),
                model=config.model_name,
                provider=config.provider,
                input_tokens=result.get("input_tokens", 0),
                output_tokens=result.get("output_tokens", 0),
                total_tokens=result.get("input_tokens", 0) + result.get("output_tokens", 0),
                latency_ms=latency_ms,
                cost=result.get("cost", 0.0),
                status="success",
                tool_calls=result.get("tool_calls"),
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return LLMCallResult(
                content="", model=config.model_name, provider=config.provider,
                input_tokens=0, output_tokens=0, total_tokens=0,
                latency_ms=int((time.time() - start_time) * 1000),
                cost=0.0, status="failed", error="模型调用失败"
            )


llm_gateway = LLMGateway()
