# REVIEW-004-FIX 项目空间管理模块复审报告

## 1. 审查结论

审查结论：需要继续修改。

Stage-04 Fix 已修复 5 个阻塞问题中的 4 个，剩余 1 个阻塞点：

- 项目归档虽然已改为调用 `sp_archive_project`，但 `archive_project_with_procedure()` 未按 PyMySQL/MySQL OUT 参数机制读取 `p_result_code`、`p_result_message`，当前实现可能在存储过程返回 404/500 时仍默认当作成功处理。

因此本轮不允许进入 Stage-05，暂不发布 `TASK-005-task-version-management.md`。

## 2. 5 个阻塞问题修复情况

### 2.1 create_project 是否返回 project_id

结论：已修复。

检查结果：

- `backend/app/repositories/project_repo.py` 中 `create_project()` 使用 `cursor.lastrowid` 获取新建项目 ID；
- `create_project()` 返回 `project_id`；
- `backend/app/services/project_service.py` 使用该 `project_id` 写入 `operation_logs`；
- `project_repo.create_project()` 内部已使用同一连接写入 `projects` 与创建人 `project_members`；
- `POST /api/projects` 最终通过 `_project_row_to_dict()` 返回包含 `project_id` 的项目数据；
- 未发现返回 `None` 的问题。

### 2.2 关键写操作和 operation_logs 是否在同一事务

结论：已修复。

检查结果：

- `backend/app/database.py` 新增 `get_db_transaction()`；
- `project_service.create_project()`、`update_project()`、`delete_project()`、`add_project_member()`、`update_project_member_role()`、`remove_project_member()` 均在 service 层打开事务；
- 业务写操作和 `user_repo.insert_operation_log_with_conn()` 使用同一个 `conn`；
- repository 方法在外部传入 `conn` 时不提前 `commit`；
- service 层负责 `conn.commit()`；
- 异常时由 `get_db_transaction()` 统一 `rollback`，连接在 finally 中关闭。

### 2.3 项目归档是否正确

结论：未完全修复，仍为阻塞问题。

已修复部分：

- `archive_project()` 已优先调用 `project_repo.archive_project_with_procedure()`；
- 调用的存储过程名称为 `sp_archive_project`；
- 调用参数数量与 `database/06_create_stored_procedures.sql` 中定义的 4 个参数一致；
- 数据库中的 `sp_archive_project` 确实会更新 `projects.status = 'archived'`、`project_tasks.status = 'archived'`、`task_branches.status = 'closed'` 并写入 `operation_logs`；
- 未发现物理删除。

剩余阻塞问题：

- `database/06_create_stored_procedures.sql` 中 `sp_archive_project` 使用 OUT 参数 `p_result_code`、`p_result_message`，但过程末尾没有 `SELECT p_result_code, p_result_message`；
- `project_repo.archive_project_with_procedure()` 当前在 `cursor.callproc("sp_archive_project", (project_id, operator_id, 0, ""))` 后直接 `cursor.fetchall()`，这通常不能读取 MySQL/PyMySQL 的 OUT 参数；
- 当 `fetchall()` 为空时，代码默认 `result_code = 0`、`result_message = ""`，可能把存储过程设置的 404/500 误判为成功；
- `archive_project_fallback()` 的注释写明会写入 `operation_logs`，但实际未插入 `operation_logs`。虽然当前 service 没有调用 fallback，但该回退方法若后续启用会不满足归档要求。

修复建议：

- 使用 MySQL/PyMySQL 正确的 OUT 参数读取方式，例如 `CALL sp_archive_project(%s, %s, @result_code, @result_message)` 后再执行 `SELECT @result_code AS result_code, @result_message AS result_message`；
- 或在存储过程末尾显式 `SELECT p_result_code AS result_code, p_result_message AS result_message`，但这会修改 `database/`，本轮不建议由 Codex 直接改数据库脚本；
- 不要在 `fetchall()` 为空时默认成功，应视为无法确认归档结果并返回错误；
- 若保留 `archive_project_fallback()`，需补齐 `operation_logs` 写入，或删除/明确标记为未使用。

