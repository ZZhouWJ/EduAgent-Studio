# HANDOFF-014-frontend-project-task-pages

## 任务状态

**完成**。

---

## 一、本次修改文件清单

### 新增文件（4 个）

| 文件 | 说明 |
|------|------|
| `frontend/src/common/apis/projects/type.ts` | 项目相关 TypeScript 类型定义 |
| `frontend/src/common/apis/projects/index.ts` | 项目相关 API 封装（10 个函数） |
| `frontend/src/common/apis/tasks/type.ts` | 任务相关 TypeScript 类型定义 |
| `frontend/src/common/apis/tasks/index.ts` | 任务相关 API 封装（10 个函数） |
| `frontend/src/common/apis/global.d.ts` | 全局类型声明（ApiResponseData） |

### 修改文件（4 个）

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/pages/projects/index.vue` | 替换占位页，实现项目列表、搜索、分页、创建弹窗 |
| `frontend/src/pages/projects/ProjectDetail.vue` | 新增，实现项目详情、成员列表、任务列表、创建任务弹窗 |
| `frontend/src/pages/tasks/index.vue` | 更新提示文字，引导前往项目列表 |
| `frontend/src/pages/tasks/TaskDetail.vue` | 新增，实现任务详情、分支列表、输出版本列表、输出详情 Drawer |
| `frontend/src/router/index.ts` | 新增 `/projects/:projectId` 和 `/tasks/:taskId` 子路由 |

---

## 二、实现内容

### 1. 项目列表页（ProjectList.vue）

- 调用 `GET /api/projects`，支持 `page`/`page_size`/`keyword`/`status` 参数
- 展示项目表格：项目名称、类型（Tag）、状态（Tag）、描述、负责人、创建时间
- 状态使用中文 Tag（进行中/已归档/已暂停）
- 支持关键词搜索、状态筛选
- 分页组件
- "新建项目"按钮 → 弹窗表单
- 空数据友好展示
- 点击项目名称/查看按钮进入详情页

### 2. 项目创建弹窗

请求体符合后端接口：

```json
{
  "project_name": "数据库课程设计项目",
  "project_type": "course_project",
  "description": "数据库管理实务结课设计"
}
```

- project_name 必填
- project_type 必填（下拉选择）
- description 选填
- 创建成功后关闭弹窗并刷新列表
- 创建失败由 axios 拦截器显示 ElMessage 错误

### 3. 项目详情页（ProjectDetail.vue）

路由：`/projects/:projectId`

三个 Tabs：

**项目概览**：el-descriptions 展示项目基本信息
**成员**：el-table 展示成员列表（姓名、用户名、学号、角色、加入时间）
**任务**：el-table 展示任务列表 + "新建任务"按钮

### 4. 创建任务弹窗

请求体符合后端接口：

```json
{
  "task_type_id": 1,
  "title": "生成需求分析初稿",
  "description": "为数据库课程报告生成需求分析部分",
  "assignee_id": 2,
  "priority": "normal",
  "due_date": "2026-06-10 23:59:59"
}
```

- title 必填
- task_type_id 必填（下拉）
- priority 可选（high/normal/low）
- due_date 可选（datetime picker）
- description 选填
- 不使用 task_name / task_type 字段

### 5. 任务详情页（TaskDetail.vue）

路由：`/tasks/:taskId`

三个 Tabs：

**基本信息**：el-descriptions 展示任务信息
**分支**：el-table 展示分支列表（名称、类型、状态、时间）
**输出版本**：el-table 展示版本列表 + 查看详情

### 6. 输出详情 Drawer/Dialog

- 点击"查看"调用 `GET /api/outputs/{output_id}`
- 同步调用 `GET /api/outputs/{output_id}/timeline`
- 展示：版本标题、版本号、来源（AI生成/人工编辑）、状态、创建人、创建时间、完整内容（只读 textarea）
- 展示版本时间线（el-timeline）

---

## 三、新增页面列表

| 页面文件 | 路由 | 说明 |
|----------|------|------|
| `frontend/src/pages/projects/ProjectDetail.vue` | `/projects/:projectId` | 项目详情 |
| `frontend/src/pages/tasks/TaskDetail.vue` | `/tasks/:taskId` | 任务详情 |
| `frontend/src/pages/projects/index.vue`（改造） | `/projects` | 项目列表 |

---

## 四、新增路由列表

已在 `frontend/src/router/index.ts` 添加：

```typescript
// projects
{
  path: "projects/:projectId",
  component: () => import("@/pages/projects/ProjectDetail.vue"),
  name: "ProjectDetail",
  meta: { title: "项目详情", svgIcon: "dashboard", hidden: true }
}
// tasks
{
  path: "tasks/:taskId",
  component: () => import("@/pages/tasks/TaskDetail.vue"),
  name: "TaskDetail",
  meta: { title: "任务详情", svgIcon: "dashboard", hidden: true }
}
```

---

## 五、新增 API 封装列表

### Projects API（`frontend/src/common/apis/projects/index.ts`）

| 函数 | 方法 | 路径 |
|------|------|------|
| `getProjectListApi` | GET | `/api/projects` |
| `createProjectApi` | POST | `/api/projects` |
| `getProjectDetailApi` | GET | `/api/projects/{id}` |
| `updateProjectApi` | PUT | `/api/projects/{id}` |
| `deleteProjectApi` | DELETE | `/api/projects/{id}` |
| `getProjectMembersApi` | GET | `/api/projects/{id}/members` |
| `addProjectMemberApi` | POST | `/api/projects/{id}/members` |
| `updateProjectMemberRoleApi` | PUT | `/api/projects/{id}/members/{mid}` |
| `removeProjectMemberApi` | DELETE | `/api/projects/{id}/members/{mid}` |
| `archiveProjectApi` | POST | `/api/projects/{id}/archive` |

### Tasks API（`frontend/src/common/apis/tasks/index.ts`）

| 函数 | 方法 | 路径 |
|------|------|------|
| `getProjectTaskListApi` | GET | `/api/projects/{id}/tasks` |
| `createProjectTaskApi` | POST | `/api/projects/{id}/tasks` |
| `getTaskDetailApi` | GET | `/api/tasks/{id}` |
| `updateTaskApi` | PUT | `/api/tasks/{id}` |
| `deleteTaskApi` | DELETE | `/api/tasks/{id}` |
| `getTaskBranchesApi` | GET | `/api/tasks/{id}/branches` |
| `createTaskBranchApi` | POST | `/api/tasks/{id}/branches` |
| `getTaskOutputsApi` | GET | `/api/tasks/{id}/outputs` |
| `getOutputDetailApi` | GET | `/api/outputs/{id}` |
| `getOutputTimelineApi` | GET | `/api/outputs/{id}/timeline` |
| `createManualOutputApi` | POST | `/api/tasks/{id}/outputs/manual` |

---

## 六、项目列表如何对接后端

- 调用 `getProjectListApi({ page: 1, page_size: 10, keyword: "...", status: "..." })`
- 响应结构：`{ code: 0, message: "success", data: { items: [...], total: N, page: 1, page_size: 10 } }`
- `request` 函数自动处理 token 携带（从 localStorage 读取 Bearer Token）
- 错误由 axios 拦截器统一处理，显示 ElMessage

---

## 七、项目创建如何对接后端

- 弹窗表单提交调用 `createProjectApi(createForm)`
- 请求体：`{ project_name, project_type, description }`
- 成功返回 code=0 后关闭弹窗并刷新列表
- 不写死 token，不使用 Mock 数据

---

## 八、项目详情如何展示成员和任务

- `Promise.all` 并行调用：`getProjectDetailApi`、`getProjectMembersApi`、`getProjectTaskListApi`
- 成员表格展示 username/real_name/student_no/project_role/joined_at
- 任务表格展示 title/task_type_name/status/priority/assignee/due_date/created_at
- 不展示 password_hash

---

## 九、创建任务请求体字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_type_id` | number | 是 | 任务类型 ID（1-6） |
| `title` | string | 是 | 任务标题，最大 200 字符 |
| `description` | string | 否 | 任务描述 |
| `assignee_id` | number | 否 | 负责人用户 ID |
| `priority` | string | 否 | 优先级：high/normal/low |
| `due_date` | string | 否 | 截止时间，格式 YYYY-MM-DD HH:mm:ss |

