# TASK-002：Stage-02 FastAPI 后端基础框架

## 任务状态

已完成。

## 背景

Stage-01 数据库脚本已通过 Codex 第三轮静态审查。实际 MySQL 导入验证后续将在 Windows MySQL 环境中补做，不阻塞 Stage-02 基础框架开发。

本任务只完成 FastAPI 后端基础框架，不实现任何业务模块。

## 必须遵守

1. `docs/00_AI开发总控规范.md`
2. `docs/01_数据库Schema冻结说明.md`
3. `docs/02_接口契约与页面清单.md`
4. `docs/03_阶段任务卡与验收清单.md`

禁止自行修改技术栈。禁止修改数据库 Schema。禁止跳到登录、项目、任务或 AI 调用业务。

## 允许修改文件

```text
backend/app/main.py
backend/app/config.py
backend/app/database.py
backend/app/utils/response.py
backend/app/utils/exceptions.py
backend/requirements.txt
backend/run.py
```

如果上述文件不存在，可以创建；如果已存在，只能围绕本任务目标做最小必要修改。

## 禁止修改

```text
database/*
frontend/*
docs/01_数据库Schema冻结说明.md
```

除上述允许文件外，不要修改其他后端业务文件、路由文件、服务文件、仓储文件或适配器文件。

## Stage-02 只允许实现

1. FastAPI 项目启动；
2. 数据库连接；
3. 统一返回格式；
4. 健康检查接口 `/api/health`；
5. 基础异常处理；
6. 配置从环境变量读取。

## Stage-02 禁止实现

1. 登录业务；
2. 用户管理；
3. 项目管理；
4. 任务管理；
5. AI 调用；
6. 前端页面；
7. 修改数据库脚本；
8. 新增未确认依赖或大型框架；
9. 使用 ORM 替代后续核心 SQL 设计。

## 接口要求

健康检查接口：

```http
GET /api/health
```

成功返回必须使用统一格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "database": "connected"
  }
}
```

如果数据库连接失败，应仍返回统一错误结构，并包含可用于排查的非敏感信息。不得输出数据库密码、API Key 或其他密钥。

## 配置要求

配置必须从环境变量读取，至少包括：

```text
APP_NAME
APP_ENV
API_PREFIX
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
```

可提供安全默认值，但不得在代码中硬编码真实密码。

## 数据库连接要求

1. 使用 MySQL 驱动连接 `ai_collab_audit_system`；
2. 提供获取连接的方法；
3. 提供健康检查用的轻量查询，例如 `SELECT 1`；
4. 连接异常必须被基础异常处理捕获；
5. 不在本阶段实现 Repository 层业务 SQL。

## 验收标准

1. 后端服务可以启动；
2. `GET /api/health` 返回统一响应；
3. 数据库连接配置来自环境变量；
4. 数据库不可用时有统一错误响应；
5. `requirements.txt` 依赖明确且不过度；
6. 没有实现登录、用户、项目、任务、AI 调用等业务接口；
7. 没有修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`。

## 建议运行方式

Cursor 完成后应在 handoff 中给出实际命令，例如：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

以及健康检查测试方式：

```bash
curl http://127.0.0.1:8000/api/health
```

## Handoff 要求

完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-002-backend-base.md`

必须包含：

1. 修改文件列表；
2. 实现说明；
3. 依赖说明；
4. 环境变量说明；
5. 启动步骤；
6. `/api/health` 测试结果；
7. 数据库连接测试结果；
8. 未完成事项和风险说明。
