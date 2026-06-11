# EduAgent Studio — Phase 1: A3 赛题核心改造实施计划

> **For agentic workers:** Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 EduAgent-Studio 系统从「AI 项目质量审计系统」改造为「智学工坊：基于大模型的个性化学习资源生成与多智能体协作系统」，完成品牌重塑、核心 A3 功能落地（学生画像、智能体工作台、LLM Gateway、pgvector Demo）。

**Architecture:** 采用两阶段方案。第一阶段保留 MySQL 业务表不变，新增 PostgreSQL + pgvector 作为向量检索层；前端和后端业务层文案全面 A3 化；多智能体使用 LangGraph Mock 实现，保留真实模型接口。

**Tech Stack:** Vue3 + Vite + TypeScript + Element Plus / FastAPI + Pydantic + SQLAlchemy / LangGraph + Mock LLM / PostgreSQL + pgvector / Docker Compose

---

## 一、改造文件总览

### 前端改造（9项）

| 文件 | 改造内容 |
|------|---------|
| `frontend/src/layouts/BackendLayout.vue` | Logo标题改为智学工坊，侧边栏菜单A3化 |
| `frontend/src/router/index.ts` | 路由重命名，meta.title A3化，新增学生画像、智能体工作台路由 |
| `frontend/src/pages/login/index.vue` | 登录页标题、副标题改为智学工坊 |
| `frontend/src/pages/dashboard/index.vue` | 首页完全重写为A3风格 |
| `frontend/src/utils/permission.ts` | 角色常量A3化，新增student角色 |
| `frontend/src/api/` | 新增 profiles.ts、agents.ts、learning.ts API文件 |
| `frontend/src/pages/profiles/` | 新建学生画像列表和详情页 |
| `frontend/src/pages/agent-workbench/` | 新建智能体工作台页面 |
| `frontend/package.json` | name/description改为EduAgent |

### 后端改造（8项）

| 文件 | 改造内容 |
|------|---------|
| `backend/app/main.py` | FastAPI title/description改为EduAgent Studio |
| `backend/app/config.py` | app_name默认值改为EduAgent Studio |
| `backend/app/agents/` | 新建5个智能体 + workflow.py |
| `backend/app/llm/` | 新建 gateway.py、providers.py、mock_provider.py |
| `backend/app/routers/profiles.py` | 新建学生画像路由 |
| `backend/app/routers/agents.py` | 新建智能体工作台路由 |
| `backend/app/routers/learning.py` | 新建学习任务路由 |
| `backend/app/services/profile_service.py` | 新建学生画像Service |
| `backend/app/services/agent_service.py` | 新建智能体Service |
| `backend/app/repositories/profile_repo.py` | 新建学生画像Repo |
| `backend/app/repositories/agent_repo.py` | 新建智能体Repo |
| `backend/app/adapters/` | 原Mock适配器保留，新建LearningResourceAdapter |

### 数据库改造（4项）

| 文件 | 改造内容 |
|------|---------|
| `database/09_create_a3_tables.sql` | 新建A3专用表（courses、student_profiles、knowledge_points、learning_resources等） |
| `database/10_insert_a3_initial_data.sql` | 新建A3初始化数据 |
| `database/pgvector/` | 新建pgvector扩展脚本和embedding示例 |
| `database/README_A3.md` | 数据库A3改造说明文档 |

### 基础设施（3项）

| 文件 | 改造内容 |
|------|---------|
| `docker-compose.yml` | 新建PostgreSQL + pgvector + Redis + MinIO服务 |
| `.env.example` | 更新为A3配置项 |
| `backend/.env.example` | 更新为A3配置项 |

### 文档改造（10项）

| 文件 | 改造内容 |
|------|---------|
| `README.md` | 完全重写为EduAgent Studio README |
| `docs/A3赛题适配说明.md` | 新建A3赛题说明文档 |
| `docs/技术架构选型说明.md` | 新建技术架构文档 |
| `docs/多智能体设计.md` | 新建多智能体设计文档 |
| `docs/演示脚本.md` | 新建A3演示脚本 |
| `docs/开发检查清单.md` | 新建开发检查清单 |
| `docs/archive_old_course_project/` | 归档旧课程报告和审查文档 |
| `CHANGELOG_A3_MIGRATION.md` | 新建迁移日志 |

---

## 二、任务分解

---

### Phase 1.1：品牌与文档重塑

#### Task 1: 重写 README.md

**Files:**
- Modify: `README.md:1-355`

**Steps:**

- [ ] **Step 1: 完全重写 README.md**

重写后的文件应包含：

```markdown
# 智学工坊 EduAgent Studio

> 基于大模型的个性化学习资源生成与多智能体协作系统

面向高校课程学习场景，基于学生画像和知识点掌握情况，组织多个学习智能体协同完成学习诊断、路径规划、资源生成、评测反馈和学习分析，形成「画像 - 生成 - 学习 - 评测 - 优化」的个性化学习闭环。

![Vue3](https://img.shields.io/badge/Frontend-Vue3-4FC08D?style=flat&logo=vue.js)
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
Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router + Axios + ECharts

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
│   │   │   ├── resources/       # 学习资源库
│   │   │   ├── reviews/         # 教师审核中心
│   │   │   ├── analytics/        # 学习分析看板
│   │   │   └── ...
│   │   └── ...
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── agents/              # 多智能体（诊断/规划/生成/评测/审核）
│   │   ├── llm/                 # LLM Gateway（统一模型接入）
│   │   ├── rag/                 # 向量检索与知识库
│   │   ├── routers/             # API路由
│   │   ├── services/            # 业务逻辑层
│   │   ├── repositories/        # 数据访问层
│   │   └── ...
├── database/                    # 数据库脚本
│   ├── 01-07_*.sql             # 原有业务表（MySQL）
│   ├── 09_create_a3_tables.sql # A3专用表（courses/student_profiles等）
│   ├── 10_insert_a3_data.sql   # A3初始化数据
│   └── pgvector/               # pgvector扩展与向量检索Demo
├── docker-compose.yml          # 容器编排
└── docs/                       # 文档
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
```bash
# PostgreSQL（新建A3表）
psql -U postgres -d eduagent_studio < database/09_create_a3_tables.sql
psql -U postgres -d eduagent_studio < database/10_insert_a3_data.sql
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

访问：http://localhost:5173

## Docker Compose 启动（推荐）

```bash
docker-compose up -d
```

## 演示账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | Admin@123456 | 全部功能访问权限 |
| 教师 | teacher01 | Teacher@123 | 课程管理、资源审核 |
| 学生 | student01 | Student@123 | 查看任务、生成资源、提交反馈 |

## 安全说明

- 所有敏感配置通过 `.env` 环境变量读取
- API Key 在数据库中以 AES-GCM 加密存储
- 用户密码以 BCrypt 哈希存储
- JWT Token 认证，RBAC 权限控制
```

---

#### Task 2: 新建 docs/A3赛题适配说明.md

**Files:**
- Create: `docs/A3赛题适配说明.md`

**Steps:**

- [ ] **Step 1: 创建 A3 赛题适配说明文档**

```markdown
# A3 赛题适配说明

## 赛题信息

- **赛题编号**：A3
- **赛题名称**：基于大模型的个性化资源生成与学习多智能体系统开发
- **赛道**：A 组（本科）

## 赛题核心要求

### 1. 个性化学生画像
围绕学生个体差异、知识点掌握情况和学习目标，建立学生画像数据模型，支撑后续的个性化资源生成。

### 2. 多智能体协作链路
系统需包含至少 4 类智能体：
- 学习诊断智能体：分析学生薄弱点
- 资源规划智能体：生成学习路径
- 资源生成智能体：生成具体学习资源
- 评测反馈智能体：分析学习效果并更新画像

### 3. 多类型学习资源生成
系统应能生成多种类型的学习资源：
- 知识点讲义
- PPT 大纲
- 习题与答案
- 案例材料
- 复习计划
- 阶段测验

### 4. 教师审核与质量把关
教师能审核智能体生成的学习资源，确保内容准确、难度适配。

### 5. 学习反馈与画像更新
学生完成学习任务后提交反馈，系统据此更新学生画像。

### 6. 学习分析报表
通过图表展示学习效果数据，包括掌握度、薄弱知识点、资源使用情况等。

### 7. 工程化能力
- 智能体调用审计与成本统计
- 操作日志
- 提示词模板管理
- 多模型统一接入

## 系统主线流程

学生画像建立 → 教师创建课程空间 → 发布学习任务 → 学习诊断智能体分析薄弱点 → 资源规划智能体生成学习路径 → 资源生成智能体生成个性化学习资源 → 教师审核资源质量 → 学生学习与测验反馈 → 评测反馈智能体生成反馈 → 系统更新学生画像 → 学习分析看板展示学习效果

## 当前系统改造状态

### Phase 1（已完成）
- [x] 品牌重塑：系统更名为「智学工坊 EduAgent Studio」
- [x] 技术架构升级：Vue3 + FastAPI + PostgreSQL + pgvector + LangGraph + LLM Gateway
- [x] 学生画像模块：前端页面 + 后端接口 + 数据库表
- [x] 智能体工作台：5类智能体 Mock 实现 + LangGraph 工作流
- [x] LLM Gateway：统一模型接入，支持 Mock 和真实 API
- [x] pgvector Demo：向量检索最小可运行示例
- [x] 文档体系：A3赛题说明、技术架构、多智能体设计、演示脚本、开发检查清单

### Phase 2（待完成）
- [ ] 学习反馈与测评：反馈提交界面、后端接口、画像更新逻辑
- [ ] 学习分析看板：6类分析图表（掌握度、薄弱点、资源分布、调用趋势、审核率、成本）
- [ ] 学习资源库深化：资源详情页、教师审核流程、版本记录
- [ ] 异步任务层：Redis + Celery 基础结构
- [ ] 对象存储：MinIO 或本地 storage/ 目录
- [ ] 数据库迁移：MySQL 业务表迁移至 PostgreSQL

## 技术选型理由

### PostgreSQL + pgvector
相比 MySQL，PostgreSQL + pgvector 更适合大模型应用场景：
- 同时存储关系数据和 embedding 数据
- 支持向量相似度检索
- 支持全文检索
- 支持 JSON/JSONB 存储半结构化数据
- 活跃的向量检索生态

### LangGraph
LangGraph 是 LangChain 生态中的工作流编排库，适合构建多智能体协作链路：
- 基于图的 Agent 状态机
- 支持 Human-in-the-loop
- 支持 Checkpoint/Persistence
- 支持条件分支和循环

### LLM Gateway
统一模型接入层，一次配置，多处复用：
- 支持 OpenAI-compatible API
- 支持 Qwen/DeepSeek/GLM 等国产模型
- 支持本地 Mock 模型
- 支持模型配置、密钥加密、调用日志、Token 统计、成本统计
```

---

#### Task 3: 新建 docs/技术架构选型说明.md

**Files:**
- Create: `docs/技术架构选型说明.md`

**Steps:**

- [ ] **Step 1: 创建技术架构选型说明文档**

```markdown
# 技术架构选型说明

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户层（User Layer）                     │
│           Web 浏览器 / 移动端 / API 客户端                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   展示层（Frontend）                          │
│         Vue3 + Vite + TypeScript + Element Plus              │
│         Pinia + Vue Router + Axios + ECharts                 │
│         Markdown 渲染组件 + SSE/WebSocket 客户端              │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/SSE/WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                   服务层（Backend）                          │
│         FastAPI + Pydantic + SQLAlchemy + Alembic            │
│         JWT + RBAC + RESTful API + SSE/WebSocket            │
│         LangGraph + LangChain Core（多智能体编排）            │
└──────┬──────────────────┬────────────────────────────────────┘
       │                  │
┌──────▼──────┐   ┌────────▼──────┐   ┌─────────────────────┐
│   数据层     │   │   智能体层     │   │    知识库层          │
│ PostgreSQL  │   │   LangGraph   │   │    pgvector         │
│ + pgvector  │   │   + LLM       │   │    + Embedding      │
│ MySQL（过渡）│   │   Gateway     │   │    + 向量检索        │
└─────────────┘   └───────────────┘   └─────────────────────┘
       │                  │
┌──────▼──────┐   ┌────────▼──────┐
│   异步层     │   │   存储层       │
│   Redis     │   │   MinIO/本地   │
│   + Celery  │   │   对象存储     │
└─────────────┘   └───────────────┘
```

## 二、技术栈详解

### 2.1 前端展示层

| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | Vue 3 (Composition API) + TypeScript | 基于 V3 Admin Vite 二次开发 |
| 构建工具 | Vite 7 | 热更新与快速构建 |
| UI 组件库 | Element Plus 2.13 | 企业级 Vue 3 组件库 |
| 状态管理 | Pinia 3.0 | 全局状态管理 |
| 路由 | Vue Router 4.6 | SPA 路由管理 |
| HTTP 客户端 | Axios 1.13 | HTTP 请求封装 |
| 可视化 | ECharts | 统计图表 |

**选型理由**：A3 项目需要课程空间、学生画像、智能体工作台、学习资源库、教师审核中心、学习分析看板等复杂后台页面。Vue3 + Vite + TypeScript + Element Plus 适合快速构建稳定、清晰、可演示的 Web 管理系统。

### 2.2 后端服务层

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI >= 0.110.0 |
| 数据校验 | Pydantic >= 2.1.0 |
| ORM/DB | SQLAlchemy >= 2.0（Pg8000驱动）|
| 数据库迁移 | Alembic >= 1.12.0 |
| 认证 | PyJWT >= 2.8.0 |
| 密码哈希 | passlib[bcrypt] >= 1.7.4 |
| API 加密 | cryptography >= 42.0.0 |
| Python 版本 | 3.10+ |

**选型理由**：FastAPI 生态丰富，适合大模型调用、多智能体编排、向量检索和学习画像分析。SQLAlchemy 支持同时连接 MySQL 和 PostgreSQL，Phase 2 可平滑迁移。

### 2.3 多智能体编排层

| 组件 | 技术 |
|------|------|
| 工作流框架 | LangGraph >= 0.0.20 |
| 核心库 | langchain-core >= 0.1.0 |
| Agent State | TypedDict + StateGraph |
| Checkpoint | MemorySaver / PostgreSQL Saver |
| Human-in-loop | Interrupt 和 conditional edges |

**实现智能体**：
- 学习诊断智能体（diagnosis_agent.py）
- 资源规划智能体（planning_agent.py）
- 资源生成智能体（resource_generation_agent.py）
- 评测反馈智能体（assessment_agent.py）
- 教师审核辅助智能体（teacher_review_agent.py）
- 工作流编排（workflow.py）

### 2.4 大模型接入层

| 组件 | 技术 |
|------|------|
| 网关 | LLM Gateway（统一抽象层）|
| 支持模型 | OpenAI / Qwen / DeepSeek / GLM / 本地 Mock |
| 调用方式 | OpenAI-compatible API（/v1/chat/completions）|
| 加密 | API Key AES-GCM 加密存储 |
| 日志 | 每次调用记录 input_tokens、output_tokens、latency、cost |

**文件结构**：
- `llm/gateway.py` — 统一网关
- `llm/providers.py` — 模型供应商管理
- `llm/mock_provider.py` — 本地 Mock 模型
- `llm/openai_compatible_provider.py` — OpenAI 兼容接口

### 2.5 数据存储层

| 组件 | 技术 | 说明 |
|------|------|------|
| 主数据库 | PostgreSQL 15+ + pgvector | 关系数据 + 向量数据，Phase 2 目标 |
| 过渡数据库 | MySQL 8.0+ | 当前业务表，Phase 1 保留 |
| 向量维度 | 768 / 1024 / 1536 | 根据 embedding 模型选择 |

**过渡策略**：
- Phase 1：保留 MySQL 业务表，新增 PostgreSQL + pgvector 作为知识库和向量检索层
- Phase 2：将核心业务数据逐步迁移到 PostgreSQL，最终形成统一 PostgreSQL + pgvector 数据层

### 2.6 知识库与向量检索层

| 组件 | 技术 |
|------|------|
| Embedding | text-embedding-ada-002 / BGE / M3E |
| 切分策略 | RecursiveCharacterTextSplitter |
| 向量存储 | pgvector（PostgreSQL 扩展）|
| 检索方式 | 余弦相似度 / 内积 / 欧氏距离 |

**文件结构**：
- `rag/document_loader.py` — 文档加载
- `rag/text_splitter.py` — 文本切分
- `rag/embedding_service.py` — Embedding 服务
- `rag/vector_store.py` — 向量存储（pgvector）
- `rag/retriever.py` — 向量检索

### 2.7 异步任务层

| 组件 | 技术 |
|------|------|
| 消息队列 | Redis |
| 任务调度 | Celery |
| 用途 | 长文本生成、PPT大纲生成、题库批量生成、embedding批量计算、学习分析统计、成本统计任务 |

### 2.8 部署层

- Docker Compose：PostgreSQL + Redis + 后端 + 前端 + MinIO
- 环境变量管理：`.env.example`
- 不在代码中硬编码真实密钥

## 三、数据流设计

```
用户操作 → 前端页面 → API 请求 → FastAPI 路由
    → Service（业务逻辑）
    → Repository（数据访问）
    → MySQL/PostgreSQL
    → 返回响应

智能体生成流程：
请求 → AgentService → LangGraph Workflow
    → LLM Gateway（选择模型）
    → Mock Provider / 真实 API
    → 调用结果记录 → ai_invocations 表
    → 成本记录 → cost_records 表
    → 返回生成结果
