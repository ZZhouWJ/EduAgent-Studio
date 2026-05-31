# REVIEW-015-FIX 前端 AI 生成、输出编辑与批注交互复审报告

## 一、审查结论

审查结论：通过。

Cursor 已针对 `REVIEW-015-frontend-ai-generation-edit.md` 中的 5 个阻塞问题完成修复。本轮复审未发现新的阻塞问题，允许进入 Stage-16。

说明：远程 Ubuntu/WSL 环境当前仍未安装 Node，执行 `node -v && npm -v && npm run build` 时返回 `node: command not found`，因此本轮无法完成 `npm run build`，已改为静态审查。

## 二、AI 生成表单 `:model="{}` 问题是否修复

结论：已修复。

检查结果：

- `TaskDetail.vue` 中已移除 AI 生成表单的 `:model="{}`。
- 新增统一响应式对象 `genForm`，包含：
  - `model_ids`
  - `branch_id`
  - `template_id`
  - `prompt_version_id`
  - `input_text`
- `el-form` 已绑定 `:model="genForm"`。
- `el-form-item prop="model_ids"` 对应 `v-model="genForm.model_ids"`。
- `el-form-item prop="input_text"` 对应 `v-model="genForm.input_text"`。
- 提交前仍调用 `genFormRef.value.validate()`。
- 校验失败时不会调用 `generateTaskOutputApi()`。
- 生成请求体从 `genForm` 读取真实字段。

该问题已解决，用户选择模型并填写文本后不会再因表单 model 脱节而无法提交。

## 三、Axios 是否保留 4004 业务错误码

结论：已修复。

检查结果：

- `frontend/src/http/axios.ts` 新增业务错误对象，非 `code = 0` 时抛出的错误对象已保留：
  - `code`
  - `message`
  - `data`
  - `isBusinessError`
- HTTP 错误分支如果后端返回业务 `code`，也会附加到 error 对象。
- `handleEditSave()` 中已可通过 `err.code === 4004` 判断乐观锁冲突。
- `code = 4004` 时会显示指定提示：
  `当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。`

非阻塞建议：

- 当前 Axios default 分支仍会先 `ElMessage.error(apiData.message || "Error")`，`handleEditSave()` 中又会针对 4004 显示专用提示。在后端 message 与专用提示相同的情况下，可能出现重复提示。该问题不影响业务码保留和 4004 识别，本轮不作为阻塞项；后续可考虑在 request 层对业务错误只抛出、不统一弹窗，交由调用方处理。

## 四、AI 生成结果字段是否适配真实后端返回

结论：已修复。

检查结果：

- `GenerateResultItem` 已改为后端真实字段：
  - `model_id`
  - `model_name`
  - `invocation_id`
  - `output_id`
  - `version_no`
  - `status`
  - `input_tokens`
  - `output_tokens`
  - `latency_ms`
  - `error_message`
- 前端不再依赖成功项返回 `content`。
- 前端失败原因读取 `error_message`。
- 模型展示通过 `getModelDisplayName(model_id)` 从本地模型列表映射 `display_name / model_name`，不再假设后端生成结果返回 `display_name`。
- 生成成功后提示用户到输出版本列表查看结果。
- 生成成功后调用 `fetchOutputs()` 刷新输出版本列表。
- 未发现伪造生成内容或调用第三方大模型接口。

## 五、编辑保存后是否刷新输出版本列表

结论：已修复。

检查结果：

- `handleEditSave()` 成功后：
  - 关闭编辑弹窗；
  - 调用 `refreshDetail()` 重新拉取输出详情；
  - 调用 `fetchOutputs()` 重新拉取输出版本列表。
- 编辑请求仍携带 `lock_version`。
- 未发现仅修改本地对象冒充成功的逻辑。

## 六、另存为新版本后是否打开或定位新版本详情

结论：已修复。

检查结果：

- 仍调用正确路径：
  - `POST /api/outputs/{output_id}/save-as-new-version`
- 未调用旧路径 `/save-as`。
- 成功后读取 `res.data?.output_id`。
- 成功后调用 `fetchOutputs()` 刷新输出版本列表。
- 如果后端返回新 `output_id`，会构造新版本对象并调用 `viewOutputDetail(newOutput)` 打开新版本详情。
- 未发现修改原版本内容的逻辑。

## 七、不得破坏已通过内容

检查结果：

- AI 生成仍调用 `POST /api/tasks/{task_id}/generate`。
- 模型选择仍从 `GET /api/ai-models` 加载。
- 提示词模板仍从 `GET /api/prompt-templates` 加载。
- 提示词版本仍从 `GET /api/prompt-templates/{template_id}/versions` 加载。
- 提示词版本 ID 不再写死。
- 输出编辑仍携带 `lock_version`。
- 批注 `comment_type` 仍只提交：
  - `comment`
  - `suggestion`
  - `approval`
- 批注 `status` 仍只提交：
  - `open`
  - `resolved`
  - `closed`
- `/reviews`、`/artifacts`、`/statistics` 仍为占位页。
- 未发现新增后端接口。
- 未发现修改 `database/`。

## 八、是否发现新问题

未发现新的阻塞问题。

非阻塞建议：

- `frontend/src/http/axios.ts` 中 `isBusinessError()` 当前未被使用，后续可以删除或实际用于错误判断，减少冗余。
- 4004 冲突提示可能重复弹出，建议后续统一错误提示策略。

## 九、是否发现越界实现

未发现明显越界实现。

说明：工作区中存在大量历史阶段遗留的 backend/database/docs 修改痕迹，不能单凭 `git status` 判定为本阶段越界；结合 handoff 和本轮代码检查，Stage-15 Fix 主要集中在前端任务详情页、任务类型定义与 request 封装。

## 十、是否允许进入 Stage-16

允许进入 Stage-16。

已发布 Stage-16 任务：

`cursor_and_codex_chat/tasks/todo/TASK-016-frontend-review-artifact-statistics.md`

