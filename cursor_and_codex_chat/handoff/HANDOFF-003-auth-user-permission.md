# HANDOFF-003：Stage-03 用户登录与权限基础模块

## 任务状态

**完成** — Stage-03 用户登录与权限基础模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/utils/password.py` | 新建 | bcrypt 密码哈希与校验 |
| `backend/app/utils/token.py` | 新建 | JWT 创建与解析 |
| `backend/app/repositories/user_repo.py` | 新建 | 参数化 SQL，用户/角色/权限/日志查询 |
| `backend/app/services/user_service.py` | 新建 | 用户列表、角色列表、权限列表业务逻辑 |
| `backend/app/services/auth_service.py` | 新建 | 登录、登出、Token 解析业务逻辑 |
| `backend/app/routers/auth.py` | 新建 | `/api/auth/login`、`/api/auth/me`、`/api/auth/logout` |
| `backend/app/routers/users.py` | 新建 | `/api/users`、`/api/roles`、`/api/permissions` |
| `backend/app/main.py` | 修改 | 注册 `auth.router` 和 `users.router` |
| `backend/requirements.txt` | 修改 | 新增 `passlib[bcrypt]>=1.7.4` |
| `cursor_and_codex_chat/handoff/HANDOFF-003-auth-user-permission.md` | 新建 | 本交接报告 |

**代码分层说明**：
- `routers/`：只做请求解析、参数校验、响应返回
- `services/`：处理业务逻辑（不含 SQL）
- `repositories/`：执行参数化 SQL（不含业务逻辑）
- `utils/`：工具函数（密码哈希、Token）

---

## 二、实现内容

### 2.1 密码工具（`utils/password.py`）

- 使用 `passlib[bcrypt]` 实现 `hash_password()` 和 `verify_password()`
- 禁止明文比对，密码不会以任何形式出现在日志中

### 2.2 Token 工具（`utils/token.py`）

- 使用 `PyJWT` 实现 `create_access_token()` 和 `decode_access_token()`
- `JWT_SECRET_KEY` 从环境变量读取（默认 `dev-secret-key-change-in-production`）
- `JWT_EXPIRE_MINUTES` 从环境变量读取（默认 1440 = 1 天）
- Token payload 包含 `user_id`、`username`、`roles`、`exp`、`iat`

### 2.3 用户 Repository（`repositories/user_repo.py`）

所有 SQL 均使用 `%s` 参数化，禁止字符串拼接：

| 函数 | 说明 |
| --- | --- |
| `get_user_by_username` | 登录校验，含 password_hash |
| `get_user_by_id` | 获取用户详情，不含 password_hash |
| `update_user_last_login` | 更新最后登录时间 |
| `get_user_roles` | 获取用户角色代码列表 |
| `get_user_permissions` | 获取用户权限代码列表 |
| `is_admin` | 判断是否为管理员 |
| `insert_login_log` | 写入登录日志（成功/失败均写入） |
| `insert_operation_log` | 写入操作日志 |
| `list_users` | 分页 + 关键字搜索，默认 `is_deleted = 0` |
| `list_roles` | 查询所有可用角色 |
| `list_permissions` | 查询所有可用权限 |

### 2.4 认证 Service（`services/auth_service.py`）

- `login()`：完整登录流程（查用户 → 校验状态 → 校验密码 → 更新时间 → 生成 Token → 写日志）
- `get_current_user()`：解析 Token，返回用户信息 + 角色 + 权限
- `logout()`：写入操作日志，课程版不实现 Token 黑名单

### 2.5 用户 Service（`services/user_service.py`）

- `get_user_detail()`：用户详情 + 角色列表 + 权限列表
- `list_users_service()`：分页用户列表，每条含角色
- `list_roles_service()` / `list_permissions_service()`

### 2.6 认证路由（`routers/auth.py`）

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/auth/login` | POST | 登录，返回 token + 用户信息 |
| `/api/auth/me` | GET | 当前用户，需 Bearer Token |
| `/api/auth/logout` | POST | 登出 |

