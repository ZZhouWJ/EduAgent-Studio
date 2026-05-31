# REVIEW-011 统计看板与课程展示数据模块审查报告

## 1. 审查结论

**不通过。**

Stage-11 已实现 7 个统计接口并注册路由，Python 语法检查通过；但存在冻结 Schema 不匹配的 SQL，会在真实 MySQL 中报错，同时部分接口返回字段不满足本轮验收要求。因此暂不允许进入 Stage-12。

## 2. Stage-11 是否遵守任务范围

基本遵守。

- 已实现 `backend/app/routers/statistics.py`、`backend/app/services/statistics_service.py`、`backend/app/repositories/statistics_repo.py`；
- `backend/app/main.py` 已注册 `statistics.router`；
- 未发现新增 AI 调用、审核中心业务或成果库业务写入；
- 未发现前端页面实现；
- `git status` 仍显示 `database/*` 与 `docs/*` 为已修改状态，这与前序阶段历史脏工作区一致；本轮 handoff 声明未修改 `database/*`、`frontend/*`、`docs/*`，本轮不据此扩大为全量归因审查。

## 3. overview 接口是否正确

**基本正确。**

`GET /api/statistics/overview` 已实现，返回 `project_count`、`active_project_count`、`task_count`、`pending_review_count`、`invocation_count`、`success_invocation_count`、`failed_invocation_count`、`artifact_count`、`total_tokens`、`total_cost`。空数据通过 `or 0` / `COALESCE` 处理，使用统一返回格式。非 admin 使用项目成员范围过滤。

## 4. projects 统计接口是否正确

**不通过。**

`GET /api/statistics/projects` 已实现，权限校验存在，也调用 `v_project_task_statistics`。

阻塞问题：

- 返回字段不满足验收要求。当前列表查询返回 `total_members`、`total_tasks`、`total_outputs`，但验收要求至少包含 `member_count`、`task_count`、`output_count`、`approved_output_count`、`artifact_count`、`invocation_count`、`total_cost`；
- 当前实现缺少 `approved_output_count`、`invocation_count`、`total_cost`；
- 字段名也未按契约要求提供 `member_count`、`task_count`、`output_count`。

代码位置：`backend/app/repositories/statistics_repo.py:171-189`、`backend/app/repositories/statistics_repo.py:198-220`

## 5. model-calls 统计接口是否正确

**不通过。**

`GET /api/statistics/model-calls` 已实现，支持 `project_id`、`date_from`、`date_to`，并做 project_id 权限校验。

阻塞问题：

1. SQL 引用了不存在的 `ai_invocations.is_deleted`：
   - `backend/app/repositories/statistics_repo.py:278`
   - `backend/app/repositories/statistics_repo.py:322`
   - 冻结 Schema 中 `ai_invocations` 是审计表，没有 `is_deleted` 字段；
   - 真实 MySQL 中会报 `Unknown column 'is_deleted'`。

2. 返回字段使用 `total_invocations`，未提供验收要求的 `call_count` 字段。

敏感字段方面：未返回 `input_text`、`output_text`、API Key 或密钥字段。

## 6. costs 统计接口是否正确

**基本正确。**

`GET /api/statistics/costs` 基于 `cost_records` 汇总，包含 `total_cost`、`input_cost`、`output_cost`、`total_tokens`、`currency`、`cost_by_model`、`cost_by_project`、`cost_by_user`。支持 `project_id`、`date_from`、`date_to`，project_id 过滤在 service 层做权限校验。未发现硬编码虚假成本或密钥字段返回。

## 7. reviews 统计接口是否正确

**基本正确。**

`GET /api/statistics/reviews` 已实现审核结论数量、平均评分和 `top_issue_tags`，project_id 权限校验存在，不返回完整 output content。空评分通过 `COALESCE(AVG(...), 0)` 处理。

## 8. member-contributions 接口是否正确

**不通过。**

阻塞问题：

1. SQL 引用了不存在的 `task_outputs.project_id`：
   - `backend/app/repositories/statistics_repo.py:613-616`
   - 冻结 Schema 中 `task_outputs` 只有 `task_id`，项目需通过 `project_tasks` 关联获取。

