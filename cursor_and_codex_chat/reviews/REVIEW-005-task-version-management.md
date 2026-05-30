# REVIEW-005 任务与版本管理模块审查报告

## 1. 审查结论

审查结论：需要继续修改。

Stage-05 已实现 11 个接口，整体分层、事务和权限框架基本符合任务方向，但存在会导致核心接口不可用或验收语义不正确的问题：

1. `GET /api/outputs/{output_id}` 使用了不存在的字段 `project_tasks.task_title`，会导致输出详情查询 SQL 执行失败；
2. `GET /api/outputs/{output_id}/timeline` 返回的是当前任务下所有根版本展开后的版本树，不是指定 `output_id` 的父版本链；
3. 版本时间线 SQL 写在 service 层，未集中在 `task_repo.py`；
4. 人工输出版本创建接口接收 `edit_summary`，但 service/repository 未保存该字段；
5. `version_no` 在事务外计算，不能保证并发创建时不重复。

因此本轮不允许进入 Stage-06，不发布 `TASK-006-prompt-template.md`。

## 2. Stage-05 是否遵守任务范围

结论：基本遵守。

检查结果：

- 已实现任务、分支、输出版本相关后端代码；
- 未发现 AI 调用实现；
- 未发现提示词模板实现；
- 未发现审核中心实现；
- 未发现成果库实现；
- 未发现前端页面实现；
- 本轮文件时间检查未发现 `database/`、`frontend/`、`docs/01_数据库Schema冻结说明.md` 被 Stage-05 修改；
- 未发现数据库表结构修改。

说明：`git status` 中仍显示 `database/` 与 `docs/01_数据库Schema冻结说明.md` 有历史未提交修改，但这些文件不是本轮 Stage-05 的新增修改。

## 3. 任务接口是否完整

结论：接口路径完整。

已实现：

- `GET /api/projects/{project_id}/tasks`
- `POST /api/projects/{project_id}/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/outputs`
- `GET /api/outputs/{output_id}`
- `GET /api/outputs/{output_id}/timeline`
- `POST /api/tasks/{task_id}/outputs/manual`

`backend/app/main.py` 已注册 `tasks.router`。

## 4. 创建任务和默认分支事务是否正确

结论：基本正确。

检查结果：

- 创建任务会插入 `project_tasks`；
- 会自动创建默认 `main` 分支；
- 会写入 `operation_logs`；
- `project_tasks`、`task_branches`、`operation_logs` 使用同一个 `get_db_transaction()` 事务；
- 返回结果包含 `task_id`，并在创建默认分支时包含 `default_branch_id`；
- 未发现物理删除。

风险：

- `task_type_id` 未在 service 层校验是否存在且启用，当前依赖外键错误；
- `assignee_id` 未校验是否存在、是否属于当前项目。

以上风险建议修复，但不是本轮最主要阻塞点。

## 5. 任务更新和软删除是否正确

结论：基本正确。

检查结果：

- `PUT /api/tasks/{task_id}` 仅允许更新 `title`、`description`、`assignee_id`、`status`、`priority`、`due_date`；
- status 值使用 Schema 中 `project_tasks.status` 允许值；
- UPDATE 返回 `rowcount`，service 检查 `affected == 0`；
- `DELETE /api/tasks/{task_id}` 使用软删除；
- 软删除设置 `is_deleted`、`deleted_at`、`deleted_by`；
- 未发现 `DELETE FROM`；
- 更新、删除均写入 `operation_logs`，且与业务写操作在同一事务。

风险：

- 更新 `assignee_id` 时同样未校验目标用户是否存在、是否属于当前项目。

## 6. 分支创建是否正确

结论：基本正确。

检查结果：

- 创建分支前校验当前用户有项目访问权限；
- 同一任务下检查 `branch_name` 重复；
- `base_output_id` 可为空；
- `base_output_id` 不为空时校验 output 属于当前 task；
- 写入 `task_branches`；
- 写入 `operation_logs`；
- 使用同一事务；
- 分支列表默认过滤 `task_branches.is_deleted = 0`。

## 7. 输出版本列表和详情是否正确

结论：输出列表基本正确，输出详情不通过。

列表检查结果：

- `GET /api/tasks/{task_id}/outputs` 会校验当前用户可访问该任务所属项目；
- 默认过滤 `task_outputs.is_deleted = 0`；
- 列表查询未返回完整 `content`；
- 未发现敏感信息返回。

详情阻塞问题：

- `task_repo.get_output_by_id()` 中 SELECT 使用 `t.task_title`；
- `project_tasks` 表字段为 `title`，不存在 `task_title`；
- 这会导致 `GET /api/outputs/{output_id}` SQL 执行失败；
- `get_output_timeline()` 和 `create_manual_output()` 后续也依赖 `get_output_by_id()`，因此会被同一字段错误影响。

必须修复为类似：

```sql
t.title AS task_title
```

## 8. 版本时间线是否正确

结论：不通过。

已满足部分：

