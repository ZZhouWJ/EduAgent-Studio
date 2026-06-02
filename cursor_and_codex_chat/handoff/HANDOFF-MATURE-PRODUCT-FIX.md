# 成熟产品化修复报告

> 修复时间：2026-06-03
> 依据：cursor_and_codex_chat/reviews/REVIEW-MATURE-PRODUCT-COMPLETE.md

---

## 修复结果总览

| # | 问题 | 修复状态 | 涉及文件 |
|---|------|---------|---------|
| 1 | 注册页未加入路由守卫白名单 | ✅ 已修复 | `frontend/src/router/guard.ts` |
| 2 | 注册接口前后端缺 confirm_password，后端未校验 | ✅ 已修复 | `backend/app/routers/auth.py`、`backend/app/services/auth_service.py`、`frontend/src/api/auth.ts`、`frontend/src/pages/register/index.vue` |
| 3 | 修改密码接口未用 password_hash 校验旧密码 | ✅ 已修复 | `backend/app/services/auth_service.py`、`backend/app/repositories/user_repo.py` |
| 4 | 注册流程 users/user_roles/operation_logs 未在同一事务 | ✅ 已修复 | `backend/app/services/auth_service.py`、`backend/app/repositories/user_repo.py` |
| 5 | 提示词列表搜索参数和 is_active 筛选与后端不符 | ✅ 已修复 | `frontend/src/api/prompts.ts`、`frontend/src/pages/prompts/index.vue` |
| 6 | 成本统计页面字段与后端不匹配 | ✅ 已修复 | `frontend/src/api/costs.ts`、`frontend/src/pages/costs/index.vue`、`backend/app/repositories/statistics_repo.py` |
| 7 | 调用审计日期筛选后端不支持 | ✅ 已移除 | `frontend/src/pages/invocations/index.vue`、`frontend/src/api/invocations.ts` |
| 8 | 登录日志失败原因字段名错误 | ✅ 已修复 | `frontend/src/pages/logs/login.vue` |

---

## 修复详情

### 问题 1：注册页未加入路由守卫白名单

**文件**: `frontend/src/router/guard.ts`

```diff
- const whiteList = ["/login"]
+ const whiteList = ["/login", "/register"]
```

未登录用户现在可以访问 `/register` 而不会被重定向到登录页。

---

### 问题 2：注册接口前后端缺 confirm_password，后端未校验

#### 后端路由 `backend/app/routers/auth.py`

- `RegisterRequest` 新增 `confirm_password: str` 字段
- 注册接口调用 service 时传入 `confirm_password`

#### 后端 Service `backend/app/services/auth_service.py`

- `register()` 函数新增 `confirm_password` 参数
- 在所有参数校验之前，先判断 `password != confirm_password`，抛出 `ValidationException("两次输入的密码不一致")`
- 注册成功后以事务方式写入 users / user_roles / operation_logs

#### 前端 API `frontend/src/api/auth.ts`

- `RegisterParams` 接口新增 `confirm_password: string` 字段

#### 前端页面 `frontend/src/pages/register/index.vue`

- `handleRegister` 调用 `authApi.register` 时传入 `confirm_password: registerForm.value.confirm_password`

---

### 问题 3：修改密码接口未用 password_hash 校验旧密码

**文件**: `backend/app/services/auth_service.py`

原代码调用 `user_repo.get_user_by_id(user_id)` 获取用户信息，但 `get_user_by_id` 不返回 `password_hash`。

修复：新增 `get_user_by_id_with_password()` 函数，返回含 `password_hash` 的用户记录。`update_password()` 改用此函数：

```python
user_record = user_repo.get_user_by_id_with_password(user_id)
if not verify_password(old_password, user_record["password_hash"]):
    raise ValidationException(message="旧密码错误")
```

---

### 问题 4：注册流程未使用同一事务

**文件**: `backend/app/repositories/user_repo.py`

新增两个带 `conn` 参数的函数：
- `create_user_with_conn(conn, ...)` — 在外部事务连接中创建用户
- `assign_default_role_with_conn(conn, user_id)` — 在外部事务连接中分配角色

`insert_operation_log_with_conn` 已存在，无需修改。

**文件**: `backend/app/services/auth_service.py`

`register()` 改为使用 `get_db_transaction()` 显式事务：

```python
from app.database import get_db_transaction
with get_db_transaction() as conn:
    user_id = user_repo.create_user_with_conn(conn=conn, ...)
    user_repo.assign_default_role_with_conn(conn=conn, user_id=user_id)
    user_repo.insert_operation_log_with_conn(conn=conn, ...)
```

