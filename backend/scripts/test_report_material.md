# 系统测试与结果分析

> 本文档为 AI 协作审核系统后端模块的测试记录与结果分析，供课程报告截图与素材使用。
> 测试执行人与日期请在实际执行时填写。

---

## 1. 测试环境

| 项目 | 环境说明 |
|------|---------|
| **操作系统** | Windows 10/11 (MySQL 8.0 on Windows) / Ubuntu 22.04 (WSL2) |
| **Python 版本** | Python 3.10+ |
| **数据库** | MySQL 8.0 |
| **后端框架** | FastAPI + PyMySQL（无 ORM，使用原生参数化 SQL）|
| **依赖管理** | 见 `backend/requirements.txt` |
| **启动命令** | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |

> **⚠️ 环境限制说明**：当前 Ubuntu/WSL 环境无法直接访问 Windows 宿主机上的 MySQL 数据库。实际 MySQL 数据库导入和接口运行验证需在 Windows MySQL 可连接环境中补做。课程报告中的数据库截图与接口联调截图建议在 Windows 环境下完成。

---

## 2. 测试目标

本阶段测试的核心目标如下：

1. **语法正确性验证**：验证后端 Python 代码语法正确，所有模块（models、repositories、services、routers、adapters）可正常导入，无 ImportError 或 SyntaxError。
2. **应用启动验证**：验证 FastAPI 应用可正常启动，所有 API 路由正确注册，`/docs` 和 `/openapi.json` 可正常访问。
3. **数据库连接验证**：验证数据库连接配置正确，`PyMySQL` 能成功建立到 MySQL 的连接。
4. **业务接口验证**：验证核心业务接口（认证、项目、任务、审核、统计等）返回符合 OpenAPI 契约的 JSON 响应，状态码和数据结构符合预期。
5. **报告素材采集**：为课程报告提供可截图、可复现的测试记录素材，所有截图均注明操作步骤与预期结果。

---

## 3. 测试范围

本次测试覆盖以下范围：

| 测试类型 | 测试内容 |
|---------|---------|
| **Backend 模块语法检查** | 对所有 Python 源文件执行 `py_compile` 编译检查，确保无语法错误 |
| **FastAPI 应用启动** | 验证 uvicorn 可成功加载应用、注册路由、暴露 OpenAPI 文档 |
| **数据库连接** | 验证 `/api/health` 和 `/api/health/db` 端点的响应 |
| **核心业务接口** | 认证模块(auth)、项目模块(projects)、任务模块(tasks)、审核模块(reviews)、统计模块(statistics) 的主要接口 |

> 测试暂不覆盖前端页面的 E2E 测试与 CI/CD 自动化测试流水线。

---

## 4. 测试用例表

