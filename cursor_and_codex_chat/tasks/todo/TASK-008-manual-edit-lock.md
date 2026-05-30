# TASK-008 人工编辑、批注与乐观锁模块

## 任务状态

已完成。

## 任务目标

实现人工编辑、基于已有输出另存为新版本、乐观锁并发控制，以及输出批注基础功能。所有写操作必须写入 `operation_logs`，并遵守 `docs/01_数据库Schema冻结说明.md` 与 `docs/02_接口契约与页面清单.md`。

本阶段不实现审核中心、成果库、统计看板或前端页面。

## 前置条件

- Stage-01 数据库脚本已通过静态审查；
- Stage-02 FastAPI 后端基础框架已通过；
- Stage-03 用户登录与权限基础模块已通过；
- Stage-04 项目空间管理模块已通过；
- Stage-05 任务与版本管理模块已通过；
- Stage-06 提示词模板管理模块已通过；
- Stage-07 模型管理、Mock 模型调用、调用日志和成本记录模块已通过 Fix R2 复审。

## 允许实现

1. 编辑输出版本接口；
2. 基于已有输出另存为新版本接口；
3. 乐观锁并发控制；
4. 输出批注新增接口；
5. 输出批注列表接口；
6. 批注状态更新接口；
7. `output_comments` 写入；
8. 人工编辑相关 `operation_logs` 写入。

## 建议接口

请以 `docs/02_接口契约与页面清单.md` 为准。如文档已有明确路径，必须优先遵守文档。

建议至少实现：

- `PUT /api/outputs/{output_id}`
- `POST /api/outputs/{output_id}/save-as`
- `GET /api/outputs/{output_id}/comments`
- `POST /api/outputs/{output_id}/comments`
- `PUT /api/comments/{comment_id}/status`

如认为 `POST /api/outputs/{output_id}/save-as` 属于接口契约补充，请在 handoff 中说明理由，不得扩展到 Stage-09 审核流程。

## 允许修改文件

- `backend/app/routers/tasks.py`
- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-008-manual-edit-lock.md`

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 审核中心；
2. 成果库；
3. 统计看板；
4. 前端页面。

## 数据库与 Schema 要求

必须严格遵守已冻结 Schema，不得新增表、改字段或新增状态值。

重点涉及表：

- `task_outputs`
- `output_comments`
- `operation_logs`
- 可读取：`project_tasks`、`task_branches`、`projects`、`project_members`

## 权限要求

1. 所有接口必须从 `Authorization: Bearer token` 解析当前用户；
2. 非项目成员不得查看、编辑、另存、批注项目输出；
3. admin 可访问全部项目输出；
4. 项目成员只能操作自己参与项目下的输出；
5. 批注状态更新至少应限制为批注创建人、项目负责人、teacher 或 admin；
6. 不得泄露其他项目的输出内容或批注。

## 编辑输出版本要求

`PUT /api/outputs/{output_id}` 必须：

1. 校验输出版本存在且 `is_deleted = 0`；
2. 校验当前用户有权限访问输出所属项目；
3. 请求体必须包含 `content`、`lock_version`、`edit_summary`；
4. 使用乐观锁：`WHERE output_id = %s AND lock_version = %s AND is_deleted = 0`；
5. 更新成功时 `lock_version = lock_version + 1`；
6. 更新 `content`、`last_modified_at`、`last_modified_by`、`edit_summary`、`updated_at`、`updated_by`；
7. `affected_rows == 0` 时返回统一错误，错误码建议 `4004`；
8. 写入 `operation_logs`；
9. 编辑和日志必须在同一事务内；
10. 不得物理删除或覆盖其他版本。

## 另存为新版本要求

基于已有输出另存为新版本时必须：

1. 校验源输出存在且未删除；
2. 校验当前用户有权限访问输出所属项目；
3. 新版本 `parent_output_id` 指向源 `output_id`；
4. 新版本 `source_type` 建议为 `manual_edit` 或 `hybrid`；
5. `version_no` 必须在事务内生成，避免重复；
6. `lock_version` 初始值符合 Schema 默认或显式设为 0/1，并与现有代码保持一致；
7. 设置 `last_modified_at`、`last_modified_by`、`edit_summary`、`created_by`；
8. 写入 `operation_logs`；
9. 输出创建和日志必须在同一事务内。

## 输出批注要求

新增批注接口必须：

1. 校验输出版本存在且未删除；
2. 校验当前用户有权限访问输出所属项目；
3. 写入 `output_comments`；
4. `comment_text` 不能为空；
5. `status` 必须使用 Schema 允许值：`open`、`resolved`、`closed`；
6. 默认状态建议为 `open`；
7. 写入 `operation_logs`；
8. 批注和日志必须在同一事务内。

批注列表接口必须：

1. 默认过滤 `output_comments.is_deleted = 0`；
2. 支持按 `status` 过滤；
3. 返回批注创建人基本信息；
4. 不返回 `password_hash` 或其他敏感信息；
5. 校验当前用户有权限访问输出所属项目。

批注状态更新接口必须：

1. 校验批注存在且未删除；
2. `status` 只能更新为 `open`、`resolved`、`closed`；
3. 检查 `affected_rows`；
4. 写入 `operation_logs`；
5. 更新和日志必须在同一事务内。

## Repository 与事务要求

1. SQL 集中在 `task_repo.py`；
2. service 层不得直接写 SQL；
3. SQL 必须全部使用参数化查询；
4. 不得拼接用户输入到 SQL；
5. 不得使用 ORM；
6. 查询默认过滤 `is_deleted = 0`；
7. 写操作由 service 层统一 `commit` / `rollback`；
8. repository 方法不得随意 `commit`；
9. `affected_rows` 必须被检查；
10. 连接和 cursor 必须正确关闭。

## 统一返回格式

成功格式必须保持：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误格式必须类似：

```json
{
  "code": 4004,
  "message": "当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。",
  "data": null
}
```

不得新增不一致的返回格式。

## 交付要求

完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-008-manual-edit-lock.md`

handoff 必须说明：

1. 实现了哪些接口；
2. 修改了哪些文件；
3. 是否修改了允许范围之外的文件；
4. 乐观锁如何实现；
5. 另存为新版本如何生成 `parent_output_id` 和 `version_no`；
6. 批注状态值如何校验；
7. 是否写入 `operation_logs`；
8. 是否使用事务；
9. 是否执行语法检查；
10. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py
```

如当前环境可运行服务，可补充接口级测试；如无法连接 Windows MySQL，不作为本阶段静态审查阻塞，但代码本身不得存在明显运行错误。

