"""
模型适配器模块。

提供统一的模型调用接口抽象和 Mock 实现。
"""

from app.adapters.base_adapter import (
    BaseModelAdapter,
    ModelAdapterConfig,
    ModelResult,
)
from app.adapters.mock_writer_adapter import MockWriterAdapter
from app.adapters.mock_code_adapter import MockCodeAdapter
from app.adapters.mock_reviewer_adapter import MockReviewerAdapter

__all__ = [
    "BaseModelAdapter",
    "ModelAdapterConfig",
    "ModelResult",
    "MockWriterAdapter",
    "MockCodeAdapter",
    "MockReviewerAdapter",
]


def get_adapter_by_model_name(model_name: str) -> BaseModelAdapter:
    """
    根据模型名称获取对应适配器。

    Args:
        model_name: 模型名称（如 'mock-writer'、'mock-code'、'mock-reviewer'）

    Returns:
        对应的适配器实例

    Raises:
        ValueError: 不支持的模型名称
    """
    name_lower = model_name.lower()
    if name_lower == "mock-writer":
        return MockWriterAdapter()
    elif name_lower == "mock-code":
        return MockCodeAdapter()
    elif name_lower == "mock-reviewer":
        return MockReviewerAdapter()
    else:
        raise ValueError(
            f"不支持的模型: {model_name}。"
            f"当前课程版仅支持 Mock 模型: mock-writer, mock-code, mock-reviewer"
        )
