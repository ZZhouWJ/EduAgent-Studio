# REVIEW 成熟产品化完善审查报告

## 1. 审查结论

需要继续修改。

Cursor 本轮确实新增了大量前端页面和部分后端接口，前端构建通过，成熟化方向是对的。但审查发现多个阻塞级契约问题：注册页当前未登录时无法访问；注册接口缺少服务端 confirm_password 校验；个人中心修改密码后端会因取不到 password_hash 报错；提示词筛选、成本统计、调用审计、登录日志存在前后端字段或参数不一致。

这些问题不是推倒重来级别，但需要 Cursor 定点修复后再作为“成熟产品化完成”验收。

## 2. 已确认完成的内容

### 前端页面存在

已确认以下页面文件存在：

- `/register`：`frontend/src/pages/register/index.vue`
- `/users`：`frontend/src/pages/users/index.vue`
- `/profile`：`frontend/src/pages/profile/index.vue`
- `/prompts`：`frontend/src/pages/prompts/index.vue`
- `/invocations`：`frontend/src/pages/invocations/index.vue`
- `/costs`：`frontend/src/pages/costs/index.vue`
- `/logs/operation`：`frontend/src/pages/logs/operation.vue`
- `/logs/login`：`frontend/src/pages/logs/login.vue`
- `/projects/:projectId`：`frontend/src/pages/projects/ProjectDetail.vue`
- `/reviews`：`frontend/src/pages/reviews/index.vue`
- `/artifacts`：`frontend/src/pages/artifacts/index.vue`

### 路由与菜单

`frontend/src/router/index.ts` 已注册新增路由；`BackendLayout.vue` 已扩展为 5 个分组菜单，并包含个人中心入口。

### 后端接口

已确认后端新增或注册：

- `POST /api/auth/register`
- `PUT /api/auth/me/password`
- `PUT /api/users/{user_id}/status`
- `PUT /api/users/{user_id}/roles`
- `GET /api/logs/operation`
- `GET /api/logs/login`

`backend/app/main.py` 已 include `logs.router`。

### 构建与语法

- 后端新增相关文件 py_compile 通过。
- Windows Node 环境执行 `npm run build` 通过，`vite build` 成功产出 dist。

## 3. 阻塞问题

### 问题 1：注册页被路由守卫拦截，未登录用户无法访问 `/register`

位置：`frontend/src/router/guard.ts`

当前白名单只有：

```ts
const whiteList = ["/login"]
```

结果：未登录用户点击登录页“注册账号”跳转 `/register` 后，会被守卫重定向回 `/login?redirect=/register`，注册页实际不可访问。

修复要求：

```ts
const whiteList = ["/login", "/register"]
```

并确认已登录用户访问 `/register` 时可跳转首页或登录页，不影响登录流程。

### 问题 2：后端注册接口没有接收和校验 confirm_password

位置：`backend/app/routers/auth.py`、`backend/app/services/auth_service.py`

前端注册页有 `confirm_password`，但提交给后端时只传：

```ts
username, real_name, student_no, email, phone, password
```

后端 `RegisterRequest` 也没有 `confirm_password` 字段。也就是说，服务端没有做确认密码一致性校验，只依赖前端校验。作为正式产品化注册接口，这不够可靠。

修复要求：

- `RegisterRequest` 增加 `confirm_password`；
- 前端 `authApi.register` 和注册页提交该字段；
- 后端服务层校验 `password == confirm_password`；
- 不一致返回统一错误格式。

### 问题 3：个人中心修改密码后端会因 password_hash 缺失报错

位置：`backend/app/services/auth_service.py`

`update_password()` 中：

```py
user_record = user_repo.get_user_by_id(user_id)
verify_password(old_password, user_record["password_hash"])
```

但 `user_repo.get_user_by_id()` 明确不返回 `password_hash`。因此修改密码接口会触发 KeyError 或系统内部错误。

修复要求：

- 新增 `user_repo.get_user_auth_by_id(user_id)`，返回 `user_id, username, password_hash, status`；或修改现有内部专用方法；
- `update_password()` 使用可拿到 hash 的仓储方法；
- 检查旧密码失败返回清晰错误；
- 成功后写入 operation_logs 更好。

### 问题 4：注册流程不是同事务，失败时可能留下半成品用户

