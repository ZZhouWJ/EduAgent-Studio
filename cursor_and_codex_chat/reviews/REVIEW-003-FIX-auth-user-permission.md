# REVIEW-003-FIX：Stage-03 Fix 用户登录与权限复审

## 1. 审查结论

结论：需要继续修改。

是否允许进入 Stage-04：暂不允许。

本轮只复审上一轮两个阻塞问题。结果如下：

1. `POST /api/auth/logout` 已修复 `data: null` 问题，但成功响应的 `message` 仍为 `已登出` / `已成功登出`，不等于本轮要求的 `success`。
2. admin 登录测试可复现性已修复：handoff 明确给出账号 `admin`、密码 `Admin@123456`，初始化脚本中的 bcrypt 哈希经校验与该密码匹配。

因此本轮仍不发布 Stage-04，只发布一个极小范围修复任务。

## 2. logout 返回格式是否修复

结论：部分修复，仍需修改。

当前代码：

```python
return success_response(data={}, message="已登出")
return success_response(data={}, message="已成功登出")
```

已修复：

- 两条成功路径均显式传入 `data={}`；
- 不再返回 `data: null`。

仍未满足本轮要求：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

当前实际响应为：

```json
{"code": 0, "message": "已登出", "data": {}}
```

或：

```json
{"code": 0, "message": "已成功登出", "data": {}}
```

必须将 logout 两条成功路径改为默认成功消息，或显式 `message="success"`。

## 3. admin 登录测试是否可复现

结论：通过。

检查结果：

| 检查项 | 结论 |
|---|---|
| handoff 是否明确给出测试账号和密码 | 通过 |
| 默认账号是否为 `admin` | 通过 |
| 默认密码是否为 `Admin@123456` | 通过 |
| `database/04_insert_initial_data.sql` 中 admin password_hash 是否为 bcrypt 哈希 | 通过 |
| 该 hash 是否匹配 `Admin@123456` | 通过 |
| `backend/app/utils/password.py` 是否使用 `verify_password()` 验证哈希 | 通过 |
| 是否没有明文保存 password_hash | 通过，数据库中保存的是 bcrypt hash |
| 是否没有修改数据库表结构 | 通过 |

核验方式：

- `database/04_insert_initial_data.sql` 仅替换 admin 用户的 `password_hash` 值；
- `git diff --ignore-space-at-eol -- database/02_create_tables.sql` 无实质结构变更输出；
- 使用本地临时安装的 `bcrypt` 包验证：

```text
Admin@123456 True
wrongpassword False
```

说明：远程 Ubuntu 环境缺少 `passlib`，因此无法在远程直接调用项目的 `verify_password()` 做运行级验证。本地使用标准 `bcrypt.checkpw()` 对同一 `$2b$12$...` 哈希进行了等价校验。

## 4. 是否发现越界修改

结论：未发现新的业务越界实现。

| 检查项 | 结论 |
|---|---|
| 是否没有实现项目管理 | 通过 |
| 是否没有实现任务管理 | 通过 |
| 是否没有实现 AI 调用 | 通过 |
| 是否没有修改 frontend/ | 通过 |
| 是否没有修改 docs/01_数据库Schema冻结说明.md | 通过 |

补充说明：

- `database/04_insert_initial_data.sql` 被修改了一处 admin 初始密码哈希，用于满足本轮“admin 登录测试可复现性”要求；
- 未发现 `database/02_create_tables.sql` 表结构实质变更；
- handoff 中提到 `backend/verify_pwd.py` 为辅助脚本，但复审时远程项目中未发现该文件残留。

## 5. Python 静态检查

已执行：

```bash
cd backend
python3 -m py_compile app/routers/auth.py app/utils/response.py app/utils/password.py app/services/auth_service.py app/repositories/user_repo.py
```

结果：通过，输出 `PY_COMPILE_OK`。

环境限制：

- 远程 Ubuntu 缺少 `pip` / `venv` / `passlib` 等运行依赖；
- 远程 Ubuntu 无法访问 Windows MySQL；
- 因此本轮未执行 FastAPI 启动和真实数据库登录测试。

环境限制不作为阻塞项；本轮唯一阻塞项是 logout 成功响应的 `message` 未严格等于 `success`。

## 6. 是否允许进入 Stage-04

暂不允许。

已发布新的极小范围修复任务：

`cursor_and_codex_chat/tasks/todo/TASK-003-FIX-R2-auth-user-permission.md`

修复完成后，只需复查 `POST /api/auth/logout` 的成功响应是否严格为：

```json
{"code": 0, "message": "success", "data": {}}
```
