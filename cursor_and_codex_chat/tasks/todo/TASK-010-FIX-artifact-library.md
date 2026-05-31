# TASK-010-FIX：修复成果库与分支合并模块审查问题

## 任务状态

已完成。

## 一、任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-010-artifact-library.md` 修复 Stage-10 阻塞问题，使成果采用、成果查询和分支合并在冻结 Schema 下可运行，并保证分支合并事务一致性。

## 二、允许修改文件

- `backend/app/repositories/artifact_repo.py`
- `backend/app/services/artifact_service.py`
- `backend/app/routers/artifacts.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-010-FIX-artifact-library.md`

如确实需要复用已有权限工具，可少量修改：

- `backend/app/repositories/user_repo.py`
- `backend/app/services/auth_service.py`

但必须在 handoff 中说明理由。

## 三、禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 四、禁止实现

1. 统计看板；
2. 前端页面；
3. 数据库结构修改；
4. Stage-11 内容。

## 五、必须修复的问题

### 1. 修复 admin 判断 SQL

`artifact_repo.is_user_admin()` 不得查询 `users.roles`。

必须改为基于冻结 Schema 的表关系：

- `users`
- `user_roles`
- `roles`

建议判断条件：

- `users.user_id = 当前用户`
- `users.is_deleted = 0`
- `user_roles.is_deleted = 0`
- `roles.is_deleted = 0`
- `roles.status = 'active'`
- `roles.role_code = 'admin'`

修复后成果采用、成果列表、成果详情、分支合并均不得因为 `users.roles` 报错。

### 2. 修复 adopt_source / adopt_target

- `adopt_source` 必须要求 `source_output_id`；
- `adopt_target` 必须要求 `target_output_id`；
- 缺失时返回清晰参数错误；
- 不允许空输出也写入 `merge_records` 并返回 success；
- 合理更新相关 `task_branches.status`；
- 所有状态更新必须检查 affected_rows。

### 3. 修复 manual_merge 新建输出版本

新建 `task_outputs` 时必须补齐：

- `branch_id`
- `last_modified_at`
- `last_modified_by`
- `edit_summary`

并保持：

- `source_type = manual_merge`
- `lock_version` 合理默认值；
- `created_by = 当前用户`
- `version_no` 在事务内生成。

### 4. 修复分支状态更新事务一致性

- 所有 `update_branch_status()` 调用必须接收并检查 affected_rows；
- affected_rows == 0 必须 rollback；
- 不允许 `merge_records` 写入成功但分支状态未更新；
- 不允许 `operation_logs` 失败但业务仍提交。

## 六、验收命令

至少执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/artifacts.py app/services/artifact_service.py app/repositories/artifact_repo.py run.py
```

如修改了用户或认证相关复用文件，还需执行：

```bash
python3 -m py_compile app/repositories/user_repo.py app/services/auth_service.py
```

## 七、完成后 handoff

完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-010-FIX-artifact-library.md`

handoff 必须说明：

1. 每个阻塞问题如何修复；
2. 是否仍查询 `users.roles`；
3. 四种 `merge_strategy` 的最终行为；
4. 分支状态 affected_rows 检查情况；
5. `manual_merge` 新建 output 字段写入情况；
6. Python 语法检查结果；
7. 是否未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
8. 是否未实现统计看板或前端页面。

