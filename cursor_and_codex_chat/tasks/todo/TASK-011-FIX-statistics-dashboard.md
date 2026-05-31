# TASK-011-FIX：修复统计看板与课程展示数据模块审查问题

## 任务状态

Codex 第一次修复复审不通过，已发布 TASK-011-FIX-R2。

## 一、任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-011-statistics-dashboard.md` 修复 Stage-11 统计接口问题，使统计 SQL 与冻结 Schema 一致，并补齐接口验收字段。

## 二、允许修改文件

- `backend/app/routers/statistics.py`
- `backend/app/services/statistics_service.py`
- `backend/app/repositories/statistics_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-statistics-dashboard.md`

## 三、禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 四、禁止实现

1. 新业务模块；
2. 前端页面；
3. 数据库结构修改；
4. Stage-12 内容。

## 五、必须修复的问题

### 1. 修复 `ai_invocations.is_deleted` 不存在问题

冻结 Schema 中 `ai_invocations` 是审计表，没有 `is_deleted` 字段。

请修复：

- `statistics_repo.py` 中所有 `ai_invocations.is_deleted` 或 `ai.is_deleted` 查询；
- 不得修改数据库结构；
- 不得给 `ai_invocations` 新增字段；
- 保留项目权限过滤和日期过滤。

### 2. 修复 `task_outputs.project_id` 不存在问题

冻结 Schema 中 `task_outputs` 没有 `project_id` 字段。

成员贡献统计中的 output 数量必须通过以下关系获取项目：

```text
task_outputs.task_id -> project_tasks.task_id -> project_tasks.project_id
```

不得直接查询 `task_outputs.project_id`。

### 3. 补齐项目统计返回字段

`GET /api/statistics/projects` 至少返回：

- `project_id`
- `project_name`
- `member_count`
- `task_count`
- `output_count`
- `approved_output_count`
- `artifact_count`
- `invocation_count`
- `total_cost`

可以保留现有 `total_tasks`、`total_members`、`total_outputs` 等字段，但必须补充上述字段。

### 4. 补齐 model-calls 返回字段

`GET /api/statistics/model-calls` 至少返回：

- `model_id`
- `model_name`
- `display_name`
- `provider_name`
- `call_count`
- `success_count`
- `failed_count`
- `success_rate`
- `avg_latency_ms`
- `total_input_tokens`
- `total_output_tokens`
- `total_tokens`

可保留 `total_invocations`，但必须补充 `call_count`。

### 5. 修复成员贡献统计权限范围

非 admin 无 `project_id` 时，不应只返回当前用户本人。

应返回当前用户参与项目范围内的成员贡献排行：

- 当前用户参与的项目；
- 这些项目中的成员；
- 不泄露无关项目成员贡献；
- 指定 `project_id` 时仍必须做权限校验。

## 六、验收命令

至少执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/statistics.py app/services/statistics_service.py app/repositories/statistics_repo.py run.py
```

## 七、完成后 handoff

完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-011-FIX-statistics-dashboard.md`

handoff 必须说明：

1. 每个阻塞问题如何修复；
2. 是否仍存在 `ai_invocations.is_deleted`；
3. 是否仍存在 `task_outputs.project_id`；
4. projects 和 model-calls 返回字段补齐情况；
5. 成员贡献统计权限范围；
6. Python 语法检查结果；
7. 是否未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
8. 是否未实现新业务模块、前端页面或 Stage-12 内容。

