# HANDOFF-016-FIX 前端审核中心、成果库与统计看板修复

## 一、Codex 审查未通过原因

Codex 在 `REVIEW-016-frontend-review-artifact-statistics.md` 中指出了 4 类阻塞问题：

1. `/artifacts` 主路由仍指向占位页，真实 `ArtifactList.vue` 未挂载
2. 成果库列表/详情字段与后端返回不一致，采用人、采用时间、正文显示为空
3. 统计看板字段与后端不匹配，多处显示 0 或空表
4. 分支合并 `adopt_separately` 策略可空提交

## 二、本次修复的文件

| 文件 | 修复内容 |
|------|----------|
| `frontend/src/router/index.ts` | `/artifacts` 路由从占位页改为 `ArtifactList.vue` |
| `frontend/src/common/apis/artifacts/type.ts` | 类型拆分 `AdoptedOutputListItem`（列表）和 `AdoptedOutputDetail`（详情） |
| `frontend/src/pages/artifacts/ArtifactList.vue` | 列表采用人字段改为 `adopted_by_name`，采用时间改为 `adopted_at` |
| `frontend/src/pages/artifacts/ArtifactDetail.vue` | 正文字段改为 `output_content`，采用时间改为 `adopted_at`，移除不存在的 `adopt_note` |
| `frontend/src/common/apis/statistics/type.ts` | 重写全部 7 种统计类型，对齐后端真实字段 |
| `frontend/src/common/apis/statistics/index.ts` | 4 个数组返回接口改为直接返回数组类型（非分页对象） |
| `frontend/src/pages/statistics/StatisticsDashboard.vue` | 重写全部展示区域，对齐后端字段；添加 `asArray()` 兼容函数 |
| `frontend/src/pages/tasks/TaskDetail.vue` | 添加 `adopt_separately` 输出选择 UI；添加至少选一个 output 的前端校验 |

## 三、Fix 1：`/artifacts` 路由从占位页改为真实列表

### 问题

`frontend/src/router/index.ts` 中 `/artifacts` 指向 `@/pages/artifacts/index.vue`，该文件是占位页。

### 修复

将路由 component 从 `index.vue` 改为 `ArtifactList.vue`：

```typescript
// 修复前
{
  path: "artifacts",
  component: () => import("@/pages/artifacts/index.vue"),
  ...
}

// 修复后
{
  path: "artifacts",
  component: () => import("@/pages/artifacts/ArtifactList.vue"),
  ...
}
```

左侧菜单"成果库"点击后跳转到 `/artifacts`，打开真实成果列表。

## 四、Fix 2：成果库列表/详情字段对齐后端

### 问题

- 列表读取 `adopted_by_real_name`、`created_at`（不存在或错误）
- 详情读取 `content`（应为 `output_content`）
- 详情采用时间读取 `created_at`（应为 `adopted_at`）

### 修复：类型拆分

后端两个不同的 transform 函数：

- `_artifact_row_to_dict()` → 列表（`adopted_by_name` 是 computed 字段）
- `_artifact_detail_to_dict()` → 详情（`output_content` 是正文字段）

类型拆分为：

```typescript
export interface AdoptedOutputListItem {
  adopted_by_name?: string   // 列表用
  adopted_at: string         // 列表用
  // ...
}
export interface AdoptedOutputDetail {
  adopted_by_real_name?: string  // 详情用
  adopted_at: string            // 详情用
  output_content?: string        // 详情正文
  output_status?: string
  // ...
}
export type AdoptedOutput = AdoptedOutputListItem & Partial<AdoptedOutputDetail>
```

### 修复：ArtifactList.vue

```vue
<!-- 修复前：采用人字段 -->
{{ row.adopted_by_real_name || row.adopted_by_username || "-" }}

<!-- 修复后：采用人字段（后端真实字段 adopted_by_name） -->
{{ row.adopted_by_name || "-" }}

<!-- 修复前：采用时间 -->
{{ row.created_at ? ... : "-" }}

<!-- 修复后：采用时间（后端真实字段 adopted_at） -->
{{ row.adopted_at ? new Date(row.adopted_at).toLocaleString("zh-CN") : "-" }}
```

### 修复：ArtifactDetail.vue

```vue
<!-- 修复前：正文字段 -->
<div v-if="detail.content">{{ detail.content }}</div>

<!-- 修复后：正文字段（后端真实字段 output_content） -->
<div v-if="detail.output_content">{{ detail.output_content }}</div>

<!-- 修复前：采用时间 -->
{{ detail.created_at ? ... : "-" }}

<!-- 修复后：采用时间（后端真实字段 adopted_at） -->
{{ detail.adopted_at ? new Date(detail.adopted_at).toLocaleString("zh-CN") : "-" }}
```

## 五、Fix 3：统计看板字段对齐后端 + 数组返回兼容

### 问题 3.1：后端返回数组，但前端读取 `res.data.items`

4 个接口后端直接返回数组，不是分页对象：

- `GET /api/statistics/projects` → `List[Dict]`
- `GET /api/statistics/model-calls` → `List[Dict]`
- `GET /api/statistics/member-contributions` → `List[Dict]`
- `GET /api/statistics/recent-activities` → `List[Dict]`

### 修复：API 类型改为数组

```typescript
// 修复前
request<ApiResponseData<{ items: ProjectStats[]; ... }>>

// 修复后
request<ApiResponseData<ProjectStats[]>>
```

### 修复：Dashboard 添加兼容函数

```typescript
function asArray<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[]
  if (Array.isArray((data as Record<string, unknown>)?.items)) return ((data as Record<string, unknown>).items) as T[]
  return []
}

// 使用
const res = await getProjectStatisticsApi()
projectStats.value = asArray<ProjectStats>(res.data)
```

