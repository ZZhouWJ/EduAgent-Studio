# REVIEW-014: Stage-14 前端项目空间、任务与版本基础页面审查报告

## 1. 审查结论

**需要继续修改**

Stage-14 已实现项目列表、项目创建弹窗、项目详情、成员列表、项目任务列表、任务详情、分支列表、输出版本列表与输出详情入口，整体仍保持 V3 Admin Vite + Element Plus 风格，也未发现 AI 生成、审核中心、成果库、统计看板等明显越界页面。

但存在几处前后端契约不匹配和表单校验缺失问题，会导致任务类型、分支信息、输出版本列表无法按验收要求正常展示。因此本轮不允许进入 Stage-15。

## 2. Stage-14 是否遵守任务范围

**基本遵守。**

已确认：

1. 主要实现集中在项目空间、任务与版本基础页面；
2. 未实现前端 AI 生成完整交互；
3. `/reviews`、`/artifacts`、`/statistics` 仍为占位页；
4. 未发现调用 `POST /api/tasks/{task_id}/generate`；
5. 未发现调用 `submit-review`、`adopt`、`branches/merge`、comments 等后续写操作接口；
6. 未发现新增后端业务接口；
7. 未发现修改后端 service / repository 的 Stage-14 证据。

说明：当前工作区仍有大量历史阶段修改，不能仅凭 `git status` 判断本轮越界；本轮按 handoff 和前端实际改动范围审查。

## 3. 项目 API 封装是否正确

**基本正确。**

