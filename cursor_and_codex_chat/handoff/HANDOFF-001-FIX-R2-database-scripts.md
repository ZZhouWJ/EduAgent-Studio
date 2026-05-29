# HANDOFF-001-FIX-R2：Stage-01 数据库脚本第三轮修复

版本：v1.0
时间：2026-05-29
修复人：Cursor
审查依据：
- `cursor_and_codex_chat/reviews/REVIEW-001-R2-database-scripts.md`
- `cursor_and_codex_chat/tasks/todo/TASK-001-FIX-R2-database-scripts.md`

---

## 一、Codex 第二轮未通过原因

### 1. P0-1：`idx_tasks_creator` 索引重复

**位置**：
- `database/02_create_tables.sql:209` — `project_tasks` 表内联 `KEY idx_tasks_creator (creator_id)`
- `database/03_create_indexes.sql:22` — 独立 `CREATE INDEX idx_tasks_creator ON project_tasks(creator_id)`

**后果**：按顺序执行 `02` 后再执行 `03`，MySQL 报 `Duplicate key name 'idx_tasks_creator'`。

### 2. P1-1：3 张关联表缺少完整审计字段

**缺失字段对照表**：

| 表 | 缺失字段 |
|---|---------|
| `user_roles` | `created_at`、`created_by`、`updated_at`、`updated_by` |
| `role_permissions` | `created_at`、`created_by`、`updated_at`、`updated_by` |
| `output_issue_relations` | `updated_at`、`updated_by` |

---

## 二、本次修复的问题列表

| # | 问题编号 | 描述 | 修复方式 |
|---|---------|------|---------|
| 1 | P0-1 | `idx_tasks_creator` 重复 | 从 `03_create_indexes.sql` 删除重复行，`idx_tasks_creator` 保留在 `02` 内联定义中 |
| 2 | P1-1 | `user_roles` 缺字段 | 补齐 `created_at`、`created_by`、`updated_at`、`updated_by` |
| 3 | P1-1 | `role_permissions` 缺字段 | 补齐 `created_at`、`created_by`、`updated_at`、`updated_by` |
| 4 | P1-1 | `output_issue_relations` 缺字段 | 补齐 `updated_at`、`updated_by` |
| 5 | — | 测试 SQL 缺少新验证项 | 追加测试 18-22：索引重复检查、3 张表审计字段验证 |

---

## 三、修改的文件列表

| 文件 | 修改类型 | 修改摘要 |
|------|---------|---------|
| `database/02_create_tables.sql` | 修改 | user_roles/role_permissions/output_issue_relations 补齐审计字段 |
| `database/03_create_indexes.sql` | 重写 | 删除重复的 `idx_tasks_creator`，仅保留 `idx_users_username` |
| `database/07_test_queries.sql` | 修改 | 追加测试 18-22（索引重复验证 + 3 表审计字段验证） |
| `cursor_and_codex_chat/handoff/HANDOFF-001-FIX-R2-database-scripts.md` | 新建 | 本文件 |

---

## 四、idx_tasks_creator 处理说明

### 发现情况

全局扫描 `02_create_tables.sql` 和 `03_create_indexes.sql` 后，确认：

| 索引名 | 出现在 02 | 出现在 03 | 是否重复 |
|--------|----------|----------|---------|
| `idx_tasks_creator` | 是（第 209 行，`project_tasks` 表内联） | 是（第 22 行，独立 CREATE INDEX） | **重复** |
| `idx_users_username` | 否 | 是（第 19 行） | 否（保留） |

其余 55 个索引均仅在 `02` 中以内联 KEY 方式定义，`03` 中不存在，不重复。

### 修复方式

**保留位置**：`02_create_tables.sql` — `project_tasks` 表内联

```sql
KEY `idx_tasks_creator` (`creator_id`)
```

**删除位置**：`03_create_indexes.sql` — 删除原第 21-22 行