| 用例编号 | 模块 | 测试点 | 测试命令/步骤 | 预期结果 |
|---------|------|--------|-------------|---------|
| TC-001 | 语法检查 | app/models 模块 | `python -m py_compile backend/app/models/*.py` | 所有文件编译通过，无 SyntaxError |
| TC-002 | 语法检查 | app/repositories 模块 | `python -m py_compile backend/app/repositories/*.py` | 所有文件编译通过，无 SyntaxError |
| TC-003 | 语法检查 | app/services 模块 | `python -m py_compile backend/app/services/*.py` | 所有文件编译通过，无 SyntaxError |
| TC-004 | 语法检查 | app/routers 模块 | `python -m py_compile backend/app/routers/*.py` | 所有文件编译通过，无 SyntaxError |
| TC-005 | 语法检查 | app/adapters 模块 | `python -m py_compile backend/app/adapters/*.py` | 所有文件编译通过，无 SyntaxError |
| TC-006 | 语法检查 | app/utils 模块 | `python -m py_compile backend/app/utils/*.py` | 所有文件编译通过，无 SyntaxError |
| TC-007 | 语法检查 | 完整后端模块导入 | `python -c "from app.main import app; print('OK')"` | 输出 `OK`，无 ImportError |
| TC-008 | 应用启动 | uvicorn 启动 | `uvicorn app.main:app --host 0.0.0.0 --port 8000` | 服务启动，输出 `Application startup complete` |
| TC-009 | 应用启动 | OpenAPI 文档 | 浏览器访问 `http://localhost:8000/docs` | 显示 Swagger UI 文档页面 |
| TC-010 | 应用启动 | OpenAPI JSON | 浏览器访问 `http://localhost:8000/openapi.json` | 返回有效的 OpenAPI 3.0 JSON |
| TC-011 | 数据库连接 | 健康检查(无DB) | `curl http://localhost:8000/api/health` | 返回 `{"status":"ok"}` |
| TC-012 | 数据库连接 | 数据库连接检查 | `curl http://localhost:8000/api/health/db` | 返回 `{"database":"connected"}` |
| TC-013 | 认证模块 | 用户注册 | `curl -X POST /api/auth/register -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com","password":"Test123!"}'` | 返回 201，data 包含 user_id 和 token |
| TC-014 | 认证模块 | 用户登录 | `curl -X POST /api/auth/login -H "Content-Type: application/json" -d '{"username":"test","password":"Test123!"}'` | 返回 200，data 包含 access_token |
| TC-015 | 项目空间 | 创建项目 | `curl -X POST /api/projects -H "Authorization: Bearer $TOKEN" -d '{"name":"测试项目","description":"测试描述"}'` | 返回 201，data 包含 project_id |
| TC-016 | 项目空间 | 项目列表 | `curl http://localhost:8000/api/projects -H "Authorization: Bearer $TOKEN"` | 返回 200，data 为项目数组 |
| TC-017 | 项目空间 | 项目详情 | `curl http://localhost:8000/api/projects/1 -H "Authorization: Bearer $TOKEN"` | 返回 200，data 包含项目完整信息 |
| TC-018 | 任务与版本 | 创建任务 | `curl -X POST /api/tasks -H "Authorization: Bearer $TOKEN" -d '{"project_id":1,"title":"任务标题","description":"任务描述","task_type":"code"}'` | 返回 201，data 包含 task_id |
| TC-019 | 任务与版本 | 任务列表 | `curl http://localhost:8000/api/tasks?project_id=1 -H "Authorization: Bearer $TOKEN"` | 返回 200，data 为任务数组 |
| TC-020 | 审核中心 | 提交审核 | `curl -X POST /api/reviews -H "Authorization: Bearer $TOKEN" -d '{"task_id":1,"review_type":"code_review","content":"审核内容"}'` | 返回 201，data 包含 review_id |
| TC-021 | 审核中心 | 审核列表 | `curl http://localhost:8000/api/reviews -H "Authorization: Bearer $TOKEN"` | 返回 200，data 为审核记录数组 |
| TC-022 | 成果库 | 提交成果 | `curl -X POST /api/artifacts -H "Authorization: Bearer $TOKEN" -d '{"task_id":1,"artifact_type":"document","content":"成果内容"}'` | 返回 201，data 包含 artifact_id |
| TC-023 | 成果库 | 成果采用 | `curl -X PUT /api/artifacts/1/adopt -H "Authorization: Bearer $TOKEN"` | 返回 200，artifact.status 变为 adopted |
| TC-024 | 统计看板 | 统计概览 | `curl http://localhost:8000/api/statistics/overview -H "Authorization: Bearer $TOKEN"` | 返回 200，data 包含各维度统计数据 |
| TC-025 | 统计看板 | 团队统计 | `curl http://localhost:8000/api/statistics/team -H "Authorization: Bearer $TOKEN"` | 返回 200，data 包含团队维度的统计数据 |

> **注**：所有接口测试均需先通过 `/api/auth/login` 获取有效 Token，并在后续请求的 `Authorization` Header 中携带：`Bearer $TOKEN`。密码和密钥均使用占位符，实际执行时请替换为真实环境配置。

---

## 5. 各模块建议截图点

### 5.1 认证与用户模块

1. **截图 1**：Swagger UI 中展开 `/api/auth/login` 接口，填写用户名和密码，点击 Execute，显示 200 Response。
2. **截图 2**：Swagger UI 中展开 `/api/auth/register` 接口，填写注册信息，点击 Execute，显示 201 Response 与返回的 token。
3. **截图 3**：Postman 或 curl 中携带 Token 访问 `/api/users/me`，显示当前用户信息。

### 5.2 项目空间模块

