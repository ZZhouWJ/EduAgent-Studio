# REVIEW-003：Stage-03 用户登录与权限基础模块审查

## 1. 审查结论

结论：需要继续修改。

是否允许进入 Stage-04：暂不允许。

Stage-03 主体实现已经接近通过：认证、当前用户、登出、用户列表、角色列表、权限列表均已实现；代码按 Router / Service / Repository 分层；用户查询和登录日志写入使用参数化 SQL；未发现项目管理、任务管理、AI 调用、审核中心、成果库或前端页面在本阶段被注册到 FastAPI 主应用。

但本轮仍发现两个必须修复的问题：

1. `POST /api/auth/logout` 的成功响应未严格符合统一成功格式，当前会返回 `data: null`。
2. `HANDOFF-003` 没有给出可复现的初始登录测试凭证，且提示“如果 admin 无法登录则手动更新数据库哈希”，导致“正确账号可登录”的验收不可复现。

因此本轮不发布 Stage-04，需先完成 `TASK-003-FIX-auth-user-permission.md`。

## 2. Stage-03 范围审查

| 检查项 | 结论 |
|---|---|
| 只实现用户登录与权限基础模块 | 基本通过 |
| 未实现项目管理 | 通过，`main.py` 未注册项目路由 |
| 未实现任务管理 | 通过，`main.py` 未注册任务路由 |
| 未实现 AI 调用 | 通过，`main.py` 未注册调用路由 |
| 未实现审核中心 | 通过，`main.py` 未注册审核路由 |
| 未实现成果库 | 通过，`main.py` 未注册成果路由 |
| 未修改 frontend/ | 通过，未发现 Stage-03 期间前端文件更新 |
| 未修改 database/ | 通过，未发现 Stage-03 期间数据库文件更新 |
| 未修改 docs/01_数据库Schema冻结说明.md | 通过，未发现 Stage-03 期间 Schema 文档更新 |

说明：`backend/app/routers/projects.py`、`tasks.py`、`invocations.py` 等后续模块文件在项目中已经存在，但时间早于 Stage-03 任务发布，且本阶段 `backend/app/main.py` 只注册了 `auth.router` 和 `users.router`。本轮按“未在 Stage-03 越界注册业务接口”处理。

## 3. 认证接口审查

| 接口 | 结论 |
|---|---|
| `POST /api/auth/login` | 已实现 |
| `GET /api/auth/me` | 已实现 |
| `POST /api/auth/logout` | 已实现，但响应格式需修复 |

通过项：

- 登录成功返回 token 和用户基本信息；
- 登录失败返回统一错误结构；
- 登录成功、用户名不存在、账户禁用、密码错误均会调用 `insert_login_log()`；
- `/api/auth/me` 从 `Authorization: Bearer <token>` 解析用户；
- `/api/auth/me` 返回用户基本信息、角色列表、权限列表；
- 接口响应未返回 `password_hash`。

必须修复：

- `backend/app/routers/auth.py:112` 和 `backend/app/routers/auth.py:124` 调用 `success_response()` 时未传 `data`，因此登出成功响应为 `{"code":0,"message":"已登出","data":null}` 或 `{"code":0,"message":"已成功登出","data":null}`。规范要求成功格式中的 `data` 为对象，至少应传 `data={}`。

## 4. 用户与权限接口审查

| 接口 | 结论 |
|---|---|
| `GET /api/users` | 已实现 |
| `GET /api/roles` | 已实现 |
| `GET /api/permissions` | 已实现 |

通过项：

- `/api/users` 支持 `page`、`page_size`、`keyword`；
- `/api/users` 默认过滤 `users.is_deleted = 0`；
- 用户列表不查询也不返回 `password_hash`；
- `/api/users` 通过角色列表限制只有 `admin` 可访问；
- `/api/roles`、`/api/permissions` 需要登录用户访问；
- 本轮未实现用户删除接口，因此软删除删除行为不作为问题。

非阻塞建议：

- `routers/users.py` 中 `BaseModel`、`user_repo`、`error_response` 当前未使用，后续可清理。
- `list_roles()` 如未来支持禁用角色，建议同时过滤 `status='active'`，但本阶段只要求软删除过滤。

## 5. Repository 与参数化 SQL 审查

通过：

