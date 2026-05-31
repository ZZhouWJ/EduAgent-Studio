# REVIEW-015 前端 AI 生成、输出编辑与批注交互页面审查报告

## 一、审查结论

审查结论：不通过。

Stage-15 主要接口封装和页面结构已经完成，且未发现审核中心、成果库、统计看板完整页面等越界实现。但本轮发现 AI 生成表单校验绑定错误、乐观锁冲突无法被正确识别、生成结果字段与后端真实返回不完全匹配等阻塞问题，暂不允许进入 Stage-16。

说明：远程 Ubuntu/WSL 环境当前未安装 Node，执行 `node -v && npm -v && npm run build` 时返回 `node: command not found`，因此本轮无法完成 `npm run build`，已改为静态审查。

## 二、Stage-15 是否遵守任务范围

结论：基本遵守。

检查结果：

- 本阶段主要修改集中在 `frontend/src/common/apis/models`、`frontend/src/common/apis/prompts`、`frontend/src/common/apis/tasks`、`frontend/src/pages/tasks/TaskDetail.vue`。
- `/reviews`、`/artifacts`、`/statistics` 仍为占位页。
- 未发现新增后端业务接口。
- 未发现前端调用审核提交、成果采用、分支合并或统计接口作为本阶段完整功能。
- 未发现真实 API Key、JWT Secret、数据库密码或完整 `sk-` 密钥。

注意：工作区中存在大量历史阶段遗留的 backend/database/docs 修改痕迹，不能单凭 `git status` 判定为本阶段越界；结合 handoff 与本轮前端代码检查，未发现 Stage-15 新增后端业务实现。

## 三、模型与提示词 API 是否正确

结论：基本正确。

检查结果：

- `getModelListApi()` 对接 `GET /api/ai-models`。
- `getTemplateListApi()` 对接 `GET /api/prompt-templates`。
- `getTemplateVersionsApi()` 对接 `GET /api/prompt-templates/{template_id}/versions`。
- 均复用统一 `request` 封装。
- 未发现 Mock 数据或硬编码 token / API Key。

## 四、AI 生成面板是否正确

结论：不通过，存在阻塞问题。

阻塞问题 1：AI 生成表单校验绑定错误，可能导致“开始生成”无法正常提交。

位置：

- `frontend/src/pages/tasks/TaskDetail.vue:57-61`
- `frontend/src/pages/tasks/TaskDetail.vue:103-117`
- `frontend/src/pages/tasks/TaskDetail.vue:570-633`

问题说明：

- `genFormRules` 校验字段为 `model_ids` 和 `input_text`。
- 但模板中 `el-form` 使用 `:model="{}"`。
- 实际输入状态存放在独立 ref：`selectedModelIds` 与 `inputText`。
- 因此 `genFormRef.value.validate()` 校验的是空对象里的 `model_ids` / `input_text`，与真实输入值脱节。
- 用户即使选择模型并填写输入文本，也可能仍被判定为未填写，导致 `generateTaskOutputApi()` 不被调用。

修复建议：

- 改为统一的 `genForm` 对象，例如：
  - `genForm.model_ids`
  - `genForm.branch_id`
  - `genForm.template_id`
  - `genForm.prompt_version_id`
  - `genForm.input_text`
- `el-form :model="genForm"`，所有 `v-model` 与 rules 字段保持一致。
- 或取消 `el-form.validate()`，改为显式手动校验 `selectedModelIds.value.length` 与 `inputText.value.trim()`，但必须确保校验通过后才调用生成接口。

## 五、生成请求体是否正确

结论：部分正确。

检查结果：

- 当前请求体包含：
  - `model_ids`
  - `branch_id`
  - `prompt_version_id`
  - `input_text`
- 字段名与后端 `GenerateRequest` 基本一致。

需要修复的问题：

- 由于 AI 生成表单校验绑定错误，请求体逻辑可能无法被执行。
- `branch_id` 当前默认取 `branches.value[0]?.branch_id`，没有明确分支选择 UI。课程版可以接受默认主分支，但建议在 handoff 中说明；如果要更稳，应提供分支选择或明确展示默认使用第一个分支。

## 六、输出详情增强是否正确

结论：基本正确。

检查结果：

- 输出详情弹窗展示 `output_title`、`version_no`、`source_type`、`status`、`lock_version`、创建人、创建时间和 `content`。
- 提供“编辑输出”和“另存为新版本”按钮。
- 提供批注列表和新增批注表单。
- 未发现提交审核和成果采用按钮。

## 七、输出编辑是否正确携带 lock_version

结论：请求体正确，但保存后刷新不完整。

检查结果：

- `openEditDialog()` 从当前 `outputDetail.lock_version` 填充 `editForm.lock_version`。
- `handleEditSave()` 调用 `PUT /api/outputs/{output_id}` 时携带：
  - `content`
  - `lock_version`
  - `edit_summary`

需要修复的问题：

- 保存成功后只调用 `refreshOutputDetail()`，未刷新输出版本列表。
- Stage-15 要求“保存成功后刷新输出详情和输出列表”，建议保存成功后同时调用 `fetchOutputs()`。

## 八、乐观锁冲突是否正确处理

