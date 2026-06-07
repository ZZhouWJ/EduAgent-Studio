# HANDOFF-003-FIX：Stage-03 修复版 - 用户登录与权限基础模块

## 任务状态

**完成** — 两个阻塞问题均已修复。

---

## 一、Codex 未通过原因

### 问题 1：POST /api/auth/logout 返回格式不统一

`backend/app/routers/auth.py` 中 `logout` 函数在以下两个路径调用 `success_response()` 时未传 `data` 参数：

- 第 112 行（Authorization 格式错误时）：`return success_response(message="已登出")`
- 第 124 行（成功登出时）：`return success_response(message="已成功登出")`

导致响应为 `{"code": 0, "message": "已登出", "data": null}`，不符合规范要求的 `data: {}`。

### 问题 2：登录成功测试不可复现

`HANDOFF-003` 中 admin 测试密码使用 `<密码>` 占位，并建议"登录失败后手动更新数据库哈希"，导致"正确账号可登录"验收无法复现。

---

## 二、本次修复了哪些文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/routers/auth.py` | 修改 | 两处 `success_response()` 均添加 `data={}` |
| `database/04_insert_initial_data.sql` | 修改 | admin 的 password_hash 替换为与 `Admin@123456` 匹配的 bcrypt 哈希 |
| `backend/verify_pwd.py` | 新建（辅助） | 用于验证哈希的临时脚本，可删除 |
| `cursor_and_codex_chat/handoff/HANDOFF-003-FIX-auth-user-permission.md` | 新建 | 本修复报告 |

---

## 三、logout 返回格式如何修复

### 修改前

```python
# auth.py:112
return success_response(message="已登出")

# auth.py:124
return success_response(message="已成功登出")
```

### 修改后

```python
# auth.py:112
return success_response(data={}, message="已登出")

# auth.py:124
return success_response(data={}, message="已成功登出")
```

### 对其他接口的影响

`success_response(data=None)` 的默认值在 Stage-02 中定义为返回 `data: null`，本修改**不影响**其他接口。其他接口（如 `/api/auth/login`、`/api/auth/me`）均显式传入 `data` 参数，行为不变。

### 验证方法

```bash
# 不带 Authorization（应返回 data: {}）
curl -X POST http://127.0.0.1:8000/api/auth/logout

# 期望：
{"code": 0, "message": "已登出", "data": {}}

# 带有效 token（应返回 data: {}）
curl -X POST http://127.0.0.1:8000/api/auth/logout \
  -H "Authorization: Bearer <token>"

# 期望：
{"code": 0, "message": "已成功登出", "data": {}}
```

---

## 四、admin 默认测试账号和密码

| 字段 | 值 |
| --- | --- |
| username | `admin` |
| password | `Admin@123456` |
| 角色 | `admin` |
| bcrypt 哈希（已更新） | `$2b$12$ShxG2SvnL1QcViFPuMRqHO.T8jCQgOpdWBJdYAwhVn9QgnVRCJB4O` |

> **安全提醒**：此密码仅用于课程设计初始化测试。真实部署后应立即使用 `backend/app/utils/password.py` 中的 `hash_password()` 生成新哈希并更新数据库。

---

## 五、password_hash 与 verify_password 是否匹配

已通过 Python 脚本验证：

```python
# verify_pwd.py 输出
NEW_HASH=$2b$12$ShxG2SvnL1QcViFPuMRqHO.T8jCQgOpdWBJdYAwhVn9QgnVRCJB4O
old vs Admin@123456: False   # 旧哈希不匹配
new vs Admin@123456: True    # 新哈希匹配

# 错误密码验证
new vs wrong: False          # 错误密码不匹配
```

**结论**：
- `backend/app/utils/password.py` 使用 `passlib[bcrypt]`，与 `04_insert_initial_data.sql` 中的哈希算法一致
- 新的 password_hash 与 `Admin@123456` 匹配
- 旧哈希（`$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq7b8F4Ly`）不匹配 `Admin@123456`
- 修改后 admin 登录成功测试可复现

---

## 六、是否修改数据库结构

**否**。本修复未修改 `database/02_create_tables.sql` 或任何表结构。

`database/04_insert_initial_data.sql` 仅替换了 `users` 表中 admin 用户的 `password_hash` 字段值，不涉及表结构变更。

---

## 七、是否修改初始化数据

