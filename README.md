# AI-Collab-Audit-System

> 智研协作 AI 项目质量审计系统

面向高校项目协作、AI 任务生成、版本管理、审核中心、成果库和统计看板的数据库课程设计系统。

![Vue3](https://img.shields.io/badge/Frontend-Vue3-4FC08D?style=flat&logo=vue.js)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)
![MySQL](https://img.shields.io/badge/Database-MySQL_8.0-4479A1?style=flat&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 项目简介

大模型（LLMs）已经广泛融入高校的课程设计、科研训练和创新创业项目中。然而，学生团队在使用 AI 工具时往往面临内容散落、提示词无法复用、模型"幻觉"难识别、多次修改后版本混乱等痛点。

**"智研协作"** 并非一个简单的"大模型聊天壳子"，而是一个结合了 **Git 版本控制思想** 的人机协同内容管理平台。系统将 AI 的调用过程纳入项目管理体系，把每一次 AI 生成与人工修改看作一次"Commit"，让 AI 辅助创作变得可管理、可追踪、可审核、可回滚。

本项目为《数据库管理实务》课程结课设计项目。

---

## 核心特性

- **项目与任务空间**：以课程/竞赛项目为单位隔离数据，支持多角色（成员、负责人、指导老师）权限协同。
- **Git 式版本管理**：每一次 AI 初稿生成、人工二次修改都将生成独立版本，构建完整的时间线与版本树，支持乐观锁防冲突。
- **质量审计与批注**：拒绝 AI 劣质内容直接入库。支持对生成结果进行多维评分（准确性、逻辑性等）、打回修改与打标签。
- **多模型统一调用**：一套 Prompt 跑多个模型，直观对比输出质量（初期采用 Mock 机制，支持扩展真实 API）。
- **Token 成本与用量大屏**：精细化统计不同用户、不同模型、不同项目的 Token 消耗量与估算成本。
- **全过程安全审计**：核心业务数据采用"软删除（Soft Delete）"，配合底层触发器与操作日志，确保内容演进的 100% 可追溯。

---

## 功能模块

| 模块 | 说明 |
|------|------|
| 登录与权限管理 | 用户注册、登录、用户信息查询、退出登录、角色权限控制、登录日志记录、密码哈希存储、用户管理、角色分配、个人中心 |
| 项目空间 | 项目 CRUD、成员管理、归档 |
| 任务与版本 | 任务创建/分配/状态流转、Git 式分支与版本管理 |
| AI 生成 | 多模型批量调用（Mock 机制）、调用日志与成本记录 |
| 人工编辑与批注 | 输出内容编辑、另存新版本、批注与问题标注 |
| 审核中心 | 提交审核、多维评分（准确性/完整性等）、问题标签 |
| 成果库 | 已采用成果归档、版本管理 |
| 统计看板 | 项目/任务/审核概览、模型调用统计、成本分析、成员贡献 |
| 操作日志 | 全局操作日志记录 |
| 调用审计 | AI 调用日志查询、调用详情、成本追踪 |
| 成本统计 | 按模型/按项目多维度成本分析 |
| 提示词管理 | 提示词模板创建、版本管理、模板启用停用 |
| 用户管理 | 用户列表、启用禁用、角色分配 |

---

## 技术栈

### 前端

| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | Vue 3 (Composition API) + TypeScript | 基于 V3 Admin Vite 二次开发 |
| 构建工具 | Vite 7 | 热更新与快速构建 |
| UI 组件库 | Element Plus 2.13 | 企业级 Vue 3 组件库 |
| 状态管理 | Pinia 3.0 | 全局状态管理 |
| 路由 | Vue Router 4.6 | SPA 路由管理 |
| HTTP 客户端 | Axios 1.13 | HTTP 请求封装 |
| CSS 方案 | UnoCSS + Sass | 原子化 CSS |
| 可视化 | ECharts | 统计图表 |

> 前端基于 [V3 Admin Vite](https://github.com/un-pany/v3-admin-vite) 模板（MIT License）二次开发，详见 `frontend/NOTICE.md`。

### 后端

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI >= 0.110.0 |
| ASGI 服务器 | uvicorn >= 0.27.0 |
| 数据库驱动 | PyMySQL >= 1.1.0（原生参数化 SQL，无 ORM）|
| 配置管理 | pydantic-settings >= 2.1.0 |
| JWT 认证 | PyJWT >= 2.8.0 |
| 密码哈希 | passlib[bcrypt] >= 1.7.4 |
| API Key 加密 | cryptography >= 42.0.0（AES-GCM）|
| Python 版本 | 3.10+ |

### 数据库

| 组件 | 技术 |
|------|------|
| 数据库 | MySQL 8.0+ |
| 设计规范 | 第三范式（3NF）|
| 数据库对象 | 表、索引、视图、存储过程、触发器 |
| 数据访问 | 原生参数化 SQL（PyMySQL）|

---

## 目录结构

```
AI-Collab-Audit-System/
├── README.md                          # 本文件（项目总览）
├── backend/                           # FastAPI 后端
│   ├── README.md                      # 后端说明
│   ├── app/
│   │   ├── adapters/                  # AI 模型调用适配器（Mock）
│   │   ├── repositories/              # 数据访问层（原生 SQL）
│   │   ├── routers/                   # API 路由定义
│   │   ├── services/                  # 业务逻辑层
│   │   ├── utils/                     # 工具模块（JWT、密码、加密、异常）
│   │   ├── config.py                 # 配置管理
│   │   ├── database.py               # 数据库连接
│   │   └── main.py                   # FastAPI 应用入口
│   ├── scripts/
│   │   ├── check_backend.py          # 后端整体语法检查
│   │   ├── curl_examples.sh          # curl 测试示例
│   │   ├── route_list.md             # API 路由清单
│   │   └── test_report_material.md   # 测试报告素材
│   ├── .env.example                  # 环境变量示例
│   ├── requirements.txt              # Python 依赖
│   └── run.py                        # 启动入口
├── frontend/                          # Vue3 前端
│   ├── README.md                      # 前端说明
│   ├── NOTICE.md                      # 开源归属说明
│   ├── .env.example                  # 环境变量示例
│   ├── src/
│   │   ├── http/                    # Axios 封装
│   │   ├── layouts/                 # 后台布局
│   │   ├── pages/                   # 页面组件
│   │   │   ├── dashboard/          # 首页
│   │   │   ├── projects/            # 项目空间
│   │   │   ├── tasks/               # 任务与版本
│   │   │   ├── reviews/             # 审核中心
│   │   │   ├── artifacts/            # 成果库
│   │   │   ├── statistics/           # 统计看板
│   │   │   ├── models/              # 模型管理
│   │   │   └── login/               # 登录页
│   │   ├── pinia/                   # 状态管理
│   │   ├── router/                  # 路由配置
│   │   └── common/                  # 通用组件与工具
│   └── scripts/
│       └── route_list.md             # 前端路由清单
├── database/                          # 数据库脚本
│   ├── 01_create_database.sql       # 建库脚本
│   ├── 02_create_tables.sql         # 建表脚本
│   ├── 03_create_indexes.sql        # 索引脚本
│   ├── 04_insert_initial_data.sql   # 初始数据
│   ├── 05_create_views.sql           # 视图脚本
│   ├── 06_create_stored_procedures.sql # 存储过程
│   └── 07_test_queries.sql          # 测试查询
├── docs/                              # 项目文档
│   ├── 系统演示流程.md
│   ├── 截图清单.md
│   ├── 最终检查清单.md
│   └── AI项目协作质量审计系统_项目开发文档_整合修订版.md
└── cursor_and_codex_chat/             # 开发记录（AI 协作记录）
    ├── tasks/todo/                    # 任务卡
    └── handoff/                      # 阶段交接文档
```

---

## 后端启动说明

### 环境要求

- Python 3.10+
- MySQL 8.0+

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS/WSL
```

编辑 `.env`，填写以下占位符值：

```env
APP_NAME=AI-Collab-Audit-System
APP_ENV=development
API_PREFIX=/api

SERVER_HOST=0.0.0.0
SERVER_PORT=8000

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<YOUR_DB_PASSWORD>
DB_NAME=ai_collab_audit_system
DB_CHARSET=utf8mb4

JWT_SECRET_KEY=<YOUR_JWT_SECRET_KEY>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

API_KEY_SECRET=<YOUR_32_BYTE_SECRET_BASE64_OR_HEX>
```

### 3. 初始化数据库

在 MySQL 中按顺序执行以下脚本：

```bash
# Step 1: 创建数据库（仅首次执行）
mysql -u root -p < database/01_create_database.sql

# Step 2-7: 在 ai_collab_audit_system 数据库中执行
mysql -u root -p ai_collab_audit_system < database/02_create_tables.sql
mysql -u root -p ai_collab_audit_system < database/03_create_indexes.sql
mysql -u root -p ai_collab_audit_system < database/04_insert_initial_data.sql
mysql -u root -p ai_collab_audit_system < database/05_create_views.sql
mysql -u root -p ai_collab_audit_system < database/06_create_stored_procedures.sql
mysql -u root -p ai_collab_audit_system < database/07_test_queries.sql
```

### 4. 启动后端

```bash
cd backend
python run.py
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

### 5. 后端语法检查

```bash
cd backend
python scripts/check_backend.py
```

当前结果：**49/49 个 Python 文件全部通过语法检查**。

---

## 前端启动说明

### 环境要求

- Node.js 18+

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
copy .env.example .env   # Windows
```

`.env` 默认内容（通常无需修改）：

```env
VITE_APP_TITLE=智研协作 AI 项目质量审计系统
VITE_ROUTER_HISTORY=hash
VITE_BASE_URL=http://127.0.0.1:8000
VITE_PUBLIC_PATH=/
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
```

---

## 数据库初始化说明

### 建库建表（必须按顺序执行）

所有脚本位于 `database/` 目录，依次执行 `01` 到 `07`。具体命令见上方"后端启动说明"第 3 步。

### 初始数据

`database/04_insert_initial_data.sql` 包含以下初始数据：

- **管理员账号**：`admin` / `Admin@123456`（BCrypt 哈希存储）
- **普通用户账号**：`teacher01` / `Teacher@123` 等
- **初始角色**：管理员（admin）、指导老师（teacher）、项目负责人（project_leader）、普通成员（member）
- **示例任务类型**：需求分析、设计文档、代码实现、测试报告、演示文稿、其他
- **示例问题标签**：内容空洞、逻辑混乱、格式不规范、事实错误、过度泛化、其他
- **示例模型供应商与模型**：DeepSeek、OpenAI（Mock），以及各模型下的具体模型条目

---

## 演示账号说明

| 角色 | 用户名 | 初始密码 | 说明 |
|------|--------|----------|------|
| 管理员 | `admin` | `Admin@123456` | 全部功能访问权限 |
| 指导老师 | `teacher01` | `Teacher@123` | 审核功能、项目管理 |
| 项目负责人 | `leader01` | `Leader@123` | 项目创建与成员管理 |
| 普通成员 | `member01` | `Member@123` | 基础功能访问 |

> 初始账号密码由 `database/04_insert_initial_data.sql` 决定。**新用户可通过前台注册页面注册账号（默认 student_member 角色），也可以由管理员在用户管理页面创建。生产环境请务必修改默认密码。

---

## 当前环境限制说明

本项目开发环境存在以下限制，课程报告中的相关截图需在本地完整环境中补做：

1. **远程 Ubuntu 环境无 Node**：前端开发服务器无法在远程 Ubuntu 环境下执行。实际前端构建和运行截图需在本地 Windows Node 环境下完成。

2. **Windows MySQL 需本地验证**：后端接口联调涉及数据库读写的测试用例（如登录、创建项目、创建任务、审核提交等），需要本地 Windows MySQL 环境验证。WSL2/Ubuntu 环境无法直接连接 Windows MySQL 宿主机数据库时，需要通过 `bind-address = 0.0.0.0` 配置或 WSL 虚拟网卡 IP 访问。

3. **实际运行截图待补充**：课程报告中的以下截图需要在本地完整环境（Windows MySQL + Node + Python）补做：
   - 数据库建表成功截图
   - 前后端联调成功截图（登录、项目 CRUD、任务 CRUD 等）
   - 前端完整业务功能截图

4. **Mock 模型说明**：当前 AI 生成模块使用 `MockModelAdapter`，返回模拟数据。扩展真实模型 API 时，只需实现 `ModelAdapter` 接口并在 `model_providers` 表中配置 API Key，无需修改业务代码。

---

## 安全说明

- 所有敏感配置（数据库密码、JWT 密钥、API Key 加密密钥）通过 `.env` 环境变量读取，不硬编码到源码。
- `.env.example` 不包含任何真实密钥，仅作配置模板。
- API Key 在数据库中以 AES-GCM 加密存储，不明文保存。
- 用户密码以 BCrypt 哈希存储，不明文保存。
- 路由按角色分级授权（公开 / 登录用户 / 管理员 / 项目 Owner/Leader）。

---

## 许可证

本项目后端代码采用 MIT License。

前端基于 [V3 Admin Vite](https://github.com/un-pany/v3-admin-vite)（MIT License）二次开发，详见 `frontend/NOTICE.md`。
