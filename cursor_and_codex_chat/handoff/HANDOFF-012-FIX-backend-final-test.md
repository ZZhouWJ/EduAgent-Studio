# HANDOFF-012-FIX：Stage-12 文档修复版

## 任务状态

**完成**。

---

## 一、Codex 未通过原因

`REVIEW-012-backend-final-test.md` 指出 4 个阻塞问题：

1. `test_report_material.md` 混入大量当前后端不存在的接口，且统一返回格式错误（`code:200` 而非 `code:0`）
2. `curl_examples.sh` 部分请求体不符合真实接口模型（generate 无 body、审核评分 90 超范围、project 含未定义字段 `course_name`）
3. `README.md` 数据库初始化步骤不完整（只有 01 和 04），健康检查响应未用统一格式
4. `.env.example` 使用 `APP_HOST`/`APP_PORT`，但 `config.py` 实际读取的是 `SERVER_HOST`/`SERVER_PORT`

---

## 二、本次修复的问题列表

| # | 问题 | 修复文件 | 修复内容 |
|---|------|----------|----------|
| 1 | `.env.example` 使用错误的变量名 | `backend/.env.example` | 移除 `APP_HOST`/`APP_PORT`，补充 `SERVER_HOST`/`SERVER_PORT` |
| 2 | curl 请求体不符合接口模型 | `backend/scripts/curl_examples.sh` | 为 generate 补充 body；审核评分改为 0-10；删除 `course_name` |
| 3 | 测试用例包含不存在接口 | `backend/scripts/test_report_material.md` | 删除所有不存在接口（register、POST /tasks、POST /reviews、PUT /artifacts、GET /statistics/team 等），替换为真实路由，统一格式改为 `code:0` |
| 4 | README 数据库步骤不完整 | `backend/README.md` | 补齐 01-07 全部脚本及执行顺序；补充统一响应格式说明和示例 |

---

## 三、本次修改文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/.env.example` | 修改 | 移除 APP_HOST/APP_PORT，补充 SERVER_HOST/SERVER_PORT |
| `backend/scripts/curl_examples.sh` | 修改 | 3 处请求体修正 |
| `backend/scripts/test_report_material.md` | 重写 | 清除不存在接口，统一格式修正 |
| `backend/README.md` | 修改 | 补齐数据库脚本 01-07，统一响应格式 |
| `cursor_and_codex_chat/handoff/HANDOFF-012-FIX-backend-final-test.md` | 新建 | 本次交接文档 |

---

## 四、test_report_material.md 清理了哪些不存在接口

以下接口已从文件中删除或替换：

| 已删除的不存在接口 | 替换为真实接口 |
|------------------|--------------|
| `POST /api/auth/register` | 删除（登录已有 `POST /api/auth/login`）|
| `GET /api/users/me` | `GET /api/auth/me` |
| `POST /api/tasks` | `POST /api/projects/{project_id}/tasks` |
| `GET /api/tasks?project_id=1` | `GET /api/projects/{project_id}/tasks` |
| `POST /api/reviews` | `POST /api/outputs/{output_id}/submit-review` |
| `GET /api/reviews` | `GET /api/reviews/pending` |
| `POST /api/artifacts` | `POST /api/outputs/{output_id}/adopt` |
| `PUT /api/artifacts/{id}/adopt` | `POST /api/outputs/{output_id}/adopt` |
| `GET /api/statistics/team` | `GET /api/statistics/member-contributions` |
| `GET /api/statistics/user/{id}` | 删除（统计概览已有 `GET /api/statistics/overview`）|
| `PATCH /api/reviews/{id}/status` | `POST /api/reviews/{request_id}/complete` |

测试用例从 25 条调整为 27 条，全部基于 `route_list.md` 中已注册的 71 个真实端点。

---

## 五、统一返回格式是否已改为 code=0

**是**。全文所有响应示例已统一改为：

```json
// 成功
{
  "code": 0,
  "message": "success",
  "data": { ... }
}

// 错误示例
{
  "code": 4001,
  "message": "权限不足",
  "data": null
}
```

不再出现 `code: 200` 或 `message: "操作成功"` 作为系统统一格式。

---

## 六、curl_examples.sh 哪些请求体已修正

1. **`POST /api/tasks/{task_id}/generate`**：补充了完整 JSON body
   ```json
   {
     "model_ids": [1],
     "input_text": "请生成数据库课程报告需求分析部分",
     "branch_id": 1,
     "prompt_version_id": 1
   }
   ```

