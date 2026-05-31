# HANDOFF-013-FIX：Vue3 前端基础框架（基于开源模板二次开发）

## 任务状态

**完成**。

---

## 一、Codex 复审问题

`REVIEW-013-frontend-base.md` 指出 Stage-13 的 P0 阻塞问题：

- 前端"手工实现"，仅"参考 UI 风格"，不符合用户要求"直接基于成熟 Vue3 开源后台模板代码二次开发"
- 未保留模板 LICENSE / NOTICE
- 未在 README 中说明模板来源和许可证

---

## 二、选用的开源模板

| 项目 | 内容 |
|------|------|
| **模板名称** | V3 Admin Vite |
| **GitHub** | https://github.com/un-pany/v3-admin-vite |
| **作者** | pany <https://github.com/pany-ang> |
| **许可证** | MIT License |
| **Copyright** | Copyright (c) 2022-present pany |
| **Stars** | ~2.6K |

选择理由：
- MIT 许可证，商业和非商业使用均友好
- 技术栈（Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router）完全匹配本项目要求
- 结构完整但不过于重型（相比 vue-pure-admin 的 20K stars + TailwindCSS）
- 体量适中，适合课程项目二次开发

---

## 三、本次修改文件

### 新建文件

| 文件 | 说明 |
|------|------|
| `frontend/NOTICE.md` | 开源归属说明（明确模板来源、许可证、修改内容）|
| `frontend/.env.example` | 环境变量示例 |
| `frontend/README.md` | 前端使用说明（含模板来源和许可证说明）|
| `frontend/src/pages/projects/index.vue` | 项目空间（占位）|
| `frontend/src/pages/tasks/index.vue` | 任务管理（占位）|
| `frontend/src/pages/reviews/index.vue` | 审核中心（占位）|
| `frontend/src/pages/artifacts/index.vue` | 成果库（占位）|
| `frontend/src/pages/statistics/index.vue` | 统计看板（占位）|
| `frontend/src/pages/models/index.vue` | 模型管理（占位）|
| `frontend/src/common/assets/images/layouts/logo.svg` | 项目 Logo（SVG）|
| `frontend/src/common/assets/images/layouts/logo-text-1.svg` | 展开 Logo（含文字）|
| `frontend/src/common/assets/images/layouts/logo-text-2.svg` | 展开 Logo（含全称）|

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `frontend/index.html` | 标题改为"智研协作 AI 项目质量审计系统" |
| `frontend/.env` | `VITE_APP_TITLE` 改为项目名称 |
| `frontend/.env.development` | `VITE_BASE_URL` 改为 `http://127.0.0.1:8000` |
| `frontend/package.json` | name/description/author 标注基于模板，保留原作者 |
| `frontend/vite.config.ts` | 端口改为 5173，移除 mock 代理，移除 ViteMcp 插件 |
| `frontend/LICENSE` | 保留（MIT，原模板版权） |
| `frontend/src/App.vue` | 移除 `usePany()` 原作者弹窗通知 |
| `frontend/src/pages/login/index.vue` | 替换为适配后端的登录页（去除验证码，对接 `/api/auth/login`）|
| `frontend/src/pages/login/apis/type.ts` | 登录请求/响应类型适配后端 |
| `frontend/src/pages/login/apis/index.ts` | 移除验证码 API，添加 `logoutApi` |
| `frontend/src/pages/dashboard/index.vue` | 替换为业务首页（欢迎信息 + 流程说明 + 模块入口卡片）|
| `frontend/src/pinia/stores/user.ts` | 对接后端 `/api/auth/me`，添加 `userInfo` 状态，修复 `logout` |
| `frontend/src/common/apis/users/index.ts` | url 改为 `api/auth/me` |
| `frontend/src/common/apis/users/type.ts` | 类型适配后端响应 |
| `frontend/src/router/index.ts` | 移除 demo/permission/link 路由，替换为业务占位路由 |
| `frontend/src/layouts/components/Logo/index.vue` | 使用项目 SVG Logo |
| `frontend/src/layouts/components/NavigationBar/index.vue` | 移除 Notify/SearchMenu 引用，移除原作者 GitHub 链接 |
| `frontend/src/layouts/config.ts` | `showNotify=false`，`showSearchMenu=false` |
| `frontend/src/common/constants/cache-key.ts` | `SYSTEM_NAME` 改为 `ai-collab-audit` |

### 删除文件（模板中不再需要的部分）

| 文件/目录 | 说明 |
|-----------|------|
| `frontend/src/pages/demo/` | 模板示例页面 |
| `frontend/src/pages/login/components/` | 登录猫头鹰动画组件 |
| `frontend/src/pages/login/composables/` | 登录焦点处理 composable |
| `frontend/src/pages/login/images/` | 登录图片资源 |
| `frontend/src/pages/dashboard/components/` | 旧 Dashboard 组件 |
| `frontend/src/pages/dashboard/images/` | 旧 Dashboard 图片 |
| `frontend/src/common/apis/tables/` | 模板表格 API |
| `frontend/src/common/components/Notify/` | 通知组件 |
| `frontend/src/common/components/SearchMenu/` | 搜索菜单组件 |

