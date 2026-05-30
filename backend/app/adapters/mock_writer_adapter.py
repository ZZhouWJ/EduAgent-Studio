"""
Mock Writer 模型适配器。

模拟中文写作型输出，适合报告、申报书、总结类任务。
输出内容稳定可复现，不访问外部网络。
"""

import re
import time
from typing import Optional

from app.adapters.base_adapter import (
    BaseModelAdapter,
    ModelAdapterConfig,
    ModelResult,
)


class MockWriterAdapter(BaseModelAdapter):
    """Mock 中文写作模型适配器。"""

    def generate(
        self,
        input_text: str,
        prompt_content: Optional[str] = None,
        config: Optional[ModelAdapterConfig] = None,
    ) -> ModelResult:
        start = time.time()

        prompt = prompt_content or ""
        full_input = f"{prompt}\n{input_text}" if prompt else input_text

        input_tokens = self._estimate_tokens(full_input)

        output = self._generate_writing(full_input)

        output_tokens = self._estimate_tokens(output)
        latency_ms = int((time.time() - start) * 1000)

        return ModelResult(
            output_text=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status="success",
        )

    def _estimate_tokens(self, text: str) -> int:
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        other_chars = len(text) - chinese_chars - english_words
        return int(chinese_chars * 0.5 + english_words * 0.75 + other_chars * 0.25)

    def _generate_writing(self, input_text: str) -> str:
        return f"""# 基于输入内容的写作结果

## 一、任务概述

根据您提供的内容，现整理如下：

**原始输入**：{input_text.strip()}

## 二、主要内容

### 2.1 核心要点分析

通过对输入内容的分析，提取以下核心要点：

1. 内容结构完整，逻辑清晰；
2. 主题明确，目标读者定位准确；
3. 语言表达规范，符合学术或工作报告规范。

### 2.2 撰写建议

1. **引言部分**：简要介绍背景和目的，说明研究的必要性和意义；
2. **主体部分**：按照逻辑顺序展开，每一部分都应有具体的案例或数据支撑；
3. **结论部分**：总结全文，提出展望或后续工作建议。

## 三、质量评估

| 评估维度 | 评分 | 说明 |
|---|---|---|
| 内容完整性 | 优 | 涵盖了任务要求的主要方面 |
| 逻辑连贯性 | 良 | 结构合理，层次分明 |
| 语言规范性 | 优 | 表述准确，行文流畅 |

## 四、后续工作建议

1. 补充相关数据和案例支撑；
2. 完善图表和可视化展示；
3. 多次审核校对，确保无误。

---
*本内容由 Mock Writer 模型生成，仅供测试使用。*
"""
