# 前端路由清单

> 本文档记录 AI-Collab-Audit-System 前端所有已实现页面路由。
> 基于 `frontend/src/router/index.ts` 生成。

---

## 路由总览（共 18 个页面）

| # | 路由 | 页面文件 | 说明 | 主要接口 | 截图建议 |
|---|------|----------|------|----------|---------|
| 1 | `/login` | `pages/login/index.vue` | 登录页，支持跳转注册 | `POST /api/auth/login` | 登录页截图 |
| 2 | `/register` | `pages/register/index.vue` | 注册页，默认分配 student_member 角色 | `POST /api/auth/register` | 注册页截图 |
| 3 | `/dashboard` | `pages/dashboard/index.vue` | 首页仪表盘 | 无数据接口（占位） | 首页截图 |
| 4 | `/projects` | `pages/projects/index.vue` | 项目列表（搜索/状态筛选） | `GET/POST /api/projects` | 项目列表截图 |
| 5 | `/projects/:projectId` | `pages/projects/ProjectDetail.vue` | 项目详情，7 Tab | 详见下方 | 项目详情各 Tab 截图 |
| 6 | `/tasks` | `pages/tasks/index.vue` | 全局任务列表 | `GET /api/projects/:id/tasks` | 任务列表截图 |
| 7 | `/tasks/:taskId` | `pages/tasks/TaskDetail.vue` | 任务详情（分支/版本/AI生成/批注） | 详见下方 | 任务详情各功能截图 |
| 8 | `/generate` | `pages/generate/index.vue` | AI 生成入口 | `POST /api/tasks/:id/generate` | AI 生成截图 |
| 9 | `/prompts` | `pages/prompts/index.vue` | 提示词模板管理 | `GET /api/prompt-templates` | 模板列表截图 |
| 10 | `/reviews` | `pages/reviews/index.vue` | 审核中心，三 Tab | `GET /api/reviews/pending` | 审核中心截图 |
| 11 | `/artifacts` | `pages/artifacts/index.vue` | 成果库（筛选/导出） | `GET /api/projects/:id/artifacts` | 成果库截图 |
| 12 | `/invocations` | `pages/invocations/index.vue` | 调用审计 | `GET /api/invocations` | 调用日志截图 |
| 13 | `/costs` | `pages/costs/index.vue` | 成本统计 | `GET /api/statistics/costs` | 成本统计截图 |
| 14 | `/statistics` | `pages/statistics/index.vue` | 统计看板 | 7 个统计接口 | 统计看板截图 |
| 15 | `/models` | `pages/models/index.vue` | 模型管理 | `GET /api/ai-models` | 模型管理截图 |
| 16 | `/users` | `pages/users/index.vue` | 用户管理 | `GET /api/users` | 用户管理截图 |
| 17 | `/logs/operation` | `pages/logs/operation.vue` | 操作日志 | `GET /api/logs/operation` | 操作日志截图 |
| 18 | `/logs/login` | `pages/logs/login.vue` | 登录日志 | `GET /api/logs/login` | 登录日志截图 |
| 19 | `/profile` | `pages/profile/index.vue` | 个人中心 | `PUT /api/auth/me/password` | 个人中心截图 |

---

## 路由文件对应关系

```
frontend/src/router/index.ts
  ├── /login              → pages/login/index.vue
  ├── /register           → pages/register/index.vue
  ├── /dashboard          → pages/dashboard/index.vue
  ├── /projects           → pages/projects/index.vue
  ├── /projects/:projectId → pages/projects/ProjectDetail.vue
  ├── /tasks             → pages/tasks/index.vue
  ├── /tasks/:taskId     → pages/tasks/TaskDetail.vue
  ├── /generate           → pages/generate/index.vue
  ├── /prompts            → pages/prompts/index.vue
  ├── /reviews            → pages/reviews/index.vue
  ├── /artifacts          → pages/artifacts/index.vue
  ├── /invocations        → pages/invocations/index.vue
  ├── /costs             → pages/costs/index.vue
  ├── /statistics         → pages/statistics/index.vue
  ├── /models            → pages/models/index.vue
  ├── /users             → pages/users/index.vue
  ├── /logs/operation    → pages/logs/operation.vue
  ├── /logs/login         → pages/logs/login.vue
  └── /profile           → pages/profile/index.vue
```

---

## 各路由详细说明

### 1. 登录 `/login`

**页面文件**: `pages/login/index.vue`

