# REVIEW-012: Stage-12 后端整体联调与报告素材审查报告

## 1. 审查结论

**不通过**

Stage-12 已完成依赖整理、环境变量样例、后端 README、语法检查脚本、curl 示例、路由清单和测试报告素材等交付物；后端 Python 语法检查通过。

但当前交付材料中存在会直接误导课程验收和接口测试的阻塞问题：

1. `backend/scripts/test_report_material.md` 混入大量当前后端不存在的接口、错误路径和错误统一返回格式。
2. `backend/scripts/curl_examples.sh` 部分关键接口请求体不符合实际接口模型，不能作为可复现测试参考。
3. `backend/README.md` 的数据库初始化步骤不完整，健康检查响应示例也未使用统一返回格式。
4. `.env.example` 中服务端口变量与实际 `config.py` 读取的变量名不一致。

因此本轮不允许进入 Stage-13，不发布 `TASK-013-frontend-base.md`。

## 2. Stage-12 是否遵守任务范围

**基本遵守，但需说明工作区状态。**

本轮交付内容集中在后端联调、运行说明、测试脚本和报告素材，未发现新增业务模块、前端页面或数据库结构修改。

说明：当前 `git status` 仍显示 `database/`、`docs/` 存在历史未提交改动；本轮 handoff 声明 Stage-12 未修改这些目录。本次审查未发现 Stage-12 为完成任务而修改数据库脚本或前端页面。

## 3. requirements.txt 是否完整合理

**基本通过。**

`backend/requirements.txt` 包含：

- `fastapi`
- `uvicorn[standard]`
- `pymysql`
- `pydantic`
- `pydantic-settings`
- `python-dotenv`
- `PyJWT`
- `bcrypt`
- `passlib[bcrypt]`
- `cryptography`

这些依赖覆盖当前后端运行、数据库连接、配置读取、认证、密码哈希和 API Key 加密需求。

小问题：`httpx` 当前主要作为测试或可替代客户端说明保留，非阻塞，但如果没有实际使用，建议移除或在 README 中说明其用途。

## 4. .env.example 是否安全完整

**需要继续修改。**

优点：

- 文件存在。
- 包含 `APP_NAME`、`APP_ENV`、`APP_HOST`、`APP_PORT`。
- 包含 `DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`、`DB_CHARSET`。
- 包含 `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_EXPIRE_MINUTES`。
- 包含 `API_KEY_SECRET`。
- 敏感字段使用占位符，未发现真实数据库密码、真实 API Key、真实 JWT Secret。

阻塞问题：

- `backend/app/config.py` 实际读取的是 `SERVER_HOST` / `SERVER_PORT`，而 `.env.example` 写的是 `APP_HOST` / `APP_PORT`。这会导致使用者修改 `APP_PORT` 后 `run.py` 不会生效。

必须修复：`.env.example` 与 `config.py` 保持一致，至少补充 `SERVER_HOST`、`SERVER_PORT`，或同步调整说明，避免误导。

## 5. backend/README.md 是否可用于运行说明

**需要继续修改。**

优点：

- 说明了后端用途、技术栈、环境要求、依赖安装、复制 `.env.example`、启动命令、Swagger/ReDoc、数据库连接注意事项和常见问题。
- 未发现真实密钥。

阻塞问题：

1. 数据库初始化步骤只写了：

```sql
SOURCE database/01_create_database.sql;
SOURCE database/04_insert_initial_data.sql;
```

缺少 `02_create_tables.sql`、`03_create_indexes.sql`、`05_create_views.sql`、`06_create_stored_procedures.sql`、`07_test_queries.sql`。按当前说明执行会在未建表时导入初始化数据，无法复现后端运行环境。

2. 健康检查响应示例写成：

```text
/api/health 返回 {"status":"ok"}
/api/health/db 返回 {"database":"connected"}
```

但实际接口使用统一返回格式，应说明为 `{"code":0,"message":"success","data":{...}}`。

## 6. check_backend.py 是否可用

**通过。**

已实际执行：

```bash
cd backend
python3 scripts/check_backend.py
```

结果：

```text
Passed: 49/49
Failed: 0/49
All checks passed!
```

脚本能自动遍历 `backend/app` 下所有 `.py` 文件，执行 `py_compile`，失败时有退出码设计；不依赖数据库和外部 API。

## 7. curl_examples.sh 是否安全且覆盖关键接口

**需要继续修改。**

优点：

- 文件存在。
- 包含 `BASE_URL`、`TOKEN` 占位符。
- 覆盖健康检查、登录、当前用户、项目、项目任务、AI 生成、提交审核、完成审核、成果采用、统计概览等关键路径。
- 未发现真实 Token、真实 API Key 或完整 `sk-` 密钥。

阻塞问题：

1. `POST /api/tasks/{task_id}/generate` 没有请求体，但实际 `GenerateRequest` 要求至少包含：
   - `model_ids`
   - `input_text`
   - 可选 `branch_id`
   - 可选 `prompt_version_id`

2. `POST /api/reviews/{request_id}/complete` 示例分数字段使用 `90`，但实际 Pydantic 限制为 `0 <= score <= 10`，该示例会校验失败。

3. `POST /api/projects` 示例包含 `course_name`，实际 `CreateProjectRequest` 只定义 `project_name`、`project_type`、`description`。建议删除未定义字段，避免测试素材和接口模型不一致。

## 8. route_list.md 是否完整

**基本通过。**