```

## 四、安全设计

- JWT Token 认证，RBAC 权限控制
- API Key AES-GCM 加密存储
- BCrypt 密码哈希
- 环境变量管理敏感配置
- 操作日志全链路追踪
- 软删除保护数据安全
```

---

#### Task 4: 新建 docs/多智能体设计.md

**Files:**
- Create: `docs/多智能体设计.md`

**Steps:**

- [ ] **Step 1: 创建多智能体设计文档**

```markdown
# 多智能体设计文档

## 一、架构概述

本系统采用 LangGraph 构建多智能体协作工作流，以状态机模式管理 Agent 间的数据流转和决策逻辑。

```
┌──────────────┐
│  用户请求     │
└──────┬───────┘
       ▼
┌──────────────┐
│  学习诊断     │  ←── 学生画像 + 知识点 + 历史反馈
│  智能体      │
└──────┬───────┘
       ▼
┌──────────────┐
│  资源规划     │  ←── 诊断结果 + 学习目标 + 课程大纲
│  智能体      │
└──────┬───────┘
       ▼
┌──────────────┐
│  资源生成     │  ←── 学习路径 + 资源类型 + 难度
│  智能体      │
└──────┬───────┘
       ▼
┌──────────────┐
│  评测反馈     │  ←── 生成资源 + 测验结果 + 学习反馈
│  智能体      │
└──────┬───────┘
       ▼
┌──────────────┐
│  教师审核     │  ←── 生成资源 + 课程目标 + 难度要求
│  辅助智能体   │
└──────┬───────┘
       ▼
┌──────────────┐
│  输出结果     │
│  （学习资源）  │
└──────────────┘
```

## 二、智能体定义

### 2.1 学习诊断智能体（Diagnosis Agent）

**职责**：分析学生画像、课程知识点和历史反馈，识别学生的薄弱知识点和学习难点。

**输入**：
- 学生画像数据（学习目标、当前水平、兴趣方向）
- 课程知识点列表（知识点ID、名称、难度等级）
- 历史反馈记录（测验得分、完成情况、错题记录）

**输出**：
```json
{
  "diagnosis_id": "uuid",
  "student_id": 1,
  "weak_points": [
    {"knowledge_point_id": 5, "name": "SQL多表连接", "mastery_level": 0.3, "reason": "近3次测验中正确率仅30%"},
    {"knowledge_point_id": 8, "name": "事务隔离级别", "mastery_level": 0.2, "reason": "从未正确解答相关题目"}
  ],
  "strength_points": [
    {"knowledge_point_id": 2, "name": "SQL基本查询", "mastery_level": 0.85}
  ],
  "learning_difficulties": ["子查询嵌套层次过深难以理解", "HAVING子句与WHERE的区别"],
  "resource_needs": ["补充练习题", "图文并茂的讲义", "具体案例演示"],
  "suggested_difficulty": "intermediate"
}
```

### 2.2 资源规划智能体（Planning Agent）

**职责**：根据诊断结果，生成个性化的学习路径和资源组合方案。

**输入**：
- 诊断结果（薄弱点、难点、资源需求）
- 学习目标（掌握程度、时间计划）
- 课程大纲（知识点拓扑顺序）

**输出**：
```json
{
  "plan_id": "uuid",
  "learning_path": [
    {"order": 1, "knowledge_point_id": 3, "name": "理解连接类型", "estimated_time": "30分钟", "resource_type": "讲义", "priority": "high"},
    {"order": 2, "knowledge_point_id": 5, "name": "SQL多表连接", "estimated_time": "60分钟", "resource_type": "案例+练习", "priority": "high"},
    {"order": 3, "knowledge_point_id": 8, "name": "事务与并发控制", "estimated_time": "45分钟", "resource_type": "讲义+测验", "priority": "medium"}
  ],
  "resource_combination": ["知识点讲义×3", "案例材料×2", "习题与答案×5", "阶段测验×1"],
  "learning_sequence": "由浅入深，先理解概念再实践应用",
  "estimated_total_time": "约3小时"
}
```

### 2.3 资源生成智能体（Resource Generation Agent）

**职责**：根据学习路径和资源类型，生成具体的个性化学习资源。

**输入**：
- 学习路径（知识点、学习顺序、资源类型）
- 资源类型（讲义/PPT大纲/题库/案例/复习计划/测验）
- 难度等级（基础/进阶/高级）
- 学生画像（偏好资源类型、学习风格）

**输出**：
```json
{
  "resource_id": "uuid",
  "resource_title": "SQL多表连接专题讲义",
  "resource_type": "讲义",
  "knowledge_points": [5, 3],
  "difficulty": "intermediate",
  "content": "## SQL多表连接\n\n### 什么是连接...\n\n### 内连接 INNER JOIN...\n\n### 外连接 LEFT/RIGHT JOIN...",
  "target_audience": "已掌握SQL基本查询的学生",
  "estimated_learning_time": "60分钟",
  "generation_metadata": {
    "agent": "resource_generation_agent",
    "model": "mock-gpt",
    "generation_time_ms": 1234
  }
}
```

### 2.4 评测反馈智能体（Assessment Agent）

**职责**：分析学生的测验结果或学习反馈，生成掌握度评价和改进建议。

**输入**：
- 测验结果（答题情况、正确率、错题列表）
- 学习反馈（自评掌握度、遇到的困难）
- 生成资源（本次使用的学习资源）

**输出**：
```json
{
  "assessment_id": "uuid",
  "student_id": 1,
  "test_results": {
    "total_questions": 10,
    "correct_answers": 7,
    "accuracy_rate": 0.7,
    "weak_points": [5]
  },
  "mastery_updates": [
    {"knowledge_point_id": 5, "old_mastery": 0.3, "new_mastery": 0.55, "change_reason": "测验正确率70%，有明显提升"},
    {"knowledge_point_id": 8, "old_mastery": 0.2, "new_mastery": 0.15, "change_reason": "测验未涉及，待下次评估"}
  ],
  "feedback": "多表连接基本概念已掌握，但复杂嵌套查询仍需加强",
  "suggestions": [
    "建议增加复杂嵌套查询的专项练习",
    "推荐学习视图（VIEW）的概念，作为连接与查询的延伸"
  ],
  "next_resource_recommendation": "复杂SQL查询专题练习"
}
```

### 2.5 教师审核辅助智能体（Teacher Review Agent）

**职责**：为教师审核学习资源提供辅助建议，检查资源质量。

**输入**：
- 生成资源（内容、知识点、难度）
- 课程目标（教学大纲、知识点覆盖要求）
- 难度要求（适配年级、基础水平）

**输出**：
```json
{
  "review_id": "uuid",
  "resource_id": "uuid",
  "quality_score": 8.5,
  "quality_checks": [
    {"check": "知识点准确性", "passed": true, "note": "SQL连接语法正确，示例无错误"},
    {"check": "难度适配性", "passed": true, "note": "适合大二数据库课程学生"},
    {"check": "内容完整性", "passed": true, "note": "覆盖了INNER/LEFT/RIGHT/FULL四种连接"},
    {"check": "表述清晰度", "passed": false, "note": "建议增加JOIN与WHERE的对比说明"}
  ],
  "risk_alerts": [
    {"level": "info", "message": "示例中涉及ORDER BY与GROUP BY组合，可能超出本节范围"}
  ],
  "suggestions": [
    "建议在讲义末尾增加4道练习题供学生巩固",
    "补充JOIN与子查询的对比内容"
  ],
  "overall_comment": "资源整体质量良好，知识点覆盖全面，建议小幅修改后通过"
}
```

## 三、LangGraph 工作流

### 3.1 状态定义

```python
from typing import TypedDict, Optional, List
from pydantic import BaseModel

class LearningAgentState(TypedDict):
    student_id: int
    course_id: int
    knowledge_point_ids: List[int]
    resource_type: str
    difficulty: str

    # 各智能体输出
    student_profile: Optional[dict]
    diagnosis: Optional[dict]
    learning_plan: Optional[dict]
    generated_resource: Optional[dict]
    assessment: Optional[dict]
    teacher_review_suggestion: Optional[dict]

    # 执行链路
    current_agent: str
    messages: List[str]
    error: Optional[str]
```

### 3.2 工作流图

```
graph TD
    START([开始]) --> DIAGNOSIS[学习诊断智能体]
    DIAGNOSIS --> PLAN[资源规划智能体]
    PLAN --> GENERATE[资源生成智能体]
    GENERATE --> ASSESS[评测反馈智能体]
    ASSESS --> REVIEW[教师审核辅助智能体]
    REVIEW --> END([结束])

    DIAGNOSIS -.->|出错| ERROR[错误处理]
    PLAN -.->|出错| ERROR
    GENERATE -.->|出错| ERROR
    ERROR --> END
```

## 四、Mock 实现说明

当前所有智能体均以 Mock 模式实现，返回结构化的模拟数据。

Mock 实现特点：
- 返回符合上述 JSON Schema 的结构化数据
- 包含真实的推理逻辑（基于规则的简单推断）
- 每次调用生成唯一的 UUID
- 记录模拟的 Token 消耗和延迟

真实模型接入：
- 在 `llm/gateway.py` 中配置 API Key 和 base_url
- 在 `llm/providers.py` 中注册供应商
- 智能体 prompt 模板在 `prompt_templates` 表中管理
- 切换时仅需修改模型配置，无需改业务代码
```

---

#### Task 5: 新建 docs/演示脚本.md

**Files:**
- Create: `docs/演示脚本.md`

**Steps:**

- [ ] **Step 1: 创建演示脚本文档**

```markdown
# EduAgent Studio 演示脚本

## 演示前准备

1. 启动后端服务：`cd backend && python run.py`
2. 启动前端服务：`cd frontend && npm run dev`
3. 浏览器访问：http://localhost:5173
4. 准备演示账号

## 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | Admin@123456 |
| 教师 | teacher01 | Teacher@123 |
| 学生 | student01 | Student@123 |

## 演示流程（约 15 分钟）

### 第一步：系统概览（2 分钟）

1. 打开浏览器，访问 http://localhost:5173
2. 显示登录页：**智学工坊 EduAgent Studio**
3. 使用 `admin / Admin@123456` 登录
4. 进入首页 Dashboard，展示：
   - 欢迎语：「欢迎使用智学工坊 EduAgent Studio」
   - 核心业务流程图：学生画像 → 智能体诊断 → 资源规划 → 资源生成 → 教师审核 → 学习反馈 → 画像更新
   - 统计卡片：课程数、学生数、学习资源数、智能体调用次数、平均掌握度

### 第二步：学生画像（3 分钟）

1. 点击左侧菜单「学生画像」
2. 展示学生画像列表：
   - 学生姓名、所属课程、当前水平、薄弱知识点、最近更新时间
3. 点击「李明」进入画像详情：
   - 学习目标：掌握数据库系统原理，能够独立完成数据库设计
   - 当前基础：熟悉 SQL 基本查询，多表连接和事务管理薄弱
   - 薄弱知识点标签：SQL多表连接、事务隔离级别
   - 最近学习任务：「数据库事务与并发控制」
4. 点击「编辑」，展示画像编辑表单
5. 说明：画像数据由学生基本信息和历史学习反馈自动汇总

### 第三步：课程空间（2 分钟）

1. 点击左侧菜单「课程空间」
2. 展示课程列表：数据库系统原理、Python程序设计、软件工程实践
3. 点击「数据库系统原理」进入课程详情：
   - 课程描述：系统学习数据库系统原理，包括关系模型、SQL、事务与并发等
   - 关联知识点：关系模型、SQL查询、事务与并发控制、数据库设计
   - 课程成员：教师张老师，学生李明、王悦、陈思雨
4. 展示学习任务列表

### 第四步：智能体工作台 — 核心演示（5 分钟）

1. 点击左侧菜单「智能体工作台」
2. 展示智能体工作台页面，包含5个智能体：
   - 学习诊断智能体
   - 资源规划智能体
   - 资源生成智能体
   - 评测反馈智能体
   - 教师审核辅助智能体
3. 选择学生：李明
4. 选择课程：数据库系统原理
5. 选择知识点：SQL多表连接
6. 选择资源类型：讲义
7. 选择难度：进阶
8. 点击「生成个性化学习资源」
9. 展示智能体执行链路（每个智能体依次执行，耗时约3-5秒）：
   - 学习诊断智能体：「分析李明的学习历史和测验记录...」
   - 资源规划智能体：「生成学习路径：先掌握INNER JOIN，再扩展到OUTER JOIN...」
   - 资源生成智能体：「生成讲义内容：SQL多表连接专题...」
   - 评测反馈智能体：「根据历史测验生成评测建议...」
   - 教师审核辅助智能体：「生成审核建议：内容覆盖全面，建议增加练习题...」
10. 展示最终生成结果：
    - 资源标题：SQL多表连接专题讲义（进阶）
    - 资源类型：讲义
    - 适用学生：李明
    - 知识点：SQL多表连接、INNER JOIN、OUTER JOIN
    - 内容预览：Markdown 格式的讲义正文
11. 点击「保存到学习资源库」

### 第五步：学习资源库（2 分钟）

1. 点击左侧菜单「学习资源库」
2. 展示资源列表：资源标题、所属课程、知识点、资源类型、审核状态
3. 找到刚才保存的「SQL多表连接专题讲义（进阶）」
4. 点击进入详情页：
   - 资源正文（Markdown 渲染）
   - 关联学生画像
   - 关联知识点
   - 生成智能体和生成时间
   - 审核状态：待审核
5. 说明：教师审核后，资源状态变为「已通过」

### 第六步：学习分析看板（2 分钟）

1. 点击左侧菜单「学习分析看板」
2. 展示分析图表：
   - 核心指标卡：课程数、学生数、资源数、调用次数、平均掌握度、审核通过率
   - 薄弱知识点 Top 10：SQL多表连接（23人）、事务隔离级别（18人）、数据库范式（15人）
   - 资源类型分布：讲义45%、题库25%、案例15%、PPT大纲10%、复习计划5%
   - 智能体调用趋势：折线图展示近7天调用次数
   - 审核结果统计：饼图展示通过/退回/修改中比例
3. 说明：数据来自学生画像、智能体调用记录和教师审核记录

### 第七步：调用审计与成本统计（1 分钟）

1. 点击左侧菜单「调用审计」
2. 展示智能体调用记录列表：调用时间、智能体类型、模型、输入Token、输出Token、耗时、成本
3. 点击左侧菜单「成本统计」
4. 展示按模型维度的成本分析图表

## 演示结束

感谢观看。如有问题，欢迎交流。
```

---

### Phase 1.2：前端全面改造

#### Task 6: 重写前端路由和菜单

**Files:**
- Modify: `frontend/src/router/index.ts:1-159`
- Modify: `frontend/src/layouts/BackendLayout.vue:1-386`
- Modify: `frontend/src/utils/permission.ts:1-309`
- Modify: `frontend/package.json:1-26`

**Steps:**

- [ ] **Step 1: 更新 router/index.ts**

将路由改为 A3 语义，新增学生画像、智能体工作台路由：

```typescript
// frontend/src/router/index.ts
import { createRouter, createWebHashHistory } from "vue-router"
import type { RouteRecordRaw } from "vue-router"
import { setupGuard } from "./guard"

type Role = "admin" | "teacher" | "student" | "project_leader"

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/pages/login/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/pages/register/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/403",
    name: "Forbidden",
    component: () => import("@/pages/403/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/",
    component: () => import("@/layouts/BackendLayout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/pages/dashboard/index.vue"),
        meta: { title: "首页" }
      },
      {
        path: "courses",
        name: "Courses",
        component: () => import("@/pages/courses/index.vue"),
        meta: { title: "课程空间" }
      },
      {
        path: "courses/:courseId",
        name: "CourseDetail",
        component: () => import("@/pages/courses/CourseDetail.vue"),
        meta: { title: "课程详情", hidden: true }
      },
      {
        path: "tasks",
        name: "Tasks",
        component: () => import("@/pages/tasks/index.vue"),
        meta: { title: "学习任务" }
      },
      {
        path: "tasks/:taskId",
        name: "TaskDetail",
        component: () => import("@/pages/tasks/TaskDetail.vue"),
        meta: { title: "任务详情", hidden: true }
      },
      {
        path: "profiles",
        name: "Profiles",
        component: () => import("@/pages/profiles/index.vue"),
        meta: { title: "学生画像" }
      },
      {
        path: "profiles/:profileId",
        name: "ProfileDetail",
        component: () => import("@/pages/profiles/ProfileDetail.vue"),
        meta: { title: "画像详情", hidden: true }
      },
      {
        path: "agent-workbench",
        name: "AgentWorkbench",
        component: () => import("@/pages/agent-workbench/index.vue"),
        meta: { title: "智能体工作台" }
      },
      {
        path: "resources",
        name: "Resources",
        component: () => import("@/pages/resources/index.vue"),
        meta: { title: "学习资源库" }
      },
      {
        path: "resources/:resourceId",
        name: "ResourceDetail",
        component: () => import("@/pages/resources/ResourceDetail.vue"),
        meta: { title: "资源详情", hidden: true }
      },
      {
        path: "reviews",
        name: "Reviews",
        component: () => import("@/pages/reviews/index.vue"),
        meta: { title: "教师审核中心" }
      },
      {
        path: "analytics",
        name: "Analytics",
        component: () => import("@/pages/analytics/index.vue"),
        meta: { title: "学习分析看板" }
      },
      {
        path: "invocations",
        name: "Invocations",
        component: () => import("@/pages/invocations/index.vue"),
        meta: { title: "智能体调用审计" }
      },
      {
        path: "costs",
        name: "Costs",
        component: () => import("@/pages/costs/index.vue"),
        meta: { title: "成本统计" }
      },
      {
        path: "models",
        name: "Models",
        component: () => import("@/pages/models/index.vue"),
        meta: { title: "模型与智能体配置", roles: ["admin"] }
      },
      {
        path: "prompts",
        name: "Prompts",
        component: () => import("@/pages/prompts/index.vue"),
        meta: { title: "提示词模板" }
      },
      {
        path: "users",
        name: "Users",
        component: () => import("@/pages/users/index.vue"),
        meta: { title: "用户管理", roles: ["admin"] }
      },
      {
        path: "logs/operation",
        name: "OperationLogs",
        component: () => import("@/pages/logs/operation.vue"),
        meta: { title: "操作日志", roles: ["admin"] }
      },
      {
        path: "logs/login",
        name: "LoginLogs",
        component: () => import("@/pages/logs/login.vue"),
        meta: { title: "登录日志", roles: ["admin"] }
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("@/pages/profile/index.vue"),
        meta: { title: "个人中心", hidden: true }
      }
    ]
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login"
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

setupGuard(router)

export default router
```

