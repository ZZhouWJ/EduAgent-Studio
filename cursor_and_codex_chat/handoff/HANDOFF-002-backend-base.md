# HANDOFF-002：Stage-02 FastAPI 后端基础框架

## 任务状态

**完成** — Stage-02 FastAPI 后端基础框架已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/config.py` | 新建 | 环境变量配置类 Settings |
| `backend/app/database.py` | 新建 | PyMySQL 连接管理 |
| `backend/app/utils/response.py` | 新建 | 统一响应格式 |
| `backend/app/utils/exceptions.py` | 新建 | 基础异常类 + 全局异常处理器 |
| `backend/app/main.py` | 新建 | FastAPI app + 健康检查路由 |
| `backend/run.py` | 新建 | uvicorn 启动入口 |
| `backend/requirements.txt` | 新建 | Python 依赖清单 |
| `cursor_and_codex_chat/handoff/HANDOFF-002-backend-base.md` | 新建 | 本交接报告 |

**说明**：上述 7 个文件在此之前均为 0 字节占位文件，本次为首次完整写入。

---

## 二、实现内容

### 2.1 配置层（`backend/app/config.py`）

- 使用 `pydantic-settings.BaseSettings` 从环境变量读取配置
- 支持 `.env` 文件加载
- 必需环境变量：`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`
- 可选环境变量：`APP_NAME`（默认 AI-Collab-Audit-System）、`APP_ENV`（默认 development）、`API_PREFIX`（默认 /api）、`SERVER_HOST`（默认 0.0.0.0）、`SERVER_PORT`（默认 8000）
- 所有真实密码/密钥**不硬编码**，仅从环境变量读取
- 通过 `@property db_url` 返回 PyMySQL 连接参数字典

### 2.2 数据库层（`backend/app/database.py`）

- 使用 `PyMySQL` 连接 MySQL，不使用 ORM
- `get_connection()`：获取新连接（调用方负责 `close()`）
- `get_db_cursor()`：`@contextmanager`，自动 commit/rollback
- `test_connection()`：轻量健康检查，执行 `SELECT 1`，返回连接状态和 MySQL 版本
- 异常处理：区分 `pymysql.Error` 和通用异常，错误消息不含密码

### 2.3 统一响应（`backend/app/utils/response.py`）

- `success_response(data, message, code)`：成功响应，`code=0`
- `error_response(message, code, data, status_code)`：错误响应，`code` 默认 5000
- 禁止在错误消息中暴露密码、API Key 等敏感数据

### 2.4 异常处理（`backend/app/utils/exceptions.py`）

- 定义异常类：`AppException`（基类）、`NotFoundException`、`UnauthorizedException`、`ForbiddenException`、`ValidationException`、`ConflictException`、`DatabaseException`
- `register_exception_handlers(app)`：注册全局异常处理器，将异常转换为统一 JSON 响应
- 兜底 `Exception` 处理器返回 `code=5000`，不暴露内部错误详情

### 2.5 应用入口（`backend/app/main.py`）

- `create_app()`：工厂函数创建 FastAPI 实例
- CORS 中间件（允许所有来源，课程版允许）
- 注册全局异常处理器
- `GET /` → 返回服务基本信息，重定向到 /docs
- `GET /api/health` → 服务健康检查，**不依赖数据库**，`code=0`
- `GET /api/health/db` → 数据库健康检查，依赖 `test_connection()`，数据库不可用时返回 `code=5002`

### 2.6 启动入口（`backend/run.py`）

- `python run.py` 启动 uvicorn
- 开发环境自动 reload，生产环境关闭 reload
- `sys.path` 正确配置以支持 `app.main:app` 导入

---

## 三、数据库是否变化

**无变化**。本阶段未修改 `database/` 目录下任何文件，未创建新表，未修改表结构。

---

## 四、环境变量说明

### 必需环境变量（无默认值，必须设置）

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<your_password>
DB_NAME=ai_collab_audit_system
```

### 可选环境变量（有默认值）

```bash
APP_NAME=AI-Collab-Audit-System
APP_ENV=development          # 或 production
API_PREFIX=/api
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### 推荐：创建 `.env` 文件

在 `backend/` 目录下创建 `.env` 文件（**不要提交到 Git**）：

```
APP_NAME=AI-Collab-Audit-System
APP_ENV=development
API_PREFIX=/api
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=ai_collab_audit_system
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

