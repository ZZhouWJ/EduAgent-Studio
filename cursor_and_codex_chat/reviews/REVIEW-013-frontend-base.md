# REVIEW-013: Stage-13 Vue3 前端基础框架审查报告

## 1. 审查结论

**不通过**

Stage-13 当前实现完成了 Vue3 + Vite + Element Plus + Pinia + Vue Router + Axios 的基础骨架、登录页、后台布局、路由守卫和占位页；但它明确不是基于成熟 Vue3 开源后台模板二次开发，而是手工实现。

用户在 Stage-13 开发中已进一步明确要求：前端 UI 希望“直接基于成熟 Vue3 开源作品的代码进行二次开发”，不是完全从零手写普通后台模板。因此本轮必须判定不通过，不允许进入 Stage-14。

## 2. 是否真正基于成熟 Vue3 开源模板二次开发

**否。**

`cursor_and_codex_chat/handoff/HANDOFF-013-frontend-base.md` 和 `frontend/README.md` 都明确写明：

- “本前端模块不基于任何第三方开源后台管理模板”
- “而是根据 Stage-13 任务要求手工搭建”
- vue-pure-admin 和 vue-element-plus-admin 仅作为 UI 风格参考，未直接使用源码

这与用户最新要求冲突。用户要求的是“直接基于成熟 Vue3 开源作品的代码进行二次开发”，不是“参考 UI 风格后手写”。

## 3. 如果未使用开源模板，是否与用户最新要求冲突

**冲突。**

Cursor 未经过用户确认就以“体量控制”“技术匹配”等理由选择手写轻量骨架。根据本轮用户明确规则：

> 如果完全手写，且未使用开源模板代码底座，应判定为不通过。

因此这是 Stage-13 的 P0 阻塞问题。

## 4. 开源许可证和来源说明是否合规

**不满足本轮要求。**

当前前端只是列出参考模板：

- vue-pure-admin
- vue-element-plus-admin

但没有实际使用模板代码底座，也没有保留模板 `LICENSE`、`NOTICE` 或版权声明文件。若后续按要求改为基于成熟模板二次开发，必须：

1. 明确模板名称；
2. 明确 GitHub 来源链接；
3. 确认许可证兼容；
4. 保留原模板 LICENSE / NOTICE / copyright 声明；
5. 在 `frontend/README.md` 和 handoff 中说明哪些模板代码被保留、哪些被裁剪、哪些被二次开发；
6. 不得把模板原项目包装成自己的原创。

## 5. Stage-13 是否遵守任务范围

**部分通过。**

已实现内容基本属于前端基础框架、登录页和整体布局范围：

- 登录页；
- 后台布局；
- 左侧导航；
- 顶部用户栏；
- 路由守卫；
- Pinia 用户状态；
- Axios 封装；
- 占位业务页面。

未发现实际完整项目管理、任务管理、审核中心、成果库或统计看板 CRUD 页面。

需要注意：

- `frontend/src/api/` 下存在多个 0 字节业务 API 文件；
- `frontend/src/views/` 下存在多个 0 字节业务页面文件；
- 这些文件目前未形成实际业务实现，但应在修复时清理或明确为模板裁剪遗留占位，避免误导后续阶段。

## 6. 前端技术栈是否正确

**通过。**

`frontend/package.json` 使用：

- Vue 3
- Vite 5
- Element Plus
- Pinia
- Vue Router 4
- Axios
- `@element-plus/icons-vue`

未发现 React、Next.js、SvelteKit 等不符合项目技术路线的框架。

## 7. Axios 封装是否正确

**基本通过。**

`frontend/src/api/request.js`：

- `baseURL` 从 `VITE_API_BASE_URL` 读取，默认 `http://127.0.0.1:8000`；
- 请求拦截器自动携带 `Authorization: Bearer <token>`；
- 响应拦截器适配后端 `{ code, message, data }`；
- `code === 0` 返回 `data`；
- `code !== 0` 提示错误并 reject；
- HTTP 401 时清理本地 token 并跳转 `/login`；
- 未发现硬编码真实 token、密码或 API Key。

小建议：后端业务错误通常以 HTTP 200 + `code != 0` 返回，若其中包含 `4002` 未登录，也应考虑清理会话并跳转登录页。当前 `fetchCurrentUser()` catch 后会清理 session，登录恢复路径可用，因此不作为本轮阻塞。

## 8. Auth API 是否正确

**通过。**

