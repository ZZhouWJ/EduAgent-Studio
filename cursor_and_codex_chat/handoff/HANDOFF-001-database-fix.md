# HANDOFF-001: Stage-01 数据库脚本修复

版本：v1.0
时间：2026-05-29
修复人：Cursor
审查依据：REVIEW-001-database-scripts.md

---

## 一、Codex 未通过原因

Codex 审查（REVIEW-001-database-scripts.md）发现 Stage-01 SQL 脚本存在 4 个 P0 阻塞问题和 2 个 P1 风险问题，导致 `02_create_tables.sql` 无法按顺序执行成功。

---

## 二、已修复问题列表

### P0-1：`task_branches` 表重复定义 `created_by` 列

**问题**：同一个 `CREATE TABLE task_branches` 中出现两次 `created_by` 字段（第 345 行和第 351 行），MySQL 会报 `Duplicate column name created_by`，导致建表失败。

**根因**：Schema 字段摘要中 `task_branches` 的 `created_by` 列在业务字段位置定义了一次，又在全局审计字段中再次定义。

**修复文件**：`database/02_create_tables.sql`

**修复内容**：删除第 345 行业务字段位置的 `created_by` 定义，只保留审计字段块中的 `created_by`（第 351 行）。`task_branches` 表现有字段定义：

```sql
`base_output_id` INT UNSIGNED NULL COMMENT '基准输出版本ID（待 task_outputs 创建后通过 ALTER TABLE 添加外键）',
`status` ENUM(...) NOT NULL DEFAULT 'active' ...,
`is_deleted` TINYINT(1) NOT NULL DEFAULT 0 ...,
`deleted_at` DATETIME NULL ...,
`deleted_by` INT UNSIGNED NULL ...,
`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ...,
`created_by` INT UNSIGNED NULL ...,
`updated_at` DATETIME NULL ...,
`updated_by` INT UNSIGNED NULL ...
```

---

### P0-2：`task_branches` 与 `task_outputs` 循环外键依赖

**问题**：`task_branches.base_output_id` 引用 `task_outputs.output_id`，而 `task_outputs.branch_id` 引用 `task_branches.branch_id`。MySQL 要求被引用表已存在，因此 `02_create_tables.sql` 按顺序执行时，`task_branches` 创建会因 `task_outputs` 不存在而失败。

**修复文件**：`database/02_create_tables.sql`

**修复内容**：

1. 创建 `task_branches` 时，不声明 `fk_task_branches_base_output` 外键约束（仅保留字段 `base_output_id INT UNSIGNED NULL`）
2. 创建 `task_outputs` 时，保留 `fk_task_outputs_branch`（因为 `task_branches` 先创建完毕）
3. 在 `02_create_tables.sql` 末尾，所有 27 张表创建完成后，追加：

```sql
-- 为 task_branches 添加 base_output_id 的外键（引用 task_outputs.output_id）
ALTER TABLE `task_branches`
    ADD CONSTRAINT `fk_task_branches_base_output`
    FOREIGN KEY (`base_output_id`) REFERENCES `task_outputs` (`output_id`);
```

---

### P0-3：`03_create_indexes.sql` 与 `02_create_tables.sql` 存在大量重复索引

**问题**：`02_create_tables.sql` 已经在每个 `CREATE TABLE` 语句中以内联 `KEY idx_xxx (...)` 方式创建了所有普通二级索引，`03_create_indexes.sql` 再次用相同名称创建全部索引，MySQL 会报 `Duplicate key name`。

**修复文件**：`database/03_create_indexes.sql`

**修复内容**：完全重写 `03_create_indexes.sql`，删除全部 57 个重复索引，仅保留 `02_create_tables.sql` 中未以内联方式创建的补充索引（共 2 个）：

```sql
-- users 表：用户名索引（精确匹配登录查询）
CREATE INDEX idx_users_username ON users(username);

