# HANDOFF-007-FIX：Stage-07 模型管理模块修复版

## 任务状态

**完成** — Stage-07 修复问题均已处理。

---

## 一、Codex 未通过原因

| # | 问题 | 严重程度 |
|---|---|---|
| 1 | 成功生成时 `task_outputs.invocation_id` 为 `NULL`，未关联对应 `ai_invocations` | 阻塞 |
| 2 | AES-GCM 加密结果 `bytes` 直接写入 TEXT/VARCHAR 字段 | 阻塞 |
| 3 | `list_models()` 带筛选条件时遗漏 `m.is_deleted = 0` | 阻塞 |
| 4 | 失败调用未写 `cost_records` | 阻塞 |
| 5 | handoff 中出现完整 API Key 示例 | 阻塞 |

---

## 二、本次修复的问题列表

1. `invocation_service.generate_task_outputs()`：先插入 `ai_invocations` 获取 `invocation_id`，再插入 `task_outputs` 关联该 ID
2. `crypto.py`：`encrypt_api_key` / `decrypt_api_key` 所有返回值改为 Base64 字符串
3. `model_repo.list_models()`：`where_parts` 始终以 `m.is_deleted = 0` 为基础条件
4. `invocation_service.generate_task_outputs()`：所有失败路径（模型不存在/未激活/不支持/返回 failed）均调用 `create_cost_record`（成本为 0）
5. handoff 中完整 API Key 示例改为占位符 `<YOUR_API_KEY>` / `<TEST_API_KEY>`

---

## 三、本次修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/utils/crypto.py` | 返回类型从 `bytes` 改为 Base64 字符串；新增 `import base64` |
| `backend/app/repositories/model_repo.py` | `list_models()` 始终包含 `m.is_deleted = 0`；`create_api_config()` 参数类型从 `bytes` 改为 `str` |
| `backend/app/services/invocation_service.py` | 成功路径先插 `ai_invocations` 再插 `task_outputs`；所有失败路径均写 `cost_records`；修复 `_invocation_row_to_dict` 参数注解语法；`get_invocation_detail` 变量名清理 |
| `cursor_and_codex_chat/handoff/HANDOFF-007-model-invocation-log.md` | 移除完整 API Key 示例，改为占位符 |

**说明**：未修改 `database/*`、`frontend/*`、`docs/*`，未修改 Stage-07 允许范围之外的文件。

---

## 四、task_outputs.invocation_id 如何修复

**修改前**（错误）：

```python
# 先插 task_outputs（invocation_id=None）
output_id = invocation_repo.create_task_output(
    task_id=task_id,
    invocation_id=None,   # ← 错误
    ...
)
# 后插 ai_invocations
invocation_id = invocation_repo.create_invocation(...)
```

**修改后**（正确）：

```python
# 1. 先插 ai_invocations，获取 invocation_id
invocation_id = invocation_repo.create_invocation(
    project_id=project_id,
    task_id=task_id,
    ...
    conn=conn,
)

# 2. 再插 task_outputs，关联 invocation_id
output_id = invocation_repo.create_task_output(
    task_id=task_id,
    invocation_id=invocation_id,   # ← 正确
    ...
    conn=conn,
)

# 3. 写成本记录
invocation_repo.create_cost_record(
    invocation_id=invocation_id,
    ...
    conn=conn,
)
```

所有三个记录（`ai_invocations`、`task_outputs`、`cost_records`）在同一事务内，`invocation_id` 一致关联。

---

## 五、ai_invocations 与 task_outputs 如何关联

```
ai_invocations.invocation_id (= N)
    ↓ 关联
task_outputs.invocation_id (= N)
    ↓ 关联
cost_records.invocation_id (= N)
```

返回结果中每个成功的模型调用包含：
- `invocation_id`: 对应 ai_invocations 记录
- `output_id`: 对应 task_outputs 记录
- 两者的 `invocation_id` 字段相同，可通过查询验证

---

## 六、AES-GCM 加密字段如何改为 Base64 字符串

**修改前**（bytes，直接写入 TEXT）：

```python
# crypto.py
return encrypted_data, iv, tag, _KEY_VERSION  # bytes
```

**修改后**（Base64 字符串）：

```python
# crypto.py
import base64

def encrypt_api_key(plaintext: str) -> Tuple[str, str, str, int]:
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    encrypted_b64 = base64.b64encode(ciphertext).decode("utf-8")
    iv_b64 = base64.b64encode(iv).decode("utf-8")
    tag_b64 = base64.b64encode(tag).decode("utf-8")
    return encrypted_b64, iv_b64, tag_b64, _KEY_VERSION

def decrypt_api_key(encrypted_base64, iv_base64, tag_base64) -> str:
    ciphertext = base64.b64decode(encrypted_base64)
    iv = base64.b64decode(iv_base64)
    tag = base64.b64decode(tag_base64)
    ...
```

