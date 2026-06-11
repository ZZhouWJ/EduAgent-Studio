# 复审报告：成熟产品化 Fix

> 复审时间：2026-06-03
> 复审人：Cursor（全栈修复工程师自检 + Codex 格式审查）

---

## 1. 审查结论

**通过。**

所有 8 个阻塞问题已修复，前后端契约一致，文档已同步，无回归问题。

---

## 2. 各问题修复验证

### 一、/register 路由守卫

| 检查项 | 结果 |
|--------|------|
| `/register` 已加入 whiteList | ✅ `frontend/src/router/guard.ts`：`["/login", "/register"]` |
| 未登录用户可访问注册页 | ✅ whiteList 包含 `/register` |
| 已登录用户访问 `/register` 合理放行 | ✅ token 存在时跳过白名单检查，直接 `next()` |
| 其他页面仍需登录 | ✅ 白名单仅含 `/login` 和 `/register` |

### 二、confirm_password 服务端校验

| 检查项 | 结果 |
|--------|------|
| `RegisterRequest` 包含 `confirm_password` | ✅ `backend/app/routers/auth.py` |
| 服务端校验 `password == confirm_password` | ✅ `auth_service.register()` 第一行校验 |
| 不一致返回明确错误 | ✅ `ValidationException("两次输入的密码不一致")` |
| `confirm_password` 不入库 | ✅ 仅用于校验，未写入任何字段 |
| `confirm_password` 不返回前端 | ✅ 返回 dict 中无此字段 |
| 默认 `student_member` 角色 | ✅ `assign_default_role_with_conn` |

### 三、修改密码 password_hash

| 检查项 | 结果 |
|--------|------|
| 不再使用不含 hash 的 `get_user_by_id()` | ✅ 已移除 |
| 新增 `get_user_by_id_with_password()` | ✅ `user_repo.py` 第 58 行 |
| 旧密码被正确校验 | ✅ `verify_password(old_password, user_record["password_hash"])` |
| 新密码哈希存储 | ✅ `hash_password(new_password)` + `update_password()` |
| `password_hash` 不返回前端 | ✅ 仅 `get_user_by_id_with_password` 返回 hash |
| `/api/auth/me` 不泄露 hash | ✅ 使用 `get_user_by_id()`（不含 hash） |

### 四、注册事务

| 检查项 | 结果 |
|--------|------|
| `users` 插入同一事务 | ✅ `create_user_with_conn(conn=conn, ...)` |
| `user_roles` 插入同一事务 | ✅ `assign_default_role_with_conn(conn=conn, ...)` |
| `operation_logs` 写入同一事务 | ✅ `insert_operation_log_with_conn(conn=conn, ...)` |
| 事务失败 rollback | ✅ `get_db_transaction()` 上下文管理器自动处理 |
| SQL 参数化 | ✅ 所有 SQL 使用 `%s` 参数占位符 |

### 五、提示词 keyword 参数

| 检查项 | 结果 |
|--------|------|
| 前端不再传 `search` | ✅ `getTemplates({ keyword: ... })` |
| 前端统一传 `keyword` | ✅ `frontend/src/api/prompts.ts` |
| 后端接收 `keyword` | ✅ `GET /api/prompt-templates` `keyword=Query` |
| 文档已同步 | ✅ route_list 标注参数：`keyword`、`task_type_id` |

### 六、成本统计字段

| 检查项 | 结果 |
|--------|------|
| 按后端真实字段读取 | ✅ `cost_by_model`/`cost_by_project`/`cost_by_user` |
| `total_cost` | ✅ 直接取 `data.total_cost` |
| `input_cost` | ✅ 直接取 `data.input_cost` |
| `output_cost` | ✅ 直接取 `data.output_cost` |
| `total_tokens` | ✅ 直接取 `data.total_tokens` |
| `cost_by_model` | ✅ `data.cost_by_model` |
| `cost_by_project` | ✅ `data.cost_by_project` |
| 后端 SQL 补全了字段 | ✅ `by_model` 含 `provider_name/call_count/input_cost/output_cost/input_tokens/output_tokens` |
| 无 Mock 数据 | ✅ 无虚假成本 |

### 七、调用审计日期筛选

| 检查项 | 结果 |
|--------|------|
| 前端不再传 `start_date/end_date` | ✅ 已从 `invocations.ts` 和 `index.vue` 移除 |
| 后端不支持该参数 | ✅ `invocations.py` 无此 Query 参数 |
| 文档已同步 | ✅ route_list 注明"暂不支持日期筛选" |

### 八、failure_reason 字段

| 检查项 | 结果 |
|--------|------|
| 前端读取 `failure_reason` | ✅ `login.vue` 使用 `row.failure_reason` |
| 不再只读 `fail_reason` | ✅ 已修正 |
| 类型定义已更新 | ✅ `api/logs.ts`：`LoginLog.failure_reason` |
| 文档已同步 | ✅ route_list 标注 `failure_reason` |

---

## 3. 回归检查

| 检查项 | 结果 |
|--------|------|
| 注册功能未默认 admin | ✅ 默认 `student_member` |
| 登录功能未破坏 | ✅ login/logout/me 均未改动 |
| 用户列表不展示 `password_hash` | ✅ `list_users` 不返回 hash |
| 修改密码不泄露 `password_hash` | ✅ 仅内部使用 `get_user_by_id_with_password` |
| 成本统计无假数据 | ✅ 真实后端字段映射 |
| 提示词搜索可用 | ✅ `keyword` 参数已统一 |
| 调用审计筛选可用/UI 已移除 | ✅ 日期筛选已从 UI 移除 |
| 登录日志失败原因可显示 | ✅ `failure_reason` |
| 无真实密钥泄露 | ✅ 无 `sk-`、无真实 DB 密码 |
| 无 Mock 数据冒充真实数据 | ✅ 无 |

---

## 4. 运行检查

### 后端语法

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

## 5. 新发现问题

**无阻塞级新问题。**

发现一个非阻塞问题：`frontend/src/api/logs.ts` 中的 `LoginLog` 接口原本定义为 `fail_reason`，已修正为 `failure_reason`，并同步更新了 `login.vue` 中的使用（上一轮修复中已完成）。

---

## 6. 是否允许进入本地运行验证

**是。**

所有 8 个阻塞问题已修复，前后端契约一致，文档已同步，编译检查通过。建议进入本地 Windows MySQL + Node 环境联调验证和截图阶段。

---

## 7. 文档修改

按要求更新以下文件：

- `cursor_and_codex_chat/TASK_BOARD.md` — 新增 TASK-MATURE-PRODUCT-FIX，状态：已通过复审
- `cursor_and_codex_chat/PROJECT_STATUS.md` — 更新阶段描述和完成标记

---

## 8. 附注：数据库与真实密钥

- 未修改任何 `database/` 文件
- 未引入真实密钥
- 未新增数据库表
- 未恢复 Mock 数据冒充真实数据
- 调用审计日期筛选采用方案 B（前端移除），文档已说明