`frontend/src/common/apis/projects/index.ts` 已封装：

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{id}`
- `GET /api/projects/{id}/members`

并复用 `@/http/axios` 统一 request 封装，未发现写死 token、Mock 数据或不存在的项目接口。

注意：文件中也封装了更新、删除、成员增删改、归档等接口，但当前 Stage-14 页面未调用这些写操作，不作为越界问题。

## 4. 任务 API 封装是否正确

**部分不正确。**

已封装：

- `GET /api/projects/{id}/tasks`
- `POST /api/projects/{id}/tasks`
- `GET /api/tasks/{id}`
- `GET /api/tasks/{id}/branches`
- `GET /api/tasks/{id}/outputs`
- `GET /api/outputs/{id}`
- `GET /api/outputs/{id}/timeline`

主要问题：

1. `getTaskOutputsApi()` 类型声明为 `ApiResponseData<OutputListResponse>`，前端页面也按 `res.data.items` 读取；但后端 `GET /api/tasks/{task_id}/outputs` 实际返回的是数组 `List[Dict]`，不是分页对象。
2. `Task` 类型和页面使用 `task_type_name`，但后端 `_task_row_to_dict()` 返回字段为 `type_name`。
3. `TaskBranch` 类型和页面使用 `branch_type`，但数据库 `task_branches` 表和后端返回均没有 `branch_type` 字段。

## 5. 项目列表页是否正确

**基本正确。**

`frontend/src/pages/projects/index.vue` 已实现：

- 调用 `GET /api/projects`；
- 展示项目名称、项目类型、状态、描述、负责人、创建时间；
- keyword 搜索；
- status 筛选；
- 分页；
- loading 状态；
- 空数据展示；
- 新建项目按钮和弹窗；
- 页面风格保持 Element Plus / V3 Admin Vite 风格。

未发现模板 Mock 项目数据作为真实数据。

## 6. 项目创建弹窗是否正确

**基本正确。**

请求体使用：

- `project_name`
- `project_type`
- `description`

未使用错误字段 `course_name`。`project_name`、`project_type` 已有表单规则，创建成功后关闭弹窗并刷新列表。

## 7. 项目详情页是否正确

**基本正确。**

`frontend/src/pages/projects/ProjectDetail.vue`：

- 路由 `/projects/:projectId` 已配置；
- 调用项目详情接口；
- 展示项目基础信息和负责人；
- 使用 Tabs 展示项目概览、成员、任务；
- 有返回项目列表按钮；
- 有创建任务按钮；
- 未实现成员增删改等复杂项目设置。

## 8. 项目成员列表是否正确

**正确。**

已调用 `GET /api/projects/{project_id}/members`，展示成员姓名、用户名、学号、项目角色、加入时间。未展示 `password_hash`，未实现成员新增、删除、修改 UI。

## 9. 项目任务列表是否正确

**需要修改。**

已调用 `GET /api/projects/{project_id}/tasks` 并展示任务标题、状态、优先级、负责人、截止时间、创建时间。

问题：

1. 任务类型列读取 `row.task_type_name`，但后端返回字段为 `type_name`，因此任务类型会显示为空。
2. 状态映射使用了 `pending / in_progress`，但后端任务状态包含 `draft / running / generated / submitted / approved / rejected / revision_required / adopted` 等，`draft / running / generated` 会直接显示英文原值。

## 10. 创建任务弹窗是否正确

**需要修改。**

请求字段总体方向正确：

- `task_type_id`
- `title`
- `description`
- `assignee_id`
- `priority`
- `due_date`

未发现 `task_name` / `task_type` 错误字段。

阻塞问题：

1. `<el-form>` 未绑定 `rules`，`title` 和 `task_type_id` 没有前端必填校验；
2. `handleCreateTask()` 调用 `validate()`，但没有规则时无法满足“title 必填、task_type_id 必填”的验收要求；
3. 当前表单没有负责人选择控件，`assignee_id` 虽是可选字段，但页面若保留该字段类型，建议明确不传或基于成员列表提供选择。

## 11. 任务详情页是否正确

**部分正确。**

`frontend/src/pages/tasks/TaskDetail.vue`：

- 路由 `/tasks/:taskId` 已配置；
- 调用 `GET /api/tasks/{task_id}`；
- 展示任务基础信息；
- 展示分支列表；
- 展示输出版本列表；
- 点击输出版本打开详情弹窗；
- 未实现 AI 生成、人工编辑、提交审核、成果采用。

问题：

1. 任务类型读取 `task.task_type_name`，但后端返回 `type_name`，任务详情任务类型会显示为空。
2. 后端返回 `project_name`，页面未展示所属项目基础信息；这低于 TASK-014 中“任务详情基础页包含所属项目基础信息”的要求。

## 12. 分支列表是否正确

**需要修改。**

已调用 `GET /api/tasks/{task_id}/branches`，并只读展示分支列表，未实现分支合并。

问题：

- 前端使用 `branch_type` 字段，但当前数据库 `task_branches` 表和后端返回均没有 `branch_type`。页面会显示空值。

建议改为展示后端真实字段，例如 `branch_name`、`status`、`base_output_title`、`created_at`、`creator_real_name`，不要使用不存在的 `branch_type`。

## 13. 输出版本列表与详情是否正确

**不正确。**

已调用：

- `GET /api/tasks/{task_id}/outputs`
- `GET /api/outputs/{output_id}`
- `GET /api/outputs/{output_id}/timeline`

但存在阻塞问题：

1. 后端 `GET /api/tasks/{task_id}/outputs` 返回数组；
2. 前端 `TaskDetail.vue` 使用 `outputsRes.data.items || []`；
3. 因此输出版本列表会一直为空，无法展示实际输出版本；
4. `OutputListResponse` 类型与后端契约不一致。

这会直接影响 Stage-14 的“输出版本列表与详情查看”验收。

## 14. 路由与菜单是否正确

**基本正确。**

已配置：

- `/projects`
- `/projects/:projectId`
- `/tasks`
- `/tasks/:taskId`

左侧菜单“项目空间”指向 `/projects`，“任务与版本”仍为入口占位页并引导到项目列表。路由守卫沿用 Stage-13 逻辑，未发现破坏登录与基础布局。

## 15. 是否发现真实密钥泄露

**未发现。**

未发现真实数据库密码、真实 API Key、真实 JWT Secret、完整 `sk-` 密钥、真实 token。`Admin@123456` 仅作为测试账号说明出现，不是自动登录逻辑。

## 16. 是否发现越界实现

**未发现明显越界页面或调用。**

未发现：

- AI 生成完整交互；
- 审核中心完整页面；
- 成果库完整页面；
- 统计看板完整页面；
- 调用 `generate`、`submit-review`、`adopt`、`branches/merge`；
- 新增后端业务接口；
- 修改数据库结构。

## 17. 启动或静态检查

远程环境无 Node.js：

```text
node: command not found
```

无法执行：

```bash
cd frontend
npm install
npm run build
```

已进行静态审查。未发现明显导入路径缺失，但由于无法运行 `vue-tsc` / Vite build，仍需 Cursor 在具备 Node 的环境中补做构建验证。

## 18. 是否允许进入 Stage-15

**不允许。**

需要先修复 Stage-14 前端与后端契约不一致问题。

## 19. 必须修复的问题

1. 修复输出版本列表响应结构不匹配：
   - 当前后端返回数组；
   - 前端不得继续读取 `outputsRes.data.items`；
   - 可改为 `outputs.value = outputsRes.data || []`，并同步修正 `OutputListResponse` 类型，或后端已有分页契约时必须确认实际返回。
2. 修复任务类型字段：
   - 前端应使用后端返回的 `type_name`；
   - 或在 API 适配层将 `type_name` 映射为 `task_type_name`；
   - 项目任务列表和任务详情都要修。
3. 修复分支字段：
   - 不要使用不存在的 `branch_type`；
   - 展示真实字段 `branch_name`、`status`、`base_output_title`、`created_at` 等。
4. 补齐创建任务表单校验：
   - 为 `<el-form>` 添加 `rules`；
   - `title` 必填；
   - `task_type_id` 必填；
   - 创建前必须前端校验通过。
5. 任务详情页补充所属项目基础信息，例如 `project_name`。
6. 建议补齐任务状态中文映射：
   - `draft`
   - `running`
   - `generated`
   - `submitted`
   - `approved`
   - `rejected`
   - `revision_required`
   - `adopted`

## 20. 后续处理

不发布 Stage-15。创建修复任务：

- `cursor_and_codex_chat/tasks/todo/TASK-014-FIX-frontend-project-task-pages.md`