位置：`auth_service.register()`、`user_repo.create_user()`、`assign_default_role()`、`insert_operation_log()`

目前创建用户、分配默认角色、写操作日志分别使用独立 `get_db_cursor()`。如果用户创建成功但默认角色分配或日志写入失败，会留下没有角色或缺日志的用户。

修复要求：

- 注册流程使用同一数据库连接事务；
- `users`、`user_roles`、`operation_logs` 同事务提交；
- 任一环节失败 rollback。

### 问题 5：提示词列表筛选参数与后端不一致

位置：`frontend/src/api/prompts.ts`、`frontend/src/pages/prompts/index.vue`、`backend/app/routers/prompts.py`

前端传：

```ts
search: searchKeyword.value
is_active: selectedIsActive.value
```

后端 `GET /api/prompt-templates` 接收：

```py
keyword
```

并不接收 `search` 或 `is_active`。结果：搜索和启用状态筛选不会生效。

修复要求：

- 前端改为传 `keyword`；
- `is_active` 如后端不支持，前端不要宣称后端筛选；可在前端本地过滤，或移除该筛选，或让后端明确支持。

### 问题 6：成本统计页面数据结构与后端返回不一致

位置：`frontend/src/api/costs.ts`、`frontend/src/pages/costs/index.vue`、`backend/app/repositories/statistics_repo.py`

前端期望：

```ts
summary
by_model
by_project
```

后端实际返回字段为：

```py
total_cost
input_cost
output_cost
total_tokens
cost_by_model
cost_by_project
cost_by_user
currency
```

结果：`/costs` 页面摘要卡和表格可能为空或显示错误。

修复要求：

- 前端 `costs.ts` 类型和页面读取字段改为后端真实字段；
- 使用 `cost_by_model`、`cost_by_project`；
- 摘要卡使用 `total_cost`、`input_cost`、`output_cost`、`total_tokens`。

### 问题 7：调用审计日期筛选参数与后端不一致

位置：`frontend/src/api/invocations.ts`、`frontend/src/pages/invocations/index.vue`、`backend/app/routers/invocations.py`

前端传 `start_date/end_date`，但后端 `GET /api/invocations` 不接收日期参数。结果：调用审计的日期筛选不会生效。

修复选择：

- 要么移除前端日期筛选；
- 要么后端新增 `date_from/date_to` 或 `start_date/end_date` 过滤，并同步 route_list。

### 问题 8：登录日志失败原因字段名不一致

位置：`frontend/src/api/logs.ts`、`frontend/src/pages/logs/login.vue`、`backend/app/repositories/user_repo.py`

前端使用：

```ts
fail_reason
```

后端返回：

```sql
failure_reason
```

结果：登录失败原因会显示为空或“未知原因”。

修复要求：

- 前端改用 `failure_reason`；或后端 alias 为 `fail_reason`，但建议前端适配后端真实字段。

## 4. 非阻塞建议

1. 注册用户名前端提示“最少3个字符”，但后端 `RegisterRequest.username` 是 `min_length=1`，建议统一为 3。
2. 注册未显式检查 `student_no` 重复，若数据库唯一约束触发，会返回不友好的数据库错误。建议服务端增加学生号重复校验。
3. 日志接口当前登录用户均可访问全部日志，若用于真实产品，应改为 admin 可全局查看，普通用户只看自己相关日志。
4. 成熟化页面大量使用 `any`，课程演示可接受，后续可逐步补类型。
5. `frontend/dist` 又因 build 重新生成，最终交付前可再次清理或明确是否需要保留。

## 5. 旧问题检查

- 未发现 Apifox/Mock API 地址残留；
- 未发现前端展示 `password_hash`；
- 未发现前端调用旧 `/save-as` 接口；
- 未发现完整 `sk-` API Key；
- `POST /api/outputs/{output_id}/save-as-new-version` 文档仍为正式接口。

## 6. 是否允许作为“成熟产品化完成”通过

暂不允许。

建议先完成 `TASK-MATURE-PRODUCT-FIX.md` 中的修复，至少解决：

1. `/register` 白名单；
2. 服务端 `confirm_password`；
3. 修改密码 `password_hash` 缺失；
4. `/costs` 返回字段适配；
5. `/prompts` 搜索参数；
6. 登录日志 `failure_reason` 字段；
7. 调用审计日期筛选处理。
