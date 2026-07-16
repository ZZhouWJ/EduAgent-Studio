# 智学工坊 EduAgent Studio

> 基于大模型的个性化学习资源生成与学习多智能体系统

EduAgent Studio 面向高校课程学习场景，根据学生画像、知识点掌握度和学习反馈，编排诊断、规划、资源生成、评测与教师审核智能体，形成可追溯的个性化学习闭环。

## 产品能力

### 学生端

- 对话式学习入口、课程任务、学习路径与个性化推荐
- 学生画像、知识点掌握度、学习历史与反馈闭环
- AI 学伴实时问答、资源证据引用与学习建议

### 教师端

- 课程、学生、任务和知识点管理
- 课程资料上传、解析、检索与知识点关联
- 讲义、习题、案例、复习计划等资源生成与审核
- 学情分析、薄弱点识别和资源质量追踪

### 管理端

- 用户与角色管理、模型供应商和智能体配置
- Prompt 版本管理、调用日志、Token 与成本统计
- 操作审计、资源证据链和系统运行状态

## 技术架构

| 层级 | 实现 |
| --- | --- |
| 前端 | React 18、TypeScript、Vite 6、Tailwind CSS、Radix UI、Zustand、Recharts、ECharts |
| 后端 | FastAPI、Pydantic、PyMySQL、JWT、REST、SSE |
| 智能体 | LangGraph、LangChain Core、统一 LLM Gateway |
| 数据 | MySQL 8、Redis、SQLite Checkpoint、本地持久化资源目录 |
| 异步任务 | Celery Worker、Celery Beat |
| 部署 | Docker Compose、Nginx SPA 托管与 API 反向代理 |

后端使用原生参数化 SQL 和 Repository 层，不依赖 ORM。LLM Gateway 支持 Mock、OpenAI-compatible 与讯飞星火配置。

## 目录结构

```text
EduAgent-Studio/
├── frontend/                 # React Web 应用和 Nginx 配置
├── backend/
│   ├── app/
│   │   ├── agents/           # 学习多智能体及工作流
│   │   ├── llm/              # 模型网关与供应商实现
│   │   ├── rag/              # 文档解析与检索
│   │   ├── routers/          # FastAPI 路由
│   │   ├── services/         # 业务服务
│   │   ├── repositories/     # MySQL 数据访问
│   │   └── tasks/            # Celery 任务
│   └── tests/
├── database/                 # MySQL 建库、表、视图、过程与种子数据
└── docker-compose.yml        # 完整运行栈
```

## 快速启动

### Docker Compose

要求 Docker Engine 24+ 与 Docker Compose v2。

```bash
cp .env.example .env
```

编辑 `.env`，至少替换 `DB_PASSWORD`、`JWT_SECRET_KEY` 和 `API_KEY_SECRET`。两个安全密钥必须独立生成：

```bash
openssl rand -hex 32
openssl rand -hex 32
```

启动完整运行栈：

```bash
docker-compose up -d --build
docker-compose ps
```

默认地址：

- Web：<http://127.0.0.1:5173>
- API 健康检查：<http://127.0.0.1:8000/api/health>
- Swagger（`APP_ENV=development`）：<http://127.0.0.1:8000/docs>

首次创建 MySQL 数据卷时，Compose 会按依赖顺序执行生产初始化脚本。`database/07_test_queries.sql` 是会写入测试数据的验证脚本，不会自动执行。

查看日志或停止服务：

```bash
docker-compose logs -f backend celery_worker
docker-compose down
```

仅在确认需要清空数据库时使用 `docker-compose down -v`。

### 原生开发

要求 Python 3.10+、Node.js 18+、MySQL 8 和 Redis 7。

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

前端：

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Vite 默认监听 5173，并将 `/api` 代理到 `127.0.0.1:8000`。

## 数据库初始化

Docker Compose 会自动初始化。原生 MySQL 环境按以下顺序执行：

```text
01, 02, 03, 04, 05, 06,
09, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26
```

其中 `01_create_database.sql` 会重建数据库，只能用于首次初始化或明确的数据重置。`07_test_queries.sql` 仅用于独立验收；`11_postgresql_migration.sql` 是历史迁移参考，不属于当前 MySQL 运行链路。

## 开发种子账号

SQL 初始化只创建禁用的占位账号。开发环境需要显式设置独立密码，再运行种子脚本激活账号：

```bash
read -s DEMO_PASSWORD
export DEMO_PASSWORD
backend/.venv/bin/python database/seed_demo_data.py
unset DEMO_PASSWORD
```

| 角色 | 用户名 |
| --- | --- |
| 管理员 | `admin` |
| 教师 | `teacher_li` |
| 学生 | `student_zhang` |

`DEMO_PASSWORD` 至少 12 个字符，不能使用示例占位值。生产部署不得创建这些开发种子账号。

## 验证

```bash
# 后端
cd backend
PYTHONPATH=. python -m unittest discover -s tests -v
python -m compileall -q app tests

# 前端
cd frontend
npm run lint
npm run build
```

接口运行检查：

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/db
```

## 安全约束

- `.env`、模型密钥和数据库密码禁止提交到版本控制。
- API Key 使用 AES-GCM 加密保存，用户密码使用 BCrypt 哈希。
- JWT 密钥在部署时注入；生产环境禁止使用示例值。
- `CORS_ORIGINS` 只允许实际前端域名，多个域名使用英文逗号分隔。
- 对外部署时由 HTTPS 反向代理终止 TLS，并限制 MySQL、Redis 和后端管理端口的公网访问。

## License

[Apache License 2.0](LICENSE)
