# AI-Collab-Audit-System — Backend

> 智研协作系统后端 API 服务。基于 FastAPI + PyMySQL，提供项目任务管理、AI 调用审计与质量审核的 RESTful 接口。

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI >= 0.110.0 |
| ASGI 服务器 | uvicorn >= 0.27.0 |
| 数据库驱动 | PyMySQL >= 1.1.0（原生参数化 SQL，无 ORM）|
| 配置管理 | pydantic-settings >= 2.1.0 |
| JWT 认证 | PyJWT >= 2.8.0 |
| 密码哈希 | passlib[bcrypt] >= 1.7.4 |
| API Key 加密 | cryptography >= 42.0.0（AES-GCM）|
| Python 版本 | 3.10+ |

## 环境要求

- Python 3.10+
- MySQL 8.0+

> **注意**：本后端连接 Windows 主机上的 MySQL 数据库（默认 `127.0.0.1:3306`）。如果从 WSL2 访问 Windows MySQL，MySQL 服务必须监听 `0.0.0.0` 或 WSL 虚拟网卡的 IP，或在 Windows 防火墙放行 3306 端口。

## 安装与启动

### 1. 克隆并进入目录

```powershell
cd AI-Collab-Audit-System/backend
```

### 2. 创建虚拟环境（Windows PowerShell）

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

（Linux/macOS/WSL）

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env`，并填写实际值：

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS/WSL
```

`.env` 示例内容：

```env
APP_NAME=AI-Collab-Audit-System
APP_ENV=development
API_PREFIX=/api

# 服务器配置（启动端口）
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<YOUR_DB_PASSWORD>
DB_NAME=ai_collab_audit_system
DB_CHARSET=utf8mb4

JWT_SECRET_KEY=<YOUR_JWT_SECRET_KEY>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

API_KEY_SECRET=<YOUR_32_BYTE_SECRET_BASE64_OR_HEX>
```

> **重要**：`.env` 文件包含敏感信息，禁止提交到版本控制。

### 5. 初始化数据库

在 MySQL 中按以下顺序执行建库建表脚本：

```bash
# Step 1: 创建数据库
mysql -u root -p < ../database/01_create_database.sql

# Step 2: 创建数据表
mysql -u root -p ai_collab_audit_system < ../database/02_create_tables.sql

# Step 3: 创建索引
mysql -u root -p ai_collab_audit_system < ../database/03_create_indexes.sql

# Step 4: 导入初始数据
mysql -u root -p ai_collab_audit_system < ../database/04_insert_initial_data.sql

# Step 5: 创建视图
mysql -u root -p ai_collab_audit_system < ../database/05_create_views.sql

# Step 6: 创建存储过程
mysql -u root -p ai_collab_audit_system < ../database/06_create_stored_procedures.sql

# Step 7: 执行测试查询（可选）
mysql -u root -p ai_collab_audit_system < ../database/07_test_queries.sql
```

> **说明**：Step 1 只在首次建库时执行一次；Step 2-7 均在 `ai_collab_audit_system` 数据库中执行。必须按顺序执行，否则后续步骤可能因依赖缺失而失败。

### 6. 启动后端

```bash
python run.py
```

或直接使用 uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：

- API 文档（Swagger UI）：http://127.0.0.1:8000/docs
- ReDoc 文档：http://127.0.0.1:8000/redoc
- 健康检查：http://127.0.0.1:8000/api/health

**统一响应格式**：所有接口均使用以下 JSON 格式：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

健康检查响应示例：

```json
// GET /api/health
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "service": "AI-Collab-Audit-System",
    "env": "development"
  }
}

// GET /api/health/db
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "database": "connected",
    "server_version": "8.0.x"
  }
}
```

## 数据库连接说明

### Windows 环境

直接连接本地 MySQL，`.env` 配置：

```
DB_HOST=127.0.0.1
DB_PORT=3306
```

