# TASK-001-FIX-R2：修复 Stage-01 第二轮数据库脚本问题

## 任务状态

待 Cursor 修复。

## 背景

Codex 已完成 Stage-01 第二轮审查，审查报告见：

`cursor_and_codex_chat/reviews/REVIEW-001-R2-database-scripts.md`

第二轮审查结论：不通过，不能进入 Stage-02。

## 允许修改

```text
database/02_create_tables.sql
database/03_create_indexes.sql
database/04_insert_initial_data.sql
database/07_test_queries.sql
```

如补齐审计字段影响其他 SQL 文件，可在 handoff 中说明影响范围。

## 禁止修改

```text
backend/*
frontend/*
docs/01_数据库Schema冻结说明.md
```

除非用户明确确认，不得修改 Schema 冻结文档。

## 必须修复的问题

### 1. 修复重复索引 `idx_tasks_creator`

当前重复位置：

- `database/02_create_tables.sql:209`
- `database/03_create_indexes.sql:22`

要求：确保 7 个 SQL 文件按顺序执行时不会重复创建同名索引。

推荐修复方式二选一：

1. 删除 `03_create_indexes.sql` 中的 `CREATE INDEX idx_tasks_creator ON project_tasks(creator_id);`；
2. 或删除 `02_create_tables.sql` 中 `project_tasks` 表内联的 `KEY idx_tasks_creator (creator_id)`，保留 `03_create_indexes.sql` 创建。

不要两处都保留。

### 2. 补齐关联业务表审计字段

按本轮验收要求，核心业务表需要包含：

```text
is_deleted
deleted_at
deleted_by
created_at
created_by
updated_at
updated_by
```

当前缺失字段：

| 表 | 需要补齐字段 |
|---|---|
| `user_roles` | `created_at`, `created_by`, `updated_at`, `updated_by` |
| `role_permissions` | `created_at`, `created_by`, `updated_at`, `updated_by` |
| `output_issue_relations` | `updated_at`, `updated_by` |

要求：补齐字段后，检查初始化数据和测试 SQL 是否需要调整。

## 验收要求

修复后请确认：

1. 7 个 SQL 文件均存在；
2. `02_create_tables.sql` 可创建 27 张表；
3. `02_create_tables.sql` 中不存在重复列；
4. `02_create_tables.sql` 和 `03_create_indexes.sql` 不存在重复索引名；
5. 上述 3 个关联表已补齐完整审计字段；
6. 重点 ENUM 状态值保持不变；
7. 不新增未确认的新表、新状态值；
8. 如果能访问 MySQL，请按顺序实际执行 7 个 SQL 文件并记录结果。

## Handoff 要求

修复完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-001-FIX-R2-database-scripts.md`

内容必须包含：

1. 修改文件列表；
2. 每个问题的修复说明；
3. 是否影响初始化数据；
4. 是否影响外键和索引；
5. SQL 顺序执行结果；
6. 无法实际执行时的原因。