`frontend/src/api/auth.js` 封装：

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`

登录请求字段为 `username` / `password`，未调用不存在的 `/api/auth/register`。

## 9. Pinia 用户状态是否正确

**通过。**

`frontend/src/stores/user.js`：

- 保存 `token`；
- 保存 `userInfo`；
- 保存 `roles`；
- 保存 `permissions`；
- 提供 `login()`；
- 提供 `fetchCurrentUser()`；
- 提供 `logout()`；
- 从 `localStorage` 恢复 token；
- 未保存 password 或 API Key。

## 10. Router 和路由守卫是否正确

**通过。**

已包含：

- `/login`
- `/dashboard`
- `/projects`
- `/tasks`
- `/reviews`
- `/artifacts`
- `/statistics`
- `/models`
- `/404`

路由守卫：

- 未登录访问后台页面跳转 `/login`；
- 已登录访问 `/login` 跳转 `/dashboard`。

## 11. 登录页是否正确

**基本通过。**

`frontend/src/views/Login.vue`：

- 展示系统名称“智研协作 AI 项目质量审计系统”；
- 有产品副标题；
- 有 username / password；
- 有登录按钮和 loading 状态；
- 调用 Pinia `login()`，间接对接 `/api/auth/login`；
- 登录成功后调用 `/api/auth/me` 恢复用户信息；
- 登录成功后跳转 `/dashboard`；
- 未实现注册功能；
- 未调用 `/api/auth/register`。

说明：页面中展示 `admin / Admin@123456` 作为数据库初始化后的测试账号提示。该信息来自课程初始化数据说明，属于提示而非自动登录逻辑，本轮不视为密钥泄露。

## 12. 后台布局是否正确

**基本通过。**

`BasicLayout`、`AppSidebar`、`AppHeader` 提供：

- 左侧导航栏；
- 顶部用户信息栏；
- 主内容 `router-view`；
- 折叠菜单；
- 退出登录；
- 首页、项目空间、任务与版本、审核中心、成果库、统计看板、模型管理菜单。

但由于整体不是基于成熟开源模板底座，视觉成熟度和模板合规仍不满足用户最新要求。

## 13. 占位页是否没有越界实现业务

**通过。**

当前实际路由中的 `Projects.vue`、`Tasks.vue`、`Reviews.vue`、`Artifacts.vue`、`Statistics.vue`、`Models.vue` 均为 `el-result` 占位页，未实现完整业务 CRUD。

`DashboardHome.vue` 为静态欢迎页和流程介绍，未调用真实统计接口，未伪造真实统计数据。

## 14. 是否发现真实密钥泄露

**未发现真实密钥泄露。**

检查范围：

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-013-frontend-base.md`

未发现真实数据库密码、真实 API Key、真实 JWT Secret、完整 `sk-` 密钥或真实 token。

`Admin@123456` 仅作为测试账号提示出现，不是自动登录逻辑。

## 15. 是否发现越界修改

**未发现新增后端业务逻辑或前端完整业务页面。**

但工作区状态显示：

- `backend/app/main.py` 处于修改状态；
- `database/*` 和 `docs/01_数据库Schema冻结说明.md` 仍处于修改状态。

Handoff 声明 Stage-13 未修改这些文件，当前状态更像前序阶段累积未提交改动。本轮未发现 Stage-13 为前端基础框架新增后端业务接口、service 或 repository。

## 16. 启动可行性检查

当前远程 Ubuntu 环境执行：

```bash
node -v
```

结果：`node: command not found`。

因此无法在当前环境执行：

```bash
npm install
npm run build
```

已进行静态检查：

- `package.json` 存在 `dev` / `build` / `preview`；
- `vite.config.js` 存在；
- `src/main.js` 正确创建 app、安装 Pinia、Router、Element Plus；
- `src/App.vue` 正常渲染 `<router-view />`；
- router / store / api 路径导入基本一致。

## 17. 是否允许进入 Stage-14

**不允许。**

原因：Stage-13 未满足用户最新明确要求“直接基于成熟 Vue3 开源后台模板代码底座二次开发”。

## 18. 必须修复的问题

### P0：改为真正基于成熟 Vue3 开源后台模板二次开发

Cursor 必须重新处理前端基础框架：

1. 选择一个成熟、许可证兼容的 Vue3 后台管理模板作为代码底座，例如：
   - vue-pure-admin；
   - vue-element-plus-admin；
   - Vben Admin；
   - Soybean Admin；
   - V3 Admin Vite；
   - 或其他明确 Vue3 后台模板。
2. 在使用前确认模板许可证允许课程项目二次开发。
3. 保留模板 LICENSE / NOTICE / copyright 声明。
4. 在 `frontend/README.md` 写明：
   - 模板名称；
   - GitHub 链接；
   - 许可证；
   - 本项目如何裁剪和二次开发；
   - 保留了哪些模板目录或核心代码。
5. 在 `HANDOFF-013-FIX-frontend-base.md` 中说明模板来源和许可证处理。
6. 删除或隐藏模板自带无关业务页面、Mock 数据和品牌 Logo。
7. 将系统品牌替换为“智研协作 AI 项目质量审计系统”。
8. 保留 Stage-13 已要求的登录页、布局、路由守卫、Axios、Pinia 对接。

### P1：清理空文件和交接不一致

当前 `frontend/src/api/`、`frontend/src/views/`、`frontend/src/components/` 中存在多个 0 字节文件。修复时应：

- 删除无用空文件；或
- 明确它们是模板裁剪后的占位文件，并避免被路由或 import 引用。

### P1：补充可构建验证

修复后应在具备 Node 环境的位置执行：

```bash
cd frontend
npm install
npm run build
```

并在 handoff 中记录结果。如果当前环境仍无 Node，需要明确说明原因。

## 19. Stage-14 发布情况

未发布 `TASK-014-frontend-project-task-pages.md`。
