# TASK-014-FIX: 修复前端项目空间、任务与版本基础页面

## 任务目标

根据 `REVIEW-014-frontend-project-task-pages.md` 修复 Stage-14 前端与后端接口契约不一致问题，确保项目空间、任务详情、分支列表、输出版本列表能够按真实后端返回结构正常展示。

## 允许修改

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-014-FIX-frontend-project-task-pages.md`

## 禁止修改

- `database/*`
- `docs/01_数据库Schema冻结说明.md`
- 后端 service / repository 业务逻辑

如仅为前端联调配置确需修改后端 CORS，必须在 handoff 中说明原因；不得新增后端业务接口。

## 禁止实现

1. 前端 AI 生成完整交互；
2. 前端审核中心完整页面；
3. 前端成果库完整页面；
4. 前端统计看板完整页面；
5. Stage-15 内容；
6. 数据库结构修改。

## 必须修复的问题

### 1. 输出版本列表响应结构不匹配

当前后端 `GET /api/tasks/{task_id}/outputs` 返回数组，不是分页对象。

必须修复：

1. `frontend/src/common/apis/tasks/type.ts` 中输出列表类型；
2. `frontend/src/pages/tasks/TaskDetail.vue` 中读取输出列表的逻辑；
3. 不得继续使用 `outputsRes.data.items` 读取数组接口；
4. 输出版本列表必须能展示真实数据。

### 2. 任务类型字段不匹配

当前后端返回字段为：

- `type_name`
- `type_code`

前端当前读取：

- `task_type_name`

必须修复：

1. 项目任务列表任务类型展示；
2. 任务详情任务类型展示；
3. TypeScript 类型定义；
4. 可选择直接使用 `type_name`，或在 API 适配层统一映射为 `task_type_name`，但页面必须能正常显示。

### 3. 分支字段不匹配

当前数据库和后端返回中没有 `branch_type` 字段。

必须修复：

1. 移除页面对 `branch_type` 的依赖；
2. 分支列表改为展示真实字段，例如：
   - `branch_name`
   - `status`
   - `base_output_title`
   - `created_at`
   - `creator_real_name`
3. TypeScript 类型定义同步修正；
4. 不得凭空展示不存在的分支类型。

### 4. 创建任务表单校验缺失

必须为创建任务表单添加校验：

1. `title` 必填；
2. `task_type_id` 必填；
3. 提交前必须执行前端校验；
4. 校验失败不得调用 `POST /api/projects/{project_id}/tasks`。

### 5. 任务详情补充所属项目信息

任务详情页应展示后端返回的项目基础信息，例如：

- `project_id`
- `project_name`

至少需要在基本信息 Tab 中展示所属项目。

### 6. 任务状态映射补齐

补齐任务状态中文展示，至少包含：

- `draft`
- `running`
- `generated`
- `submitted`
- `approved`
- `rejected`
- `revision_required`
- `adopted`

## 验收要求

1. `/projects` 项目列表可正常展示；
2. `/projects/:projectId` 项目详情可正常展示成员和任务；
3. 项目任务列表能显示任务类型；
4. 创建任务空标题时前端直接提示，不调用接口；
5. `/tasks/:taskId` 任务详情能显示所属项目、任务类型、分支列表；
6. 输出版本列表能显示真实后端返回的数组数据；
7. 点击输出版本能打开详情；
8. 不调用 AI 生成、审核、成果采用等 Stage-15 或后续接口；
9. 不出现 Mock 数据冒充真实业务数据；
10. 不修改数据库和后端业务逻辑。

## Handoff 要求

完成后创建：

- `cursor_and_codex_chat/handoff/HANDOFF-014-FIX-frontend-project-task-pages.md`

handoff 必须说明：

1. 修改文件清单；
2. 每个阻塞问题的修复方式；
3. 是否执行 `npm run build`；
4. 如果环境无 Node，说明限制；
5. 是否修改后端配置，如有必须说明原因。
