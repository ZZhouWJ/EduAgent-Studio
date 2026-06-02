# AI-Collab-Audit-System — Frontend

> 智研协作 AI 项目质量审计系统前端。轻量 Vue3 演示版。

## 背景说明

本前端原基于 V3 Admin Vite 模板开发。由于模板在本地运行中持续出现端口、代理、CORS、登录链路等问题，项目决定放弃复杂模板，改为重写一个轻量 Vue3 前端演示版，保证课程演示稳定可用。

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 (Composition API) | ^3.5 |
| 构建工具 | Vite | ^7.0 |
| UI 组件库 | Element Plus | ^2.13 |
| 状态管理 | Pinia | ^3.0 |
| 路由 | Vue Router | ^4.6 |
| HTTP 客户端 | Axios | ^1.13 |
| 语言 | TypeScript | ^5.9 |

## 环境要求

- Node.js 18+
- npm 或 pnpm

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

## 启动后端

```bash
cd backend
# 首次需要创建虚拟环境和安装依赖
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 启动后端（默认端口 8000，与前端 proxy target 一致）
python run.py
```

> 前端 Vite proxy 将 `/api/*` 请求转发到 `http://127.0.0.1:8000`，不直接在浏览器跨域请求后端。

## 配置

环境变量文件 `.env.development`：

```env
VITE_PUBLIC_PATH=/
```

Vite proxy 配置在 `vite.config.ts` 中，target 为 `http://127.0.0.1:8000`。

## 测试账号

- 用户名：`admin`
- 密码：`admin123`

> 账号由 `database/04_insert_initial_data.sql` 初始化。

## 已实现页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录页 | `/login` | 对接 `/api/auth/login`、`/api/auth/me`，支持跳转注册 |
| 注册页 | `/register` | 用户注册，默认分配 student_member 角色 |
| 首页 Dashboard | `/dashboard` | 流程卡片、模块入口 |
| 项目空间 | `/projects` | 项目列表（搜索/状态筛选）+ 创建项目 |
| 项目详情 | `/projects/:projectId` | 7 Tab：概览/成员/任务/成果/调用/日志/统计 |
| 任务与版本 | `/tasks` | 全局任务列表 |
| 任务详情 | `/tasks/:taskId` | 任务信息 + 分支管理 + AI 生成 + 输出版本 + 批注协作 |
| AI 生成 | `/generate` | 全局 AI 生成入口 |
| 提示词管理 | `/prompts` | 模板列表 + 版本管理（创建/编辑/激活） |
| 审核中心 | `/reviews` | 三 Tab：待审核/我提交的/审核历史，评分仪表盘，问题标签 |
| 成果库 | `/artifacts` | 成果列表（项目/类型筛选）+ Markdown 导出 |
| 调用审计 | `/invocations` | 调用日志（项目/模型/状态/日期筛选）+ 详情对话框 |
| 成本统计 | `/costs` | 四摘要卡片 + 按模型/按项目统计（可排序） |
| 统计看板 | `/statistics` | 概览统计、调用、成本、审核质量、成员贡献、最近动态 |
| 模型管理 | `/models` | 供应商 + 模型列表 + 启用禁用 |
| 用户管理 | `/users` | 用户列表（搜索/状态筛选）+ 启用禁用 + 角色分配 |
| 操作日志 | `/logs/operation` | 操作日志（操作人/对象/类型/日期筛选）+ 变更详情 |
| 登录日志 | `/logs/login` | 登录记录（状态/日期筛选）+ IP/UA 信息 |
| 个人中心 | `/profile` | 用户信息展示 + 修改密码 |

## 未实现或简化内容

- 复杂动态权限系统（当前为路由级守卫）
- 标签栏（tags-view）已移除
- 主题切换、暗色模式已移除
- 独立分支合并管理页面（合并功能在任务详情内）
- 独立版本对比页面（时间线对比在任务详情内）

## 目录结构

```
frontend/
├── .env.development         # 开发环境变量
├── .env.example            # 环境变量示例
├── index.html
├── package.json
├── vite.config.ts          # Vite 配置（含 proxy）
├── tsconfig.json
└── src/
    ├── App.vue              # 根组件
    ├── main.ts             # 应用入口
    ├── assets/
    │   └── main.css       # 全局样式
    ├── layouts/
    │   └── BackendLayout.vue  # 后台整体布局（侧边栏+顶部栏+内容区）
    ├── pages/
    │   ├── login/          # 登录页
    │   ├── register/        # 注册页
    │   ├── dashboard/       # 首页
    │   ├── projects/        # 项目列表、详情（7 Tab）
    │   ├── tasks/           # 任务列表、详情（分支+版本+AI生成）
    │   ├── generate/        # AI 生成
    │   ├── prompts/         # 提示词管理
    │   ├── reviews/         # 审核中心
    │   ├── artifacts/       # 成果库
    │   ├── invocations/     # 调用审计
    │   ├── costs/           # 成本统计
    │   ├── statistics/       # 统计看板
    │   ├── models/          # 模型管理
    │   ├── users/           # 用户管理
    │   ├── profile/         # 个人中心
    │   └── logs/            # 操作日志、登录日志
    ├── api/
    │   ├── auth.ts         # 认证（登录/注册/用户/角色）
    │   ├── projects.ts      # 项目 CRUD + 成员
    │   ├── tasks.ts         # 任务 + 分支 + 输出 + 批注
    │   ├── models.ts        # 模型管理 + 任务类型
    │   ├── reviews.ts       # 审核
    │   ├── artifacts.ts      # 成果
    │   ├── invocations.ts   # 调用日志
    │   ├── costs.ts         # 成本统计
    │   ├── logs.ts          # 操作日志 + 登录日志
    │   ├── statistics.ts    # 统计看板
    │   └── prompts.ts       # 提示词模板
    ├── router/
    │   ├── index.ts        # 路由定义（静态路由，含 18 个页面）
    │   └── guard.ts        # 路由守卫（未登录重定向）
    ├── stores/
    │   └── user.ts         # 用户状态（token + 用户信息）
    └── utils/
        └── request.ts       # Axios 封装（统一响应拦截）
```

## 与后端联调

1. 确保 MySQL 数据库已初始化（执行 `database/01` ~ `07` 脚本）
2. 启动后端：`python run.py --port 8002`
3. 启动前端：`npm run dev`
4. 打开 http://localhost:5173 → 自动跳转登录页
5. 使用测试账号登录

## 常见问题

### Q1: 登录后白屏

检查后端是否在 8002 端口运行，proxy target 是否匹配。

### Q2: API 请求 404

确认后端已启动，端口与 proxy target 一致（默认 8002）。

### Q3: 编译报 TS 错误

确保 Node >= 18，重新 `npm install`。
