# REVIEW-010-FIX 成果库与分支合并模块修复复审报告

## 1. 审查结论

**不通过。**

本轮只复审 `REVIEW-010-artifact-library.md` 中指出的 4 个阻塞问题。当前 3 个问题已修复，但分支状态更新的 affected_rows 检查仍未完全覆盖，因此暂不允许进入 Stage-11。

## 2. 4 个阻塞问题是否全部修复

**未全部修复。**

### 2.1 `is_user_admin()` 是否修复

结论：**已修复。**

- 不再查询不存在的 `users.roles`；
- 已改为 `users` + `user_roles` + `roles` 三表关联；
- 已过滤 `user_roles.is_deleted = 0`、`roles.is_deleted = 0`、`users.is_deleted = 0`；
- SQL 使用参数化查询；
- `artifact_repo.py` 中未发现 `users.roles` 或 `roles LIKE` 引用。

代码位置：`backend/app/repositories/artifact_repo.py:557-576`

备注：`artifact_repo.py:577` 有一行重复的不可达 `return cursor.fetchone() is not None`，不影响运行，但建议顺手清理。

### 2.2 `adopt_source` / `adopt_target` 是否强制要求 output_id

结论：**已修复。**

- `adopt_source` 已强制要求 `source_output_id`，缺失时抛出 `ValidationException`；
- `source_output_id` 会通过 `get_output_context()` 校验属于当前 task 且未删除；
- `adopt_target` 已强制要求 `target_output_id`，缺失时抛出 `ValidationException`；
- `target_output_id` 会通过 `get_output_context()` 校验属于当前 task 且未删除；
- `adopt_separately` 已要求 `source_output_id` / `target_output_id` 至少存在一个；
- 参数错误返回清晰错误，且错误发生在 `merge_records` 写入前。

代码位置：`backend/app/services/artifact_service.py:334-372`、`backend/app/services/artifact_service.py:395-407`

### 2.3 `manual_merge` 新建 `task_outputs` 字段是否完整

结论：**已修复。**

- 已写入 `branch_id`；
- `branch_id` 使用 `target_branch_id`，不为空；
- 已写入 `last_modified_at`；
- 已写入 `last_modified_by`；
- 已写入 `edit_summary`；
- 已写入 `lock_version = 0`；
- 已写入 `created_by`；
- 已写入 `source_type = manual_merge`；
- `version_no` 仍在事务内通过 `get_next_version_no()` 生成；
- `task_outputs` 插入与 `merge_records`、`task_branches`、`operation_logs` 在同一事务内。

代码位置：`backend/app/services/artifact_service.py:374-393`、`backend/app/repositories/artifact_repo.py:346-407`

### 2.4 分支状态更新 affected_rows 是否检查

结论：**未完全修复。**

已修复部分：

- `adopt_source` 更新 `source_branch` 后检查 affected_rows；
- `adopt_target` 更新 `target_branch` 后检查 affected_rows；
- `manual_merge` 更新 `source_branch` 后检查 affected_rows；
- `adopt_separately` 更新 `source_branch` 后检查 affected_rows。

剩余问题：

- `manual_merge` 中 `target_branch_id -> active` 仍直接调用 `artifact_repo.update_branch_status(target_branch_id, "active", conn)`，未接收返回值，也未检查 affected_rows。
- 代码位置：`backend/app/services/artifact_service.py:393`

这与本轮复审要求冲突：

> 如果 target_branch 有更新，是否也检查 affected_rows。

也与上一轮阻塞问题的修复要求冲突：

> 所有 `update_branch_status()` 调用必须检查 affected_rows；affected_rows == 0 必须 rollback。

虽然 `target_branch` 在事务前查询过，但本阶段要求的是写操作结果检查。当前仍存在 `target_branch` 状态未实际更新而 `merge_records` 和 `operation_logs` 提交的风险。

## 3. 是否发现新问题

未发现新的阻塞问题。

非阻塞建议：

- 清理 `artifact_repo.py:577` 重复不可达 return；
- 如需更稳妥，可为 `roles.status = 'active'` 增加过滤，但本轮验收重点未强制该项。

## 4. 是否发现越界修改

本轮窄口径复审未发现统计看板接口或前端页面实现。

说明：

- 远程 `git status` 仍显示 `database/*` 与 `docs/*` 为已修改状态，这与前序阶段历史脏工作区一致；
- 本轮 handoff 声明未修改 `database/*`、`frontend/*`、`docs/*`；
- 本轮未据此扩大为全量 Git 归因审查。

## 5. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/artifacts.py app/services/artifact_service.py app/repositories/artifact_repo.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准；
- 不因无法连接 MySQL 阻塞 Stage-10，但代码逻辑仍有明确未修复项，因此判定不通过。

## 6. 是否允许进入 Stage-11

**不允许。**

## 7. 必须修复的问题

只剩 1 个问题：

`manual_merge` 中 `target_branch_id -> active` 的更新必须检查 affected_rows。

建议修复方式：

```python
affected = artifact_repo.update_branch_status(target_branch_id, "active", conn)
if affected == 0:
    conn.rollback()
    raise NotFoundException(message="目标分支不存在或无权更新状态")
```

修复后请补充 handoff，说明所有 `update_branch_status()` 调用均已检查 affected_rows。

