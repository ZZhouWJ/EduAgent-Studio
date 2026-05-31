# REVIEW-013-FIX: Stage-13 Fix 前端基础框架复审报告

## 1. 审查结论

**需要继续修改**

上一轮阻塞点“前端是否真正基于成熟 Vue3 开源后台模板二次开发”已经修复：当前 `frontend/` 明确基于 **V3 Admin Vite**，保留了模板结构、布局、路由、Pinia、Axios、Element Plus、UnoCSS 等代码底座，并补充了 `LICENSE` 与 `NOTICE.md`。

但本轮发现新的阻塞问题：`frontend/.env.production` 与 `frontend/.env.staging` 仍保留原模板 Apifox Mock API 地址，生产 / 预发布构建会默认访问模板 Mock 服务，而不是本项目后端接口。这违反“不得保留模板 Mock 数据作为真实业务数据”的要求，也会破坏 Stage-13 与后端认证接口的真实对接。

因此暂不允许进入 Stage-14，不发布 `TASK-014-frontend-project-task-pages.md`。

## 2. 是否真正基于成熟 Vue3 开源模板二次开发

**已修复。**

已明确使用：

- 模板名称：V3 Admin Vite
- GitHub：https://github.com/un-pany/v3-admin-vite
- 许可证：MIT License
- 原作者：pany

`frontend/` 中可见模板代码底座，包括：

- `src/layouts/`
- `src/router/`
- `src/pinia/`
- `src/http/axios.ts`
- `src/common/`
- `src/plugins/`
- `uno.config.ts`
- `vite.config.ts`
- `types/auto/`

这不是继续手写 19 个文件，上一轮 P0 阻塞点已解决。

## 3. 模板来源和许可证是否说明

**基本符合要求。**

已存在：

- `frontend/LICENSE`
- `frontend/NOTICE.md`
- `frontend/README.md`
- `cursor_and_codex_chat/handoff/HANDOFF-013-FIX-frontend-base.md`

以上文件均说明了 V3 Admin Vite 的来源、GitHub 链接、MIT 许可证和原作者版权声明。未发现使用 LobeChat / Open WebUI 的 React / Svelte 源码冒充 Vue3。

需要注意：`frontend/README.zh-CN.md` 仍是原模板 README，`src/common/composables/usePany.ts` 也仍保留原模板推广链接，但当前未作为本项目业务入口使用。建议后续清理或标注为模板原始文档，避免课程报告中误认为仍是模板原系统。

## 4. 是否完成本项目品牌替换

**主要入口已替换。**

已替换为：

- 系统名称：智研协作 AI 项目质量审计系统
- 登录页标题与副标题
- 后台 Logo / 顶部品牌
- 左侧菜单：首页、项目空间、任务与版本、审核中心、成果库、统计看板、模型管理
- `index.html` 标题
- `frontend/README.md`

未发现活动路由中继续展示模板原业务菜单。

## 5. 登录、布局、路由、状态管理是否符合要求

**基本符合 Stage-13 要求。**

已检查：

- Vue3 + Vite + TypeScript 存在；
- Element Plus 存在；
- Pinia 存在；
- Vue Router 存在；
- Axios 存在；
- `frontend/.env.example` 存在；
- 登录页存在；
- 后台基础布局存在；
- 左侧导航栏存在；
- 顶部用户信息栏存在；
- 路由守卫存在；
- 项目、任务、审核、成果、统计、模型页面均为占位页，未实现完整 CRUD。

认证接口适配情况：

- `POST /api/auth/login`：已封装；
- `GET /api/auth/me`：已封装；
- `POST /api/auth/logout`：已封装；
- 登录字段为 `username / password`；
- 未发现调用 `/api/auth/register`；
- Axios 已按 `{ code, message, data }` 统一返回格式处理；
- token 保存到 localStorage / Pinia；
- 未发现把 `Admin@123456` 写成自动登录逻辑，仅作为测试账号说明展示。

## 6. 是否发现真实密钥泄露

**未发现真实密钥泄露。**

未发现：

- 真实数据库密码；
- 真实 API Key；
- 真实 JWT Secret；
- 完整 `sk-` 开头密钥；
- 真实 token。

`Admin@123456` 仅作为初始化测试账号提示出现，不是自动登录逻辑。

## 7. 是否发现越界实现

**未发现 Stage-14 业务页面越界实现。**

未发现：

- 完整项目管理页面；
- 完整任务管理页面；
- 完整审核中心页面；
- 完整成果库页面；
- 完整统计看板页面；
- 新增后端业务接口；
- 修改后端 service / repository 业务逻辑；
- 发布 `TASK-014-frontend-project-task-pages.md`。

工作区中 `database/`、`docs/01_数据库Schema冻结说明.md`、大量后端文件显示已有修改，但这些是历史阶段遗留的未提交状态；本轮 Stage-13 Fix 的 handoff 声明未修改后端和数据库。本轮未发现前端修复需要直接改动这些文件。

## 8. 启动或静态检查结果

远程环境仍未安装 Node.js：

```text
node: command not found
```

因此无法执行：

```bash
cd frontend
npm install
npm run build
```

已改为静态审查：

- `package.json` 存在；
- `dev` / `build` 脚本存在；
- `vite.config.ts` 存在；
- `src/main.ts` 可见 Vue app 挂载逻辑；
- `src/App.vue` 存在；
- router / Pinia / Axios 目录路径基本正确；
- 未发现明显语法级缺失导入。

## 9. 本轮发现的新问题

### P0. 生产 / 预发布环境仍指向原模板 Apifox Mock API

位置：

- `frontend/.env.production`
- `frontend/.env.staging`

当前内容仍包含：

```env
VITE_BASE_URL = https://apifoxmock.com/m1/2930465-2145633-default/api/v1
```

影响：

1. `npm run build` 默认会读取生产环境配置，构建产物将请求原模板 Mock 地址；
2. 这会导致登录、获取当前用户等接口不再访问本项目后端；
3. 这属于模板 Mock 配置残留，不符合“不得保留模板 Mock 数据作为真实业务数据”的要求；
4. `.env.production` 还保留 `/v3-admin-vite/` public path 示例，容易造成部署路径错误。

修复建议：

1. 将 `.env.production`、`.env.staging` 的 `VITE_BASE_URL` 改为本项目后端地址占位或相对路径，例如：

```env
VITE_BASE_URL = http://127.0.0.1:8000
```

或：

```env
VITE_BASE_URL = /api
```

但若使用 `/api`，必须确认前端接口路径不会变成 `/api/api/auth/login`。

2. 将 `VITE_PUBLIC_PATH` 改为 `/` 或本项目部署路径，不要保留 `/v3-admin-vite/`；
3. 在 `frontend/README.md` / handoff 中说明生产环境变量需要按部署环境替换；
4. 不要再保留 Apifox Mock 作为默认业务接口地址。

## 10. 是否允许进入 Stage-14

**不允许。**

Stage-13 Fix 已解决模板底座和开源合规主问题，但仍需先清理生产 / 预发布 Mock API 配置。修复后可再次复审；通过后再发布 Stage-14。

## 11. 必须修复的问题

1. 清理 `frontend/.env.production` 中的 Apifox Mock API 地址；
2. 清理 `frontend/.env.staging` 中的 Apifox Mock API 地址；
3. 清理或替换 `/v3-admin-vite/` 这类原模板部署路径；
4. 确保所有环境的 `VITE_BASE_URL` 都指向本项目后端或明确的安全占位；
5. 更新 handoff 说明本次修复内容；
6. 不要发布 Stage-14，直到本问题复审通过。