### 2.4 teacher 项目列表权限是否正确

结论：已修复。

检查结果：

- 非 admin 且拥有 teacher 系统角色时，项目列表通过 `project_members` 子查询限制；
- 子查询包含 `pm.user_id = 当前用户 ID`；
- 子查询包含 `pm.project_role = 'teacher'`；
- 子查询包含 `pm.is_deleted = 0`；
- 外层查询包含 `p.is_deleted = 0`；
- admin 分支仍可查看全部未删除项目；
- 普通成员分支仍限制为自己参与的项目。

### 2.5 UPDATE affected_rows 是否检查

结论：基本已修复，但归档结果判断仍受 2.3 阻塞问题影响。

检查结果：

- `update_project()` repository 返回 `cursor.rowcount`，service 检查 `affected == 0`；
- `soft_delete_project()` repository 返回 `cursor.rowcount`，service 检查 `affected == 0`；
- `update_project_member_role()` repository 返回 `cursor.rowcount`，service 检查 `affected == 0`；
- `soft_delete_project_member()` repository 返回 `cursor.rowcount`，service 检查 `affected == 0`；
- 项目归档使用存储过程，未直接通过 UPDATE 模拟 affected_rows，但存储过程 OUT 参数读取不可靠，导致 service 层不能可靠判断归档失败。

## 3. 是否发现新问题

发现 2 个与归档相关的新问题：

1. `archive_project_with_procedure()` 的返回类型注解为 `Tuple[int, int, str]`，实际返回 `(result_code, result_message, 1)`，第二项是字符串，第三项是整数，类型注解与实际返回顺序不一致。
2. `archive_project_fallback()` 注释称会写入 `operation_logs`，实际没有写入。当前未被 service 调用，但建议修复以免后续误用。

以上新问题中，第 1 个是代码质量问题，第 2 个是潜在业务一致性问题。真正阻塞 Stage-05 的问题仍是归档存储过程 OUT 参数读取不可靠。

## 4. 是否发现越界修改

未发现越界修改。

检查结果：

- 未发现本轮修改 `database/`；
- 未发现本轮修改 `frontend/`；
- 未发现本轮修改 `docs/01_数据库Schema冻结说明.md`；
- 未发现实现任务管理；
- 未发现实现 AI 调用；
- 未发现实现提示词模板；
- 未发现实现审核中心；
- 未发现实现成果库；
- 未发现物理 `DELETE FROM`。

## 5. 语法检查结果

已在远程环境执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/projects.py app/services/project_service.py app/repositories/project_repo.py app/database.py app/repositories/user_repo.py run.py
```

结果：通过。

说明：当前 Ubuntu/WSL 环境仍无法直接连接 Windows MySQL，本轮未做真实接口和数据库联调，不因此阻塞复审结论。

## 6. 是否允许进入 Stage-05

不允许。

原因：项目归档是 Stage-04 明确要求的核心接口，当前实现无法可靠读取 `sp_archive_project` 的 OUT 参数，可能出现归档失败却返回成功的情况。

## 7. 必须修复的问题

Cursor 需要继续修复以下问题：

1. 修复 `backend/app/repositories/project_repo.py` 中 `archive_project_with_procedure()` 的 OUT 参数读取逻辑；
2. 不得在无法读取存储过程返回值时默认成功；
3. 确保 `backend/app/services/project_service.py` 能根据真实 `result_code` 返回成功、404 或错误；
4. 修正 `archive_project_with_procedure()` 返回类型注解与实际返回值顺序；
5. 如保留 `archive_project_fallback()`，补齐 `operation_logs` 写入，或在 handoff 中明确该方法未启用且不得作为满足验收的依据。

## 8. 后续动作

- 不发布 `TASK-005-task-version-management.md`；
- 创建 `TASK-004-FIX-R2-project-space.md`，要求 Cursor 修复归档存储过程 OUT 参数读取问题后再复审。
