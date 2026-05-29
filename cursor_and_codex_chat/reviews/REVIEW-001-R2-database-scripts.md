# REVIEW-001-R2：Stage-01 数据库脚本第二轮审查

## 1. 审查结论

结论：不通过，需要继续修改。

是否允许进入 Stage-02：不允许。

本轮说明：Cursor 已修复上一轮多数问题，但 `database/03_create_indexes.sql` 仍与 `database/02_create_tables.sql` 存在一个同名重复索引，按顺序执行仍会失败。同时，本轮验收明确要求所有核心业务表包含完整软删除与审计字段，当前仍有 3 个关联业务表未满足该项要求。

## 2. SQL 执行情况

尝试执行前先检查远程环境：

```bash
mysql --version
mysqladmin ping -uroot
```

结果：远程服务器返回 `mysql: command not found`。当前环境没有 MySQL/MariaDB 客户端，因此无法实际执行以下导入命令：

```bash
mysql -u root -p < database/01_create_database.sql
mysql -u root -p ai_collab_audit_system < database/02_create_tables.sql
mysql -u root -p ai_collab_audit_system < database/03_create_indexes.sql
mysql -u root -p ai_collab_audit_system < database/04_insert_initial_data.sql
mysql -u root -p ai_collab_audit_system < database/05_create_views.sql
mysql -u root -p ai_collab_audit_system < database/06_create_stored_procedures.sql
mysql -u root -p ai_collab_audit_system < database/07_test_queries.sql
```

因此本轮采用逐文件静态审查，并用脚本解析表、字段、枚举、索引和对象定义。

## 3. 上一轮问题修复情况

| 上一轮问题 | 结论 | 证据 |
|---|---|---|
| P0-1 `task_branches.created_by` 重复定义 | 已修复 | `database/02_create_tables.sql:339-360` 中仅保留一个 `created_by` |
| P0-2 `task_branches` 与 `task_outputs` 循环外键顺序 | 已修复 | `task_branches` 建表时不再内联引用 `task_outputs`，末尾用 `ALTER TABLE` 添加 `fk_task_branches_base_output` |
| P0-3 `03_create_indexes.sql` 与 `02_create_tables.sql` 大量重复索引 | 部分修复但未完成 | 重复索引从 38 个降为 1 个，但 `idx_tasks_creator` 仍重复 |
| P0-4 `07_test_queries.sql` 重复写 `created_by` | 已修复 | `database/07_test_queries.sql:158`、`:215` 改为包含 `base_output_id` 且不重复 `created_by` |
| P1-1 视图固定 `DEFINER = root@%` | 已修复 | `database/05_create_views.sql` 不再包含 `DEFINER` |
| P1-2 `sp_complete_review` 参数使用 `ENUM` | 已修复 | `database/06_create_stored_procedures.sql:454` 改为 `VARCHAR(30)`，并在 `:477` 附近显式校验 |

## 4. 本轮静态审查结果

### 4.1 基础结构

- 7 个 SQL 文件均存在。
- `01_create_database.sql` 使用数据库名 `ai_collab_audit_system`。
- `02_create_tables.sql` 解析到 27 个 `CREATE TABLE`。
- 表定义使用 `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`。
- 未发现额外表名；表清单与 Schema 冻结文档一致。

27 张表：

```text
users, roles, user_roles, permissions, role_permissions, projects,
project_members, task_types, project_tasks, prompt_templates,
prompt_versions, model_providers, ai_models, api_configs,
task_branches, ai_invocations, task_outputs, review_requests,
output_reviews, issue_tags, output_issue_relations, output_comments,
adopted_outputs, merge_records, cost_records, operation_logs, login_logs
```

### 4.2 关键字段

- `ai_models` 包含 `input_price`、`output_price`、`price_unit`。
- `task_outputs` 包含 `parent_output_id`、`source_type`、`lock_version`、`last_modified_at`、`last_modified_by`、`edit_summary`、`is_final_candidate`。
- `api_configs` 包含 `encrypted_api_key`、`key_iv`、`key_tag`、`key_version`、`key_mask`。

### 4.3 ENUM / 状态值

重点枚举均符合本轮要求：

| 字段 | 结果 |
|---|---|
| `project_members.project_role` | `member / leader / reviewer / teacher` |
| `output_comments.status` | `open / resolved / closed` |
| `issue_tags.severity` | `low / medium / high` |
| `merge_records.merge_strategy` | `adopt_source / adopt_target / manual_merge / adopt_separately` |
| `task_outputs.status` | `draft / generated / submitted / approved / rejected / revision_required / adopted / conflict_pending` |

未发现 Cursor 自行添加的新状态值。

### 4.4 初始化数据、高级对象和测试查询

