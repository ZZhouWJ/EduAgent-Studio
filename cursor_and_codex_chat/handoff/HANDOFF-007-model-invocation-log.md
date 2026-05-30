# HANDOFF-007：Stage-07 模型管理、Mock 模型调用、调用日志和成本记录模块

## 任务状态

**完成** — Stage-07 模型管理与 Mock 调用模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/utils/crypto.py` | 新建 | AES-256-GCM 加密/解密/mask 工具 |
| `backend/app/adapters/base_adapter.py` | 新建 | BaseModelAdapter 抽象基类 + ModelResult 数据类 |
| `backend/app/adapters/mock_writer_adapter.py` | 新建 | Mock 中文写作模型适配器 |
| `backend/app/adapters/mock_code_adapter.py` | 新建 | Mock 代码/SQL 生成模型适配器 |
| `backend/app/adapters/mock_reviewer_adapter.py` | 新建 | Mock 审稿建议模型适配器 |
| `backend/app/adapters/__init__.py` | 新建 | 适配器统一导出 + `get_adapter_by_model_name()` |
| `backend/app/repositories/model_repo.py` | 新建 | 供应商/模型/API配置所有参数化 SQL |
| `backend/app/repositories/invocation_repo.py` | 新建 | 调用记录/输出/成本所有参数化 SQL |
| `backend/app/services/model_service.py` | 新建 | 模型管理业务逻辑 + 权限 |
| `backend/app/services/invocation_service.py` | 新建 | 调用生成业务逻辑 + 事务 |
| `backend/app/routers/models.py` | 新建 | 模型管理 API 路由 |
| `backend/app/routers/invocations.py` | 新建 | 调用日志 API 路由 |
| `backend/app/main.py` | 修改 | 注册 `models.router` + `invocations.router` |
| `backend/requirements.txt` | 修改 | 新增 `cryptography>=42.0.0` |
| `cursor_and_codex_chat/handoff/HANDOFF-007-model-invocation-log.md` | 新建 | 本交接报告 |

**说明**：`task_service.py` 和 `task_repo.py` 未修改。调用生成复用 `task_repo.get_task_by_id()`、`get_branch_by_id_and_task()` 查询任务信息，复用 `prompt_repo.get_version_by_id()` 查询提示词版本。

---

## 二、实现内容

### 2.1 API Key 加密

- **算法**：AES-256-GCM（`cryptography.hazmat.primitives.ciphers.aead.AESGCM`）
- **主密钥**：来自环境变量 `API_KEY_SECRET`，不硬编码
- **IV**：每次加密随机生成 12 字节
- **Tag**：GCM 认证标签 16 字节
- **key_version**：当前固定为 1
- **mask**：保留前 4 后 4 位，中间 `****`

```python
# 加密
encrypted_data, iv, tag, key_version = encrypt_api_key("sk-test-123456")
# 解密
plaintext = decrypt_api_key(encrypted_data, iv, tag)
# 掩码
mask_api_key("sk-test-123456")  # "sk-te****3456"
```

### 2.2 Mock Adapter

三个 Mock 适配器均继承 `BaseModelAdapter`，统一返回 `ModelResult`：

```python
@dataclass
class ModelResult:
    output_text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    status: str           # success / failed / timeout
    error_message: str   # nullable
```

| 适配器 | 模型名 | 输出风格 |
|---|---|---|
| `MockWriterAdapter` | `mock-writer` | 中文报告/申报书结构化输出 |
| `MockCodeAdapter` | `mock-code` | Python / SQL 代码示例 |
| `MockReviewerAdapter` | `mock-reviewer` | 审稿意见表格化输出 |

适配器通过 `get_adapter_by_model_name(model_name)` 根据模型名称选择。

### 2.3 模型生成事务

`generate_task_outputs()` 在一个 `get_db_transaction()` 内完成：

1. 遍历每个 `model_id`
2. 校验模型存在且 active
3. 调用 Mock Adapter（失败也记录）
4. 成功时：`SELECT ... FOR UPDATE` + `INSERT task_outputs`
5. 成功时：`INSERT ai_invocations`
6. 成功时：`INSERT cost_records`
7. 写 `operation_logs`
8. `conn.commit()`

单个模型失败不影响其他模型，互不干扰。

### 2.4 Repository 层 SQL

**model_repo.py**：供应商查询/创建、模型列表/创建、API配置列表/创建（不返回加密字段）

**invocation_repo.py**：调用记录查询/创建、输出创建（FOR UPDATE版本号）、成本记录创建

---

## 三、数据库是否变化

**否**。本阶段未修改 `database/` 目录，未修改表结构。

涉及数据表：

| 表 | 操作 |
|---|---|
| `model_providers` | SELECT / INSERT |
| `ai_models` | SELECT / INSERT |
| `api_configs` | SELECT / INSERT（加密字段）|
| `ai_invocations` | INSERT |
| `task_outputs` | INSERT |
| `cost_records` | INSERT |
| `operation_logs` | INSERT |
| `project_tasks` | SELECT（权限校验）|
| `task_branches` | SELECT（权限校验）|
| `prompt_versions` | SELECT（获取提示词内容）|

---

## 四、新增接口列表

```
模型供应商：
GET    /api/model-providers
POST   /api/model-providers

