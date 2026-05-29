# REVIEW-004：Stage-04 项目空间管理模块审查

## 1. 审查结论

结论：需要继续修改。

是否允许进入 Stage-05：暂不允许。

Stage-04 已实现 10 个项目与成员接口，并注册到 `backend/app/main.py`。整体分层基本符合 Router / Service / Repository 模式，项目查询、成员查询、软删除等大部分 SQL 使用参数化查询，未发现物理 DELETE。

但本轮发现多个阻塞问题，其中 `project_repo.create_project()` 未返回 `project_id` 会直接导致项目创建接口返回错误数据并写入错误日志；关键写操作与 `operation_logs` 没有放在同一事务；项目归档未使用 Stage-01 已定义的 `sp_archive_project`，且当前直接 UPDATE 会漏掉任务归档、分支关闭和存储过程内部日志。

因此本轮不发布 Stage-05，已发布修复任务：

`cursor_and_codex_chat/tasks/todo/TASK-004-FIX-project-space.md`

## 2. Stage-04 范围审查

| 检查项 | 结论 |
|---|---|
| 是否只实现项目空间管理模块 | 基本通过 |
| 是否没有实现任务管理 | 通过，`main.py` 未注册 tasks 路由 |
| 是否没有实现 AI 调用 | 通过，`main.py` 未注册 invocations 路由 |
| 是否没有实现提示词模板 | 通过，`main.py` 未注册 prompts 路由 |
| 是否没有实现审核中心 | 通过，`main.py` 未注册 reviews 路由 |
| 是否没有实现成果库 | 通过，`main.py` 未注册 artifacts 路由 |
| 是否没有修改 frontend/ | 通过，未发现 Stage-04 期间前端文件更新 |
| 是否没有修改 database/ | 通过，未发现 Stage-04 期间数据库文件更新 |
| 是否没有修改 docs/01_数据库Schema冻结说明.md | 通过，未发现 Stage-04 期间 Schema 文档更新 |
| 是否没有修改数据库表结构 | 通过，本阶段未改表结构 |

说明：仓库中存在历史未提交改动，因此本轮主要根据任务发布时间后的文件时间、main.py 注册路由、handoff 和审查对象判断 Stage-04 范围。

## 3. 项目接口是否完整

| 接口 | 结论 |
|---|---|
| `GET /api/projects` | 已实现 |
| `POST /api/projects` | 已实现，但创建流程存在阻塞 bug |
| `GET /api/projects/{project_id}` | 已实现 |
| `PUT /api/projects/{project_id}` | 已实现 |
| `DELETE /api/projects/{project_id}` | 已实现 |
| `GET /api/projects/{project_id}/members` | 已实现 |
| `POST /api/projects/{project_id}/members` | 已实现 |
| `PUT /api/projects/{project_id}/members/{member_id}` | 已实现 |
| `DELETE /api/projects/{project_id}/members/{member_id}` | 已实现 |
| `POST /api/projects/{project_id}/archive` | 已实现，但归档逻辑不符合要求 |

## 4. 项目列表权限是否正确

通过项：

- admin 分支不加成员过滤，可查看全部未删除项目；
- 普通用户分支通过 `project_members.user_id` 限制只能查看自己参与的项目；
- 查询默认过滤 `projects.is_deleted = 0`；
- 支持 `page`、`page_size`、`keyword`、`status`；
- 返回统一分页结构。

需要修复：

- `project_repo.py:87-103` 的 teacher 分支只判断用户是否拥有系统角色 `teacher`，然后返回该用户参与的所有项目；没有限制 `project_members.project_role = 'teacher'`。用户本轮要求是“teacher 是否只能查看自己作为 teacher 参与的项目”，当前如果教师账号在某项目中只是 `member`，仍会看到该项目。

## 5. 项目创建事务是否正确

不通过。

阻塞问题：

