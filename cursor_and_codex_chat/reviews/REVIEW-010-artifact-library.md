# REVIEW-010 成果库与分支合并模块审查报告

## 1. 审查结论

**不通过。**

Stage-10 已实现成果库路由、Service、Repository，并通过 Python 语法检查；但存在会导致接口运行失败和事务一致性不满足的阻塞问题，暂不允许进入 Stage-11。

## 2. Stage-10 是否遵守任务范围

基本遵守。

- 已实现 `backend/app/routers/artifacts.py`、`backend/app/services/artifact_service.py`、`backend/app/repositories/artifact_repo.py` 并在 `main.py` 注册；
- 未发现前端页面实现；
- 未发现统计看板路由注册；
- 远程已有 `statistics` 相关空文件，但内容为 0 行，未作为 Stage-11 实质实现处理；
- `git status` 显示 `database/*` 和 `docs/01_数据库Schema冻结说明.md` 仍处于已修改状态，这更像前序阶段遗留脏工作区；本轮审查未发现 Stage-10 artifacts 代码依赖数据库结构变更。

## 3. 采用成果接口是否正确

**部分正确，但存在阻塞。**

已实现 `POST /api/outputs/{output_id}/adopt`，包含：

- output 存在性校验；
- 项目访问权限校验；
- admin / leader / teacher 采用权限；
- output 状态必须为 `approved`；
- 重复采用校验；
- `adopted_outputs` 插入；
- `task_outputs.status = adopted` 更新；
- `project_tasks.status = adopted` 更新；
- `operation_logs` 写入；
- 同一事务提交。

阻塞问题：

`artifact_repo.is_user_admin()` 查询了不存在的 `users.roles` 字段：

- `backend/app/repositories/artifact_repo.py:535-543`
- Schema 冻结文档和 `database/02_create_tables.sql` 中 `users` 表没有 `roles` 字段；
- `_can_access_project()` 与 `_can_adopt_or_merge()` 都会调用该函数；
- 结果是成果采用、分支合并以及非 admin 成果查询在真实 MySQL 中会触发 `Unknown column 'roles'`，接口无法可靠运行。

应改为通过 `user_roles` + `roles.role_code = 'admin'` 判断管理员，或复用已验证的认证/用户权限工具。

## 4. 成果列表和详情是否正确

**部分正确。**

已实现：

- `GET /api/projects/{project_id}/artifacts`
- `GET /api/artifacts/{adopted_id}`
- 默认过滤 `adopted_outputs.is_deleted = 0`
- 支持 `artifact_type`、`keyword`、`page`、`page_size`
- 列表不返回完整 content
- 详情返回完整 output content
- 未返回 `password_hash`、API Key 或密钥字段。

阻塞关联问题：

- 非 admin 用户访问成果列表和成果详情时会走 `_can_access_project()`，最终触发不存在的 `users.roles` 查询。

## 5. 分支合并接口是否正确

**不通过。**

已实现 `POST /api/tasks/{task_id}/branches/merge`，并校验：

- task 存在；
- source / target branch 属于当前 task；
- source / target output 如传入则属于当前 task；
- `merge_strategy` 白名单；
- admin / leader / teacher 权限。

阻塞问题：

1. `adopt_source` 未强制要求 `source_output_id`，如果为空会直接跳过 output 状态更新，仍写入 `merge_records` 并返回 success。
2. `adopt_target` 未强制要求 `target_output_id`，如果为空同样可能空合并成功。
3. `manual_merge` 和 `adopt_separately` 调用 `update_branch_status()` 后没有检查 `affected_rows`：
   - `backend/app/services/artifact_service.py:362-366`
   - 可能出现分支状态未更新但 `merge_records` 和 `operation_logs` 已提交。
4. `adopt_source` / `adopt_target` 未更新任何 `task_branches` 状态，不满足本阶段对 `task_branches` 状态更新和合并闭环的要求。

## 6. 四种 merge_strategy 是否正确处理

**未全部正确。**

- `adopt_source`：未要求 `source_output_id` 必填；缺少分支状态处理；
- `adopt_target`：未要求 `target_output_id` 必填；缺少分支状态处理；
- `manual_merge`：会创建新 `task_outputs`，但新版本字段不完整；
- `adopt_separately`：会更新 source_branch，但未检查 affected_rows，且分支状态规则过弱。

`manual_merge` 新建输出的问题：

