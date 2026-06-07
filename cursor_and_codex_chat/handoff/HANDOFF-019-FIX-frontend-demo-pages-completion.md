# HANDOFF-019-FIX 前端演示页面补齐修复

## 验收要求回应

### 1. 修复了哪些文件

| 文件 | 修复内容 |
|------|---------|
| `frontend/src/pages/tasks/TaskDetail.vue` | 任务类型字段 fallback、另存为新版本独立弹窗、模型名称 fallback |
| `frontend/src/pages/generate/index.vue` | 加载任务分支、默认选中 active 分支、模型名称 fallback、分支为空拦截 |
| `frontend/src/pages/models/index.vue` | 模型名称 display_name fallback |

### 2. `save-as-new-version` 的真实调用位置

`POST /api/outputs/{output_id}/save-as-new-version` 在 `frontend/src/pages/tasks/TaskDetail.vue` 的 `handleSaveAsNewVersion()` 函数中被调用（第 232 行起）。

具体流程：
1. 用户点击输出详情抽屉中的「另存为新版本」按钮（`CopyDocument` 图标）
2. `openSaveAsDialog(output)` 打开独立弹窗 `saveAsDialogVisible`，预填 `output_title` 和 `content`
3. 用户确认后调用 `handleSaveAsNewVersion()`，通过 `tasksApi.saveAsNewVersion()` 提交到真实接口
4. 成功后刷新输出版本列表，如果有返回 `output_id` 则自动打开新版本详情

新增的独立状态：
- `saveAsDialogVisible: ref(false)` — 弹窗显隐
- `saveAsLoading: ref(false)` — 提交 loading
- `saveAsForm: ref({ output_title, content, edit_summary, branch_id })` — 独立表单，不复用 adoptForm

### 3. AI 生成入口页如何选择分支

`frontend/src/pages/generate/index.vue` `goToStep3()` 进入配置步骤时并行调用：
- `loadModels()` — 加载可选模型
- `loadBranches(selectedTask.value)` — **新增**，加载该任务所有分支

`loadBranches()` 逻辑：
1. 调用 `tasksApi.getBranches(taskId)` 获取分支列表
2. 自动选中 `status === 'active'` 的分支到 `selectedBranch`
3. 页面 Step 3 表单中显示分支选择下拉框，默认显示 `b.branch_name (b.status)`

`handleGenerate()` 拦截逻辑：
- 有分支但未选择 → 提示"请选择目标分支"
- 无可用分支 → 提示"该任务没有可用分支，无法生成输出，请先创建分支"并阻止提交

### 4. 是否执行 `npm run build`

是，Windows 环境执行 `cd frontend && npm run build`，构建成功。

```
dist/assets/index-B671g-kS.js                          9.61 kB
dist/assets/TaskDetail-Dj6F5hpB.js                    23.15 kB
✓ built in 4.57s
```

### 5. 当前环境说明

Windows 10 (win32) + PowerShell，Node.js 环境可用，执行构建正常通过。

## 变更摘要

### TaskDetail.vue

**任务类型字段（问题 2）**
- 模板：`{{ task?.type_name || task?.task_type_name || "-" }}`
- 优先使用后端真实字段 `type_name`，兼容旧字段 `task_type_name`

**另存为新版本弹窗（问题 1）**
- 新增独立状态：`saveAsDialogVisible`、`saveAsLoading`、`saveAsForm`
- `openSaveAsDialog(output)` 预填 `output_title` 和 `content`，不再复用 adoptForm
- `handleSaveAsNewVersion()` 调用 `tasksApi.saveAsNewVersion()`，请求体为 `{ output_title, content, edit_summary, branch_id }`
- 成功后刷新版本列表，自动打开新版本详情
- 输出抽屉「操作」区域新增「另存为新版本」按钮（`CopyDocument` 图标，status 非 adopted 时显示）

**模型名称 fallback（问题 4）**
- `{{ m.display_name || m.model_name || `模型 #${m.model_id}` }}`

### generate/index.vue

**分支加载（问题 3）**
- 新增 `branches: ref<any[]>([])`、`branchesLoading: ref(false)`
- 新增 `loadBranches(taskId)` 函数，调用 `tasksApi.getBranches()` 并默认选中 active 分支
- `goToStep3()` 同时调用 `loadModels()` 和 `loadBranches(selectedTask.value)`
- Step 3 表单新增分支选择下拉框，无分支时显示提示
- `handleGenerate()` 增加分支空状态拦截

**模型名称 fallback（问题 4）**
- `{{ m.display_name || m.model_name || `模型 #${m.model_id}` }}`

### models/index.vue

**模型名称 fallback（问题 4）**
- 主列：`row.display_name || row.model_name || `模型 #${row.model_id}``
- 副列：`row.model_name || "-"`（避免两个字段同时为空时都显示 `-`）

## 破坏性变更检查

以下已通过内容未受影响：
- 登录调用 `/api/auth/login` 和 `/api/auth/me` — 未改动 auth 相关代码
- 项目创建不使用 `course_name` — 未改动 projects 相关代码
- 任务创建使用 `task_type_id` 和 `title` — 未改动任务创建代码
- 输出编辑携带 `lock_version` — 未改动 editOutput 代码
- 批注枚举 `comment / suggestion / approval` — 未改动
- 批注状态 `open / resolved / closed` — 未改动
- 审核评分 0-10 — 未改动
- 无新增后端接口调用 — 仅使用已有的 `save-as-new-version` 和 `getBranches`
- 无数据库结构修改
- 无真实密钥泄露