- 数据库访问集中在 `backend/app/repositories/user_repo.py`；
- 未使用 ORM 替代核心 SQL；
- 查询和写入均使用 `%s` 占位符和 `cursor.execute(sql, params)`；
- 未发现直接拼接用户输入到 SQL；
- `/api/users` 的模糊查询虽然构造了 `like_pattern = f"%{keyword}%"`，但该值仍作为参数传入 SQL，不属于 SQL 拼接；
- 查询用户、角色、权限时正确关联 `users`、`roles`、`user_roles`、`permissions`、`role_permissions`；
- `insert_login_log()` 写入 `login_logs`，字段与 Schema 匹配。

非阻塞建议：

- `update_user_last_login()` 在 `UPDATE` 后调用 `cursor.fetchone()` 没有必要，建议删除该行以减少误导。

## 6. 密码哈希与 Token 安全审查

通过项：

- 密码校验使用 `passlib[bcrypt]`；
- 未发现明文密码比较；
- JWT token 包含 `exp` 和 `iat`；
- token 密钥通过 `JWT_SECRET_KEY` 环境变量读取；
- 未发现返回 `password_hash`；
- 未发现返回 API Key；
- `requirements.txt` 未引入大型依赖。

需要注意：

- `backend/app/utils/token.py:14` 提供默认 `dev-secret-key-change-in-production`，属于可被环境变量覆盖的开发默认值，不按硬编码真实密钥处理。但后续部署必须通过环境变量覆盖。
- `HANDOFF-003` 已提醒生产环境必须设置高强度随机 `JWT_SECRET_KEY`，这是正确的。

## 7. login_logs 写入逻辑审查

通过：

- 用户名不存在会写入 `login_logs`，`login_status='failed'`；
- 禁用账户会写入 `login_logs`，`login_status='failed'`；
- 密码错误会写入 `login_logs`，`login_status='failed'`；
- 登录成功会写入 `login_logs`，`login_status='success'`；
- 写入字段与 `login_logs` 表结构一致。

需补充：

- handoff 中必须给出可复现的登录成功测试凭证。当前 `HANDOFF-003` 使用 `<密码>` 占位，并建议登录失败时手动更新数据库哈希，这不满足阶段验收可复现要求。

## 8. 硬编码敏感信息审查

未发现硬编码数据库账号密码、真实 API Key 或不可替换的生产密钥。

发现开发默认值：

- `JWT_SECRET_KEY` 默认值为 `dev-secret-key-change-in-production`。该值可被环境变量替换，报告中不作为阻塞问题，但必须保留部署提醒。

## 9. 运行与静态检查

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/auth.py app/routers/users.py app/services/auth_service.py app/services/user_service.py app/repositories/user_repo.py app/utils/password.py app/utils/token.py run.py
```

结果：通过，输出 `PY_COMPILE_OK`。

环境限制：

- 当前远程 Ubuntu 仍缺少 `pip` / `venv` / `ensurepip`；
- 当前环境未安装 FastAPI、PyMySQL、PyJWT、passlib 等运行依赖；
- 当前 Ubuntu 环境无法直接访问 Windows MySQL；
- 因此本轮未实际执行 `pip install -r requirements.txt`、`python run.py` 或真实接口 curl 测试。

本轮结论基于静态审查与 Python 语法编译。环境问题不直接导致 Stage-03 不通过；本轮不通过原因来自代码/交付本身仍有必须修复项。

## 10. 是否发现越界实现

未发现 Stage-03 审查对象中注册以下越界接口：

- 项目管理；
- 任务管理；
- AI 调用；
- 审核中心；
- 成果库；
- 前端页面。

## 11. 必须修复的问题

1. 修复 `POST /api/auth/logout` 成功响应格式：无论是否携带有效 token，都必须返回统一成功结构，且 `data` 至少为 `{}`，不得为 `null`。
2. 修复 `HANDOFF-003` 的登录成功测试说明：必须提供与当前初始化数据匹配的明确测试账号和密码，或明确说明当前初始化数据无法提供可复现登录成功测试，并提交后续数据库初始化数据修复申请。不得用“如果失败则手动更新数据库哈希”替代验收步骤。

## 12. 是否允许进入 Stage-04

暂不允许。

已发布修复任务：

`cursor_and_codex_chat/tasks/todo/TASK-003-FIX-auth-user-permission.md`
