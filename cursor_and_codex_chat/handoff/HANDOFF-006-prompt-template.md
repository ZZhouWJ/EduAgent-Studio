# HANDOFF-006：Stage-06 提示词模板管理模块

## 任务状态

**完成** — Stage-06 提示词模板管理模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/prompt_repo.py` | 新建 | 任务类型、模板、版本所有参数化 SQL |
| `backend/app/services/prompt_service.py` | 新建 | 业务逻辑 + 权限判断 |
| `backend/app/routers/prompts.py` | 新建 | 9 个接口 |
| `backend/app/main.py` | 修改 | 导入并注册 `prompts.router` |
| `cursor_and_codex_chat/handoff/HANDOFF-006-prompt-template.md` | 新建 | 本交接报告 |

**说明**：`project_service.py` 和 `project_repo.py` 均未修改。权限复用通过 import `user_repo.is_admin()` 和直接读取 `user["roles"]` 实现。

---

## 二、实现内容

### 2.1 Repository 层（`prompt_repo.py`）

**任务类型查询**：
| 函数 | 说明 |
|---|---|
| `list_task_types` | 查询任务类型列表（可选只查 active）|
| `get_task_type_by_id` | 按 ID 查询任务类型 |

**提示词模板查询**：
| 函数 | 说明 |
|---|---|
| `get_template_by_id` | 查询模板详情（含当前版本 prompt_content）|
| `list_templates` | 分页查询模板列表，支持 task_type_id/keyword 过滤 |

**提示词模板写操作**：
| 函数 | 说明 |
|---|---|
| `create_template` | 创建模板（支持外部 conn）|
| `update_template` | 更新字段（支持外部 conn）|
| `soft_delete_template` | 软删除（支持外部 conn）|
| `set_current_version` | 设置当前活动版本（支持外部 conn）|

**提示词版本查询/写操作**：
| 函数 | 说明 |
|---|---|
| `list_template_versions` | 版本列表 |
| `get_version_by_id` | 按 ID 查询版本 |
| `get_version_by_template_and_id` | 确认版本属于指定模板 |
| `get_next_version_no` | 自动生成版本号（按 created_at DESC 取最大 + 1）|
| `get_template_created_by` | 获取模板创建人 |
| `create_version` | 创建版本（支持外部 conn）|

### 2.2 Service 层（`prompt_service.py`）

- 权限判断复用 `user["roles"]` 中的角色：`admin`/`teacher`/`project_leader`
- `can_manage_template`：admin / teacher / project_leader / 模板创建人
- `list_task_types`：已登录用户可查看
- `list_templates`：已登录用户可查看
- `get_template_detail`：已登录用户可查看
- `create_template`：admin / teacher / project_leader 可创建
- `update_template`：可管理者可更新
- `delete_template`：可管理者可软删除
- `list_template_versions`：已登录用户可查看
- `create_version`：可管理者可创建（auto_activate 首个版本）
- `activate_version`：可管理者可启用版本

### 2.3 Router 层（`prompts.py`）

9 个接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/task-types` | 任务类型列表 |
| GET | `/api/prompt-templates` | 模板列表 |
| POST | `/api/prompt-templates` | 创建模板 |
| GET | `/api/prompt-templates/{template_id}` | 模板详情 |
| PUT | `/api/prompt-templates/{template_id}` | 更新模板 |
| DELETE | `/api/prompt-templates/{template_id}` | 软删除模板 |
| GET | `/api/prompt-templates/{template_id}/versions` | 版本列表 |
| POST | `/api/prompt-templates/{template_id}/versions` | 创建版本 |
| POST | `/api/prompt-templates/{template_id}/versions/{version_id}/activate` | 启用版本 |

---

## 三、数据库是否变化

**否**。本阶段未修改 `database/` 目录，未修改表结构。

涉及数据表：

| 表 | 操作 |
|---|---|
| `task_types` | SELECT |
| `prompt_templates` | SELECT / INSERT / UPDATE（软删除）|
| `prompt_versions` | SELECT / INSERT |
| `operation_logs` | INSERT |

---

## 四、新增接口列表

```
GET    /api/task-types
GET    /api/prompt-templates
POST   /api/prompt-templates
GET    /api/prompt-templates/{template_id}
PUT    /api/prompt-templates/{template_id}
DELETE /api/prompt-templates/{template_id}
GET    /api/prompt-templates/{template_id}/versions
POST   /api/prompt-templates/{template_id}/versions
POST   /api/prompt-templates/{template_id}/versions/{version_id}/activate
```

---

## 五、权限规则说明

| 操作 | admin | teacher | project_leader | 模板创建人 | 普通成员 |
|---|---|---|---|---|---|
| 查看任务类型列表 | 可 | 可 | 可 | 可 | 可 |
| 查看模板列表/详情 | 可 | 可 | 可 | 可 | 可 |
| 创建模板 | 可 | 可 | 可 | 不可 | 不可 |
| 更新模板 | 可 | 可 | 可 | 可 | 不可 |
| 软删除模板 | 可 | 可 | 可 | 可 | 不可 |
| 创建版本 | 可 | 可 | 可 | 可 | 不可 |
| 启用版本 | 可 | 可 | 可 | 可 | 不可 |

### 权限复用方式

直接在 `prompt_service.py` 中检查 `user["roles"]` 列表：

```python
def _is_admin(user): return "admin" in user.get("roles", [])
def _is_teacher(user): return "teacher" in user.get("roles", [])
def _is_project_leader(user): return "project_leader" in user.get("roles", [])
def _can_manage_template(created_by, user):
    return _is_admin(user) or _is_teacher(user) or _is_project_leader(user) \
           or (created_by == user["user_id"])
```