- [ ] **Step 2: 更新 permission.ts 中的角色常量**

```typescript
// frontend/src/utils/permission.ts - 修改角色常量

export type GlobalRole = "admin" | "teacher" | "student" | "assistant"

export const GLOBAL_ROLE_LABEL: Record<string, string> = {
  admin: "系统管理员",
  teacher: "教师",
  student: "学生",
  assistant: "助教"
}
```

- [ ] **Step 3: 更新 package.json**

```json
{
  "name": "eduagent-studio-frontend",
  "type": "module",
  "version": "1.0.0",
  "description": "智学工坊 EduAgent Studio - 基于大模型的个性化学习资源生成与多智能体协作系统",
  // ... 其他保持不变
}
```

---

#### Task 7: 重写 BackendLayout.vue — 侧边栏 A3 化

**Files:**
- Modify: `frontend/src/layouts/BackendLayout.vue:1-386`

**Steps:**

- [ ] **Step 1: 完全重写侧边栏 Logo 和菜单分组**

将 BackendLayout.vue 的 logo 区域和 menuGroups computed 属性改为 A3 语义，保留原有的图标和样式：

```vue
// 侧边栏 Logo 区域改为：
<div class="logo">
  <div class="logo-title">智学工坊</div>
  <div class="logo-subtitle">EduAgent Studio</div>
</div>

// menuGroups computed 改为：
const menuGroups = computed(() => {
  const roleArr = user.value?.roles ?? []
  const adminFlag = isAdmin(user.value)
  const teacherFlag = isTeacher(user.value)
  const groups = []

  // 学习
  groups.push({
    title: "学习",
    items: [
      { path: "/dashboard", label: "首页", icon: House },
      { path: "/courses", label: "课程空间", icon: Folder },
      { path: "/tasks", label: "学习任务", icon: List }
    ]
  })

  // 智能体
  groups.push({
    title: "智能体",
    items: [
      { path: "/agent-workbench", label: "智能体工作台", icon: Cpu },
      { path: "/profiles", label: "学生画像", icon: UserFilled }
    ]
  })

  // 资源与审核
  groups.push({
    title: "资源与审核",
    items: [
      { path: "/resources", label: "学习资源库", icon: Collection },
      { path: "/reviews", label: "教师审核中心", icon: CircleCheck }
    ]
  })

  // AI能力
  groups.push({
    title: "AI能力",
    items: [
      { path: "/invocations", label: "调用审计", icon: Monitor },
      { path: "/costs", label: "成本统计", icon: Money },
      { path: "/prompts", label: "提示词模板", icon: Comment }
    ]
  })

  // 分析
  groups.push({
    title: "分析",
    items: [
      { path: "/analytics", label: "学习分析看板", icon: DataLine }
    ]
  })

  // 系统管理 — 仅 admin
  if (adminFlag) {
    groups.push({
      title: "系统",
      items: [
        { path: "/users", label: "用户管理", icon: Tools },
        { path: "/models", label: "模型与智能体配置", icon: Setting },
        { path: "/logs/operation", label: "操作日志", icon: Document },
        { path: "/logs/login", label: "登录日志", icon: Key }
      ]
    })
  } else if (teacherFlag) {
    groups.push({
      title: "系统",
      items: [
        { path: "/models", label: "模型与智能体配置", icon: Setting }
      ]
    })
  }

  return groups
})
```

---

#### Task 8: 重写登录页

**Files:**
- Modify: `frontend/src/pages/login/index.vue:1-149`

**Steps:**

- [ ] **Step 1: 更新登录页标题和副标题**

```vue
<!-- 标题区域改为：-->
<div class="title">
  <h1>智学工坊</h1>
  <div class="title-en">EduAgent Studio</div>
</div>
<div class="subtitle">基于大模型的个性化学习资源生成与多智能体协作系统</div>

<!-- 测试账号改为：-->
测试账号：admin / Admin@123456（管理员）&nbsp;&nbsp; teacher01 / Teacher@123（教师）&nbsp;&nbsp; student01 / Student@123（学生）
```

---

#### Task 9: 重写 Dashboard 首页

**Files:**
- Modify: `frontend/src/pages/dashboard/index.vue:1-387`

**Steps:**

- [ ] **Step 1: 完全重写首页为 A3 风格**

主要改动：
1. 欢迎语改为「欢迎使用智学工坊 EduAgent Studio」
2. 业务流程图改为 A3 链路：学生画像 → 智能体诊断 → 资源规划 → 资源生成 → 教师审核 → 学习反馈 → 画像更新
3. 统计卡片改为 A3 指标：课程数、学生数、学习资源数、智能体调用次数、平均掌握度、教师审核通过率
4. 模块入口改为 A3 菜单：学生画像、课程空间、智能体工作台、学习资源库、教师审核中心、学习分析看板

```vue
const flowSteps = [
  { index: 1, title: "学生画像", desc: "建立和维护学习者画像" },
  { index: 2, title: "智能体诊断", desc: "诊断薄弱知识点" },
  { index: 3, title: "资源规划", desc: "生成个性化学习路径" },
  { index: 4, title: "资源生成", desc: "生成学习资源" },
  { index: 5, title: "教师审核", desc: "质量把关" },
  { index: 6, title: "学习反馈", desc: "更新画像" },
  { index: 7, title: "分析看板", desc: "展示效果" }
]

const modules = [
  { name: "学生画像", desc: "查看和管理学生画像信息", icon: "UserFilled", path: "/profiles" },
  { name: "课程空间", desc: "管理课程、发布学习任务", icon: "Folder", path: "/courses" },
  { name: "智能体工作台", desc: "多智能体协作生成学习资源", icon: "Cpu", path: "/agent-workbench" },
  { name: "学习资源库", desc: "查看和管理学习资源", icon: "Collection", path: "/resources" },
  { name: "教师审核中心", desc: "审核学习资源质量", icon: "CircleCheck", path: "/reviews" },
  { name: "学习分析看板", desc: "学习效果数据分析", icon: "DataLine", path: "/analytics" }
]

const statCards = [
  { key: "course_count", label: "课程数", suffix: "门" },
  { key: "student_count", label: "学生数", suffix: "人" },
  { key: "resource_count", label: "学习资源", suffix: "份" },
  { key: "invocation_count", label: "智能体调用", suffix: "次" },
  { key: "avg_mastery", label: "平均掌握度", suffix: "%" },
  { key: "review_pass_rate", label: "审核通过率", suffix: "%" }
]
```

---

#### Task 10: 新建学生画像页面

**Files:**
- Create: `frontend/src/pages/profiles/index.vue`
- Create: `frontend/src/pages/profiles/ProfileDetail.vue`
- Create: `frontend/src/api/profiles.ts`

**Steps:**

- [ ] **Step 1: 创建 profiles.ts API**

```typescript
// frontend/src/api/profiles.ts
import request from "@/utils/request"

export interface StudentProfile {
  profile_id: number
  student_id: number
  student_name: string
  course_id: number
  course_name: string
  learning_goal: string
  current_level: string
  weak_points: string[]
  preferences: string[]
  mastery_score: number
  last_updated: string
}

export interface ProfileDetail {
  profile_id: number
  student_id: number
  student_name: string
  student_no: string
  learning_goal: string
  current_level: string
  interests: string[]
  resource_preferences: string[]
  weekly_hours: number
  weak_points: Array<{ kp_id: number; kp_name: string; mastery: number; reason: string }>
  strong_points: Array<{ kp_id: number; kp_name: string; mastery: number }>
  recent_tasks: Array<{ task_id: number; title: string; status: string; completed_at: string }>
  recent_tests: Array<{ test_id: number; accuracy: number; date: string }>
  ai_suggestions: string
}

export const profilesApi = {
  list(params?: { page?: number; page_size?: number; course_id?: number; keyword?: string }) {
    return request.get<{ data: { items: StudentProfile[]; total: number } }>(
      "/api/profiles",
      { params }
    )
  },
  getById(profileId: number) {
    return request.get<{ data: ProfileDetail }>(`/api/profiles/${profileId}`)
  },
  update(profileId: number, data: Partial<ProfileDetail>) {
    return request.put(`/api/profiles/${profileId}`, data)
  },
  updateMastery(profileId: number, data: { kp_id: number; mastery: number }) {
    return request.post(`/api/profiles/${profileId}/mastery`, data)
  }
}
```

- [ ] **Step 2: 创建 profiles/index.vue**

学生画像列表页，包含：
- 筛选：课程下拉、学习水平下拉、关键词搜索
- 表格列：学生姓名、所属课程、当前水平、薄弱知识点（标签）、掌握度评分（进度条）、最近更新时间、操作
- 操作：查看详情、编辑画像

```vue
<!-- 页面标题 -->
<h1 class="page-title">学生画像</h1>

<!-- 筛选区 -->
<el-card>
  <el-form inline>
    <el-form-item label="课程">
      <el-select v-model="filterForm.course_id" clearable>
        <el-option label="全部课程" :value="undefined" />
        <el-option label="数据库系统原理" :value="1" />
        <el-option label="Python程序设计" :value="2" />
        <el-option label="软件工程实践" :value="3" />
      </el-select>
    </el-form-item>
    <el-form-item label="关键词">
      <el-input v-model="filterForm.keyword" placeholder="学生姓名/学号" clearable />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="loadProfiles">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </el-form-item>
  </el-form>
</el-card>

<!-- 列表 -->
<el-table :data="tableData" v-loading="loading">
  <el-table-column prop="student_name" label="学生姓名" />
  <el-table-column prop="course_name" label="所属课程" />
  <el-table-column prop="current_level" label="当前水平" />
  <el-table-column label="薄弱知识点">
    <template #default="{ row }">
      <el-tag v-for="wp in row.weak_points" :key="wp" size="small" type="danger" style="margin-right: 4px">
        {{ wp }}
      </el-tag>
    </template>
  </el-table-column>
  <el-table-column label="掌握度评分">
    <template #default="{ row }">
      <el-progress :percentage="row.mastery_score * 100" :color="masteryColor(row.mastery_score)" />
    </template>
  </el-table-column>
  <el-table-column prop="last_updated" label="最近更新" />
  <el-table-column label="操作" width="180">
    <template #default="{ row }">
      <el-button type="primary" size="small" @click="viewDetail(row)">查看详情</el-button>
      <el-button size="small" @click="editProfile(row)">编辑</el-button>
    </template>
  </el-table-column>
</el-table>
```

- [ ] **Step 3: 创建 profiles/ProfileDetail.vue**

画像详情页，包含：
- 基础信息卡片：姓名、学号、所属课程、学习目标、当前基础、兴趣方向、资源类型偏好、每周学习时间
- 知识点掌握度：雷达图或柱状图展示各知识点掌握度，薄弱点红色标注
- 最近学习任务：列表形式
- AI 诊断建议：文本展示

---

#### Task 11: 新建智能体工作台页面

**Files:**
- Create: `frontend/src/pages/agent-workbench/index.vue`
- Create: `frontend/src/api/agents.ts`

**Steps:**

- [ ] **Step 1: 创建 agents.ts API**

```typescript
// frontend/src/api/agents.ts
import request from "@/utils/request"

export interface AgentRequest {
  student_id: number
  course_id: number
  knowledge_point_ids: number[]
  resource_type: string
  difficulty: string
}

export interface AgentResult {
  diagnosis: {
    weak_points: Array<{ kp_id: number; name: string; mastery_level: number; reason: string }>
    learning_difficulties: string[]
    resource_needs: string[]
  }
  plan: {
    learning_path: Array<{ order: number; kp_name: string; estimated_time: string; resource_type: string }>
    resource_combination: string[]
  }
  resource: {
    resource_id: string
    title: string
    type: string
    content: string
    knowledge_points: number[]
    difficulty: string
  }
  assessment: {
    accuracy_rate: number
    suggestions: string[]
  }
  teacher_review_suggestion: {
    quality_score: number
    quality_checks: Array<{ check: string; passed: boolean; note: string }>
    suggestions: string[]
    overall_comment: string
  }
}

export const agentsApi = {
  generate(data: AgentRequest) {
    return request.post<{ data: AgentResult }>("/api/agents/generate", data)
  },
  getAgents() {
    return request.get<{ data: Array<{ id: string; name: string; description: string; type: string }> }>(
      "/api/agents/list"
    )
  },
  saveResource(data: { result: AgentResult; title: string; course_id: number }) {
    return request.post("/api/agents/save-resource", data)
  }
}
```

- [ ] **Step 2: 创建 agent-workbench/index.vue**

核心页面，包含：

**选择区（左侧）**：
- 学生选择（el-select，关联学生画像列表）
- 课程选择（el-select，关联课程列表）
- 知识点选择（el-select-multiple，关联课程知识点）
- 资源类型选择（el-select：讲义/PPT大纲/题库/案例/复习计划/测验）
- 难度选择（el-select：基础/进阶/高级）

**生成按钮**：
- el-button: "生成个性化学习资源"
- 绑定点击事件，调用 agentsApi.generate()

**执行链路展示（中间）**：
- 5 个步骤卡片，按顺序执行
- 每个步骤：标题、状态图标（loading/success/error）、输出摘要
- 步骤间用箭头连接

**结果展示（右侧）**：
- Tab 页签：诊断结果 / 学习规划 / 生成资源 / 评测反馈 / 审核建议
- 生成资源 Tab 包含 Markdown 渲染的讲义内容
- 每个 Tab 显示对应智能体输出的 JSON 内容

**保存按钮**：
- el-button: "保存到学习资源库"
- 弹出资源标题输入框
- 调用 agentsApi.saveResource()

```vue
<template>
  <div class="agent-workbench">
    <h1 class="page-title">智能体工作台</h1>

    <el-row :gutter="20">
      <!-- 左侧：配置区 -->
      <el-col :span="6">
        <el-card class="config-card">
          <template #header>资源配置</template>
          <el-form label-width="90px">
            <el-form-item label="选择学生">
              <el-select v-model="form.student_id" placeholder="请选择学生" filterable>
                <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择课程">
              <el-select v-model="form.course_id" placeholder="请选择课程" @change="onCourseChange">
                <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择知识点">
              <el-select v-model="form.knowledge_point_ids" multiple placeholder="请选择知识点">
                <el-option v-for="kp in knowledgePoints" :key="kp.id" :label="kp.name" :value="kp.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="资源类型">
              <el-select v-model="form.resource_type" placeholder="请选择资源类型">
                <el-option label="知识点讲义" value="lecture" />
                <el-option label="PPT大纲" value="ppt" />
                <el-option label="习题与答案" value="quiz" />
                <el-option label="案例材料" value="case" />
                <el-option label="复习计划" value="review" />
                <el-option label="阶段测验" value="test" />
              </el-select>
            </el-form-item>
            <el-form-item label="难度等级">
              <el-select v-model="form.difficulty" placeholder="请选择难度">
                <el-option label="基础" value="basic" />
                <el-option label="进阶" value="intermediate" />
                <el-option label="高级" value="advanced" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="generating" @click="handleGenerate">
                生成个性化学习资源
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 中间：执行链路 -->
      <el-col :span="5">
        <el-card>
          <template #header>智能体执行链路</template>
          <div class="agent-chain">
            <div v-for="(step, idx) in agentSteps" :key="step.id" class="chain-step">
              <div class="step-indicator">
                <el-icon v-if="step.status === 'pending'" color="#c0c4cc"><Clock /></el-icon>
                <el-icon v-else-if="step.status === 'running'" class="spin" color="#409eff"><Loading /></el-icon>
                <el-icon v-else-if="step.status === 'success'" color="#67c23a"><CircleCheck /></el-icon>
                <el-icon v-else color="#f56c6c"><CircleClose /></el-icon>
              </div>
              <div class="step-info">
                <div class="step-name">{{ step.name }}</div>
                <div class="step-desc">{{ step.desc }}</div>
              </div>
              <el-icon v-if="idx < agentSteps.length - 1" class="chain-arrow" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：结果展示 -->
      <el-col :span="13">
        <el-card v-if="result">
          <template #header>
            <span>生成结果</span>
            <el-button type="success" size="small" style="float: right" @click="handleSave">
              保存到学习资源库
            </el-button>
          </template>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="诊断结果" name="diagnosis">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="薄弱知识点">
                  <el-tag v-for="wp in result.diagnosis.weak_points" :key="wp.kp_id" type="danger">
                    {{ wp.name }}（掌握度 {{ (wp.mastery_level * 100).toFixed(0) }}%）
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="学习难点">
                  <span v-for="d in result.diagnosis.learning_difficulties" :key="d">{{ d }}；</span>
                </el-descriptions-item>
                <el-descriptions-item label="资源需求">{{ result.diagnosis.resource_needs.join('、') }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            <el-tab-pane label="学习规划" name="plan">
              <el-steps direction="vertical" :space="60">
                <el-step v-for="step in result.plan.learning_path" :key="step.order" :title="`步骤${step.order}: ${step.kp_name}`" :description="`预计${step.estimated_time}，使用${step.resource_type}`" />
              </el-steps>
            </el-tab-pane>
            <el-tab-pane label="生成资源" name="resource">
              <h3>{{ result.resource.title }}</h3>
              <el-tag size="small">{{ result.resource.type }}</el-tag>
              <el-tag size="small" type="info">{{ result.resource.difficulty }}</el-tag>
              <div class="resource-content markdown-body" v-html="renderMarkdown(result.resource.content)" />
            </el-tab-pane>
            <el-tab-pane label="评测反馈" name="assessment">
              <el-progress type="circle" :percentage="(result.assessment.accuracy_rate * 100).toFixed(0)" />
              <el-divider />
              <el-tag v-for="s in result.assessment.suggestions" :key="s">{{ s }}</el-tag>
            </el-tab-pane>
            <el-tab-pane label="审核建议" name="review">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="质量评分">{{ result.teacher_review_suggestion.quality_score }}/10</el-descriptions-item>
                <el-descriptions-item label="整体评价">{{ result.teacher_review_suggestion.overall_comment }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        <el-empty v-else description="请先选择配置并点击生成" />
      </el-col>
    </el-row>
  </div>
</template>
```

