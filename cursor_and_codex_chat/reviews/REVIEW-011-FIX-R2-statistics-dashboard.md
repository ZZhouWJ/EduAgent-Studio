# REVIEW-011-FIX-R2: Stage-11 统计看板第二次修复复审报告

## 1. 审查结论

**不通过**

本轮只复审 `REVIEW-011-FIX-statistics-dashboard.md` 中剩余 2 个阻塞问题。结论如下：

- `GET /api/statistics/projects?project_id=...` 单项目统计字段已补齐，通过。
- `GET /api/statistics/model-calls` 的 `project_id/date_from/date_to` 过滤仍不可靠，不通过。

因此本轮不允许进入 Stage-12，不发布 `TASK-012-backend-final-test.md`。

## 2. 单项目统计字段是否已补齐

**已补齐。**

`backend/app/repositories/statistics_repo.py` 中 `get_project_stats_by_id()` 已重写，返回字段与项目统计列表保持一致，至少包含：

- `project_id`
- `project_name`
- `member_count`
- `task_count`
- `output_count`
- `approved_output_count`
- `artifact_count`
- `invocation_count`
- `total_cost`

检查结果：

- `member_count` 来自 `project_members`，过滤 `is_deleted = 0`。
- `task_count` 来自 `project_tasks`，过滤 `is_deleted = 0`。
- `output_count` 通过 `task_outputs.task_id -> project_tasks.project_id` 统计，未引用不存在的 `task_outputs.project_id`。
- `approved_output_count` 基于 `task_outputs.status = 'approved'`。
- `artifact_count` 来自 `adopted_outputs`。
- `invocation_count` 来自 `ai_invocations`。
- `total_cost` 来自 `cost_records`。
- 各统计字段使用 `COALESCE(..., 0)`，空统计不会返回 `None`。
- SQL 使用 `%s` 参数化查询。
- `project_id` 过滤权限仍在 `statistics_service.list_project_stats()` 中调用 `check_user_can_access_project()`。

## 3. model-calls 的 project_id/date 过滤是否可靠

**仍不可靠。**

已修复的部分：

- 不再存在 `project_join` / `sub_params` 残留变量。
- `project_id` 明确传入时，SQL 中已加入 `ai.project_id = %s`。
- 非 admin 未传 `project_id` 时，会先查询当前用户参与项目，再使用 `ai.project_id IN (...)` 限制范围。
- 未发现 `ai_invocations.is_deleted` 或 `i.is_deleted` 引用。
- 查询结果未返回 `input_text`、`output_text`、API Key、`encrypted_api_key`、`key_iv`、`key_tag`。

仍存在的阻塞问题：

`get_model_call_stats()` 中日期过滤只保留了一个 `date_filter` 字符串：

```python
date_filter = ""
if date_from:
    date_filter = "ai.created_at >= %s"
    params.append(date_from)
if date_to:
    date_filter = "ai.created_at <= %s"
    params.append(date_to + " 23:59:59")
```

当 `date_from` 和 `date_to` 同时存在时：

- `params` 会追加两个日期参数；
- 但 `date_filter` 会被 `date_to` 覆盖，最终 SQL 只包含 `ai.created_at <= %s` 一个日期占位符；
- SQL 占位符数量与参数数量不一致；
- `project_id + date_from + date_to` 同时存在时同样会出现参数数量/顺序不匹配；
- 该接口可能运行时报错，无法满足“project_id/date_from/date_to 过滤可靠”的验收要求。

必须修复为能同时拼接两个日期条件，例如将日期条件分别追加到 `conditions`：

```python
if date_from:
    conditions.append("ai.created_at >= %s")
    params.append(date_from)
if date_to:
    conditions.append("ai.created_at <= %s")
    params.append(date_to + " 23:59:59")
```

或使用等价方式，确保 SQL 占位符顺序与 `params` 顺序严格一致。

## 4. 是否发现新问题

未发现与本轮范围无关的新业务问题。

本轮剩余问题属于上一轮阻塞点 P0-2 的继续未完全修复：`model-calls` 日期过滤参数和 SQL 占位符不一致。

## 5. 是否发现越界修改

未发现 Stage-12 内容、前端页面实现或数据库结构修改。

说明：

- 当前工作区中 `database/`、`docs/` 仍显示历史未提交改动；本轮 handoff 声明 Fix R2 未修改这些目录。
- 未发现为了本轮修复新增业务表、修改数据库脚本或实现后端最终联调内容。

## 6. 不得破坏已通过内容检查

静态检查结果：

- `overview` 接口仍存在。
- `costs` 接口仍基于 `cost_records`。
- `reviews` 统计仍基于 `output_reviews` / `output_issue_relations`。
- `member-contributions` 仍按当前用户参与项目范围返回成员贡献，不再只返回当前用户本人。
- `recent-activities` 仍基于 `operation_logs`。
- `project_id` 明确传入时，权限过滤仍在 service 层调用 `check_user_can_access_project()`。

## 7. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/statistics.py app/services/statistics_service.py app/repositories/statistics_repo.py run.py
```

结果：通过，无 Python 语法错误。

说明：当前 Ubuntu / WSL 环境无法直接访问 Windows MySQL，本轮未执行真实数据库查询，仅进行静态审查和 Python 语法检查。

## 8. 是否允许进入 Stage-12

**不允许。**

## 9. 剩余问题

仅剩 1 个阻塞问题：

### P0：修复 `GET /api/statistics/model-calls` 同时传入 `date_from` 和 `date_to` 时的参数/占位符不一致

要求：

1. `date_from` 和 `date_to` 同时存在时，SQL 必须同时包含：
   - `ai.created_at >= %s`
   - `ai.created_at <= %s`
2. `params` 顺序必须与 SQL 占位符顺序一致。
3. `project_id + date_from + date_to` 同时存在时不得参数错位。
4. 非 admin 无 `project_id` 时，项目范围参数与日期参数顺序也必须一致。
5. 修复后重新执行 `py_compile`。

## 10. Stage-12 发布情况

未发布 `cursor_and_codex_chat/tasks/todo/TASK-012-backend-final-test.md`。
