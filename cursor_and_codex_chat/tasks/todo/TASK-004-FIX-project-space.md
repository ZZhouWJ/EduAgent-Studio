# TASK-004-FIX：Stage-04 项目空间管理模块修复

## 任务状态

待 Cursor 领取。

## 任务背景

Codex 对 Stage-04 项目空间管理模块审查后，结论为：需要继续修改。

本修复任务只允许围绕 Stage-04 项目空间管理模块修复审查问题，不得进入 Stage-05，不得实现任务管理、AI 调用、提示词模板、审核中心、成果库或前端页面。

## 允许修改文件

只允许修改：

- `backend/app/routers/projects.py`
- `backend/app/services/project_service.py`
- `backend/app/repositories/project_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-004-FIX-project-space.md`

如确实需要复用事务或日志工具，可少量修改：

- `backend/app/database.py`
- `backend/app/repositories/user_repo.py`

但必须在 handoff 中说明理由、修改范围和对既有接口的影响。

## 禁止修改文件

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现内容

本修复任务禁止实现：

1. 任务管理；
2. AI 调用；
3. 提示词模板；
4. 审核中心；
5. 成果库；
6. 前端页面；
7. 任何 Stage-05 或后续阶段接口。

## 必须修复的问题

### 1. 修复项目创建返回值

`backend/app/repositories/project_repo.py` 中 `create_project()` 必须返回新建 `project_id`。

当前问题：

- Repository 中拿到了 `cursor.lastrowid`；
- 但函数没有 `return project_id`；
- Service 层得到 `None`，导致日志和接口返回错误。

修复要求：

- `POST /api/projects` 必须返回真实项目详情；
- `operation_logs.target_id` 和 `operation_logs.project_id` 必须是新建项目 ID；
- 创建人必须自动写入 `project_members`，`project_role='leader'`。

### 2. 修复关键操作事务一致性

以下操作必须保证业务写入和 `operation_logs` 写入在同一事务中：

- 创建项目；
- 更新项目；
- 软删除项目；
- 添加成员；
- 修改成员角色；
- 移除成员；
- 项目归档。

修复建议：

- 在 `project_repo.py` 中实现完整事务函数；
- 或扩展可复用事务上下文，允许业务 SQL 和日志 SQL 共用同一个 cursor/connection；
- 不要在业务 UPDATE 已提交后再另开事务写日志。

### 3. 修复项目归档逻辑

必须优先调用 Stage-01 已定义的存储过程：

```sql
CALL sp_archive_project(...)
```

注意 `sp_archive_project` 定义了 OUT 参数：

- `p_result_code`
- `p_result_message`

修复要求：

- 正确处理存储过程返回码；
- 成功后项目 status 应为 `archived`；
- 存储过程会同时归档项目任务、关闭任务分支、写入 operation_logs；
- 不要再额外重复写一条语义冲突的归档日志。

如果确实不能调用存储过程，必须在 `project_repo.py` 中用单个事务完整模拟存储过程行为：

1. 更新 `projects.status='archived'`；
2. 更新 `project_tasks.status='archived'`；
3. 更新 `task_branches.status='closed'`；
4. 写入 `operation_logs`；
5. 所有步骤同一事务提交或回滚；
6. 在 handoff 中说明为什么不调用存储过程。

仅更新 `projects.status` 不合格。

### 4. 修复 teacher 项目列表权限

本阶段要求：

teacher 只能查看自己作为 `project_members.project_role='teacher'` 参与的项目。

当前问题：

- 代码只判断用户是否拥有系统角色 `teacher`；
- 然后返回该用户参与的所有项目；
- 没有限制项目内角色必须为 `teacher`。

修复要求：

- teacher 分支应加上 `pm.project_role = 'teacher'`；
- 普通成员和项目负责人仍只能查看自己参与的项目；
- admin 仍可查看全部项目。

### 5. 检查 UPDATE 返回值

以下操作必须检查 repository 返回值：

- `update_project`
- `soft_delete_project`
- `archive_project`
- `update_project_member_role`
- `soft_delete_project_member`

如果影响行数为 0，不得写成功日志，也不得返回成功响应，应返回资源不存在、状态不允许操作或数据库事务失败等统一错误。

### 6. 修复错误处理细节

请修复：

- 未登录场景建议使用 `UnauthorizedException`，错误码应为 4002；
- 删除或不要使用 `projects.py` 中会把任意 `str(e)` 返回前端的 `_handle_service()`；
- 请求体参数不要写成 `body: Model = None` 后再直接访问属性，缺少 body 时应返回参数错误而不是 `NoneType` 系统错误。

## 验收清单

Cursor 完成修复后，请确认：

1. `POST /api/projects` 返回真实新建项目详情；
2. 创建项目同时写入 `project_members.project_role='leader'`；
3. 创建项目日志中的 `project_id` 和 `target_id` 不为 `None`；
4. 关键写操作与 `operation_logs` 同一事务；
5. 归档优先调用 `sp_archive_project`，或完整事务模拟存储过程行为；
6. teacher 只能查看自己作为 `project_role='teacher'` 的项目；
7. 所有软删除仍为 UPDATE，不出现物理 DELETE；
8. 所有 SQL 仍使用参数化查询；
9. 不返回 `password_hash`；
10. 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
11. 未实现任务管理、AI 调用、提示词模板、审核中心、成果库或前端页面；
12. `python3 -m py_compile app/main.py app/routers/projects.py app/services/project_service.py app/repositories/project_repo.py run.py` 通过。

## 交付要求

完成后请创建：

`cursor_and_codex_chat/handoff/HANDOFF-004-FIX-project-space.md`

handoff 必须说明：

1. 修复了哪些文件；
2. `project_id` 返回问题如何修复；
3. 哪些操作现在使用同一事务；
4. 项目归档是否调用 `sp_archive_project`；
5. teacher 权限过滤如何修复；
6. 如何验证 UPDATE 返回值；
7. 已执行的静态检查命令；
8. 是否仍遵守 Stage-04 范围。
