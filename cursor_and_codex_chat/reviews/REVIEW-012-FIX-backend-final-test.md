# REVIEW-012-FIX: Stage-12 后端联调材料修复复审报告

## 1. 审查结论

**需要继续修改**

本轮重点复审 `REVIEW-012-backend-final-test.md` 中的 4 个阻塞问题。结论如下：

- 4 个上轮阻塞问题已基本修复；
- 后端 Python 语法检查通过；
- 未发现真实密钥泄露；
- 未发现 Stage-13 前端内容或新业务模块；
- 但 `backend/scripts/test_report_material.md` 中仍存在会导致课程测试照文档执行失败的新问题：创建任务示例请求体与真实接口模型不一致。

因此本轮暂不允许进入 Stage-13，不发布 `TASK-013-frontend-base.md`。

## 2. 4 个阻塞问题是否全部修复

### 2.1 `test_report_material.md` 是否清理不存在接口和错误返回格式

**旧阻塞点已修复。**

检查结果：

- 未再发现 `/api/auth/register`。
- 未再发现 `POST /api/tasks`。
- 未再发现 `POST /api/reviews`。
- 未再发现 `GET /api/statistics/team`。
- 未再发现 `GET /api/statistics/user/{id}`。
- 未再发现把统一成功格式写成 `code: 200` 或 `message: 操作成功`。
- 成功响应示例已改为：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 保留了当前环境限制说明，明确 Ubuntu / WSL 暂时无法直接访问 Windows MySQL，真实数据库联调和截图需在 Windows MySQL 可连接环境中补做。

### 2.2 `curl_examples.sh` 请求体是否符合真实接口模型

**已修复。**

检查结果：

- `POST /api/tasks/{task_id}/generate` 已包含合法 JSON body：
  - `model_ids`
  - `input_text`
  - `branch_id`
  - `prompt_version_id`
- `POST /api/reviews/{request_id}/complete` 的评分已改为 0-10 范围，未再使用 90、95、100 等百分制评分。
- `POST /api/projects` 请求体已移除未定义字段 `course_name`。
- 示例中未发现真实密码、真实 Token、真实 API Key，均使用占位符。

### 2.3 `README` 数据库初始化步骤和健康检查响应是否修复

**已修复。**

检查结果：

- `backend/README.md` 已按顺序列出：
  - `database/01_create_database.sql`
  - `database/02_create_tables.sql`
  - `database/03_create_indexes.sql`
  - `database/04_insert_initial_data.sql`
  - `database/05_create_views.sql`
  - `database/06_create_stored_procedures.sql`
  - `database/07_test_queries.sql`
- 已说明 Step 1 首次建库执行，Step 2-7 在 `ai_collab_audit_system` 数据库中按顺序执行。
- 健康检查响应示例已改为统一返回格式 `code = 0`。
- 未再使用裸 `{"status":"ok"}` 作为接口完整响应。
- 保留 Windows MySQL / WSL 连接限制说明，未虚构数据库导入和接口联调已全部成功。

### 2.4 `.env.example` 是否与 `config.py` / `run.py` 对齐

**已修复。**

检查结果：

- `.env.example` 已移除容易误导的 `APP_HOST` / `APP_PORT`。
- 已改为 `SERVER_HOST` / `SERVER_PORT`，与 `backend/app/config.py` 中 `alias="SERVER_HOST"` / `alias="SERVER_PORT"` 一致。
- 数据库环境变量与当前配置读取保持一致。
- `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_EXPIRE_MINUTES` 存在。
- `API_KEY_SECRET` 存在。
- 所有敏感值均为占位符，未发现真实数据库密码、真实 JWT Secret、真实 API Key。

## 3. 是否发现新问题

**发现 1 个需要继续修改的问题。**

`backend/scripts/test_report_material.md` 中创建任务示例仍使用不存在于真实请求模型中的字段：

```json
{"task_name":"测试任务","task_type":"code_review"}
```

以及：

```json
{"task_name":"需求分析任务","task_type":"document_writing"}
```

但真实接口 `POST /api/projects/{project_id}/tasks` 的 `CreateTaskRequest` 定义为：

```python
task_type_id: int
title: str
description: Optional[str]
assignee_id: Optional[int]
priority: Optional[str]
due_date: Optional[str]
```

如果课程测试人员照 `test_report_material.md` 执行，创建任务接口会因为缺少 `task_type_id` 和 `title` 而失败。因此该报告素材仍不能完全作为可复现测试说明使用。

必须将 `test_report_material.md` 中所有创建任务示例改为真实字段，例如：

```json
{
  "task_type_id": 1,
  "title": "需求分析任务",
  "description": "生成课程报告需求分析部分",
  "assignee_id": 2,
  "priority": "normal",
  "due_date": "2026-06-10 23:59:59"
}
```

如不确定 `assignee_id`，可省略可选字段，但必须保留 `task_type_id` 和 `title`。

## 4. 是否发现真实密钥或敏感信息泄露

**未发现真实密钥泄露。**

检查范围：

- `backend/.env.example`
- `backend/README.md`
- `backend/scripts/curl_examples.sh`
- `backend/scripts/test_report_material.md`
- `backend/scripts/route_list.md`
- `cursor_and_codex_chat/handoff/HANDOFF-012-FIX-backend-final-test.md`

未发现真实数据库密码、真实 JWT Secret、真实 API Key、完整 `sk-` 密钥或服务器密码。

说明：`your_token_here` 属于占位符，不视为真实 Token。

## 5. 是否发现越界修改

未发现 Stage-13 前端内容、新业务模块、新业务接口、数据库结构修改或前端页面实现。

说明：

- 当前工作区仍显示 `database/` 存在历史未提交改动，本轮 handoff 声明未修改 `database/*`。
- 当前工作区仍显示 `backend/app/config.py`、`backend/app/database.py`、`backend/app/main.py`、`backend/run.py` 处于修改状态；handoff 声明本轮未修改这些文件。该状态与前序阶段历史改动一致，本轮未发现新增业务逻辑。

## 6. Python 语法和脚本检查

已执行：

```bash
cd backend
python3 scripts/check_backend.py
python3 -m py_compile run.py app/main.py app/config.py app/database.py
```

结果：

- `check_backend.py`：49/49 通过，失败 0。
- 额外 `py_compile`：通过。

说明：当前 Ubuntu / WSL 环境无法直接访问 Windows MySQL，本轮未执行真实数据库连接和接口联调；这不作为 Stage-12 阻塞项。

## 7. 是否允许进入 Stage-13

**不允许。**

原因：`test_report_material.md` 仍有创建任务请求体与真实接口模型不一致的问题，影响课程报告素材的可复现性。

## 8. 剩余必须修复的问题

仅剩 1 个问题：

修复 `backend/scripts/test_report_material.md` 中所有 `POST /api/projects/{project_id}/tasks` 的请求体示例：

- 不得使用 `task_name`；
- 不得使用 `task_type`；
- 必须使用真实字段 `task_type_id` 和 `title`；
- 可选字段使用 `description`、`assignee_id`、`priority`、`due_date`；
- 相关预期结果和截图说明中也应使用 `title` / `task_id`，不要再写 `task_name`。

## 9. Stage-13 发布情况

未发布 `cursor_and_codex_chat/tasks/todo/TASK-013-frontend-base.md`。