- 使用了 `WITH RECURSIVE`；
- 返回字段包含 `output_id`、`parent_output_id`、`version_no`、`output_title`、`source_type`、`created_by`、`created_at`、`depth`；
- 查询前会通过目标 output 所属 task/project 做权限校验。

阻塞问题：

- 当前递归从 `parent_output_id IS NULL` 的所有根版本开始；
- 查询条件只限制 `task_id`，没有把递归链收敛到传入的 `output_id`；
- 因此当一个任务下存在多条独立版本链时，接口会返回整个任务的版本树，而不是“从最早父版本到当前 output”的版本链；
- 如果查询的是某个中间版本，当前实现还可能返回它的后代版本，不符合“当前版本时间线”语义；
- SQL 写在 `task_service.py` 中，违反“SQL 集中在 task_repo.py”的分层要求。

必须修复为：

- 在 repository 层新增时间线查询方法；
- 以目标 `output_id` 为起点递归向上查父版本，或等价地只返回目标 output 的祖先链；
- 返回顺序必须从最早父版本到当前版本；
- 必须保证不会返回同一任务下其他无关版本链。

## 9. 人工输出版本创建是否正确

结论：需要继续修改。

已满足部分：

- 会校验任务存在；
- 会校验当前用户可访问项目；
- `branch_id` 不为空时校验属于当前 task；
- `parent_output_id` 不为空时校验属于当前 task；
- `parent_output_id` 为空时使用 `manual_edit`；
- `parent_output_id` 不为空时使用 `hybrid`；
- `lock_version` 显式写入 0；
- `last_modified_by` 为当前用户；
- `last_modified_at` 为当前时间；
- 写入 `operation_logs`；
- `task_outputs` 插入与 `operation_logs` 插入在同一事务；
- 未实现编辑已有版本的乐观锁保存，符合本阶段边界。

阻塞/风险问题：

- router 请求体包含 `edit_summary`，但 `task_service.create_manual_output()` 未接收该参数；
- `task_repo.create_manual_output()` 固定写入 `edit_summary = NULL`，用户提交的编辑说明丢失；
- `get_next_version_no()` 在事务外读取 `MAX(version_no) + 1`，并发创建时存在重复版本号风险，不能满足“version_no 不会重复”的要求；
- 创建成功后调用 `get_output_by_id()` 返回详情，会被 `t.task_title` 字段错误影响。

## 10. operation_logs 是否写入

结论：基本符合要求。

以下操作均写入 `operation_logs`，且与业务操作使用同一事务：

- 创建任务；
- 更新任务；
- 软删除任务；
- 创建任务分支；
- 创建人工输出版本。

## 11. Repository 层和参数化 SQL 是否符合要求

结论：部分符合，需要修改。

符合点：

- 核心 SQL 大多集中在 `task_repo.py`；
- 未发现直接拼接用户输入到 SQL；
- 未使用 ORM；
- 查询基本默认过滤 `is_deleted = 0`；
- 多表写入基本由 service 层统一事务控制；
- UPDATE 操作检查了 affected_rows。

问题：

- 版本时间线递归 SQL 写在 `task_service.py`；
- `task_repo.get_output_by_id()` 使用不存在字段 `t.task_title`；
- `get_next_version_no()` 不在写入事务内执行，无法保证并发安全。

## 12. 是否发现越界实现

未发现越界实现。

检查结果：

- 未发现 AI 调用接口；
- 未发现提示词模板接口；
- 未发现审核中心接口；
- 未发现成果库接口；
- 未发现前端页面实现；
- 未发现 Stage-06 内容提前实现。

## 13. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py app/services/project_service.py app/repositories/project_repo.py
```

结果：通过。

说明：当前 Ubuntu/WSL 环境无法直接访问 Windows MySQL，未执行真实 SQL 和接口联调。本轮不因无法连接 MySQL 直接判失败，但 `t.task_title` 字段错误和时间线逻辑错误可通过静态审查确认。

## 14. 是否允许进入 Stage-06

不允许。

原因：输出版本详情和版本时间线属于 Stage-05 核心验收功能，目前存在明确阻塞问题。

## 15. 必须修复的问题

Cursor 必须逐条修复：

1. 修复 `task_repo.get_output_by_id()` 中不存在的 `t.task_title` 字段，改为 `t.title AS task_title`；
2. 修复 `get_output_timeline()`，只返回目标 `output_id` 的父版本链，不能返回整个任务的版本树；
3. 将版本时间线 SQL 从 `task_service.py` 移到 `task_repo.py`；
4. 保存人工输出版本创建请求中的 `edit_summary`；
5. 将 `version_no` 生成纳入创建输出版本的事务，并采取可避免重复的方案；
6. 修复后重新执行 Python 语法检查，并在 handoff 中说明无法连接 MySQL 时的静态验证结果。

## 16. 后续动作

- 不发布 `TASK-006-prompt-template.md`；
- 创建 `TASK-005-FIX-task-version-management.md`，要求 Cursor 修复以上问题后再复审。