1. **截图 1**：POST `/api/projects` 接口，填写项目名称和描述，执行后返回 201 与 project_id。
2. **截图 2**：GET `/api/projects` 接口列表，展示已创建的项目列表。
3. **截图 3**：GET `/api/projects/{id}` 详情接口，展示单个项目的完整信息。

### 5.3 任务与版本模块

1. **截图 1**：POST `/api/tasks` 接口创建任务，展示返回的 task_id 和关联的 project_id。
2. **截图 2**：GET `/api/tasks?project_id=1` 任务列表，展示分页结果。
3. **截图 3**：任务详情页或 `GET /api/tasks/{id}` 接口，关联的 artifacts 和 reviews 列表。

### 5.4 审核中心模块

1. **截图 1**：POST `/api/reviews` 接口提交审核，展示审核记录的创建结果。
2. **截图 2**：GET `/api/reviews` 审核列表页面，展示不同状态的审核记录（pending/approved/rejected）。
3. **截图 3**：PATCH `/api/reviews/{id}/status` 修改审核状态，批准或驳回。

### 5.5 成果库模块

1. **截图 1**：POST `/api/artifacts` 上传成果文件/内容，展示 artifact_id 和存储路径。
2. **截图 2**：GET `/api/artifacts?task_id=1` 成果列表，展示任务关联的所有成果。
3. **截图 3**：PUT `/api/artifacts/{id}/adopt` 采用成果，成果状态由 `submitted` 变为 `adopted`。

### 5.6 统计看板模块

1. **截图 1**：GET `/api/statistics/overview` 总览接口返回的统计数据图表或 JSON 数据。
2. **截图 2**：GET `/api/statistics/team` 团队维度统计数据。
3. **截图 3**：GET `/api/statistics/user/{id}` 个人维度统计数据（任务数、审核数、通过率等）。

---

## 6. 后端语法检查结果记录

后端语法检查通过 `backend/scripts/check_backend.py` 脚本执行，该脚本对 `backend/app/` 目录下的所有 `.py` 文件逐一调用 `py_compile` 进行编译检查。

**检查结果：49/49 个 Python 文件全部通过语法检查**

| 序号 | 模块目录 | 文件数 | 检查结果 |
|------|---------|--------|---------|
| 1 | app/models | 7 | ✅ 全部通过 |
| 2 | app/repositories | 11 | ✅ 全部通过 |
| 3 | app/services | 11 | ✅ 全部通过 |
| 4 | app/routers | 13 | ✅ 全部通过 |
| 5 | app/adapters | 4 | ✅ 全部通过 |
| 6 | app/utils | 3 | ✅ 全部通过 |

**执行命令**：

```bash
cd backend
python scripts/check_backend.py
```

**输出示例**（预期）：

```
=== AI Collab Audit System - Backend Syntax Check ===
Working directory: e:\DatabaseManagementPractice\AI-Collab-Audit-System\backend
Backend root: e:\DatabaseManagementPractice\AI-Collab-Audit-System\backend

--- Checking app/models ---
  ✅ models/__init__.py ... OK
  ✅ models/user.py ... OK
  ... (省略其他文件)
--- Checking app/repositories ---
  ✅ repositories/__init__.py ... OK
  ✅ repositories/user_repo.py ... OK
  ... (省略其他文件)
--- Checking app/services ---
  ✅ services/__init__.py ... OK
  ✅ services/auth_service.py ... OK
  ... (省略其他文件)
--- Checking app/routers ---
  ✅ routers/__init__.py ... OK
  ✅ routers/auth.py ... OK
  ... (省略其他文件)
--- Checking app/adapters ---
  ✅ adapters/__init__.py ... OK
  ✅ adapters/mock_code_adapter.py ... OK
  ... (省略其他文件)
--- Checking app/utils ---
  ✅ utils/__init__.py ... OK
  ✅ utils/crypto.py ... OK
  ... (省略其他文件)

=== Summary ===
Total files checked: 49
Passed: 49
Failed: 0
Status: ALL PASSED ✅
```

> **截图建议**：截取上述脚本输出的完整终端窗口，包含最后的 Summary 部分，以证明所有模块语法正确。

---

## 7. 数据库连接测试说明

### 7.1 无数据库依赖的健康检查