AI 模型：
GET    /api/ai-models
POST   /api/ai-models

API 配置：
GET    /api/api-configs
POST   /api/api-configs

调用生成：
POST   /api/tasks/{task_id}/generate

调用日志：
GET    /api/invocations
GET    /api/invocations/{invocation_id}
```

---

## 五、API Key 加密实现说明

详见上文"二、实现内容 - 2.1 API Key 加密"。

**环境变量设置**：

```bash
# 生成随机密钥
python -c "from app.utils.crypto import generate_random_secret; print(generate_random_secret(32))"
# 将结果写入 .env
echo "API_KEY_SECRET=<生成的密钥>" >> backend/.env
```

**安全性保证**：
- 加密主密钥不硬编码
- 明文 key 不写入日志
- operation_logs 写入时只记录 `key_mask`
- 数据库只存 `encrypted_api_key + key_iv + key_tag`，不存明文

---

## 六、Mock Adapter 实现说明

详见上文"二、实现内容 - 2.2 Mock Adapter"。

- 不访问外网
- 输出稳定可复现（基于模板）
- Token 估算：中文 0.5/字，英文 0.75/词，其他 0.25/字
- latency 模拟真实感（`time.time()` 计算）

---

## 七、模型生成事务说明

详见上文"二、实现内容 - 2.3 模型生成事务"。

所有数据库写操作在同一事务内，异常时统一 rollback。

---

## 八、ai_invocations 写入说明

每个模型调用（无论成功/失败）都写入 `ai_invocations`：

| 场景 | status | output_text | error_message |
|---|---|---|---|
| 成功 | `success` | 模型输出 | NULL |
| 模型不存在/未激活 | `failed` | NULL | 错误信息 |
| 适配器不支持 | `failed` | NULL | 错误信息 |
| Mock 调用失败 | `failed` | NULL | ModelResult.error_message |

---

## 九、task_outputs 写入说明

仅成功调用时写入 `task_outputs`：

```sql
INSERT INTO task_outputs
  (task_id, branch_id, invocation_id, version_no, output_title, content,
   source_type, parent_output_id,
   lock_version, last_modified_at, last_modified_by,
   is_final_candidate, status, is_deleted, created_at, created_by)
VALUES
  (..., 'ai_generated', NULL, 0, NOW(), user_id, 0, 'draft', 0, NOW(), user_id)
