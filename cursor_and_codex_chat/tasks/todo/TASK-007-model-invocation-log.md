# TASK-007 模型管理、Mock 模型调用、调用日志和成本记录模块

## 任务目标

完成模型管理、Mock 模型调用、调用日志和成本记录模块，使系统能够通过 Mock ModelAdapter 执行一次任务生成流程，并写入 `ai_invocations`、`task_outputs`、`cost_records` 和 `operation_logs`。

本阶段不实现审核中心、成果库、统计看板或前端页面。

## 前置条件

- Stage-01 数据库脚本已通过静态审查；
- Stage-02 FastAPI 后端基础框架已通过；
- Stage-03 用户登录与权限基础模块已通过；
- Stage-04 项目空间管理模块已通过；
- Stage-05 任务与版本管理模块已通过；
- Stage-06 提示词模板管理模块已通过。

## 允许实现

1. 模型供应商列表接口；
2. 模型列表接口；
3. 创建模型供应商接口；
4. 创建 AI 模型接口；
5. API 配置列表接口；
6. 创建 API 配置接口；
7. API Key AES-GCM 加密保存；
8. Mock ModelAdapter；
9. 任务模型生成接口；
10. `ai_invocations` 写入；
11. `task_outputs` 写入；
12. `cost_records` 写入；
13. `operation_logs` 写入；
14. 调用日志列表接口；
15. 调用详情接口。

## 建议接口

请以 `docs/02_接口契约与页面清单.md` 为准。如文档已有明确路径，必须优先遵守文档。

建议至少实现：

- `GET /api/model-providers`
- `POST /api/model-providers`
- `GET /api/ai-models`
- `POST /api/ai-models`
- `GET /api/api-configs`
- `POST /api/api-configs`
- `POST /api/tasks/{task_id}/generate`
- `GET /api/invocations`
- `GET /api/invocations/{invocation_id}`

## 允许修改文件

- `backend/app/routers/models.py`
- `backend/app/routers/invocations.py`
- `backend/app/services/model_service.py`
- `backend/app/services/invocation_service.py`
- `backend/app/repositories/model_repo.py`
- `backend/app/repositories/invocation_repo.py`
- `backend/app/adapters/base_adapter.py`
- `backend/app/adapters/mock_writer_adapter.py`
- `backend/app/adapters/mock_code_adapter.py`
- `backend/app/adapters/mock_reviewer_adapter.py`
- `backend/app/utils/crypto.py`
- `backend/app/main.py`
- `backend/requirements.txt`
- `cursor_and_codex_chat/handoff/HANDOFF-007-model-invocation-log.md`

如确实需要复用 task 输出版本逻辑，可少量修改：

- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`

但必须在 handoff 中说明理由。

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 审核中心；
2. 成果库；
3. 统计看板；
4. 前端页面。

## 数据库与 Schema 要求

必须严格遵守 `docs/01_数据库Schema冻结说明.md` 和 `database/02_create_tables.sql`。

涉及表：

- `model_providers`
- `ai_models`
- `api_configs`
- `ai_invocations`
- `task_outputs`
- `cost_records`
- `operation_logs`
- 可读取：`project_tasks`、`task_branches`、`prompt_versions`

禁止：

- 新增表；
- 修改表结构；
- 新增未定义字段；
- 新增未定义状态值；
- 保存明文 API Key；
- 用 ORM 替代核心 SQL。

## 权限要求

1. 所有接口必须从 `Authorization: Bearer token` 解析当前用户；
2. 模型供应商、AI 模型、API 配置的创建建议限制为 admin；
3. 模型和供应商列表可允许已登录用户查看；
4. API 配置列表不得返回完整 API Key；
5. 普通用户不得查看完整 API Key；
6. 任务生成接口只允许 admin 或有权访问该任务所属项目的项目成员调用；
7. 非项目成员不得为无关项目任务生成内容；
8. 调用日志列表 admin 可查看全部，普通成员只能查看自己有权限项目内的调用记录。

## API Key 安全要求

1. API Key 不得明文存储；
2. 必须使用 AES-GCM 加密保存；
3. 数据库只允许保存：
   - `encrypted_api_key`
   - `key_iv`
   - `key_tag`
   - `key_version`
   - `key_mask`
4. 加密主密钥必须来自环境变量或配置，不得硬编码到代码；
5. 返回给前端时只能返回 `key_mask`；
6. 日志中不得出现完整 API Key；
7. Mock 配置也不得使用明文真实 Key。

## Mock ModelAdapter 要求

1. 定义基础 adapter 接口；
2. 至少实现以下 Mock 适配器：
   - `MockWriterAdapter`
   - `MockCodeAdapter`
   - `MockReviewerAdapter`
3. Mock 输出应体现不同风格；
4. Mock 调用不访问外网；
5. Mock 调用仍必须写入 `ai_invocations`、`task_outputs`、`cost_records`、`operation_logs`。

## 任务生成接口要求

`POST /api/tasks/{task_id}/generate` 必须：

1. 校验任务存在且未删除；
2. 校验当前用户有权限访问该任务所属项目；
3. 校验 `branch_id` 属于当前 task；
4. 校验模型存在且未删除；
5. 如传入 `prompt_version_id`，校验版本存在且未删除；
6. 使用 Mock Adapter 生成内容；
7. 写入 `ai_invocations`；
8. 成功时写入 `task_outputs`；
9. 写入 `cost_records`；
10. 写入 `operation_logs`；
11. 上述写操作必须在同一事务内；
12. 失败调用也应写入 `ai_invocations`，状态为 `failed` 或 Schema 允许的失败状态；
13. 不得实现审核中心或成果库逻辑。

## task_outputs 要求

生成成功写入 `task_outputs` 时：

1. `source_type` 必须为 `ai_generated`；
2. `status` 必须使用 Schema 允许值；
3. `version_no` 应自动生成，避免重复；
4. `lock_version` 应符合当前数据库默认或显式设定；
5. `last_modified_by` 应为当前用户；
6. `last_modified_at` 应为当前时间；
7. 不得覆盖已有输出版本。

## 成本记录要求

写入 `cost_records` 时：

1. 使用 `ai_models.input_price`、`output_price`、`price_unit` 计算成本；
2. 保存 `input_tokens`、`output_tokens`、`total_tokens`；
3. 保存 `input_cost`、`output_cost`、`total_cost`；
4. 保存 `currency`；
5. 成本计算可课程版简化，但不得硬编码为永远 0，除非 Mock 模型单价确实为 0 并在 handoff 中说明。

## 调用日志接口要求

1. `GET /api/invocations` 支持分页；
2. 支持按 `project_id`、`task_id`、`model_id`、`status`、时间范围等基础筛选；
3. 普通用户只能查看自己有权限项目内的调用记录；
4. admin 可查看全部；
5. `GET /api/invocations/{invocation_id}` 必须做权限校验；
6. 不得返回 API Key 或加密明文。

## 统一返回格式

成功格式必须保持：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误格式必须类似：

```json
{
  "code": 4001,
  "message": "权限不足",
  "data": null
}
```

不得新增不一致的返回格式。

## 交付要求

完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-007-model-invocation-log.md`

handoff 必须说明：

1. 实现了哪些接口；
2. 修改了哪些文件；
3. 是否修改了允许范围之外的文件；
4. API Key 如何加密保存；
5. Mock Adapter 如何选择；
6. 任务生成如何写入 `ai_invocations`、`task_outputs`、`cost_records`、`operation_logs`；
7. 是否使用事务；
8. 是否执行语法检查；
9. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/models.py app/routers/invocations.py app/services/model_service.py app/services/invocation_service.py app/repositories/model_repo.py app/repositories/invocation_repo.py app/adapters/base_adapter.py app/adapters/mock_writer_adapter.py app/adapters/mock_code_adapter.py app/adapters/mock_reviewer_adapter.py app/utils/crypto.py run.py
```

如当前环境可运行服务，可补充接口级测试；如无法连接 Windows MySQL，不作为本阶段静态审查阻塞，但代码本身不得存在明显运行错误。
