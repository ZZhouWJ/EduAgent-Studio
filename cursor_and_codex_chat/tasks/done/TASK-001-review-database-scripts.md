# TASK-001：Codex 审查 Stage-01 数据库脚本

## 任务状态

待 Codex 审查。

## 背景

Cursor 已完成 Stage-01 数据库脚本，并修正过 ENUM 状态值问题。

## Codex 审查目标

请审查 database/ 下的 7 个 SQL 文件：

- database/01_create_database.sql
- database/02_create_tables.sql
- database/03_create_indexes.sql
- database/04_insert_initial_data.sql
- database/05_create_views.sql
- database/06_create_stored_procedures.sql
- database/07_test_queries.sql

## 审查重点

1. 是否严格符合 docs/01_数据库Schema冻结说明.md；
2. 是否创建 27 张表；
3. 是否所有核心表包含软删除字段；
4. 是否主外键关系合理；
5. 是否初始化数据完整；
6. 是否 ENUM 状态值正确；
7. 是否有视图；
8. 是否有触发器；
9. 是否有存储过程；
10. 是否有测试 SQL；
11. 是否可以进入 Stage-02。

## 输出要求

请创建：

cursor_and_codex_chat/reviews/REVIEW-001-database-scripts.md

审查结论必须包含：

- 通过 / 不通过 / 需要修改
- 发现的问题
- 修改建议
- 是否允许进入 Stage-02