事务失败时整体回滚，不会出现用户创建成功但角色未分配或日志未写入的情况。

---

### 问题 5：提示词列表搜索参数与 is_active 筛选

**后端接口** `GET /api/prompt-templates` 参数：
- `keyword` — 按模板名模糊搜索
- `task_type_id` — 按任务类型过滤
- **无 is_active 参数**

**修复内容**：

`frontend/src/api/prompts.ts` — `getTemplates` 参数改为 `keyword?: string`，移除 `is_active` 和 `search`。
`frontend/src/pages/prompts/index.vue` — 调用时传入 `keyword` 而非 `search`；移除 `selectedIsActive` 变量和相关筛选下拉框（状态列在表格中仍正常展示）。

---

### 问题 6：成本统计页面字段与后端不匹配

#### 后端返回结构

`GET /api/statistics/costs` 返回：

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

原前端错误地将 `total` 嵌套在 `summary` 下，且 `by_model`/`by_project` 字段名错误。

#### `backend/app/repositories/statistics_repo.py` 补全

`by_model` SQL 新增字段：`provider_name`、`call_count`、`input_cost`、`output_cost`、`total_cost`、`total_tokens`、`input_tokens`、`output_tokens`（通过 JOIN `model_providers` 获取 `provider_name`）。

`by_project` SQL 新增字段：`call_count`、`total_tokens`、`avg_cost_per_call`。

#### `frontend/src/api/costs.ts` 修正类型

```typescript
export interface CostStatisticsData {
  total_cost: number
  input_cost: number
  output_cost: number
  total_tokens: number
  currency: string
  cost_by_model: ModelCostStat[]
  cost_by_project: ProjectCostStat[]
}
```

#### `frontend/src/pages/costs/index.vue` 修正映射

- 摘要卡片直接取 `data.total_cost`、`data.input_cost`、`data.output_cost`、`data.total_tokens`
- 表格数据改为 `data.cost_by_model` 和 `data.cost_by_project`

---

### 问题 7：调用审计日期筛选后端不支持

**后端接口** `GET /api/invocations` 参数：
- `project_id`、`task_id`、`model_id`、`status`、`page`、`page_size`
- **无 start_date / end_date 参数**

**修复内容**：
- `frontend/src/pages/invocations/index.vue` — 移除 `startDate`、`endDate` 变量及相关日期选择器 UI
- `frontend/src/api/invocations.ts` — `getInvocations` 参数移除 `start_date` 和 `end_date`
- `clearFilters()` 函数移除日期重置逻辑

---

### 问题 8：登录日志失败原因字段名

**后端返回字段**: `failure_reason`（数据库表 `login_logs` 列为 `failure_reason`）

**修复内容** `frontend/src/pages/logs/login.vue`：

```diff
- <el-table-column prop="fail_reason" ...>
- {{ row.fail_reason || "未知原因" }}
+ <el-table-column prop="failure_reason" ...>
+ {{ row.failure_reason || "未知原因" }}
```

---

## 检查结果

### 后端语法检查

```bash
python -m py_compile app/routers/auth.py          # ✅ EXIT:0
python -m py_compile app/services/auth_service.py # ✅ EXIT:0
python -m py_compile app/repositories/user_repo.py        # ✅ EXIT:0
python -m py_compile app/main.py                 # ✅ EXIT:0
python -m py_compile run.py                      # ✅ EXIT:0
python -m py_compile app/repositories/statistics_repo.py # ✅ EXIT:0
```

### 前端构建

```bash
cd ../frontend && npm run build
```

✅ **构建成功**（4.98s，1577 modules，17 assets，0 errors）

---

## 未修改内容

- `database/*` — 按要求未修改
- `docs/01_数据库Schema冻结说明.md` — 按要求未修改

---

## 注意事项

1. **数据库事务**：后端 `get_db_transaction()` 使用 `autocommit=False` 连接，事务失败时自动 rollback，无需手动处理。
2. **成本统计数据**：后端返回的 `cost_by_model` 和 `cost_by_project` 包含完整的 `input_cost`、`output_cost`、`input_tokens`、`output_tokens`、`call_count`、`provider_name` 等字段，前端表格已对应展示。
3. **调用审计日期筛选**：如需按日期过滤，可在审核中心或操作日志页面按 `created_at` 过滤，或在后续迭代中在后端 `invocations` 路由新增日期参数。