---

## 六、事务使用说明

以下操作使用 `get_db_transaction()` 保证与 `operation_logs` 同一事务：

| 操作 | 事务内容 | 是否含日志 |
|---|---|---|
| 创建模板 | `INSERT prompt_templates` + `INSERT operation_logs` | 是，同一事务 |
| 更新模板 | `UPDATE prompt_templates` + `INSERT operation_logs` | 是，同一事务 |
| 软删除模板 | `UPDATE prompt_templates` + `INSERT operation_logs` | 是，同一事务 |
| 创建版本 | `INSERT prompt_versions` + `INSERT operation_logs` | 是，同一事务 |
| 启用版本 | `UPDATE prompt_templates` + `INSERT operation_logs` | 是，同一事务 |

---

## 七、operation_logs 写入说明

| 操作 | action_type | action_desc 示例 |
|---|---|---|
| 创建模板 | `prompt_template:create` | `创建提示词模板: xxx` |
| 更新模板 | `prompt_template:update` | `更新提示词模板: 1` |
| 删除模板 | `prompt_template:delete` | `删除提示词模板: 1` |
| 创建版本 | `prompt_version:create` | `创建提示词版本: v1` |
| 启用版本 | `prompt_version:activate` | `启用提示词版本: version_id=5` |

所有日志通过 `user_repo.insert_operation_log_with_conn()` 与业务操作在同一事务内写入。

---

## 八、任务类型列表测试方法

```bash
# 先登录获取 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 查询任务类型列表
curl "http://127.0.0.1:8000/api/task-types" \
  -H "Authorization: Bearer $TOKEN"
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {"task_type_id": 1, "type_name": "需求分析", "type_code": "requirement_analysis", ...},
    ...
  ]
}
```

---

## 九、提示词模板创建测试方法

```bash
# 创建提示词模板（假设 task_type_id=1）
curl -X POST "http://127.0.0.1:8000/api/prompt-templates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"template_name":"需求分析生成模板","task_type_id":1,"description":"用于生成需求分析"}'
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "template_id": 1,
    "template_name": "需求分析生成模板",
    "task_type_id": 1,
    ...
  }
}
```

---

## 十、提示词版本创建测试方法

```bash
# 创建提示词版本（假设 template_id=1）
curl -X POST "http://127.0.0.1:8000/api/prompt-templates/1/versions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt_content":"你是一名数据库课程设计助手，请根据以下材料生成需求分析……","change_note":"初始版本"}'
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "prompt_version_id": 1,
    "template_id": 1,
    "version_no": "1",
    "prompt_content": "你是一名数据库课程设计助手...",
    ...
  }
}
```

---

## 十一、启用提示词版本测试方法

```bash
# 启用版本（假设 template_id=1, version_id=1）
curl -X POST "http://127.0.0.1:8000/api/prompt-templates/1/versions/1/activate" \
  -H "Authorization: Bearer $TOKEN"
```

期望：模板的 `current_version_id` 变为 1。

---

## 十二、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查。
2. **version_no 字段类型**：`prompt_versions.version_no` 在 Schema 中定义为 VARCHAR，接口接受字符串输入，也支持自动生成整数后转为字符串。
3. **auto_activate 逻辑**：创建版本时，若模板无 `current_version_id`，自动设为当前版本（首个版本自动成为活动版本）。
4. **版本号自动生成**：不提供 `version_no` 时自动取 `MAX(created_at DESC LIMIT 1) + 1`。

---

## 十三、是否实现 AI 调用

**否**。

---

## 十四、是否实现审核中心

**否**。

---

## 十五、是否实现成果库

**否**。

---

## 十六、是否实现前端页面

**否**。

---

## 十七、需要 Codex 审查的重点

1. **事务边界**：确认 5 类写操作（创建/更新/删除模板、创建版本、启用版本）与 `operation_logs` 在同一 `get_db_transaction()` 事务内
2. **affected_rows 检查**：确认所有 UPDATE 失败时 `rollback` + 抛异常
3. **软删除**：确认删除模板使用 `UPDATE ... SET is_deleted=1`，无物理 `DELETE`
4. **参数化 SQL**：确认所有 SQL 无字符串拼接用户输入
5. **权限判断**：确认 admin/teacher/project_leader/模板创建人权限正确实现
6. **无越界**：确认未实现 AI 调用、审核中心、成果库、前端页面
7. **模板详情返回当前版本**：确认 `get_template_by_id` 联表查询了 `current_version_id` 对应的 `prompt_content`

---

## 十八、验收清单

- [x] 任务类型列表接口
- [x] 提示词模板列表接口（支持 task_type_id / keyword 过滤）
- [x] 创建提示词模板（需 admin / teacher / project_leader）
- [x] 提示词模板详情（含当前版本 prompt_content）
- [x] 更新提示词模板（需权限，UPDATE 检查 affected_rows）
- [x] 软删除提示词模板（需权限，UPDATE 检查 affected_rows）
- [x] 提示词版本列表
- [x] 创建提示词版本（需权限，version_no 自动生成）
- [x] 启用提示词版本（需权限）
- [x] 所有写操作写入 operation_logs
- [x] 所有写操作与日志同一事务
- [x] 所有 SQL 参数化
- [x] 未修改 `database/*`、`frontend/*`
- [x] 未实现 AI 调用、审核中心、成果库、前端页面

---

**本阶段完成后停止，不进入 Stage-07。**