结论：不通过，存在阻塞问题。

阻塞问题 2：前端无法可靠识别后端 `code = 4004`。

位置：

- `frontend/src/pages/tasks/TaskDetail.vue:271-275`
- `frontend/src/http/axios.ts`

问题说明：

- `handleEditSave()` 试图通过 `err.code === 4004` 判断乐观锁冲突。
- 但当前 Axios 响应拦截器对所有非 `code = 0` 的业务响应执行：
  - `ElMessage.error(apiData.message || "Error")`
  - `Promise.reject(new Error("Error"))`
- 这会丢失后端返回的业务 `code` 和 `message`。
- 因此 `handleEditSave()` 中的 `err.code` 通常拿不到 `4004`，无法显示指定文案：
  `当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。`

修复建议：

- 在 `frontend/src/http/axios.ts` 中让非 0 业务错误 reject 原始 `apiData`，或构造携带 `code`、`message` 的自定义错误对象。
- 确保 `handleEditSave()` 能识别 `code === 4004` 并显示指定提示。
- 避免同时弹出通用错误和专用冲突提示造成重复提示。

## 九、另存为新版本是否正确

结论：部分正确。

检查结果：

- 已调用正确路径 `POST /api/outputs/{output_id}/save-as-new-version`。
- 未使用旧路径 `/save-as`。
- 弹窗打开时会复制当前 output content。
- `output_title`、`content` 已做必填校验。
- 成功后调用 `fetchOutputs()` 刷新输出版本列表。

需要修复的问题：

- 成功后没有打开或切换到新版本详情；Stage-15 检查项要求“成功后是否可以打开新版本详情”。
- 建议后端返回新版本 `output_id` 后，调用 `viewOutputDetail(res.data)` 或重新加载列表后定位新版本，使用户可以立即查看新版本详情。

## 十、批注列表是否正确

结论：基本正确。

检查结果：

- 已调用 `GET /api/outputs/{output_id}/comments`。
- 展示 `comment_type`、`comment_text`、批注人、状态、创建时间。
- 空状态有提示。
- 未展示 `password_hash` 或敏感字段。
- 批注状态使用 Tag 展示。

## 十一、新增批注是否正确

结论：正确。

检查结果：

- 已调用 `POST /api/outputs/{output_id}/comments`。
- `comment_type` 选项提交英文枚举：
  - `comment`
  - `suggestion`
  - `approval`
- UI 中文显示，提交值为英文。
- `comment_text` 必填。
- 成功后刷新批注列表。

## 十二、批注状态更新是否正确

结论：基本正确。

检查结果：

- 已调用 `PUT /api/comments/{comment_id}/status`。
- 提交值为英文枚举：
  - `resolved`
  - `closed`
- 成功后刷新批注列表。
- 失败由 request 拦截器提示。

非阻塞建议：

- 当前 UI 只提供“标记为已解决”和“关闭”，没有把状态改回 `open` 的入口；如课程演示需要完整三态切换，可改为下拉框。

## 十三、是否破坏 Stage-14 已通过内容

结论：未发现破坏。

检查结果：

- 项目列表、项目详情、创建任务逻辑不在本轮主要修改中。
- 任务详情仍展示所属项目基础信息。
- 分支列表仍只读。
- 输出版本列表仍兼容数组返回。
- 未发现读取 `branch_type`。
- 任务类型仍使用 `type_name`。

## 十四、是否发现真实密钥泄露

未发现。

说明：

- `frontend/src/pages/login/index.vue` 中仍展示 `admin / Admin@123456` 作为测试账号说明，属于既有课程测试说明，不是自动登录逻辑或密钥配置。
- 未发现完整 `sk-` API Key、真实 JWT Secret、数据库密码或真实 token。

## 十五、是否发现越界实现

未发现明显越界实现。

检查结果：

- `/reviews`、`/artifacts`、`/statistics` 仍为占位页。
- 未发现新增后端接口。
- 未发现前端实现审核中心完整页面、成果库完整页面或统计看板完整页面。

## 十六、是否允许进入 Stage-16

不允许进入 Stage-16。

## 十七、必须修复的问题

1. 修复 AI 生成表单校验绑定错误：
   - 不得使用 `:model="{}`；
   - `model_ids` 和 `input_text` 必须与真实表单数据绑定；
   - 校验通过后才能调用 `POST /api/tasks/{task_id}/generate`。

2. 修复乐观锁冲突识别：
   - Axios 拦截器或局部调用必须保留后端业务 `code`；
   - `code = 4004` 时必须显示指定乐观锁冲突提示；
   - 不得把 4004 吞成普通 `Error`。

3. 对齐 AI 生成结果字段：
   - 后端失败结果字段为 `error_message`，前端当前读取 `error`；
   - 后端成功结果不返回 `content` 和 `display_name`，前端展示逻辑应兼容真实字段；
   - 单模型失败时应能展示失败原因。

4. 编辑输出保存成功后应同时刷新输出详情和输出版本列表。

5. 另存为新版本成功后应能打开或定位到新版本详情。

## 十八、后续动作

已创建修复任务：

`cursor_and_codex_chat/tasks/todo/TASK-015-FIX-frontend-ai-generation-edit.md`

