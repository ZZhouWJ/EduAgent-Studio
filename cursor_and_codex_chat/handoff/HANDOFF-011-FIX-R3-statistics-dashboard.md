# HANDOFF-011-FIX-R3：Stage-11 统计看板第三次修复版

## 任务状态

**完成** — Stage-11 Fix R3 唯一剩余问题已修复。

---

## 一、Codex 本轮唯一剩余问题

`GET /api/statistics/model-calls` 中，`date_from` 和 `date_to` 同时传入时，`date_filter` 被覆盖，SQL 只有一个 `%s` 占位符，但 `params` 追加了两个日期参数，导致 SQL 占位符数量与参数数量不一致。

---

## 二、本次修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/repositories/statistics_repo.py` | 修复 `get_model_call_stats()` 中的 `date_filter` 覆盖问题 |
| `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-R3-statistics-dashboard.md` | 新建 |

**说明**：未修改 `database/*`、`frontend/*`、`docs/*`、`statistics_service.py`。

---

## 三、date_from/date_to 为什么会参数错位

**修复前**（错误代码）：

```python
date_filter = ""
if date_from:
    date_filter = "ai.created_at >= %s"   # date_filter 被赋值
    params.append(date_from)
if date_to:
    date_filter = "ai.created_at <= %s"   # date_filter 被覆盖！
    params.append(date_to + " 23:59:59")

conditions = ["m.is_deleted = 0", project_filter, date_filter]
```

问题：

- 当 `date_from` 和 `date_to` 同时存在时，`date_filter` 最终只包含 `"ai.created_at <= %s"`
- SQL 中 `WHERE {where_clause}` 只有 **1 个**日期占位符
- 但 `params` 追加了 **2 个**日期参数
- 结果：SQL 占位符数量（1）与 `params` 长度（2）不一致，MySQL 执行报错

---

## 四、修复后如何保证 SQL 占位符与 params 一致

**修复后**（正确代码）：

```python
# 2. date 过滤（列表累积，避免 date_from 被 date_to 覆盖）
date_conditions = []
if date_from:
    date_conditions.append("ai.created_at >= %s")
    params.append(date_from)
if date_to:
    date_conditions.append("ai.created_at <= %s")
    params.append(date_to + " 23:59:59")

# 构建 WHERE 子句
conditions = ["m.is_deleted = 0", project_filter]
conditions.extend(date_conditions)
where_clause = " AND ".join(c for c in conditions if c)
```

**保证一致的机制**：

- 每个条件独立 `append` 到 `date_conditions` 列表，不会覆盖
- `conditions.extend(date_conditions)` 将所有日期条件追加到主列表
- SQL 占位符数量 = `conditions` 非空元素数量 = `params` 长度
- 无论有多少个日期条件，始终一一对应

---

## 五、已支持哪些参数组合

所有 10 种组合均无参数错位风险：

| # | project_id | date_from | date_to | params 顺序 |
|---|---|---|---|---|
| 1 | 无 | 无 | 无 | `[]`（无日期占位符）|
| 2 | 明确值 | 无 | 无 | `[project_id]` |
| 3 | 无 | 有 | 无 | `[date_from]` |
| 4 | 无 | 无 | 有 | `[date_to]` |
| 5 | 无 | 有 | 有 | `[date_from, date_to]` |
| 6 | 明确值 | 有 | 无 | `[project_id, date_from]` |
| 7 | 明确值 | 无 | 有 | `[project_id, date_to]` |
| 8 | 明确值 | 有 | 有 | `[project_id, date_from, date_to]` |
| 9 | 非 admin 无，allowed_project_ids | 有/无 | 有/无 | `[id1, ..., date_from?, date_to?]` |
| 10 | 非 admin 有，已校验 | 有/无 | 有/无 | `[project_id, date_from?, date_to?]` |

SQL 占位符顺序：`m.is_deleted = 0` → `project_filter` → `date_from` → `date_to`，与 `params.append` 顺序严格对应。

---

## 六、是否修改 database

**否**。

---

## 七、是否修改 frontend

**否**。

---

## 八、是否实现 Stage-12

**否**。

---

## 九、Python 语法检查命令

```bash
cd backend
python -m py_compile app/repositories/statistics_repo.py app/services/statistics_service.py
```

结果：`EXIT:0`（通过）。

---

## 十、当前环境限制

- 当前环境无 MySQL，无法真实执行 SQL 验证，基于静态代码审查
- 未修改 `database/` 目录，未修改表结构

---

## 十一、需要 Codex 复审的重点

1. **`date_conditions` 列表累积**：确认 `date_from` 和 `date_to` 各自独立 `append`，不会相互覆盖
2. **`conditions.extend(date_conditions)`**：确认日期条件追加到主条件列表，而非覆盖
3. **参数顺序一致性**：确认 10 种参数组合的 `params` 顺序与 SQL 占位符顺序一致
4. **已通过内容未被破坏**：确认以下内容仍正常：
   - `get_project_stats_by_id()` 返回 9 个统一字段
   - `ai_invocations.is_deleted` 未被重新引用
   - `task_outputs.project_id` 未被重新引用
   - `call_count` 字段存在
   - 非 admin 成员贡献统计范围正确
   - 无 `input_text`/`output_text`/`API Key` 返回
5. **无越界**：确认未修改 `database/*`、`frontend/*`、`docs/*`

---

## 十二、验收清单

- [x] `date_filter` 覆盖问题已修复（改为 `date_conditions` 列表累积）
- [x] SQL 占位符数量与 params 长度严格一致
- [x] 所有 10 种参数组合无参数错位风险
- [x] 已通过内容未被破坏
- [x] Python 语法检查通过
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`

---

**本修复完成后停止，等待 Codex 复审。**