```sql
-- 已删除（与 02 重复）：
-- CREATE INDEX idx_tasks_creator ON project_tasks(creator_id);
```

**修复后**：`03_create_indexes.sql` 仅包含 `idx_users_username`（唯一不在 `02` 内联定义的补充索引）。

---

## 五、3 张表补齐审计字段详情

### 5.1 user_roles（4 个字段）

**现有字段**：`user_role_id`、`user_id`、`role_id`、`assigned_by`、`assigned_at`、`is_deleted`、`deleted_at`、`deleted_by`

**补齐字段**：

```sql
`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
`created_by` INT UNSIGNED NULL COMMENT '创建人',
`updated_at` DATETIME NULL COMMENT '更新时间',
`updated_by` INT UNSIGNED NULL COMMENT '更新人',
```

**补齐后**：`user_roles` 包含完整 7 个审计字段：`is_deleted`、`deleted_at`、`deleted_by`、`created_at`、`created_by`、`updated_at`、`updated_by`。

### 5.2 role_permissions（4 个字段）

**现有字段**：`role_permission_id`、`role_id`、`permission_id`、`assigned_at`、`is_deleted`、`deleted_at`、`deleted_by`

**补齐字段**：

```sql
`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
`created_by` INT UNSIGNED NULL COMMENT '创建人',
`updated_at` DATETIME NULL COMMENT '更新时间',
`updated_by` INT UNSIGNED NULL COMMENT '更新人',
```

**补齐后**：`role_permissions` 包含完整 7 个审计字段。

### 5.3 output_issue_relations（2 个字段）

**现有字段**：`relation_id`、`output_id`、`review_id`、`tag_id`、`is_deleted`、`deleted_at`、`deleted_by`、`created_at`、`created_by`

**补齐字段**：

```sql
`updated_at` DATETIME NULL COMMENT '更新时间',
`updated_by` INT UNSIGNED NULL COMMENT '更新人',
```

**补齐后**：`output_issue_relations` 包含完整 7 个审计字段。

---

## 六、是否影响外键

**不影响**。

- 新增字段类型为 `DATETIME` 和 `INT`，无外键约束
- `created_by`、`updated_by`、`deleted_by` 不引用其他表，不影响现有外键关系
- 原有主键、唯一约束、外键均未改动

---

## 七、是否影响初始化数据

**可能影响**。

`04_insert_initial_data.sql` 中通过 `CROSS JOIN` 向 `user_roles` 和 `role_permissions` 插入数据时：

```sql
INSERT INTO `user_roles` (`user_id`, `role_id`, `assigned_by`)
SELECT u.user_id, r.role_id, NULL
FROM `users` u, `roles` r
WHERE u.username = 'admin' AND r.role_code = 'admin';
```

修复后表增加了 `created_at`（有 DEFAULT）和 `created_by`（允许 NULL），`assigned_by` 保持 NULL 不变。INSERT 语句不需要修改——`created_at` 自动用 DEFAULT，`created_by` 隐式为 NULL，可以正常执行。

**结论**：初始化数据 INSERT 语句无需修改，可正常执行。

---

## 八、是否影响测试 SQL

**仅追加，不影响已有测试**。

`07_test_queries.sql` 末尾追加了 5 个新测试（第 18-22 组），不影响原有任何测试语句。

---

## 九、SQL 执行顺序

```
01_create_database.sql
  ↓
02_create_tables.sql        （建 27 表 + ALTER TABLE 循环 FK + 补齐审计字段）
  ↓
03_create_indexes.sql     （仅 idx_users_username，无重复）
  ↓
04_insert_initial_data.sql （角色、权限、用户、任务类型、标签、模型）
  ↓
05_create_views.sql        （5 个视图）
  ↓
06_create_stored_procedures.sql （3 个触发器 + 5 个存储过程）
  ↓
07_test_queries.sql        （含新增测试 18-22）
```

---

## 十、验证 SQL

### V1：idx_tasks_creator 仅存在一次

