# TASK-012-FIX: 后端整体联调与报告素材修复

## 任务目标

根据 `REVIEW-012-backend-final-test.md` 修复 Stage-12 交付材料中的阻塞问题，使后端运行说明、curl 示例、路由清单和课程测试报告素材真实、可复现、安全且与当前后端接口一致。

## 允许修改文件

- `backend/.env.example`
- `backend/README.md`
- `backend/scripts/curl_examples.sh`
- `backend/scripts/test_report_material.md`
- `cursor_and_codex_chat/handoff/HANDOFF-012-FIX-backend-final-test.md`

如确需补充说明，也可少量修改：

- `backend/scripts/route_list.md`

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 新业务模块；
2. 新业务接口；
3. 前端页面；
4. 数据库结构修改；
5. AI 新调用能力；
6. 审核中心、成果库、统计看板的新业务逻辑。

## 必须修复的问题

### 1. 修复 `test_report_material.md`

必须删除或替换所有当前后端不存在的接口，包括但不限于：

- `POST /api/auth/register`
- `/api/users/me`
- `POST /api/tasks`
- `GET /api/tasks?project_id=1`
- `POST /api/reviews`
- `GET /api/reviews`
- `POST /api/artifacts`
- `PUT /api/artifacts/{id}/adopt`
- `GET /api/statistics/team`
- `GET /api/statistics/user/{id}`

必须改为当前真实接口，例如：

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/projects/{project_id}/tasks`
- `GET /api/projects/{project_id}/tasks`
- `POST /api/outputs/{output_id}/submit-review`
- `GET /api/reviews/pending`
- `POST /api/reviews/{request_id}/complete`
- `POST /api/outputs/{output_id}/adopt`
- `GET /api/statistics/overview`
- `GET /api/statistics/member-contributions`

统一返回格式必须改为：

```json
{"code":0,"message":"success","data":{}}
```

不得写成 `code: 200` 或 `message: 操作成功`。

### 2. 修复 `curl_examples.sh`

必须：

- 为 `POST /api/tasks/{task_id}/generate` 补充合法 JSON 请求体；
- 审核评分使用 0-10 范围；
- 删除 `POST /api/projects` 中未定义的 `course_name`；
- 所有密码、Token、API Key 使用占位符；
- 不声明所有接口已真实运行通过，除非 handoff 中有可复现证据。

### 3. 修复 `backend/README.md`

必须：

- 数据库初始化命令按正确顺序覆盖 `database/01` 到 `database/07`；
- 健康检查响应示例使用统一返回格式；
- 不虚构数据库连接或接口联调已全部通过。

### 4. 修复 `.env.example`

必须：

- 与 `backend/app/config.py`、`backend/run.py` 实际读取的变量一致；
- 补充 `SERVER_HOST`、`SERVER_PORT`，或明确替换 `APP_HOST` / `APP_PORT`；
- 保持所有敏感值为占位符。

### 5. 修复 handoff

必须创建：

`cursor_and_codex_chat/handoff/HANDOFF-012-FIX-backend-final-test.md`

handoff 中说明：

1. 修改了哪些文件；
2. 每个阻塞问题如何修复；
3. `python3 scripts/check_backend.py` 的执行结果；
4. 是否修改 `backend/app/main.py`、`backend/app/config.py`、`backend/app/database.py`、`backend/run.py`，如有必须说明原因；
5. 未修改 `database/*`、未修改 `frontend/*`、未修改数据库结构；
6. 未实现新业务模块。

## 验收标准

1. Stage-12 交付材料不再包含不存在接口；
2. curl 示例能作为真实接口测试参考；
3. README 能指导从零初始化数据库并启动后端；
4. `.env.example` 与实际配置读取一致；
5. 无真实密钥泄露；
6. `python3 scripts/check_backend.py` 通过；
7. 不越界修改数据库、前端或业务逻辑。
