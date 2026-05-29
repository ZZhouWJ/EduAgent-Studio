# 01_数据库Schema冻结说明

文档版本：v1.0  
数据库基准：MySQL 8.0  
可选适配：SQL Server  
使用方式：本文件是数据库结构唯一事实来源。AI 编程助手不得擅自改表名、字段名、状态值、主外键关系。

---

## 0. Schema 冻结原则

1. 本文件列出的表名、字段名、状态值为固定设计。
2. AI 不得自行删除表、合并表、改名、新增核心字段。
3. 如必须新增字段，必须先提出“Schema 变更申请”，经用户确认后再修改。
4. 所有核心业务表采用软删除。
5. 所有核心数据库操作使用参数化 SQL。
6. 所有关键状态变更使用事务。
7. 审计日志、调用记录、登录日志原则上不物理删除。

## 1. 命名规范

表名统一小写下划线；主键统一为表名单数 + `_id`；外键字段与引用主键同名；时间字段统一使用 `created_at`、`updated_at`、`deleted_at`；用户字段统一使用 `created_by`、`updated_by`、`deleted_by`。

## 2. 全局审计字段

除特殊审计表外，核心业务表必须包含以下字段：

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| is_deleted | TINYINT(1) | NOT NULL DEFAULT 0 | 软删除标记 |
| deleted_at | DATETIME | NULL | 删除时间 |
| deleted_by | INT | NULL | 删除人 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| created_by | INT | NULL | 创建人 |
| updated_at | DATETIME | NULL | 更新时间 |
| updated_by | INT | NULL | 更新人 |


普通查询必须默认加：

```sql
WHERE is_deleted = 0
```

## 3. 固定状态枚举

| 字段 | 允许值 | 说明 |
| --- | --- | --- |
| users.status | active / disabled | 用户正常 / 禁用 |
| projects.status | active / archived / suspended | 项目进行中 / 已归档 / 暂停 |
| project_tasks.status | draft / running / generated / submitted / approved / rejected / revision_required / adopted / archived / conflict_pending | 任务全流程状态 |
| task_branches.status | active / merged / closed / conflict_pending | 分支状态 |
| review_requests.request_status | pending / approved / rejected / revision_required | 审核请求状态 |
| task_outputs.source_type | ai_generated / manual_edit / hybrid / manual_merge | 内容来源 |
| ai_invocations.status | success / failed / timeout / blocked | 模型调用状态 |


## 4. 数据表总清单

| 序号 | 表名 | 中文含义 |
| --- | --- | --- |
| 1 | users | 用户表 |
| 2 | roles | 角色表 |
| 3 | user_roles | 用户角色关联表 |
| 4 | permissions | 权限表 |
| 5 | role_permissions | 角色权限关联表 |
| 6 | projects | 项目空间表 |
| 7 | project_members | 项目成员表 |
| 8 | project_tasks | 项目任务表 |
| 9 | task_branches | 任务分支表 |
| 10 | task_types | 任务类型表 |
| 11 | prompt_templates | 提示词模板表 |
| 12 | prompt_versions | 提示词版本表 |
| 13 | model_providers | 模型供应商表 |
| 14 | ai_models | AI模型表 |
| 15 | api_configs | API配置表 |
| 16 | ai_invocations | AI调用记录表 |
| 17 | task_outputs | 任务输出版本表 |
| 18 | review_requests | 审核请求表 |
| 19 | output_reviews | 输出审核表 |
| 20 | issue_tags | 问题标签表 |
| 21 | output_issue_relations | 输出问题关联表 |
| 22 | output_comments | 输出批注表 |
| 23 | adopted_outputs | 采用成果表 |
| 24 | merge_records | 分支合并记录表 |
| 25 | cost_records | 成本记录表 |
| 26 | operation_logs | 操作日志表 |
| 27 | login_logs | 登录日志表 |


## 5. 详细表结构冻结版

说明：以下“字段摘要”是 AI 生成 SQL 和接口时的字段边界。生成 `02_create_tables.sql` 时必须展开为完整字段、类型、主键、外键、默认值、软删除字段、审计字段。

