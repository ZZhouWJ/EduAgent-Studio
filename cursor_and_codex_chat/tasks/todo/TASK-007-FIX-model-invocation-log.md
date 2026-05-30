# TASK-007-FIX 模型管理、Mock 调用、调用日志和成本记录修复任务

## 任务状态

已完成。

## 任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-007-model-invocation-log.md` 修复 Stage-07 审查发现的阻塞问题。修复完成后提交 handoff，等待 Codex 复审。复审通过前不得进入 Stage-08。

## 允许修改文件

- `backend/app/services/invocation_service.py`
- `backend/app/repositories/invocation_repo.py`
- `backend/app/repositories/model_repo.py`
- `backend/app/services/model_service.py`
- `backend/app/utils/crypto.py`
- `cursor_and_codex_chat/handoff/HANDOFF-007-FIX-model-invocation-log.md`

如确实需要调整路由请求/返回说明，可少量修改：

- `backend/app/routers/models.py`
- `backend/app/routers/invocations.py`

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 审核中心；
2. 成果库；
3. 统计看板；
4. 前端页面；
5. Stage-08 人工编辑与乐观锁内容。

## 必须修复的问题

### 1. 修复 task_outputs.invocation_id 为空

当前成功生成路径中先插入 `task_outputs`，且传入 `invocation_id=None`，后续没有回填。

修复要求：

1. 成功调用应先写入 `ai_invocations`，拿到 `invocation_id`；
2. 再写入 `task_outputs`，传入该 `invocation_id`；
3. `task_outputs.invocation_id` 必须关联对应 `ai_invocations.invocation_id`；
4. `ai_invocations`、`task_outputs`、`cost_records`、`operation_logs` 必须仍在同一事务内；
5. 返回结果中的 `invocation_id` 与 `output_id` 必须对应同一次生成。

### 2. 修复 API Key 加密字段落库格式

当前 `encrypt_api_key()` 返回 bytes，并直接写入 `api_configs.encrypted_api_key`、`key_iv`、`key_tag`。Schema 中这些字段是 `TEXT` / `VARCHAR(64)`，并要求 IV / Tag 使用 Base64 文本。

修复要求：

1. `encrypted_api_key`、`key_iv`、`key_tag` 入库前必须 Base64 编码为字符串；
2. `decrypt_api_key()` 应接受 Base64 字符串并解码后再解密；
3. `model_repo.create_api_config()` 参数类型应改为字符串；
4. 不得保存明文 API Key；
5. 不得修改数据库结构。

### 3. 修复 AI 模型列表软删除过滤

当前 `model_repo.list_models()` 在传入 `provider_id`、`status` 或 `keyword` 时遗漏 `m.is_deleted = 0`。

修复要求：

1. `filters` 应默认包含 `m.is_deleted = 0`；
2. `count_sql` 和 `data_sql` 都必须过滤软删除模型；
3. 联表 `model_providers` 时继续过滤 `p.is_deleted = 0`。

### 4. 失败调用补写成本记录

当前模型不存在、模型未激活、非 Mock 模型或 adapter 返回失败时，只写入 `ai_invocations`，没有写入 `cost_records`。

修复要求：

1. 每次模型调用都应写入 `cost_records`；
2. 失败调用可写入 `input_tokens=0`、`output_tokens=0`、`total_tokens=0`、`input_cost=0`、`output_cost=0`、`total_cost=0`；
3. 成本记录应关联对应失败调用的 `invocation_id`；
4. 多模型调用中单个失败仍不得影响其他模型。

### 5. 清理 handoff 中完整 API Key 示例

当前 handoff 示例中包含完整 `api_key` 字符串。

修复要求：

1. handoff 中不得出现完整 API Key；
2. 示例应改为 `<TEST_API_KEY>`、`sk-test-****1234` 或其他脱敏形式；
3. operation_logs、错误信息、返回体中也不得出现完整 API Key。

## 复审要求

修复完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-007-FIX-model-invocation-log.md`

handoff 必须说明：

1. 5 个阻塞问题分别如何修复；
2. 是否修改了允许范围之外的文件；
3. 是否仍未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
4. 是否执行 Python 语法检查；
5. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/models.py app/routers/invocations.py app/services/model_service.py app/services/invocation_service.py app/repositories/model_repo.py app/repositories/invocation_repo.py app/adapters/base_adapter.py app/adapters/mock_writer_adapter.py app/adapters/mock_code_adapter.py app/adapters/mock_reviewer_adapter.py app/utils/crypto.py run.py
```