2. SQL 再次引用不存在的 `ai_invocations.is_deleted`：
   - `backend/app/repositories/statistics_repo.py:631-634`
   - `ai_invocations` 没有 `is_deleted` 字段。

3. 非 admin 无 project_id 时使用 `pm.user_id = 当前用户` 过滤：
   - 这只返回当前用户自己的贡献；
   - 任务要求是“项目成员只能查看自己参与项目的成员贡献”，用于成员贡献排行时应返回其可访问项目内的成员贡献，而不是只返回自己。

未发现 `password_hash`、email、phone 返回。

## 9. recent-activities 接口是否正确

**基本正确。**

`GET /api/statistics/recent-activities` 基于 `operation_logs` 查询，支持 project_id 和 limit，limit 限制为 1 到 100，按 `created_at DESC` 排序，返回字段符合要求，未返回敏感字段。

## 10. Repository 层和参数化 SQL 是否符合要求

**部分符合。**

- SQL 集中在 `statistics_repo.py`；
- service 层未直接写 SQL；
- 未使用 ORM；
- 用户输入通过参数绑定，`LIMIT` 也使用参数；
- 使用了 COUNT、SUM、AVG、GROUP BY、CASE WHEN 等聚合；
- 使用了 `v_project_task_statistics` 和 `v_model_invocation_statistics` 视图。

阻塞问题是 SQL 字段与冻结 Schema 不匹配：`ai_invocations.is_deleted` 不存在，`task_outputs.project_id` 不存在。

## 11. 权限控制是否符合要求

**部分符合。**

- service 层对 `project_id` 过滤做了权限校验；
- admin 可以查看全局；
- 非 admin 查询多数通过项目成员关系过滤；
- 但成员贡献统计在无 project_id 时只返回当前用户，不符合项目成员贡献排行场景，应改为限制在当前用户参与的项目范围内。

## 12. 敏感字段过滤是否符合要求

**符合。**

未发现统计接口返回 `password_hash`、API Key、`encrypted_api_key`、`key_iv`、`key_tag`、完整 `input_text`、完整 `output_text`、email、phone。

## 13. 路由注册是否正确

**正确。**

`backend/app/main.py` 已导入并注册 `statistics.router`，可形成本轮要求的 7 个 `/api/statistics/*` 路径。

## 14. 是否发现越界实现

未发现新增业务表、数据库结构修改、前端页面、新增 AI 调用逻辑、审核中心业务、成果库业务或 Stage-12 内容。

说明：工作区历史脏状态仍存在，但本轮审查对象内未发现越界业务实现。

## 15. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/statistics.py app/services/statistics_service.py app/repositories/statistics_repo.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准；
- 不因无法连接 MySQL 直接判定失败，但 SQL 字段错误是静态可确认问题。

## 16. 是否允许进入 Stage-12

**不允许。**

## 17. 必须修复的问题

1. 修复 `ai_invocations.is_deleted` 不存在问题：
   - 删除 `ai_invocations` 相关 SQL 中的 `is_deleted = 0` 条件；
   - 涉及 `statistics_repo.py:278`、`statistics_repo.py:322`、`statistics_repo.py:634`；
   - 保持项目权限过滤和日期过滤。

2. 修复 `task_outputs.project_id` 不存在问题：
   - 成员贡献统计中 output 数量应通过 `task_outputs -> project_tasks` 关联到项目；
   - 不得直接使用 `task_outputs.project_id`。

3. 修复项目统计返回字段：
   - 至少返回 `project_id`、`project_name`、`member_count`、`task_count`、`output_count`、`approved_output_count`、`artifact_count`、`invocation_count`、`total_cost`；
   - 可以在保留现有 `total_*` 字段的同时补充规范字段。

4. 修复 model-calls 返回字段：
   - 至少提供 `call_count`；
   - 可保留 `total_invocations`，但必须补充 `call_count` 以满足验收。

5. 修复成员贡献统计权限范围：
   - 非 admin 无 project_id 时，应返回当前用户参与项目范围内的成员贡献排行；
   - 不应只返回当前用户本人。

6. 修复后创建 `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-statistics-dashboard.md`，说明上述问题逐条修复情况和语法检查结果。

