# REVIEW-013-FIX-R2: Stage-13 Fix R2 前端基础框架复审报告

## 1. 审查结论

**通过**

本轮只复审上一轮唯一阻塞点：`frontend/.env.production` 和 `frontend/.env.staging` 是否仍保留 V3 Admin Vite 原模板 Apifox Mock API 地址。

复审结果：阻塞点已修复，允许进入 Stage-14。

## 2. Apifox Mock API 是否已从 production / staging 移除

**已移除。**

已检查：

- `frontend/.env.production`
- `frontend/.env.staging`
- `frontend/.env.example`
- `frontend/README.md`
- `frontend/src`
- `frontend/vite.config.ts`

当前配置：

```env
VITE_BASE_URL = http://127.0.0.1:8000
```

结论：

1. `frontend/.env.production` 不再包含 Apifox Mock 地址；
2. `frontend/.env.staging` 不再包含 Apifox Mock 地址；
3. 未发现 `mock.apifox.com`；
4. 未发现 `apifoxmock.com`；
5. 未发现其他第三方模板 Mock API 地址；
6. 生产 / 预发布 API 地址已改为本项目 FastAPI 后端本地地址占位；
7. API 环境变量名为 `VITE_BASE_URL`，与 request 封装实际读取一致。

## 3. request 封装是否仍存在模板 Mock 地址

**不存在。**

`frontend/src/http/axios.ts` 使用：

```ts
baseURL: import.meta.env.VITE_BASE_URL
```

已确认：

1. 未硬编码 Apifox Mock baseURL；
2. 未发现模板 Mock 登录接口；
3. 未发现模板 Mock 用户信息接口；
4. API baseURL 通过环境变量读取；
5. fallback / 默认环境地址为本项目本地后端 `http://127.0.0.1:8000`；
6. 登录接口仍为 `POST /api/auth/login`；
7. 当前用户接口仍为 `GET /api/auth/me`；
8. 登出接口仍为 `POST /api/auth/logout`；
9. 未发现 `/api/auth/register` 调用。

## 4. .env.example 和 README 是否同步

**已同步。**

`frontend/.env.example` 明确说明：

- `axios.ts` 读取 `import.meta.env.VITE_BASE_URL`；
- 默认后端地址为 `http://127.0.0.1:8000`；
- 生产 / 预发布环境需要替换为实际后端地址。

`frontend/README.md` 已说明：

- 本项目不使用 V3 Admin Vite 原模板的 Apifox Mock API；
- 所有环境变量中的 API 地址均指向本项目 FastAPI 后端；
- `.env.production` / `.env.staging` 的地址部署时需要替换。

未发现将模板 Mock 数据声明为真实业务数据的问题。

## 5. 是否仍符合 V3 Admin Vite 模板二次开发要求

**仍符合。**

已确认：

1. 前端仍基于 V3 Admin Vite 模板二次开发；
2. `frontend/LICENSE` 保留；
3. `frontend/NOTICE.md` 保留；
4. `frontend/README.md` 保留模板来源、GitHub 链接和 MIT 许可证说明；
5. 系统品牌仍为“智研协作 AI 项目质量审计系统”；
6. 未发现回退为完全手写普通模板；
7. 未发现复制 LobeChat / Open WebUI 的 React / Svelte 源码。

## 6. 是否发现越界修改

**未发现本轮阻塞点相关越界实现。**

已确认：

1. 未发现修改 `database/` 的必要证据；
2. 未发现修改后端 service / repository；
3. 未发现完整项目管理页面；
4. 未发现完整任务管理页面；
5. 未发现完整审核中心页面；
6. 未发现完整成果库页面；
7. 未发现完整统计看板页面；
8. 未发现进入 Stage-14 的业务实现；
9. 复审前 `TASK-014-frontend-project-task-pages.md` 尚未存在。

说明：工作区仍有大量历史阶段文件处于 modified / untracked 状态，这是此前多阶段协作遗留状态。本轮按用户要求只复审 Stage-13 Fix R2 的唯一阻塞点，未将历史脏工作区作为阻塞项。

## 7. 启动或静态检查

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

已进行静态检查：

- `frontend/package.json` 存在；
- `dev` / `build` 脚本存在；
- `frontend/vite.config.ts` 存在；
- `VITE_BASE_URL` 变量名与 request 封装一致；
- 未发现明显路径错误；
- 未发现 Apifox Mock 残留。

## 8. 是否允许进入 Stage-14

**允许。**

Stage-13 Fix R2 通过，发布 Stage-14 任务：

- `cursor_and_codex_chat/tasks/todo/TASK-014-frontend-project-task-pages.md`
