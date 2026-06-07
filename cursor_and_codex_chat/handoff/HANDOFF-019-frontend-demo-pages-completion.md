# HANDOFF-019-frontend-demo-pages-completion

## 任务概述

本次任务（TASK-019）补齐了 AI-Collab-Audit-System 的轻量 Vue3 前端，从已有骨架扩展为可完整演示课程流程的演示系统。

**不涉及重写后端、新增数据库结构、注册功能、复杂权限或真实大模型调用。**

---

## 一、补齐的页面清单

| 序号 | 页面 | 路由 | 状态 |
|---|---|---|---|
| 1 | 首页（Dashboard） | `/dashboard` | 完成 |
| 2 | 登录页 | `/login` | 完成（修正测试密码） |
| 3 | 项目空间（列表） | `/projects` | 完成（大幅增强） |
| 4 | 项目详情 | `/projects/:projectId` | 完成（大幅增强） |
| 5 | 任务与版本（入口） | `/tasks` | 完成（新增） |
| 6 | 任务详情 | `/tasks/:taskId` | 完成（大幅增强） |
| 7 | AI 生成（入口） | `/generate` | 完成（新增） |
| 8 | 审核中心 | `/reviews` | 完成（大幅增强） |
| 9 | 成果库 | `/artifacts` | 完成（完善） |
| 10 | 统计看板 | `/statistics` | 完成（大幅增强） |
| 11 | 模型管理 | `/models` | 完成（新增） |

---

## 二、新增或修改的文件

### 新增文件

| 文件路径 | 说明 |
|---|---|
| `frontend/src/api/auth.ts` | 认证 API 封装 |
| `frontend/src/api/projects.ts` | 项目 API 封装 |
| `frontend/src/api/tasks.ts` | 任务/输出/批注 API 封装 |
| `frontend/src/api/reviews.ts` | 审核 API 封装 |
| `frontend/src/api/artifacts.ts` | 成果库 API 封装 |
| `frontend/src/api/statistics.ts` | 统计 API 封装 |
| `frontend/src/api/models.ts` | 模型 API 封装 |
| `frontend/src/pages/tasks/index.vue` | 任务入口页 |
| `frontend/src/pages/generate/index.vue` | AI 生成入口页 |
| `frontend/src/pages/models/index.vue` | 模型管理页 |
| `cursor_and_codex_chat/handoff/HANDOFF-019-frontend-demo-pages-completion.md` | 本文档 |

### 修改文件

| 文件路径 | 说明 |
|---|---|
| `frontend/src/layouts/BackendLayout.vue` | 左侧菜单扩充至 8 项；顶部显示角色中文名；Logo 改为系统全称 |
| `frontend/src/router/index.ts` | 新增 `/tasks`、`/generate`、`/models` 路由；`/tasks/:taskId` 和 `/projects/:projectId` 移除 `hidden` 使面包屑可见 |
| `frontend/src/pages/login/index.vue` | 测试账号信息修正（admin/Admin@123456 + student1/test123） |
| `frontend/src/pages/dashboard/index.vue` | 统计卡片（6 项）、成本行、模块网格扩展至 6 个 |
| `frontend/src/pages/projects/index.vue` | 新增搜索栏、状态筛选、分页器、新建项目弹窗 |
| `frontend/src/pages/projects/ProjectDetail.vue` | 成员列表展示、新建任务弹窗（含优先级/截止日期） |
| `frontend/src/pages/tasks/TaskDetail.vue` | 完全重写：模型选择、输出详情抽屉、内容编辑、批注增删改、提交审核、采用成果 |
| `frontend/src/pages/reviews/index.vue` | 审核详情抽屉、完成审核弹窗（6 项评分、问题标签多选） |
| `frontend/src/pages/artifacts/index.vue` | 成果详情抽屉、内容展示 |
| `frontend/src/pages/statistics/index.vue` | 7 个统计维度（overview + 6 个专项）、最近操作动态流 |

---

## 三、各页面调用的接口

### Dashboard
- `GET /api/statistics/overview`

### 项目空间
- `GET /api/projects`（列表，支持 keyword、status、page、page_size）
- `POST /api/projects`（新建）

### 项目详情
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/members`（只读）
- `GET /api/projects/{project_id}/tasks`
- `POST /api/projects/{project_id}/tasks`

### 任务入口
- `GET /api/projects`（下拉选择）
- `GET /api/projects/{project_id}/tasks`

### 任务详情
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/outputs`
- `GET /api/outputs/{output_id}`（查看详情）
- `GET /api/outputs/{output_id}/comments`
- `POST /api/outputs/{output_id}/comments`
- `PUT /api/comments/{comment_id}/status`
- `POST /api/tasks/{task_id}/generate`
- `PUT /api/outputs/{output_id}`（编辑输出，含 lock_version 乐观锁）
- `POST /api/outputs/{output_id}/submit-review`
- `POST /api/outputs/{output_id}/adopt`
- `GET /api/ai-models`（模型选择下拉）

### AI 生成入口
- `GET /api/projects`（选择项目）
- `GET /api/projects/{project_id}/tasks`（选择任务）
- `GET /api/ai-models`（选择模型）
- `POST /api/tasks/{task_id}/generate`

### 审核中心
- `GET /api/reviews/pending`
- `GET /api/reviews/{request_id}`
- `POST /api/reviews/{request_id}/complete`
- `GET /api/issue-tags`

### 成果库
- `GET /api/projects`（项目选择）
- `GET /api/projects/{project_id}/artifacts`
- `GET /api/artifacts/{adopted_id}`

### 统计看板
- `GET /api/statistics/overview`
- `GET /api/statistics/projects`
- `GET /api/statistics/model-calls`
- `GET /api/statistics/costs`
- `GET /api/statistics/reviews`
- `GET /api/statistics/member-contributions`
- `GET /api/statistics/recent-activities`

