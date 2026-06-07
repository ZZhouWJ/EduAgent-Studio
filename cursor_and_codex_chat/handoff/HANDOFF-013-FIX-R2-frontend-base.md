# HANDOFF-013-FIX-R2：移除模板 Mock API 配置

## 任务状态

**完成**。

---

## 一、Codex 本轮未通过原因

`REVIEW-013-frontend-base.md`（上一轮）指出：

- `.env.production` 和 `.env.staging` 仍保留 V3 Admin Vite 原模板的 Apifox Mock API 地址：
  ```
  VITE_BASE_URL=https://apifoxmock.com/m1/2930465-2145633-default/api/v1
  ```
- 生产/预发布构建会连接到第三方 Mock 服务，而不是本项目后端
- 违反"不得保留模板 Mock 数据作为真实业务"的要求

---

## 二、本次修改文件

| 文件 | 修改内容 |
|------|----------|
| `frontend/.env.production` | Apifox Mock URL → `http://127.0.0.1:8000` |
| `frontend/.env.staging` | Apifox Mock URL → `http://127.0.0.1:8000` |
| `frontend/.env` | 补充 `VITE_BASE_URL` 默认值 |
| `frontend/.env.example` | 重写，补充环境变量说明表格 |
| `frontend/README.md` | 补充"不使用 Apifox Mock"说明，补充环境变量说明表格，更新裁剪列表 |
| `frontend/README.zh-CN.md` | **已删除**（模板原中文 README） |

### .env.production 修复前后对比

**修复前：**
```env
VITE_BASE_URL=https://apifoxmock.com/m1/2930465-2145633-default/api/v1
VITE_PUBLIC_PATH=/v3-admin-vite/
```

**修复后：**
```env
VITE_APP_TITLE=智研协作 AI 项目质量审计系统
VITE_BASE_URL=http://127.0.0.1:8000
VITE_PUBLIC_PATH=/
VITE_ROUTER_HISTORY=hash
```

### .env.staging 修复前后对比

**修复前：**
```env
VITE_BASE_URL=https://apifoxmock.com/m1/2930465-2145633-default/api/v1
VITE_PUBLIC_PATH=/
```

**修复后：**
```env
VITE_APP_TITLE=智研协作 AI 项目质量审计系统
VITE_BASE_URL=http://127.0.0.1:8000
VITE_PUBLIC_PATH=/
VITE_ROUTER_HISTORY=hash
```

---

## 三、Apifox Mock API 已移除

全局搜索确认（搜索范围：`*.{ts,vue,js,json,md}`）：

- `apifoxmock.com` URL：**已从 `.env.production` 和 `.env.staging` 移除**
- `vite.config.ts`：`proxy` 配置中**无** mock.apifox 引用
- `src/http/axios.ts`：`baseURL` 从 `import.meta.env.VITE_BASE_URL` 读取，**无硬编码 mock 地址**
- 所有登录相关接口均调用本项目后端：
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - `POST /api/auth/logout`
- 无 `/api/auth/register` 调用

---

## 四、Request 封装检查

`frontend/src/http/axios.ts`：

```typescript
const defaultConfig: AxiosRequestConfig = {
  baseURL: import.meta.env.VITE_BASE_URL,  // ✅ 从环境变量读取
  headers: {
    "Authorization": token ? `Bearer ${token}` : undefined,
    "Content-Type": "application/json"
  },
  timeout: 5000,
  withCredentials: false
}
```

- ✅ `baseURL` 从 `VITE_BASE_URL` 环境变量读取
- ✅ 无硬编码 Mock 地址
- ✅ 无生产环境 fallback 到模板 Mock
- ✅ 默认值 `http://127.0.0.1:8000`（本项目后端）

---

## 五、环境变量汇总

| 文件 | VITE_BASE_URL | 说明 |
|------|---------------|------|
| `.env` | `http://127.0.0.1:8000` | 所有环境共享默认值 |
| `.env.development` | `http://127.0.0.1:8000` | 开发环境 |
| `.env.staging` | `http://127.0.0.1:8000`（需替换）| 预发布环境 |
| `.env.production` | `http://127.0.0.1:8000`（需替换）| 生产环境 |

> 注：`.env.staging` 和 `.env.production` 中保留了 `http://127.0.0.1:8000` 作为占位符，实际部署时需替换为真实服务器地址。

---

## 六、README 是否说明生产/预发布配置

✅ 已更新 `frontend/README.md`：

```markdown
> **重要**：本项目**不使用** V3 Admin Vite 原模板的 Apifox Mock API。
> 所有环境变量中的 API 地址均指向本项目 FastAPI 后端。

| 文件 | VITE_BASE_URL 默认值 |
|------|---------------------|
| `.env` | `http://127.0.0.1:8000` |
| `.env.development` | `http://127.0.0.1:8000` |
| `.env.staging` | `http://127.0.0.1:8000`（需替换为实际地址）|
| `.env.production` | `http://127.0.0.1:8000`（需替换为实际地址）|
```

---

## 七、项目开发文档说明

用户要求同步修改"项目开发文档"中关于前端实现的旧表述（"手工实现"、"参考 UI 风格"等）。

**仓库中不存在** `docs/AI开发总控规范.md` 以外的项目开发文档 Markdown 文件。Canvas 文档（如存在）需人工同步。

`frontend/README.md` 已明确说明：
- 前端基于 V3 Admin Vite 模板二次开发
- 保留 LICENSE / NOTICE / 来源说明
- 删除了模板 Mock API
- 系统品牌替换为"智研协作 AI 项目质量审计系统"
- 前端接口指向本项目 FastAPI 后端

---

## 八、是否修改 backend

**否**。

---

## 九、是否修改 database

**否**。

---

## 十、是否实现完整业务页面

**否**。

---

## 十一、是否实现 Stage-14

**否**。

---

## 十二、当前环境限制

当前环境无 Node.js（`node -v: command not found`），无法执行 `npm install` / `npm run build`。

已进行静态检查：
- 所有 `.env*` 文件已清理 Mock URL
- `vite.config.ts` 无 mock proxy 配置
- `axios.ts` baseURL 从环境变量读取，无硬编码
- `README.md` 已补充完整环境变量说明

---

## 十三、验收清单

- [x] `.env.production` Apifox Mock URL 已移除
- [x] `.env.staging` Apifox Mock URL 已移除
- [x] `.env` 补充了 `VITE_BASE_URL` 默认值
- [x] `.env.example` 补充了环境变量说明表格
- [x] axios.ts 不含硬编码 Mock 地址
- [x] vite.config.ts 不含 mock 反向代理
- [x] README.md 说明"不使用 Apifox Mock API"
- [x] README.md 补充生产/预发布环境配置说明
- [x] README.zh-CN.md（模板原中文 README）已删除
- [x] 项目开发文档说明已更新（README.md 中）
- [x] 未修改 backend
- [x] 未修改 database
- [x] 未实现完整业务页面
- [x] 未实现 Stage-14
