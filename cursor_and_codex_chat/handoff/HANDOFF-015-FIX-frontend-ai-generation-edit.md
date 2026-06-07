# HANDOFF-015-FIX 前端 AI 生成、输出编辑与批注交互修复

## 一、Codex 审查未通过原因

Codex 在 `REVIEW-015-frontend-ai-generation-edit.md` 中指出了 5 个阻塞问题：

1. **AI 生成表单使用 `:model="{}"`，导致校验与真实输入脱节**
2. **乐观锁冲突 code=4004 被 Axios 拦截器吞掉，前端无法识别**
3. **AI 生成结果字段与后端真实返回不一致（`error`/`display_name`/`content` vs `error_message`/`model_name`，成功项无 `content`）**
4. **编辑输出保存成功后只刷新详情，未刷新输出版本列表**
5. **另存为新版本成功后未打开/定位到新版本详情**

## 二、本次修复的文件

| 文件 | 修复内容 |
|------|----------|
| `frontend/src/http/axios.ts` | 拦截器保留业务错误码 code/message/data |
| `frontend/src/common/apis/tasks/type.ts` | `GenerateResultItem` 类型与后端字段对齐 |
| `frontend/src/pages/tasks/TaskDetail.vue` | 表单绑定、生成结果展示、编辑保存刷新、另存为导航 |

## 三、AI 生成表单绑定修复

### 问题

原代码使用 `:model="{}"`（空对象字面量），但 `genFormRules` 校验的是 `model_ids` 和 `input_text`，这些字段的输入值实际存放在独立 ref `selectedModelIds` 和 `inputText` 中，导致校验与真实输入完全脱节。

### 修复方案

建立统一的响应式表单对象 `genForm`，所有 `v-model` 和 `:rules` 均绑定此对象：

```typescript
const genFormRef = ref()

/** 统一表单对象，所有 v-model 和 rules 都绑定此对象 */
const genForm = ref({
  model_ids: [] as number[],
  branch_id: null as number | null,
  template_id: null as number | null,
  prompt_version_id: null as number | null,
  input_text: ""
})

const genRules = {
  model_ids: [
    {
      type: "array",
      required: true,
      message: "请至少选择一个模型",
      trigger: "change"
    }
  ],
  input_text: [
    { required: true, message: "请输入生成内容描述", trigger: "blur" }
  ]
}
```

模板中：

```vue
<el-form ref="genFormRef" :model="genForm" :rules="genRules" label-width="100px">
  <el-form-item label="选择模型" prop="model_ids">
    <el-select v-model="genForm.model_ids" multiple ...>
      <el-option v-for="m in modelList" :key="m.model_id"
                 :label="m.display_name" :value="m.model_id" />
    </el-select>
  </el-form-item>
  <el-form-item label="生成内容" prop="input_text">
    <el-input v-model="genForm.input_text" type="textarea" ... />
  </el-form-item>
</el-form>
```

### 校验字段说明

| 字段 | 校验规则 | 说明 |
|------|----------|------|
| `model_ids` | 必填，至少选一个 | type=array, required=true |
| `input_text` | 必填，非空 | required=true |
| `branch_id` | 可选（默认取第一个分支） | 自动填充 |
| `prompt_version_id` | 可选 | 选模板后才可用 |

提交前必须调用 `await genFormRef.value.validate()`，校验失败不调用生成接口。

## 四、Axios 拦截器修复：保留业务错误码

### 问题

原拦截器对非 `code=0` 的业务响应执行：
```javascript
ElMessage.error(apiData.message || "Error")
return Promise.reject(new Error("Error"))  // code 丢失！
```

### 修复方案

在 `frontend/src/http/axios.ts` 中，为拦截器定义了 `BusinessError` 接口，并在非 0 业务错误时构造携带 `code`/`message`/`data` 的自定义错误对象：

```typescript
/** 业务错误对象，保留 code/message/data */
interface BusinessError {
  code: number
  message: string
  data: unknown
  isBusinessError: true
}
```

业务错误分支（default case）改为：

```typescript
default: {
  // 业务错误：保留 code、message、data 到抛出对象中
  ElMessage.error(apiData.message || "Error")
  const err = new Error(apiData.message || "Error") as Error & BusinessError
  err.code = code
  err.data = apiData.data
  err.isBusinessError = true
  return Promise.reject(err)
}
```

HTTP 错误分支（网络层）也附加了 `apiCode`：

```typescript
const apiCode = get(error, "response.data.code")
// ...
if (apiCode !== undefined) {
  ;(error as Error & BusinessError).code = apiCode
  ;(error as Error & BusinessError).isBusinessError = true
}
```

### 4004 乐观锁冲突识别

`handleEditSave()` 中通过 `(err as Record<string, unknown>)?.code === 4004` 判断：

