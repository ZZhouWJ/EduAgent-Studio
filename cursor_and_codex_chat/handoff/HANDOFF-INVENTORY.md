# 全项目盘点结果

## 一、当前后端已有接口（共71个）

### auth (3)
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 当前用户
- `POST /api/auth/logout` - 登出

### users (3)
- `GET /api/users` - 用户列表
- `GET /api/roles` - 角色列表
- `GET /api/permissions` - 权限列表

### projects (10)
- `GET /api/projects` - 项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/:id` - 项目详情
- `PUT /api/projects/:id` - 更新项目
- `DELETE /api/projects/:id` - 删除项目
- `POST /api/projects/:id/archive` - 归档项目
- `GET /api/projects/:id/members` - 成员列表
- `POST /api/projects/:id/members` - 添加成员
- `PUT /api/projects/:id/members/:mid` - 更新成员角色
- `DELETE /api/projects/:id/members/:mid` - 移除成员

### tasks (15+)
- `GET /api/projects/:id/tasks` - 项目任务列表
- `POST /api/projects/:id/tasks` - 创建任务
- `GET /api/tasks/:id` - 任务详情
- `PUT /api/tasks/:id` - 更新任务
- `DELETE /api/tasks/:id` - 删除任务
- `GET /api/tasks/:id/branches` - 分支列表
- `POST /api/tasks/:id/branches` - 创建分支
- `POST /api/tasks/:id/branches/merge` - 合并分支
- `GET /api/tasks/:id/outputs` - 输出列表
- `POST /api/tasks/:id/outputs/manual` - 手动创建输出
- `GET /api/outputs/:id` - 输出详情
- `PUT /api/outputs/:id` - 更新输出（乐观锁）
- `GET /api/outputs/:id/timeline` - 版本时间线
- `POST /api/outputs/:id/save-as` - 另存版本
- `POST /api/outputs/:id/save-as-new-version` - 另存新版本
- `POST /api/outputs/:id/submit-review` - 提交审核
- `POST /api/outputs/:id/adopt` - 采用成果
- `GET /api/outputs/:id/comments` - 批注列表
- `POST /api/outputs/:id/comments` - 新增批注
- `PUT /api/comments/:id/status` - 更新批注状态

### prompts (7)
- `GET /api/task-types` - 任务类型
- `GET /api/prompt-templates` - 模板列表
- `POST /api/prompt-templates` - 创建模板
- `GET /api/prompt-templates/:id` - 模板详情
- `PUT /api/prompt-templates/:id` - 更新模板
- `DELETE /api/prompt-templates/:id` - 删除模板
- `GET /api/prompt-templates/:id/versions` - 版本列表
- `POST /api/prompt-templates/:id/versions` - 新增版本
- `POST /api/prompt-templates/:id/versions/:vid/activate` - 激活版本

### models (4)
- `GET /api/model-providers` - 供应商列表
- `POST /api/model-providers` - 创建供应商
- `GET /api/ai-models` - 模型列表
- `POST /api/ai-models` - 创建模型
- `GET /api/api-configs` - API配置列表
- `POST /api/api-configs` - 创建API配置

### invocations (3)
- `POST /api/tasks/:id/generate` - AI生成
- `GET /api/invocations` - 调用日志列表
- `GET /api/invocations/:id` - 调用详情

### reviews (4)
- `GET /api/reviews/pending` - 待审核列表
- `GET /api/reviews/:id` - 审核详情
- `POST /api/reviews/:id/complete` - 完成审核
- `GET /api/issue-tags` - 问题标签

### artifacts (3)
- `GET /api/projects/:id/artifacts` - 项目成果列表
- `GET /api/artifacts/:id` - 成果详情
- `POST /api/tasks/:id/branches/merge` - 分支合并

### statistics (7)
- `GET /api/statistics/overview` - 总览
- `GET /api/statistics/projects` - 项目统计
- `GET /api/statistics/model-calls` - 模型调用统计
- `GET /api/statistics/costs` - 成本统计
- `GET /api/statistics/reviews` - 审核统计
- `GET /api/statistics/member-contributions` - 成员贡献
- `GET /api/statistics/recent-activities` - 最近动态

### logs (0) - **缺失**

---

## 二、当前前端已有页面

| 路由 | 页面 | 状态 |
|------|------|------|
| `/login` | 登录页 | 基础可用 |
| `/dashboard` | 首页 | 基础可用 |
| `/projects` | 项目列表 | 基础可用 |
| `/projects/:id` | 项目详情 | 基础可用 |
| `/tasks` | 任务列表 | 基础可用 |
| `/tasks/:id` | 任务详情 | 基础可用 |
| `/generate` | AI生成 | 基础可用 |
| `/reviews` | 审核中心 | 基础可用 |
| `/artifacts` | 成果库 | 基础可用 |
| `/statistics` | 统计看板 | 基础可用 |
| `/models` | 模型管理 | 基础可用 |
| `/register` | 注册页 | **不存在** |
| `/users` | 用户管理 | **不存在** |
| `/prompts` | 提示词模板 | **不存在** |
| `/invocations` | 调用日志 | **不存在** |
| `/costs` | 成本统计 | **不存在** |
| `/logs` | 操作日志 | **不存在** |
| `/logs/login` | 登录日志 | **不存在** |

---

## 三、当前数据库已有表（27个）

全部完整，具体见 `02_create_tables.sql`。关键表已就绪：
- `users` (含 password_hash, 无 email/phone 唯一约束)
- `projects`, `project_members`
- `project_tasks`, `task_branches`, `task_outputs`
- `prompt_templates`, `prompt_versions`
- `model_providers`, `ai_models`, `api_configs`
- `ai_invocations`, `cost_records`
- `review_requests`, `output_reviews`, `output_comments`
- `adopted_outputs`, `merge_records`
- `operation_logs`, `login_logs`
- `issue_tags`, `output_issue_relations`
- `roles`, `user_roles`, `permissions`, `role_permissions`

---

## 四、已完成功能盘点

| 功能 | 后端 | 前端 | 状态 |
|------|------|------|------|
| 登录/登出 | ✅ | ✅ | 完整 |
| JWT认证 | ✅ | ✅ | 完整 |
| RBAC权限 | ✅ | 部分 | 完整 |
| 项目CRUD | ✅ | ✅ | 完整 |
| 项目成员管理 | ✅ | ✅ | 完整 |
| 任务CRUD | ✅ | ✅ | 完整 |
| 分支管理 | ✅ | ✅ | 完整 |
| 输出版本 | ✅ | ✅ | 完整 |
| 乐观锁 | ✅ | ✅ | 完整 |
| AI生成 | ✅ | ✅ | 完整（Mock） |
| 审核提交 | ✅ | ✅ | 完整 |
| 审核完成 | ✅ | ✅ | 完整 |
| 成果采用 | ✅ | ✅ | 完整 |
| 分支合并 | ✅ | 部分 | 需完善 |
| 批注协作 | ✅ | ✅ | 完整 |
| 提示词模板 | ✅ | ❌ | 缺前端 |
| 模型管理 | ✅ | ✅ | 完整 |
| 调用日志 | ✅ | ❌ | 缺前端 |
| 成本记录 | ✅ | 部分 | 缺前端页面 |
| 审核列表 | ✅ | ✅ | 完整 |
| 统计总览 | ✅ | ✅ | 完整 |
| 操作日志 | ✅ | ❌ | 缺前端 |
| 登录日志 | ✅ | ❌ | 缺前端 |
| 用户列表 | ✅ | ❌ | 缺前端 |
| 用户注册 | ❌ | ❌ | **需新增** |
| 密码修改 | ❌ | ❌ | **需新增** |
| 个人中心 | ❌ | ❌ | **需新增** |
| 用户启用/禁用 | ✅ | ❌ | 缺前端 |
| 用户角色分配 | ✅ | ❌ | 缺前端 |
| 版本对比 | ✅ | ❌ | **需新增** |
| 版本时间线 | ✅ | 部分 | 需完善 |

---

## 五、缺失功能分析

### 直接用已有接口可实现（只缺前端页面）
- 用户列表 → 已有 `GET /api/users`
- 提示词模板 → 已有全部 `prompts` 接口
- 调用日志 → 已有 `GET /api/invocations`
- 操作日志 → 已有 `operation_logs` 表
- 登录日志 → 已有 `login_logs` 表
- 成本统计 → 已有 `GET /api/statistics/costs`
- 用户启用/禁用 → 后端已支持，前端需要用户列表页面
- 用户角色分配 → 后端已支持，前端需要用户列表页面

### 需要补后端接口
- `POST /api/auth/register` - 用户注册
- `PUT /api/users/:id/password` - 修改密码
- `PUT /api/users/:id/status` - 启用/禁用用户
- `PUT /api/users/:id/roles` - 分配角色
- `GET /api/logs/operation` - 操作日志列表
- `GET /api/logs/login` - 登录日志列表
- `GET /api/outputs/compare` - 版本对比

### 需要数据库变更
- `login_logs` 表已有，可直接使用
- `operation_logs` 表已有，可直接使用
- 注册用户默认 `student_member` 角色（`user_roles` 表已支持）
- `users` 表已有 `password_hash` 字段，无需修改

---

## 六、实施计划

### 第一批：注册与账号管理
1. 后端：新增 `/api/auth/register`, `/api/users/:id/password`, `/api/users/:id/status`, `/api/users/:id/roles`
2. 后端：补全 `user_repo` 的 `create_user`, `update_user_status`, `assign_roles`
3. 前端：新增 `/register` 页面
4. 前端：新增 `/users` 用户管理页面
5. 前端：登录页增加注册链接
6. 前端：个人中心（修改密码）

### 第二批：提示词模板 + 调用审计 + 日志
7. 前端：新增 `/prompts` 提示词管理页面
8. 前端：新增 `/invocations` 调用日志页面
9. 前端：新增 `/costs` 成本统计页面
10. 前端：新增 `/logs` 操作日志页面
11. 前端：新增 `/logs/login` 登录日志页面
12. 后端：补全 `logs` 路由

### 第三批：项目空间完善
13. 项目详情页 Tabs 化（概览/成员/任务/成果/调用/日志/统计）
14. 项目搜索、状态筛选、类型筛选
15. 项目编辑、归档

### 第四批：任务工作台完善
16. 任务详情页工作台化
17. 版本时间线完善
18. 版本对比功能

### 第五批：UI 全面美化
19. 所有页面标题+说明
20. 状态 Tag 化
21. Empty 占位符
22. Loading + Error 处理
23. 登录页高级化

### 第六批：文档同步
24. 更新所有 README 和文档
25. 创建最终 handoff