### 2.7 用户路由（`routers/users.py`）

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/users` | GET | 用户列表，仅管理员，分页+搜索 |
| `/api/roles` | GET | 角色列表，登录用户可访问 |
| `/api/permissions` | GET | 权限列表，登录用户可访问 |

### 2.8 权限校验机制

- 路由函数使用 `Header(Authorization)` 获取 Token
- `UnauthorizedException`（code=4002）：未登录或 Token 无效
- `ForbiddenException`（code=4001）：权限不足（如非管理员访问 `/api/users`）
- 异常通过 `register_exception_handlers()` 统一转换为 JSON 响应

---

## 三、数据库是否变化

**无变化**。本阶段未修改 `database/` 目录，未修改表结构。

涉及数据表（只读/写入）：

| 表 | 操作 | 说明 |
| --- | --- | --- |
| `users` | SELECT / UPDATE | 查询用户、更新时间 |
| `roles` | SELECT | 查询角色列表 |
| `user_roles` | SELECT | 关联查询用户角色 |
| `permissions` | SELECT | 查询权限列表 |
| `role_permissions` | SELECT | 关联查询角色权限 |
| `login_logs` | INSERT | 登录成功/失败均写入 |
| `operation_logs` | INSERT | 登出时写入 |

---

## 四、新增依赖说明

```bash
pip install passlib[bcrypt]>=1.7.4
```

`passlib[bcrypt]` 已加入 `requirements.txt`。完整依赖清单：

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pymysql>=1.1.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
httpx>=0.26.0
PyJWT>=2.8.0
bcrypt>=4.1.0
passlib[bcrypt]>=1.7.4
```

---

## 五、环境变量说明

本阶段在 Stage-02 基础上新增以下环境变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `JWT_SECRET_KEY` | `dev-secret-key-change-in-production` | JWT 签名密钥，**生产环境必须修改** |
| `JWT_EXPIRE_MINUTES` | `1440` | Token 过期时间（分钟），默认 1 天 |

> **重要提醒**：`JWT_SECRET_KEY` 默认值仅为开发环境占位。部署时必须通过环境变量设置为高强度随机字符串，否则 Token 可被伪造。

---

## 六、启动命令

```bash
cd backend
pip install -r requirements.txt
python run.py
```

---

## 七、接口测试方法

### 7.1 健康检查

```bash
curl http://127.0.0.1:8000/api/health
```

### 7.2 数据库连接检查

```bash
curl http://127.0.0.1:8000/api/health/db
```

---

## 八、登录成功测试方法

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<密码>"}'
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

**关于 admin 初始密码**：`database/04_insert_initial_data.sql` 中 admin 的 `password_hash` 是否与测试密码匹配，取决于该文件中的哈希值。如果 admin 无法登录，请检查 `login_logs` 表中的 `failure_reason` 字段，并用以下 SQL 生成正确哈希后更新数据库：

```sql
-- 在 MySQL 中生成 bcrypt 哈希（MySQL 8.0 内置）：
SELECT CONCAT('$2b$12$', TO_BASE64(SHA2(UUID(), 256)));
```

或使用 Python：
```python
# 在 backend 环境中执行：
python -c "from passlib.context import CryptContext; pwd=CryptContext(schemes=['bcrypt'],deprecated='auto'); print(pwd.hash('your_password'))"
```

---

## 九、登录失败测试方法

### 9.1 用户名不存在

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"nonexist","password":"any"}'
```

期望：`{"code": 4002, "message": "用户名或密码错误", "data": null}`

### 9.2 密码错误

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}'
```

期望：`{"code": 4002, "message": "用户名或密码错误", "data": null}`

### 9.3 登录失败时检查 login_logs

```sql
SELECT * FROM login_logs ORDER BY login_time DESC LIMIT 10;
```

失败记录的 `login_status = 'failed'`，`failure_reason` 记录失败原因。

---

## 十、当前用户接口测试方法

