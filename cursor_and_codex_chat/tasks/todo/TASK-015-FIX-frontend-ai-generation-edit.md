# TASK-015-FIX 前端 AI 生成、输出编辑与批注交互修复任务

## 一、任务目标

根据 `REVIEW-015-frontend-ai-generation-edit.md` 修复 Stage-15 前端 AI 生成、输出编辑与批注交互中的阻塞问题。

本次修复只允许围绕 Stage-15 已实现页面和前端 API 做小范围修复，不得进入 Stage-16。

## 二、允许修改文件

- `frontend/src/pages/tasks/TaskDetail.vue`
- `frontend/src/common/apis/tasks/type.ts`
- `frontend/src/common/apis/tasks/index.ts`
- `frontend/src/http/axios.ts`
- 如确有必要，可少量修改：
  - `frontend/src/common/apis/models/*`
  - `frontend/src/common/apis/prompts/*`
- `cursor_and_codex_chat/handoff/HANDOFF-015-FIX-frontend-ai-generation-edit.md`

## 三、禁止修改文件

禁止修改：

- `backend/*`
- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 四、禁止实现内容

本次修复禁止实现：

1. 前端审核中心完整页面；
2. 前端成果库完整页面；
3. 前端统计看板完整页面；
4. 后端新接口；
5. 数据库结构修改；
6. 新的大模型调用能力；
7. Stage-16 内容。

## 五、必须修复的问题

### 1. 修复 AI 生成表单校验绑定错误

当前问题：

- `TaskDetail.vue` 中 AI 生成表单使用 `:model="{}"`；
- rules 校验字段为 `model_ids` 和 `input_text`；
- 真实输入值存放在 `selectedModelIds` 和 `inputText`；
- 表单校验与真实输入脱节，可能导致用户选择模型、填写内容后仍无法提交。

修复要求：

- 不得继续使用 `:model="{}`；
- 应建立真实表单对象，例如：
  - `model_ids`
  - `branch_id`
  - `template_id`
  - `prompt_version_id`
  - `input_text`
- `el-form :model`、`el-form-item prop`、`v-model`、提交请求体必须保持字段一致；
- `model_ids` 必须至少选择一个；
- `input_text` 必须非空；
- 校验失败不得调用 `generateTaskOutputApi()`；
- 校验通过后调用 `POST /api/tasks/{task_id}/generate`。

### 2. 修复乐观锁 4004 冲突识别

当前问题：

- `handleEditSave()` 通过 `err.code === 4004` 判断乐观锁冲突；
- 但 `frontend/src/http/axios.ts` 对非 `code = 0` 的业务错误会 `Promise.reject(new Error("Error"))`；
- 后端返回的业务 `code` 会丢失，导致前端无法识别 `4004`。

修复要求：

- 修改前端 request 错误处理，使业务错误 reject 时保留：
  - `code`
  - `message`
  - `data`
- 或在 `updateOutputApi()` 调用链中单独保留原始响应；
- `code = 4004` 时必须显示：
  `当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。`
- 不得同时弹出重复的通用错误和专用冲突提示。

### 3. 对齐 AI 生成结果真实字段

当前问题：

- 后端 `generate_task_outputs()` 成功项返回：
  - `model_id`
  - `model_name`
  - `invocation_id`
  - `output_id`
  - `version_no`
  - `status`
  - `input_tokens`
  - `output_tokens`
  - `latency_ms`
- 失败项返回：
  - `model_id`
  - `model_name`
  - `invocation_id`
  - `status`
  - `error_message`
- 前端类型和 UI 当前使用 `display_name`、`content`、`error`，与后端返回不完全一致。

修复要求：

- 更新 `GenerateResultItem` 类型，使其兼容后端真实字段；
- 失败原因应读取 `error_message`；
- 成功时应展示 `output_id`、`version_no`、`model_name` 等真实字段；
- 如果需要显示 `display_name`，应通过本地 `modelList` 根据 `model_id` 映射，不得假设后端返回。

### 4. 编辑输出保存成功后刷新输出列表

当前问题：

- `handleEditSave()` 保存成功后只调用 `refreshOutputDetail()`；
- 未刷新输出版本列表。

修复要求：

- 保存成功后必须同时刷新：
  - 当前输出详情；
  - 输出版本列表。

### 5. 另存为新版本成功后可查看新版本详情

当前问题：

- `handleSaveAs()` 成功后只刷新输出版本列表；
- 没有打开或定位到新版本详情。

修复要求：

- 成功后应刷新输出版本列表；
- 并基于返回的新版本 `output_id` 打开新版本详情，或在列表中明确定位到新版本；
- 不得修改原版本内容。

## 六、不得破坏已通过内容

修复时必须保持：

1. 模型列表仍从 `GET /api/ai-models` 加载；
2. 提示词模板仍从 `GET /api/prompt-templates` 加载；
3. 提示词版本仍从 `GET /api/prompt-templates/{template_id}/versions` 加载；
4. 另存为新版本路径仍为 `/api/outputs/{output_id}/save-as-new-version`；
5. 批注类型提交值仍为：
   - `comment`
   - `suggestion`
   - `approval`
6. 批注状态提交值仍为：
   - `open`
   - `resolved`
   - `closed`
7. Stage-14 已通过内容不得被破坏：
   - 项目详情；
   - 创建任务；
   - 任务详情所属项目；
   - 分支列表；
   - 输出版本列表数组兼容；
   - `type_name` 字段；
   - 不读取 `branch_type`。

## 七、交付要求

完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-015-FIX-frontend-ai-generation-edit.md`

handoff 必须说明：

1. 修复了哪些文件；
2. AI 生成表单绑定如何修复；
3. 乐观锁 4004 如何保留并提示；
4. 生成结果字段如何与后端对齐；
5. 编辑成功后如何刷新详情和列表；
6. 另存为新版本后如何查看新版本；
7. 是否执行了 `npm run build`；
8. 如无法执行，说明环境原因。

