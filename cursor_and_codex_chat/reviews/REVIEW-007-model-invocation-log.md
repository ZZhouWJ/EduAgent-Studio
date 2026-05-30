# REVIEW-007 模型管理、Mock 模型调用、调用日志和成本记录模块审查报告

## 1. 审查结论

**不通过。**

Stage-07 已完成主要接口和模块骨架，Python 语法检查通过，且未发现本阶段修改 `database/`、`frontend/`、`docs/01_数据库Schema冻结说明.md`。但本轮发现 4 个必须修复的阻塞问题，涉及 `task_outputs.invocation_id` 关联、API Key 加密字段落库格式、软删除过滤和失败调用成本记录。

因此：**不允许进入 Stage-08**，本次不发布 `TASK-008-manual-edit-lock.md`。

## 2. Stage-07 是否遵守任务范围

结论：**基本遵守范围。**

- 已实现模型供应商、AI 模型、API 配置、Mock 调用、调用日志相关模块；
- 未发现审核中心、成果库、统计看板、前端页面实现；
- 未发现本阶段越界修改 `database/`、`frontend/`、`docs/01_数据库Schema冻结说明.md`；
- `task_service.py`、`task_repo.py` 未因 Stage-07 额外修改，符合 handoff 说明。

## 3. 模型供应商和 AI 模型接口是否正确

结论：**部分通过。**

已实现：

- `GET /api/model-providers`
- `POST /api/model-providers`
- `GET /api/ai-models`
- `POST /api/ai-models`

供应商创建限制为 admin，写入 `operation_logs`，并使用事务。AI 模型创建限制为 admin，能返回 `model_id`，也写入 `operation_logs`。

阻塞问题：

1. `backend/app/repositories/model_repo.py:164-182` 中 `list_models()` 只在没有任何筛选条件时使用 `m.is_deleted = 0`。一旦传入 `provider_id`、`status` 或 `keyword`，`where_clause` 会变成筛选条件本身，导致软删除模型可能被查出。

修复要求：

- `filters` 初始化时应包含 `m.is_deleted = 0`；
- `count_sql` 和 `data_sql` 必须都默认过滤 `m.is_deleted = 0`；
- 联表 provider 时继续限制 `p.is_deleted = 0`。

## 4. API 配置和 AES-GCM 加密是否安全

结论：**不通过。**

已实现：

- `encrypt_api_key()`；
- `decrypt_api_key()`；
- `mask_api_key()`；
- 使用 `AESGCM`；
- 主密钥来自 `API_KEY_SECRET`；
- API 配置列表不返回 `encrypted_api_key`、`key_iv`、`key_tag` 或明文 key；
- `requirements.txt` 已包含 `cryptography`。

阻塞问题：

1. `backend/app/utils/crypto.py:49-69` 返回 `bytes` 类型的 `encrypted_data`、`iv`、`tag`，而 `database/02_create_tables.sql` 中 `api_configs.encrypted_api_key` 是 `TEXT`，`key_iv` 和 `key_tag` 是 `VARCHAR(64)`，并且字段注释要求 IV / Tag 为 Base64。`backend/app/repositories/model_repo.py:326-360` 直接把 bytes 写入这些文本字段，在 MySQL `utf8mb4` 下存在写入失败或不可读风险。
2. `cursor_and_codex_chat/handoff/HANDOFF-007-model-invocation-log.md:319` 给出了完整 `api_key` 示例。虽然看起来是测试 key，但本阶段要求 handoff 中也不要输出完整 API Key，建议改为 `sk-test-****1234` 或 `<TEST_API_KEY>`。

修复要求：

- 加密工具应将 `encrypted_api_key`、`key_iv`、`key_tag` 统一 Base64 编码为字符串后写入数据库；
- 解密工具应接受 Base64 字符串并解码后再解密；
- `create_api_config()` 入库字段类型应与 Schema 文本字段匹配；
- handoff 中不得出现完整 API Key 示例。

## 5. Mock Adapter 是否符合要求

结论：**通过。**

- `BaseModelAdapter` 定义统一 `generate()` 接口；
- `MockWriterAdapter`、`MockCodeAdapter`、`MockReviewerAdapter` 输出风格区分明确；
- 未调用真实外部 API；
- 返回结构包含 `output_text`、`input_tokens`、`output_tokens`、`latency_ms`、`status`、`error_message`；
- 依赖较轻，没有引入不必要大型依赖。

## 6. 模型生成接口是否正确

结论：**不通过。**

已实现：

- `POST /api/tasks/{task_id}/generate`；
- 校验任务存在；
- 校验当前用户有项目权限；
- 校验分支属于当前任务；
- 校验提示词版本存在；
- 支持多个模型逐个调用；
- 非 Mock 模型通过 adapter 选择失败记录为 failed；
- 单个模型失败不会中断其他模型。