```typescript
async function handleEditSave() {
  // ...
  try {
    await updateOutputApi(...)
    // 成功
  } catch (err: unknown) {
    const code = (err as Record<string, unknown>)?.code as number | undefined
    if (code === 4004) {
      ElMessage.error("当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。")
    }
  }
}
```

这样 `axios` 拦截器已显示过通用错误提示（`当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。`），`catch` 中不会再弹出重复的通用错误。

## 五、AI 生成结果字段对齐后端真实返回

### 后端真实返回结构

根据 `invocation_service.py` 中 `generate_task_outputs()` 的返回值：

**成功项：**
```json
{
  "model_id": 1,
  "model_name": "mock-writer",
  "invocation_id": 123,
  "output_id": 456,
  "version_no": "1",
  "status": "success",
  "input_tokens": 150,
  "output_tokens": 300,
  "latency_ms": 2500
}
```

**失败项：**
```json
{
  "model_id": 1,
  "model_name": "mock-writer",
  "invocation_id": 123,
  "status": "failed",
  "error_message": "模型不存在或未激活"
}
```

### 修复后的 `GenerateResultItem` 类型

```typescript
export interface GenerateResultItem {
  model_id: number
  model_name: string
  invocation_id: number
  output_id?: number
  version_no?: string | number
  status: string
  input_tokens?: number
  output_tokens?: number
  latency_ms?: number
  error_message?: string
}
```

删除了不存在的字段：`display_name`、`content`、`error`。

### 生成结果展示逻辑

生成成功后不再依赖返回 `content`，而是在成功后提示用户刷新输出版本列表查看结果：

```typescript
const allSuccess = genResults.value.every(r => r.status === "success")
if (allSuccess) {
  ElMessage.success("AI 生成完成，请在输出版本列表查看结果")
  await fetchOutputs()
} else {
  const failed = genResults.value.filter(r => r.status !== "failed")
  // 展示失败项的 error_message
}
```

结果卡片展示字段：`model_id`（映射为 display_name）、`status`、`error_message`（失败时）、`version_no`（成功时）、`output_id`（成功时）、`input_tokens`/`output_tokens`/`latency_ms`。

## 六、编辑保存成功后刷新输出详情和输出版本列表

### 问题

原代码 `handleEditSave()` 只调用 `refreshOutputDetail()`。

### 修复

```typescript
async function handleEditSave() {
  // ...
  await updateOutputApi(outputDetail.value.output_id, data)
  ElMessage.success("保存成功")
  editDialogVisible.value = false
  await refreshDetail()   // 刷新详情
  await fetchOutputs()     // 刷新输出版本列表
}
```

`fetchOutputs()` 调用 `getTaskOutputsApi()`，确保列表中展示的 `status`、`version_no`、`updated_at`、`lock_version` 等字段为最新状态。

## 七、另存为新版本后打开/定位新版本详情

### 问题

原代码成功后只调用 `fetchOutputs()` 刷新列表。

### 修复

```typescript
async function handleSaveAs() {
  const res = await saveOutputAsNewVersionApi(outputDetail.value.output_id, data)
  ElMessage.success(`新版本 v${res.data?.version_no} 已创建`)
  saveAsDialogVisible.value = false
  await fetchOutputs()  // 刷新输出版本列表
  if (res.data?.output_id) {
    // 合并新版本数据后打开详情
    const newOutput: TaskOutput = { ...outputDetail.value, ...res.data } as TaskOutput
    await viewOutputDetail(newOutput)
  }
}
```

## 八、是否越界实现

| 项目 | 是否实现 | 说明 |
|------|----------|------|
| 审核中心完整页面 | **否** | 未实现 |
| 成果库完整页面 | **否** | 未实现 |
| 统计看板完整页面 | **否** | 未实现 |
| 修改 backend | **否** | 仅修改前端 |
| 修改 database | **否** | 未修改 |

## 九、当前环境限制

远程 Ubuntu/WSL 环境未安装 Node，无法执行 `npm install` / `npm run build`。本次修复已完成文件级别的静态修改，所有文件均通过 linter 检查（无 lint 错误）。

## 十、Codex 复审重点

1. **AI 生成表单**：`genForm` 是否为真实响应式对象；`:model="genForm"` 是否正确绑定；`validate()` 是否在调用 API 前执行
2. **乐观锁 4004**：`axios.ts` 拦截器 default 分支是否保留了 `code`；`handleEditSave()` 是否能通过 `err.code === 4004` 判断
3. **生成结果字段**：`GenerateResultItem` 是否移除了 `display_name`、`content`、`error`；是否添加了 `error_message`、`version_no`、`input_tokens`、`output_tokens`、`latency_ms`
4. **编辑保存刷新**：成功后是否同时调用 `refreshDetail()` 和 `fetchOutputs()`
5. **另存为新版本**：成功后是否打开新版本详情（`viewOutputDetail` with new output_id）
6. **已通过内容是否被破坏**：项目详情、任务详情、分支列表、批注 CRUD 等
