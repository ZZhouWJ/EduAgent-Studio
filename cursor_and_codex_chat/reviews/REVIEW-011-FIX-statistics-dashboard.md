# REVIEW-011-FIX: Stage-11 统计看板修复复审报告

## 1. 审查结论

**不通过**

Stage-11 Fix 已修复部分上一轮阻塞问题，但仍有 2 个与本轮验收直接相关的问题未完全修复：

1. `GET /api/statistics/projects?project_id=...` 仍未返回验收要求的完整项目统计字段。
2. `GET /api/statistics/model-calls` 的 `project_id` 过滤逻辑仍存在明显错误，可能返回跨项目统计或参数错位。

因此本轮不允许进入 Stage-12，不发布 `TASK-012-backend-final-test.md`。

## 2. 5 个阻塞问题修复情况

### 2.1 ai_invocations.is_deleted 是否已移除

**已修复。**

检查结果：

- `backend/app/repositories/statistics_repo.py` 未再引用 `ai_invocations.is_deleted`。
- 未发现 `i.is_deleted` 或等价的调用表软删除字段引用。
- 调用相关统计改为通过 `projects.is_deleted = 0`、项目成员关系等现有字段控制范围。
- 未发现为了修复该问题修改数据库结构。

### 2.2 task_outputs.project_id 是否已修复

**已修复。**

检查结果：

- `statistics_repo.py` 未再引用 `task_outputs.project_id`。
- 未发现 `o.project_id`。
- 成员贡献统计中的输出归属已通过：

```sql
task_outputs o
INNER JOIN project_tasks pt ON o.task_id = pt.task_id
```

再由 `project_tasks.project_id` 判断项目归属。

### 2.3 项目统计字段是否补齐

**部分修复，仍不通过。**

`list_project_stats()` 在未传 `project_id` 时已补齐：

- `member_count`
- `task_count`
- `output_count`
- `approved_output_count`
- `artifact_count`
- `invocation_count`
- `total_cost`

但 `GET /api/statistics/projects?project_id=...` 的 service 层会调用 `get_project_stats_by_id()`，该方法仍返回：

- `total_members`
- `total_tasks`
- `total_outputs`
- `artifact_count`

并缺少或未按验收字段名返回：

- `member_count`
- `task_count`
- `output_count`
- `approved_output_count`
- `invocation_count`
- `total_cost`

这会导致带 `project_id` 的项目统计接口仍不满足 Stage-11 验收要求。

### 2.4 模型调用统计 call_count 是否补齐

**部分修复，仍不通过。**

`call_count` 字段已补齐，但 `project_id` 过滤存在严重逻辑问题：

1. `get_model_call_stats()` 构造了 `project_join`，但最终 SQL 没有使用该变量。
2. admin 只传 `project_id` 且不传日期时，代码先查出该项目使用过的 `model_id`，然后从 `v_model_invocation_statistics` 返回这些模型的全局统计，不是该项目内统计。
3. 传入 `project_id + date_from/date_to` 时，`project_id` 被加入 `params`，但复杂 SQL 没有对应的 `project_id = %s` 条件，存在参数错位风险。
4. 非 admin 传 `project_id` 时，同样没有 `ai.project_id = %s` 条件，且 `params` 中的 `project_id` 会排在 `user_id` 前，可能被绑定到 `pm.user_id = %s`，导致查询错误或结果为空。

因此虽然字段名 `call_count` 已补齐，但 `project_id/date_from/date_to` 过滤未可靠生效。

### 2.5 非 admin 无 project_id 的成员贡献统计是否修复

**已修复。**

检查结果：

- admin 无 `project_id` 可查看全局成员贡献。
- admin 有 `project_id` 可查看指定项目成员贡献。
- 非 admin 有 `project_id` 时，service 层先调用 `check_user_can_access_project()` 校验权限，再返回该项目所有成员贡献。
- 非 admin 无 `project_id` 时，repository 使用当前用户参与的项目集合限制 `pm.project_id IN (...)`，返回这些项目范围内所有成员贡献，不再只返回当前用户本人。
- 返回字段包含 `user_id`、`real_name` 和贡献计数字段，未返回 `password_hash`、`email`、`phone`。

## 3. 是否发现新问题

发现 1 个与修复点直接相关的新问题：

- `get_model_call_stats()` 中 `sub_params = list(params)` 未被使用，`project_join` 也未被使用，说明当前过滤 SQL 仍存在未完成的修复痕迹。该问题已归入 2.4 的阻塞问题。

## 4. 是否发现越界修改

本轮静态审查未发现统计模块实现前端页面、数据库结构修改或 Stage-12 内容。

说明：

- 当前 `git status` 仍显示 `database/`、`docs/` 下存在未提交改动，但这些文件属于前序阶段长期存在的工作区改动；本轮 handoff 声明 Stage-11 Fix 仅修改 `backend/app/repositories/statistics_repo.py` 和 handoff 文件。
- 未发现 Stage-11 Fix 为修复本轮问题新增业务表或修改数据库脚本。

## 5. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/statistics.py app/services/statistics_service.py app/repositories/statistics_repo.py run.py
```

结果：通过，无语法错误。

说明：当前 Ubuntu / WSL 环境无法直接访问 Windows MySQL，本轮未执行真实数据库查询，仅进行静态审查和 Python 语法检查。

## 6. 是否允许进入 Stage-12

**不允许。**

原因：Stage-11 Fix 仍未完全修复项目统计字段和模型调用统计过滤问题。

## 7. 必须修复的问题

### P0-1：修复 `GET /api/statistics/projects?project_id=...` 返回字段

必须保证带 `project_id` 和不带 `project_id` 的项目统计接口都至少返回：

- `project_id`
- `project_name`
- `member_count`
- `task_count`
- `output_count`
- `approved_output_count`
- `artifact_count`
- `invocation_count`
- `total_cost`

建议：

- 要么让 `project_id` 场景复用 `list_project_stats(..., project_id=project_id)` 的同一套 SQL；
- 要么补齐 `get_project_stats_by_id()`，并统一字段别名。

### P0-2：修复 `GET /api/statistics/model-calls` 的 `project_id` 过滤

必须保证：

- `project_id` 传入时，统计范围严格限制为该项目内 `ai_invocations.project_id = %s`。
- `project_id + date_from/date_to` 同时传入时，参数顺序和 SQL 占位符一致。
- 非 admin 传 `project_id` 时，既要 service 层权限校验，也要 repository SQL 中限制 `ai.project_id = %s`。
- 不得通过“先查 model_id 再查模型全局视图”的方式返回跨项目聚合数据。
- 删除未使用的 `project_join`、`sub_params` 等残留变量，避免继续误导维护者。

## 8. Stage-12 发布情况

未发布 `TASK-012-backend-final-test.md`。
