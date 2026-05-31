# TASK-013: Vue3 前端基础框架、登录页和整体布局

## 任务目标

完成 Vue3 前端基础框架、登录页和后台管理整体布局，为后续项目、任务、审核、成果库和统计页面开发提供稳定前端骨架。

## 允许实现内容

1. `frontend` 项目基础结构；
2. Vue3 + Vite 初始化；
3. Element Plus / Naive UI 依赖；
4. Axios 封装；
5. Pinia 用户状态；
6. Vue Router 路由基础；
7. 登录页；
8. 后台管理整体布局；
9. 左侧导航栏；
10. 顶部用户信息栏；
11. 路由守卫基础；
12. 与后端 `/api/auth/login`、`/api/auth/me` 对接的基础逻辑。

## 允许修改

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-013-frontend-base.md`

如确实需要补充跨域配置，可少量修改：

- `backend/app/main.py`

但必须在 handoff 中说明理由。

## 禁止修改

- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 前端项目管理完整页面；
2. 前端任务管理完整页面；
3. 前端审核中心完整页面；
4. 前端成果库完整页面；
5. 前端统计看板完整页面。

## 前端实现要求

1. 使用 Vue3 + Vite，不得替换为 React、Next.js 或其他技术栈。
2. 使用 Pinia 保存当前登录用户、Token、角色和权限基础信息。
3. 使用 Vue Router 建立基础路由：
   - `/login`
   - `/`
   - `/dashboard` 或等价首页占位
4. 登录页对接后端：
   - `POST /api/auth/login`
   - `GET /api/auth/me`
5. Axios 封装必须：
   - 统一 `baseURL`
   - 自动携带 `Authorization: Bearer <token>`
   - 识别后端统一返回格式 `code/message/data`
   - 对未登录或 Token 失效做基础处理
6. 后台布局必须包含：
   - 左侧导航栏；
   - 顶部用户信息栏；
   - 主内容区域；
   - 登出入口。
7. 页面占位可以存在，但不得实现后续完整业务页面。

## 交付要求

完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-013-frontend-base.md`

handoff 中必须说明：

1. 修改了哪些文件；
2. 前端安装依赖命令；
3. 前端启动命令；
4. 登录页如何对接后端；
5. 路由守卫逻辑；
6. 是否修改 `backend/app/main.py`，如有必须说明原因；
7. 未修改 `database/*`、未修改 `docs/01_数据库Schema冻结说明.md`；
8. 未实现项目管理、任务管理、审核中心、成果库、统计看板完整页面。

## 验收标准

1. 前端项目可安装依赖并启动；
2. 登录页可提交用户名和密码；
3. 登录成功后保存 Token，并进入后台布局；
4. 刷新后可通过 `/api/auth/me` 恢复当前用户信息；
5. 未登录访问后台路由会跳转到登录页；
6. 后台布局显示左侧导航、顶部用户信息栏和内容区；
7. 没有实现 Stage-14 及后续完整业务页面；
8. 没有修改数据库结构或 Schema 文档。
