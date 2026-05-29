# TASK-003-FIX：Stage-03 用户登录与权限基础模块修复

## 任务状态

待 Cursor 领取。

## 任务背景

Codex 对 Stage-03 进行审查后，结论为：需要继续修改。

Stage-03 主体实现已经接近通过，但仍有两个必须修复的问题。本修复任务只允许围绕 Stage-03 的认证与权限基础模块做小范围修复，不得进入 Stage-04。

## 允许修改文件

优先只修改：

- `backend/app/routers/auth.py`
- `cursor_and_codex_chat/handoff/HANDOFF-003-auth-user-permission.md`

如确实需要补充说明，可修改：

- `cursor_and_codex_chat/tasks/todo/TASK-003-auth-user-permission.md`

除上述文件外，不得修改其他后端业务文件。

## 禁止修改文件

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现内容

本修复任务禁止实现：

1. 项目管理；
2. 任务管理；
3. AI 调用；
4. 审核中心；
5. 成果库；
6. 前端页面；
7. 用户新增、用户编辑、用户删除、角色分配等超出当前修复范围的接口。

## 必须修复的问题

### 1. 修复登出成功响应格式

当前 `backend/app/routers/auth.py` 中 `POST /api/auth/logout` 在以下场景会返回 `data: null`：

- 未提供或格式错误的 Authorization；
- 提供有效 token 并成功登出。

统一成功格式要求：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

修复要求：

- `logout()` 的所有成功返回都必须显式传入 `data={}`；
- 不得破坏现有统一响应结构；
- 不得修改 `database/*` 或前端。

建议修复方式：

```python
return success_response(data={}, message="已登出")
return success_response(data={}, message="已成功登出")
```

### 2. 修复登录成功测试说明不可复现问题

当前 `HANDOFF-003` 使用 `<密码>` 占位，并说明如果 admin 无法登录则手动更新数据库哈希。这会导致 Stage-03 的“正确账号可登录”验收无法复现。

修复要求二选一：

1. 如果当前 `database/04_insert_initial_data.sql` 中 admin 的 bcrypt 哈希对应某个明确明文密码，请在 handoff 中写清楚：
   - 测试账号；
   - 测试密码；
   - 登录成功 curl 命令；
   - 预期响应；
   - 不要要求审查者临时改数据库。

2. 如果当前初始化数据无法确认可用明文密码，则不得声称“登录成功测试已可执行”。请在 handoff 中明确写成：
   - 当前代码逻辑支持 bcrypt 登录；
   - 当前初始化数据缺少可复现明文测试密码；
   - 需要后续提交数据库初始化数据修复申请；
   - 不得直接修改 `database/*`。

## 验收清单

Cursor 完成修复后，请确认：

1. `POST /api/auth/logout` 所有成功路径都返回 `data: {}`；
2. 登录失败仍返回统一错误格式；
3. `POST /api/auth/login`、`GET /api/auth/me`、`GET /api/users`、`GET /api/roles`、`GET /api/permissions` 不被破坏；
4. `HANDOFF-003` 中登录成功测试步骤可复现，或者明确声明初始化数据测试凭证缺失并提出修复申请；
5. 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
6. 未实现 Stage-04 或其他后续阶段功能。

## 交付要求

完成后请更新：

`cursor_and_codex_chat/handoff/HANDOFF-003-auth-user-permission.md`

handoff 必须说明：

1. 修改了哪些文件；
2. 如何验证登出响应格式；
3. 登录成功测试凭证是否可复现；
4. 如不可复现，是否提交了明确的初始化数据修复申请；
5. 是否仍遵守 Stage-03 范围。
