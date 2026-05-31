# AI-Collab-Audit-System — Frontend

> 智研协作 AI 项目质量审计系统前端。基于 Vue3 + Vite + Element Plus + Pinia + Vue Router 手工实现。

## 实现说明

本前端模块**不基于任何第三方开源后台管理模板**，而是根据 Stage-13 任务要求手工搭建。

### 为什么选择手工实现而非模板

1. **体量控制**：vue-pure-admin（20K stars）和 vue-element-plus-admin（3.6K stars）均为 TypeScript + TailwindCSS 技术栈，体量较大，不适合课程项目的快速迭代和完全自主可控要求。
2. **技术匹配**：本项目后端采用 Python FastAPI，前端使用原生 JavaScript（而非 TypeScript）可降低课程组学习和维护成本。
3. **需求覆盖**：手工实现的轻量骨架已完整覆盖 Stage-13 全部要求：登录、布局、导航、路由守卫、占位页面。

如后续需要更丰富的前端组件和样式，可考虑引入模板作为参考。

### 开源模板参考说明

以下模板在本项目开发过程中作为 UI 风格参考（未直接使用源码）：

| 模板名称 | 仓库 | 技术栈 | 参考内容 |
|----------|------|--------|----------|
| vue-pure-admin | https://github.com/pure-admin/vue-pure-admin | Vue3 + TypeScript + TailwindCSS + Element Plus | 后台布局风格、配色方案、菜单交互 |
| vue-element-plus-admin | https://github.com/kailong321200875/vue-element-plus-admin | Vue3 + TypeScript + Element Plus | 侧边栏折叠、顶部栏设计 |

以上模板均为 MIT 许可证。

## 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | Vue 3 (Composition API) |
| 构建工具 | Vite 5 |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| HTTP 客户端 | Axios |
| 图标 | @element-plus/icons-vue |

## 环境要求

- Node.js 18+
- npm 或 yarn

## 安装依赖

```bash
cd frontend
npm install
```

## 配置

复制环境变量示例文件：

```bash
cp .env.example .env
```

`.env` 内容（开发环境默认配置）：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

> 如果后端在其他地址或端口，请修改 `VITE_API_BASE_URL`。

## 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

## 构建生产版本

```bash
npm run build
npm run preview
```

## 测试账号

后端数据库初始化后，默认测试账号：

- 用户名：`admin`
- 密码：`Admin@123456`

> 初始账号密码由 `database/04_insert_initial_data.sql` 决定。

## 当前阶段实现范围

Stage-13 仅完成前端基础框架和登录功能，包括：

- [x] Vue3 + Vite 项目基础结构
- [x] Element Plus UI 集成
- [x] Pinia 用户状态管理
- [x] Vue Router 路由基础（含守卫）
- [x] 登录页（对接 `/api/auth/login`、`/api/auth/me`）
- [x] 后台管理整体布局（左侧导航 + 顶部栏）
- [x] 首页占位（DashboardHome）

以下模块在本阶段仅为占位页面，**不实现完整业务功能**：

| 页面 | 路由 | 说明 |
|------|------|------|
| 项目空间 | `/projects` | 占位 |
| 任务与版本 | `/tasks` | 占位 |
| 审核中心 | `/reviews` | 占位 |
| 成果库 | `/artifacts` | 占位 |
| 统计看板 | `/statistics` | 占位 |
| 模型管理 | `/models` | 占位 |

## 目录结构

```
frontend/
├── .env.example           # 环境变量示例
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js            # 应用入口
    ├── App.vue            # 根组件
    ├── api/
    │   ├── request.js     # Axios 封装
    │   └── auth.js        # 认证 API
    ├── components/
    │   ├── AppSidebar.vue  # 左侧导航栏
    │   └── AppHeader.vue   # 顶部用户栏
    ├── layouts/
    │   └── BasicLayout.vue # 后台整体布局
    ├── router/
    │   └── index.js       # 路由配置与守卫
    ├── stores/
    │   └── user.js        # Pinia 用户状态
    └── views/
        ├── Login.vue       # 登录页
        ├── DashboardHome.vue # 首页
        ├── Projects.vue     # 项目空间（占位）
        ├── Tasks.vue        # 任务管理（占位）
        ├── Reviews.vue      # 审核中心（占位）
        ├── Artifacts.vue    # 成果库（占位）
        ├── Statistics.vue   # 统计看板（占位）
        ├── Models.vue       # 模型管理（占位）
        └── NotFound.vue     # 404 页面
```

## 与后端联调

1. 确保后端已启动（`cd backend && python run.py`）
2. 确保数据库已初始化（执行 `database/01` 到 `07` 脚本）
3. 确认 `.env` 中 `VITE_API_BASE_URL` 指向正确后端地址
4. 使用测试账号登录

## 常见问题

### Q1: 图标不显示

确保已安装 `@element-plus/icons-vue`：

```bash
npm install @element-plus/icons-vue
```

### Q2: 登录后跳转白屏

检查浏览器控制台是否有跨域错误。确保后端 `backend/app/main.py` 已配置 CORS 中间件。

### Q3: `VITE_API_BASE_URL` 修改后不生效

Vite 的环境变量需要重启开发服务器：

```bash
# 修改 .env 后
npm run dev
```