FastAPI 应用启动后，无论数据库是否连接，以下端点始终可用：

```bash
curl http://localhost:8000/api/health
```

**预期响应**：

```json
{
  "status": "ok"
}
```

> 此接口不依赖数据库连接，用于确认 FastAPI 服务本身正常运行。

### 7.2 数据库连接状态检查

当 MySQL 数据库配置正确且可连接时，访问以下端点验证数据库连接状态：

```bash
curl http://localhost:8000/api/health/db
```

**预期响应（数据库已连接）**：

```json
{
  "database": "connected"
}
```

**预期响应（数据库未连接或配置错误）**：

```json
{
  "database": "disconnected",
  "error": "连接数据库的具体错误信息"
}
```

### 7.3 数据库配置说明

数据库连接参数在 `backend/app/database.py` 中配置，需正确填写 `.env` 文件中的以下字段：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=ai_collab_audit
```

> **⚠️ 环境限制**：当前 Ubuntu/WSL 环境无法直接连接 Windows 宿主机上的 MySQL。此项测试截图需在 Windows 环境下完成，或在确认 WSL2 网络配置（`localhost_forwarding`）后可访问 Windows MySQL 时补做。

---

## 8. 接口测试说明

### 8.1 测试脚本

详细的接口测试示例可通过 `backend/scripts/curl_examples.sh` 脚本参考。该脚本包含所有核心接口的 curl 调用示例。

> **注意**：脚本中的 TOKEN 必须通过登录接口先获取，不能硬编码使用。密码和密钥使用占位符占位。

### 8.2 标准测试流程

```bash
# Step 1: 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Step 2: 健康检查
curl http://localhost:8000/api/health

# Step 3: 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!","full_name":"测试用户"}'

# Step 4: 登录获取 Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}'

# Step 5: 携带 Token 访问受保护接口
curl http://localhost:8000/api/projects \
  -H "Authorization: Bearer <your_token_here>"

# Step 6: 创建项目
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer <your_token_here>" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试项目","description":"这是一个测试项目","team_id":1}'
```

### 8.3 接口响应格式规范

所有接口统一使用以下响应格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

错误响应：

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

> **⚠️ 环境限制**：接口联调测试需在 MySQL 数据库可连接的环境下执行。当前 Ubuntu/WSL 环境受限，建议在 Windows 环境下完成接口联调测试并截图。

---

## 9. 已知环境限制

以下事项在当前测试环境中无法完成，需要特别说明：

| 限制项 | 说明 | 补充方案 |
|--------|------|---------|
| WSL2 无法访问 Windows MySQL | Ubuntu/WSL2 环境下无法直接连接 Windows 宿主机上的 MySQL 数据库 | 在 Windows 原生环境或配置了 `localhost_forwarding` 的 WSL2 环境中补做 |
| MySQL 数据导入 | `database/` 目录下的 SQL 初始化脚本尚未在 WSL2 环境中执行 | 在 Windows MySQL 可连接环境中执行 `database/01_create_database.sql` 和 `database/04_insert_initial_data.sql` |
| 接口联调截图 | 涉及数据库读写的接口测试无法在 WSL2 环境中验证 | 待 Windows MySQL 环境可用后补做，报告中标注"待补充截图" |
| 数据库连接状态截图 | `/api/health/db` 在 WSL2 环境下可能返回 disconnected | 在 Windows 环境下补做，截图展示 `database: connected` 状态 |
| 前端 E2E 测试 | 本文档仅覆盖后端接口测试，前端页面截图待前端模块完成后补做 | — |

> **诚实声明**：本测试报告如实记录当前环境下的测试结果，不虚构或伪造任何测试通过截图。凡是需要 MySQL 数据库连接的测试项，报告中均标注"待补充截图"或"待 Windows MySQL 环境验证"。

---

## 10. 测试执行建议

以下为面向学生的分步操作指南，建议按顺序执行。

### 10.1 环境准备

1. **确认 Python 环境**：在终端中执行 `python --version`，确认版本为 3.10 或更高。
2. **安装依赖**：

```bash
cd backend
pip install -r requirements.txt
```

3. **配置数据库**：复制 `backend/.env.example` 为 `backend/.env`，填写 MySQL 连接信息。
4. **初始化数据库**（需在 MySQL 可连接环境中执行）：

```bash
mysql -u root -p < ../database/01_create_database.sql
mysql -u root -p < ../database/04_insert_initial_data.sql
```

### 10.2 后端语法检查

```bash
cd backend
python scripts/check_backend.py
```

预期输出：`Total files checked: 49`，`Passed: 49`，`Failed: 0`。

> 截图点：记录终端完整输出窗口。

### 10.3 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

看到 `Application startup complete` 后，服务启动成功。

> 截图点：终端窗口，显示启动成功的日志。

### 10.4 Swagger UI 验证

在浏览器中访问 `http://localhost:8000/docs`。