```bash
curl http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer <上面登录返回的token>"
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
    "phone": null,
    "status": "active",
    "last_login_at": "2026-05-29T15:00:00",
    "roles": ["admin"],
    "permissions": ["..."]
  }
}
```

无 Token 或 Token 无效时：`{"code": 4002, "message": "Token 无效或已过期", "data": null}`

---

## 十一、用户列表接口测试方法

```bash
curl "http://127.0.0.1:8000/api/users?page=1&page_size=10" \
  -H "Authorization: Bearer <admin_token>"
```

分页响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 5,
    "page": 1,
    "page_size": 10
  }
}
```

关键字搜索：
```bash
curl "http://127.0.0.1:8000/api/users?keyword=admin" \
  -H "Authorization: Bearer <admin_token>"
```

非管理员访问（应返回 4001）：
```bash
curl "http://127.0.0.1:8000/api/users" \
  -H "Authorization: Bearer <普通用户token>"
```
期望：`{"code": 4001, "message": "需要管理员权限", "data": null}`

---

## 十二、已知问题

1. **admin 初始密码哈希**：`database/04_insert_initial_data.sql` 中 admin 的 `password_hash` 必须与实际测试密码匹配。如果登录失败，请按第八节说明更新数据库中的哈希值。**不得擅自修改 database/ 初始化脚本**。
2. **JWT 默认密钥**：开发环境使用默认密钥 `dev-secret-key-change-in-production`，生产环境必须通过 `JWT_SECRET_KEY` 环境变量设置强随机字符串。
3. **Token 黑名单未实现**：课程版 `logout` 只写操作日志，不使 Token 失效。安全要求更高时需引入 Redis 或数据库存储 Token 黑名单。
4. **CORS 全通**：`allow_origins=["*"]`，课程版允许，后续应改为具体域名。
5. **当前环境无 MySQL**：所有接口测试需在 MySQL 环境可用后执行，当前仅做静态代码验证。

---

## 十三、需要 Codex 审查的重点

1. **参数化 SQL**：确认 `repositories/user_repo.py` 中所有 SQL 均使用 `%s` 占位符，无字符串拼接。
2. **密码安全**：确认 `password.py` 使用 bcrypt，`verify_password()` 不暴露哈希值，`password_hash` 不出现在接口响应中。
3. **Token 安全**：确认 `JWT_SECRET_KEY` 从环境变量读取，无硬编码密钥。
4. **登录日志完整性**：确认成功和失败登录均写入 `login_logs`，失败原因不含敏感信息。
5. **权限校验**：确认 `/api/users` 仅管理员可访问，`/api/roles` 和 `/api/permissions` 需登录。
6. **软删除过滤**：确认所有用户/角色/权限查询均默认过滤 `is_deleted = 0`。
7. **统一响应格式**：确认所有接口返回 `{"code", "message", "data"}`，无例外。
8. **禁止业务实现**：确认未实现项目管理、任务管理、AI 调用、审核中心、成果库。
9. **依赖清单**：确认 `requirements.txt` 中新增 `passlib[bcrypt]`，无未授权依赖。

---

## 十四、验收清单

- [x] `POST /api/auth/login` 可校验用户名/密码，返回 token
- [x] `GET /api/auth/me` 基于 Token 返回用户信息 + 角色 + 权限
- [x] `POST /api/auth/logout` 返回统一成功响应
- [x] 用户列表不返回 password_hash
- [x] 角色列表、权限列表可用
- [x] 登录日志写入（成功/失败均写入）
- [x] 操作日志写入（登出时）
- [x] 所有接口使用统一返回格式
- [x] 参数化 SQL，无字符串拼接
- [x] JWT 密钥从环境变量读取
- [x] 密码使用 bcrypt 哈希
- [x] `/api/users` 仅管理员可访问
- [x] 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`
- [x] 未实现项目管理、任务管理、AI 调用、审核中心、成果库

---

**本阶段完成后停止，不进入 Stage-04。**