`model_repo.create_api_config()` 参数类型从 `bytes` 改为 `str`，直接写入 TEXT/VARCHAR 字段。

---

## 七、ai_models 列表 m.is_deleted = 0 如何保证不丢失

**修改前**（带筛选时丢失）：

```python
base_where = "m.is_deleted = 0"
filters = []
# ... append conditions ...
where_clause = " AND ".join(filters) if filters else base_where
# 问题：filters 非空时，base_where 被丢弃
```

**修改后**（始终保留）：

```python
base_where = "m.is_deleted = 0"
filters = []
# ... append conditions ...
where_parts = [base_where] + filters  # ← base_where 始终在第一项
where_clause = " AND ".join(where_parts)
# 无论是否有筛选条件，WHERE 始终以 m.is_deleted = 0 开头
```

生成的 WHERE 子句：
- 无筛选：`m.is_deleted = 0`
- 有 provider_id 筛选：`m.is_deleted = 0 AND m.provider_id = %s`
- 有 status 筛选：`m.is_deleted = 0 AND m.status = %s`
- 有 keyword 筛选：`m.is_deleted = 0 AND (m.model_name LIKE %s OR m.display_name LIKE %s)`

---

## 八、失败调用 0 成本 cost_records 如何写入

所有失败路径（3 种）均调用 `create_cost_record`：

```python
# 1. 模型不存在或未激活
invocation_id = create_invocation(..., status="failed", ...)
create_cost_record(
    invocation_id=invocation_id,
    input_tokens=0, output_tokens=0, total_tokens=0,
    input_cost=0.0, output_cost=0.0, total_cost=0.0,
    currency="CNY", conn=conn,
)

# 2. 不支持的模型
invocation_id = create_invocation(..., status="failed", ...)
create_cost_record(...)  # 同样写 0 成本

# 3. Mock 调用返回 failed
invocation_id = create_invocation(..., status="failed", ...)
create_cost_record(...)  # 同样写 0 成本
```

每条 `ai_invocations` 记录均有对应的 `cost_records` 记录，通过 `invocation_id` 一一对应。

---

## 九、是否清理完整 API Key 示例

**是**。已修复两处（均在 HANDOFF-007 原文档中）：

1. 代码示例：完整 Key → `"<YOUR_API_KEY>"`
2. curl 示例：完整 Key → `"<TEST_API_KEY>"`

**本次（FIX）文档已清理所有 key-like 字符串，仅保留脱敏形式或占位符。**

`operation_logs` 写入时使用 `key_mask`（如 `"sk-te****3456"`），不出现完整 Key。

---

## 十、是否修改数据库结构

**否**。

---

## 十一、是否修改 frontend

**否**。

---

## 十二、是否实现审核中心

**否**。

---

## 十三、是否实现成果库

**否**。

---

## 十四、是否实现统计看板

**否**。

---

## 十五、Python 语法检查命令

```bash
cd backend
python -m py_compile app/utils/crypto.py app/repositories/model_repo.py app/services/invocation_service.py app/services/model_service.py app/main.py
```

结果：`EXIT:0`（通过）。

---

## 十六、当前环境限制

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查
2. **cryptography 需安装**：`pip install cryptography` 已在 `requirements.txt` 中声明
3. **API_KEY_SECRET 环境变量**：`crypto.py` 运行时需要设置该环境变量

---

## 十七、需要 Codex 复审的重点

1. **invocation_id 关联顺序**：确认成功路径中先插 `ai_invocations` 再插 `task_outputs`，`task_outputs.invocation_id` 不为 NULL
2. **失败也写 cost_records**：确认所有失败路径（3 种）都调用 `create_cost_record`
3. **Base64 编码**：确认 `encrypt_api_key` / `decrypt_api_key` 返回/接受 Base64 字符串
4. **is_deleted 不丢失**：确认无论 `list_models` 是否有筛选条件，`m.is_deleted = 0` 始终在 WHERE 子句中
5. **API Key 脱敏**：确认 handoff 中无完整 API Key
6. **事务一致性**：确认 `ai_invocations`、`task_outputs`、`cost_records`、`operation_logs` 在同一事务内
7. **无越界**：确认未实现审核中心、成果库、统计看板、前端页面

---

## 十八、验收清单

- [x] 成功生成的 `task_outputs.invocation_id` 关联正确的 `ai_invocations.invocation_id`
- [x] AES-GCM 加密结果均为 Base64 字符串
- [x] `list_models` 无论筛选条件如何均保留 `m.is_deleted = 0`
- [x] 所有失败路径均写 `cost_records`（成本为 0）
- [x] handoff 中无完整 API Key 示例
- [x] 所有 Python 语法检查通过
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`

---

**本修复完成后停止，等待 Codex 复审。**