-- project_tasks 表：创建人索引（用于查询某用户创建的所有任务）
CREATE INDEX idx_tasks_creator ON project_tasks(creator_id);
```

---

### P0-4：`07_test_queries.sql` 中 `task_branches` INSERT 语句重复 `created_by` 列

**问题**：两处测试 SQL 列清单中出现两次 `created_by`：

```sql
-- 错误写法
INSERT INTO task_branches (project_id, task_id, branch_name, created_by, status, created_by)
VALUES (...)
```

**修复文件**：`database/07_test_queries.sql`

**修复内容**：将列清单修正为与 `task_branches` 实际字段顺序一致（`base_output_id` 已在 `branch_name` 之后），删除重复 `created_by`：

```sql
-- 正确写法
INSERT INTO task_branches (project_id, task_id, branch_name, base_output_id, status, created_by)
VALUES (@tp, @tt, 'feature-test-trigger', NULL, 'active', 1);
```

修复位置：
- 第 158 行（触发器测试分支）
- 第 214 行（归档测试分支，两行 VALUES 批量插入）

---

### P1-1：`05_create_views.sql` 使用固定 `DEFINER = root@%`

**问题**：所有 5 个视图使用 `DEFINER = 'root'@'%'`，课程验收环境不一定允许当前用户创建带 `root@%` DEFINER 的视图，可能出现权限错误。

**修复文件**：`database/05_create_views.sql`

**修复内容**：删除全部 5 个视图定义中的 `ALGORITHM = UNDEFINED / DEFINER = 'root'@'%' / SQL SECURITY DEFINER` 三行，改为标准 `CREATE VIEW v_xxx AS ...` 形式。

---

### P1-2：`sp_complete_review` 参数使用 `ENUM(...)`

**问题**：`p_review_status ENUM('approved','rejected','revision_required')` 对 MySQL 版本兼容性不如 `VARCHAR` 稳定，也不利于未来适配 SQL Server。

**修复文件**：`database/06_create_stored_procedures.sql`

**修复内容**：

1. 参数类型从 `ENUM('approved','rejected','revision_required')` 改为 `VARCHAR(30)`
2. 在存储过程内部添加显式校验：

```sql
IF p_review_status NOT IN ('approved', 'rejected', 'revision_required') THEN
    SET p_result_code = 400;
    SET p_result_message = CONCAT('非法审核结论：', p_review_status, '，允许值：approved/rejected/revision_required');
ELSE
    -- 正常业务逻辑
END IF;
```

校验失败时直接退出（不进入事务），校验通过后才进入 `START TRANSACTION`。

---

## 三、修改文件列表

| 文件 | 修改类型 | 修改内容摘要 |
|------|---------|------------|
| `database/02_create_tables.sql` | 修改 | 删除 `task_branches` 重复 `created_by` 列；移除循环外键约束；追加 ALTER TABLE |
| `database/03_create_indexes.sql` | 重写 | 删除 57 个重复索引；仅保留 2 个补充索引 |
| `database/05_create_views.sql` | 修改 | 删除 5 个视图的 `DEFINER` 声明 |
| `database/06_create_stored_procedures.sql` | 修改 | `sp_complete_review` 参数 ENUM 改为 VARCHAR + 显式校验 |
| `database/07_test_queries.sql` | 修改 | 修复 2 处 `task_branches` INSERT 重复 `created_by` 列 |

未修改：`01_create_database.sql`（未涉及）、`04_insert_initial_data.sql`（未涉及）

---

## 四、是否影响外键

**不影响现有外键**，仅做了以下调整：

- `task_branches.base_output_id` 外键从 CREATE TABLE 内联声明改为末尾 ALTER TABLE 追加（行为不变）
- 其他所有外键约束（`fk_task_outputs_branch`、`fk_adopted_outputs_*`、`fk_merge_records_*` 等）均未改动

---

## 五、是否影响初始化数据

**不影响**。初始化数据中未涉及 `task_branches` 表的 `base_output_id` 字段，无需修改 `04_insert_initial_data.sql`。

---

## 六、是否影响测试 SQL

**影响范围：仅 `07_test_queries.sql` 中的 2 处 INSERT 语句**，已修复。

修复前：
```sql
INSERT INTO task_branches (..., created_by, status, created_by) VALUES (...)
```

修复后：
```sql
INSERT INTO task_branches (project_id, task_id, branch_name, base_output_id, status, created_by) VALUES (...)
```

其他测试 SQL 均未受影响。

---

## 七、重新执行 SQL 命令

```powershell
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\01_create_database.sql
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\02_create_tables.sql
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\03_create_indexes.sql
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\04_insert_initial_data.sql
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\05_create_views.sql
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\06_create_stored_procedures.sql
mysql -u root -p < E:\DatabaseManagementPractice\AI-Collab-Audit-System\database\07_test_queries.sql
```

**注意**：`01_create_database.sql` 包含 `DROP DATABASE IF EXISTS`，会清空已有数据库，仅适合首次初始化或重建测试库。

---

## 八、验证结果

执行以下 SQL 验证修复是否成功：

```sql
-- 验证1：27 张表全部创建成功
SELECT COUNT(*) AS total_tables
FROM information_schema.tables
WHERE table_schema = 'ai_collab_audit_system' AND table_type = 'BASE TABLE';
-- 期望：27

-- 验证2：无重复列（task_branches 只有 1 个 created_by）
SELECT COLUMN_NAME, COUNT(*) AS cnt
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system' AND table_name = 'task_branches'
GROUP BY COLUMN_NAME HAVING cnt > 1;
-- 期望：空结果（无重复列名）