- 初始化数据包含角色、权限、管理员用户、任务类型、问题标签、模型供应商、AI 模型、API 配置占位数据。
- `05_create_views.sql` 包含 5 个视图。
- `06_create_stored_procedures.sql` 包含 3 个触发器、5 个存储过程。
- `07_test_queries.sql` 覆盖用户角色、项目任务统计、模型统计、待审核、成果库、递归版本链、触发器、归档存储过程、创建项目存储过程、枚举、表结构、视图、过程、触发器和外键检查。

## 5. 本轮发现的新问题 / 未完成问题

### P0-1：`idx_tasks_creator` 仍重复创建，按顺序执行会失败

位置：

- `database/02_create_tables.sql:209`
- `database/03_create_indexes.sql:22`

问题：`project_tasks` 表内已经定义：

```sql
KEY `idx_tasks_creator` (`creator_id`)
```

但 `03_create_indexes.sql` 又执行：

```sql
CREATE INDEX idx_tasks_creator ON project_tasks(creator_id);
```

MySQL 同一张表中同名索引不能重复创建，按顺序导入到 `03_create_indexes.sql` 时会报 `Duplicate key name idx_tasks_creator`。

修复建议：删除其中一处。为了保持 `03_create_indexes.sql` 作为补充索引脚本，建议删除 `03_create_indexes.sql:21-22` 中的 `idx_tasks_creator`，或者从 `02_create_tables.sql:209` 移除内联索引并保留 `03` 中的创建语句。二选一即可，不能重复。

### P1-1：部分关联业务表未满足本轮完整审计字段要求

本轮验收要求所有核心业务表包含：

```text
is_deleted, deleted_at, deleted_by, created_at, created_by, updated_at, updated_by
```

静态检查发现以下表缺字段：

| 表 | 缺失字段 |
|---|---|
| `user_roles` | `created_at`, `created_by`, `updated_at`, `updated_by` |
| `role_permissions` | `created_at`, `created_by`, `updated_at`, `updated_by` |
| `output_issue_relations` | `updated_at`, `updated_by` |

说明：`docs/01_数据库Schema冻结说明.md` 的详细字段摘要对这些关联表写得较简略，但同文档“全局审计字段”章节和本轮用户验收要求都明确要求核心业务表具备完整软删除与审计字段。因此本轮按更严格要求判定为需要修复。

修复建议：补齐上述字段，并同步检查初始化数据和相关插入语句是否需要显式或默认处理。若团队决定关联表不属于“核心业务表”，需要在 Schema 冻结文档中明确例外范围；否则应按本轮要求补齐。

## 6. 对照验收清单

| 检查项 | 结论 |
|---|---|
| 7 个 SQL 文件均存在 | 通过 |
| 数据库名为 `ai_collab_audit_system` | 通过 |
| 表使用 InnoDB | 通过 |
| 字符集使用 utf8mb4 | 通过 |
| 27 张表全部存在 | 通过 |
| 核心业务表完整软删除/审计字段 | 不通过，3 个关联表缺字段 |
| 主键、外键、唯一约束、非空约束合理 | 基本通过，但索引脚本仍有重复执行风险 |
| 初始化数据完整 | 通过课程初始化要求 |
| `ai_models` 计费字段 | 通过 |
| `task_outputs` 版本/乐观锁字段 | 通过 |
| `api_configs` 加密字段 | 通过 |
| 重点 ENUM 状态值 | 通过 |
| 视图存在 | 通过静态审查 |
| 触发器存在 | 通过静态审查 |
| 存储过程存在 | 通过静态审查 |
| `07_test_queries.sql` 覆盖关键验收场景 | 通过静态审查 |
| 不存在新状态值、新表名 | 通过 |
| 不存在绕过 Schema 冻结设计 | 需要修复审计字段一致性 |
| 是否允许进入 Stage-02 | 不允许 |

## 7. 必须修复项

Cursor 需要继续修复：

1. 删除或移动重复索引 `idx_tasks_creator`，确保 `02_create_tables.sql` 与 `03_create_indexes.sql` 顺序执行不会重复创建同名索引。
2. 按本轮验收要求补齐以下审计字段：
   - `user_roles.created_at`
   - `user_roles.created_by`
   - `user_roles.updated_at`
   - `user_roles.updated_by`
   - `role_permissions.created_at`
   - `role_permissions.created_by`
   - `role_permissions.updated_at`
   - `role_permissions.updated_by`
   - `output_issue_relations.updated_at`
   - `output_issue_relations.updated_by`
3. 修复后重新提交 handoff，并说明是否已在具备 MySQL 客户端的环境中按 7 个脚本顺序执行成功。

## 8. 任务流转

Stage-01 第二轮审查不通过。本次不发布 `TASK-002-backend-base.md`。

已创建后续修复任务：`cursor_and_codex_chat/tasks/todo/TASK-001-FIX-R2-database-scripts.md`。