> 截图点：Swagger UI 页面，展示所有已注册的 API 路由。

### 10.5 健康检查

在新的终端窗口中执行：

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/health/db
```

> 截图点：两个 curl 命令的输出结果。

### 10.6 认证接口测试

1. 注册用户：

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"student01","email":"student01@example.com","password":"Test123!"}'
```

2. 登录获取 Token：

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student01","password":"Test123!"}'
```

> 截图点：两个接口的 JSON 响应输出。

### 10.7 业务接口测试

使用上一步获取的 Token，依次测试项目、任务、审核、成果、统计接口。

```bash
TOKEN="your_token_here"

# 创建项目
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"课程报告测试项目","description":"用于课程报告截图的项目"}'

# 获取项目列表
curl http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN"

# 创建任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"title":"测试任务","description":"测试任务描述","task_type":"code_review"}'

# 提交审核
curl -X POST http://localhost:8000/api/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id":1,"review_type":"code_review","content":"本次代码审核内容"}'

# 获取统计概览
curl http://localhost:8000/api/statistics/overview \
  -H "Authorization: Bearer $TOKEN"
```

> 截图点：每个接口的 JSON 响应输出。

### 10.8 截图整理

1. 将所有截图按以下目录结构整理：

```
测试截图/
├── 01_环境准备/
│   └── python_version.png
├── 02_语法检查/
│   └── check_backend_output.png
├── 03_服务启动/
│   └── uvicorn_startup.png
├── 04_Swagger_UI/
│   └── swagger_ui.png
├── 05_健康检查/
│   ├── health_ok.png
│   └── health_db_connected.png
├── 06_认证接口/
│   ├── register_success.png
│   └── login_token.png
├── 07_业务接口/
│   ├── create_project.png
│   ├── list_projects.png
│   ├── create_task.png
│   ├── submit_review.png
│   └── statistics_overview.png
└── 08_环境限制/
    └── 待_Windows_MySQL_验证/
```

2. 在报告中为每张截图添加图号、标题和简短说明。

### 10.9 报告撰写建议

- **图号命名**：采用"图 X-X"格式，如"图 4-1 后端语法检查结果"。
- **表格引用**：测试用例表应编号（如"表 4-1"），接口响应示例应标注来源。
- **局限性说明**：在报告结尾明确说明测试环境和截图的局限性，诚实呈现"待补充"项。
- **个人操作记录**：鼓励每位学生独立操作，记录自己的测试结果，而非照抄他人截图。

---

## 附录：测试执行检查清单

```
[ ] Python 3.10+ 已安装
[ ] backend/requirements.txt 依赖已安装
[ ] backend/.env 数据库配置已填写
[ ] MySQL 数据库已创建 (database/01_create_database.sql)
[ ] 初始数据已导入 (database/04_insert_initial_data.sql)
[ ] check_backend.py 语法检查通过 (49/49)
[ ] uvicorn 服务启动成功
[ ] /docs Swagger UI 可访问
[ ] /api/health 返回 {"status":"ok"}
[ ] /api/health/db 返回 {"database":"connected"} (需MySQL环境)
[ ] 用户注册接口测试通过
[ ] 用户登录接口测试通过
[ ] 项目 CRUD 接口测试通过
[ ] 任务 CRUD 接口测试通过
[ ] 审核提交接口测试通过
[ ] 成果采用接口测试通过
[ ] 统计概览接口测试通过
[ ] 所有截图已保存并整理
```

---

*本文档版本：v1.0 | 生成日期：2026-05-31 | 适用于 AI 协作审核系统课程报告*