-- 验证3：task_branches.base_output_id 外键已通过 ALTER TABLE 添加
SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM information_schema.key_column_usage
WHERE table_schema = 'ai_collab_audit_system'
  AND TABLE_NAME = 'task_branches'
  AND REFERENCED_TABLE_NAME = 'task_outputs';
-- 期望：fk_task_branches_base_output -> base_output_id -> task_outputs.output_id

-- 验证4：task_outputs.branch_id 外键正常
SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
FROM information_schema.key_column_usage
WHERE table_schema = 'ai_collab_audit_system'
  AND TABLE_NAME = 'task_outputs'
  AND REFERENCED_TABLE_NAME = 'task_branches';
-- 期望：fk_task_outputs_branch -> branch_id -> task_branches.branch_id

-- 验证5：无重复索引名
SELECT INDEX_NAME, COUNT(*) AS cnt
FROM information_schema.statistics
WHERE table_schema = 'ai_collab_audit_system'
GROUP BY TABLE_NAME, INDEX_NAME
HAVING cnt > 1 AND INDEX_NAME NOT IN ('PRIMARY');
-- 期望：空结果

-- 验证6：索引总数（Schema 要求 17 个 + 补充 2 个 = 19 个以上）
SELECT COUNT(*) AS total_indexes
FROM information_schema.statistics
WHERE table_schema = 'ai_collab_audit_system' AND INDEX_NAME != 'PRIMARY';
-- 期望：>= 19

-- 验证7：5 个视图全部创建
SELECT table_name FROM information_schema.views
WHERE table_schema = 'ai_collab_audit_system'
ORDER BY table_name;
-- 期望：v_artifacts, v_model_invocation_statistics, v_pending_reviews, v_project_task_statistics, v_user_permissions

-- 验证8：3 个触发器全部创建
SELECT trigger_name FROM information_schema.triggers
WHERE event_object_schema = 'ai_collab_audit_system'
ORDER BY trigger_name;
-- 期望：trg_output_review_approved, trg_output_review_rejected, trg_output_review_revision_required

-- 验证9：5 个存储过程全部创建
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'ai_collab_audit_system' AND routine_type = 'PROCEDURE'
ORDER BY routine_name;
-- 期望：sp_adopt_output, sp_archive_project, sp_complete_review, sp_create_project_with_owner, sp_submit_output_for_review

-- 验证10：task_branches INSERT 语句无重复列（搜索源码）
-- 在 07_test_queries.sql 中搜索不应出现双 created_by：
-- SELECT * FROM 07_test_queries.sql WHERE column_list LIKE '%created_by, status, created_by%'
-- 期望：无结果

-- 验证11：task_outputs 所有 8 个状态值可写入
INSERT INTO task_outputs (task_id, version_no, output_title, content, source_type, status, created_by)
VALUES (1, 1, '测试draft', '内容', 'ai_generated', 'draft', 1);
-- 期望：成功（不报 ENUM 错误）

-- 验证12：sp_complete_review 非法状态值被拒绝
SET @c=0, @m='';
CALL sp_complete_review(999, 1, 'invalid_status', 8,8,8,8,8,1, '测试', NULL, @c, @m, @r);
SELECT @c AS code, @m AS message;
-- 期望：@c = 400, @m 包含"非法审核结论"

-- 验证13：初始化数据正确
SELECT role_code FROM roles WHERE is_deleted = 0;
-- 期望：admin, project_leader, student_member, teacher

SELECT tag_code, severity FROM issue_tags WHERE is_deleted = 0;
-- 期望：severity 包含 low/medium/high（无 critical/major/minor）
```

---

## 九、修复摘要

| 问题编号 | 描述 | 严重级别 | 修复文件 | 修复方式 |
|---------|------|---------|---------|---------|
| P0-1 | task_branches 重复 created_by 列 | P0 | 02_create_tables.sql | 删除重复列定义 |
| P0-2 | task_branches ↔ task_outputs 循环外键 | P0 | 02_create_tables.sql | FK 延后至 ALTER TABLE |
| P0-3 | 03_create_indexes.sql 57 个重复索引 | P0 | 03_create_indexes.sql | 删除重复，仅保留 2 个补充索引 |
| P0-4 | 07_test_queries INSERT 重复 created_by | P0 | 07_test_queries.sql | 修正列顺序，删除重复列 |
| P1-1 | 视图 DEFINER=root@% 权限风险 | P1 | 05_create_views.sql | 删除 DEFINER 声明 |
| P1-2 | sp_complete_review 参数 ENUM 兼容性 | P1 | 06_create_stored_procedures.sql | 改为 VARCHAR + 显式校验 |
