"""
Mock Reviewer 模型适配器。

模拟审稿 / 审核建议型输出。
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


class MockReviewerAdapter(BaseModelAdapter):
    """Mock 审稿 / 审核建议模型适配器。"""

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

        output = self._generate_review(full_input)

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

    def _generate_review(self, input_text: str) -> str:
        return f"""# 审稿意见

## 一、总体评价

经过对您提交内容的审阅，**整体质量良好**，内容结构清晰，逻辑较为严谨，符合相关规范要求。

## 二、内容审查

### 2.1 优点

1. **内容完整性**：涵盖了任务要求的主要方面，要点全面；
2. **结构规范性**：章节安排合理，层次分明，便于阅读；
3. **语言表达**：表述准确，用词规范。

### 2.2 需要改进的地方

| 序号 | 问题类型 | 具体描述 | 建议修改方式 |
|---|---|---|---|
| 1 | 内容深度 | 部分章节分析深度不足，建议补充更多数据支撑 | 添加相关统计结果或案例分析 |
| 2 | 逻辑衔接 | 2.3 与 2.4 节之间过渡不够自然 | 增加过渡语句或重新调整段落顺序 |
| 3 | 格式规范 | 图表编号和标题格式不统一 | 统一使用"图 1-1"、"表 1-1"格式 |

## 三、修改建议

### 3.1 内容层面

1. 在关键结论处增加量化数据支撑，提高说服力；
2. 补充对比分析，如与同类工作的对比、实验前后对比等；
3. 完善结论部分，补充局限性说明和未来工作展望。

### 3.2 格式层面

1. 统一全文图表样式和编号规则；
2. 规范参考文献格式（建议使用 GB/T 7714-2015）；
3. 检查全文标点符号使用是否一致。

## 四、总体评分建议

| 评估维度 | 当前评分 | 满分 | 建议得分 |
|---|---|---|---|
| 内容完整性 | B+ | A | A- |
| 逻辑严谨性 | B | A | B+ |
| 格式规范性 | B- | A | B+ |
| 创新性 | B | A | B |

**综合建议**：在终稿提交前，请重点关注上述表格中序号 1-3 的问题。

## 五、结语

本审稿意见仅供参考，作者可根据实际情况采纳或调整。如有疑问，欢迎进一步讨论。

---
*本审稿意见由 Mock Reviewer 模型生成，仅供测试使用。*
"""
