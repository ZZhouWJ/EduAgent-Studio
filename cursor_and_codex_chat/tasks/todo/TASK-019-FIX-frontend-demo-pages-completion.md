# TASK-019-FIX 前端演示页面补齐修复任务

## 任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-019-frontend-demo-pages-completion.md` 修复 TASK-019 中剩余的前端演示阻塞问题，使轻量 Vue3 前端可以稳定演示项目、任务、AI 生成、编辑批注、审核、成果和统计流程。

## 允许修改

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-019-FIX-frontend-demo-pages-completion.md`

## 禁止修改

- `backend/*`
- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 必须修复的问题

### 1. 修复任务详情页“另存为新版本”入口

当前 `frontend/src/pages/tasks/TaskDetail.vue` 中 `tasksApi.saveAsNewVersion()` 没有被页面实际调用，`openSaveAsDialog()` 还复用了成果采用弹窗。

请修复为：

1. 新增独立的“另存为新版本”按钮；
2. 新增独立的 `saveAsDialogVisible`、`saveAsForm`、`saveAsLoading`；
3. 弹窗打开时默认复制当前 output 的 `output_title` 和 `content`；
4. 请求体使用真实字段：`output_title`、`content`、`edit_summary`、可选 `branch_id`；
5. 调用真实接口 `POST /api/outputs/{output_id}/save-as-new-version`；
6. 不得调用旧路径 `/save-as`；
7. 不得复用成果采用弹窗；
8. 成功后刷新输出版本列表；
9. 如果后端返回新 `output_id` 或 `new_output_id`，自动打开或高亮新版本详情；
10. 不得修改原版本内容。

### 2. 修复 TaskDetail 任务类型字段

`TaskDetail.vue` 任务类型显示必须优先使用后端真实字段：

```vue
{{ task?.type_name || task?.task_type_name || '-' }}
```

不得只读取 `task_type_name`。

### 3. 修复 AI 生成入口页分支选择

`frontend/src/pages/generate/index.vue` 当前没有加载任务分支，导致 `branch_id` 可能为空。

请修复为：

1. 进入配置生成步骤时，调用 `tasksApi.getBranches(selectedTask)`；
2. 默认选择 `status === 'active'` 的分支；
3. 页面显示分支选择框；
4. 提交生成时携带 `branch_id`；
5. 如果没有可用分支，应给出清晰提示，不要调用生成接口。

### 4. 模型名称展示增加 fallback

以下页面模型名称展示建议兼容：

```ts
model.display_name || model.model_name || `模型 #${model.model_id}`
```

涉及：

- `frontend/src/pages/tasks/TaskDetail.vue`
- `frontend/src/pages/generate/index.vue`
- `frontend/src/pages/models/index.vue`

## 不得破坏已通过内容

1. 登录仍调用 `/api/auth/login` 和 `/api/auth/me`；
2. 项目创建仍不使用 `course_name`；
3. 创建任务仍使用 `task_type_id` 和 `title`，不得使用 `task_name` / `task_type`；
4. 输出编辑仍携带 `lock_version`；
5. 批注枚举仍为 `comment / suggestion / approval`；
6. 批注状态仍为 `open / resolved / closed`；
7. 审核评分仍为 0-10；
8. 不得新增后端接口；
9. 不得修改数据库结构；
10. 不得写入真实密钥或 token。

## 验收要求

请在 handoff 中说明：

1. 修复了哪些文件；
2. `save-as-new-version` 的真实调用位置；
3. AI 生成入口页如何选择分支；
4. 是否执行 `npm run build`；
5. 如果当前环境无法执行，请说明原因。