- `backend/app/repositories/artifact_repo.py:363-384`
- 插入 `task_outputs` 时没有写 `branch_id`；
- 没有写 `last_modified_at`；
- 没有写 `last_modified_by`；
- 没有写 `edit_summary`；
- 不满足本阶段对人工合并输出版本的可追溯要求。

## 7. adopted_outputs 和 merge_records 是否正确写入

**部分正确。**

- `adopted_outputs` 插入使用参数化 SQL，并返回 `cursor.lastrowid`；
- `merge_records` 插入使用参数化 SQL，并返回 `cursor.lastrowid`；
- 但分支合并存在空 output 也可成功写 `merge_records` 的问题，导致合并记录可能不可信。

## 8. task_outputs、project_tasks、task_branches 状态更新是否正确

**不通过。**

- 成果采用会检查 `task_outputs` 与 `project_tasks` 的 affected_rows；
- 分支合并中的 `task_branches` 更新没有检查 affected_rows；
- `adopt_source` / `adopt_target` 没有更新分支状态；
- `manual_merge` 新建 output 缺少 `last_modified_*` 等关键版本字段。

## 9. operation_logs 是否写入

**已写入。**

成果采用和分支合并均调用 `user_repo.insert_operation_log_with_conn()`，与业务写操作处于同一事务中。

## 10. Repository 层和参数化 SQL 是否符合要求

**基本符合，但管理员判断 SQL 不符合 Schema。**

- 成果库 SQL 集中在 `artifact_repo.py`；
- 未发现 service 层直接写业务 SQL；
- 未发现拼接用户输入；
- 未使用 ORM；
- 但 `users.roles` 是 Schema 中不存在的字段，必须修复。

## 11. 事务一致性是否符合要求

**不通过。**

采用成果事务结构较完整。

分支合并事务存在风险：

- `update_branch_status()` 不检查 affected_rows；
- `adopt_source` / `adopt_target` 缺少必需 output 时仍可能提交；
- `task_branches` 状态更新失败时不会 rollback。

## 12. 权限控制是否符合要求

**不通过。**

设计意图正确：admin、项目 leader、项目 teacher 可采用和合并；普通 member / reviewer 不可采用或合并。

但管理员判断使用不存在的 `users.roles` 字段，导致权限控制在真实数据库中不可运行。权限判断必须基于 `roles`、`user_roles`，或复用已有 token 中解析出的角色信息和项目成员角色判断。

## 13. 是否发现越界实现

未发现 Stage-11 统计看板的实质实现；未发现前端页面实现。

说明：工作区存在历史脏文件，包含 `database/*` 与 `docs/01_数据库Schema冻结说明.md` 的修改状态。本轮未将其作为 Stage-10 新增越界代码处理，但 Cursor 后续 handoff 需要继续明确未改数据库和 Schema 文档。

## 14. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/artifacts.py app/services/artifact_service.py app/repositories/artifact_repo.py run.py app/services/task_service.py app/repositories/task_repo.py app/services/review_service.py app/repositories/review_repo.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准；
- 不因无法连接 MySQL 阻塞，但 Schema 字段错误属于静态可确认问题。

## 15. 是否允许进入 Stage-11

**不允许。**

## 16. 必须修复的问题

1. 修复 `artifact_repo.is_user_admin()`：
   - 禁止查询不存在的 `users.roles`；
   - 改为通过 `user_roles` + `roles.role_code = 'admin'` 判断，或复用已有认证/用户权限工具；
   - 确保成果采用、成果列表、成果详情、分支合并在普通项目成员和 admin 场景下都不会 SQL 报错。

2. 修复 `adopt_source` / `adopt_target`：
   - `adopt_source` 必须要求合法 `source_output_id`；
   - `adopt_target` 必须要求合法 `target_output_id`；
   - 缺失时返回参数错误，不能写入空合并记录并返回 success；
   - 合理更新相关 `task_branches.status` 并检查 affected_rows。

3. 修复 `manual_merge` 新建 `task_outputs`：
   - 写入合法 `branch_id`；
   - 写入 `last_modified_at`；
   - 写入 `last_modified_by`；
   - 写入 `edit_summary`；
   - 保持 `source_type = manual_merge`；
   - `version_no` 仍需在事务内生成。

4. 修复分支状态更新事务一致性：
   - 所有 `update_branch_status()` 调用必须检查 affected_rows；
   - affected_rows == 0 必须 rollback；
   - 不允许 `merge_records` 成功但分支状态未更新。

5. 修复完成后创建 `cursor_and_codex_chat/handoff/HANDOFF-010-FIX-artifact-library.md`，说明修复点、测试命令和未越界承诺。

