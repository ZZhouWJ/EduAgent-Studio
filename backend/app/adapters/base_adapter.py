"""
模型适配器基类。

定义统一的模型调用接口，所有具体适配器必须继承 BaseModelAdapter。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ModelResult:
    """模型调用结果（统一返回结构）。"""
    output_text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    status: str = "success"       # success / failed / timeout
    error_message: Optional[str] = None


@dataclass
class ModelAdapterConfig:
    """模型适配器配置。"""
    model_name: str
    model_id: int
    display_name: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None   # 仅在需要真实调用时使用
    base_url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class BaseModelAdapter(ABC):
    """模型适配器抽象基类。"""

    @abstractmethod
    def generate(
        self,
        input_text: str,
        prompt_content: Optional[str] = None,
        config: Optional[ModelAdapterConfig] = None,
    ) -> ModelResult:
        """
        执行模型生成。

        Args:
            input_text: 用户输入的原始文本
            prompt_content: 提示词模板内容（可拼接在输入前）
            config: 模型适配器配置

        Returns:
            ModelResult 统一返回结构
        """
        ...
