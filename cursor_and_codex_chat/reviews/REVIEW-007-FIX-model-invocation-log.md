# REVIEW-007-FIX 模型管理、Mock 调用、调用日志和成本记录修复复审报告

## 1. 审查结论

**不通过。**

本轮代码层面的 4 个阻塞问题已经修复，Python 语法检查通过，也未发现越界修改。但上轮第 5 个阻塞问题“完整 API Key 示例泄露”仍未彻底修复：`HANDOFF-007-FIX-model-invocation-log.md` 中仍保留了完整 key-like 示例字符串。

因此：**暂不允许进入 Stage-08**，本次不发布 `TASK-008-manual-edit-lock.md`。

## 2. 5 个阻塞问题是否全部修复

结论：**未全部修复，4 个已修复，1 个仍需修改。**

### 2.1 task_outputs.invocation_id 关联问题

结论：**已修复。**

依据：

- `backend/app/services/invocation_service.py:205-221` 成功生成时先写入 `ai_invocations` 并获取 `invocation_id`；
- `backend/app/services/invocation_service.py:223-235` 随后写入 `task_outputs`，并传入同一个 `invocation_id`；
- 成功路径随后写入 `cost_records`，并使用同一个 `invocation_id`；
- 失败路径只写 `ai_invocations` 和 `cost_records`，未写成功输出版本。

### 2.2 AES-GCM 字段 Base64 字符串问题

结论：**已修复。**

依据：

- `backend/app/utils/crypto.py:49-72` 中 `encrypt_api_key()` 返回 `encrypted_b64`、`iv_b64`、`tag_b64`；
- `backend/app/utils/crypto.py:75-92` 中 `decrypt_api_key()` 接受 Base64 字符串并解码后解密；
- `backend/app/repositories/model_repo.py` 中 `create_api_config()` 参数已改为字符串；
- 未发现硬编码主密钥，仍从 `API_KEY_SECRET` 读取。

### 2.3 ai_models 列表 is_deleted 过滤问题

结论：**已修复。**

依据：

- `backend/app/repositories/model_repo.py:164-183` 中 `base_where = "m.is_deleted = 0"`；
- `where_parts = [base_where] + filters`，无论是否有 `provider_id`、`status`、`keyword` 筛选，都会保留 `m.is_deleted = 0`；
- 联表 `model_providers` 时仍保留 `p.is_deleted = 0`；
- 查询参数仍使用 `%s` 参数化绑定。

### 2.4 失败调用 0 成本 cost_records 问题

结论：**已修复。**

依据：

- 模型不存在或未激活路径：`backend/app/services/invocation_service.py:109-139` 写入 failed invocation 后写入 0 成本 `cost_records`；
- 不支持的模型路径：`backend/app/services/invocation_service.py:151-183` 写入 failed invocation 后写入 0 成本 `cost_records`；
- Mock 返回 failed 路径：`backend/app/services/invocation_service.py:274-304` 写入 failed invocation 后写入 0 成本 `cost_records`；
- 成功路径仍写入实际 token 和成本。

### 2.5 完整 API Key 示例泄露问题

结论：**未修复彻底。**

问题：

- `cursor_and_codex_chat/handoff/HANDOFF-007-FIX-model-invocation-log.md:203-204` 仍出现完整 key-like 示例：
  - `"sk-test-123456"`
  - `"sk-test-abcdefgh1234"`

虽然该段是在描述“旧值改为占位符”，但本轮复审要求明确包含：“HANDOFF-007-FIX 是否没有完整 API Key 示例”。因此 handoff 文件中不应再出现完整 API Key 示例字符串。

修复建议：

- 将第 203-204 行改为不暴露完整示例的写法，例如：
  - `旧代码示例完整 key-like 字符串 → <YOUR_API_KEY>`
  - `旧 curl 示例完整 key-like 字符串 → <TEST_API_KEY>`
- 或改为：
  - `"sk-****3456" → "<YOUR_API_KEY>"`
  - `"sk-****1234" → "<TEST_API_KEY>"`

## 3. 是否发现新问题

未发现新的代码阻塞问题。

说明：

- 本轮重点仅复审上轮 5 个阻塞问题；
- 未进行 Stage-07 全量重新审查；
- 未连接 Windows MySQL 做真实接口联调。

## 4. 是否发现 API Key 泄露风险

**仍发现文档级 API Key 示例泄露风险。**

代码层面未发现完整 API Key 返回、日志输出或硬编码主密钥。但 handoff 中仍出现完整 key-like 示例，需清理。

## 5. 是否发现越界修改

未发现。

- 未发现本轮修改 `database/`；
- 未发现本轮修改 `frontend/`；
- 未发现本轮修改 `docs/01_数据库Schema冻结说明.md`；
- 未发现审核中心、成果库、统计看板或 Stage-08 人工编辑/乐观锁实现。

## 6. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/models.py app/routers/invocations.py app/services/model_service.py app/services/invocation_service.py app/repositories/model_repo.py app/repositories/invocation_repo.py app/adapters/base_adapter.py app/adapters/mock_writer_adapter.py app/adapters/mock_code_adapter.py app/adapters/mock_reviewer_adapter.py app/utils/crypto.py run.py
python3 -m py_compile app/services/task_service.py app/repositories/task_repo.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准，不因无法连接 MySQL 阻塞。

## 7. 是否允许进入 Stage-08

**不允许。**

请先清理 `HANDOFF-007-FIX-model-invocation-log.md` 中残留的完整 key-like 示例字符串。修复后可进行一次极小范围复审；无需改业务代码。

## 8. 必须修复的问题

唯一剩余问题：

1. `cursor_and_codex_chat/handoff/HANDOFF-007-FIX-model-invocation-log.md:203-204` 仍包含完整 API Key 示例字符串。请改为脱敏格式或占位符，确保 handoff 中不再出现完整 key-like 示例。