阻塞问题：

1. 成功生成时，`backend/app/services/invocation_service.py:174-210` 先插入 `task_outputs`，且 `invocation_id=None`，随后才插入 `ai_invocations`。后续没有回填 `task_outputs.invocation_id`。这违反 Stage-07 要求：“task_outputs.invocation_id 是否关联对应 ai_invocations”。

修复要求：

- 成功调用应先写入 `ai_invocations`，拿到 `invocation_id` 后再写入 `task_outputs`；
- 或者先写输出后必须在同一事务内回填 `task_outputs.invocation_id`，但推荐先插入 invocation；
- 返回的 `output_id` 对应记录必须能查到正确的 `invocation_id`。

## 7. ai_invocations、task_outputs、cost_records、operation_logs 是否正确写入

结论：**不通过。**

已实现：

- 成功/失败均会写 `ai_invocations`；
- 成功调用会写 `task_outputs`；
- 成功调用会写 `cost_records`；
- 生成操作会写 `operation_logs`；
- 写入动作处于同一事务上下文中。

阻塞问题：

1. 成功调用写入 `task_outputs` 时 `invocation_id` 为 `NULL`，导致输出版本无法关联调用记录。
2. 失败调用路径只写入 `ai_invocations`，没有写入 `cost_records`。Stage-07 要求每次调用都写入成本记录；失败调用可以记录 token 和成本为 0，但不能完全缺失成本记录。
3. 成本计算未检查 `price_unit`，当前默认按 `1K_TOKENS` 计算。课程版可只支持 `1K_TOKENS`，但应在代码中明确判断：非 `1K_TOKENS` 返回清晰错误或按约定处理，避免静默误算。

## 8. 调用日志列表和详情权限是否正确

结论：**基本通过。**

- `GET /api/invocations` admin 可查全部；
- 非 admin 使用项目成员子查询限制访问范围；
- 列表不返回完整 `input_text`、`output_text`；
- `GET /api/invocations/{invocation_id}` 会根据调用所属任务校验项目访问权限；
- 未发现返回 API Key 或加密字段。

建议：

- `get_invocation_detail()` 中变量名 `project_id = invocation["task_id"]` 可读性较差，虽然后续调用 `task_repo.get_task_by_id()` 实际上传入的是 task_id，但建议改名为 `task_id`，避免后续维护误改。

## 9. Repository 层和参数化 SQL 是否符合要求

结论：**部分通过。**

- 模型相关 SQL 集中在 `model_repo.py`；
- 调用相关 SQL 集中在 `invocation_repo.py`；
- 未发现用户输入直接拼接到 SQL；
- 动态 `where_clause` 由固定片段组成，参数仍通过 `%s` 绑定；
- 未使用 ORM。

必须修复：

- `list_models()` 带筛选时遗漏 `m.is_deleted = 0`。

## 10. 是否发现 API Key 泄露风险

结论：**发现轻度风险。**

代码层面未发现把真实明文 API Key 写入 operation_logs 或接口返回，但 handoff 测试示例中出现完整 `api_key` 字符串。即使是测试值，也建议按规范改成占位符或脱敏格式。

## 11. 是否发现越界实现

结论：**未发现。**

未发现 Stage-07 实现审核中心、成果库、统计看板或前端页面；未发现本阶段修改数据库结构或 Schema 冻结文档。

## 12. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/models.py app/routers/invocations.py app/services/model_service.py app/services/invocation_service.py app/repositories/model_repo.py app/repositories/invocation_repo.py app/adapters/base_adapter.py app/adapters/mock_writer_adapter.py app/adapters/mock_code_adapter.py app/adapters/mock_reviewer_adapter.py app/utils/crypto.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL，因此未执行真实数据库接口联调；
- 本轮结论基于静态代码审查和 Python 语法检查。

## 13. 是否允许进入 Stage-08

**不允许。**

必须先完成 `TASK-007-FIX-model-invocation-log.md`。

## 14. 必须修复的问题

1. 修复模型生成成功后 `task_outputs.invocation_id` 为 `NULL` 的问题，确保输出版本关联对应 `ai_invocations.invocation_id`。
2. 修复 AES-GCM 加密字段落库格式，`encrypted_api_key`、`key_iv`、`key_tag` 必须以 Base64 字符串形式存入 Schema 定义的文本字段。
3. 修复 `list_models()` 带筛选条件时遗漏 `m.is_deleted = 0` 的问题。
4. 失败调用也应写入 `cost_records`，token 和成本可为 0，但应与 `ai_invocations` 一一对应或在代码中有明确课程版约定。
5. 删除 handoff 中完整 API Key 示例，改为脱敏值或占位符。

