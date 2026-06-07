# TASK-011-FIX-R3：修复统计看板第三次审查问题（date_filter 覆盖）

## 任务状态

已完成。

## 一、任务目标

修复 Codex 复审指出的唯一剩余问题：

`GET /api/statistics/model-calls` 中 `date_from` 和 `date_to` 同时传入时，`date_filter` 被覆盖，导致 SQL 占位符数量与 `params` 参数数量不一致。

## 二、修复内容

将 `date_filter` 标量赋值改为 `date_conditions` 列表累积：

```python
# 修复前（错误）
date_filter = ""
if date_from:
    date_filter = "ai.created_at >= %s"   # 被覆盖！
    params.append(date_from)
if date_to:
    date_filter = "ai.created_at <= %s"
    params.append(date_to + " 23:59:59")

# 修复后（正确）
date_conditions = []
if date_from:
    date_conditions.append("ai.created_at >= %s")
    params.append(date_from)
if date_to:
    date_conditions.append("ai.created_at <= %s")
    params.append(date_to + " 23:59:59")
```

## 三、修改文件

- `backend/app/repositories/statistics_repo.py`
- `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-R3-statistics-dashboard.md`