**功能**: 用户登录系统，支持跳转注册页。

**主要接口**:
- `POST /api/auth/login` — 登录认证
- `GET /api/auth/me` — 获取当前用户信息

**截图建议**: 登录页整体截图、登录成功跳转截图

---

### 2. 注册 `/register`

**页面文件**: `pages/register/index.vue`

**功能**: 用户注册，bcrypt 哈希存储密码，默认分配 student_member 角色。

**主要接口**:
- `POST /api/auth/register` — 用户注册

**截图建议**: 注册页截图

---

### 3. 首页 `/dashboard`

**页面文件**: `pages/dashboard/index.vue`

**功能**: 首页仪表盘，展示系统概览和模块入口。

---

### 4. 项目列表 `/projects`

**页面文件**: `pages/projects/index.vue`

**功能**: 项目列表（搜索/状态筛选）、创建项目。

**主要接口**:
- `GET /api/projects` — 获取项目列表（分页）
- `POST /api/projects` — 创建新项目

---

### 5. 项目详情 `/projects/:projectId`

**页面文件**: `pages/projects/ProjectDetail.vue`

**功能**: 7 Tab 专业分栏：概览/成员/任务/成果/调用/日志/统计

**主要接口**:
- `GET /api/projects/:projectId` — 项目详情
- `GET /api/projects/:projectId/members` — 成员列表
- `POST /api/projects/:projectId/members` — 添加成员
- `PUT /api/projects/:projectId/members/:memberId` — 更新成员角色
- `DELETE /api/projects/:projectId/members/:memberId` — 移除成员
- `GET /api/projects/:projectId/tasks` — 任务列表
- `POST /api/projects/:projectId/tasks` — 创建任务
- `PUT /api/projects/:projectId` — 更新项目
- `POST /api/projects/:projectId/archive` — 归档项目
- `GET /api/statistics/projects?project_id=X` — 项目统计

**截图建议**: 概览 Tab、成员 Tab、任务 Tab 各一张

---

### 6. 任务列表 `/tasks`

**页面文件**: `pages/tasks/index.vue`

**功能**: 全局任务列表，支持搜索和状态筛选。

**主要接口**:
- `GET /api/projects/:id/tasks` — 获取任务列表

---

### 7. 任务详情 `/tasks/:taskId`

**页面文件**: `pages/tasks/TaskDetail.vue`

**功能**: 任务详情 + 分支管理 + AI 生成 + 输出版本 + 批注协作 + 提交审核 + 成果采用。

**主要接口**:
- `GET /api/tasks/:taskId` — 任务详情
- `GET /api/tasks/:taskId/branches` — 分支列表
- `POST /api/tasks/:taskId/branches` — 创建分支
- `POST /api/tasks/:taskId/branches/merge` — 分支合并
- `GET /api/tasks/:taskId/outputs` — 输出列表
- `POST /api/tasks/:taskId/generate` — AI 生成
- `GET /api/outputs/:outputId` — 输出详情
- `PUT /api/outputs/:outputId` — 更新输出（乐观锁）
- `POST /api/outputs/:outputId/save-as-new-version` — 另存新版本
- `POST /api/outputs/:outputId/submit-review` — 提交审核
- `POST /api/outputs/:outputId/adopt` — 成果采用
- `GET /api/outputs/:outputId/comments` — 批注列表
- `POST /api/outputs/:outputId/comments` — 添加批注
- `PUT /api/comments/:commentId/status` — 更新批注状态
- `GET /api/ai-models` — 模型列表
- `GET /api/prompt-templates` — 提示词模板

**截图建议**: 任务信息、分支列表、输出版本、AI 生成弹窗、输出详情抽屉、批注列表、完成审核弹窗各一张

---

### 8. AI 生成 `/generate`

**页面文件**: `pages/generate/index.vue`

**功能**: 全局 AI 生成入口，支持选择模型和分支。

**主要接口**:
- `POST /api/tasks/:taskId/generate` — AI 生成
- `GET /api/ai-models` — 模型列表
- `GET /api/prompt-templates` — 模板列表

---

### 9. 提示词管理 `/prompts`

**页面文件**: `pages/prompts/index.vue`

**功能**: 提示词模板管理（模板列表 + 版本管理）。

