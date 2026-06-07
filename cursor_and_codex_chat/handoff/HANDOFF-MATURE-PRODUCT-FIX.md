# 成熟产品化修复报告

> 修复时间：2026-06-03
> 依据：cursor_and_codex_chat/reviews/REVIEW-MATURE-PRODUCT-COMPLETE.md
> 状态：已全部完成

---

## Codex 未通过原因

8 个前后端契约阻塞问题：
1. `/register` 未加入路由守卫白名单
2. 注册接口缺服务端 `confirm_password` 校验
3. 修改密码接口 `get_user_by_id()` 取不到 `password_hash`
4. 注册流程 `users/user_roles/operation_logs` 非同事务
5. 提示词搜索传 `search` 而后端接收 `keyword`
6. 成本统计前端字段结构与后端返回不匹配
7. 调用审计前端传 `start_date/end_date` 后端不支持
8. 登录日志前端用 `fail_reason` 后端返回 `failure_reason`

---

## 修复文件总览

| # | 修复项 | 后端文件 | 前端文件 | 其他文件 |
|---|--------|---------|---------|---------|
| 1 | 注册页路由守卫白名单 | — | `src/router/guard.ts` | — |
| 2 | confirm_password 服务端校验 | `app/routers/auth.py`、`app/services/auth_service.py` | `src/api/auth.ts`、`src/pages/register/index.vue` | — |
| 3 | 修改密码 password_hash | `app/services/auth_service.py`、`app/repositories/user_repo.py` | — | — |
| 4 | 注册流程同事务 | `app/services/auth_service.py`、`app/repositories/user_repo.py` | — | — |
| 5 | 提示词搜索 keyword | — | `src/api/prompts.ts`、`src/pages/prompts/index.vue` | `backend/scripts/route_list.md`、`frontend/scripts/route_list.md` |
| 6 | 成本统计字段 | `app/repositories/statistics_repo.py` | `src/api/costs.ts`、`src/pages/costs/index.vue` | `backend/scripts/route_list.md`、`frontend/scripts/route_list.md` |
| 7 | 调用审计日期筛选移除 | — | `src/pages/invocations/index.vue`、`src/api/invocations.ts` | `backend/scripts/route_list.md`、`frontend/scripts/route_list.md` |
| 8 | failure_reason 字段 | — | `src/pages/logs/login.vue`、`src/api/logs.ts` | `backend/scripts/route_list.md`、`frontend/scripts/route_list.md` |

---

## 修复详情

### 1. /register 路由守卫白名单

**文件**: `frontend/src/router/guard.ts`

```diff
- const whiteList = ["/login"]
+ const whiteList = ["/login", "/register"]
```

未登录用户现在可以访问 `/register`；已登录用户访问 `/register` 时，因为 token 存在，路由守卫会跳过重定向逻辑直接放行。

---

### 2. confirm_password 服务端校验

#### 后端 `backend/app/routers/auth.py`

- `RegisterRequest` 新增 `confirm_password: str` 字段
- 注册接口调用 service 时传入 `confirm_password`

#### 后端 `backend/app/services/auth_service.py`

- `register()` 函数新增 `confirm_password` 参数
- 在所有参数校验之前，先判断 `password != confirm_password`，抛出 `ValidationException("两次输入的密码不一致")`
- `confirm_password` 不入库，不返回前端

#### 前端 `frontend/src/api/auth.ts`

- `RegisterParams` 接口新增 `confirm_password: string` 字段

#### 前端 `frontend/src/pages/register/index.vue`

- `handleRegister` 调用 `authApi.register` 时传入 `confirm_password: registerForm.value.confirm_password`

---

### 3. 修改密码 password_hash 获取

**文件**: `backend/app/services/auth_service.py`、`backend/app/repositories/user_repo.py`

`get_user_by_id()` 不返回 `password_hash`，无法做旧密码校验。新增：

```python
def get_user_by_id_with_password(user_id: int) -> Optional[Dict[str, Any]]:
    """按 user_id 查询（含 password_hash，用于密码校验）"""
    sql = """
        SELECT user_id, username, password_hash, real_name, student_no,
               email, phone, status, last_login_at,
               created_at, created_by, updated_at, updated_by
        FROM users
        WHERE user_id = %s AND is_deleted = 0
    """
```

`update_password()` 改用此函数：

```python
user_record = user_repo.get_user_by_id_with_password(user_id)
if not verify_password(old_password, user_record["password_hash"]):
    raise ValidationException(message="旧密码错误")
```

`/api/auth/me` 和用户列表接口不受影响，仍使用不返回 `password_hash` 的 `get_user_by_id()`。

---

### 4. 注册流程同事务

**文件**: `backend/app/repositories/user_repo.py`

新增两个带 `conn` 参数的函数：
- `create_user_with_conn(conn, ...)` — 在外部事务连接中创建用户
- `assign_default_role_with_conn(conn, user_id)` — 在外部事务连接中分配角色

`insert_operation_log_with_conn` 已存在，无需修改。

**文件**: `backend/app/services/auth_service.py`

```python
from app.database import get_db_transaction
with get_db_transaction() as conn:
    user_id = user_repo.create_user_with_conn(conn=conn, ...)
    user_repo.assign_default_role_with_conn(conn=conn, user_id=user_id)
    user_repo.insert_operation_log_with_conn(conn=conn, ...)
```

事务失败时 `get_db_transaction()` 上下文管理器自动 rollback，不会出现用户创建成功但角色未分配的情况。

---

### 5. 提示词搜索 keyword 参数

