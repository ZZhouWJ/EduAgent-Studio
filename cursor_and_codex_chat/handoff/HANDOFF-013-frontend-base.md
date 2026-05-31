# HANDOFF-013：Vue3 前端基础框架、登录页和整体布局

## 任务状态

**完成**。

---

## 一、本次修改文件

### 新建文件（Stage-13 产出）

| 文件 | 说明 |
|------|------|
| `frontend/package.json` | 项目依赖配置 |
| `frontend/vite.config.js` | Vite 构建配置 |
| `frontend/index.html` | HTML 入口 |
| `frontend/.env.example` | 环境变量示例 |
| `frontend/README.md` | 前端使用说明 |
| `frontend/src/main.js` | 应用入口 |
| `frontend/src/App.vue` | 根组件 |
| `frontend/src/api/request.js` | Axios 封装 |
| `frontend/src/api/auth.js` | 认证 API 封装 |
| `frontend/src/stores/user.js` | Pinia 用户状态 |
| `frontend/src/router/index.js` | 路由配置与守卫 |
| `frontend/src/components/AppSidebar.vue` | 左侧导航栏 |
| `frontend/src/components/AppHeader.vue` | 顶部用户栏 |
| `frontend/src/layouts/BasicLayout.vue` | 后台整体布局 |
| `frontend/src/views/Login.vue` | 登录页 |
| `frontend/src/views/DashboardHome.vue` | 后台首页 |
| `frontend/src/views/Projects.vue` | 项目空间（占位）|
| `frontend/src/views/Tasks.vue` | 任务管理（占位）|
| `frontend/src/views/Reviews.vue` | 审核中心（占位）|
| `frontend/src/views/Artifacts.vue` | 成果库（占位）|
| `frontend/src/views/Statistics.vue` | 统计看板（占位）|
| `frontend/src/views/Models.vue` | 模型管理（占位）|
| `frontend/src/views/NotFound.vue` | 404 页面 |
| `frontend/src/styles/global.css` | 全局样式 |
| `cursor_and_codex_chat/handoff/HANDOFF-013-frontend-base.md` | 本次交接文档 |

### 未修改文件

- `backend/app/main.py`（已有 `allow_origins=["*"]` CORS 配置，无需修改）
- `database/*`
- `docs/*`
- `backend/app/routers/*`、`backend/app/services/*`、`backend/app/repositories/*`

---

## 二、实现说明

### 实现方式

本前端模块**不基于任何第三方开源后台管理模板**，而是根据 Stage-13 任务要求手工搭建。

选择手工实现的原因：
1. **体量控制**：vue-pure-admin（20K stars，TypeScript+TailwindCSS）和 vue-element-plus-admin（3.6K stars，TypeScript）体量较大，不适合课程项目快速迭代
2. **技术匹配**：纯 JavaScript 实现，无 TypeScript 门槛，更适合课程组自主维护
3. **需求覆盖**：手工轻量骨架已完整覆盖 Stage-13 全部要求

### 开源模板参考说明

以下模板作为 UI 风格参考（未直接使用源码）：

| 模板名称 | 仓库 | 许可证 | 参考内容 |
|----------|------|--------|----------|
| vue-pure-admin | https://github.com/pure-admin/vue-pure-admin | MIT | 后台布局风格、配色方案、菜单交互 |
| vue-element-plus-admin | https://github.com/kailong321200875/vue-element-plus-admin | MIT | 侧边栏折叠、顶部栏设计 |

### 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | Vue 3 (Composition API + `<script setup>`) |
| 构建工具 | Vite 5 |
| UI 组件库 | Element Plus 2.6 |
| 状态管理 | Pinia 2.1 |
| 路由 | Vue Router 4 |
| HTTP 客户端 | Axios 1.6 |

### Axios 封装（`src/api/request.js`）

- `baseURL` 从 `import.meta.env.VITE_API_BASE_URL` 读取，默认 `http://127.0.0.1:8000`
- 请求拦截器自动附加 `Authorization: Bearer <token>`
- 响应拦截器适配后端统一返回格式 `{ code, message, data }`：
  - `code === 0`：resolve 返回 `data`
  - `code !== 0`：reject + Element Plus Message 错误提示
- 401 响应：清除 localStorage，跳转 `/login`
- 无硬编码 token

### 认证 API（`src/api/auth.js`）

| 函数 | 后端接口 | 说明 |
|------|----------|------|
| `login(data)` | `POST /api/auth/login` | 请求体 `{username, password}`，响应 `{token, user}` |
| `getMe()` | `GET /api/auth/me` | 获取当前用户信息（roles、permissions）|
| `logout()` | `POST /api/auth/logout` | 登出 |

### Pinia 用户状态（`src/stores/user.js`）

状态：`token`、`userInfo`、`roles`、`permissions`（均持久化到 localStorage）

Actions：`login()`、`fetchCurrentUser()`、`logout()`、`setToken()`、`setUserInfo()`、`clearSession()`

页面刷新后：构造函数从 localStorage 恢复 token，`fetchCurrentUser()` 从 `/api/auth/me` 恢复用户信息。

### Vue Router（`src/router/index.js`）

嵌套路由结构：`/login`（独立）→ 后台路由（使用 `BasicLayout` 包裹）

路由清单：

