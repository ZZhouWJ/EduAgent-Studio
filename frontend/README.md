# AI-Collab-Audit-System — Frontend

> 智研协作 AI 项目质量审计系统前端。基于 V3 Admin Vite 模板二次开发。

## 开源模板说明

本项目前端**基于 [V3 Admin Vite](https://github.com/un-pany/v3-admin-vite)** 模板进行二次开发。

| 项目 | 内容 |
|------|------|
| **模板名称** | V3 Admin Vite |
| **GitHub** | https://github.com/un-pany/v3-admin-vite |
| **作者** | pany <https://github.com/pany-ang> |
| **许可证** | MIT License |
| **Copyright** | Copyright (c) 2022-present pany |

详细归属说明请参见 [NOTICE.md](./NOTICE.md)。

### 模板来源合规性

- V3 Admin Vite 采用 MIT 许可证，允许自由使用、复制、修改和分发
- 本项目保留了完整的 LICENSE 文件（MIT License）
- 本项目新增了 NOTICE.md 文件，明确说明模板来源和修改内容
- 本项目未删除原作者版权声明
- 本项目未将模板包装为原创

### 本项目的裁剪与修改

1. 将系统名称、品牌标识替换为"智研协作 AI 项目质量审计系统"
2. 替换登录页，去除验证码逻辑，对接后端 `/api/auth/login` 接口
3. 修改路由配置，替换示例路由为业务占位页面
4. 修改用户状态管理，对接后端 `/api/auth/me` 和 `/api/auth/logout` 接口
5. 修改 Axios 封装，适配后端统一返回格式 `{ code: 0, message: "success", data: {} }`
6. 删除模板自带示例页面（demo、permission 等）
7. 删除模板原 README.zh-CN.md，保留英文版并重写
8. 移除 `.env.production` 和 `.env.staging` 中的 Apifox Mock API 地址
9. 移除 `vite.config.ts` 中的 mock 反向代理配置
10. 替换 Logo 和品牌图片

## 技术栈

| 组件 | 技术 | 来源 |
|------|------|------|
| 框架 | Vue 3 (Composition API) | 模板 |
| 构建工具 | Vite 7 | 模板 |
| UI 组件库 | Element Plus 2.13 | 模板 |
| 状态管理 | Pinia 3.0 | 模板 |
| 路由 | Vue Router 4.6 | 模板 |
| HTTP 客户端 | Axios 1.13 | 模板 |
| 图标 | @element-plus/icons-vue | 模板 |
| CSS 方案 | UnoCSS + Sass | 模板 |
| 语言 | TypeScript | 模板 |

## 环境要求

- Node.js 18+
- npm 或 pnpm

## 安装依赖

```bash
cd frontend

# npm
npm install

# 或 pnpm（模板推荐）
pnpm install
```

## 配置

> **重要**：本项目**不使用** V3 Admin Vite 原模板的 Apifox Mock API。所有环境变量中的 API 地址均指向本项目 FastAPI 后端。

### 环境变量文件说明

| 文件 | 用途 | VITE_BASE_URL 默认值 |
|------|------|---------------------|
| `.env` | 所有环境共享 | `http://127.0.0.1:8000` |
| `.env.development` | 开发环境 | `http://127.0.0.1:8000` |
| `.env.staging` | 预发布环境 | `http://127.0.0.1:8000`（需替换为实际地址）|
| `.env.production` | 生产环境 | `http://127.0.0.1:8000`（需替换为实际地址）|

### 修改步骤

复制环境变量示例文件：

```bash
cp .env.example .env
```

`.env` 默认内容：

```env
VITE_APP_TITLE = 智研协作 AI 项目质量审计系统
VITE_ROUTER_HISTORY = hash
VITE_BASE_URL = http://127.0.0.1:8000
VITE_PUBLIC_PATH = /
```

- **本地开发**：`VITE_BASE_URL` 保持 `http://127.0.0.1:8000` 即可
- **预发布/生产**：请将 `.env.staging` / `.env.production` 中的 `VITE_BASE_URL` 替换为实际后端服务器地址

## 启动开发服务器

```bash
npm run dev
# 或 pnpm
pnpm dev
```

访问：http://localhost:5173

## 构建生产版本

```bash
npm run build
# 或 pnpm
pnpm build
```

## 测试账号

后端数据库初始化后，默认测试账号：

- 用户名：`admin`
- 密码：`Admin@123456`

> 初始账号密码由 `database/04_insert_initial_data.sql` 决定。

## 当前阶段实现范围

Stage-13 仅完成前端基础框架和登录功能，包括：

- [x] 基于 V3 Admin Vite 模板二次开发
- [x] Vue3 + Vite + TypeScript + Element Plus 项目基础结构
- [x] Pinia 用户状态管理
- [x] Vue Router 路由基础（含守卫）
- [x] 登录页（对接 `/api/auth/login`、`/api/auth/me`）
- [x] 后台管理整体布局（左侧导航 + 顶部栏 + 标签栏）
- [x] 首页占位（Dashboard）

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
├── .env.example              # 环境变量示例
├── .env                      # 环境变量（勿提交）
├── LICENSE                   # MIT 许可证（来自 V3 Admin Vite）
├── NOTICE.md                 # 开源归属说明
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── App.vue              # 根组件
    ├── main.ts              # 应用入口
    ├── common/              # 通用模块（来自模板）
    │   ├── assets/         # 静态资源（含品牌 Logo）
    │   ├── components/      # 通用组件
    │   ├── composables/     # 组合式函数
    │   ├── constants/       # 常量
    │   └── utils/          # 工具函数
    ├── http/
    │   └── axios.ts        # Axios 封装（已适配后端统一返回格式）
    ├── layouts/             # 后台布局组件（来自模板）
    │   ├── components/     # 布局子组件
    │   ├── modes/          # 布局模式
    │   └── config.ts
    ├── pages/              # 页面组件
    │   ├── dashboard/      # 首页（已替换为业务内容）
    │   ├── projects/       # 项目空间（占位）
    │   ├── tasks/          # 任务管理（占位）
    │   ├── reviews/         # 审核中心（占位）
    │   ├── artifacts/       # 成果库（占位）
    │   ├── statistics/      # 统计看板（占位）
    │   ├── models/          # 模型管理（占位）
    │   ├── login/           # 登录页（已适配后端接口）
    │   ├── error/           # 错误页
    │   └── redirect/        # 重定向页
    ├── pinia/               # 状态管理（来自模板）
    │   └── stores/
    ├── plugins/             # 插件（来自模板）
    └── router/              # 路由配置（已替换为业务路由）
```

## 与后端联调

1. 确保后端已启动（`cd backend && python run.py`）
2. 确保数据库已初始化（执行 `database/01` 到 `07` 脚本）
3. 确认 `.env` 中 `VITE_BASE_URL` 指向正确后端地址
4. 使用测试账号登录

## 常见问题

### Q1: 编译报 TS 错误

确保使用 V3 Admin Vite 推荐的 Node 18+ 环境：

```bash
node -v  # 应 >= 18
npm install
npm run build
```

### Q2: 登录后跳转白屏

检查浏览器控制台是否有跨域错误。确保后端 `backend/app/main.py` 已配置 CORS 中间件（已默认启用 `allow_origins=["*"]`）。

### Q3: 环境变量修改后不生效

Vite 的环境变量需要重启开发服务器：

```bash
# 修改 .env 后
npm run dev
```