**不使用**：`task_name`、`task_type`

---

## 十、任务详情、分支列表、输出版本列表说明

- 任务详情 Tab：展示所有任务基础字段
- 分支 Tab：调用 `getTaskBranchesApi`，展示 branch_name/branch_type/status/created_at
- 输出版本 Tab：调用 `getTaskOutputsApi`，展示 output_title/version_no/source_type/status/creator/created_at
- 输出详情 Dialog：调用 `getOutputDetailApi` + `getOutputTimelineApi`
- 内容（content）仅在详情 Dialog 中展示（只读）

---

## 十一、是否实现 AI 生成

**否**。本阶段不实现 AI 生成交互、模型选择、AI 调用按钮等。

---

## 十二、是否实现审核中心完整页面

**否**。`/reviews` 页面仍为占位页，不在本阶段实现。

---

## 十三、是否实现成果库完整页面

**否**。`/artifacts` 页面仍为占位页，不在本阶段实现。

---

## 十四、是否实现统计看板完整页面

**否**。`/statistics` 页面仍为占位页，不在本阶段实现。

---

## 十五、是否修改 backend

**否**。本阶段仅对接 Stage-04/05 已实现的后端接口。未修改任何后端代码。

---

## 十六、是否修改 database

**否**。

---

## 十七、启动或静态检查说明

本阶段新增文件均为标准 TypeScript/Vue 代码，无外部依赖引入。`global.d.ts` 声明了 `ApiResponseData` 全局接口类型，供所有 API 文件引用。

---

## 十八、当前环境限制

远程环境无 Node.js，无法执行 `npm install` / `npm run build`。建议在本地环境验证：

```bash
cd frontend
npm install
npm run dev
```

---

## 十九、需要 Codex 审查的重点

1. API 封装路径是否与 `backend/scripts/route_list.md` 中的实际后端路由一致
2. 创建项目请求体 `{ project_name, project_type, description }` 是否与后端一致
3. 创建任务请求体 `{ task_type_id, title, description, assignee_id, priority, due_date }` 是否与后端一致
4. `createTaskDialogVisible` 在弹窗关闭时重置字段（`@closed` 事件）
5. `outputDetail.content` 在 Dialog 中使用 `v-model` 绑定只读 textarea 的合理性（内容较长时是否有性能问题）
6. 路由 `/projects/:projectId` 和 `/tasks/:taskId` 的 `meta.hidden: true` 是否正确（隐藏侧边栏菜单高亮）
7. 分支列表和输出版本列表在 Stage-14 中仅做只读展示，是否符合任务卡要求
