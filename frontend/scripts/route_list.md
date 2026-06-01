# 前端路由清单

> 本文档整理智研协作 AI 项目质量审计系统前端所有已实现路由，标注对应页面文件和主要对接后端接口。
> 基于 `frontend/src/router/index.ts` 和 `frontend/src/router/guard.ts` 生成。
> 最后更新时间：2026-06-01

---

## 路由总览

| # | 路由 | 页面 | 组件文件 | 说明 | 对接后端接口 |
|---|------|------|----------|------|-------------|
| 1 | `/login` | 登录页 | `pages/login/index.vue` | 用户登录，对接认证接口 | `POST /api/auth/login`<br>`GET /api/auth/me`<br>`POST /api/auth/logout` |
| 2 | `/dashboard` | 首页 | `pages/dashboard/index.vue` | 统计概览、流程卡片 | `GET /api/statistics/overview` |
| 3 | `/projects` | 项目空间列表 | `pages/projects/index.vue` | 项目列表、创建项目弹窗 | `GET /api/projects`<br>`POST /api/projects`<br>`DELETE /api/projects/{id}` |
| 4 | `/projects/:projectId` | 项目详情 | `pages/projects/ProjectDetail.vue` | 成员列表、任务列表、成果列表 | `GET /api/projects/{id}`<br>`GET /api/projects/{id}/members`<br>`GET /api/projects/{id}/tasks` |
| 5 | `/tasks` | 任务列表入口 | `pages/tasks/index.vue` | 全局任务列表入口，引导至项目空间查看详情 | 从项目详情进入；任务详情：`GET /api/tasks/{id}` |
| 6 | `/tasks/:taskId` | 任务详情 | `pages/tasks/TaskDetail.vue` | 分支、版本、AI生成面板、编辑、批注 | `GET /api/tasks/{id}`<br>`GET /api/tasks/{id}/branches`<br>`GET /api/tasks/{id}/outputs`<br>`POST /api/tasks/{id}/generate`<br>`GET /api/outputs/{id}/comments` |
| 7 | `/reviews` | 审核中心列表 | `pages/reviews/index.vue` | 待审核列表、审核统计 | `GET /api/reviews/pending` |
| 8 | `/reviews/:requestId` | 审核详情 | `pages/reviews/ReviewDetail.vue` | 输出内容查看、评分弹窗、提交审核 | `GET /api/reviews/{id}`<br>`POST /api/reviews/{id}/complete`<br>`GET /api/issue-tags` |
| 9 | `/artifacts` | 成果库列表 | `pages/artifacts/ArtifactList.vue` | 所有已采用成果列表（按项目查询） | `GET /api/projects/{project_id}/artifacts` |
| 10 | `/artifacts/:adoptedId` | 成果详情 | `pages/artifacts/ArtifactDetail.vue` | 成果完整内容展示 | `GET /api/artifacts/{adopted_id}` |
| 11 | `/statistics` | 统计看板 | `pages/statistics/StatisticsDashboard.vue` | 多维度统计图表 | `GET /api/statistics/overview`<br>`GET /api/statistics/projects`<br>`GET /api/statistics/model-calls`<br>`GET /api/statistics/costs`<br>`GET /api/statistics/reviews`<br>`GET /api/statistics/member-contributions`<br>`GET /api/statistics/recent-activities` |
| 12 | `/models` | 模型管理 | `pages/models/index.vue` | 供应商、模型、API配置管理 | `GET /api/model-providers`<br>`GET /api/ai-models`<br>`GET /api/api-configs` |
| 13 | `/404` | 404 错误页 | `pages/error/404.vue` | 路由未匹配 | — |
| 14 | `/403` | 403 错误页 | `pages/error/403.vue` | 无权限访问 | — |

---

## 路由守卫说明

| 路由 | 守卫规则 |
|------|---------|
| `/login` | 未登录用户允许访问；已登录用户访问自动跳转首页 |
| `/dashboard` | 需要登录，无权限则跳转 `/403` |
| `/projects` | 需要登录 |
| `/projects/:projectId` | 需要登录（详细权限由后端接口控制）|
| `/tasks` | 需要登录 |
| `/tasks/:taskId` | 需要登录（详细权限由后端接口控制）|
| `/reviews` | 需要登录 |
| `/reviews/:requestId` | 需要登录（详细权限由后端接口控制）|
| `/artifacts` | 需要登录 |
| `/artifacts/:adoptedId` | 需要登录（详细权限由后端接口控制）|
| `/statistics` | 需要登录 |
| `/models` | 需要登录 |
| `/403`、`/404` | 无限制 |

> **注**：当前前端所有登录用户均可访问全部页面，路由级权限由后端接口控制（部分接口返回 403）。

---

## 路由嵌套关系

```
/ (Layouts)
├── /dashboard                    → Dashboard
├── /projects                    → Projects (列表)
├── /projects/:projectId         → ProjectDetail
├── /tasks                       → Tasks (列表)
├── /tasks/:taskId               → TaskDetail
├── /reviews                     → Reviews (列表)
├── /reviews/:requestId          → ReviewDetail
├── /artifacts                   → Artifacts (列表)
├── /artifacts/:adoptedId        → ArtifactDetail
├── /statistics                  → StatisticsDashboard
├── /models                      → Models
├── /login                       → Login
├── /403                         → 403
└── /404                         → 404
```

---

## 截图建议

| 页面 | 建议截图点 |
|------|-----------|
| `/login` | 登录表单、登录成功跳转 |
| `/dashboard` | 流程卡片、统计数据卡片 |
| `/projects` | 项目列表、创建项目弹窗 |
| `/projects/:projectId` | 成员列表、任务列表、Tab 切换 |
| `/tasks` | 任务列表、筛选条件 |
| `/tasks/:taskId` | 分支列表、版本时间线、AI 生成面板 |
| `/reviews` | 待审核列表、审核状态统计 |
| `/reviews/:requestId` | 输出内容、评分弹窗 |
| `/artifacts` | 成果列表、筛选 |
| `/artifacts/:adoptedId` | 成果详情、版本信息 |
| `/statistics` | 多个统计图表（概览、调用量、成本、审核质量）|
| `/models` | 模型列表、供应商列表 |
