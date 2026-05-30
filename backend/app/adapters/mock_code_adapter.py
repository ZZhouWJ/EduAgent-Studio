"""
Mock Code 模型适配器。

模拟代码解释或 SQL 生成型输出。
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


class MockCodeAdapter(BaseModelAdapter):
    """Mock 代码 / SQL 生成模型适配器。"""

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

        output = self._generate_code_response(full_input)

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

    def _generate_code_response(self, input_text: str) -> str:
        has_sql = "sql" in input_text.lower() or "查询" in input_text or "数据库" in input_text
        has_code = "python" in input_text.lower() or "代码" in input_text or "function" in input_text.lower()

        if has_sql:
            return self._generate_sql_response(input_text)
        elif has_code:
            return self._generate_code_response_impl(input_text)
        else:
            return self._generate_general_response(input_text)

    def _generate_sql_response(self, input_text: str) -> str:
        return f"""# SQL 查询分析结果

## 原始需求
{input_text.strip()}

## 建议 SQL 查询

```sql
-- 基于输入需求生成的示例 SQL
SELECT
    t.task_id,
    t.title       AS task_title,
    t.status      AS task_status,
    p.project_name,
    u.username    AS assignee,
    t.created_at
FROM project_tasks t
INNER JOIN projects p ON t.project_id = p.project_id
LEFT JOIN users u ON t.assignee_id = u.user_id
WHERE t.is_deleted = 0
  AND p.is_deleted = 0
  AND u.is_deleted = 0
  -- 可根据实际需求添加 WHERE 条件
ORDER BY t.created_at DESC
LIMIT 100;
```

## 查询说明

1. 该查询从 `project_tasks` 表出发，关联 `projects` 和 `users` 表；
2. 使用 `INNER JOIN` 确保项目存在，使用 `LEFT JOIN` 确保即使没有负责人也返回记录；
3. 所有关联表均过滤 `is_deleted = 0`，保证只返回未删除数据；
4. 可根据实际需求添加更多 WHERE 条件或 JOIN 条件。

## 优化建议

- 确保相关字段建立了索引（如 `project_tasks.project_id`、`task_assignee_id`）；
- 大数据量时可考虑分页查询；
- 敏感字段请在 SELECT 中做脱敏处理。

---
*本内容由 Mock Code 模型生成，仅供测试使用。*
"""

    def _generate_code_response_impl(self, input_text: str) -> str:
        return f"""# 代码分析结果

## 原始需求
{input_text.strip()}

## Python 示例代码

```python
from typing import List, Dict, Any, Optional
from datetime import datetime


def process_task_data(
    tasks: List[Dict[str, Any]],
    filter_status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    \"\"\"
    处理任务数据，按状态过滤并返回结果。

    Args:
        tasks: 原始任务列表
        filter_status: 可选的状态过滤条件

    Returns:
        处理后的任务列表
    \"\"\"
    result = []

    for task in tasks:
        # 过滤已删除任务
        if task.get("is_deleted"):
            continue

        # 状态过滤
        if filter_status and task.get("status") != filter_status:
            continue

        # 数据转换
        processed = {{
            "task_id": task["task_id"],
            "title": task["title"],
            "status": task["status"],
            "created_at": task["created_at"].isoformat()
                if isinstance(task["created_at"], datetime)
                else task["created_at"],
        }}
        result.append(processed)

    return result


# 使用示例
if __name__ == "__main__":
    sample_tasks = [
        {{"task_id": 1, "title": "需求分析", "status": "draft",
          "is_deleted": 0, "created_at": datetime.now()}},
        {{"task_id": 2, "title": "数据库设计", "status": "running",
          "is_deleted": 0, "created_at": datetime.now()}},
    ]
    result = process_task_data(sample_tasks, filter_status="draft")
    print(result)
```

## 代码说明

1. 函数接受任务列表和可选的状态过滤参数；
2. 遍历所有任务，跳过已删除或不符合过滤条件的任务；
3. 将 `datetime` 对象转换为 ISO 格式字符串，确保 JSON 序列化兼容；
4. 返回处理后的干净数据列表。

---
*本内容由 Mock Code 模型生成，仅供测试使用。*
"""

    def _generate_general_response(self, input_text: str) -> str:
        return f"""# 代码分析结果

## 原始需求
{input_text.strip()}

## 建议处理流程

```text
1. 需求理解
   └─ 明确输入内容的核心目标

2. 方案设计
   └─ 制定实现策略和技术选型

3. 代码实现
   └─ 按模块编写代码，遵循编码规范

4. 测试验证
   └─ 编写单元测试，确保覆盖率

5. 文档完善
   └─ 补充 README 和 API 文档
```

## 建议使用技术栈

- **后端**：Python / FastAPI / MySQL
- **前端**：Vue.js / Element Plus
- **工具**：Git / Docker / Postman

---
*本内容由 Mock Code 模型生成，仅供测试使用。*
"""