```

- `version_no` 在事务内通过 `SELECT ... FOR UPDATE` 生成
- `invocation_id` 关联对应 `ai_invocations`

---

## 十、cost_records 写入说明

```python
input_cost  = input_tokens / 1000.0 * model.input_price
output_cost = output_tokens / 1000.0 * model.output_price
total_cost  = input_cost + output_cost
```

- `price_unit` 固定为 `1K_TOKENS`
- `currency` 固定为 `CNY`
- 价格来自 `ai_models.input_price / output_price` 字段，不硬编码

---

## 十一、operation_logs 写入说明

- **模型生成**：`action_type=task:generate`，记录 `task_id` 和 `model_ids`
- 所有 `operation_logs` 通过 `insert_operation_log_with_conn()` 与业务操作在同一事务内写入

---

## 十二、调用日志权限规则

| 角色 | 列表 | 详情 |
|---|---|---|
| admin | 查看全部 | 查看全部 |
| 项目成员 | 只能查看自己参与项目的记录 | 只能查看自己参与项目的记录 |
| 非成员 | 无权查看 | 无权查看 |

权限判断通过 `list_invocations()` 中的子查询限制：

```sql
i.task_id IN (
    SELECT task_id FROM project_tasks pt
    INNER JOIN project_members pm ON pt.project_id = pm.project_id
    WHERE pm.user_id = %s AND pm.is_deleted = 0 AND pt.is_deleted = 0
)
```

---

## 十三、成本计算公式

```
total_tokens = input_tokens + output_tokens
input_cost  = (input_tokens  / 1000.0) * input_price
output_cost = (output_tokens / 1000.0) * output_price
total_cost  = input_cost + output_cost
currency    = "CNY"
```

---

## 十四、模型生成测试方法

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 假设 task_id=1, branch_id=1, model_ids=[1]
curl -X POST "http://127.0.0.1:8000/api/tasks/1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "model_ids": [1],
    "branch_id": 1,
    "input_text": "请为数据库课程报告生成需求分析部分"
  }'
```

期望：返回 `ai_invocations` 记录列表，包含 `output_id`。

---

## 十五、调用日志测试方法

```bash
# 列表
curl "http://127.0.0.1:8000/api/invocations?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# 详情
curl "http://127.0.0.1:8000/api/invocations/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十六、API 配置安全测试方法

```bash
# 查看配置（只能 admin 查看）
curl "http://127.0.0.1:8000/api/api-configs" \
  -H "Authorization: Bearer $TOKEN"
# 期望：返回 key_mask 如 "sk-te****3456"，不返回 encrypted_api_key 或明文

# 创建配置（API Key 加密存储）
curl -X POST "http://127.0.0.1:8000/api/api-configs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"provider_id":1,"config_name":"测试配置","api_key":"sk-test-abcdefgh1234","quota_limit":100000}'
# 期望：返回 api_config_id 和 key_mask
```

---

## 十七、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查
2. **cryptography 未安装**：运行时需要 `pip install cryptography`，已在 `requirements.txt` 中声明
3. **环境变量依赖**：`API_KEY_SECRET` 必须设置，否则加密/解密会抛出 `RuntimeError`
4. **API 配置解密未暴露接口**：当前未实现"查看已加密 API Key 明文"的接口（安全考量）

---

## 十八、是否实现审核中心

**否**。

---

## 十九、是否实现成果库

**否**。

---

## 二十、是否实现前端页面

**否**。

---

## 二十一、需要 Codex 审查的重点

1. **事务一致性**：`generate_task_outputs` 在一个 `get_db_transaction()` 内完成所有写操作
2. **SQL 集中**：所有 SQL 在 `model_repo.py` 和 `invocation_repo.py` 中，service 层无内联 SQL
3. **API Key 安全**：明文 key 不写入数据库、不写入日志、operation_logs 只写 `key_mask`
4. **Mock 适配器选择**：`get_adapter_by_model_name` 正确根据模型名路由
5. **成本计算**：使用 `ai_models` 表的 `input_price / output_price` 动态计算，不硬编码
6. **affected_rows**：所有写操作使用 `conn.cursor()` + 正确 `finally` 关闭
7. **权限校验**：非项目成员无法调用生成、无法查看调用日志
8. **无越界**：确认未实现审核中心、成果库、前端页面

---

## 二十二、验收清单

- [x] 模型供应商列表/创建接口
- [x] AI 模型列表/创建接口
- [x] API 配置列表/创建接口（API Key 加密）
- [x] AES-GCM 加密工具（主密钥来自环境变量）
- [x] MockWriterAdapter / MockCodeAdapter / MockReviewerAdapter
- [x] 任务模型生成接口（批量模型调用）
- [x] ai_invocations 写入（成功/失败均记录）
- [x] task_outputs 写入（仅成功，FOR UPDATE 版本号）
- [x] cost_records 写入（动态价格计算）
- [x] operation_logs 写入
- [x] 调用日志列表/详情接口
- [x] 所有 SQL 参数化
- [x] 所有写操作事务统一
- [x] 未修改 `database/*`、`frontend/*`
- [x] 未实现审核中心、成果库、前端页面
- [x] Python 语法检查通过

---

**本阶段完成后停止，不进入 Stage-08。**