`backend/scripts/route_list.md` 按模块整理了健康检查、认证与用户、项目空间、任务与版本、提示词模板、模型管理、模型调用与日志、人工编辑与批注、审核中心、成果库、统计看板等模块，包含请求方法、路径、功能说明和权限说明。

未发现它列出明显不存在的核心验收接口。

## 9. test_report_material.md 是否适合课程报告

**不通过。**

该文件当前不适合作为课程报告“系统测试与结果分析”素材，原因是混入了大量当前后端不存在或不符合本项目接口契约的内容。

必须修复的错误包括但不限于：

- `POST /api/auth/register` 不存在。
- `/api/users/me` 不存在，当前用户接口是 `GET /api/auth/me`。
- `POST /api/tasks` 不存在，创建任务接口是 `POST /api/projects/{project_id}/tasks`。
- `GET /api/tasks?project_id=1` 不存在，项目任务列表是 `GET /api/projects/{project_id}/tasks`。
- `POST /api/reviews` 不存在，提交审核是 `POST /api/outputs/{output_id}/submit-review`。
- `GET /api/reviews` 不存在，待审核列表是 `GET /api/reviews/pending`。
- `POST /api/artifacts` 不存在，采用成果是 `POST /api/outputs/{output_id}/adopt`。
- `PUT /api/artifacts/{id}/adopt` 不存在。
- `GET /api/statistics/team` 不存在。
- `GET /api/statistics/user/{id}` 不存在。
- 统一返回格式写成 `{"code":200,"message":"操作成功"}` / `{"code":400,...}`，与项目规范 `{"code":0,"message":"success","data":...}` 不一致。
- 多处“截图建议”和“标准测试流程”仍引用上述不存在接口。

这类问题会直接误导课程报告截图和验收操作，必须修复。

## 10. run.py 和 main.py 是否存在启动或导入问题

**通过。**

已审查：

- `backend/run.py`
- `backend/app/main.py`

结果：

- `run.py` 能通过 `uvicorn.run("app.main:app", ...)` 启动。
- `main.py` 注册了当前主要业务 router。
- 未发现重复注册路由或导入不存在模块。
- 未发现 Stage-12 新增业务逻辑。

## 11. Python 语法检查结果

已执行：

```bash
cd backend
python3 scripts/check_backend.py
python3 -m py_compile run.py app/main.py app/config.py app/database.py
```

结果：全部通过。

说明：当前 Ubuntu / WSL 环境无法直接访问 Windows MySQL，本轮未执行真实数据库连接和接口联调，仅执行静态审查和 Python 语法检查。

## 12. 是否发现真实密钥或敏感信息泄露

**未发现真实密钥泄露。**

检查范围：

- `backend/.env.example`
- `backend/README.md`
- `backend/scripts/*`
- `cursor_and_codex_chat/handoff/HANDOFF-012-backend-final-test.md`

未发现真实数据库密码、真实 JWT Secret、真实 API Key、完整 `sk-` 密钥示例或服务器密码。

注意：`test_report_material.md` 中存在 `Test123!`、`your_password` 等示例密码，虽然不是真实密钥，但建议统一改为 `<PLACEHOLDER_PASSWORD>` 或 `<TEST_PASSWORD>`，保持与安全规范一致。

## 13. 是否发现越界修改

本轮审查未发现 Stage-12 实现新业务模块、前端页面、AI 新能力、审核中心/成果库/统计看板新业务功能或数据库结构修改。

但 `git status` 显示 `backend/app/config.py`、`backend/app/database.py`、`backend/app/main.py`、`backend/run.py` 处于修改状态，而 handoff 声明未修改这些文件。请 Cursor 在修复 handoff 中说明这些变更是否为前序历史改动或 Stage-12 修复启动路径所需，避免交接信息不一致。

## 14. 是否允许进入下一阶段

**不允许。**

Stage-12 交付材料仍需修复后再进入 Stage-13。

## 15. 必须修复的问题

1. 修复 `backend/scripts/test_report_material.md`：
   - 删除所有不存在接口；
   - 全部改为当前后端真实路由；
   - 统一返回格式改为 `code: 0 / message: success / data`；
   - 使用“待 Windows MySQL 环境验证”“待补充截图”等谨慎表述，不虚构已通过结果。

2. 修复 `backend/scripts/curl_examples.sh`：
   - 为 `POST /api/tasks/{task_id}/generate` 补充合法 JSON 请求体；
   - 将审核评分改为 0-10 范围；
   - 删除 `POST /api/projects` 中未定义的 `course_name`；
   - 确保所有示例使用占位符，不使用真实密码、Token、API Key。

3. 修复 `backend/README.md`：
   - 数据库初始化命令必须包含 `database/01` 到 `database/07` 的正确顺序，或明确哪些是建库、建表、索引、初始化、视图、存储过程、测试查询；
   - 健康检查响应示例必须使用统一返回格式。

4. 修复 `backend/.env.example`：
   - 补充或修正 `SERVER_HOST`、`SERVER_PORT`，使其与 `backend/app/config.py` 和 `backend/run.py` 实际读取变量一致；
   - 保留 `APP_HOST` / `APP_PORT` 时需说明用途，避免误导。

5. 修复 handoff：
   - 如 `backend/app/main.py`、`backend/app/config.py`、`backend/app/database.py`、`backend/run.py` 处于修改状态，请说明是否为本阶段修改，以及修改原因；
   - 不得声称未修改而工作区实际包含本阶段改动。

## 16. Stage-13 发布情况

未发布 `TASK-013-frontend-base.md`。