| 路径 | 名称 | 组件 | 需登录 |
|------|------|------|--------|
| `/login` | Login | `Login.vue` | 否 |
| `/` | - | 重定向 `/dashboard` | - |
| `/dashboard` | Dashboard | `DashboardHome.vue` | 是 |
| `/projects` | Projects | `Projects.vue`（占位）| 是 |
| `/tasks` | Tasks | `Tasks.vue`（占位）| 是 |
| `/reviews` | Reviews | `Reviews.vue`（占位）| 是 |
| `/artifacts` | Artifacts | `Artifacts.vue`（占位）| 是 |
| `/statistics` | Statistics | `Statistics.vue`（占位）| 是 |
| `/models` | Models | `Models.vue`（占位）| 是 |
| `/404` | NotFound | `NotFound.vue` | 否 |

路由守卫逻辑：

- 未登录访问需认证页面 → 跳转 `/login`（带 `redirect` 查询参数）
- 已登录访问 `/login` → 跳转 `/dashboard`
- 其余直接放行

### 登录页（`src/views/Login.vue`）

- 系统名称：智研协作 AI 项目质量审计系统
- 副标题：面向高校项目协作的 AI 任务生成、版本管理与质量审核平台
- 表单字段：`username`、`password`
- 登录按钮带 loading 状态
- 错误提示由 axios 拦截器统一处理（`ElMessage.error`）
- 登录成功后保存 token 和用户信息，跳转 `/dashboard`
- 不实现注册功能，不出现 `/api/auth/register`
- 不写真实密钥，测试账号以提示信息展示

### 布局（`src/layouts/BasicLayout.vue`）

- 左侧固定导航栏（宽度 220px，可折叠至 64px）
- 顶部用户信息栏（含系统名称、用户名、退出登录按钮）
- 主内容区域 `<router-view>`（含页面切换过渡动画）

左侧导航包含：首页、项目空间、任务与版本、审核中心、成果库、统计看板、模型管理。

### 登录流程说明

```
用户输入用户名密码 → 点击登录
  → userStore.login({ username, password })
    → api.post('/api/auth/login', { username, password })
      → 成功：保存 token → userStore.fetchCurrentUser()
        → 成功：跳转 /dashboard
        → 失败：显示 ElMessage 错误提示
      → 失败：axios 拦截器捕获，显示错误，reject
```

---

## 三、CORS 配置说明

`backend/app/main.py` 已有 CORS 中间件配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

`allow_origins=["*"]` 已覆盖前端 `localhost:5173`，**无需修改** `main.py`。

---

## 四、是否修改 backend

**否**。`backend/app/main.py` 无需修改（已有 CORS 配置）。

---

## 五、是否修改 database

**否**。

---

## 六、是否实现完整业务页面

**否**。以下页面仅为占位，展示了 `el-result` 组件和返回首页按钮：

- `/projects` — Projects.vue（占位）
- `/tasks` — Tasks.vue（占位）
- `/reviews` — Reviews.vue（占位）
- `/artifacts` — Artifacts.vue（占位）
- `/statistics` — Statistics.vue（占位）
- `/models` — Models.vue（占位）

---

## 七、是否实现前端统计看板

**否**。统计数据将在后续阶段接入。

---

## 八、启动命令

### 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

访问：http://localhost:5173

### 后端（需先启动）

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 填写实际数据库密码
python run.py
```

访问：http://localhost:8000/docs

---

## 九、测试方法

1. **环境准备**：启动后端 + 初始化数据库（`database/01` 到 `07`）
2. **语法检查**：前端无 Python，无需 py_compile
3. **依赖安装**：`npm install`（确保 node 18+）
4. **启动前端**：`npm run dev`
5. **登录测试**：
   - 访问 http://localhost:5173，自动跳转 `/login`
   - 输入用户名 `admin`，密码 `Admin@123456`（或数据库中实际初始密码）
   - 点击登录，观察是否进入后台布局
6. **路由守卫测试**：
   - 登录后访问 http://localhost:5173/login，自动跳转 `/dashboard`
   - 清空 localStorage，访问 http://localhost:5173/projects，自动跳转 `/login`
7. **布局测试**：左侧导航切换各模块，确认页面切换正常

---

## 十、已知问题

- 当前环境无 MySQL，登录功能需要后端数据库初始化完成才能真实联调
- 所有占位页面不调用业务接口
- `/api/auth/me` 在页面刷新后调用，需确保后端数据库已初始化

---

## 十一、需要 Codex 审查的重点

1. **技术栈合规**：确认使用 Vue3 + Vite + Element Plus + Pinia + Vue Router，未引入禁止技术栈
2. **登录接口对接**：确认 `POST /api/auth/login` 请求体为 `{username, password}`，未出现 `/api/auth/register`
3. **Token 安全**：确认 axios 拦截器从 localStorage 读取 token，无硬编码
4. **路由守卫**：确认未登录无法访问后台页面，已登录无法访问登录页
5. **CORS**：确认 main.py 无需修改（已有 `allow_origins=["*"]`）
6. **占位页面合规**：确认各业务页面仅为占位，未实现 CRUD、表格、图表
7. **无越界实现**：确认未实现项目管理、任务管理、审核中心、成果库、统计看板的完整页面
8. **无数据库修改**：确认未修改 `database/*`
9. **前端目录结构**：确认符合项目规范（`src/api/`、`src/views/`、`src/components/`、`src/stores/`）
10. **响应格式适配**：确认 axios 拦截器正确处理后端 `{ code, message, data }` 格式