| 表名 | 中文含义 | 固定字段摘要 | 关键约束 |
| --- | --- | --- | --- |
| users | 用户表 | user_id, username, password_hash, real_name, student_no, email, phone, status, last_login_at, soft-delete/audit fields | username unique; student_no/email unique; status in active/disabled |
| roles | 角色表 | role_id, role_name, role_code, description, status, soft-delete/audit fields | role_code unique |
| user_roles | 用户角色关联表 | user_role_id, user_id, role_id, assigned_by, assigned_at, is_deleted, deleted_at, deleted_by | FK users/roles; unique(user_id, role_id, is_deleted) |
| permissions | 权限表 | permission_id, permission_name, permission_code, module_name, description, soft-delete/audit fields | permission_code unique |
| role_permissions | 角色权限关联表 | role_permission_id, role_id, permission_id, assigned_at, is_deleted, deleted_at, deleted_by | FK roles/permissions |
| projects | 项目空间表 | project_id, project_name, project_type, description, owner_id, status, soft-delete/audit fields | FK owner_id users |
| project_members | 项目成员表 | member_id, project_id, user_id, project_role, joined_at, status, contribution_score, soft-delete/audit fields | FK projects/users; unique(project_id,user_id,is_deleted) |
| project_tasks | 项目任务表 | task_id, project_id, task_type_id, title, description, creator_id, assignee_id, status, priority, due_date, soft-delete/audit fields | FK projects/task_types/users |
| task_branches | 任务分支表 | branch_id, project_id, task_id, branch_name, base_output_id, created_by, status, soft-delete/audit fields | FK projects/tasks/task_outputs/users |
| task_types | 任务类型表 | task_type_id, type_name, type_code, description, default_template_id, status, soft-delete/audit fields | type_code unique |
| prompt_templates | 提示词模板表 | template_id, template_name, task_type_id, description, current_version_id, is_active, soft-delete/audit fields | FK task_types/users |
| prompt_versions | 提示词版本表 | prompt_version_id, template_id, version_no, prompt_content, change_note, soft-delete/audit fields | FK prompt_templates/users |
| model_providers | 模型供应商表 | provider_id, provider_name, provider_code, base_url, website, description, status, soft-delete/audit fields | provider_code unique |
| ai_models | AI模型表 | model_id, provider_id, model_name, display_name, capability_tags, max_context, input_price, output_price, price_unit, status, soft-delete/audit fields | FK provider; unique(provider_id, model_name, is_deleted) |
| api_configs | API配置表 | api_config_id, provider_id, config_name, encrypted_api_key, key_iv, key_tag, key_version, key_mask, quota_limit, used_quota, status, soft-delete/audit fields | FK provider/users; no plaintext key |
| ai_invocations | AI调用记录表 | invocation_id, project_id, task_id, branch_id, model_id, prompt_version_id, input_text, output_text, input_tokens, output_tokens, latency_ms, status, error_message, created_by, created_at | Audit table; no business delete |
| task_outputs | 任务输出版本表 | output_id, task_id, branch_id, invocation_id, version_no, output_title, content, source_type, parent_output_id, lock_version, last_modified_at, last_modified_by, edit_summary, is_final_candidate, status, soft-delete/audit fields | FK self parent; optimistic lock required |
| review_requests | 审核请求表 | request_id, output_id, task_id, project_id, submitter_id, reviewer_id, request_status, submit_note, reviewed_at, soft-delete/audit fields | FK outputs/tasks/projects/users |
| output_reviews | 输出审核表 | review_id, request_id, output_id, reviewer_id, accuracy_score, completeness_score, logic_score, format_score, usability_score, risk_score, review_status, review_comment, reviewed_at, soft-delete/audit fields | FK review_requests/task_outputs/users |
| issue_tags | 问题标签表 | tag_id, tag_name, tag_code, description, severity, soft-delete/audit fields | tag_code unique |
| output_issue_relations | 输出问题关联表 | relation_id, output_id, review_id, tag_id, created_at, created_by, is_deleted, deleted_at, deleted_by | FK outputs/reviews/tags |
| output_comments | 输出批注表 | comment_id, output_id, commenter_id, comment_type, comment_text, status, soft-delete/audit fields | FK outputs/users |
| adopted_outputs | 采用成果表 | adopted_id, project_id, task_id, output_id, artifact_title, artifact_type, release_version, adopted_by, adopted_at, soft-delete/audit fields | FK projects/tasks/outputs/users |
| merge_records | 分支合并记录表 | merge_id, project_id, task_id, base_output_id, source_output_id, target_output_id, merged_output_id, merge_strategy, merge_comment, merged_by, merged_at, is_deleted, deleted_at, deleted_by | FK outputs/users |
| cost_records | 成本记录表 | cost_id, invocation_id, project_id, task_id, model_id, user_id, input_tokens, output_tokens, total_tokens, input_cost, output_cost, total_cost, currency, created_at | Audit/stat table; no business delete |
| operation_logs | 操作日志表 | log_id, user_id, project_id, task_id, target_type, target_id, action_type, action_desc, old_value, new_value, ip_address, user_agent, created_at | Audit table; no delete |
| login_logs | 登录日志表 | login_id, user_id, username, login_status, failure_reason, ip_address, user_agent, login_time | Audit table; no delete |