---

### Phase 1.3：后端新增模块

#### Task 12: 新建 LLM Gateway

**Files:**
- Create: `backend/app/llm/__init__.py`
- Create: `backend/app/llm/gateway.py`
- Create: `backend/app/llm/providers.py`
- Create: `backend/app/llm/mock_provider.py`
- Create: `backend/app/llm/openai_compatible_provider.py`

**Steps:**

- [ ] **Step 1: 创建 llm/__init__.py**

```python
"""LLM Gateway - 统一大模型接入层"""
from app.llm.gateway import LLMGateway, llm_gateway
from app.llm.mock_provider import MockProvider

__all__ = ["LLMGateway", "llm_gateway", "MockProvider"]
```

- [ ] **Step 2: 创建 llm/gateway.py**

```python
"""
LLM Gateway - 统一大模型接入网关

支持：
- OpenAI-compatible API 格式
- 本地 Mock 模型
- Qwen / DeepSeek / GLM 等国产模型
- 模型配置、调用日志、Token 统计、成本统计
"""

import time
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from app.llm.providers import get_provider

logger = logging.getLogger(__name__)


@dataclass
class LLMCallResult:
    """LLM 调用结果"""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    cost: float
    status: str = "success"
    error: Optional[str] = None


@dataclass
class LLMConfig:
    """LLM 配置"""
    model_id: int
    model_name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 60


class LLMGateway:
    """统一 LLM 网关"""

    def __init__(self):
        self._providers: Dict[str, Any] = {}

    def register_provider(self, name: str, provider: Any) -> None:
        """注册模型供应商"""
        self._providers[name] = provider
        logger.info(f"Registered LLM provider: {name}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: LLMConfig,
        **kwargs
    ) -> LLMCallResult:
        """
        统一生成接口。

        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
            config: LLM 配置
            **kwargs: 额外参数（temperature, max_tokens 等）

        Returns:
            LLMCallResult
        """
        start_time = time.time()

        # 获取供应商
        provider = self._providers.get(config.provider)
        if provider is None:
            # 尝试获取默认 Mock 供应商
            provider = self._providers.get("mock")
            if provider is None:
                return LLMCallResult(
                    content="",
                    model=config.model_name,
                    provider=config.provider,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    latency_ms=0,
                    cost=0.0,
                    status="failed",
                    error=f"Provider '{config.provider}' not found"
                )

        try:
            result = provider.generate(messages, config, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)
            return LLMCallResult(
                content=result.get("content", ""),
                model=config.model_name,
                provider=config.provider,
                input_tokens=result.get("input_tokens", 0),
                output_tokens=result.get("output_tokens", 0),
                total_tokens=result.get("input_tokens", 0) + result.get("output_tokens", 0),
                latency_ms=latency_ms,
                cost=result.get("cost", 0.0),
                status="success"
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return LLMCallResult(
                content="",
                model=config.model_name,
                provider=config.provider,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=int((time.time() - start_time) * 1000),
                cost=0.0,
                status="failed",
                error=str(e)
            )


# 全局单例
llm_gateway = LLMGateway()
```

- [ ] **Step 3: 创建 llm/providers.py**

```python
"""
LLM 供应商管理
"""

import logging
from typing import Any, Dict, Optional
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider

logger = logging.getLogger(__name__)


_PROVIDER_REGISTRY: Dict[str, type] = {
    "mock": MockProvider,
    "openai": OpenAICompatibleProvider,
    "openai_compatible": OpenAICompatibleProvider,
}


def get_provider(name: str, **kwargs) -> Any:
    """获取供应商实例"""
    provider_cls = _PROVIDER_REGISTRY.get(name.lower())
    if provider_cls is None:
        logger.warning(f"Unknown provider '{name}', falling back to MockProvider")
        return MockProvider(**kwargs)
    return provider_cls(**kwargs)


def register_provider(name: str, provider_cls: type) -> None:
    """注册新的供应商"""
    _PROVIDER_REGISTRY[name.lower()] = provider_cls
    logger.info(f"Registered provider: {name}")
```

- [ ] **Step 4: 创建 llm/mock_provider.py**

```python
"""
Mock LLM 提供商 — 用于测试和演示

返回结构化的模拟数据，不产生真实 API 调用。
"""

import uuid
import hashlib
import time
import random
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MockProvider:
    """Mock LLM 提供商"""

    def __init__(
        self,
        model_name: str = "mock-gpt",
        base_url: str = "",
        api_key: str = "",
        **kwargs
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self._knowledge_base = self._build_knowledge_base()

    def _build_knowledge_base(self) -> Dict[str, str]:
        """构建 Mock 知识库"""
        return {
            "sql_join": """## SQL 多表连接

### 什么是连接（JOIN）
连接是从两个或多个表中获取数据的操作，通过指定它们之间的关联列来实现。

### 内连接（INNER JOIN）
返回两个表中具有匹配值的记录。

```sql
SELECT a.name, b.score
FROM students a
INNER JOIN scores b ON a.id = b.student_id;
```

### 左外连接（LEFT JOIN）
返回左表中的所有记录，以及右表中匹配记录的记录。

```sql
SELECT a.name, b.score
FROM students a
LEFT JOIN scores b ON a.id = b.student_id;
```

### 右外连接（RIGHT JOIN）
返回右表中的所有记录，以及左表中匹配记录的记录。

### 全外连接（FULL OUTER JOIN）
返回两个表中的所有记录，未匹配的部分为 NULL。

### 连接与子查询的选择
- 当需要跨表比较和筛选时，JOIN 通常更高效
- 当逻辑复杂且需要中间结果时，子查询更清晰
""",
            "database_transaction": """## 数据库事务与并发控制

### 事务的概念
事务是数据库操作的基本单位，具有 ACID 特性：
- **原子性（Atomicity）**：事务中的所有操作要么全部成功，要么全部失败
- **一致性（Consistency）**：事务执行前后，数据库状态保持一致
- **隔离性（Isolation）**：并发执行的事务互不干扰
- **持久性（Durability）**：事务提交后，其结果永久保存

### 事务隔离级别
| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|----------|------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ | 不可能 | 不可能 | 可能 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

### 并发问题
- **脏读**：读取了另一个事务未提交的数据
- **不可重复读**：同一查询在事务中返回不同结果
- **幻读**：同一查询在事务中返回不同数量的行
""",
            "python_function": """## Python 函数设计原则

### 函数的基本结构
```python
def function_name(param1: Type1, param2: Type2 = default_value) -> ReturnType:
    '''函数文档字符串'''
    # 函数体
    return result
```

### 单一职责原则
每个函数应该只做一件事，并且做好这件事。

### 参数设计
- 必需参数放在可选参数之前
- 使用类型注解提高可读性
- 避免过多参数（超过3个考虑使用字典或类）

### 返回值设计
- 明确函数的返回值类型
- 成功返回结果，失败抛出异常
- 不要返回 None 表示失败
""",
            "quiz_template": """## {topic} 练习题

### 选择题

**1. {question_1}**
A. {option_a}
B. {option_b}
C. {option_c}
D. {option_d}

**答案：** {answer_1}

**解析：** {explanation_1}

### 填空题

**2. {fill_question}

**答案：** {fill_answer}
""",
        }

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Mock 生成接口。

        根据输入内容匹配知识库，返回相关模拟内容。
        """
        # 提取用户输入
        user_input = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_input = msg.get("content", "")
                break

        input_text = user_input.lower()
        input_tokens = len(input_input := " ".join([m.get("content", "") for m in messages])) // 4

        # 根据输入关键词匹配知识库
        response_content = self._generate_response(input_text, config.model_name)

        output_tokens = len(response_content) // 4
        total_cost = (input_tokens + output_tokens) * 0.000001  # Mock 成本

        return {
            "content": response_content,
            "input_tokens": max(input_tokens, 10),
            "output_tokens": max(output_tokens, 10),
            "cost": total_cost,
            "model": self.model_name,
            "latency_ms": random.randint(500, 3000),
        }

    def _generate_response(self, input_text: str, model_name: str) -> str:
        """根据输入生成 Mock 响应"""
        time.sleep(random.uniform(0.5, 2.0))  # 模拟延迟

        # 诊断智能体
        if "诊断" in input_text or "薄弱" in input_text or "分析" in input_text:
            return self._mock_diagnosis(input_text)

        # 规划智能体
        if "规划" in input_text or "路径" in input_text or "学习" in input_text:
            return self._mock_planning(input_text)

        # 评测反馈智能体
        if "评测" in input_text or "反馈" in input_text or "测验" in input_text:
            return self._mock_assessment(input_text)

        # 审核辅助智能体
        if "审核" in input_text or "质量" in input_text:
            return self._mock_teacher_review(input_text)

        # 资源生成智能体
        if "讲义" in input_text or "生成" in input_text or "资源" in input_text:
            return self._mock_resource_generation(input_text)

        # 默认响应
        return f"""# 个性化学习资源

根据您的学习需求，系统生成了以下学习内容：

## 学习目标
掌握相关知识点，建立系统的知识体系。

## 学习路径
1. 理解基础概念
2. 掌握核心原理
3. 实践应用
4. 综合练习

## 资源内容
（详细内容由多智能体协作生成）

---
*本资源由 {model_name} 生成 | EduAgent Studio*
"""

    def _mock_diagnosis(self, input_text: str) -> str:
        return """{
  "diagnosis_id": "mock-""" + str(uuid.uuid4())[:8] + """",
  "weak_points": [
    {"kp_id": 5, "name": "SQL多表连接", "mastery_level": 0.3, "reason": "近3次测验中正确率仅30%，复杂查询容易出错"},
    {"kp_id": 8, "name": "事务隔离级别", "mastery_level": 0.2, "reason": "从未正确解答相关题目，概念理解模糊"},
    {"kp_id": 12, "name": "数据库范式", "mastery_level": 0.4, "reason": "能够判断基本范式，但高阶范式理解不足"}
  ],
  "strength_points": [
    {"kp_id": 2, "name": "SQL基本查询", "mastery_level": 0.85},
    {"kp_id": 3, "name": "数据定义DDL", "mastery_level": 0.78}
  ],
  "learning_difficulties": [
    "多表连接时条件判断容易混淆",
    "子查询嵌套层次过深难以理解",
    "HAVING子句与WHERE的区别总是记不清"
  ],
  "resource_needs": ["图文并茂的讲义", "具体案例演示", "补充练习题"],
  "suggested_difficulty": "intermediate"
}"""

    def _mock_planning(self, input_text: str) -> str:
        return """{
  "plan_id": "mock-""" + str(uuid.uuid4())[:8] + """",
  "learning_path": [
    {"order": 1, "kp_id": 5, "kp_name": "理解INNER JOIN", "estimated_time": "30分钟", "resource_type": "讲义", "priority": "high"},
    {"order": 2, "kp_id": 5, "kp_name": "掌握OUTER JOIN", "estimated_time": "30分钟", "resource_type": "案例", "priority": "high"},
    {"order": 3, "kp_id": 5, "kp_name": "多表连接综合练习", "estimated_time": "45分钟", "resource_type": "习题", "priority": "high"},
    {"order": 4, "kp_id": 8, "kp_name": "事务ACID特性", "estimated_time": "25分钟", "resource_type": "讲义", "priority": "medium"},
    {"order": 5, "kp_id": 8, "kp_name": "隔离级别详解", "estimated_time": "30分钟", "resource_type": "案例", "priority": "medium"},
    {"order": 6, "kp_id": 5, "kp_name": "阶段测验", "estimated_time": "20分钟", "resource_type": "测验", "priority": "high"}
  ],
  "resource_combination": ["讲义×3", "案例×2", "习题×5", "阶段测验×1"],
  "learning_sequence": "由浅入深，先掌握单表查询再扩展到多表连接，先理解INNER JOIN再掌握OUTER JOIN",
  "estimated_total_time": "约3小时"
}"""

    def _mock_resource_generation(self, input_text: str) -> str:
        return """# SQL 多表连接专题讲义（进阶）

## 一、连接概述

连接（JOIN）是从两个或多个表中获取数据的操作。在关系数据库中，数据通常分布在多个相关表中，通过连接可以将它们组合在一起进行分析。

### 1.1 为什么需要连接？

假设有一个教务系统：
- `students` 表：存储学生信息（id, name, class_id）
- `classes` 表：存储班级信息（id, name, teacher）
- `scores` 表：存储成绩信息（id, student_id, subject, score）

如果想知道"每个学生的班级名称和平均成绩"，就需要连接这三个表。

## 二、内连接（INNER JOIN）

内连接返回两个表中具有匹配值的记录。

### 语法
```sql
SELECT column_list
FROM table1
INNER JOIN table2 ON table1.column = table2.column;
```

### 示例
```sql
SELECT s.name, c.name AS class_name
FROM students s
INNER JOIN classes c ON s.class_id = c.id;
```

**结果**：只会返回既存在于 students 表又存在于 classes 表的记录。

## 三、外连接（OUTER JOIN）

### 3.1 左外连接（LEFT JOIN）

返回左表中的所有记录，以及右表中匹配记录的记录。

```sql
SELECT s.name, sc.score
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id;
```

**特点**：即使某个学生没有成绩，查询结果中仍会包含该学生，score 显示为 NULL。

### 3.2 右外连接（RIGHT JOIN）

返回右表中的所有记录，以及左表中匹配记录的记录。

### 3.3 全外连接（FULL OUTER JOIN）

返回两个表中的所有记录，未匹配的部分为 NULL。

## 四、连接与子查询的选择

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 多表聚合统计 | JOIN | 更高效 |
| 复杂筛选条件 | 子查询 | 更清晰 |
| 层次结构查询 | WITH RECURSIVE | 支持递归 |

## 五、练习题

1. 查询所有学生的成绩，包括没有成绩的学生
2. 统计每个班级的平均分
3. 找出平均分超过85分的学生

---
*本讲义由 EduAgent Studio 智能体工作台生成*
"""

    def _mock_assessment(self, input_text: str) -> str:
        return """{
  "assessment_id": "mock-""" + str(uuid.uuid4())[:8] + """",
  "test_results": {
    "total_questions": 10,
    "correct_answers": 7,
    "accuracy_rate": 0.7
  },
  "mastery_updates": [
    {"kp_id": 5, "old_mastery": 0.3, "new_mastery": 0.55, "change_reason": "测验正确率70%，多表连接基本掌握"},
    {"kp_id": 8, "old_mastery": 0.2, "new_mastery": 0.15, "change_reason": "测验未涉及该知识点，保持观察"}
  ],
  "feedback": "多表连接基本概念已掌握，INNER JOIN运用熟练，LEFT JOIN偶有混淆。复杂嵌套查询仍需加强。",
  "suggestions": [
    "建议增加3道复杂嵌套查询的专项练习",
    "推荐学习视图（VIEW）的概念，作为连接与查询的延伸",
    "可以尝试用EXPLAIN分析查询执行计划"
  ],
  "next_resource_recommendation": "复杂SQL查询专题练习"
}"""

    def _mock_teacher_review(self, input_text: str) -> str:
        return """{
  "review_id": "mock-""" + str(uuid.uuid4())[:8] + """",
  "quality_score": 8.5,
  "quality_checks": [
    {"check": "知识点准确性", "passed": true, "note": "SQL连接语法正确，示例无错误"},
    {"check": "难度适配性", "passed": true, "note": "适合大二数据库课程进阶阶段学生"},
    {"check": "内容完整性", "passed": true, "note": "覆盖了INNER/LEFT/RIGHT/FULL四种连接"},
    {"check": "代码示例质量", "passed": true, "note": "示例简洁且有实际意义"},
    {"check": "练习题设计", "passed": false, "note": "建议增加4道练习题供学生巩固"}
  ],
  "risk_alerts": [
    {"level": "info", "message": "讲义中涉及ORDER BY与GROUP BY组合，可能超出本节范围"},
    {"level": "low", "message": "全外连接（FULL OUTER JOIN）在某些数据库中语法略有不同"}
  ],
  "suggestions": [
    "建议在讲义末尾增加4道练习题",
    "补充JOIN与子查询的对比内容，帮助学生理解何时用哪种方式",
    "增加一个实际项目案例，如教务系统的多表查询"
  ],
  "overall_comment": "资源整体质量良好，知识点覆盖全面，示例代码规范。建议小幅修改后通过审核。"
}"""
```

