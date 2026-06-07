# HANDOFF-015-frontend-ai-generation-edit：前端 AI 生成、输出编辑与批注交互页面

## 任务状态

**完成**。

---

## 一、本次修改文件清单

### 新增文件（4 个）

| 文件 | 说明 |
|------|------|
| `frontend/src/common/apis/models/type.ts` | AI 模型类型定义 |
| `frontend/src/common/apis/models/index.ts` | AI 模型 API（2 个函数） |
| `frontend/src/common/apis/prompts/type.ts` | 提示词模板类型定义 |
| `frontend/src/common/apis/prompts/index.ts` | 提示词模板 API（4 个函数） |

### 修改文件（3 个）

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/common/apis/tasks/type.ts` | 新增 OutputComment、GenerateRequestData、UpdateOutputRequestData、SaveAsNewVersionRequestData、CreateCommentRequestData、UpdateCommentStatusRequestData 类型；TaskOutput 新增 lock_version |
| `frontend/src/common/apis/tasks/index.ts` | 新增 generateTaskOutputApi、updateOutputApi、saveOutputAsNewVersionApi、getOutputCommentsApi、createOutputCommentApi、updateCommentStatusApi（6 个函数） |
| `frontend/src/pages/tasks/TaskDetail.vue` | 重写：新增 AI 生成弹窗、输出详情增强、编辑弹窗、另存为新版本弹窗、批注列表、新增批注表单 |

---

## 二、新增 API 封装列表

### Models API（`frontend/src/common/apis/models/index.ts`）

| 函数 | 方法 | 路径 |
|------|------|------|
| `getModelListApi` | GET | `/api/ai-models` |
| `getProviderListApi` | GET | `/api/model-providers` |

### Prompts API（`frontend/src/common/apis/prompts/index.ts`）

| 函数 | 方法 | 路径 |
|------|------|------|
| `getTemplateListApi` | GET | `/api/prompt-templates` |
| `getTemplateDetailApi` | GET | `/api/prompt-templates/{id}` |
| `getTemplateVersionsApi` | GET | `/api/prompt-templates/{id}/versions` |
| `getTaskTypesApi` | GET | `/api/task-types` |

### Tasks API 新增（`frontend/src/common/apis/tasks/index.ts`）

| 函数 | 方法 | 路径 |
|------|------|------|
| `generateTaskOutputApi` | POST | `/api/tasks/{id}/generate` |
| `updateOutputApi` | PUT | `/api/outputs/{id}` |
| `saveOutputAsNewVersionApi` | POST | `/api/outputs/{id}/save-as-new-version` |
| `getOutputCommentsApi` | GET | `/api/outputs/{id}/comments` |
| `createOutputCommentApi` | POST | `/api/outputs/{id}/comments` |
| `updateCommentStatusApi` | PUT | `/api/comments/{id}/status` |

---

## 三、AI 生成面板实现说明

入口：任务详情页"输出版本" Tab 右上角"AI 生成"按钮。

功能：
- 模型多选（从 `/api/ai-models` 加载）
- 提示词模板选择（从 `/api/prompt-templates` 加载，可按 task_type_id 筛选）
- 选择模板后加载版本列表（从 `/api/prompt-templates/{id}/versions`）
- 输入文本 textarea（默认填入任务描述）
- 调用 `POST /api/tasks/{task_id}/generate`
- loading 状态展示
- 生成成功提示 + 刷新输出版本列表
- 生成失败或部分失败时给出提示
- 不伪造生成结果，不调用第三方真实模型

---

## 四、模型选择如何加载

- 组件挂载时调用 `getModelListApi({ page: 1, page_size: 100 })`
- 展示 `display_name` / `model_name`
- 支持多选（因为后端 `model_ids: List[int]` 支持批量）
- loading 状态，无模型时显示 empty
- 不得写死模型 ID

---

## 五、提示词版本如何加载

- 选择模板后自动加载版本：`getTemplateVersionsApi(templateId)`
- 版本列表展示 `version_no` 和 `version_name`
- `prompt_version_id` 作为最终提交字段
- 版本列表可为空（模板版本可选）

---

## 六、generate 请求体字段说明

```json
{
  "model_ids": [1, 2],
  "branch_id": 1,
  "prompt_version_id": 1,
  "input_text": "请生成数据库课程报告需求分析部分"
}
```

- `model_ids`：必填，至少选一个
- `input_text`：必填，用户输入
- `branch_id`：可选，取第一个分支
- `prompt_version_id`：可选，选择模板版本后传入

---

## 七、输出编辑如何携带 lock_version

输出详情弹窗中展示 `lock_version`（来自 `TaskOutput`）。

编辑请求体：
```json
{
  "content": "修改后的正文内容",
  "lock_version": 3,
  "edit_summary": "补充系统非功能需求"
}
```

- `lock_version` 来自后端返回，每次打开弹窗时从当前 output 读取
- 不在前端伪造 lock_version
- 保存成功后刷新输出详情和输出版本列表

---

## 八、乐观锁冲突如何处理

axios 拦截器不拦截业务 code，仅拦截 HTTP 状态码。因此在 `handleEditSave()` 的 catch 中手动判断：

```typescript
catch (err: unknown) {
  const code = (err as Record<string, unknown>)?.code
  if (code === 4004) {
    ElMessage.error("当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。")
    return
  }
  // 其他错误由拦截器统一处理
}
```

`lock_version` 不匹配时后端返回 `code: 4004`，前端检测到此 code 后显示专用提示，不展示异常堆栈。

---

## 九、另存为新版本接口路径说明

- 正确路径：`POST /api/outputs/{output_id}/save-as-new-version`
- 不使用旧路径 `/save-as`
- 请求体不含 `lock_version`
- 请求体：
```json
{
  "output_title": "需求分析人工修改版",
  "content": "另存为新版本的正文内容",
  "edit_summary": "基于 AI 初稿进行人工修改",
  "branch_id": 1
}
```
- `branch_id` 可选
- 成功后刷新输出版本列表

---

## 十、批注 comment_type 枚举说明

| UI 显示 | 提交值 |
|---------|--------|
| 批注 | `comment` |
| 修改建议 | `suggestion` |
| 审核意见 | `approval` |

UI 显示中文，提交给后端为英文枚举值。

---

## 十一、批注 status 枚举说明

| UI 显示 | 提交值 |
|---------|--------|
| 待处理 | `open` |
| 已解决 | `resolved` |
| 已关闭 | `closed` |

批注状态更新通过 `PUT /api/comments/{comment_id}/status` 提交。

---

## 十二、是否实现审核中心完整页面

**否**。`/reviews` 仍为占位页。

---

## 十三、是否实现成果库完整页面

**否**。`/artifacts` 仍为占位页。

---

## 十四、是否实现统计看板完整页面

**否**。`/statistics` 仍为占位页。

---

## 十五、是否修改 backend

**否**。本阶段仅对接 Stage-07/08 已实现的后端接口。

---

## 十六、是否修改 database

**否**。

---

## 十七、当前环境限制

远程环境无 Node.js，无法执行 `npm install` / `npm run build`。已在具备 Node 的环境中进行静态审查，确认无 linter 错误。

---

## 十八、需要 Codex 审查的重点

1. `generateTaskOutputApi` 请求体字段与后端 `GenerateRequest` Pydantic 模型是否完全对齐
2. `saveOutputAsNewVersionApi` 使用正确路径 `/save-as-new-version`，未使用旧路径 `/save-as`
3. 乐观锁冲突判断 `code === 4004` 是否准确（后端 `ConflictException` 是否真的抛出 code 4004）
4. `comment_type` 和批注 `status` 提交值均为英文枚举，UI 显示中文
5. `lock_version` 从 output 详情读取，不在前端伪造
6. 输出编辑弹窗关闭后再次打开是否正确刷新 lock_version
7. Stage-14 已通过内容（项目列表、任务类型 `type_name`、分支列表不含 `branch_type`）是否未被破坏
8. 是否未实现审核提交（`submit-review`）、成果采用（`adopt`）等后续阶段接口