### 问题 3.2：字段名不匹配

| 区域 | 修复前（错误字段） | 修复后（后端真实字段） |
|------|------|------|
| 概览-卡片1 | `total_projects` | `project_count` |
| 概览-卡片2 | `active_projects` | `active_project_count` |
| 概览-卡片4 | `completed_tasks` | 无 → 用 `pending_review_count` |
| 概览-卡片5 | `total_outputs` | 无 |
| 概览-卡片6 | `approved_outputs` | `artifact_count` |
| 概览-卡片7 | `total_invocations` | `invocation_count` |
| 概览-卡片8 | `total_members` | 无 |
| 成本统计 | `total_input_cost` | `input_cost` |
| 成本统计 | `total_output_cost` | `output_cost` |
| 审核统计 | `total_reviews` | `review_count` |
| 审核统计 | 无 `top_issue_tags` | `top_issue_tags[]` |
| 成员贡献 | `output_count` | `output_created_count` |
| 成员贡献 | `approved_output_count` | `artifact_adopted_count` |
| 成员贡献 | `username` | 移除（不存在） |
| 模型调用 | `total_cost` | `total_cost`（保留） |
| 模型调用 | 无 `success_count` | `success_count` |
| 模型调用 | 无 `provider_name` | `provider_name` |

### 修复：概览卡片

```vue
<!-- 修复前 -->
{{ overview.total_projects ?? 0 }}

<!-- 修复后 -->
{{ overview.project_count ?? 0 }}
{{ overview.active_project_count ?? 0 }}
{{ overview.task_count ?? 0 }}
{{ overview.pending_review_count ?? 0 }}
{{ overview.invocation_count ?? 0 }}
{{ overview.success_invocation_count ?? 0 }}
{{ overview.artifact_count ?? 0 }}
{{ overview.total_cost ?? 0 }}
```

### 修复：成本统计

```vue
{{ (costStats.input_cost ?? 0).toFixed(4) }}
{{ (costStats.output_cost ?? 0).toFixed(4) }}
{{ (costStats.total_cost ?? 0).toFixed(4) }}
{{ (costStats.total_tokens ?? 0).toLocaleString() }}
```

### 修复：审核统计

```vue
{{ reviewStats.review_count ?? 0 }}
{{ reviewStats.approved_count ?? 0 }}
{{ reviewStats.rejected_count ?? 0 }}
{{ reviewStats.revision_required_count ?? 0 }}
<!-- 新增 top_issue_tags -->
<el-tag v-for="tag in reviewStats.top_issue_tags">
  {{ tag.tag_name }} ({{ tag.tag_count }})
</el-tag>
```

### 修复：成员贡献

```vue
{{ row.real_name || `用户 #${row.user_id}` }}
{{ row.task_created_count ?? 0 }}
{{ row.output_created_count ?? 0 }}
{{ row.review_count ?? 0 }}
{{ row.artifact_adopted_count ?? 0 }}
```

## 六、Fix 4：`adopt_separately` 增加至少一个 output 的前端校验

### 问题

`handleMerge()` 没有对 `adopt_separately` 策略做输出选择校验，可在两个 output 都为空时提交。

### 修复：UI 添加 adopt_separately 的输出选择

```vue
<!-- adopt_separately: 源分支输出 -->
<el-form-item v-if="mergeForm.merge_strategy === 'adopt_separately'" label="源分支输出">
  <el-select v-model="mergeForm.source_output_id" clearable ...>
    <el-option ... />
  </el-select>
</el-form-item>
<!-- adopt_separately: 目标分支输出 -->
<el-form-item v-if="mergeForm.merge_strategy === 'adopt_separately'" label="目标分支输出">
  <el-select v-model="mergeForm.target_output_id" clearable ...>
    <el-option ... />
  </el-select>
</el-form-item>
```

### 修复：`handleMerge()` 添加校验

```typescript
if (mergeForm.value.merge_strategy === "adopt_separately") {
  if (!mergeForm.value.source_output_id && !mergeForm.value.target_output_id) {
    ElMessage.warning("分别保留时至少需要选择一个输出版本")
    return
  }
}
```

## 七、是否越界实现

| 项目 | 是否 | 说明 |
|------|------|------|
| 修改 backend | **否** | 仅修改前端 |
| 修改 database | **否** | 未修改 |
| 新增后端接口 | **否** | 未新增 |
| 进入 Stage-17 | **否** | 仅修复 Stage-16 阻塞问题 |

## 八、当前环境限制

远程 Ubuntu/WSL 环境当前未安装 Node，无法执行 `npm install` 或 `npm run build`。本次已完成所有文件级别的静态修改，所有文件均通过 linter 检查（无 lint 错误）。

## 九、需要 Codex 复审的重点

1. `/artifacts` 路由是否已指向 `ArtifactList.vue`，不再是占位页
2. 成果库列表是否正确读取 `adopted_by_name` 和 `adopted_at`
3. 成果详情是否正确读取 `output_content` 和 `adopted_at`
4. 统计看板 4 个数组接口是否使用了 `asArray()` 兼容函数，不再读取 `res.data.items`
5. 统计看板概览是否使用正确字段名（`project_count`、`active_project_count` 等）
6. `adopt_separately` 策略是否同时提供了 source/target output 选择控件
7. `adopt_separately` 校验是否阻止两个 output 都为空时提交
8. 是否未破坏 Stage-13 ~ Stage-15 已通过内容
9. 所有文件 linter 是否全部通过（已通过，无 lint 错误）
