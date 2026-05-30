# REVIEW-006 提示词模板管理模块审查报告

## 1. 审查结论

审查结论：通过。

Stage-06 已完成提示词模板管理模块，9 个接口完整，主要逻辑符合任务范围、Schema 约束、Repository 分层、参数化 SQL、事务与 `operation_logs` 要求。允许进入 Stage-07。

已发布：

- `cursor_and_codex_chat/tasks/todo/TASK-007-model-invocation-log.md`

## 2. Stage-06 是否遵守任务范围

结论：遵守。

检查结果：

- 只实现了任务类型、提示词模板、提示词版本管理；
- 未发现 AI 调用；
- 未发现审核中心；
- 未发现成果库；
- 未发现统计看板；
- 未发现前端页面；
- 本轮未发现修改 `database/`；
- 本轮未发现修改 `docs/01_数据库Schema冻结说明.md`；
- 未发现数据库表结构修改。

说明：`git status` 中仍可见 `database/` 与 `docs/01_数据库Schema冻结说明.md` 的历史未提交修改，但文件时间检查显示这些不是本轮 Stage-06 产生的修改。

## 3. 任务类型接口是否正确

结论：正确。

检查结果：

- 已实现 `GET /api/task-types`；
- 查询表为 `task_types`；
- 默认过滤 `is_deleted = 0`；
- 默认只返回 `status = 'active'` 的任务类型；
- 返回 `task_type_id`、`type_name`、`type_code`、`description`、`default_template_id`、`status`；
- router 使用 `success_response()`，符合统一返回格式。

## 4. 提示词模板列表、创建、详情、更新、软删除是否正确

结论：基本正确。

### 模板列表

检查结果：

- 已实现 `GET /api/prompt-templates`；
- 查询表为 `prompt_templates`；
- 默认过滤 `pt.is_deleted = 0`；
- 支持 `task_type_id` 过滤；
- 支持 `keyword` 模糊搜索 `template_name`；
- 支持 `page`、`page_size`；
- 返回统一分页结构；
- 联表返回 `task_types.type_name`、`type_code`；
- 返回 `current_version_id`；
- 列表接口未返回完整 `prompt_content`。

### 创建模板

检查结果：

- 已实现 `POST /api/prompt-templates`；
- 只有 admin、teacher、project_leader 可以创建；
- 普通 student_member 不能创建；
- 创建前校验 `task_type_id` 存在且未删除；
- 插入 `prompt_templates`；
- `created_by` 为当前用户；
- 写入 `operation_logs`；
- 使用事务；
- 返回 `template_id`；
- 未修改数据库结构。

### 模板详情

检查结果：

- 已实现 `GET /api/prompt-templates/{template_id}`；
- 查询 `prompt_templates`；
- 默认过滤 `pt.is_deleted = 0`；
- 返回模板基础信息；
- 返回 `current_version_id`；
- 通过 `LEFT JOIN prompt_versions` 返回当前版本的 `current_version_no` 和 `current_prompt_content`；
- 模板不存在时抛出清晰的 `NotFoundException`；
- 未发现敏感信息泄露。

### 更新模板

检查结果：

- 已实现 `PUT /api/prompt-templates/{template_id}`；
- admin、teacher、project_leader、模板创建人可更新；
- 普通 student_member 不能更新；
- 只允许更新 `template_name`、`task_type_id`、`description`、`is_active`；
- 未允许更新 `template_id`、`created_by`、`created_at`；
- UPDATE 检查 affected_rows；
- 写入 `operation_logs`；
- 使用事务；
- SQL 参数化。

### 软删除模板

检查结果：

- 已实现 `DELETE /api/prompt-templates/{template_id}`；
- admin、teacher、project_leader、模板创建人可删除；
- 使用软删除；
- 设置 `is_deleted = 1`、`deleted_at`、`deleted_by`；
- 未发现物理 `DELETE FROM`；
- UPDATE 检查 affected_rows；
- 写入 `operation_logs`；
- 与日志写入处于同一事务。

## 5. 提示词版本创建、列表、启用是否正确

结论：通过，存在非阻塞改进建议。