```sql
SELECT
    table_name,
    index_name,
    COUNT(*) AS index_count
FROM information_schema.statistics
WHERE table_schema = 'ai_collab_audit_system'
  AND index_name = 'idx_tasks_creator'
GROUP BY table_name, index_name;
-- 期望：1 行，cnt = 1（project_tasks 表）
```

### V2：所有索引无重复

```sql
SELECT table_name, index_name, COUNT(*) AS cnt
FROM information_schema.statistics
WHERE table_schema = 'ai_collab_audit_system'
  AND index_name != 'PRIMARY'
GROUP BY table_name, index_name
HAVING cnt > 1;
-- 期望：空结果
```

### V3：user_roles 完整审计字段（7 个）

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name = 'user_roles'
  AND column_name IN (
    'is_deleted', 'deleted_at', 'deleted_by',
    'created_at', 'created_by', 'updated_at', 'updated_by'
  )
ORDER BY column_name;
-- 期望：7 行
```

### V4：role_permissions 完整审计字段（7 个）

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name = 'role_permissions'
  AND column_name IN (
    'is_deleted', 'deleted_at', 'deleted_by',
    'created_at', 'created_by', 'updated_at', 'updated_by'
  )
ORDER BY column_name;
-- 期望：7 行
```

### V5：output_issue_relations 完整审计字段（7 个）

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name = 'output_issue_relations'
  AND column_name IN (
    'is_deleted', 'deleted_at', 'deleted_by',
    'created_at', 'created_by', 'updated_at', 'updated_by'
  )
ORDER BY column_name;
-- 期望：7 行
```

### V6：27 张表全部创建

```sql
SELECT COUNT(*) AS total_tables
FROM information_schema.tables
WHERE table_schema = 'ai_collab_audit_system'
  AND table_type = 'BASE TABLE';
-- 期望：27
```

### V7：3 张关联表无重复列

```sql
SELECT column_name, COUNT(*) AS cnt
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name IN ('user_roles', 'role_permissions', 'output_issue_relations')
GROUP BY column_name
HAVING cnt > 1;
-- 期望：空结果
```

---

## 十一、仍然存在的限制

### 无法在当前环境中实际执行 SQL

Codex 第二轮审查已确认：当前环境没有 MySQL/MariaDB 客户端（`mysql: command not found`）。

因此：
- **无法通过 `mysql -u root -p < *.sql` 实际导入验证**
- **所有验证均为静态审查**（通过解析 SQL 文件内容、检查 `information_schema` 元数据查询）
- 如需完整执行验证，需在具备 MySQL 客户端的环境中运行上述 7 个 SQL 脚本

### 静态验证的局限性

以下项目在无 MySQL 环境下**无法静态验证**：
1. 存储过程和触发器是否能在 MySQL 内部编译（语法正确性）
2. `DELIMITER` 块是否在 MySQL 解析器下正确
3. ENUM 值是否在运行时正确约束
4. 外键约束是否在数据插入时正确触发

这些将在具备 MySQL 环境时由 Codex 第三轮审查验证。

---

## 十二、修复摘要

| 问题编号 | 问题描述 | 修复文件 | 修复操作 |
|---------|---------|---------|---------|
| P0-1 | `idx_tasks_creator` 重复 | 03_create_indexes.sql | 删除 `CREATE INDEX idx_tasks_creator`（保留 02 内联定义） |
| P1-1 | `user_roles` 缺 4 个审计字段 | 02_create_tables.sql | 补齐 `created_at/created_by/updated_at/updated_by` |
| P1-1 | `role_permissions` 缺 4 个审计字段 | 02_create_tables.sql | 补齐 `created_at/created_by/updated_at/updated_by` |
| P1-1 | `output_issue_relations` 缺 2 个审计字段 | 02_create_tables.sql | 补齐 `updated_at/updated_by` |
| — | 缺少新验证项 | 07_test_queries.sql | 追加测试 18-22 |
