# HANDOFF-005：Stage-05 任务与版本管理模块

## 任务状态

**完成** — Stage-05 任务与版本管理模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/task_repo.py` | 新建 | 任务/分支/输出所有参数化 SQL |
| `backend/app/services/task_service.py` | 新建 | 任务/分支/输出业务逻辑 + 权限判断 |
| `backend/app/routers/tasks.py` | 新建 | 11 个接口 |
| `backend/app/main.py` | 修改 | 注册 `tasks.router` |
| `cursor_and_codex_chat/handoff/HANDOFF-005-task-version-management.md` | 新建 | 本交接报告 |

**说明**：`project_service.py` 和 `project_repo.py` 未修改。复用方式：在 `task_service.py` 中直接 import `project_repo` 的 `is_user_in_project`、`is_user_project_owner`、`is_user_project_leader` 函数，以及 `user_repo.is_admin()`，无需修改原文件。

---

## 二、实现内容

### 2.1 Repository 层（`task_repo.py`）

**任务基础查询**：
| 函数 | 说明 |
|---|---|
| `get_task_by_id` | 按 ID 查询任务，含项目名、创建人、负责人信息 |
| `list_tasks_for_project` | 分页查询项目任务，支持 status/keyword 过滤 |

**任务写操作**：
| 函数 | 说明 |
|---|---|
| `create_task` | 创建任务（支持外部 conn）|
| `update_task` | 更新任务字段（动态构造，支持外部 conn）|
| `soft_delete_task` | 软删除（支持外部 conn）|

**分支查询/写操作**：
| 函数 | 说明 |
|---|---|
| `list_task_branches` | 查询分支列表 |
| `get_branch_by_id` | 按 ID 查询分支 |
| `is_branch_name_exists_in_task` | 检查分支名重复 |
| `create_task_branch` | 创建分支（支持外部 conn）|

**输出版本查询/写操作**：
| 函数 | 说明 |
|---|---|
| `list_task_outputs` | 查询版本列表（不含 content）|
| `get_output_by_id` | 查询版本详情（含 content）|
| `get_output_task_id` | 从 output_id 查 task_id |
| `get_next_version_no` | 生成下一个版本号 |
| `get_output_by_id_and_task` | 确认 output 属于指定 task |
| `get_branch_by_id_and_task` | 确认分支属于指定 task |
| `create_manual_output` | 创建人工输出版本（支持外部 conn）|

### 2.2 Service 层（`task_service.py`）

- 权限判断复用 `project_repo` 和 `user_repo`：`_is_admin`、`_can_access_project`、`_can_manage_project`、`_can_create_task`、`_can_update_task`、`_can_delete_task`
- `list_project_tasks`：分页列表 + 权限校验 + status/keyword 过滤
- `create_task`：创建任务 + 创建默认 main 分支 + operation_logs（事务）
- `get_task_detail`：详情 + 权限校验
- `update_task`：更新 + operation_logs（事务）+ affected_rows 检查
- `delete_task`：软删除 + operation_logs（事务）+ affected_rows 检查
- `list_task_branches`：分支列表 + 权限校验
- `create_task_branch`：创建分支 + 分支名重复检查 + operation_logs（事务）
- `list_task_outputs`：版本列表 + 权限校验
- `get_output_detail`：版本详情 + 权限校验
- `get_output_timeline`：使用 WITH RECURSIVE 查询版本链 + 权限校验
- `create_manual_output`：创建人工版本 + version_no 自动递增 + operation_logs（事务）

### 2.3 Router 层（`tasks.py`）

11 个接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/projects/{project_id}/tasks` | 项目任务列表 |
| POST | `/api/projects/{project_id}/tasks` | 创建项目任务 |
| GET | `/api/tasks/{task_id}` | 任务详情 |
| PUT | `/api/tasks/{task_id}` | 更新任务 |
| DELETE | `/api/tasks/{task_id}` | 软删除任务 |
| GET | `/api/tasks/{task_id}/branches` | 分支列表 |
| POST | `/api/tasks/{task_id}/branches` | 创建分支 |
| GET | `/api/tasks/{task_id}/outputs` | 版本列表 |
| GET | `/api/outputs/{output_id}` | 版本详情 |
| GET | `/api/outputs/{output_id}/timeline` | 版本时间线 |
| POST | `/api/tasks/{task_id}/outputs/manual` | 创建人工版本 |