2. **`POST /api/reviews/{request_id}/complete`**：评分改为 0-10 范围
   ```json
   {
     "review_status": "approved",
     "accuracy_score": 9,
     "completeness_score": 8.5,
     "logic_score": 9,
     "format_score": 8,
     "usability_score": 9,
     "risk_score": 1,
     "review_comment": "整体可用，建议补充非功能需求。",
     "issue_tag_ids": [1]
   }
   ```

3. **`POST /api/projects`**：删除未定义字段 `course_name`
   ```json
   {
     "project_name": "数据库课程设计项目",
     "project_type": "course_project",
     "description": "数据库管理实务结课设计"
   }
   ```

---

## 七、README 数据库初始化步骤是否补齐 01-07

**是**。`backend/README.md` 第 5 节"初始化数据库"已补齐：

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
mysql -u root -p ai_collab_udit_system < ../database/07_test_queries.sql
```

并添加了说明：Step 1 只在首次建库执行一次，Step 2-7 均在 `ai_collab_audit_system` 数据库中执行，必须按顺序。

---

## 八、README 健康检查响应是否已统一格式

**是**。`backend/README.md` 已新增"统一响应格式"小节，包含：

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

同时修正了"验证数据库连接"小节的说明文字，不再出现裸 JSON 格式。

---

## 九、.env.example 是否已使用 SERVER_HOST / SERVER_PORT

**是**。`backend/.env.example` 已修正：

```env
# 服务器配置（启动端口）
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

与 `backend/app/config.py` 中 `Settings` 类实际读取的 `alias="SERVER_HOST"` / `alias="SERVER_PORT"` 完全一致。

---

## 十、是否修改业务代码

**否**。本次仅修改了文档和脚本文件，未修改：

- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/run.py`
- `backend/app/routers/*`
- `backend/app/services/*`
- `backend/app/repositories/*`

---

## 十一、是否修改 database

**否**。

---

## 十二、是否修改 frontend

**否**。

---

## 十三、是否实现 Stage-13

**否**。

---

## 十四、Python 检查命令

```bash
cd backend
python scripts/check_backend.py
```

**预期结果**：`Passed: 49/49`，`Failed: 0/49`。

---

## 十五、当前环境限制

- 当前环境无 MySQL，无法执行真实的数据库连接和接口集成测试
- WSL2 环境无法直接访问 Windows 宿主机上的 MySQL
- 实际 MySQL 数据库导入和接口联调验证需在 Windows MySQL 可连接环境中补做
- 课程报告中的数据库截图和接口联调截图建议在 Windows 环境下完成

---

## 十六、需要 Codex 复审的重点

1. **`.env.example` 一致性**：确认 `SERVER_HOST`/`SERVER_PORT` 与 `config.py` 的 `alias` 一致
2. **`curl_examples.sh` 请求体正确性**：确认 generate 有 body、审核评分 0-10、project 无 `course_name`
3. **`test_report_material.md` 接口真实性**：确认全文不再包含不存在接口（register、POST /tasks、POST /reviews、PUT /artifacts、statistics/team 等）
4. **统一返回格式**：`code:0` 替代 `code:200`，`message:success` 替代 `message:操作成功`
5. **README 数据库脚本完整性**：确认 01-07 全部列出且顺序正确
6. **README 响应格式**：确认健康检查使用统一格式而非裸 JSON
7. **无越界修改**：确认未修改 `database/*`、`frontend/*`、业务代码
8. **诚实声明**：确认所有数据库连接测试项标注"待补充截图"或"待 Windows MySQL 环境验证"，无虚构结果

---

## 十七、验收清单

- [x] `.env.example` 使用 `SERVER_HOST`/`SERVER_PORT`，与 `config.py` 一致
- [x] `curl_examples.sh` generate 接口有 body，审核评分 0-10，project 无 `course_name`
- [x] `test_report_material.md` 不含不存在接口，全部替换为真实路由
- [x] 统一返回格式改为 `code:0`，不再出现 `code:200`
- [x] README 数据库脚本补齐 01-07，执行顺序正确
- [x] README 健康检查响应使用统一格式
- [x] README `.env` 示例同步更新为 `SERVER_HOST`/`SERVER_PORT`
- [x] 未修改 `database/*`、`frontend/*`、业务代码
- [x] 无真实密钥泄露
- [x] 环境限制声明完整
