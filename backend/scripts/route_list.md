# API 路由清单

> 本文档由脚本自动生成，基于 `backend/app/routers/` 目录下所有路由文件的分析。
> 最后更新时间：2026-05-31

---

## 1. 健康检查

| Method | Path | 功能说明 | 权限 |
|--------|------|----------|------|
| GET | /api/health | 服务健康检查（不依赖数据库） | 公开 |
| GET | /api/health/db | 数据库连接检查（依赖数据库） | 公开 |

---

## 2. 认证与用户

### 认证（/api/auth）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| POST | /api/auth/login | `login` | 用户登录，返回 token 和用户信息 | 公开 |
| GET | /api/auth/me | `get_me` | 获取当前登录用户信息 | 登录用户 |
| POST | /api/auth/logout | `logout` | 用户登出 | 登录用户 |

### 用户与权限（/api）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/users | `list_users` | 获取用户列表（分页+搜索） | 管理员 |
| GET | /api/roles | `list_roles` | 获取角色列表 | 登录用户 |
| GET | /api/permissions | `list_permissions` | 获取权限列表 | 登录用户 |

---

## 3. 项目空间（/api/projects）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/projects | `list_projects` | 获取项目列表（分页+搜索+状态过滤） | 登录用户 |
| POST | /api/projects | `create_project` | 创建新项目（创建人自动成为 owner/leader） | 登录用户 |
| GET | /api/projects/{project_id} | `get_project` | 获取项目详情 | 登录用户（需有权限） |
| PUT | /api/projects/{project_id} | `update_project` | 更新项目信息 | admin/owner/leader |
| DELETE | /api/projects/{project_id} | `delete_project` | 软删除项目 | admin/owner/leader |
| POST | /api/projects/{project_id}/archive | `archive_project` | 归档项目 | admin/owner/leader |
| GET | /api/projects/{project_id}/members | `list_project_members` | 获取项目成员列表 | 登录用户（需有权限） |
| POST | /api/projects/{project_id}/members | `add_project_member` | 添加项目成员 | admin/owner/leader |
| PUT | /api/projects/{project_id}/members/{member_id} | `update_project_member_role` | 修改项目成员角色 | admin/owner/leader |
| DELETE | /api/projects/{project_id}/members/{member_id} | `remove_project_member` | 移除项目成员（软删除） | admin/owner/leader |

---

## 4. 任务与版本（/api）

### 项目任务（/api/projects/{project_id}/tasks）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/projects/{project_id}/tasks | `list_project_tasks` | 获取项目任务列表（分页+搜索+状态过滤） | 登录用户（需有权限） |
| POST | /api/projects/{project_id}/tasks | `create_task` | 创建项目任务（自动创建默认主分支） | 登录用户（需有权限） |

### 任务（/api/tasks/{task_id}）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/tasks/{task_id} | `get_task_detail` | 获取任务详情 | 登录用户（需有权限） |
| PUT | /api/tasks/{task_id} | `update_task` | 更新任务信息 | 登录用户（需有权限） |
| DELETE | /api/tasks/{task_id} | `delete_task` | 软删除任务 | 登录用户（需有权限） |

### 任务分支（/api/tasks/{task_id}/branches）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/tasks/{task_id}/branches | `list_task_branches` | 获取任务分支列表 | 登录用户（需有权限） |
| POST | /api/tasks/{task_id}/branches | `create_task_branch` | 创建任务分支 | 登录用户（需有权限） |
| POST | /api/tasks/{task_id}/branches/merge | `merge_branches` | 执行分支合并 | admin/leader/teacher |

### 输出版本（/api/tasks/{task_id}/outputs）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/tasks/{task_id}/outputs | `list_task_outputs` | 获取任务输出版本列表 | 登录用户（需有权限） |
| POST | /api/tasks/{task_id}/outputs/manual | `create_manual_output` | 创建人工输出版本 | 登录用户（需有权限） |

