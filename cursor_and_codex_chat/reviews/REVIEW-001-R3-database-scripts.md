# REVIEW-001-R3：Stage-01 数据库脚本第三轮审查

## 1. 审查结论

结论：通过。

是否允许进入 Stage-02：允许。

本轮以静态审查为主。根据用户说明，当前 MySQL 安装在 Windows 环境中，Codex 所在 Ubuntu / WSL 环境暂时无法直接访问 Windows MySQL，因此实际 MySQL 导入验证不作为本轮阻塞项。后续仍建议在 Windows MySQL 环境中补做 7 个 SQL 文件的顺序导入测试。

## 2. SQL 执行情况

检查当前环境未发现可用 MySQL/MariaDB 客户端：

```bash
command -v mysql
command -v mariadb
command -v mysqladmin
```

均无输出。因此本轮未执行：

```bash
mysql -u root -p < database/01_create_database.sql
mysql -u root -p ai_collab_audit_system < database/02_create_tables.sql
mysql -u root -p ai_collab_audit_system < database/03_create_indexes.sql
mysql -u root -p ai_collab_audit_system < database/04_insert_initial_data.sql
mysql -u root -p ai_collab_audit_system < database/05_create_views.sql
mysql -u root -p ai_collab_audit_system < database/06_create_stored_procedures.sql
mysql -u root -p ai_collab_audit_system < database/07_test_queries.sql
```

按本轮规则，无法访问 Windows MySQL 不阻塞 Stage-01 通过。本报告结论基于逐文件静态审查。

## 3. 第二轮 3 个问题修复情况

### 3.1 `idx_tasks_creator` 重复索引问题

结论：已修复。

证据：

- `database/02_create_tables.sql` 中 `project_tasks` 表保留内联 `KEY idx_tasks_creator (creator_id)`。
- `database/03_create_indexes.sql` 实际只创建 `idx_users_username`。
- 静态解析 `02` 与 `03`，未发现同名重复索引。

说明：`database/03_create_indexes.sql` 的注释中仍提到 `idx_tasks_creator`，但不再执行 `CREATE INDEX idx_tasks_creator ...`，不会造成重复索引错误。

### 3.2 三张关联表完整审计字段问题

结论：已修复。

静态检查确认以下字段均已存在：

```text
is_deleted, deleted_at, deleted_by, created_at, created_by, updated_at, updated_by
```

| 表 | 审查结果 |
|---|---|
| `user_roles` | 7 个审计字段完整 |
| `role_permissions` | 7 个审计字段完整 |
| `output_issue_relations` | 7 个审计字段完整 |

### 3.3 `07_test_queries.sql` 补充验证 SQL

结论：已修复。

`database/07_test_queries.sql` 已补充：

1. 测试 18：验证 `idx_tasks_creator` 无重复；
2. 测试 19：验证 `user_roles` 完整审计字段；
3. 测试 20：验证 `role_permissions` 完整审计字段；
4. 测试 21：验证 `output_issue_relations` 完整审计字段；
5. 测试 22：验证所有索引无重复。

## 4. 本轮静态审查结果

### 4.1 SQL 文件结构

- 7 个 SQL 文件均存在。
- `01_create_database.sql` 使用数据库名 `ai_collab_audit_system`。
- `02_create_tables.sql` 静态解析出 27 张表。
- 27 张表均使用 `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`。
- 未发现额外表名或缺失表名。

### 4.2 Schema 关键字段

通过：

- `ai_models` 包含 `input_price`、`output_price`、`price_unit`。
- `task_outputs` 包含 `parent_output_id`、`source_type`、`lock_version`、`last_modified_at`、`last_modified_by`、`edit_summary`、`is_final_candidate`。
- `api_configs` 包含 `encrypted_api_key`、`key_iv`、`key_tag`、`key_version`、`key_mask`。

### 4.3 重点 ENUM 状态值

通过：

| 字段 | 静态审查结果 |
|---|---|
| `project_members.project_role` | `member / leader / reviewer / teacher` |
| `output_comments.status` | `open / resolved / closed` |
| `issue_tags.severity` | `low / medium / high` |
| `merge_records.merge_strategy` | `adopt_source / adopt_target / manual_merge / adopt_separately` |
| `task_outputs.status` | `draft / generated / submitted / approved / rejected / revision_required / adopted / conflict_pending` |

未发现 Cursor 为本次修复自行新增表名或新增状态值。

### 4.4 初始化数据、视图、触发器、存储过程、测试 SQL

通过静态审查：

- `04_insert_initial_data.sql` 包含角色、权限、管理员用户、任务类型、问题标签、模型供应商、AI 模型、API 配置占位数据。
- `05_create_views.sql` 包含 5 个视图，且不含固定 `DEFINER`。
- `06_create_stored_procedures.sql` 包含 3 个触发器和 5 个存储过程，`sp_complete_review` 不再使用 `ENUM` 参数。
- `07_test_queries.sql` 覆盖关键验收场景，并已补充第二轮要求的验证 SQL。

## 5. 是否发现新问题

未发现阻塞 Stage-01 的新问题。

保留提醒：实际 MySQL 导入验证尚未在本环境执行。建议后续在 Windows MySQL 环境补做顺序导入，并保留执行截图或日志用于课程报告。

## 6. 是否允许进入 Stage-02

允许进入 Stage-02。

本次已发布下一阶段任务：

`cursor_and_codex_chat/tasks/todo/TASK-002-backend-base.md`

Stage-02 仅允许实现 FastAPI 后端基础框架，不允许扩展到登录、用户管理、项目管理、任务管理、AI 调用或前端页面。
