# REVIEW-008 人工编辑、批注与乐观锁模块审查报告

## 1. 审查结论

**不通过。**

Stage-08 已实现主要代码框架，乐观锁更新逻辑本身有效，Python 语法检查通过，也未发现本阶段越界修改 `database/`、`frontend/` 或 `docs/01_数据库Schema冻结说明.md`。但本轮发现 3 个阻塞问题，涉及接口路径不符合本轮验收要求、批注类型未按 Schema 枚举校验、批注状态更新权限未正确使用项目内 leader 身份。

因此：**不允许进入 Stage-09**，本次不发布 `TASK-009-review-center.md`。

## 2. Stage-08 是否遵守任务范围

结论：**基本遵守范围。**

- 已实现人工编辑、另存新版本、输出批注新增/列表/状态更新；
- 未发现审核中心、成果库、统计看板、前端页面实现；
- 未发现本轮修改 `database/`、`frontend/`、`docs/01_数据库Schema冻结说明.md`；
- 未发现数据库表结构修改；
- 未发现提前实现 Stage-09 内容。

## 3. 编辑输出版本接口是否正确

结论：**通过。**

已实现：

- `PUT /api/outputs/{output_id}`；
- 当前用户必须有 output 所属项目访问权限；
- 使用请求体 `lock_version`；
- 更新 `content`、`edit_summary`、`last_modified_at`、`last_modified_by`、`updated_at`、`updated_by`；
- 写入 `operation_logs`；
- 输出更新和日志写入在同一事务内。

## 4. 乐观锁是否真正有效

结论：**通过。**

依据：

- `backend/app/repositories/task_repo.py` 中 `update_output_with_lock()` 的 `WHERE` 条件包含 `output_id`、`lock_version`、`is_deleted = 0`；
- 更新成功时 `lock_version = lock_version + 1`；
- `backend/app/services/task_service.py` 中 `affected == 0` 时回滚并抛出 `ConflictException`；
- `ConflictException` 对应 `code = 4004`；
- 冲突时不会写入成功编辑日志。

## 5. 另存为新版本是否正确

结论：**不通过。**

已实现的逻辑基本正确：

- 源 output 必须存在且未删除；
- 当前用户必须有项目访问权限；
- 新版本 `parent_output_id` 指向原 `output_id`；
- 新版本沿用原 `task_id`；
- 未指定 `branch_id` 时沿用原 `branch_id`；
- 指定 `branch_id` 时校验分支属于同一 task；
- `version_no` 在事务内生成；
- `source_type = hybrid`；
- 插入新版本和 `operation_logs` 在同一事务内。

阻塞问题：

1. 本轮验收要求接口为 `POST /api/outputs/{output_id}/save-as-new-version`，但当前只实现了 `POST /api/outputs/{output_id}/save-as`（`backend/app/routers/tasks.py:420`）。因此验收指定接口缺失。

修复要求：

- 增加 `POST /api/outputs/{output_id}/save-as-new-version`；
- 可保留 `/save-as` 作为兼容别名，但必须实现本轮验收指定路径；
- 两个路径如共存，应调用同一个 service 函数，避免逻辑分叉。

## 6. 批注新增、列表、状态更新是否正确

结论：**需要修改。**

已实现：

- `POST /api/outputs/{output_id}/comments`；
- `GET /api/outputs/{output_id}/comments`；
- `PUT /api/comments/{comment_id}/status`；
- 新增批注校验 output 存在且当前用户有项目权限；
- 批注列表默认过滤 `output_comments.is_deleted = 0`；
- 批注状态只允许 `open`、`resolved`、`closed`；
- 状态更新检查 `affected_rows`；
- 批注新增、状态更新均写入 `operation_logs` 并使用事务。

阻塞问题：

1. `comment_type` 未按 Schema 枚举校验。`database/02_create_tables.sql` 中 `output_comments.comment_type` 只允许 `comment`、`suggestion`、`approval`，但 `backend/app/services/task_service.py:917-921` 只校验非空，非法值会进入 repository，导致数据库层异常或产生不一致错误格式。
2. 批注状态更新权限未正确使用项目内 leader 角色。`backend/app/services/task_service.py:994-1003` 检查的是全局 `roles` 中是否包含 `"project_leader"`，但项目成员表中项目负责人角色是 `project_members.project_role = 'leader'`，项目内 leader 可能无法更新批注状态。

修复要求：

- 新增 `VALID_COMMENT_TYPE = {"comment", "suggestion", "approval"}` 或等价校验；
- `POST /api/outputs/{output_id}/comments` 应拒绝非法 `comment_type`，返回统一参数错误；
- 批注状态更新应使用项目内权限判断，例如 `project_repo.is_user_project_leader(project_id, user_id)`；
- teacher 权限也建议以项目内 `project_role = 'teacher'` 或既有项目权限工具判断，而不是只依赖全局角色字符串。

## 7. operation_logs 是否写入

结论：**通过。**

- 编辑输出写入 `output:update`；
- 另存为新版本写入 `output:save_as`；
- 新增批注写入 `output:comment`；
- 批注状态更新写入 `output:comment_status`；
- 以上写操作均与业务数据操作处于同一事务中。

## 8. Repository 层和参数化 SQL 是否符合要求

结论：**基本通过。**

- Stage-08 新增 SQL 集中在 `task_repo.py`；
- service 层未发现直接写 SQL；
- SQL 使用 `%s` 参数化绑定；
- 未发现 ORM；
- 查询默认过滤 `is_deleted = 0`；
- repository 方法未随意 `commit`；
- service 层统一事务提交/回滚。

建议：

- `output_comments` 新增和状态更新可以补齐 `created_by`、`updated_by` 审计字段，使其更符合全局审计字段规范。

## 9. 权限控制是否符合要求

结论：**不通过。**

通过项：

- 非项目成员不能编辑 output；
- 非项目成员不能查看 output comments；
- 非项目成员不能新增 comment；
- admin 可通过 `_can_access_project()` 访问全部；
- 项目成员只能操作自己参与项目的 output。

阻塞问题：

- 批注状态更新权限未正确识别项目内 leader。当前代码依赖全局 `"project_leader"` 角色字符串，不符合 `project_members.project_role = 'leader'` 的项目内角色设计。

## 10. 是否发现越界实现

结论：**未发现。**

- 未发现修改 `database/`；
- 未发现修改 `frontend/`；
- 未发现修改 `docs/01_数据库Schema冻结说明.md`；
- 未发现审核中心、成果库、统计看板或 Stage-09 内容。

## 11. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准，不因无法连接 MySQL 阻塞。

## 12. 是否允许进入 Stage-09

**不允许。**

必须先完成 `TASK-008-FIX-manual-edit-lock.md`。

## 13. 必须修复的问题

1. 增加验收要求的 `POST /api/outputs/{output_id}/save-as-new-version` 接口路径。
2. 为 `comment_type` 增加 Schema 枚举校验，只允许 `comment`、`suggestion`、`approval`。
3. 修复批注状态更新权限，项目内 `leader` 应可更新批注状态，不应只依赖全局 `"project_leader"` 角色字符串。