**后端**: `GET /api/prompt-templates` 接收 `keyword`、`task_type_id`，**不支持** `search` 和 `is_active`。

**修复**:

- `frontend/src/api/prompts.ts` — `getTemplates` 参数改为 `keyword?: string`，移除 `is_active` 和 `search`
- `frontend/src/pages/prompts/index.vue` — 调用时传入 `keyword` 而非 `search`；移除 `selectedIsActive` 变量和相关筛选下拉框（状态列在表格中仍正常展示）

> 注：`is_active` 在类型定义中存在，因为 `PromptTemplate` 返回类型和 `UpdateTemplateBody` 更新请求都需要它，但列表查询不再传此参数。

---

### 6. 成本统计字段适配

**后端 `GET /api/statistics/costs` 真实返回**：

```json
{
  "total_cost": 0.0,
  "input_cost": 0.0,
  "output_cost": 0.0,
  "total_tokens": 0,
  "currency": "CNY",
  "cost_by_model": [...],
  "cost_by_project": [...],
  "cost_by_user": [...]
}
```

**修复**:

- `backend/app/repositories/statistics_repo.py` — `by_model` SQL 新增 `provider_name`（JOIN `model_providers`）、`call_count`、`input_cost`、`output_cost`、`input_tokens`、`output_tokens`；`by_project` SQL 新增 `call_count`、`avg_cost_per_call`
- `frontend/src/api/costs.ts` — 类型改为 `cost_by_model`/`cost_by_project`，移除嵌套的 `summary`
- `frontend/src/pages/costs/index.vue` — 摘要卡片直接取 `data.total_cost`、`data.input_cost` 等；表格改为 `data.cost_by_model` 和 `data.cost_by_project`

---

### 7. 调用审计日期筛选处理

**后端**: `GET /api/invocations` 支持 `project_id`、`task_id`、`model_id`、`status`、`page`、`page_size`，**不支持** `start_date/end_date`。

**修复**:

- `frontend/src/pages/invocations/index.vue` — 移除 `startDate`、`endDate` 变量及相关日期选择器 UI、`clearFilters()` 日期重置逻辑
- `frontend/src/api/invocations.ts` — `getInvocations` 参数移除 `start_date` 和 `end_date`

如需按日期过滤，可通过审核中心或操作日志页面（支持 `created_at` 日期筛选）实现。

---

### 8. failure_reason 字段

**后端返回**: 数据库表 `login_logs` 列为 `failure_reason`，`list_login_logs` 查询返回该字段。

**修复**:

- `frontend/src/pages/logs/login.vue` — 改为读取 `row.failure_reason`
- `frontend/src/api/logs.ts` — `LoginLog` 接口字段从 `fail_reason` 改为 `failure_reason`

---

## 文档同步

以下文档已同步更新：

| 文档 | 同步内容 |
|------|---------|
| `backend/scripts/route_list.md` | 注册接口说明补充 confirm_password 和事务；调用审计注明不支持日期筛选 |
| `frontend/scripts/route_list.md` | 注册页说明补充 confirm_password；提示词搜索注明 keyword 参数；调用审计注明不支持日期筛选、移除参数；成本统计注明返回字段；登录日志注明 failure_reason |
| `docs/最终检查清单.md` | 修正"禁止注册"为"支持注册"；路由数 13→19；新增通过标准条目 |
| `docs/系统测试与结果分析素材.md` | TC-036 成本统计预期结果补充 cost_by_model/cost_by_project；版本升至 v1.1 |

---

## 是否修改数据库结构

**否**。未修改 `database/*` 和 `docs/01_数据库Schema冻结说明.md`。

---

## 是否引入真实密钥

**否**。所有密钥均为占位符，未引入真实 API Key 或数据库密码。

---

## 检查结果

### 后端语法检查

```bash
python -m py_compile app/routers/auth.py          # ✅ EXIT:0
python -m py_compile app/services/auth_service.py # ✅ EXIT:0
python -m py_compile app/repositories/user_repo.py        # ✅ EXIT:0
python -m py_compile app/repositories/statistics_repo.py # ✅ EXIT:0
python -m py_compile app/main.py                 # ✅ EXIT:0
python -m py_compile run.py                      # ✅ EXIT:0
```

### 前端构建

```bash
cd ../frontend && npm run build
```

✅ **构建成功**（4.66s，1577 modules，0 errors）

---

## 需要 Codex 复审的重点

1. **注册事务**：`get_db_transaction()` 的 rollback 是否在所有异常路径正确触发？
2. **修改密码**：`get_user_by_id_with_password` 与 `get_user_by_id` 的区别是否清晰、不会误用？
3. **成本统计 SQL**：`by_project` 的 `avg_cost_per_call` 是前端计算的，后端返回的 `call_count` 和 `total_cost` 是否正确聚合？
4. **文档一致性**：route_list 中对接口参数的描述是否与代码完全一致？

---

## 注意事项

1. **注册事务**：`get_db_transaction()` 使用 `autocommit=False` 连接，异常时自动 rollback。
2. **成本统计**：后端 `by_model` 包含 `input_cost/output_cost/input_tokens/output_tokens/call_count/provider_name`，前端表格已对应展示。
3. **调用审计日期筛选**：如需此功能，可在后续迭代中在后端 `invocations` 路由新增日期参数（`created_at` 字段）。
4. **回归检查**：全文搜索 `fail_reason` 仅剩 handoff 文档历史引用（修复前代码），生产代码中已全部修正为 `failure_reason`；`password_hash` 未在前端展示；无真实密钥泄露；无 Mock 数据冒充真实数据。
