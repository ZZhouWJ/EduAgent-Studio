# 数据库 A3 改造说明

## 一、改造策略：两阶段方案

### Phase 1（当前）
- 保留 MySQL 业务表（01-08 脚本）不变
- 新增 A3 专用表（09-10 脚本）：courses、knowledge_points、student_profiles 等
- 新增 PostgreSQL + pgvector 脚本用于向量检索（Phase 2 迁移用）

### Phase 2（后续）
- 将 MySQL 业务表逐步迁移到 PostgreSQL
- 合并为统一的 PostgreSQL + pgvector 数据层

### Phase 3（当前）
- `database/11_postgresql_migration.sql` 完成 A3 业务表的 PostgreSQL schema 创建 + 种子数据迁移
- 执行方式：`psql -U postgres -d eduagent_studio -f database/11_postgresql_migration.sql`

## 二、执行顺序

```bash
# MySQL（Phase 1 当前）
mysql -u root -p ai_collab_audit_system < database/09_create_a3_tables.sql
mysql -u root -p ai_collab_audit_system < database/10_insert_a3_initial_data.sql

# PostgreSQL（Phase 2/3 使用）
# 方式一：仅创建 schema（推荐先试）
psql -U postgres -d eduagent_studio -f database/pgvector/01_enable_pgvector.sql
psql -U postgres -d eduagent_studio -f database/pgvector/02_create_embeddings_table.sql
psql -U postgres -d eduagent_studio -f database/11_postgresql_migration.sql

# 方式二：完整迁移（需先从 MySQL 导出数据）
# mysqldump -h 127.0.0.1 -P 3306 -u root -p061202 \
#   ai_collab_audit_system \
#   courses knowledge_points learning_tasks \
#   student_profiles student_knowledge_mastery learning_resources learning_feedbacks \
#   --where="is_deleted=0" --no-create-info > a3_data.sql
# sed -i 's/`//g' a3_data.sql
# psql -U postgres -d eduagent_studio -f database/11_postgresql_migration.sql
# psql -U postgres -d eduagent_studio -c "\i a3_data.sql"
```

## 三、表命名说明

| A3 表名 | 说明 | 可映射到 MySQL |
|---------|------|---------------|
| courses | 课程空间 | projects |
| learning_tasks | 学习任务 | project_tasks |
| learning_resources | 学习资源 | task_outputs |
| student_profiles | 学生画像 | （新增）|
| knowledge_points | 知识点 | （新增）|
| learning_feedbacks | 学习反馈 | （新增）|