### 输出详情（/api/outputs/{output_id}）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/outputs/{output_id} | `get_output_detail` | 获取输出版本详情（含完整 content） | 登录用户（需有权限） |
| PUT | /api/outputs/{output_id} | `update_output` | 使用乐观锁更新输出版本 | 登录用户（需有权限） |
| GET | /api/outputs/{output_id}/timeline | `get_output_timeline` | 获取输出版本时间线（基于 parent_output_id） | 登录用户（需有权限） |
| POST | /api/outputs/{output_id}/save-as | `save_output_as` | 基于已有输出另存为新版本（兼容路径） | 登录用户（需有权限） |
| POST | /api/outputs/{output_id}/save-as-new-version | `save_output_as_new_version` | 基于已有输出另存为新版本（验收指定路径） | 登录用户（需有权限） |
| POST | /api/outputs/{output_id}/adopt | `adopt_output` | 采用输出作为项目成果 | 登录用户（需有权限） |
| POST | /api/outputs/{output_id}/submit-review | `submit_for_review` | 提交输出到审核 | 登录用户（需有权限） |

### 输出批注（/api/outputs/{output_id}/comments）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/outputs/{output_id}/comments | `list_output_comments` | 查询输出的批注列表 | 登录用户（需有权限） |
| POST | /api/outputs/{output_id}/comments | `create_output_comment` | 为输出新增批注 | 登录用户（需有权限） |

### 批注（/api/comments/{comment_id}）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| PUT | /api/comments/{comment_id}/status | `update_comment_status` | 更新批注状态 | admin/teacher/project_leader/批注创建人 |

---

## 5. 提示词模板（/api）

### 任务类型（/api/task-types）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/task-types | `list_task_types` | 查询任务类型列表 | 登录用户 |

### 提示词模板（/api/prompt-templates）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/prompt-templates | `list_templates` | 分页查询提示词模板列表 | 登录用户 |
| POST | /api/prompt-templates | `create_template` | 创建提示词模板 | admin/teacher/project_leader |
| GET | /api/prompt-templates/{template_id} | `get_template_detail` | 获取模板详情 | 登录用户 |
| PUT | /api/prompt-templates/{template_id} | `update_template` | 更新提示词模板 | admin/teacher/project_leader/模板创建人 |
| DELETE | /api/prompt-templates/{template_id} | `delete_template` | 软删除提示词模板 | admin/teacher/project_leader/模板创建人 |

### 提示词版本（/api/prompt-templates/{template_id}/versions）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/prompt-templates/{template_id}/versions | `list_template_versions` | 查询模板的版本列表 | 登录用户 |
| POST | /api/prompt-templates/{template_id}/versions | `create_version` | 创建提示词版本 | admin/teacher/project_leader/模板创建人 |
| POST | /api/prompt-templates/{template_id}/versions/{version_id}/activate | `activate_version` | 启用指定版本为当前活动版本 | admin/teacher/project_leader/模板创建人 |

---

## 6. 模型管理（/api）

### 模型供应商（/api/model-providers）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/model-providers | `list_providers` | 查询模型供应商列表 | 登录用户 |
| POST | /api/model-providers | `create_provider` | 创建模型供应商 | 管理员 |

### AI 模型（/api/ai-models）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/ai-models | `list_models` | 分页查询 AI 模型列表 | 登录用户 |
| POST | /api/ai-models | `create_model` | 创建 AI 模型 | 管理员 |

### API 配置（/api/api-configs）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/api-configs | `list_api_configs` | 查询 API 配置列表（不返回加密字段） | 管理员 |
| POST | /api/api-configs | `create_api_config` | 创建 API 配置（API Key 加密保存） | 管理员 |

---

## 7. 模型调用与日志（/api）

### 任务模型生成（/api/tasks/{task_id}/generate）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| POST | /api/tasks/{task_id}/generate | `generate_task_outputs` | 任务模型生成（调用 Mock 模型，支持批量模型调用） | 登录用户（需有权限） |