## 6. 关键字段强约束

### 6.1 ai_models 计费字段

`ai_models` 必须包含：`input_price`、`output_price`、`price_unit`。成本估算由 `input_tokens`、`output_tokens` 和模型单价计算。课程版统一约定 `price_unit = 1K_TOKENS`。

### 6.2 task_outputs 乐观锁字段

`task_outputs` 必须包含：`lock_version`、`last_modified_at`、`last_modified_by`、`edit_summary`。编辑保存必须检查旧的 `lock_version`。

### 6.3 API Key 加密字段

`api_configs` 必须包含：`encrypted_api_key`、`key_iv`、`key_tag`、`key_version`、`key_mask`。数据库严禁保存明文 API Key。

### 6.4 大文本字段

AI 输入、输出、人工修改正文优先使用 `LONGTEXT`。SQL Server 适配时使用 `NVARCHAR(MAX)`。后期如进入比赛版，可迁移至对象存储，数据库只保存 URL、hash、size、version 等元数据。

## 7. 必须创建的索引

```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status_deleted ON users(status, is_deleted);
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status_deleted ON projects(status, is_deleted);
CREATE INDEX idx_project_members_project ON project_members(project_id, is_deleted);
CREATE INDEX idx_project_members_user ON project_members(user_id, is_deleted);
CREATE INDEX idx_tasks_project_status ON project_tasks(project_id, status, is_deleted);
CREATE INDEX idx_tasks_assignee ON project_tasks(assignee_id, is_deleted);
CREATE INDEX idx_outputs_task ON task_outputs(task_id, is_deleted);
CREATE INDEX idx_outputs_parent ON task_outputs(parent_output_id);
CREATE INDEX idx_outputs_status ON task_outputs(status, is_deleted);
CREATE INDEX idx_invocations_task ON ai_invocations(task_id);
CREATE INDEX idx_invocations_model ON ai_invocations(model_id);
CREATE INDEX idx_invocations_created_at ON ai_invocations(created_at);
CREATE INDEX idx_review_requests_status ON review_requests(request_status, is_deleted);
CREATE INDEX idx_reviews_output ON output_reviews(output_id);
CREATE INDEX idx_operation_logs_user_time ON operation_logs(user_id, created_at);
CREATE INDEX idx_login_logs_user_time ON login_logs(user_id, login_time);
```

## 8. 数据库高级特性要求

必须提供以下脚本：`05_create_views.sql`、`06_create_stored_procedures.sql`、`07_test_queries.sql`。

至少包含：项目任务统计视图、模型调用统计视图、审核通过自动写日志触发器、项目一键归档存储过程、版本树递归查询测试 SQL。

## 9. Schema 变更申请格式

如确需变更，AI 必须先输出：

```text
Schema 变更申请

1. 需要变更的表：
2. 需要新增/修改/删除的字段：
3. 变更原因：
4. 对现有外键的影响：
5. 对接口的影响：
6. 对初始化数据的影响：
7. 是否需要迁移脚本：
8. 建议 SQL：
9. 请用户确认后再执行。
```
