# EduAgent Studio 数据库说明

> 当前运行基线：MySQL 8.4。PostgreSQL/pgvector 文件仅保留为历史方案参考，不属于当前初始化或部署链路。

## 运行模型

- 业务数据、课程知识库、学生画像、学习路径、资源审核和调用审计统一存储在 MySQL。
- 知识检索由 MySQL 文档分块与轻量 BM25/中文 n-gram 检索完成，无需 pgvector 才能运行。
- Redis 承担应用缓存与 Celery 任务队列，不替代 MySQL 持久化。
- LangGraph checkpoint 存储在后端持久化数据目录中的 SQLite 文件。

## 初始化方式

### Docker Compose

首次创建 MySQL 数据卷时，`docker-compose.yml` 会按文件名顺序挂载并执行生产初始化脚本。已存在数据卷时不会自动重放。

```bash
cp .env.example .env
docker-compose up -d --build
docker-compose ps
```

### 原生 MySQL

`01_create_database.sql` 会重建数据库，只能用于首次初始化或已确认的数据重置。完整初始化顺序为：

```text
01, 02, 03, 04, 05, 06,
09, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
27, 28, 29, 30, 31, 32
```

对已有数据库只顺序执行尚未应用的迁移脚本，不要重新执行 `01_create_database.sql`。例如：

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p ai_collab_audit_system \
  < database/32_seed_course_knowledge_base.sql
```

## 脚本分类

| 范围 | 用途 |
| --- | --- |
| `01`-`06` | 基础库、业务表、索引、初始数据、视图和存储过程 |
| `09`-`10` | A3 课程、知识点、任务、画像与学习资源基础数据 |
| `13`-`17` | 课程资料、文档分块、画像对话、Tutor 会话和证据链 |
| `18`-`26` | 账号、角色、平台设置、资源审核和产品化种子数据修正 |
| `27`-`31` | 任务进度、数据清理、教育 Prompt、模型配置与认证会话 |
| `32` | 导入 CS301《数据库系统原理》9 个课程章节，建立已确认的知识点证据关联 |

`07_test_queries.sql` 会写入验证数据，仅用于独立测试，不参与自动初始化。`08_insert_prompt_templates.sql` 已被后续教育 Prompt 迁移取代。`11_postgresql_migration.sql` 与 `database/pgvector/` 是早期迁移探索，不得与当前 MySQL 链路混用。

## 核心 A3 实体

| 数据表 | 业务含义 |
| --- | --- |
| `courses` | 课程空间与教师归属 |
| `knowledge_points` | 课程知识结构 |
| `course_materials` / `course_material_chunks` | 可检索的课程资料与分块 |
| `kp_chunk_links` | 文档分块与知识点的人工确认证据关联 |
| `student_profiles` / `student_knowledge_mastery` | 学生画像与知识点掌握度 |
| `learning_tasks` / `learning_task_progress` | 教师任务与学生完成进度 |
| `learning_resources` / `learning_resource_reviews` | AI 生成资源、审核与发布状态 |
| `resource_evidence_links` | 学习资源到原始分块的可追溯证据链 |
| `learning_feedbacks` | 学习反馈和画像回写依据 |
| `tutor_sessions` / `tutor_messages` | AI 学伴会话与消息历史 |

## 课程证据种子

`database/fixtures/database_system_principles.md` 是 CS301 的可追溯课程材料。`32_seed_course_knowledge_base.sql` 可重复执行，会：

1. 确保课程材料记录存在并标记为已解析。
2. 写入 9 个课程章节分块。
3. 将每个分块与对应知识点建立 `confirmed` 关联。
4. 为资源生成、Tutor 问答和引用追溯提供真实证据。

## 验证

```bash
curl http://127.0.0.1:8000/api/health/db

cd backend
PYTHONPATH=. python -m unittest tests.test_database_migration_manifest -v
PYTHONPATH=. python -m unittest tests.test_rag_retriever -v
```

全量后端测试命令见根目录 `README.md` 和 `docs/测试说明书.md`。
