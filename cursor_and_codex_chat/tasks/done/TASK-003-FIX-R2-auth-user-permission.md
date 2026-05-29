# TASK-003-FIX-R2：修复 logout 成功响应 message

## 任务状态

待 Cursor 领取。

## 任务背景

Codex 已完成 Stage-03 Fix 复审。admin 登录测试可复现性已经通过，但 `POST /api/auth/logout` 的成功响应仍不完全符合本轮要求。

当前响应：

```json
{"code": 0, "message": "已登出", "data": {}}
```

或：

```json
{"code": 0, "message": "已成功登出", "data": {}}
```

本轮要求：

```json
{"code": 0, "message": "success", "data": {}}
```

## 允许修改文件

只允许修改：

- `backend/app/routers/auth.py`
- `cursor_and_codex_chat/handoff/HANDOFF-003-FIX-R2-auth-user-permission.md`

## 禁止修改文件

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`
- 其他后端业务文件

## 禁止实现内容

本任务只允许修复 logout 响应 message，禁止实现：

1. 项目管理；
2. 任务管理；
3. AI 调用；
4. 审核中心；
5. 成果库；
6. 前端页面；
7. 新增认证接口；
8. 新增用户管理接口；
9. 修改数据库结构或初始化数据。

## 必须修复的问题

将 `backend/app/routers/auth.py` 中 `logout()` 的两条成功返回路径改为：

```python
return success_response(data={})
```

或：

```python
return success_response(data={}, message="success")
```

修复后，以下两种场景都必须返回：

```json
{"code": 0, "message": "success", "data": {}}
```

场景：

1. 不带 Authorization 调用 `POST /api/auth/logout`；
2. 带有效 token 调用 `POST /api/auth/logout`。

## 验收清单

Cursor 完成后请确认：

1. `POST /api/auth/logout` 不带 Authorization 时返回 `{"code":0,"message":"success","data":{}}`；
2. `POST /api/auth/logout` 带有效 token 时返回 `{"code":0,"message":"success","data":{}}`；
3. 不再返回 `message: "已登出"`；
4. 不再返回 `message: "已成功登出"`；
5. 不再返回 `data: null`；
6. 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
7. 未实现任何 Stage-04 或后续阶段功能。

## 交付要求

完成后请创建：

`cursor_and_codex_chat/handoff/HANDOFF-003-FIX-R2-auth-user-permission.md`

handoff 必须说明：

1. 修改了哪几行；
2. logout 两条成功路径的最终响应；
3. 已执行的静态检查命令；
4. 是否遵守禁止修改范围。