---

## 三、数据库是否变化

**否**。本阶段未修改 `database/` 目录，未修改表结构。

涉及数据表（只读/写入）：

| 表 | 操作 |
|---|---|
| `project_tasks` | SELECT / INSERT / UPDATE（软删除）|
| `task_branches` | SELECT / INSERT |
| `task_outputs` | SELECT / INSERT |
| `projects` | SELECT（权限校验）|
| `project_members` | SELECT（权限校验）|
| `users` | SELECT（关联查询）|
| `operation_logs` | INSERT |

---

## 四、新增接口列表

```
GET    /api/projects/{project_id}/tasks
POST   /api/projects/{project_id}/tasks
GET    /api/tasks/{task_id}
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
GET    /api/tasks/{task_id}/branches
POST   /api/tasks/{task_id}/branches
GET    /api/tasks/{task_id}/outputs
GET    /api/outputs/{output_id}
GET    /api/outputs/{output_id}/timeline
POST   /api/tasks/{task_id}/outputs/manual
```

---

## 五、权限规则说明

### 项目级访问权限（复用 Stage-04）

| 角色 | 任务列表 | 任务详情 | 分支/版本 |
|---|---|---|---|
| admin | 查看全部 | 可查看 | 可操作全部 |
| 项目成员 | 只能查看本项目任务 | 只能查看本项目 | 只能查看本项目 |

### 任务操作权限

| 操作 | 允许角色 |
|---|---|
| 创建任务 | admin 或项目成员 |
| 更新任务 | admin 或项目 owner/leader 或任务创建人或任务负责人 |
| 删除任务 | admin 或项目 owner/leader 或任务创建人 |
| 创建分支 | admin 或项目成员 |
| 创建人工版本 | admin 或项目成员 |

### 权限复用方式

直接在 `task_service.py` 中 import `project_repo.is_user_in_project`、`is_user_project_owner`、`is_user_project_leader` 和 `user_repo.is_admin()`，不在 `project_service.py` 中添加新函数。

---

## 六、事务使用说明

以下操作使用 `get_db_transaction()` 保证与 `operation_logs` 同一事务：

| 操作 | 事务内容 | 是否含日志 |
|---|---|---|
| 创建任务 | `INSERT project_tasks` + `INSERT task_branches` + `INSERT operation_logs` | 是，同一事务 |
| 更新任务 | `UPDATE project_tasks` + `INSERT operation_logs` | 是，同一事务 |
| 删除任务 | `UPDATE project_tasks` + `INSERT operation_logs` | 是，同一事务 |
| 创建分支 | `INSERT task_branches` + `INSERT operation_logs` | 是，同一事务 |
| 创建人工版本 | `INSERT task_outputs` + `INSERT operation_logs` | 是，同一事务 |

---

## 七、operation_logs 写入说明

以下操作写入 `operation_logs`：

| 操作 | action_type | action_desc 示例 |
|---|---|---|
| 创建任务 | `task:create` | `创建任务: xxx` |
| 更新任务 | `task:update` | `更新任务: 5` |
| 删除任务 | `task:delete` | `删除任务: 5` |
| 创建分支 | `task:create_branch` | `创建任务分支: xxx` |
| 创建人工版本 | `task:create_output` | `创建人工输出版本: xxx` |

所有日志通过 `user_repo.insert_operation_log_with_conn()` 与业务操作在同一事务内写入。

---

## 八、任务创建测试方法

```bash
# 先登录获取 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 创建任务（假设 project_id=1, task_type_id=1）
curl -X POST "http://127.0.0.1:8000/api/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"task_type_id":1,"title":"生成需求分析初稿","description":"为课程报告生成需求分析","priority":"normal"}'
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": 1,
    "project_id": 1,
    "title": "生成需求分析初稿",
    "status": "draft",
    "default_branch_id": 1,
    ...
  }
}
```

---

## 九、分支创建测试方法

```bash
# 查看任务分支
curl "http://127.0.0.1:8000/api/tasks/1/branches" \
  -H "Authorization: Bearer $TOKEN"

# 创建新分支
curl -X POST "http://127.0.0.1:8000/api/tasks/1/branches" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"branch_name":"张三修改版","base_output_id":null}'
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "branch_id": 2,
    "task_id": 1,
    "branch_name": "张三修改版",
    "status": "active",
    ...
  }
}
```