### 模型管理
- `GET /api/model-providers`
- `GET /api/ai-models`

---

## 四、功能说明

### 完整交互功能（可实际操作）
- 登录/退出
- 项目搜索、筛选、分页、新建
- 项目详情查看成员列表
- 项目内创建任务（含任务类型、优先级、截止日期）
- 任务列表查看和跳转
- 任务详情查看基本信息、输出版本、分支
- AI 生成（选择模型、输入提示词、查看生成结果）
- 输出内容查看（抽屉展示）
- 输出内容编辑（乐观锁 lock_version）
- 批注新增（comment_type 仅允许 comment/suggestion/approval）
- 批注状态更新（open/resolved/closed）
- 提交审核（带审核说明）
- 完成审核（审核结果 + 6 项评分 0-10 + 问题标签多选）
- 采用成果（artifact_title + artifact_type + release_version）
- 成果详情查看
- 统计看板（概览 + 项目 + AI 调用 + 成本 + 审核质量 + 成员贡献 + 操作动态）

### 只读展示功能
- 成员列表（不提供增删改）
- 模型供应商列表
- AI 模型列表

### 课程演示简化
- AI 生成调用后端 `/api/tasks/{task_id}/generate`，由后端服务层判断是否为 Mock 模式；不实现真实外部大模型调用
- 审核评分 6 项均为可选（0-10），不强制
- 所有接口依赖后端数据库已有数据，首次使用数据为空属正常现象

---

## 五、安全说明

本次修改未引入：
- 真实数据库密码
- 真实 API Key
- 真实 JWT Secret
- 完整 sk- 开头密钥
- 硬编码 token
- `password_hash` 字段
- `/api/auth/register` 调用
- 自动登录 Admin@123456

测试账号仅作为页面提示出现，不自动填充、不自动登录。

---

## 六、登录是否仍可用

是。`/api/auth/login` 和 `/api/auth/me` 接口完全未改动，登录功能保持原样。

测试账号：
- `admin` / `Admin@123456`（管理员，有所有权限）
- `student1` / `test123`（学生，student_member 角色）

---

## 七、Vite Proxy 当前配置

`frontend/vite.config.ts` 中已配置：
```ts
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8001',
    changeOrigin: true,
  }
}
```

- 前端 Vite 端口：`5173`
- 后端 FastAPI 端口：`8001`
- 所有前端请求统一走 `/api/...`，通过 proxy 转发至后端

---

## 八、npm run build 执行结果

```
✓ 1548 modules transformed.
✓ built in 4.68s
```

构建成功，无错误。dist 输出在 `frontend/dist/`。

---

## 九、是否修改 backend/database

否。本次修改严格限制在 `frontend/*` 范围内，未触碰：
- `backend/*`
- `database/*`
- `docs/01_数据库Schema冻结说明.md`

---

## 十、当前依赖的初始化数据

前端依赖后端已存在的种子数据：
- `admin` 用户（user_id=1，密码 Admin@123456，admin 角色）
- `student1` 用户（user_id=2，密码 test123，student_member 角色，role_id=1）
- 4 个系统角色（student_member, project_leader, teacher, admin）
- 44 个权限定义
- 9 个任务类型
- 10 个问题标签（issue_tags）
- 3 个模型供应商（Mock, OpenAI, DeepSeek）
- 8 个 AI 模型

如需完整演示流程，需先在数据库中创建项目、任务等数据。

---

## 十一、已知限制

1. **首次使用数据为空**：所有列表页首次访问时为空，需要通过创建项目、创建任务、调用 AI 生成等操作后数据才会出现
2. **AI 生成受 Mock 模式限制**：后端服务层判断是否真实调用，Mock 模式下返回预设结果，不消耗真实 API 配额
3. **成员管理**：项目详情页仅展示成员，不提供增删改成员入口
4. **路由**：使用 hash history，URL 中带有 `#` 前缀（如 `http://localhost:5173/#/projects`）
5. **分页字段名**：后端分页响应中，`total` 字段在部分接口中为数字，部分可能缺失，均已在页面中做兜底处理
6. **任务类型名称**：项目详情和任务入口页使用前端硬编码的任务类型映射，后端 `/api/task-types` 接口可覆盖但不强制依赖
7. **审核结果**：审核完成后 review 请求从 pending 列表消失，需重新刷新页面

---

## 十二、修改摘要对照

| 修改项 | 修改前 | 修改后 |
|---|---|---|
| 左侧菜单 | 5 项（首页/项目空间/审核中心/成果库/统计看板） | 8 项（新增：任务与版本、AI 生成、模型管理） |
| 顶部用户信息 | 仅显示用户名 | 显示用户名 + 角色中文名标签 |
| 登录测试账号 | `admin/admin123` | `admin/Admin@123456` + `student1/test123` |
| 项目列表 | 简单表格 | 搜索 + 筛选 + 分页 + 新建弹窗 |
| 项目详情 | 基本信息 + 任务表 | 新增成员列表 + 创建任务弹窗 |
| 任务详情 | 简单生成按钮 + 表格 | 完整 AI 生成 + 模型选择 + 输出详情抽屉 + 批注 + 编辑 + 提交审核 + 采用 |
| 审核中心 | 简单表格 | 详情抽屉 + 完成审核弹窗（评分 + 标签） |
| 成果库 | 简单列表 | 成果详情抽屉 + 内容展示 |
| 统计看板 | 4 个数字卡片 + 2 表 | 7 个维度全覆盖 + 操作动态流 |
| 模型管理 | 无此页面 | 供应商 + 模型列表，只读展示 |
| API 调用 | 页面内直接写 `request.get/post` | 统一封装到 `src/api/*.ts` |
