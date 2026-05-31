# REVIEW-011-FIX-R3: Stage-11 统计看板第三次修复复审报告

## 1. 审查结论

**通过**

本轮只复审唯一剩余问题：`GET /api/statistics/model-calls` 的 `date_from` / `date_to` / `project_id` SQL 参数构造是否可靠。

复审结论：

- `date_from` / `date_to` 不再互相覆盖。
- `project_id + date_from + date_to` 同时存在时，SQL 占位符顺序与 `params` 顺序一致。
- 未发现新的参数错位风险。
- 允许进入 Stage-12。

## 2. date_from/date_to 同时存在时 SQL 与 params 是否一致

**一致。**

`backend/app/repositories/statistics_repo.py` 中 `get_model_call_stats()` 已改为使用 `date_conditions` 列表累积日期条件：

```python
date_conditions = []
if date_from:
    date_conditions.append("ai.created_at >= %s")
    params.append(date_from)
if date_to:
    date_conditions.append("ai.created_at <= %s")
    params.append(date_to + " 23:59:59")
```

随后通过：

```python
conditions = ["m.is_deleted = 0", project_filter]
conditions.extend(date_conditions)
where_clause = " AND ".join(c for c in conditions if c)
```

构造 SQL。这样当 `date_from` 和 `date_to` 同时存在时，SQL 会同时包含：

- `ai.created_at >= %s`
- `ai.created_at <= %s`

`params` 也会按同一顺序包含：

- `date_from`
- `date_to + " 23:59:59"`

因此占位符数量与参数数量一致。

## 3. project_id + date_from + date_to 是否不会参数错位

**不会参数错位。**

静态审查确认以下组合均安全：

1. 只有 `project_id`：SQL 包含 `ai.project_id = %s`，`params = [project_id]`。
2. 只有 `date_from`：SQL 包含 `ai.created_at >= %s`，`params = [date_from]`。
3. 只有 `date_to`：SQL 包含 `ai.created_at <= %s`，`params = [date_to + " 23:59:59"]`。
4. `date_from + date_to`：SQL 包含两个日期条件，`params = [date_from, date_to + " 23:59:59"]`。
5. `project_id + date_from`：`params = [project_id, date_from]`，占位符顺序一致。
6. `project_id + date_to`：`params = [project_id, date_to + " 23:59:59"]`，占位符顺序一致。
7. `project_id + date_from + date_to`：`params = [project_id, date_from, date_to + " 23:59:59"]`，占位符顺序一致。
8. 非 admin 无 `project_id` 且带日期：先追加参与项目 ID，再追加日期参数，SQL 中也是 `ai.project_id IN (...)` 在前、日期条件在后。
9. 非 admin 有 `project_id`：service 层仍先调用 `check_user_can_access_project()` 做权限校验，再进入 repository 查询。

## 4. 已通过内容是否保持

确认未破坏以下已通过内容：

- `project_id` 过滤仍通过 `ai.project_id = %s` 或 `ai.project_id IN (...)` 生效。
- 非 admin 不带 `project_id` 时仍只统计自己参与项目范围。
- admin 无 `project_id` 时仍可查看全部调用统计。
- 未重新引用 `ai_invocations.is_deleted` 或 `i.is_deleted`。
- 结果中未返回 `input_text` / `output_text`。
- 未返回 API Key、`encrypted_api_key`、`key_iv`、`key_tag`。
- `call_count` 字段仍存在。
- `success_rate` 仍通过 `CASE WHEN COUNT(ai.invocation_id) > 0` 避免除以 0。

## 5. Stage-11 其他已通过内容

静态确认：

- `GET /api/statistics/projects?project_id=...` 字段仍完整。
- 成员贡献统计仍不只返回当前用户本人。
- `costs` 仍基于 `cost_records`。
- `reviews` 统计仍基于 `output_reviews` / `output_issue_relations`。
- `recent-activities` 仍基于 `operation_logs`。

## 6. 是否发现新问题

未发现本轮范围内的新问题。

## 7. 是否发现越界修改

未发现 Stage-12 内容、前端页面实现或数据库结构修改。

说明：当前工作区中 `database/`、`docs/` 仍显示历史未提交改动；本轮 handoff 声明 Fix R3 未修改这些目录。本轮复审未发现为修复该问题修改数据库结构或实现前端页面。

## 8. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/statistics.py app/services/statistics_service.py app/repositories/statistics_repo.py run.py
```

结果：通过，无 Python 语法错误。

说明：当前 Ubuntu / WSL 环境无法直接访问 Windows MySQL，本轮未执行真实数据库查询，仅进行静态审查和 Python 语法检查。

## 9. 是否允许进入 Stage-12

**允许。**

Stage-11 Fix R3 通过，允许发布 Stage-12。

## 10. Stage-12 发布情况

已发布：

`cursor_and_codex_chat/tasks/todo/TASK-012-backend-final-test.md`