---

## 四、模板来源和许可证处理

### LICENSE

已保留 V3 Admin Vite 的 MIT License（`frontend/LICENSE`），Copyright 声明归原作者 pany。

### NOTICE.md

已创建 `frontend/NOTICE.md`，包含：
- 模板名称、GitHub 链接、作者
- 许可证（MIT）和 Copyright 声明
- 本项目的 8 项修改说明
- 英文版本归属说明

### README.md

已在 `frontend/README.md` 开头明确说明：
- 基于哪个开源模板
- GitHub 链接
- 许可证
- 本项目的裁剪和修改内容

---

## 五、路由配置

`frontend/src/router/index.ts` 中已移除所有模板示例路由（demo、permission、link），替换为业务占位路由：

| 路径 | 组件 | 说明 |
|------|------|------|
| `/dashboard` | Dashboard | 首页（已实现欢迎页）|
| `/projects` | Projects.vue | 项目空间（占位）|
| `/tasks` | Tasks.vue | 任务管理（占位）|
| `/reviews` | Reviews.vue | 审核中心（占位）|
| `/artifacts` | Artifacts.vue | 成果库（占位）|
| `/statistics` | Statistics.vue | 统计看板（占位）|
| `/models` | Models.vue | 模型管理（占位）|

---

## 六、后端认证接口对接

### 登录（`POST /api/auth/login`）

```typescript
// frontend/src/pages/login/apis/index.ts
loginApi({ username, password })  // -> { token, user }
```

### 当前用户（`GET /api/auth/me`）

```typescript
// frontend/src/common/apis/users/index.ts
getCurrentUserApi()  // -> { user_id, username, real_name, roles, permissions }
```

### 登出（`POST /api/auth/logout`）

```typescript
// frontend/src/pages/login/apis/index.ts
logoutApi()  // 清除本地 token + 跳转登录页
```

### Axios 适配

`frontend/src/http/axios.ts` 适配后端统一返回格式 `{ code: 0, message: "success", data: {} }`：
- `code === 0`：返回 `apiData`（即 `{ code: 0, message, data }`）
- `code !== 0`：显示 `ElMessage.error(message)`
- HTTP 401：调用 `logout()` 清理 token 并重载页面

---

## 七、路由守卫逻辑

`frontend/src/router/guard.ts`：

```typescript
// 未登录 -> 跳转 /login
// 已登录访问 /login -> 跳转 /
// 已登录无角色 -> 调用 getInfo() 获取用户信息
// 路由动态加载（当前阶段 dynamicRoutes 为空数组，所有登录用户共享常驻路由）
```

---

## 八、前端安装依赖命令

```bash
cd frontend
npm install
# 或 pnpm install（模板推荐）
```

---

## 九、前端启动命令

```bash
npm run dev
# http://localhost:5173
```

---

## 十、npm install / npm run build 执行结果

当前环境无 Node.js（`node -v: command not found`），无法执行 `npm install` / `npm run build`。

已进行静态检查：
- `package.json` 存在，scripts 包含 `dev` / `build`
- `vite.config.ts` 存在，端口已改为 5173
- `tsconfig.json` 存在，TypeScript 配置完整
- `src/main.ts` 正确注册 Pinia、Router、Element Plus
- 所有路由组件路径导入正确
- 所有 API 接口路径已适配后端（`api/auth/login`、`api/auth/me`、`api/auth/logout`）

---

## 十一、是否修改 backend/app/main.py

**否**。`backend/app/main.py` 已有 `CORSMiddleware(allow_origins=["*"])`，前端 `localhost:5173` 可直接访问，无需修改。

---

## 十二、是否修改 database

**否**。

---

## 十三、是否修改 docs/01_数据库Schema冻结说明.md

**否**。

---

## 十四、是否实现完整项目管理、任务管理、审核中心、成果库、统计看板页面

**否**。所有业务页面仅为占位，使用 `el-result` 组件展示提示信息。

---

## 十五、验收清单

- [x] 确实基于 V3 Admin Vite 模板代码（MIT License）二次开发
- [x] 保留 V3 Admin Vite LICENSE（MIT）文件
- [x] 创建 NOTICE.md 说明模板来源和许可证
- [x] README.md 说明模板来源、许可证、裁剪修改内容
- [x] 系统品牌已替换为"智研协作 AI 项目质量审计系统"
- [x] 登录页对接 `POST /api/auth/login`（无验证码）
- [x] 用户信息对接 `GET /api/auth/me`
- [x] 登出对接 `POST /api/auth/logout`
- [x] Axios 适配后端 `{ code: 0, message, data }` 格式
- [x] 路由守卫正确：未登录跳转 `/login`，已登录跳转 `/`
- [x] 后台布局完整（左侧导航 + 顶部栏 + 标签栏 + Logo）
- [x] 删除模板示例页面（demo、permission 等）
- [x] 删除原作者弹窗通知（usePany）
- [x] 删除模板通知和搜索菜单组件引用
- [x] 未越界实现完整业务页面
- [x] 未泄露真实密钥
- [x] 未修改数据库结构或 Schema 冻结文档
- [x] 未修改后端业务逻辑