### WSL2 / Ubuntu 环境

WSL2 访问 Windows MySQL 有以下两种方式：

**方式一：通过 localhost（MySQL 需监听 WSL 网卡）**

在 Windows 的 MySQL 配置文件 `my.cnf`（或 `my.ini`）中添加：

```ini
[mysqld]
bind-address = 0.0.0.0
```

重启 MySQL 服务后，在 WSL2 中使用 Windows 主机 IP（例如 `172.x.x.x`）连接：

```env
DB_HOST=172.x.x.x
```

查询 Windows 主机 IP：

```bash
# 在 WSL2 中
ip route | grep default
```

**方式二：通过 Windows 防火墙放行后用 localhost**

确保 Windows 防火墙允许 MySQL 端口（默认 3306）入站，或在 WSL2 中直接用 Windows 主机 IP。

### 验证数据库连接

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/db
```

- `/api/health` 返回 `{"code":0,"message":"success","data":{"status":"ok"}}` — 服务正常
- `/api/health/db` 返回 `{"code":0,"message":"success","data":{"database":"connected"}}` — 数据库连接正常
  - 当前环境无 MySQL 时返回 `{"code":5002,"message":"...","data":{"database":"disconnected"}}`

## 后端整体语法检查

运行 `backend/scripts/check_backend.py`（自动检查所有 `.py` 文件）：

```bash
python scripts/check_backend.py
```

当前结果：**49/49 文件全部通过**。

## API 测试脚本

运行 `backend/scripts/curl_examples.sh` 中的 curl 示例：

> **注意**：首次使用前需要先登录获取 Token，再替换脚本中的 `$TOKEN` 变量。

```bash
# 1. 登录获取 Token（将 <PLACEHOLDER_PASSWORD> 替换为实际密码）
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 2. 将返回的 access_token 填入 curl_examples.sh 的 TOKEN 变量
# 3. 然后执行各接口测试
```

## 常见问题

### Q1: `pydantic_settings` 导入失败

确保安装 `pydantic-settings`：

```bash
pip install pydantic-settings
```

### Q2: MySQL 连接被拒绝

- 确认 MySQL 服务已启动
- 确认 `DB_HOST` / `DB_PORT` 正确
- 确认用户名和密码正确
- WSL2 用户：确认 Windows MySQL 监听地址为 `0.0.0.0` 或 WSL 网卡 IP

### Q3: `cryptography` 安装失败

在 Windows 上可能需要 Microsoft Visual C++ Build Tools：

```powershell
pip install cryptography --only-binary :all:
```

### Q4: `pip install` 速度慢

使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 目录结构

```
backend/
├── app/
│   ├── adapters/          # AI 模型调用适配器（Mock）
│   ├── repositories/       # 数据访问层（原生 SQL + PyMySQL）
│   ├── routers/            # API 路由定义
│   ├── services/           # 业务逻辑层
│   ├── utils/              # 工具模块（Token、JWT、密码、加密、异常）
│   ├── config.py           # 配置管理（环境变量）
│   ├── database.py         # 数据库连接管理
│   └── main.py             # FastAPI 应用入口
├── scripts/
│   ├── check_backend.py    # 后端整体语法检查脚本
│   ├── curl_examples.sh    # 关键接口 curl 测试示例
│   ├── route_list.md       # API 路由清单
│   └── test_report_material.md  # 测试报告素材
├── .env.example            # 环境变量示例
├── requirements.txt        # Python 依赖清单
└── run.py                  # 启动入口
```

## 安全说明

- 所有敏感配置（数据库密码、JWT 密钥、API Key 加密密钥）通过 `.env` 环境变量读取，不硬编码。
- `.env.example` 不包含任何真实密钥，仅作配置模板。
- API Key 在数据库中以 AES-GCM 加密存储，不明文保存。
- 路由按角色分级授权（公开 / 登录用户 / 管理员 / 项目 Owner/Leader）。