1. `backend/app/repositories/project_repo.py:151-200` 中 `create_project()` 在同一事务里插入 `projects` 和 `project_members`，但函数末尾没有 `return project_id`。因此 `project_service.py:136` 得到的 `project_id` 是 `None`。
2. 由于 `project_id` 为 `None`，`project_service.py:144-153` 会向 `operation_logs` 写入 `target_id=None`、`project_id=None`，随后 `project_service.py:155` 用 `None` 查询项目，接口最终可能返回 `{}`，无法满足“项目创建成功后返回项目详情”的要求。
3. `operation_logs` 写入不在项目创建事务内。`project_repo.create_project()` 的事务提交后，`user_repo.insert_operation_log()` 才另开连接写日志；如果日志写入失败，项目和成员已提交，接口却可能报错，破坏关键操作的一致性。

必须修复：

- `project_repo.create_project()` 必须返回新建 `project_id`；
- 创建项目、自动写入 leader 成员、写入 `operation_logs` 必须放在同一事务内，或提供明确的单个 repository 事务函数完成三者。

## 6. 项目成员管理是否正确

通过项：

- 成员列表默认过滤 `project_members.is_deleted = 0`；
- 成员列表不返回 `password_hash`；
- 添加成员前校验项目存在、操作者权限、角色枚举、目标用户存在、未删除成员重复；
- `project_role` 限制为 `member / leader / reviewer / teacher`；
- 修改成员角色时禁止把项目 owner 改成非 leader；
- 移除成员时禁止移除项目 owner；
- 移除成员使用软删除。

需要修复：

- 添加成员、修改成员角色、移除成员的业务写入和 `operation_logs` 写入分别在不同事务中执行，不满足关键操作事务一致性要求。
- `project_repo.update_project_member_role()` 和 `project_repo.soft_delete_project_member()` 只按 `member_id` 更新，虽然 service 先查了 `project_id`，但更稳妥的做法是在 UPDATE 条件中同时带上 `project_id`，防止后续调用方误用。

## 7. 项目软删除是否正确

部分通过。

通过项：

- `DELETE /api/projects/{project_id}` 使用 `UPDATE projects SET is_deleted = 1, deleted_at = ..., deleted_by = ...`；
- 未发现物理 `DELETE FROM`；
- 未级联删除其他表。

需要修复：

- 软删除项目与写入 `operation_logs` 不在同一事务中执行，不满足关键操作事务一致性要求。
- `project_service.delete_project()` 没有检查 `project_repo.soft_delete_project()` 的返回值；如果 UPDATE 未影响行数，仍会继续写日志并返回成功。

## 8. 项目归档是否正确

不通过。

Stage-01 已定义 `sp_archive_project`，该存储过程会在事务中：

1. 更新 `projects.status = 'archived'`；
2. 将项目下 `project_tasks.status` 置为 `archived`；
3. 将项目下 `task_branches.status` 置为 `closed`；
4. 写入 `operation_logs`；
5. 返回结果码和结果消息。

当前 `backend/app/repositories/project_repo.py:274-293` 只执行：

```sql
UPDATE projects SET status = 'archived' ...
```

问题：

- 未优先调用 `sp_archive_project`；
- 未归档项目任务；
- 未关闭任务分支；
- 未使用存储过程中的完整事务；
- Service 层又单独写了一条 `operation_logs`，仍不在同一事务；
- 这与“项目一键归档接口”的数据库高级特性和任务要求不一致。

必须修复：

- 优先调用 `CALL sp_archive_project(...)`，正确处理 OUT 参数；
- 如果确实不能调用存储过程，必须在 repository 中用单个事务完整模拟存储过程行为，包括项目、任务、分支、日志，并在 handoff 中说明原因。但当前仅更新项目状态不够。

## 9. 操作日志是否写入

部分通过。

已覆盖：

- 创建项目；
- 更新项目；
- 删除项目；
- 归档项目；
- 添加成员；
- 修改成员角色；
- 移除成员。