### 调用日志（/api/invocations）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/invocations | `list_invocations` | 分页查询调用日志列表 | admin：全部；普通成员：仅自己有权限项目 |
| GET | /api/invocations/{invocation_id} | `get_invocation_detail` | 获取调用详情 | 登录用户（需有项目访问权限） |

---

## 8. 人工编辑与批注

> 相关端点已整合到"任务与版本"模块中：
> - `/api/outputs/{output_id}/comments` - 批注列表与新增
> - `/api/comments/{comment_id}/status` - 批注状态更新

---

## 9. 审核中心（/api）

### 输出审核（/api/outputs/{output_id}）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| POST | /api/outputs/{output_id}/submit-review | `submit_for_review` | 提交输出到审核 | 登录用户（需有权限） |

### 审核（/api/reviews）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/reviews/pending | `list_pending_reviews` | 查询待审核列表（分页） | 登录用户（需有权限） |
| GET | /api/reviews/{request_id} | `get_review_detail` | 获取审核详情（含完整输出内容） | 登录用户（需有权限） |
| POST | /api/reviews/{request_id}/complete | `complete_review` | 完成审核（提交评分与评价） | 登录用户（需有权限） |

### 问题标签（/api/issue-tags）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/issue-tags | `list_issue_tags` | 查询所有可用的问题标签 | 登录用户 |

---

## 10. 成果库（/api）

### 项目成果（/api/projects/{project_id}/artifacts）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/projects/{project_id}/artifacts | `list_project_artifacts` | 查询项目成果列表（分页） | 登录用户（需有权限） |

### 成果详情（/api/artifacts）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/artifacts/{adopted_id} | `get_artifact_detail` | 获取成果详情（含完整内容） | 登录用户（需有权限） |

---

## 11. 统计看板（/api/statistics）

| Method | Path | 函数名 | 功能说明 | 权限 |
|--------|------|--------|----------|------|
| GET | /api/statistics/overview | `get_overview` | 首页统计概览 | admin：全局；其他：参与项目范围 |
| GET | /api/statistics/projects | `list_project_stats` | 项目维度统计列表（支持 project_id 过滤） | admin：所有项目；其他：参与项目 |
| GET | /api/statistics/model-calls | `get_model_call_stats` | 模型调用统计（支持日期范围过滤） | 登录用户 |
| GET | /api/statistics/costs | `get_cost_stats` | 成本统计（支持日期范围过滤） | 登录用户 |
| GET | /api/statistics/reviews | `get_review_stats` | 审核质量统计（支持 project_id 过滤） | 登录用户 |
| GET | /api/statistics/member-contributions | `get_member_contribution_stats` | 成员贡献统计（支持 project_id 过滤） | 登录用户 |
| GET | /api/statistics/recent-activities | `get_recent_activities` | 最近操作动态（limit 默认 20，最大 100） | 登录用户 |

---

## 汇总统计

| 模块 | 端点数量 |
|------|----------|
| 健康检查 | 2 |
| 认证与用户 | 6 |
| 项目空间 | 10 |
| 任务与版本 | 22 |
| 提示词模板 | 9 |
| 模型管理 | 5 |
| 模型调用与日志 | 3 |
| 审核中心 | 5 |
| 成果库 | 2 |
| 统计看板 | 7 |
| **总计** | **71** |

---

## 权限说明

| 标识 | 说明 |
|------|------|
| 公开 | 无需认证即可访问 |
| 登录用户 | 需要有效的 Bearer Token |
| 管理员 | 需要 admin 角色 |
| admin/owner/leader | 需要 admin 角色或项目 Owner/Leader 角色 |
| admin/teacher/project_leader | 需要 admin/teacher/project_leader 角色之一 |
| 需有权限 | 需要项目访问权限（项目成员或管理员） |

---

*本文件由 `backend/scripts/route_list.md` 脚本自动生成*
