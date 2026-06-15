# 智学工坊 EduAgent Studio

> 基于大模型的个性化学习资源生成与多智能体协作系统

面向高校课程学习场景，基于学生画像和知识点掌握情况，组织多个学习智能体协同完成学习诊断、路径规划、资源生成、评测反馈和学习分析，形成「画像 - 生成 - 学习 - 评测 - 优化」的个性化学习闭环。

![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat&logo=react)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL+pgvector-336791?style=flat&logo=postgresql)
![LangGraph](https://img.shields.io/badge/Multi--Agent-LangGraph-7C3AED?style=flat)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 项目简介

本系统为中国软件杯 A3 赛题「基于大模型的个性化资源生成与学习多智能体系统开发」参赛作品。

## 核心功能

- **学生画像**：建立和维护每位学生的学习目标、薄弱知识点、资源偏好和学习历史
- **课程空间**：教师创建和管理课程，发布学习任务
- **智能体工作台**：多智能体协作链路（诊断→规划→生成→评测→审核建议），生成个性化学习资源
- **学习资源库**：统一管理讲义、PPT大纲、题库、案例等各类学习资源
- **教师审核中心**：教师审核学习资源质量，确保内容准确性和适配性
- **学习分析看板**：展示掌握度、薄弱点、资源分布、调用趋势等分析报表
- **学习反馈**：学生提交学习反馈，系统更新画像，智能体生成改进建议
- **智能体调用审计**：完整记录每次智能体调用的输入、输出、Token消耗和成本
- **模型配置**：统一管理多模型供应商，支持本地Mock和真实API

## 核心业务流程

学生画像建立 → 教师创建课程 → 发布学习任务 → 学习诊断智能体分析薄弱点 → 资源规划智能体生成学习路径 → 资源生成智能体生成个性化资源 → 教师审核资源质量 → 学生学习与测验 → 评测反馈智能体生成反馈 → 系统更新学生画像 → 学习分析看板展示效果

## 技术栈

### 前端展示层
React 18 + Vite 6 + TypeScript 5 + Tailwind v4 + shadcn/ui (Radix + CVA) + Zustand + Axios + Recharts + react-router 7

### 后端服务层
FastAPI + Pydantic + SQLAlchemy + Alembic + JWT + RBAC + RESTful API + SSE

### 多智能体编排层
LangGraph + LangChain Core + Agent State + Agent Workflow

### 大模型接入层
统一 LLM Gateway（支持 OpenAI-compatible API、Qwen、DeepSeek、GLM、本地 Mock）

### 数据存储层
PostgreSQL + pgvector（关系数据 + 向量数据）
MySQL（当前业务表，Phase 2迁移至PostgreSQL）

### 知识库与向量检索层
Embedding 生成服务 + 课程材料切分 + 知识点embedding + 资源相似度检索

### 异步任务层
Redis + Celery（长文本生成、资源向量化、学习分析统计）

## 目录结构

```
EduAgent-Studio/
├── frontend/                     # Vue3 前端
│   ├── src/
│   │   ├── pages/
│   │   │   ├── dashboard/       # 首页
│   │   │   ├── courses/         # 课程空间
│   │   │   ├── tasks/           # 学习任务
│   │   │   ├── profiles/        # 学生画像
│   │   │   ├── agent-workbench/ # 智能体工作台
│   │   │   ├── resources/        # 学习资源库
│   │   │   ├── reviews/         # 教师审核中心
│   │   │   ├── analytics/       # 学习分析看板
│   │   │   └── ...
│   │   └── ...
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── agents/              # 多智能体（诊断/规划/生成/评测/审核）
│   │   ├── llm/                 # LLM Gateway（统一模型接入）
│   │   ├── rag/                 # 向量检索与知识库
│   │   ├── routers/             # API路由
│   │   ├── services/             # 业务逻辑层
│   │   ├── repositories/         # 数据访问层
│   │   └── ...
├── database/                    # 数据库脚本
│   ├── 01-08_*.sql            # 原有业务表（MySQL）
│   ├── 09_create_a3_tables.sql # A3专用表（courses/student_profiles等）
│   ├── 10_insert_a3_data.sql   # A3初始化数据
│   └── pgvector/               # pgvector扩展与向量检索Demo
├── docker-compose.yml           # 容器编排
└── docs/                      # 文档
    ├── A3赛题适配说明.md
    ├── 技术架构选型说明.md
    ├── 多智能体设计.md
    └── ...
```

## 后端启动

### 环境要求
- Python 3.10+
- PostgreSQL 15+（带pgvector扩展）
- Redis（可选，用于异步任务）

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env填写配置
```

### 3. 初始化数据库

项目当前用 **MySQL** 跑业务表，用 **PostgreSQL + pgvector** 跑向量检索：

```bash
# MySQL（跑 business 表 + A3 表）
mysql -u root -p ai_collab_audit_system < database/01_create_initial_tables.sql
mysql -u root -p ai_collab_audit_system < database/02_insert_initial_data.sql
# ... 03-08 视情况追加 ...
mysql -u root -p ai_collab_audit_system < database/09_create_a3_tables.sql
mysql -u root -p ai_collab_audit_system < database/10_insert_a3_data.sql

# PostgreSQL（pgvector 可选，给知识库用）
psql -U postgres -d eduagent_studio < database/pgvector/01_enable_pgvector.sql
```

### 4. 启动后端
```bash
cd backend
python run.py
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 前端启动

### 环境要求
- Node.js 18+

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 配置环境变量
```bash
cp .env.example .env
```

### 3. 启动开发服务器
```bash
npm run dev
```

访问：http://localhost:5174

> 注意：5173 端口可能已被其他项目占用，Vite 会自动切换到 5174/5175 等。
> Vite proxy 会把 `/api/*` 转发到 `http://127.0.0.1:8000`（后端默认端口）。

## Docker Compose 启动（推荐）

```bash
docker-compose up -d
```

## 演示账号

| 角色 | 用户名 | 密码 | 登录入口 |
|------|--------|------|---------|
| 管理员 | admin | `Admin@123` | `/admin` |
| 教师 | teacher1 | `123456` | `/teacher` |
| 学生 | student1 | `123456` | `/student` |

> 实际数据库中 `admin`/`teacher01`/`student01` 等账号的密码可能因历史数据不同步而无法登录，
> 可用如下 Python 脚本重置（连接信息见 `backend/.env`）：
>
> ```python
> import pymysql, bcrypt
> conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
>                        password='<DB_PASSWORD>', database='ai_collab_audit_system')
> cur = conn.cursor()
> for u, p in [('admin','Admin@123'), ('teacher1','123456'), ('student1','123456')]:
>     cur.execute("UPDATE users SET password_hash=%s WHERE username=%s",
>                 (bcrypt.hashpw(p.encode(), bcrypt.gensalt(12)).decode(), u))
> conn.commit()
> ```

## 安全说明

- 所有敏感配置通过 `.env` 环境变量读取
- API Key 在数据库中以 AES-GCM 加密存储
- 用户密码以 BCrypt 哈希存储
- JWT Token 认证，RBAC 权限控制