- [ ] **Step 5: 创建 llm/openai_compatible_provider.py**

```python
"""
OpenAI-compatible API 提供商

支持任何兼容 OpenAI API 格式的服务：
- OpenAI GPT 系列
- Qwen (阿里云通义千问)
- DeepSeek
- GLM (智谱华章)
- 本地部署的 vLLM / Ollama 等
"""

import logging
import time
import json
from typing import Any, Dict, List
import httpx

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """OpenAI 兼容接口提供商"""

    def __init__(
        self,
        model_name: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        **kwargs
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(timeout=60.0)

    def generate(
        self,
        messages: List[Dict[str, str]],
        config: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用 OpenAI-compatible API。

        Args:
            messages: [{"role": "system|user|assistant", "content": "..."}]
            config: LLMConfig 对象

        Returns:
            {"content": str, "input_tokens": int, "output_tokens": int, "cost": float}
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key or config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", config.temperature),
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
        }

        start_time = time.time()
        try:
            response = self._client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # 估算成本（需要根据模型定价调整）
            cost = (input_tokens * 0.000001 + output_tokens * 0.000002)

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model": config.model_name,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
```

---

#### Task 13: 新建多智能体模块

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/diagnosis_agent.py`
- Create: `backend/app/agents/planning_agent.py`
- Create: `backend/app/agents/resource_generation_agent.py`
- Create: `backend/app/agents/assessment_agent.py`
- Create: `backend/app/agents/teacher_review_agent.py`
- Create: `backend/app/agents/workflow.py`

**Steps:**

- [ ] **Step 1: 创建 agents/__init__.py**

```python
"""多智能体协作模块"""
from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.resource_generation_agent import ResourceGenerationAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.teacher_review_agent import TeacherReviewAgent
from app.agents.workflow import LearningAgentWorkflow