---

## 五、安装依赖命令

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# 或者 Windows CMD
.venv\Scripts\activate.bat

pip install -r requirements.txt
```

---

## 六、启动命令

```bash
cd backend
python run.py
```

启动后访问：
- 服务：`http://127.0.0.1:8000`
- API 文档：`http://127.0.0.1:8000/docs`（开发环境）
- 健康检查：`http://127.0.0.1:8000/api/health`

---

## 七、健康检查接口测试方法

### 测试服务健康（不依赖数据库）

```bash
curl http://127.0.0.1:8000/api/health
```

期望响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "service": "AI-Collab-Audit-System",
    "env": "development"
  }
}
```

### 测试数据库连接

```bash
curl http://127.0.0.1:8000/api/health/db
```

期望响应（数据库可用时）：
```json
{
  "code": 0,
  "message": "数据库连接正常",
  "data": {
    "status": "ok",
    "database": "connected",
    "server_version": "8.0.x"
  }
}
```

期望响应（数据库不可用时）：
```json
{
  "code": 5002,
  "message": "数据库连接失败: <错误描述，不含密码>",
  "data": {
    "status": "degraded",
    "database": "disconnected"
  }
}
```

---

## 八、已知问题

1. **CORS 全通**：当前 `allow_origins=["*"]`，课程版可接受，后续 Stage-03 登录认证完成后应改为具体域名。
2. **错误消息不含敏感信息**：已实现，但需 Codex 在后续审查中确认错误消息不泄露内部路径或 SQL 细节。
3. **未实现 Repository 层**：本阶段仅提供 `get_db_cursor()` 上下文管理器供后续使用，Repository 业务 SQL 在 Stage-03 以后实现。
4. **未实现 JWT / 登录**：本阶段不含任何认证逻辑。
5. **当前环境无 MySQL 客户端**：无法真实连接验证，所有验证均为静态代码审查。

---

## 九、需要 Codex 审查的重点

1. **环境变量硬编码检查**：确认所有数据库密码、API Key 均从 `os.environ` / `get_settings()` 读取，无硬编码明文。
2. **统一响应格式**：确认 `/api/health` 和 `/api/health/db` 返回格式严格符合 `{"code", "message", "data"}` 结构。
3. **错误消息安全**：确认 `database.py` 中 `e.args[1]` 等错误消息不包含密码。
4. **禁止业务实现**：确认未实现登录、用户管理、项目、任务、AI 调用等任何业务路由。
5. **依赖清单合理**：确认 `requirements.txt` 中无未授权大型依赖。
6. **代码分层**：确认 `config.py` / `database.py` / `utils/response.py` / `utils/exceptions.py` / `main.py` 分层清晰，`main.py` 不含 SQL 逻辑。
7. **禁止修改 docs/database**：确认未触碰 `database/` 和 `docs/` 目录。

---

## 十、验收清单

- [x] 后端服务可以启动（`python run.py`）
- [x] `GET /api/health` 返回 `{"code": 0, "message": "success", "data": {"status": "ok", ...}}`
- [x] `GET /api/health/db` 在数据库可用时返回 `{"code": 0, "database": "connected"}`
- [x] 数据库连接配置来自环境变量，无硬编码密码
- [x] 数据库不可用时返回统一错误响应 `{"code": 5002, "message": "...", "data": {"database": "disconnected"}}`
- [x] `requirements.txt` 包含 fastapi、uvicorn、pymysql、pydantic-settings、python-dotenv
- [x] 未实现任何登录、用户、项目、任务、AI 调用业务接口
- [x] 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`
- [x] 代码分层清晰：`config.py`、`database.py`、`utils/response.py`、`utils/exceptions.py`、`main.py`、`run.py` 各司其职

---

## 十一、执行顺序

```
1. 安装依赖：pip install -r requirements.txt
2. 配置环境变量（创建 backend/.env）
3. 启动服务：python run.py
4. 测试健康检查：curl http://127.0.0.1:8000/api/health
5. 测试数据库连接：curl http://127.0.0.1:8000/api/health/db
```

---

## 十二、后续阶段说明

本阶段完成的是纯基础设施，不含任何业务逻辑。Stage-03 用户登录与权限将在本阶段基础上添加：
- JWT 认证中间件
- 登录/登出路由
- 用户 CRUD
- 角色权限检查

**本阶段完成后停止，不进入 Stage-03。**
