# 智学工坊 EduAgent Studio

> 基于大模型的个性化学习资源生成与多智能体协作系统

面向高校课程学习场景，基于学生画像和知识点掌握情况，组织多个学习智能体协同完成学习诊断、路径规划、资源生成、评测反馈和学习分析，形成闭环的个性化学习系统。

[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL+pgvector-336791?style=flat&logo=postgresql)](https://www.postgresql.org)
[![LangGraph](https://img.shields.io/badge/Multi--Agent-LangGraph-7C3AED?style=flat)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

---

## 项目简介

本系统为中国软件杯 A3 赛题「基于大模型的个性化资源���成与学习多智能体系统开发」参赛作品。

## 核心功能

### 学生端
- **学习仪表盘**：查看今日任务、推荐资源、薄弱点分析
- **学习路径**：按课程查看个人学习路径与任务进度
- **学习任务**：浏览和完成任务，获取智能体生成的个性化资源
- **学习画像**：维护个人目标、薄弱知识点、资源偏好和学习历史
- **智能辅导**：AI 学伴，实时问答与学习引导
- **学习反馈**：提交反馈后智能体生成改进建议

### 教师端
- **教师仪表盘**：查看课程概况、最近任务和学生表现
- **课程管理**：创建和管理课程，发布学习任务
- **知识库管理**：上传和检索课程相关资料
- **教师审核**：审核学生提交的资源，确保准确性和适配性
- **资源库**：管理讲义、PPT 大纲、题库、案例等各类学习资源

### 管理员端
- **管理仪表盘**：系统全局统计（项目、任务、调用量、成本）
- **用户管理**：管理教师、学生账号和权限
- **课程管理**：管理所有课程和课程关联
- **智能体配置**：配置诊断、规划、生成、评测、审核五类智能体
- **模型配置**：统一管理多模型供应商，支持本地 Mock 与真实 API
- **成本统计**：按模型、智能体、课程分析大模型调用成本
- **Prompt 管理**：管理和版本化各智能体的 Prompt 模板
- **调用日志**：完整记录每次智能体调用的输入、输出、Token 消耗和成本
- **操作日志**：追踪用户操作和登录行为

## 核心业务流程

```
学生画像建立 → 教师创建课程 → 发布学习任务
→ 诊断智能体分析薄弱点
→ 规划智能体生成学习路径
→ 生成智能体创建个性化资源
→ 教师审核资源质量
→ 学生学习与测验
→ 评测智能体生成反馈
→ 系统更新学生画像
→ 学习分析看板展示效果
```

## 技术栈

### 前端展示层
React 18 + Vite 6 + TypeScript 5 + Tailwind v4 + shadcn/ui (Radix + CVA) + Zustand + Axios + Recharts + React Router 7

### 后端服务层
FastAPI + Pydantic + SQLAlchemy + Alembic + JWT + RBAC + RESTful API + SSE

### 多智能体编排层
LangGraph + LangChain Core + Agent State + Agent Workflow

### 大模型接入层
统一 LLM Gateway（支持 OpenAI-compatible API、Qwen、DeepSeek、GLM、本地 Mock）

### 数据存储层
PostgreSQL + pgvector（关系数据 + 向量数据）

### 异步任务层
Redis + Celery（长文本生成、资源向量化、学习分析统计）

## 目录结构

```
EduAgent-Studio/
├── frontend/                          # React 前端
│   └── src/
│       ├── app/
│       │   ├── components/            # 通用组件 (Layout, ProductUI...)
│       │   └── pages/                 # 页面 (Login, Admin*, Student*, Teacher*)
│       ├── lib/
│       │   └── api/                   # API 客户端 (agents, artifacts, auth...)
│       └── main.tsx                   # 入口
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── agents/                   # 多智能体 (diagnostic/planner/generator/evaluator/reviewer)
│   │   ├── llm/                     # LLM Gateway (统一模型接入)
│   │   ├── rag/                     # 向量检索与知识库
│   │   ├── routers/                 # API 路由 (auth, tasks, prompts, models...)
│   │   ├── services/                 # 业务逻辑层
│   │   ├── repositories/            # 数据访问层
│   │   ├── adapters/                # 外部服务适配器
│   │   └── tasks/                   # Celery 异步任务
│   └── requirements.txt
├── database/                          # 数据库迁移脚本
├── docker-compose.yml                 # 容器编排
└── docs/                            # 技术文档
```

## 快速启动

### 环境要求
- Python 3.10+ / Node.js 18+
- PostgreSQL 15+（带 pgvector 扩展）
- Redis（可选，用于异步任务）

### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填写数据库和 API Key 配置
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档地址：http://localhost:8000/api/docs

### 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

访问：http://localhost:5174（Vite 自动选择可用端口，proxy 将 `/api/*` 转发到 `http://127.0.0.1:8000`）

### Docker Compose（推荐）

```bash
docker-compose up -d
```

## 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | `Pass@1234` |
| 教师 | teacher01 | `Pass@1234` |
| 学生 | student01 | `Pass@1234` |

> 如果历史数据密码不一致，可连接数据库执行：
> ```sql
> UPDATE users SET password_hash = '$2b$12$...'
> WHERE username IN ('admin','teacher01','student01');
> ```
> 或使用 BCrypt 重新哈希密码。

## API 概览

后端提供 40+ RESTful API 端点，��模块分组：

| 模块 | 前缀 | 说明 |
|------|------|------|
| `auth` | `/api/auth` | 登录、注册、Token |
| `users` | `/api/users` | 用户管理 |
| `projects` | `/api/projects` | 项目管理 |
| `tasks` | `/api/tasks` | 任务 CRUD 与状态流转 |
| `prompts` | `/api/prompt-templates` | Prompt 模板与版本管理 |
| `models` | `/api/models` | 模型供应商配置 |
| `invocations` | `/api/invocations` | 智能体调用记录 |
| `artifacts` | `/api/artifacts` | 学习资源管理 |
| `reviews` | `/api/reviews` | 教师审核 |
| `logs` | `/api/logs` | 操作日志与登录日志 |
| `statistics` | `/api/statistics` | 数据统计与报表 |
| `learning` | `/api/learning` | 课程、知识点、学生画像 |
| `feedbacks` | `/api/feedbacks` | 学习反馈 |
| `resources` | `/api/resources` | 资源库 |
| `profiles` | `/api/profiles` | 学生画像 |
| `storage` | `/api/storage` | 文件存储 |

## 安全说明

- 所有敏感配置通过 `.env` 环境变量读取
- API Key 在数据库中以 AES-GCM 加密存储
- 用户密码以 BCrypt 哈希存储
- JWT Token 认证，RBAC 权限控制