### 创建版本

检查结果：

- 已实现 `POST /api/prompt-templates/{template_id}/versions`；
- admin、teacher、project_leader、模板创建人可创建；
- 创建前校验 `template_id` 存在且未删除；
- 插入 `prompt_versions`；
- `created_by` 为当前用户；
- 写入 `version_no`、`prompt_content`、`change_note`；
- 如果模板没有 `current_version_id`，会自动设置新版本为当前版本；
- 写入 `operation_logs`；
- 使用事务；
- 返回 `prompt_version_id`。

非阻塞建议：

- `version_no` 目前允许请求传入字符串，数据库字段实际为 `INT UNSIGNED`。建议后续改为只允许正整数或完全由后端自动生成，避免传入非数字导致数据库错误；
- 自动生成 `version_no` 当前在事务外读取上一版本，课程版可接受；如后续增强并发安全，建议迁移到事务内并加锁。

### 版本列表

检查结果：

- 已实现 `GET /api/prompt-templates/{template_id}/versions`；
- 先校验 `template_id` 存在且未删除；
- 查询 `prompt_versions`；
- 默认过滤 `is_deleted = 0`；
- 返回 `prompt_version_id`、`template_id`、`version_no`、`prompt_content`、`change_note`、`created_by`、`created_at`；
- 按 `created_at DESC` 排序；
- SQL 参数化。

### 启用版本

检查结果：

- 已实现 `POST /api/prompt-templates/{template_id}/versions/{version_id}/activate`；
- admin、teacher、project_leader、模板创建人可启用；
- 校验 `template_id` 存在且未删除；
- 校验 `version_id` 属于该 `template_id`；
- 校验版本未删除；
- 更新 `prompt_templates.current_version_id = version_id`；
- UPDATE 检查 affected_rows；
- 写入 `operation_logs`；
- 使用事务。

## 6. operation_logs 是否写入

结论：符合要求。

以下操作均写入 `operation_logs`，并与核心写操作处于同一事务：

- 创建提示词模板；
- 更新提示词模板；
- 软删除提示词模板；
- 创建提示词版本；
- 启用提示词版本。

## 7. Repository 层和参数化 SQL 是否符合要求

结论：符合要求。

检查结果：

- SQL 集中在 `prompt_repo.py`；
- 未发现直接拼接用户输入到 SQL；
- 未使用 ORM；
- 查询默认过滤 `is_deleted = 0`；
- 多表写入使用 service 层事务；
- repository 方法在传入 `conn` 时不自行 commit；
- service 层统一 commit / rollback；
- UPDATE 操作检查 affected_rows；
- 游标和连接由上下文管理或 finally 关闭。

说明：`list_templates()` 中使用 f-string 拼接的是由固定条件片段组成的 `where_clause`，用户输入仍通过参数绑定传入，未发现 SQL 注入风险。

## 8. 权限控制是否符合要求

结论：符合要求。

检查结果：

- admin 可管理所有模板；
- teacher 可创建和管理模板；
- project_leader 可创建和管理模板；
- 模板创建人可管理自己创建的模板；
- 普通 student_member 只能查看任务类型、模板、版本，不能创建、更新、删除或启用版本；
- 权限判断集中在 `prompt_service.py`；
- 未发现普通成员越权修改模板的路径。

## 9. 是否发现越界实现

未发现越界实现。

检查结果：

- 未发现 AI 调用；
- 未发现审核中心；
- 未发现成果库；
- 未发现统计看板；
- 未发现前端页面；
- 未发现 Stage-07 内容提前实现。

## 10. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/prompts.py app/services/prompt_service.py app/repositories/prompt_repo.py run.py
```

结果：通过。

环境限制：当前 Ubuntu/WSL 环境无法访问 Windows MySQL，本轮未执行真实 SQL 和接口联调。按要求进行静态审查，不因此阻塞 Stage-06 通过。

## 11. 是否允许进入 Stage-07

允许。

Stage-06 提示词模板管理模块通过审查，可以进入 Stage-07：模型管理、Mock 模型调用、调用日志和成本记录模块。