阻塞问题：

- 日志写入均通过 `user_repo.insert_operation_log()` 在业务写入之后另开事务执行，未和关键业务写入保持同一事务一致性。
- 创建项目因为 `project_id` 未返回，日志目标 ID 会是 `None`。

## 10. Repository 层和参数化 SQL 是否符合要求

部分通过。

通过项：

- 核心 SQL 集中在 `project_repo.py`；
- 未使用 ORM；
- 未发现直接拼接用户输入到 SQL；
- `keyword` 被构造成 `%keyword%` 后仍作为参数传入，不属于 SQL 注入拼接；
- 普通查询大多默认过滤 `is_deleted = 0`；
- 未发现物理删除。

需要修复或说明：

- `project_repo.py:118-134` 和 `project_repo.py:245` 使用 f-string 组装 SQL 片段。当前字段和 where 片段来自白名单/内部逻辑，风险可控，但修复时应保持字段白名单，不得引入用户输入拼接。
- 缺少可复用事务接口，导致 Service 层跨多个 repository 调用时无法原子提交。

## 11. 统一返回和错误处理

部分通过。

通过项：

- 成功响应使用 `success_response()`；
- `ForbiddenException`、`NotFoundException`、`ValidationException` 由全局异常处理转换为统一错误结构；
- 未发现原始堆栈直接暴露。

需要修复：

- `_require_auth()` 当前用 `ForbiddenException(message="未登录或登录已过期")` 表达未登录，错误码会是 4001；按接口契约未登录应使用 4002。建议改为 `UnauthorizedException`。
- `projects.py:50-62` 的 `_handle_service()` 未使用，且会把任意异常 `str(e)` 返回前端；建议删除或不要用于生产路径。
- 请求体参数写成 `body: CreateProjectRequest = None` 等形式，缺少请求体时会变成 `None` 后触发属性错误；建议改为必填请求体，避免把参数错误变成系统错误。

## 12. 是否发现越界实现

未发现 Stage-04 审查对象中注册以下越界接口：

- 任务管理；
- AI 调用；
- 提示词模板；
- 审核中心；
- 成果库；
- 前端页面。

## 13. 静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/projects.py app/services/project_service.py app/repositories/project_repo.py run.py
```

结果：通过，输出 `PY_COMPILE_OK`。

环境限制：

- 当前远程 Ubuntu 仍缺少 `pip` / `venv` / 运行依赖；
- 当前 Ubuntu 环境无法直接访问 Windows MySQL；
- 因此未实际执行 `pip install -r requirements.txt`、`python run.py` 或真实数据库接口测试。

环境限制不作为本轮不通过原因。本轮不通过原因来自代码逻辑和事务设计问题。

## 14. 必须修复的问题

1. 修复 `project_repo.create_project()` 不返回 `project_id` 的问题，并确保 `POST /api/projects` 返回真实项目详情。
2. 将创建项目、软删除项目、添加成员、修改成员角色、移除成员、项目归档与对应 `operation_logs` 写入放在同一事务内。
3. 项目归档必须优先调用 `sp_archive_project`；如果无法调用，必须完整模拟存储过程行为：归档项目、归档项目任务、关闭任务分支、写日志，并使用单个事务。
4. 修复 teacher 项目列表权限：teacher 只能查看自己在 `project_members.project_role = 'teacher'` 下参与的项目。
5. 对 soft delete / update / archive 等 UPDATE 返回值进行检查，未影响行数时不得继续写成功日志或返回成功。
6. 清理或避免使用会暴露 `str(e)` 的 `_handle_service()`，并将未登录错误改为 4002。
7. 修正请求体声明，避免缺少 body 时出现 `NoneType` 属性错误。

## 15. 是否允许进入 Stage-05

暂不允许。

已发布修复任务：

`cursor_and_codex_chat/tasks/todo/TASK-004-FIX-project-space.md`
