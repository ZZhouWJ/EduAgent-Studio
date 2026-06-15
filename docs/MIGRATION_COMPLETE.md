# EduAgent Studio — React 前端迁移完成总结

> 迁移时间：2026-06-14 → 2026-06-15
> 范围：frontend/ 从 Vue 3 + Element Plus 切到 React 18 + shadcn/ui
> 详情计划：[`2026-06-14-react-frontend-migration.md`](2026-06-14-react-frontend-migration.md)

## 背景

原 `frontend/` 是 Vue 3 + Vite + Element Plus + Pinia 实现，UI 风格偏传统后台，难以满足 A3 赛题演示对"AI 教育 SaaS 平台"质感的诉求。
本次迁移保留全部业务逻辑、API 契约、数据库 schema，只重做前端实现。

## 迁移产出

### 1. 新前端（React 18 + shadcn/ui）

- 框架：React 18 + Vite 6 + TypeScript 5
- UI 库：shadcn/ui（50+ Radix 组件）+ Tailwind v4 + lucide-react + sonner + recharts
- 状态：Zustand（auth + UI 状态）
- HTTP：axios（拦截器统一处理 `{code, message, data}` 响应格式）
- 路由：react-router 7（BrowserRouter，三角色分流）
- 27 个业务页面：4 个公共页（Login/404 等）+ 7 个 Student 页面 + 9 个 Teacher 页面 + 11 个 Admin 页面

### 2. 17 个 API 模块（`frontend/src/lib/api/`）

| 模块 | 后端路径前缀 | 方法数 |
|---|---|---|
| auth-api.ts | `/api/auth` | 8 |
| users.ts | `/api/users` | 3 |
| profiles.ts | `/api/profiles` | 4 |
| learning.ts | `/api/learning` | 5 |
| resources.ts | `/api/learning/resources` | 2 |
| feedbacks.ts | `/api/learning/feedbacks` | 3 |
| agents.ts | `/api/agents` | 4 |
| tasks.ts | `/api/tasks`, `/api/outputs`, `/api/comments` | 11 |
| projects.ts | `/api/projects` | 9 |
| artifacts.ts | `/api/projects/:id/artifacts`, `/api/artifacts` | 2 |
| prompts.ts | `/api/prompt-templates` | 7 |
| reviews.ts | `/api/reviews`, `/api/issue-tags` | 4 |
| invocations.ts | `/api/invocations` | 2 |
| models.ts | `/api/model-providers`, `/api/ai-models`, `/api/task-types` | 3 |
| logs.ts | `/api/logs/operation`, `/api/logs/login` | 2 |
| statistics.ts | `/api/statistics` | 14 |
| courses.ts | `/api/learning/courses` | 2 |
| **合计** | | **85 个方法** |

### 3. 基础设施

- `src/lib/api.ts`：axios 客户端（token 注入 + 401 自动跳登录）
- `src/lib/toast.ts`：sonner 包装（统一 success/error/info/warning）
- `src/lib/useApi.ts`：通用 React Hook（loading/error/data/refetch）
- `src/stores/auth.ts`：Zustand auth store（persist 到 localStorage）
- `src/lib/router-guard.tsx`：路由守卫（未登录跳 `/login`、按角色分流）
- `src/app/components/Layout.tsx`：顶栏 + 侧边栏 + 用户菜单 + 退出登录

## 联调修复

迁移完成后通过 28 端点 smoke test，发现并修复 3 个后端 bug：

| Bug | 位置 | 根因 | 修复 |
|---|---|---|---|
| **Auth Header 注入错误** | `backend/app/services/auth_service.py:get_current_user_dependency` | `authorization: str = ""` 永远拿不到 header，导致 `/api/learning/*` 全部 401 | 改为 `Header(None, alias="Authorization")` |
| **Cursor closed** | `backend/app/repositories/learning_repo.py:list_courses` | `with get_db_cursor()` 出块后 cursor 关闭，循环内仍用 cursor | 把 for 循环移入 with 块 |
| **表名错误** | `backend/app/repositories/statistics_learning_repo.py` | SQL 用 `invocations`，实际表名 `ai_invocations` | 改表名 |

另外补全了 `ai_invocations` 表的 `cost` 和 `is_deleted` 两列。

## 验证结果

```
========== API Smoke Test ==========
✅ login admin (admin/Admin@123)
✅ login teacher (teacher1/123456)
✅ login student (student1/123456)
✅ auth/me
✅ GET /users (6 users)
✅ GET /auth/roles (3 roles)
✅ GET /statistics/overview
✅ GET /statistics/learning-overview
✅ GET /statistics/weak-knowledge-points
✅ GET /statistics/costs
✅ GET /statistics/invocation-trend
✅ GET /learning/courses (3 courses)
✅ GET /learning/tasks
✅ GET /learning/resources
✅ GET /learning/feedbacks
✅ GET /profiles/
✅ GET /model-providers
✅ GET /ai-models
✅ GET /task-types
✅ GET /projects
✅ GET /prompt-templates
✅ GET /reviews/pending
✅ GET /issue-tags
✅ GET /invocations
✅ GET /logs/operation
✅ GET /logs/login
✅ login wrong password rejected
✅ no token → 401
========== 28 passed, 0 failed ==========
```

前端 `tsc --noEmit` 0 errors，vite 编译通过。

## Git 提交记录

12 个提交从 `3939c53` 推进到 `f8fe249`，全部已推送到 `origin/main`：

```
f8fe249 fix(frontend+backend): 联调 28 个 API 端点 + 修复 3 类 bug
3b782cb feat(frontend): Admin 11 页面接入 API
becee46 feat(frontend): Student 页面接入 API - 7 / 7
240d18a feat(frontend): Teacher Review/Library/AgentWorkbench/KnowledgeBase 接入 API
609a044 feat(frontend): TeacherDashboard/Courses/Tasks 接入 API
1ec4ec7 feat(frontend): Login + Layout 接入真实用户
cb255c8 feat(frontend): 17 个 API 模块
7554ee2 feat(frontend): 基础架构 - axios/Zustand/useApi/router-guard/Toast
a219a87 chore(frontend): 项目身份 + Vite proxy + 依赖
2cbc97f chore: 添加 langgraph-checkpoint-sqlite
1cd5cca fix(backend): 解决 main.py 和 learning.py 残留的 git 合并冲突
adcb8c2 chore: 切换前端到 React 18 + shadcn/ui 模板
```

## 旧前端位置

`frontend_old/` 目录保留旧 Vue 3 代码作为历史参考，**已加入 `.gitignore` 不进仓库**。仅本地可见，团队成员如需查阅可直接访问。

## 后续工作

- [ ] PostgreSQL pgvector 知识库 RAG 端到端联调
- [ ] MinIO 对象存储对接（学习资源 PDF/视频上传）
- [ ] 教师/学生/管理员三角色端到端 UI 测试（Playwright）
- [ ] 前端打包体积优化（vite build + chunks 分析）
- [ ] 暗黑模式 / 主题切换（shadcn/ui 已支持，按需）