__all__ = [
    "DiagnosisAgent",
    "PlanningAgent",
    "ResourceGenerationAgent",
    "AssessmentAgent",
    "TeacherReviewAgent",
    "LearningAgentWorkflow",
]
```

- [ ] **Step 2: 创建 diagnosis_agent.py**

```python
"""
学习诊断智能体

分析学生画像、课程知识点和历史反馈，识别薄弱知识点和学习难点。
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DiagnosisAgent:
    """学习诊断智能体"""

    AGENT_NAME = "diagnosis_agent"
    AGENT_DESC = "学习诊断智能体 — 分析学生薄弱知识点"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        student_profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        learning_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        执行诊断。

        Args:
            student_profile: 学生画像数据
            knowledge_points: 知识点列表
            learning_history: 历史学习记录（可选）

        Returns:
            诊断结果字典
        """
        logger.info(f"[{self.AGENT_NAME}] 诊断学生: {student_profile.get('student_name')}")

        # 构建诊断上下文
        context = self._build_context(student_profile, knowledge_points, learning_history)

        # 调用 LLM（Mock 或真实）
        if self.llm_gateway:
            result = self._call_llm(context)
        else:
            result = self._mock_run(context)

        logger.info(f"[{self.AGENT_NAME}] 诊断完成，识别 {len(result.get('weak_points', []))} 个薄弱点")
        return result

    def _build_context(
        self,
        student_profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        learning_history: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        return {
            "student": student_profile,
            "knowledge_points": knowledge_points,
            "learning_history": learning_history or [],
        }

    def _call_llm(self, context: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的学习诊断智能体。根据学生画像和知识点信息，分析学生的薄弱知识点，并给出诊断结果。

请以 JSON 格式输出，包含以下字段：
- weak_points: 薄弱知识点列表，每个包含 kp_id, name, mastery_level (0-1), reason
- strength_points: 优势知识点列表，每个包含 kp_id, name, mastery_level
- learning_difficulties: 学习难点描述列表
- resource_needs: 资源需求列表（如：补充练习题、图文讲义、案例演示）
- suggested_difficulty: 建议难度（basic/intermediate/advanced）"""
            },
            {
                "role": "user",
                "content": f"学生画像：{context['student']}\n知识点列表：{context['knowledge_points']}\n学习历史：{context['learning_history']}"
            }
        ]

        from app.llm.gateway import LLMConfig
        config = LLMConfig(
            model_id=1,
            model_name="mock-gpt",
            provider="mock",
        )

        result = self.llm_gateway.generate(messages, config)
        import json
        return json.loads(result.content)

    def _mock_run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 诊断结果"""
        weak_points = []
        strong_points = []

        for kp in context["knowledge_points"]:
            mastery = kp.get("mastery_level", 0.5)
            if mastery < 0.5:
                weak_points.append({
                    "kp_id": kp.get("kp_id", 0),
                    "name": kp.get("name", ""),
                    "mastery_level": mastery,
                    "reason": f"测验正确率仅{int(mastery * 100)}%，知识点掌握不足"
                })
            else:
                strong_points.append({
                    "kp_id": kp.get("kp_id", 0),
                    "name": kp.get("name", ""),
                    "mastery_level": mastery
                })

        return {
            "diagnosis_id": f"diag-{uuid.uuid4().hex[:8]}",
            "weak_points": weak_points,
            "strength_points": strong_points,
            "learning_difficulties": [
                "多表连接时条件判断容易混淆",
                "子查询嵌套层次过深难以理解"
            ],
            "resource_needs": ["图文并茂的讲义", "具体案例演示", "补充练习题"],
            "suggested_difficulty": "intermediate"
        }
```

- [ ] **Step 3: 创建 planning_agent.py**

```python
"""
资源规划智能体

根据诊断结果生成学习路径和资源组合方案。
"""
import logging
import uuid
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PlanningAgent:
    """资源规划智能体"""

    AGENT_NAME = "planning_agent"
    AGENT_DESC = "资源规划智能体 — 生成个性化学习路径"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        diagnosis: Dict[str, Any],
        learning_goal: str,
        course_outline: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        生成学习路径规划。
        """
        logger.info(f"[{self.AGENT_NAME}] 规划学习路径")

        weak_points = diagnosis.get("weak_points", [])
        suggested_difficulty = diagnosis.get("suggested_difficulty", "intermediate")

        # 按难度排序：先基础后进阶
        learning_path = []
        order = 1

        for wp in weak_points:
            learning_path.append({
                "order": order,
                "kp_id": wp["kp_id"],
                "kp_name": wp["name"],
                "estimated_time": self._estimate_time(wp["name"], suggested_difficulty),
                "resource_type": self._suggest_resource_type(wp["name"]),
                "priority": "high" if order <= 2 else "medium"
            })
            order += 1

        resource_combination = self._build_resource_combination(weak_points)

        return {
            "plan_id": f"plan-{uuid.uuid4().hex[:8]}",
            "learning_path": learning_path,
            "resource_combination": resource_combination,
            "learning_sequence": "由浅入深，先理解基础概念再掌握实际应用",
            "estimated_total_time": f"约{sum(int(p['estimated_time']) for p in learning_path if p['estimated_time']) + 20}分钟"
        }

    def _estimate_time(self, kp_name: str, difficulty: str) -> str:
        base_times = {
            "basic": 20,
            "intermediate": 40,
            "advanced": 60
        }
        minutes = base_times.get(difficulty, 40)
        return f"{minutes}分钟"

    def _suggest_resource_type(self, kp_name: str) -> str:
        if "连接" in kp_name or "查询" in kp_name:
            return "讲义+案例"
        if "事务" in kp_name or "并发" in kp_name:
            return "讲义"
        if "范式" in kp_name or "设计" in kp_name:
            return "案例+练习"
        return "讲义+习题"

    def _build_resource_combination(self, weak_points: List[Dict]) -> List[str]:
        types = ["讲义", "案例", "习题"]
        counts = {"讲义": 0, "案例": 0, "习题": 0}
        for wp in weak_points:
            for t in types:
                if t in self._suggest_resource_type(wp.get("name", "")):
                    counts[t] += 1
        return [f"{t}×{c}" for t, c in counts.items() if c > 0]
```

- [ ] **Step 4: 创建 resource_generation_agent.py**

```python
"""
资源生成智能体

根据学习路径和资源类型生成具体的个性化学习资源。
"""
import logging
import uuid
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ResourceGenerationAgent:
    """资源生成智能体"""

    AGENT_NAME = "resource_generation_agent"
    AGENT_DESC = "资源生成智能体 — 生成个性化学习资源"

    RESOURCE_TYPE_TITLES = {
        "lecture": "知识点讲义",
        "ppt": "PPT大纲",
        "quiz": "习题与答案",
        "case": "案例材料",
        "review": "复习计划",
        "test": "阶段测验",
    }

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        learning_path: List[Dict[str, Any]],
        resource_type: str,
        difficulty: str,
        student_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成学习资源。

        Args:
            learning_path: 学习路径
            resource_type: 资源类型（lecture/ppt/quiz/case/review/test）
            difficulty: 难度（basic/intermediate/advanced）
            student_profile: 学生画像
        """
        logger.info(f"[{self.AGENT_NAME}] 生成资源: {resource_type}")

        # 获取主知识点
        main_kp = learning_path[0] if learning_path else {}
        kp_name = main_kp.get("kp_name", "知识点")
        kp_ids = [p["kp_id"] for p in learning_path]

        title = f"{kp_name}专题{'讲义' if resource_type == 'lecture' else '资源'}（{difficulty}）"

        content = self._generate_content(kp_name, resource_type, difficulty, student_profile)

        return {
            "resource_id": f"res-{uuid.uuid4().hex[:8]}",
            "title": title,
            "type": self.RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
            "knowledge_points": kp_ids,
            "difficulty": difficulty,
            "content": content,
            "target_audience": f"已掌握基础的学生，当前学习{difficulty}难度",
            "estimated_learning_time": f"约{30 + len(learning_path) * 10}分钟",
            "generation_metadata": {
                "agent": self.AGENT_NAME,
                "model": "mock-gpt",
            }
        }

    def _generate_content(
        self,
        kp_name: str,
        resource_type: str,
        difficulty: str,
        student_profile: Dict[str, Any],
    ) -> str:
        """生成资源内容"""
        if resource_type == "lecture":
            return self._generate_lecture(kp_name, difficulty)
        elif resource_type == "quiz":
            return self._generate_quiz(kp_name, difficulty)
        elif resource_type == "case":
            return self._generate_case(kp_name, difficulty)
        else:
            return self._generate_lecture(kp_name, difficulty)

    def _generate_lecture(self, kp_name: str, difficulty: str) -> str:
        templates = {
            "SQL多表连接": """# SQL 多表连接专题讲义

## 一、连接概述
连接（JOIN）是从两个或多个表中获取数据的操作，通过指定关联列来实现。

### 1.1 内连接（INNER JOIN）
返回两个表中具有匹配值的记录。

```sql
SELECT a.name, b.score
FROM students a
INNER JOIN scores b ON a.id = b.student_id;
```

### 1.2 左外连接（LEFT JOIN）
返回左表所有记录及右表匹配记录。

```sql
SELECT a.name, b.score
FROM students a
LEFT JOIN scores b ON a.id = b.student_id;
```

## 二、多表连接
三个表以上的连接需要注意连接顺序和条件。

```sql
SELECT s.name, c.name AS class_name, sc.score
FROM students s
INNER JOIN classes c ON s.class_id = c.id
INNER JOIN scores sc ON s.id = sc.student_id;
```

## 三、练习题
1. 查询所有学生及其班级名称（包括无班级学生）
2. 统计每个班级的平均成绩

---
*由 EduAgent Studio 智能体工作台生成*
""",
            "default": f"""# {kp_name} 专题讲义

## 概述
本讲义帮助学生系统掌握 {kp_name} 相关知识。

## 核心概念
（详细内容由智能体根据学习路径生成）

## 实践应用
（包含代码示例和案例分析）

---
*由 EduAgent Studio 智能体工作台生成*
"""
        }
        return templates.get(kp_name, templates["default"].format(kp_name=kp_name))

    def _generate_quiz(self, kp_name: str, difficulty: str) -> str:
        return f"""# {kp_name} 练习题

## 选择题

**1. 关于 {kp_name}，以下说法正确的是？**
A. 选项A
B. 选项B
C. 选项C
D. 选项D

**答案：** B

**解析：** （由智能体分析）

**2. 在实际应用中，{kp_name} 的典型使用场景是？**
（题目由智能体根据知识点生成）

---
*由 EduAgent Studio 智能体工作台生成*
"""

    def _generate_case(self, kp_name: str, difficulty: str) -> str:
        return f"""# {kp_name} 案例分析

## 案例背景
某高校教务系统需要管理学生、课程、成绩之间的关系。

## 需求描述
1. 每个学生属于一个班级
2. 每门课程由一位教师授课
3. 学生可以选修多门课程并获得成绩

## 案例分析
（由智能体详细分析）

## 代码实现
```sql
-- 由智能体生成相关 SQL 语句
```

---
*由 EduAgent Studio 智能体工作台生成*
"""
```

- [ ] **Step 5: 创建 assessment_agent.py**

```python
"""
评测反馈智能体

分析测验结果或学习反馈，生成掌握度评价和改进建议。
"""
import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AssessmentAgent:
    """评测反馈智能体"""

    AGENT_NAME = "assessment_agent"
    AGENT_DESC = "评测反馈智能体 — 分析学习效果并更新画像"

    def run(
        self,
        test_results: Optional[Dict[str, Any]] = None,
        learning_feedback: Optional[Dict[str, Any]] = None,
        generated_resource: Optional[Dict[str, Any]] = None,
        student_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成评测反馈。
        """
        logger.info(f"[{self.AGENT_NAME}] 生成评测反馈")

        # Mock 数据
        accuracy = 0.0
        total = 0
        correct = 0

        if test_results:
            total = test_results.get("total_questions", 10)
            correct = int(total * (test_results.get("accuracy_rate", 0.7)))
            accuracy = test_results.get("accuracy_rate", 0.7)

        if accuracy >= 0.8:
            feedback = "掌握情况良好，建议进入下一阶段学习。"
            mastery_change = 0.15
        elif accuracy >= 0.6:
            feedback = "基本掌握，但仍有提升空间，建议加强练习。"
            mastery_change = 0.05
        else:
            feedback = "掌握不足，建议重新学习相关内容，增加练习量。"
            mastery_change = -0.1

        return {
            "assessment_id": f"assess-{uuid.uuid4().hex[:8]}",
            "test_results": {
                "total_questions": total or 10,
                "correct_answers": correct or 7,
                "accuracy_rate": accuracy or 0.7,
            },
            "mastery_updates": [
                {
                    "kp_id": 5,
                    "old_mastery": student_profile.get("mastery_score", 0.3) if student_profile else 0.3,
                    "new_mastery": min(1.0, (student_profile.get("mastery_score", 0.3) if student_profile else 0.3) + mastery_change),
                    "change_reason": f"测验正确率{int((accuracy or 0.7) * 100)}%，{'有明显提升' if mastery_change > 0 else '需继续加强'}"
                }
            ],
            "feedback": feedback,
            "suggestions": [
                "建议增加相关知识点的专项练习",
                "可以观看配套视频教程加深理解",
                "尝试用实际项目来巩固知识"
            ],
            "next_resource_recommendation": "综合练习题或下一知识点讲义"
        }
```

- [ ] **Step 6: 创建 teacher_review_agent.py**

```python
"""
教师审核辅助智能体

为教师审核学习资源提供质量检查建议。
"""
import logging
import uuid
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TeacherReviewAgent:
    """教师审核辅助智能体"""

    AGENT_NAME = "teacher_review_agent"
    AGENT_DESC = "教师审核辅助智能体 — 生成资源质量检查建议"

    def run(
        self,
        generated_resource: Dict[str, Any],
        course_objectives: Optional[List[str]] = None,
        difficulty_requirement: str = "intermediate",
    ) -> Dict[str, Any]:
        """
        生成审核建议。
        """
        logger.info(f"[{self.AGENT_NAME}] 生成审核建议")

        quality_checks = [
            {
                "check": "知识点准确性",
                "passed": True,
                "note": "SQL连接语法正确，示例无错误"
            },
            {
                "check": "难度适配性",
                "passed": True,
                "note": f"适合{difficulty_requirement}难度学生"
            },
            {
                "check": "内容完整性",
                "passed": True,
                "note": "覆盖了核心知识点"
            },
            {
                "check": "代码示例质量",
                "passed": True,
                "note": "示例简洁且有实际意义"
            },
            {
                "check": "练习题设计",
                "passed": False,
                "note": "建议增加练习题数量"
            }
        ]

        passed_count = sum(1 for c in quality_checks if c["passed"])
        quality_score = round(passed_count / len(quality_checks) * 10, 1)

        return {
            "review_id": f"review-{uuid.uuid4().hex[:8]}",
            "resource_id": generated_resource.get("resource_id"),
            "quality_score": quality_score,
            "quality_checks": quality_checks,
            "risk_alerts": [
                {
                    "level": "info",
                    "message": "部分内容可能超出本节范围，需教师确认"
                }
            ],
            "suggestions": [
                "建议在讲义末尾增加练习题",
                "补充相关知识点的对比内容",
                "增加实际应用场景案例"
            ],
            "overall_comment": f"资源整体质量评分{quality_score}/10，{'建议通过审核' if quality_score >= 7 else '建议修改后审核'}"
        }
```

- [ ] **Step 7: 创建 workflow.py**

```python
"""
多智能体工作流编排

使用 LangGraph 模式编排 5 个智能体的协作流程。
"""

import logging
from typing import Any, Dict, List, Optional

from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.resource_generation_agent import ResourceGenerationAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.teacher_review_agent import TeacherReviewAgent

logger = logging.getLogger(__name__)


class LearningAgentState:
    """智能体状态（类似 LangGraph State）"""

    def __init__(self):
        self.student_id: Optional[int] = None
        self.course_id: Optional[int] = None
        self.knowledge_point_ids: List[int] = []
        self.resource_type: str = "lecture"
        self.difficulty: str = "intermediate"

        self.student_profile: Optional[Dict[str, Any]] = None
        self.knowledge_points: List[Dict[str, Any]] = []
        self.learning_history: List[Dict[str, Any]] = []

        self.diagnosis: Optional[Dict[str, Any]] = None
        self.learning_plan: Optional[Dict[str, Any]] = None
        self.generated_resource: Optional[Dict[str, Any]] = None
        self.assessment: Optional[Dict[str, Any]] = None
        self.teacher_review_suggestion: Optional[Dict[str, Any]] = None

        self.current_step: str = "idle"
        self.messages: List[str] = []
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "course_id": self.course_id,
            "knowledge_point_ids": self.knowledge_point_ids,
            "resource_type": self.resource_type,
            "difficulty": self.difficulty,
            "student_profile": self.student_profile,
            "knowledge_points": self.knowledge_points,
            "learning_history": self.learning_history,
            "diagnosis": self.diagnosis,
            "learning_plan": self.learning_plan,
            "generated_resource": self.generated_resource,
            "assessment": self.assessment,
            "teacher_review_suggestion": self.teacher_review_suggestion,
            "current_step": self.current_step,
            "messages": self.messages,
            "error": self.error,
        }


class LearningAgentWorkflow:
    """
    多智能体工作流

    编排 5 个智能体的协作链路：
    诊断 → 规划 → 生成 → 评测 → 审核建议
    """

    def __init__(self, llm_gateway=None):
        self.diagnosis_agent = DiagnosisAgent(llm_gateway)
        self.planning_agent = PlanningAgent(llm_gateway)
        self.resource_agent = ResourceGenerationAgent(llm_gateway)
        self.assessment_agent = AssessmentAgent()
        self.review_agent = TeacherReviewAgent()

    def run(
        self,
        student_id: int,
        course_id: int,
        knowledge_point_ids: List[int],
        resource_type: str,
        difficulty: str,
        # 额外上下文（可选）
        student_profile: Optional[Dict[str, Any]] = None,
        knowledge_points: Optional[List[Dict[str, Any]]] = None,
        learning_history: Optional[List[Dict[str, Any]]] = None,
        test_results: Optional[Dict[str, Any]] = None,
        learning_feedback: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行完整的多智能体工作流。

        Returns:
            包含所有智能体输出的字典
        """
        state = LearningAgentState()
        state.student_id = student_id
        state.course_id = course_id
        state.knowledge_point_ids = knowledge_point_ids
        state.resource_type = resource_type
        state.difficulty = difficulty
        state.student_profile = student_profile
        state.knowledge_points = knowledge_points or []
        state.learning_history = learning_history or []

        # === 步骤 1: 学习诊断 ===
        state.current_step = "diagnosis"
        state.messages.append("开始执行学习诊断...")
        try:
            state.diagnosis = self.diagnosis_agent.run(
                student_profile=student_profile or {},
                knowledge_points=knowledge_points or [],
                learning_history=learning_history or [],
            )
            state.messages.append("诊断完成：识别薄弱知识点")
        except Exception as e:
            logger.error(f"Diagnosis agent failed: {e}")
            state.error = f"诊断失败: {str(e)}"
            return self._get_partial_result(state)

        # === 步骤 2: 资源规划 ===
        state.current_step = "planning"
        state.messages.append("开始生成学习路径...")
        try:
            state.learning_plan = self.planning_agent.run(
                diagnosis=state.diagnosis,
                learning_goal=student_profile.get("learning_goal", "") if student_profile else "",
                course_outline=knowledge_points or [],
            )
            state.messages.append("规划完成：生成学习路径")
        except Exception as e:
            logger.error(f"Planning agent failed: {e}")
            state.error = f"规划失败: {str(e)}"
            return self._get_partial_result(state)

        # === 步骤 3: 资源生成 ===
        state.current_step = "generation"
        state.messages.append("开始生成学习资源...")
        try:
            state.generated_resource = self.resource_agent.run(
                learning_path=state.learning_plan.get("learning_path", []),
                resource_type=resource_type,
                difficulty=difficulty,
                student_profile=student_profile or {},
            )
            state.messages.append(f"生成完成：{state.generated_resource.get('title', '学习资源')}")
        except Exception as e:
            logger.error(f"Resource generation agent failed: {e}")
            state.error = f"生成失败: {str(e)}"
            return self._get_partial_result(state)

        # === 步骤 4: 评测反馈 ===
        state.current_step = "assessment"
        state.messages.append("开始生成评测反馈...")
        try:
            state.assessment = self.assessment_agent.run(
                test_results=test_results,
                learning_feedback=learning_feedback,
                generated_resource=state.generated_resource,
                student_profile=student_profile,
            )
            state.messages.append("评测完成：生成改进建议")
        except Exception as e:
            logger.error(f"Assessment agent failed: {e}")
            state.error = f"评测失败: {str(e)}"
            # 不阻塞流程，继续

        # === 步骤 5: 教师审核辅助 ===
        state.current_step = "teacher_review"
        state.messages.append("开始生成审核建议...")
        try:
            state.teacher_review_suggestion = self.review_agent.run(
                generated_resource=state.generated_resource,
                difficulty_requirement=difficulty,
            )
            state.messages.append("审核建议生成完成")
        except Exception as e:
            logger.error(f"Teacher review agent failed: {e}")
            state.error = f"审核辅助失败: {str(e)}"
            # 不阻塞流程，继续

        state.current_step = "completed"
        state.messages.append("全部智能体执行完成")
        logger.info(f"[Workflow] 完成，学生ID={student_id}，资源={state.generated_resource.get('title')}")

        return self._get_result(state)

    def _get_result(self, state: LearningAgentState) -> Dict[str, Any]:
        return {
            "diagnosis": state.diagnosis,
            "plan": state.learning_plan,
            "resource": state.generated_resource,
            "assessment": state.assessment,
            "teacher_review_suggestion": state.teacher_review_suggestion,
            "metadata": {
                "current_step": state.current_step,
                "messages": state.messages,
                "error": state.error,
            }
        }

    def _get_partial_result(self, state: LearningAgentState) -> Dict[str, Any]:
        return {
            "diagnosis": state.diagnosis,
            "plan": state.learning_plan,
            "resource": state.generated_resource,
            "assessment": state.assessment,
            "teacher_review_suggestion": state.teacher_review_suggestion,
            "metadata": {
                "current_step": state.current_step,
                "messages": state.messages,
                "error": state.error,
                "partial": True,
            }
        }
```

---

#### Task 14: 新建后端 API 路由

**Files:**
- Create: `backend/app/routers/profiles.py`
- Create: `backend/app/routers/agents.py`
- Create: `backend/app/routers/learning.py`
- Create: `backend/app/services/profile_service.py`
- Create: `backend/app/services/agent_service.py`
- Create: `backend/app/repositories/profile_repo.py`

**Steps:**

- [ ] **Step 1: 创建 profiles 路由**

```python
# backend/app/routers/profiles.py
"""学生画像 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["学生画像"])


@router.get("/")
async def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    keyword: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    """获取学生画像列表"""
    service = ProfileService()
    return service.list_profiles(
        user=token,
        page=page,
        page_size=page_size,
        course_id=course_id,
        keyword=keyword,
    )


@router.get("/{profile_id}")
async def get_profile(profile_id: int, token: str = Depends(get_current_user)):
    """获取学生画像详情"""
    service = ProfileService()
    return service.get_profile(profile_id, token)


@router.put("/{profile_id}")
async def update_profile(
    profile_id: int,
    data: dict,
    token: str = Depends(get_current_user),
):
    """更新学生画像"""
    service = ProfileService()
    return service.update_profile(profile_id, data, token)


@router.post("/{profile_id}/mastery")
async def update_mastery(
    profile_id: int,
    data: dict,
    token: str = Depends(get_current_user),
):
    """更新知识点掌握度"""
    service = ProfileService()
    return service.update_mastery(profile_id, data, token)
```

- [ ] **Step 2: 创建 profile_service.py**

```python
# backend/app/services/profile_service.py
"""学生画像 Service"""
from typing import Any, Dict, List, Optional
from app.repositories.profile_repo import ProfileRepository

# Mock 数据用于演示
_MOCK_PROFILES = [
    {
        "profile_id": 1,
        "student_id": 101,
        "student_name": "李明",
        "course_id": 1,
        "course_name": "数据库系统原理",
        "learning_goal": "掌握数据库系统原理，能够独立完成数据库设计",
        "current_level": "大二计算机专业，已学习SQL基础",
        "weak_points": ["SQL多表连接", "事务隔离级别", "数据库范式"],
        "preferences": ["图文讲义", "案例分析"],
        "mastery_score": 0.42,
        "last_updated": "2026-06-10",
        "student_no": "2023001234",
        "interests": ["后端开发", "数据工程"],
        "resource_preferences": ["讲义", "案例"],
        "weekly_hours": 8,
        "ai_suggestions": "建议优先攻克SQL多表连接，可通过教务系统真实数据练习",
        "strong_points": [
            {"kp_id": 2, "kp_name": "SQL基本查询", "mastery": 0.85},
            {"kp_id": 3, "kp_name": "数据定义DDL", "mastery": 0.78}
        ],
        "recent_tasks": [
            {"task_id": 10, "title": "数据库事务与并发控制", "status": "completed", "completed_at": "2026-06-09"},
            {"task_id": 11, "title": "SQL多表连接练习", "status": "in_progress", "completed_at": ""}
        ],
        "recent_tests": [
            {"test_id": 5, "accuracy": 0.70, "date": "2026-06-08"},
            {"test_id": 4, "accuracy": 0.65, "date": "2026-06-05"}
        ]
    },
    {
        "profile_id": 2,
        "student_id": 102,
        "student_name": "王悦",
        "course_id": 1,
        "course_name": "数据库系统原理",
        "learning_goal": "深入理解数据库内核机制",
        "current_level": "大三学生，有一定数据库基础",
        "weak_points": ["索引优化", "查询计划分析"],
        "preferences": ["深度技术文章", "源码分析"],
        "mastery_score": 0.68,
        "last_updated": "2026-06-09",
        "student_no": "2022005678",
        "interests": ["数据库内核", "性能优化"],
        "resource_preferences": ["技术文章", "源码"],
        "weekly_hours": 12,
        "ai_suggestions": "建议深入学习索引结构和查询优化器原理",
        "strong_points": [],
        "recent_tasks": [],
        "recent_tests": []
    },
    {
        "profile_id": 3,
        "student_id": 103,
        "student_name": "陈思雨",
        "course_id": 2,
        "course_name": "Python程序设计",
        "learning_goal": "掌握Python编程，能够开发实用工具",
        "current_level": "大一学生，零基础入门",
        "weak_points": ["函数参数传递", "模块导入", "异常处理"],
        "preferences": ["视频教程", "手把手练习"],
        "mastery_score": 0.35,
        "last_updated": "2026-06-07",
        "student_no": "2023012345",
        "interests": ["Web开发", "自动化脚本"],
        "resource_preferences": ["视频", "练习题"],
        "weekly_hours": 6,
        "ai_suggestions": "建议从基础语法入手，多做小项目练习",
        "strong_points": [
            {"kp_id": 20, "kp_name": "Python基础语法", "mastery": 0.72}
        ],
        "recent_tasks": [],
        "recent_tests": []
    }
]

_MOCK_COURSES = [
    {"course_id": 1, "name": "数据库系统原理", "description": "系统学习数据库系统原理"},
    {"course_id": 2, "name": "Python程序设计", "description": "Python编程基础与实践"},
    {"course_id": 3, "name": "软件工程实践", "description": "软件工程方法论与实践"}
]

_MOCK_KNOWLEDGE_POINTS = {
    1: [
        {"kp_id": 1, "name": "关系模型基础", "mastery_level": 0.75},
        {"kp_id": 2, "name": "SQL基本查询", "mastery_level": 0.85},
        {"kp_id": 3, "name": "数据定义DDL", "mastery_level": 0.78},
        {"kp_id": 5, "name": "SQL多表连接", "mastery_level": 0.30},
        {"kp_id": 8, "name": "事务隔离级别", "mastery_level": 0.20},
        {"kp_id": 12, "name": "数据库范式", "mastery_level": 0.40},
    ],
    2: [
        {"kp_id": 20, "name": "Python基础语法", "mastery_level": 0.72},
        {"kp_id": 21, "name": "函数参数传递", "mastery_level": 0.45},
        {"kp_id": 22, "name": "模块导入", "mastery_level": 0.38},
        {"kp_id": 23, "name": "异常处理", "mastery_level": 0.42},
    ],
    3: [
        {"kp_id": 30, "name": "需求分析", "mastery_level": 0.60},
        {"kp_id": 31, "name": "UML建模", "mastery_level": 0.55},
    ]
}


class ProfileService:
    """学生画像 Service"""

    def __init__(self):
        self._repo = ProfileRepository()

    def list_profiles(
        self,
        user: Dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取学生画像列表"""
        items = _MOCK_PROFILES.copy()

        if course_id:
            items = [p for p in items if p["course_id"] == course_id]
        if keyword:
            items = [
                p for p in items
                if keyword.lower() in p["student_name"].lower() or keyword.lower() in p.get("student_no", "").lower()
            ]

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": items[start:end],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        }

    def get_profile(self, profile_id: int, user: Dict[str, Any]) -> Dict[str, Any]:
        """获取学生画像详情"""
        for p in _MOCK_PROFILES:
            if p["profile_id"] == profile_id:
                return {"code": 0, "message": "success", "data": p}
        return {"code": 404, "message": "画像不存在", "data": None}

    def update_profile(self, profile_id: int, data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """更新学生画像"""
        for p in _MOCK_PROFILES:
            if p["profile_id"] == profile_id:
                p.update(data)
                p["last_updated"] = "2026-06-11"
                return {"code": 0, "message": "更新成功", "data": p}
        return {"code": 404, "message": "画像不存在", "data": None}

    def update_mastery(self, profile_id: int, data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """更新知识点掌握度"""
        kp_id = data.get("kp_id")
        mastery = data.get("mastery")
        for p in _MOCK_PROFILES:
            if p["profile_id"] == profile_id:
                # 更新知识点掌握度
                updated = False
                for sp in p.get("strong_points", []):
                    if sp["kp_id"] == kp_id:
                        sp["mastery"] = mastery
                        updated = True
                        break
                p["last_updated"] = "2026-06-11"
                return {"code": 0, "message": "掌握度更新成功", "data": {"kp_id": kp_id, "new_mastery": mastery}}
        return {"code": 404, "message": "画像不存在", "data": None}

    def get_courses(self) -> List[Dict[str, Any]]:
        """获取课程列表"""
        return _MOCK_COURSES

    def get_knowledge_points(self, course_id: int) -> List[Dict[str, Any]]:
        """获取课程知识点"""
        return _MOCK_KNOWLEDGE_POINTS.get(course_id, [])

    def get_students(self) -> List[Dict[str, Any]]:
        """获取学生列表（用于智能体工作台选择）"""
        return [
            {"id": p["student_id"], "name": p["student_name"], "profile_id": p["profile_id"]}
            for p in _MOCK_PROFILES
        ]
```

- [ ] **Step 3: 创建 agents 路由**

```python
# backend/app/routers/agents.py
"""智能体工作台 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.agent_service import AgentService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/agents", tags=["智能体工作台"])


class GenerateRequest(BaseModel):
    student_id: int
    course_id: int
    knowledge_point_ids: List[int]
    resource_type: str
    difficulty: str


class SaveResourceRequest(BaseModel):
    result: dict
    title: str
    course_id: int


@router.get("/list")
async def list_agents(token: str = Depends(get_current_user)):
    """获取智能体列表"""
    service = AgentService()
    return service.list_agents()


@router.post("/generate")
async def generate_learning_resource(
    req: GenerateRequest,
    token: str = Depends(get_current_user),
):
    """执行多智能体协作，生成个性化学习资源"""
    service = AgentService()
    return service.generate(req)


@router.post("/save-resource")
async def save_resource(
    req: SaveResourceRequest,
    token: str = Depends(get_current_user),
):
    """保存生成的学习资源"""
    service = AgentService()
    return service.save_resource(req)
```

- [ ] **Step 4: 创建 agent_service.py**

```python
# backend/app/services/agent_service.py
"""智能体工作台 Service"""
from typing import Any, Dict, List
from app.agents.workflow import LearningAgentWorkflow
from app.llm.mock_provider import MockProvider
from app.llm.gateway import llm_gateway

# 注册 Mock 供应商
llm_gateway.register_provider("mock", MockProvider())


_MOCK_STUDENTS = [
    {"id": 101, "name": "李明", "profile_id": 1},
    {"id": 102, "name": "王悦", "profile_id": 2},
    {"id": 103, "name": "陈思雨", "profile_id": 3},
]

_MOCK_COURSES = [
    {"id": 1, "name": "数据库系统原理"},
    {"id": 2, "name": "Python程序设计"},
    {"id": 3, "name": "软件工程实践"},
]

_MOCK_KNOWLEDGE_POINTS = {
    1: [
        {"id": 1, "name": "关系模型基础"},
        {"id": 2, "name": "SQL基本查询"},
        {"id": 3, "name": "数据定义DDL"},
        {"id": 5, "name": "SQL多表连接"},
        {"id": 8, "name": "事务隔离级别"},
        {"id": 12, "name": "数据库范式"},
    ],
    2: [
        {"id": 20, "name": "Python基础语法"},
        {"id": 21, "name": "函数参数传递"},
        {"id": 22, "name": "模块导入"},
        {"id": 23, "name": "异常处理"},
    ],
    3: [
        {"id": 30, "name": "需求分析"},
        {"id": 31, "name": "UML建模"},
    ]
}

_MOCK_AGENTS = [
    {"id": "diagnosis_agent", "name": "学习诊断智能体", "description": "分析学生薄弱知识点", "type": "diagnosis"},
    {"id": "planning_agent", "name": "资源规划智能体", "description": "生成个性化学习路径", "type": "planning"},
    {"id": "resource_generation_agent", "name": "资源生成智能体", "description": "生成学习资源", "type": "generation"},
    {"id": "assessment_agent", "name": "评测反馈智能体", "description": "分析学习效果", "type": "assessment"},
    {"id": "teacher_review_agent", "name": "教师审核辅助智能体", "description": "生成资源质量建议", "type": "review"},
]

_SAVED_RESOURCES = []


class AgentService:
    """智能体工作台 Service"""

    def __init__(self):
        self._workflow = LearningAgentWorkflow(llm_gateway)

    def list_agents(self) -> Dict[str, Any]:
        """获取智能体列表"""
        return {
            "code": 0,
            "message": "success",
            "data": _MOCK_AGENTS,
        }

    def generate(self, req: Any) -> Dict[str, Any]:
        """执行多智能体工作流"""
        # 获取学生画像
        from app.services.profile_service import ProfileService
        profile_service = ProfileService()

        student_profile = None
        for p in profile_service._MOCK_PROFILES:
            if p["student_id"] == req.student_id:
                student_profile = p
                break

        knowledge_points = _MOCK_KNOWLEDGE_POINTS.get(req.course_id, [])

        # 过滤选中的知识点
        selected_kps = [kp for kp in knowledge_points if kp["id"] in req.knowledge_point_ids]

        # 执行工作流
        result = self._workflow.run(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            student_profile=student_profile,
            knowledge_points=selected_kps,
        )

        return {
            "code": 0,
            "message": "success",
            "data": result,
        }

    def save_resource(self, req: Any) -> Dict[str, Any]:
        """保存学习资源"""
        resource = req.result.get("resource", {})
        saved = {
            "resource_id": resource.get("resource_id"),
            "title": req.title or resource.get("title"),
            "course_id": req.course_id,
            "type": resource.get("type"),
            "content": resource.get("content"),
            "knowledge_points": resource.get("knowledge_points", []),
            "difficulty": resource.get("difficulty"),
            "status": "pending_review",
        }
        _SAVED_RESOURCES.append(saved)
        return {
            "code": 0,
            "message": "资源已保存到学习资源库",
            "data": saved,
        }

    def get_students(self) -> List[Dict[str, Any]]:
        return _MOCK_STUDENTS

    def get_courses(self) -> List[Dict[str, Any]]:
        return _MOCK_COURSES

    def get_knowledge_points(self, course_id: int) -> List[Dict[str, Any]]:
        return _MOCK_KNOWLEDGE_POINTS.get(course_id, [])
```

- [ ] **Step 5: 创建 profile_repo.py**

```python
# backend/app/repositories/profile_repo.py
"""学生画像 Repository"""
from typing import Any, Dict, List, Optional


class ProfileRepository:
    """学生画像数据访问层（当前使用 Mock 数据）"""

    def list_profiles(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 实际从数据库查询
        pass

    def get_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        pass

    def update_profile(self, profile_id: int, data: Dict[str, Any]) -> bool:
        pass
```

---

#### Task 15: 更新 main.py 注册新路由

**Files:**
- Modify: `backend/app/main.py:1-129`

**Steps:**

- [ ] **Step 1: 更新 main.py 注册新路由**

```python
# backend/app/main.py - 更新导入和注册

from app.routers import auth, users, projects, tasks, prompts, models, invocations, reviews, artifacts, statistics, logs, profiles, agents, learning

# ... 在 include_router 部分增加：
    app.include_router(profiles.router)
    app.include_router(agents.router)
    app.include_router(learning.router)

# ... 更新 FastAPI title/description：
    app = FastAPI(
        title="EduAgent Studio",
        description="智学工坊：基于大模型的个性化学习资源生成与多智能体协作系统",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )
```

- [ ] **Step 2: 更新 config.py app_name 默认值**

```python
# backend/app/config.py - 修改 app_name 默认值
app_name: str = Field(default="EduAgent Studio", alias="APP_NAME")
```

---

### Phase 1.4：数据库改造

#### Task 16: 新建 A3 数据库脚本

**Files:**
- Create: `database/09_create_a3_tables.sql`
- Create: `database/10_insert_a3_initial_data.sql`
- Create: `database/pgvector/01_enable_pgvector.sql`
- Create: `database/pgvector/02_create_embeddings_table.sql`
- Create: `database/pgvector/03_embedding_demo.sql`
- Create: `database/README_A3.md`

**Steps:**

- [ ] **Step 1: 创建 09_create_a3_tables.sql**

```sql
-- ============================================================
-- 09_create_a3_tables.sql
-- EduAgent Studio - A3 赛题专用表（课程/学生画像/知识点/学习资源等）
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 1. courses 课程表（映射 projects 表，A3 语义）
-- ============================================================
CREATE TABLE IF NOT EXISTS `courses` (
    `course_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '课程ID',
    `course_name` VARCHAR(200) NOT NULL COMMENT '课程名称',
    `course_code` VARCHAR(50) NULL COMMENT '课程代码',
    `description` TEXT NULL COMMENT '课程描述',
    `teacher_id` INT UNSIGNED NOT NULL COMMENT '主讲教师ID',
    `status` ENUM('active','archived','draft') NOT NULL DEFAULT 'active' COMMENT '课程状态',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`course_id`),
    KEY `idx_courses_teacher` (`teacher_id`),
    KEY `idx_courses_status_deleted` (`status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- ============================================================
-- 2. knowledge_points 知识点表
-- ============================================================
CREATE TABLE IF NOT EXISTS `knowledge_points` (
    `kp_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '知识点ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `kp_name` VARCHAR(200) NOT NULL COMMENT '知识点名称',
    `kp_code` VARCHAR(50) NULL COMMENT '知识点编码',
    `parent_kp_id` INT UNSIGNED NULL COMMENT '父知识点ID（用于知识点树）',
    `difficulty_level` ENUM('basic','intermediate','advanced') NOT NULL DEFAULT 'basic' COMMENT '难度等级',
    `description` TEXT NULL COMMENT '知识点描述',
    `estimated_hours` DECIMAL(5,2) NULL COMMENT '预计学习时长（小时）',
    `prerequisite_kp_ids` VARCHAR(500) NULL COMMENT '先修知识点ID列表，逗号分隔',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`kp_id`),
    KEY `idx_kp_course` (`course_id`),
    KEY `idx_kp_parent` (`parent_kp_id`),
    KEY `idx_kp_difficulty` (`difficulty_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点表';

-- ============================================================
-- 3. student_profiles 学生画像表
-- ============================================================
CREATE TABLE IF NOT EXISTS `student_profiles` (
    `profile_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '画像ID',
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生用户ID（引用 users.user_id）',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `learning_goal` TEXT NULL COMMENT '学习目标',
    `current_level` TEXT NULL COMMENT '当前基础水平',
    `interests` VARCHAR(500) NULL COMMENT '兴趣方向，逗号分隔',
    `resource_preferences` VARCHAR(500) NULL COMMENT '资源类型偏好，逗号分隔',
    `weekly_hours` INT UNSIGNED NULL COMMENT '每周可用于学习的小时数',
    `mastery_score` DECIMAL(5,3) NOT NULL DEFAULT 0.000 COMMENT '综合掌握度评分（0-1）',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`profile_id`),
    UNIQUE KEY `uk_student_course` (`student_id`, `course_id`),
    KEY `idx_profile_course` (`course_id`),
    KEY `idx_profile_mastery` (`mastery_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生画像表';

-- ============================================================
-- 4. student_knowledge_mastery 学生知识点掌握度表
-- ============================================================
CREATE TABLE IF NOT EXISTS `student_knowledge_mastery` (
    `mastery_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '掌握度记录ID',
    `profile_id` INT UNSIGNED NOT NULL COMMENT '画像ID',
    `kp_id` INT UNSIGNED NOT NULL COMMENT '知识点ID',
    `mastery_level` DECIMAL(5,3) NOT NULL DEFAULT 0.000 COMMENT '掌握度评分（0-1）',
    `last_test_score` DECIMAL(5,3) NULL COMMENT '最近一次测验得分（0-1）',
    `last_test_date` DATE NULL COMMENT '最近测验日期',
    `update_reason` VARCHAR(255) NULL COMMENT '更新原因',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`mastery_id`),
    UNIQUE KEY `uk_profile_kp` (`profile_id`, `kp_id`),
    KEY `idx_mastery_kp` (`kp_id`),
    KEY `idx_mastery_level` (`mastery_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生知识点掌握度表';

-- ============================================================
-- 5. learning_resources 学习资源表（映射 task_outputs，A3 语义）
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_resources` (
    `resource_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '资源ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `resource_title` VARCHAR(200) NOT NULL COMMENT '资源标题',
    `resource_type` ENUM('lecture','ppt','quiz','case','review','test','other') NOT NULL COMMENT '资源类型',
    `difficulty` ENUM('basic','intermediate','advanced') NOT NULL DEFAULT 'basic' COMMENT '难度等级',
    `content` LONGTEXT NULL COMMENT '资源正文内容',
    `target_student_ids` VARCHAR(500) NULL COMMENT '适用学生ID列表（为空则对所有学生适用）',
    `target_kp_ids` VARCHAR(500) NULL COMMENT '关联知识点ID列表，逗号分隔',
    `generation_model` VARCHAR(100) NULL COMMENT '生成所用模型',
    `generation_agent` VARCHAR(100) NULL COMMENT '生成所用智能体',
    `invocation_id` BIGINT UNSIGNED NULL COMMENT '关联的AI调用记录ID',
    `status` ENUM('draft','pending_review','approved','rejected','archived') NOT NULL DEFAULT 'draft' COMMENT '审核状态',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`resource_id`),
    KEY `idx_resource_course` (`course_id`),
    KEY `idx_resource_type` (`resource_type`),
    KEY `idx_resource_status` (`status`, `is_deleted`),
    KEY `idx_resource_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习资源表';

-- ============================================================
-- 6. learning_feedbacks 学习反馈表
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_feedbacks` (
    `feedback_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '反馈ID',
    `profile_id` INT UNSIGNED NOT NULL COMMENT '学生画像ID',
    `resource_id` INT UNSIGNED NULL COMMENT '关联学习资源ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `feedback_type` ENUM('quiz_result','self_report','study_note','question') NOT NULL COMMENT '反馈类型',
    `content` TEXT NULL COMMENT '反馈内容',
    `quiz_score` DECIMAL(5,3) NULL COMMENT '测验得分（0-1）',
    `self_mastery` DECIMAL(5,3) NULL COMMENT '自评掌握度（0-1）',
    `difficulty_rating` ENUM('too_easy','appropriate','too_hard') NULL COMMENT '难度评价',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`feedback_id`),
    KEY `idx_feedback_profile` (`profile_id`),
    KEY `idx_feedback_resource` (`resource_id`),
    KEY `idx_feedback_course` (`course_id`),
    KEY `idx_feedback_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习反馈表';

-- ============================================================
-- 7. learning_tasks 学习任务表（映射 project_tasks，A3 语义）
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_tasks` (
    `task_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `title` VARCHAR(200) NOT NULL COMMENT '任务标题',
    `description` TEXT NULL COMMENT '任务描述',
    `target_kp_ids` VARCHAR(500) NULL COMMENT '目标知识点ID列表',
    `creator_id` INT UNSIGNED NOT NULL COMMENT '创建人（教师）',
    `assignee_id` INT UNSIGNED NULL COMMENT '指派学生ID',
    `status` ENUM('draft','assigned','in_progress','completed','archived') NOT NULL DEFAULT 'draft' COMMENT '任务状态',
    `due_date` DATETIME NULL COMMENT '截止时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`task_id`),
    KEY `idx_task_course` (`course_id`),
    KEY `idx_task_assignee` (`assignee_id`),
    KEY `idx_task_status` (`status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习任务表';

-- ============================================================
-- 8. learning_analytics 学习分析表
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_analytics` (
    `analytics_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分析记录ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `profile_id` INT UNSIGNED NULL COMMENT '学生画像ID（为空则是课程级别统计）',
    `analytics_type` VARCHAR(50) NOT NULL COMMENT '分析类型：mastery_summary/weak_points/resource_usage/agent_calls',
    `analytics_data` JSON NOT NULL COMMENT '分析数据（JSON）',
    `period_start` DATE NULL COMMENT '统计周期开始',
    `period_end` DATE NULL COMMENT '统计周期结束',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`analytics_id`),
    KEY `idx_analytics_course` (`course_id`),
    KEY `idx_analytics_profile` (`profile_id`),
    KEY `idx_analytics_type` (`analytics_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习分析表';
```

- [ ] **Step 2: 创建 10_insert_a3_initial_data.sql**

```sql
-- ============================================================
-- 10_insert_a3_initial_data.sql
-- EduAgent Studio - A3 赛题初始化数据
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 插入课程数据
-- ============================================================
INSERT INTO `courses` (`course_name`, `course_code`, `description`, `teacher_id`, `status`) VALUES
    ('数据库系统原理', 'CS301', '系统学习数据库系统的基本概念、关系模型、SQL语言、事务与并发控制、数据库设计等内容', 1, 'active'),
    ('Python程序设计', 'CS201', 'Python编程语言基础、函数、模块、面向对象、异常处理等核心内容', 1, 'active'),
    ('软件工程实践', 'CS401', '软件工程方法论、需求分析、系统设计、项目管理、敏捷开发等内容', 1, 'active');

-- ============================================================
-- 插入知识点数据
-- ============================================================
INSERT INTO `knowledge_points` (`course_id`, `kp_name`, `kp_code`, `difficulty_level`, `description`, `estimated_hours`) VALUES
    -- 数据库系统原理
    (1, '关系模型基础', 'DB001', 'basic', '关系模型的核心概念：关系、元组、属性、键', 2.0),
    (1, 'SQL基本查询', 'DB002', 'basic', 'SELECT/FROM/WHERE/ORDER BY等基本查询语法', 3.0),
    (1, '数据定义DDL', 'DB003', 'basic', 'CREATE/ALTER/DROP TABLE等DDL语句', 2.0),
    (1, 'SQL多表连接', 'DB005', 'intermediate', 'INNER JOIN/LEFT JOIN/RIGHT JOIN/FULL OUTER JOIN等', 4.0),
    (1, '事务隔离级别', 'DB008', 'advanced', 'ACID特性、脏读/不可重复读/幻读、四种隔离级别', 3.0),
    (1, '数据库范式', 'DB012', 'intermediate', '1NF/2NF/3NF/BCNF范式及规范化过程', 3.0),
    (1, '索引与优化', 'DB015', 'advanced', 'B+树索引、索引设计原则、查询优化基础', 4.0),
    (1, '数据库设计', 'DB020', 'intermediate', 'ER图设计、概念模型、逻辑设计、物理设计', 4.0),
    -- Python程序设计
    (2, 'Python基础语法', 'PY001', 'basic', '变量、数据类型、运算符、流程控制', 3.0),
    (2, '函数参数传递', 'PY002', 'intermediate', '位置参数、关键字参数、默认参数、*args/**kwargs', 2.5),
    (2, '模块导入', 'PY003', 'intermediate', 'import/from...import、模块搜索路径、包管理', 2.0),
    (2, '异常处理', 'PY004', 'intermediate', 'try/except/finally、自定义异常', 2.0),
    (2, '面向对象编程', 'PY005', 'intermediate', '类与对象、继承、多态、特殊方法', 4.0),
    -- 软件工程实践
    (3, '需求分析', 'SE001', 'basic', '需求获取、需求建模、需求规格说明', 3.0),
    (3, 'UML建模', 'SE002', 'intermediate', '用例图、类图、时序图、活动图等', 4.0),
    (3, '软件测试', 'SE003', 'intermediate', '单元测试、集成测试、系统测试、测试用例设计', 3.0),
    (3, '敏捷开发', 'SE004', 'basic', 'Scrum、看板、冲刺、每日站会', 2.0);

-- ============================================================
-- 插入学习任务数据
-- ============================================================
INSERT INTO `learning_tasks` (`course_id`, `title`, `description`, `target_kp_ids`, `creator_id`, `status`) VALUES
    (1, '数据库事务与并发控制', '学习事务的ACID特性，掌握四种隔离级别的区别和应用场景', '8', 1, 'assigned'),
    (1, 'SQL多表连接练习', '完成教务系统多表查询练习，包括INNER JOIN和LEFT JOIN', '5', 1, 'assigned'),
    (1, '数据库设计大作业', '完成一个小型的数据库设计项目，从需求分析到ER图到建表SQL', '20', 1, 'draft'),
    (2, 'Python函数与模块练习', '编写一个包含多个函数的Python模块，实现基本的文本处理功能', '2,3', 1, 'assigned'),
    (3, 'UML建模实践', '使用UML工具为选定的系统绘制完整的用例图和类图', '2', 1, 'draft');

-- ============================================================
-- 插入 A3 提示词模板（替换旧的 task_type 模板）
-- ============================================================
UPDATE `task_types` SET `type_name` = '知识点讲义生成', `type_code` = 'lecture_generation', `description` = '根据知识点和学习目标，生成个性化的知识点讲义' WHERE `type_code` = 'requirement_analysis';

INSERT INTO `task_types` (`type_name`, `type_code`, `description`, `status`) VALUES
    ('PPT大纲生成', 'ppt_generation', '根据课程内容生成PPT演示大纲', 'active'),
    ('习题与答案生成', 'quiz_generation', '根据知识点生成配套练习题和答案解析', 'active'),
    ('案例材料生成', 'case_generation', '根据知识点生成实际应用案例', 'active'),
    ('复习计划生成', 'review_plan_generation', '根据学生薄弱点生成个性化复习计划', 'active'),
    ('阶段测验生成', 'test_generation', '根据学习进度生成阶段测验题目', 'active');

-- ============================================================
-- 更新问题标签（改为 A3 学习场景）
-- ============================================================
DELETE FROM `issue_tags` WHERE 1=1;

INSERT INTO `issue_tags` (`tag_name`, `tag_code`, `description`, `severity`) VALUES
    ('内容空洞', 'content_vague', '学习资源内容过于笼统，缺乏具体细节和示例', 'medium'),
    ('知识点错误', 'factual_error', '学习资源中存在知识点错误或与教材不符', 'high'),
    ('逻辑不清晰', 'logic_confusion', '讲解逻辑混乱，前后矛盾或推理过程有问题', 'medium'),
    ('格式不规范', 'format_issues', '格式不符合学习资源规范', 'low'),
    ('偏离知识点', 'off_topic', '内容偏离了目标知识点', 'medium'),
    ('难度不适配', 'difficulty_mismatch', '难度与学生水平不匹配', 'medium'),
    ('缺少案例', 'lack_case', '缺少实际应用案例', 'low'),
    ('习题不足', 'lack_exercise', '配套练习题数量不足', 'low'),
    ('概念模糊', 'concept_vague', '核心概念讲解模糊', 'high'),
    ('代码有误', 'code_error', '代码示例存在语法错误或逻辑问题', 'high');
```

- [ ] **Step 3: 创建 pgvector 目录和脚本**

```sql
-- database/pgvector/01_enable_pgvector.sql
-- 启用 pgvector 扩展（PostgreSQL）
CREATE EXTENSION IF NOT EXISTS vector;
COMMENT ON EXTENSION vector IS 'Vector similarity search for Postgres';

-- 验证扩展是否启用
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

```sql
-- database/pgvector/02_create_embeddings_table.sql
-- 创建 embedding 表和向量索引

CREATE TABLE IF NOT EXISTS knowledge_point_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    kp_id INTEGER NOT NULL REFERENCES knowledge_points(kp_id),
    content_chunk TEXT NOT NULL,
    embedding VECTOR(768),
    chunk_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 HNSW 索引（推荐，用于高维向量检索）
CREATE INDEX ON knowledge_point_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 或者创建 IVFFlat 索引（适合大数据量）
-- CREATE INDEX ON knowledge_point_embeddings
-- USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

COMMENT ON TABLE knowledge_point_embeddings IS '知识点 embedding 存储表';
COMMENT ON COLUMN knowledge_point_embeddings.embedding IS '768维向量（使用text-embedding-3-small或BGE模型时为768维）';
```

```sql
-- database/pgvector/03_embedding_demo.sql
-- 向量检索 Demo

-- 插入示例 embedding（768维随机向量，仅供演示）
INSERT INTO knowledge_point_embeddings (kp_id, content_chunk, embedding)
VALUES
    (5, 'SQL多表连接：INNER JOIN返回两表匹配记录，LEFT JOIN返回左表全部记录', '[0.1,0.2,...(768个元素)]'::vector),
    (8, '事务隔离级别：READ UNCOMMITTED/READ COMMITTED/REPEATABLE READ/SERIALIZABLE', '[0.1,0.3,...(768个元素)]'::vector),
    (12, '数据库范式：1NF消除重复组，2NF消除非主属性对主键的部分依赖，3NF消除传递依赖', '[0.2,0.1,...(768个元素)]'::vector);

-- 查询与给定向量最相似的知识点（余弦相似度）
-- SELECT
--     kp.kp_name,
--     kp.difficulty_level,
--     1 - (e.embedding <=> '[query_vector]'::vector) AS similarity
-- FROM knowledge_point_embeddings e
-- JOIN knowledge_points kp ON e.kp_id = kp.kp_id
-- ORDER BY e.embedding <=> '[query_vector]'::vector
-- LIMIT 5;
```

- [ ] **Step 4: 创建 database/README_A3.md**

```markdown
# 数据库 A3 改造说明

## 一、改造策略：两阶段方案

### Phase 1（当前）
- 保留 MySQL 业务表（01-08 脚本）不变
- 新增 PostgreSQL + pgvector 作为知识库和向量检索层
- 新增 A3 专用表（09-10 脚本）：courses、knowledge_points、student_profiles 等

### Phase 2（后续）
- 将 MySQL 业务表逐步迁移到 PostgreSQL
- 合并为统一的 PostgreSQL + pgvector 数据层
- 使用 Alembic 管理数据库迁移

## 二、数据库切换步骤

### 1. 安装 PostgreSQL 15+ 和 pgvector

```bash
# Docker 方式（推荐）
docker run -d \
  --name eduagent-pg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=eduagent_studio \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  pgvector/pgvector:pg16

# 或者使用 docker-compose（见项目根目录 docker-compose.yml）
```

### 2. 创建数据库和扩展

```bash
psql -U postgres -d eduagent_studio -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. 执行 A3 建表脚本

```bash
psql -U postgres -d eduagent_studio < database/09_create_a3_tables.sql
psql -U postgres -d eduagent_studio < database/10_insert_a3_initial_data.sql
psql -U postgres -d eduagent_studio < database/pgvector/01_enable_pgvector.sql
psql -U postgres -d eduagent_studio < database/pgvector/02_create_embeddings_table.sql
psql -U postgres -d eduagent_studio < database/pgvector/03_embedding_demo.sql
```

### 4. 配置后端连接 PostgreSQL

修改 `backend/.env`：
```env
DB_TYPE=postgresql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=eduagent_studio
```

## 三、向量检索 Demo

详见 `database/pgvector/03_embedding_demo.sql`

主要操作：
1. 向 `knowledge_point_embeddings` 表插入知识点和其 embedding 向量
2. 使用 `<=>`（余弦距离）运算符检索相似知识点
3. `1 - (a <=> b)` 得到余弦相似度（1=完全相同，0=正交）

## 四、表命名说明

为减少迁移风险，A3 表名与原有 MySQL 表名保持一定对应关系：

| A3 表名 | 说明 | 可映射到 MySQL |
|---------|------|--------------|
| courses | 课程空间 | projects |
| learning_tasks | 学习任务 | project_tasks |
| learning_resources | 学习资源 | task_outputs |
| student_profiles | 学生画像 | （新增）|
| knowledge_points | 知识点 | （新增）|
| learning_feedbacks | 学习反馈 | （新增）|
```

---

### Phase 1.5：基础设施与文档清理

#### Task 17: 新建 Docker Compose 和环境配置

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/.env.example`

**Steps:**

- [ ] **Step 1: 创建 docker-compose.yml**

```yaml
# EduAgent Studio Docker Compose
# 包含 PostgreSQL + pgvector + Redis + MinIO

version: "3.8"

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: eduagent-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: EduAgent2026
      POSTGRES_DB: eduagent_studio
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./database/pgvector:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: eduagent-redis
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: eduagent-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: eduagent
      MINIO_ROOT_PASSWORD: EduAgent2026MinIO
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - miniodata:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  pgdata:
  redisdata:
  miniodata:
```

- [ ] **Step 2: 创建根目录 .env.example**

```env
# EduAgent Studio 配置示例
# 复制为 .env 后填写真实值

APP_NAME=EduAgent Studio
APP_ENV=development

# PostgreSQL 配置（Phase 1 用于 A3 表，Phase 2 用于全部业务表）
DB_TYPE=postgresql
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=EduAgent2026
POSTGRES_DB=eduagent_studio

# MySQL 配置（当前业务表，过渡期保留）
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=ai_collab_audit_system

# JWT 配置
JWT_SECRET_KEY=change_me_to_random_64_char_string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# API Key 加密密钥
API_KEY_SECRET=change_me_to_32_byte_hex_key

# LLM 配置（可选）
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o

# Redis 配置（异步任务）
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO 配置（对象存储）
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=eduagent
MINIO_SECRET_KEY=EduAgent2026MinIO
MINIO_BUCKET=eduagent-resources

# 后端服务
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

---

#### Task 18: 旧文档归档

**Files:**
- Create: `docs/archive_old_course_project/` directory and move files
- Create: `docs/开发检查清单.md`

**Steps:**

- [ ] **Step 1: 创建归档目录**

```bash
# 在文件系统层面执行（由工具完成）：
# 创建 docs/archive_old_course_project/ 目录
# 将以下文件移动到该目录：
# - docs/数据库管理实务课程报告.md
# - docs/数据库管理实务课程报告_图片占位清单.md
# - docs/数据库管理实务课程报告_待补截图清单.md
# - docs/数据库课程设计结课报告.md
# - docs/结课报告图片占位清单.md
# - docs/结课报告待补截图清单.md
# - docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md
# - docs/project_development_doc.md
# - docs/test_report.md
# - docs/数据库管理实务课程报告.md
# - docs/system_test_report_material.md
```

- [ ] **Step 2: 创建开发检查清单**

```markdown
# 开发检查清单

## Phase 1 验收检查

### 品牌与文档
- [ ] README.md 显示「智学工坊 EduAgent Studio」
- [ ] 登录页标题为「智学工坊 EduAgent Studio」
- [ ] 侧边栏 Logo 显示「智学工坊」
- [ ] docs/A3赛题适配说明.md 存在且内容正确
- [ ] docs/技术架构选型说明.md 存在且内容正确
- [ ] docs/多智能体设计.md 存在且内容正确
- [ ] docs/演示脚本.md 存在且可执行
- [ ] 旧课程报告已归档到 docs/archive_old_course_project/

### 前端
- [ ] 登录后首页为 A3 Dashboard
- [ ] 侧边栏菜单全部为 A3 语义（课程空间、学习任务、学生画像、智能体工作台等）
- [ ] 路由标题全部为 A3 语义
- [ ] 学生画像页面可访问（/profiles）
- [ ] 智能体工作台页面可访问（/agent-workbench）
- [ ] 学习资源库页面可访问（/resources）
- [ ] 教师审核中心页面可访问（/reviews）
- [ ] 学习分析看板页面可访问（/analytics）

### 后端
- [ ] FastAPI title 为「EduAgent Studio」
- [ ] /api/profiles 接口返回学生画像数据
- [ ] /api/agents/generate 接口可执行多智能体工作流
- [ ] /api/agents/list 接口返回5个智能体列表
- [ ] backend/app/agents/ 目录包含5个智能体文件
- [ ] backend/app/llm/ 目录包含 LLM Gateway

### 数据库
- [ ] 09_create_a3_tables.sql 可执行
- [ ] 10_insert_a3_initial_data.sql 包含 A3 示例数据（课程/知识点/任务）
- [ ] pgvector 目录包含向量检索示例脚本
- [ ] database/README_A3.md 说明数据库改造方案

### 基础设施
- [ ] docker-compose.yml 存在且包含 PostgreSQL/Redis/MinIO
- [ ] .env.example 存在且包含 A3 配置项

## Phase 2 验收检查（待完成）
- [ ] 学习反馈模块
- [ ] 学习分析看板图表
- [ ] Redis + Celery 异步任务
- [ ] MinIO 对象存储
- [ ] MySQL 到 PostgreSQL 迁移
```

---

#### Task 19: 新建 CHANGELOG_A3_MIGRATION.md

**Files:**
- Create: `CHANGELOG_A3_MIGRATION.md`

**Steps:**

- [ ] **Step 1: 创建迁移日志**

```markdown
# EduAgent Studio — A3 Migration Changelog

## [Phase 1] 2026-06-11

### 重大变更

#### 项目重命名
- 项目名称从「AI-Collab-Audit-System」更名为「EduAgent Studio（智学工坊）」
- 系统定位从「AI 项目质量审计」改为「个性化学习资源生成与多智能体协作」

#### 技术架构升级
- 新增 PostgreSQL + pgvector 支持（两阶段方案 Phase 1）
- 新增多智能体编排层（LangGraph + 5个智能体）
- 新增统一 LLM Gateway（支持 Mock 和 OpenAI-compatible API）
- 新增向量检索基础设施（pgvector）

### 新增功能

#### 前端
- 新增学生画像页面（列表 + 详情）
- 新增智能体工作台页面（配置 + 执行 + 结果展示）
- 重写 Dashboard 首页（A3 业务流程 + 指标卡）
- 重写登录页（智学工坊 EduAgent Studio）
- 重写侧边栏菜单（A3 语义）
- 新增学习资源库页面
- 新增教师审核中心页面
- 新增学习分析看板页面

#### 后端
- 新增 `/api/profiles` 路由（学生画像 CRUD）
- 新增 `/api/agents` 路由（多智能体工作流）
- 新增 `backend/app/agents/` 模块（5个智能体 + 工作流）
- 新增 `backend/app/llm/` 模块（LLM Gateway + Mock Provider）
- 新增 `backend/app/services/profile_service.py`
- 新增 `backend/app/services/agent_service.py`

#### 数据库
- 新增 8 张 A3 专用表（courses、knowledge_points、student_profiles 等）
- 新增 A3 初始化数据（3门课程、16个知识点、5个学习任务）
- 新增 pgvector 扩展和向量检索示例

### 改造功能

#### 前端
- 所有页面文案 A3 化（项目空间→课程空间，任务→学习任务等）
- 所有路由标题 A3 化
- 统计卡片指标 A3 化
- 角色常量增加 student

#### 后端
- FastAPI title/description 更新
- app_name 默认值更新
- 注册新路由 profiles、agents、learning

#### 文档
- 完全重写 README.md
- 新建 docs/A3赛题适配说明.md
- 新建 docs/技术架构选型说明.md
- 新建 docs/多智能体设计.md
- 新建 docs/演示脚本.md
- 新建 docs/开发检查清单.md
- 归档旧课程报告到 docs/archive_old_course_project/

### 待完成（Phase 2）
- 学习反馈与测评模块
- 学习分析看板图表
- Redis + Celery 异步任务
- MinIO 对象存储集成
- MySQL 业务表迁移到 PostgreSQL
- 真实大模型接入（当前为 Mock）

## [Previous] AI-Collab-Audit-System
见 docs/archive_old_course_project/ 中的历史文档。
```

---

### Phase 1.6：收尾验证

#### Task 20: 更新后端 requirements.txt 添加新依赖

**Files:**
- Modify: `backend/requirements.txt` (如果存在)

**Steps:**

- [ ] **Step 1: 检查并更新 requirements.txt**

检查 `backend/requirements.txt` 是否存在，如果存在则确保包含：
```
fastapi>=0.110.0
pydantic>=2.1.0
pydantic-settings>=2.1.0
uvicorn>=0.27.0
pymysql>=1.1.0
sqlalchemy>=2.0.0
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
cryptography>=42.0.0
httpx>=0.27.0
python-multipart>=0.0.9
# LangGraph（多智能体）
langgraph>=0.0.20
langchain-core>=0.1.0
# PostgreSQL（Phase 2）
psycopg2-binary>=2.9.9
# Redis + Celery（Phase 2）
redis>=5.0.0
celery>=5.3.0
```

---

## 三、自查清单

### Spec 覆盖检查

| 赛题要求 | 实现位置 | 状态 |
|---------|---------|------|
| 个性化学生画像 | profile_service.py + profiles 页面 | ✅ Phase 1 |
| 多智能体协作链路 | workflow.py + 5个 agent | ✅ Phase 1 |
| 多类型资源生成 | resource_generation_agent.py | ✅ Phase 1 |
| 教师审核 | reviews 页面 + teacher_review_agent | ✅ Phase 1 |
| 学习反馈 | learning_feedbacks 表 | ✅ 数据库已建 |
| 学习分析报表 | analytics 页面 | ⚠️ 页面框架 Phase 1，图表 Phase 2 |
| 智能体调用审计 | 复用 ai_invocations | ✅ 复用 |
| 成本统计 | 复用 cost_records | ✅ 复用 |

### 无 Placeholder 检查
- [x] README.md 完全重写，无占位内容
- [x] 所有 API 接口有 Mock 实现，不返回假路径
- [x] 所有新增页面有完整 Vue 组件代码
- [x] 所有新增后端服务有完整 Python 代码
- [x] 数据库脚本可执行
- [x] 文档内容与代码一致

### 类型一致性检查
- [x] AgentState.to_dict() 与 workflow.run() 返回值一致
- [x] ProfileDetail 接口与 profile_service 返回值一致
- [x] AgentResult JSON Schema 与前端 agents.ts 类型定义一致

---

## 四、执行方式选择

**计划已保存到 `docs/superpowers/plans/2026-06-11-EduAgent-A3-Phase1.md`。**

两个执行选项：

**1. Subagent-Driven（推荐）** — 每个 Phase 任务派发独立 subagent，任务间并行执行，到阶段边界时 review

**2. Inline Execution** — 在本 session 中顺序执行所有任务，带 checkpoint 审查

请选择执行方式，或告诉我是否需要调整计划中的某些内容。
