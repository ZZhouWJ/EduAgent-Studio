# TASK-003：Stage-03 用户登录与权限基础模块

## 任务状态

已完成。

## 任务背景

Stage-02 FastAPI 后端基础框架已通过 Codex 审查。现在进入 Stage-03，只允许实现用户登录与权限基础模块，不得扩展到项目、任务、AI 调用、审核中心、成果库或前端页面。

## 任务目标

完成用户登录与权限基础模块，包括：

1. 登录接口；
2. 当前用户接口；
3. JWT 或 Token 管理；
4. 密码哈希；
5. 登录日志写入；
6. 用户列表基础查询；
7. 角色列表基础查询；
8. 权限校验基础工具。

## 允许修改文件

只允许修改或创建以下文件：

- `backend/app/routers/auth.py`
- `backend/app/routers/users.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/user_service.py`
- `backend/app/repositories/user_repo.py`
- `backend/app/utils/password.py`
- `backend/app/utils/token.py`
- `backend/app/main.py`
- `backend/requirements.txt`
- `cursor_and_codex_chat/handoff/HANDOFF-003-auth-user-permission.md`

## 禁止修改文件

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现内容

Stage-03 禁止实现：

1. 项目管理；
2. 任务管理；
3. AI 调用；
4. 审核中心；
5. 成果库；
6. 前端页面。

## 接口范围

本阶段建议实现以下后端接口，路径必须符合 `docs/02_接口契约与页面清单.md`：

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/users`
- `GET /api/roles`

如规范文件中接口命名存在更精确约定，以规范文件为准，不得自行发明额外业务接口。

## 数据表范围

本阶段只允许围绕以下表做查询或写入：

- `users`
- `roles`
- `user_roles`
- `permissions`
- `role_permissions`
- `login_logs`
- `operation_logs`

不得修改数据库结构，不得新增表、字段、状态值或枚举值。

## 实现要求

1. 使用 Repository 层封装 SQL，业务逻辑放在 Service 层，路由层只做请求解析和响应返回。
2. SQL 必须使用参数化查询，不得拼接用户输入。
3. 查询用户、角色、权限时必须遵守软删除字段，默认过滤 `is_deleted = 0`。
4. 登录成功和失败都应写入 `login_logs`。
5. 重要鉴权相关操作建议写入 `operation_logs`。
6. 不得在接口响应中返回 `password_hash`、密钥、完整 token 或数据库内部敏感信息。
7. 密码校验必须使用哈希方案，不得明文比对生产密码。
8. Token 密钥、过期时间等配置必须从环境变量读取或提供安全默认值，不得硬编码真实密钥。
9. 所有接口必须使用 Stage-02 已建立的统一返回格式。
10. 数据库连接失败或认证失败时必须优雅返回错误响应，不得导致服务崩溃。

## 统一返回格式

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误响应：

```json
{
  "code": 4001,
  "message": "错误信息",
  "data": null
}
```

具体错误码可按现有异常工具扩展，但不得破坏统一响应结构。

## 验收清单

Cursor 完成后，请确认：

1. `POST /api/auth/login` 可以校验用户名/密码并返回 token 或登录凭证；
2. `GET /api/auth/me` 可以基于 token 返回当前用户基础信息和角色/权限摘要；
3. `POST /api/auth/logout` 能返回统一成功响应；
4. 用户列表基础查询不返回密码哈希；
5. 角色列表基础查询可用；
6. 权限校验工具可被后续模块复用；
7. 登录日志写入逻辑存在；
8. 所有新增接口均使用统一返回格式；
9. 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
10. 未实现项目管理、任务管理、AI 调用、审核中心、成果库或前端页面。

## 交付要求

完成后请创建或更新：

`cursor_and_codex_chat/handoff/HANDOFF-003-auth-user-permission.md`

handoff 必须说明：

1. 修改了哪些文件；
2. 实现了哪些接口；
3. 依赖安装命令；
4. 启动命令；
5. 接口测试方法；
6. 是否需要数据库初始化数据支持；
7. 已知限制或待 Codex 审查事项。
