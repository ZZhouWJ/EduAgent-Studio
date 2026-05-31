# TASK-014: 前端项目空间、任务与版本基础页面

## 任务目标

完成前端项目空间、任务与版本基础页面，并与后端项目 / 任务相关接口完成基础对接。

本阶段是在 Stage-13 已完成的 V3 Admin Vite 前端模板底座上继续开发，必须保持现有模板结构、许可证说明、品牌替换和登录布局能力。

## 允许实现

1. 项目列表页；
2. 项目创建弹窗；
3. 项目详情页；
4. 项目成员列表；
5. 项目任务列表；
6. 创建任务弹窗；
7. 任务详情基础页；
8. 分支列表；
9. 输出版本列表；
10. 输出详情查看；
11. 与后端项目 / 任务相关接口对接。

## 允许修改

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-014-frontend-project-task-pages.md`

## 禁止修改

- `database/*`
- `docs/01_数据库Schema冻结说明.md`

如确需修改后端 CORS 或极少量前端联调配置，必须先在 handoff 中说明原因；不得修改后端业务 service / repository。

## 禁止实现

1. 前端 AI 生成完整交互；
2. 前端审核中心完整页面；
3. 前端成果库完整页面；
4. 前端统计看板完整页面；
5. 新增后端业务模块；
6. 修改数据库结构。

## 接口范围

优先对接 Stage-04 / Stage-05 已实现的后端接口：

### 项目空间

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `PUT /api/projects/{project_id}`
- `DELETE /api/projects/{project_id}`
- `GET /api/projects/{project_id}/members`
- `POST /api/projects/{project_id}/members`
- `PUT /api/projects/{project_id}/members/{member_id}`
- `DELETE /api/projects/{project_id}/members/{member_id}`
- `POST /api/projects/{project_id}/archive`

### 任务与版本

- `GET /api/projects/{project_id}/tasks`
- `POST /api/projects/{project_id}/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/outputs`
- `GET /api/outputs/{output_id}`
- `GET /api/outputs/{output_id}/timeline`
- `POST /api/tasks/{task_id}/outputs/manual`

## 页面要求

### 项目列表页

必须包含：

1. 项目列表表格；
2. 分页；
3. keyword 搜索；
4. status 筛选；
5. 创建项目按钮；
6. 查看项目详情入口；
7. 统一 loading / empty / error 状态；
8. 不展示 password_hash、API Key 等敏感字段。

### 项目创建弹窗

必须包含：

1. project_name；
2. project_type；
3. description；
4. status；
5. 表单校验；
6. 提交成功后刷新项目列表。

### 项目详情页

必须包含：

1. 项目基础信息；
2. owner 基本信息；
3. 项目成员列表；
4. 项目任务列表入口或内嵌任务列表；
5. 返回项目列表入口。

### 项目成员列表

必须包含：

1. 成员表格；
2. 添加成员弹窗；
3. 修改成员角色；
4. 移除成员；
5. project_role 只能使用 `member / leader / reviewer / teacher`；
6. 不展示 password_hash。

### 项目任务列表

必须包含：

1. 任务表格；
2. page / page_size；
3. status 过滤；
4. keyword 搜索；
5. 创建任务按钮；
6. 进入任务详情入口。

### 创建任务弹窗

必须使用真实接口字段：

- `task_type_id`
- `title`
- `description`
- `assignee_id`
- `priority`
- `due_date`

不得使用错误字段：

- `task_name`
- `task_type`

### 任务详情基础页

必须包含：

1. 任务基础信息；
2. 所属项目基础信息；
3. 创建人 / 负责人基础信息；
4. 分支列表；
5. 输出版本列表；
6. 输出详情查看入口。

### 分支列表

必须包含：

1. 分支列表；
2. 创建分支弹窗；
3. base_output_id 可为空；
4. 仅做基础展示和创建，不实现分支合并交互。

### 输出版本列表和详情

必须包含：

1. 输出版本列表；
2. 列表中避免展示完整 content；
3. 输出详情查看；
4. 输出详情展示完整 content；
5. lock_version 展示；
6. 版本时间线基础展示。

## 前端工程要求

1. 继续使用 V3 Admin Vite 现有布局、路由、Pinia、Axios 封装；
2. 新增 API 封装应集中在 `frontend/src` 合理目录中；
3. API 调用必须复用统一 request 封装；
4. 必须适配后端统一返回格式 `{ code, message, data }`；
5. token 必须继续通过现有登录状态自动携带；
6. 页面必须有 loading、empty、error、分页等基本状态；
7. 不得写死真实 token、真实密码、真实 API Key；
8. 不得使用模板 Mock 数据冒充真实业务数据；
9. 如果需要占位数据，必须明确为静态 UI 占位，不得当作接口返回结果。

## 验收要求

1. `npm run build` 在可用 Node 环境中应通过；如果当前环境无 Node，必须在 handoff 中说明；
2. 项目列表、项目详情、任务列表、任务详情相关页面路由可访问；
3. 登录状态失效时仍能回到登录页；
4. 不出现 `/api/auth/register`；
5. 不出现 Apifox Mock API；
6. 不越界实现 AI 生成完整交互、审核中心完整页面、成果库完整页面、统计看板完整页面。

## Handoff 要求

完成后创建：

- `cursor_and_codex_chat/handoff/HANDOFF-014-frontend-project-task-pages.md`

handoff 必须说明：

1. 修改文件清单；
2. 新增页面和路由；
3. 新增 API 封装；
4. 已对接的后端接口；
5. 未实现且留待后续阶段的功能；
6. `npm install` / `npm run build` 执行结果或环境限制；
7. 是否修改后端配置，如有必须说明原因。
