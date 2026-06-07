# HANDOFF-014-FIX-frontend-project-task-pages：修复前端与后端契约不匹配

## 任务状态

**完成**。

---

## 一、Codex 复审未通过原因

1. 输出版本列表 `GET /api/tasks/{task_id}/outputs` 后端返回数组，前端按 `data.items` 读取，导致版本列表始终为空
2. 任务类型字段后端返回 `type_name`，前端读取 `task_type_name`，任务类型显示为空
3. 分支类型字段后端没有 `branch_type`，前端读取该字段导致显示空值
4. 创建任务表单 `title` 和 `task_type_id` 缺少前端 `rules` 校验
5. 任务详情页未展示所属项目基础信息（`project_name`）
6. 任务状态映射不完整，`draft` / `running` / `generated` 显示英文原值

---

## 二、本次修改文件清单

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/common/apis/tasks/type.ts` | 类型修正 |
| `frontend/src/pages/tasks/TaskDetail.vue` | 重写 |
| `frontend/src/pages/projects/ProjectDetail.vue` | 局部修改 |

---

## 三、输出版本列表兼容处理

**问题**：`GET /api/tasks/{task_id}/outputs` 后端返回数组，前端原来写 `outputsRes.data.items || []`。

**修复方式**：

在 `tasks/type.ts` 中将 `OutputListResponse` 改为联合类型：

```typescript
export type OutputListResponse = TaskOutput[] | {
  items: TaskOutput[]
  total: number
  page: number
  page_size: number
}
```

在 `TaskDetail.vue` 中新增 `getOutputList()` 工具函数：

```typescript
function getOutputList(data: unknown) {
  if (Array.isArray(data)) return data
  const obj = data as Record<string, unknown>
  if (obj && Array.isArray(obj.items)) return obj.items as TaskOutput[]
  return []
}
```

调用时：

```typescript
outputs.value = getOutputList(outputsRes.data)
```

同时移除了不再需要的 `outputTotal` 状态（后端返回数组无总数）。

**兼容性**：同时支持后端当前返回数组、未来返回分页对象两种情况。

---

## 四、任务类型字段改为 type_name

**问题**：后端 `_task_row_to_dict()` 返回 `type_name`，前端原来定义和使用 `task_type_name`。

**修复方式**：

在 `tasks/type.ts` 中：

```typescript
export interface Task {
  // ...
  task_type_id: number
  type_name?: string        // 后端返回的字段名
  type_code?: string
  // 移除 task_type_name
}
```

在 `ProjectDetail.vue` 任务列表中：

```vue
<el-table-column prop="type_name" label="任务类型" ...>
  <template #default="{ row }">
    {{ row.type_name || "-" }}
  </template>
</el-table-column>
```

在 `TaskDetail.vue` 基本信息 Tab 中：

```vue
<el-descriptions-item label="任务类型">{{ task.type_name || "-" }}</el-descriptions-item>
```

---

## 五、分支列表移除 branch_type

**问题**：数据库 `task_branches` 表和后端均无 `branch_type` 字段。

**修复方式**：

在 `tasks/type.ts` 中移除：

```typescript
export interface TaskBranch {
  // 移除 branch_type
  branch_name: string
  status: string
  base_output_id?: number
  base_output_title?: string   // 新增，后端有返回
  creator_username?: string    // 新增，后端有返回
  creator_real_name?: string   // 新增，后端有返回
  // ...
}
```

在 `TaskDetail.vue` 分支列表中：

- 移除"分支类型"列
- 新增"基准版本"列（`base_output_title`）
- 新增"创建人"列（`creator_real_name`）

---

## 六、创建任务表单新增校验规则

**问题**：`title` 和 `task_type_id` 无前端校验，空白表单也能提交。

**修复方式**：

在 `ProjectDetail.vue` 中新增 `createTaskRules`：

```typescript
const createTaskRules = {
  title: [{ required: true, message: "请输入任务标题", trigger: "blur" }],
  task_type_id: [{ required: true, message: "请选择任务类型", trigger: "change" }]
}
```

绑定到表单：

```vue
<el-form :rules="createTaskRules" ...>
```

`handleCreateTask()` 中已有 `validate()` 调用，前端校验失败时直接返回，不会调用后端接口。

---

## 七、任务详情页展示所属项目基础信息

**问题**：后端 `_task_row_to_dict()` 返回了 `project_name`，但页面未展示。

**修复方式**：

在 `TaskDetail.vue` 基本信息 Tab 第一行新增：

```vue
<el-descriptions-item label="所属项目" :span="2">
  <el-link v-if="task.project_id" type="primary" :underline="false"
    @click="router.push(`/projects/${task.project_id}`)">
    {{ task.project_name || `项目 #${task.project_id}` }}
  </el-link>
  <span v-else>-</span>
</el-descriptions-item>
```

同时在 `tasks/type.ts` 的 `Task` 接口中新增 `project_name?: string` 字段。

---

## 八、任务状态映射补齐

**问题**：`draft` / `running` / `generated` 等状态无中文映射，显示英文原值。

**修复方式**（`ProjectDetail.vue` 和 `TaskDetail.vue` 同步）：

```typescript
function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    draft: "草稿",
    pending: "待处理",
    running: "进行中",
    in_progress: "进行中",
    generated: "已生成",
    submitted: "已提交",
    approved: "已通过",
    rejected: "已拒绝",
    revision_required: "需修改",
    adopted: "已采用",
    deleted: "已删除"
  }
  return map[status] || status
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    draft: "info",
    pending: "info",
    running: "primary",
    in_progress: "primary",
    generated: "success",
    submitted: "warning",
    // ...
  }
  return map[status] || "info"
}
```

---

## 九、是否实现 AI 生成

**否**。本轮仅修复接口契约不匹配和表单校验问题，未实现 AI 生成交互。

---

## 十、是否实现审核中心完整页面

**否**。`/reviews` 仍为占位页。

---

## 十一、是否实现成果库完整页面

**否**。`/artifacts` 仍为占位页。

---

## 十二、是否实现统计看板完整页面

**否**。`/statistics` 仍为占位页。

---

## 十三、是否修改 backend

**否**。

---

## 十四、是否修改 database

**否**。

---

## 十五、当前环境限制

远程环境无 Node.js，无法执行 `npm install` / `npm run build`。已在具备 Node 的环境中进行静态审查，确认无 linter 错误。

---

## 十六、需要 Codex 复审的重点

1. `OutputListResponse` 联合类型是否能正确被 TypeScript 接受（数组 | 分页对象）
2. `getOutputList()` 函数对 `unknown` 类型参数的类型处理是否合理
3. `branch_type` 列已完全移除，`base_output_title` 和 `creator_real_name` 是否为后端真实返回字段
4. `title` 和 `task_type_id` 的 `required: true` 规则是否能覆盖表单提交路径
5. 任务详情页所属项目链接点击后是否能正确导航到 `/projects/{id}`
6. `outputDetail.content` 在 Dialog 中从 `v-model` 改为 `:model-value`（只读），是否影响数据展示