---

## 十、人工输出版本创建测试方法

```bash
# 先创建一个人工版本（需要 task_id 和 branch_id）
curl -X POST "http://127.0.0.1:8000/api/tasks/1/outputs/manual" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"branch_id":1,"output_title":"需求分析 v1.0","content":"# 需求分析\n\n## 功能需求\n\n1. 用户登录...\n","edit_summary":"初始版本"}'
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "output_id": 1,
    "task_id": 1,
    "branch_id": 1,
    "version_no": 1,
    "output_title": "需求分析 v1.0",
    "source_type": "manual_edit",
    "content": "# 需求分析\n\n## 功能需求\n\n1. 用户登录...\n",
    ...
  }
}
```

---

## 十一、版本时间线测试方法

```bash
# 查询版本时间线
curl "http://127.0.0.1:8000/api/outputs/1/timeline" \
  -H "Authorization: Bearer $TOKEN"
```

期望（使用 WITH RECURSIVE）：
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {"output_id": 1, "parent_output_id": null, "version_no": 1, "depth": 0, ...},
    {"output_id": 2, "parent_output_id": 1, "version_no": 2, "depth": 1, ...}
  ]
}
```

---

## 十二、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查。
2. **时间线 CTE 兼容性**：MySQL 8.0 完全支持 `WITH RECURSIVE`，但如果 MySQL 版本低于 8.0 会失败；目前假设数据库为 MySQL 8.0。
3. **task_type_id 有效性未校验**：创建任务时只检查了 task_type_id 类型，未查询 task_types 表确认记录存在。如需严格校验，需在 service 层添加。
4. **乐观锁未实现**：版本创建后 `lock_version` 默认为 0，版本编辑时的乐观锁检查（对比旧 `lock_version`）在后续阶段实现。

---

## 十三、是否实现 AI 调用

**否**。

---

## 十四、是否实现提示词模板

**否**。

---

## 十五、是否实现审核中心

**否**。

---

## 十六、是否实现前端页面

**否**。

---

## 十七、Python 语法检查命令

```bash
cd backend
python -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py
```

结果：`EXIT:0`（通过）。

---

## 十八、需要 Codex 审查的重点

1. **事务边界**：确认 5 类关键操作（创建/更新/删除任务、创建分支、创建版本）与 `operation_logs` 在同一 `get_db_transaction()` 事务内
2. **权限复用**：确认 `task_service.py` 直接 import `project_repo` 和 `user_repo` 函数，未修改原文件
3. **affected_rows 检查**：确认所有 UPDATE 失败时 `rollback` + 抛异常
4. **软删除**：确认删除任务使用 `UPDATE ... SET is_deleted=1`，无物理 `DELETE`
5. **参数化 SQL**：确认所有 SQL 无字符串拼接用户输入
6. **version_no 递增**：确认 `get_next_version_no` 正确获取最大版本号并 +1
7. **source_type 逻辑**：确认 `parent_output_id` 为空 → `manual_edit`，非空 → `hybrid`
8. **时间线递归**：确认使用 `WITH RECURSIVE` 正确从根节点向下遍历
9. **无越界实现**：确认未实现 AI 调用、提示词模板、审核中心、成果库

---

## 十九、验收清单

- [x] 项目任务列表支持分页、status、keyword 过滤
- [x] 创建任务自动创建默认 main 分支
- [x] 创建任务写入 operation_logs
- [x] 创建任务使用事务
- [x] 任务详情需有权限
- [x] 更新任务需 admin/owner/leader/creator/assignee
- [x] 更新任务写入 operation_logs
- [x] 删除任务为软删除
- [x] 删除任务写入 operation_logs
- [x] 分支创建需有权限
- [x] 分支名唯一性校验
- [x] base_output_id 归属校验
- [x] 分支创建写入 operation_logs
- [x] 版本列表不返回完整 content
- [x] 版本详情含 content 和 lock_version
- [x] 时间线使用 WITH RECURSIVE
- [x] 人工版本 source_type 正确（manual_edit/hybrid）
- [x] 版本号自动递增
- [x] 版本创建写入 operation_logs
- [x] 所有 SQL 参数化
- [x] 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`
- [x] 未实现 AI 调用、提示词模板、审核中心、成果库、前端页面

---

**本阶段完成后停止，不进入 Stage-06。**
