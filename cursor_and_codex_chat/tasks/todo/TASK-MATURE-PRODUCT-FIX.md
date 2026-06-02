# TASK 成熟产品化完善修复任务

## 任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-MATURE-PRODUCT-COMPLETE.md` 修复成熟产品化页面和接口中的前后端契约问题，使注册、个人中心、提示词管理、调用审计、成本统计和日志页面可真实可用。

## 允许修改

- `frontend/*`
- `backend/app/routers/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/repositories/user_repo.py`
- `backend/app/routers/invocations.py`（仅当选择后端支持调用日志日期筛选时）
- `backend/app/services/invocation_service.py`（仅当选择后端支持调用日志日期筛选时）
- `backend/app/repositories/invocation_repo.py`（仅当选择后端支持调用日志日期筛选时）
- `backend/scripts/route_list.md`
- `frontend/scripts/route_list.md`
- `cursor_and_codex_chat/handoff/HANDOFF-MATURE-PRODUCT-FIX.md`

## 禁止修改

- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 必须修复

1. `frontend/src/router/guard.ts`：将 `/register` 加入未登录白名单。
2. 注册接口：前后端都加入 `confirm_password`，后端服务层必须校验两次密码一致。
3. 修改密码：修复 `auth_service.update_password()` 使用 `get_user_by_id()` 取不到 `password_hash` 的问题。
4. 注册事务：`users`、`user_roles`、`operation_logs` 同事务提交，失败 rollback。
5. 提示词管理：前端搜索参数改为后端真实 `keyword`；`is_active` 筛选要么移除，要么改成真实后端支持。
6. 成本统计：前端改用后端真实字段 `cost_by_model`、`cost_by_project`、`cost_by_user`、`total_cost`、`input_cost`、`output_cost`、`total_tokens`。
7. 调用审计日期筛选：要么移除前端日期筛选，要么后端支持日期参数并同步文档。
8. 登录日志：前端字段从 `fail_reason` 改为 `failure_reason`。

## 建议同步修复

1. 用户名前后端最小长度统一为 3；
2. 注册时显式检查 `student_no` 重复；
3. 日志页面普通用户权限范围收紧，或页面标明仅管理员使用。

## 验收命令

后端：

```bash
cd backend
python3 -m py_compile app/routers/auth.py app/services/auth_service.py app/repositories/user_repo.py app/main.py run.py
```

前端：

```bash
cd frontend
npm run build
```

## Handoff 要求

创建：

`cursor_and_codex_chat/handoff/HANDOFF-MATURE-PRODUCT-FIX.md`

说明：

1. 修复了哪些文件；
2. `/register` 是否未登录可访问；
3. 注册 confirm_password 是否服务端校验；
4. 修改密码是否已能读取 password_hash；
5. 成本、提示词、调用审计、登录日志字段是否与后端一致；
6. 是否执行后端 py_compile；
7. 是否执行前端 build。