**是**，但仅修改了一处：`users` 表中 admin 用户的 `password_hash` 字段值，从无效占位哈希替换为 `Admin@123456` 的 bcrypt 哈希。

其他所有初始化数据（角色、权限、任务类型、问题标签、模型供应商、Mock 模型等）未修改。

---

## 八、如何重新执行初始化数据

如果数据库已经初始化过，需要更新 admin 的 password_hash：

```sql
-- 方式一：直接更新（仅修改 admin 用户的密码哈希）
UPDATE users
SET password_hash = '$2b$12$ShxG2SvnL1QcViFPuMRqHO.T8jCQgOpdWBJdYAwhVn9QgnVRCJB4O'
WHERE username = 'admin' AND is_deleted = 0;

-- 方式二：重新执行初始化脚本
-- 重新执行 database/01~07 所有 SQL 文件（会先 DROP DATABASE，需谨慎）
```

---

## 九、如何测试登录成功

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}'
```

期望响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "<JWT-token>",
    "user": {
      "user_id": 1,
      "username": "admin",
      "real_name": "系统管理员",
      "roles": ["admin"]
    }
  }
}
```

---

## 十、如何测试登录失败

### 用户名不存在

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"nonexist","password":"Admin@123456"}'
```

期望：`{"code": 4002, "message": "用户名或密码错误", "data": null}`

### 密码错误

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}'
```

期望：`{"code": 4002, "message": "用户名或密码错误", "data": null}`

### 登录失败后检查 login_logs

```sql
SELECT login_id, username, login_status, failure_reason, login_time
FROM login_logs
ORDER BY login_time DESC
LIMIT 10;
```

---

## 十一、如何测试 /api/auth/me

```bash
# 先登录获取 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 测试 /api/auth/me
curl http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

期望响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "admin",
    "real_name": "系统管理员",
    "student_no": null,
    "email": "admin@example.com",
    "phone": "13800000000",
    "status": "active",
    "last_login_at": "2026-05-29T...",
    "roles": ["admin"],
    "permissions": ["..."]
  }
}
```

无 Token 或 Token 无效：`{"code": 4002, "message": "Token 无效或已过期", "data": null}`

---

## 十二、已知环境限制

1. **当前环境无 MySQL 客户端**：无法真实执行 SQL 验证，修复依赖静态代码审查和 Python 哈希生成脚本验证。
2. **当前环境无 pip/venv**：无法 `pip install -r requirements.txt` 和启动 FastAPI 服务，所有运行测试需在 MySQL + Python 环境可用后执行。
3. **无法访问 Windows MySQL**：远程 Ubuntu 环境无法连接本地 Windows MySQL，数据库连接测试暂不可行。
4. **辅助脚本需删除**：`backend/verify_pwd.py` 为本次修复创建的临时验证脚本，应在 Codex 确认后删除。
5. **admin 密码明文暴露于 handoff**：handoff 中包含明文测试密码，仅作为初始化测试用途，真实部署需更换。

---

## 十三、需要 Codex 复审的重点

1. **logout 响应格式**：`data: {}` 是否符合规范要求，是否影响其他接口
2. **password_hash 合法性**：`$2b$12$ShxG2SvnL1QcViFPuMRqHO.T8jCQgOpdWBJdYAwhVn9QgnVRCJB4O` 是否为有效 bcrypt 哈希
3. **未修改数据库结构**：确认 `04_insert_initial_data.sql` 仅替换了一个哈希值
4. **admin 登录测试可复现**：确认新哈希与 `Admin@123456` 匹配
5. **范围检查**：确认未实现 Stage-04 相关功能，未越界修改其他文件
6. **辅助文件清理**：确认 `backend/verify_pwd.py` 是否需要删除

---

## 十四、验收清单

- [x] `POST /api/auth/logout` 所有成功路径返回 `data: {}`
- [x] admin 用户 password_hash 与 `Admin@123456` 匹配
- [x] 旧占位哈希已替换
- [x] `database/04_insert_initial_data.sql` 未修改表结构
- [x] 其他初始化数据未修改
- [x] 登录成功/失败测试可复现
- [x] 未修改 `frontend/*`、`database/02_create_tables.sql`、`docs/01_数据库Schema冻结说明.md`
- [x] 未实现项目管理、任务管理、AI 调用、审核中心、成果库

---

**本修复完成后停止，等待 Codex 复审。**