**主要接口**:
- `GET /api/prompt-templates` — 模板列表
- `POST /api/prompt-templates` — 创建模板
- `PUT /api/prompt-templates/:id` — 更新模板
- `DELETE /api/prompt-templates/:id` — 删除模板
- `GET /api/prompt-templates/:id/versions` — 版本列表
- `POST /api/prompt-templates/:id/versions` — 新增版本
- `POST /api/prompt-templates/:id/versions/:vid/activate` — 激活版本
- `GET /api/task-types` — 任务类型

---

### 10. 审核中心 `/reviews`

**页面文件**: `pages/reviews/index.vue`

**功能**: 三 Tab（待审核/我提交的/审核历史）+ 评分仪表盘 + 问题标签。

**主要接口**:
- `GET /api/reviews/pending` — 待审核列表
- `GET /api/reviews/:requestId` — 审核详情
- `POST /api/reviews/:requestId/complete` — 完成审核
- `GET /api/issue-tags` — 问题标签列表
- `GET /api/statistics/reviews` — 审核统计

**截图建议**: 审核列表、审核详情抽屉、评分弹窗各一张

---

### 11. 成果库 `/artifacts`

**页面文件**: `pages/artifacts/index.vue`

**功能**: 成果列表（按项目/类型筛选）+ Markdown 导出 + 详情抽屉。

**主要接口**:
- `GET /api/projects/:id/artifacts` — 项目成果列表
- `GET /api/artifacts/:adoptedId` — 成果详情

---

### 12. 调用审计 `/invocations`

**页面文件**: `pages/invocations/index.vue`

**功能**: 调用日志（项目/模型/状态/日期筛选）+ 详情对话框（输入/输出预览）。

**主要接口**:
- `GET /api/invocations` — 调用日志列表
- `GET /api/invocations/:id` — 调用详情

---

### 13. 成本统计 `/costs`

**页面文件**: `pages/costs/index.vue`

**功能**: 四摘要卡片 + 筛选栏 + 按模型/按项目两 Tab + 可排序列。

**主要接口**:
- `GET /api/statistics/costs` — 成本统计

---

### 14. 统计看板 `/statistics`

**页面文件**: `pages/statistics/index.vue`

**功能**: 概览卡片 + AI 调用 + 成本 + 项目 + 审核质量 + 成员贡献 + 最近动态。

**主要接口**:
- `GET /api/statistics/overview` — 统计概览
- `GET /api/statistics/projects` — 项目统计
- `GET /api/statistics/model-calls` — 模型调用
- `GET /api/statistics/costs` — 成本统计
- `GET /api/statistics/reviews` — 审核质量
- `GET /api/statistics/member-contributions` — 成员贡献
- `GET /api/statistics/recent-activities` — 最近动态

---

### 15. 模型管理 `/models`

**页面文件**: `pages/models/index.vue`

**功能**: 供应商列表 + 模型列表（启用禁用）+ API Key 脱敏展示。

**主要接口**:
- `GET /api/model-providers` — 供应商列表
- `POST /api/model-providers` — 创建供应商
- `GET /api/ai-models` — 模型列表
- `POST /api/ai-models` — 创建模型
- `GET /api/api-configs` — API 配置列表
- `POST /api/api-configs` — 创建 API 配置

---

### 16. 用户管理 `/users`

**页面文件**: `pages/users/index.vue`

**功能**: 用户列表（搜索/状态筛选）+ 启用禁用 + 角色分配。

**主要接口**:
- `GET /api/users` — 用户列表
- `PUT /api/users/:id/status` — 启用/禁用用户
- `PUT /api/users/:id/roles` — 分配角色
- `GET /api/roles` — 角色列表

---

### 17. 操作日志 `/logs/operation`

**页面文件**: `pages/logs/operation.vue`

**功能**: 操作日志（操作人/对象类型/操作类型/日期筛选）+ 变更详情（old→new）。

**主要接口**:
- `GET /api/logs/operation` — 操作日志列表

---

### 18. 登录日志 `/logs/login`

**页面文件**: `pages/logs/login.vue`

**功能**: 登录日志（用户名/状态/日期筛选）+ IP/UA/失败原因。

**主要接口**:
- `GET /api/logs/login` — 登录日志列表

---

### 19. 个人中心 `/profile`

**页面文件**: `pages/profile/index.vue`

**功能**: 用户信息展示 + 修改密码。

**主要接口**:
- `GET /api/auth/me` — 获取当前用户
- `PUT /api/auth/me/password` — 修改密码

---

*本文件最后更新：2026-06-02*
