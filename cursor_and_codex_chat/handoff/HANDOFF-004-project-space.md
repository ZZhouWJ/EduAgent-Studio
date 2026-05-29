# HANDOFF-004：Stage-04 项目空间管理模块

## 任务状态

**完成** — Stage-04 项目空间管理模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/project_repo.py` | 新建 | 项目和项目成员的所有参数化 SQL |
| `backend/app/services/project_service.py` | 新建 | 项目和项目成员业务逻辑，含权限判断 |
| `backend/app/routers/projects.py` | 新建 | 项目和项目成员管理接口（10 个端点）|
| `backend/app/main.py` | 修改 | 注册 `projects.router` |
| `cursor_and_codex_chat/handoff/HANDOFF-004-project-space.md` | 新建 | 本交接报告 |

**说明**：未修改 `user_repo.py`、`auth_service.py`、`token.py`，因为所有权限判断逻辑（`_is_admin`、`_is_project_manager`、`_can_access_project`）均已在 `project_service.py` 中实现，复用了已有的 `user_repo.is_admin()`，其余逻辑直接调用 `project_repo` 函数，不需新增工具函数。

---

## 二、实现内容

### 2.1 Repository 层（`project_repo.py`）

**项目基础**：
| 函数 | 说明 |
|---|---|
| `get_project_by_id` | 按 ID 查询项目，含 owner 用户信息 |
| `list_projects_for_user` | 按权限分页查询项目列表（admin/teacher/普通成员）|

**项目写操作**：
| 函数 | 说明 |
|---|---|
| `create_project` | 创建项目 + 写入 project_members，事务内完成 |
| `update_project` | 更新项目字段（动态构造）|
| `soft_delete_project` | 软删除（is_deleted=1, deleted_at, deleted_by）|
| `archive_project` | 归档项目（status='archived'）|

**项目成员**：
| 函数 | 说明 |
|---|---|
| `list_project_members` | 查询项目成员列表 |
| `get_project_member` | 按 member_id 查询成员 |
| `get_project_member_by_user` | 按 (project_id, user_id) 查询成员 |
| `is_user_project_owner` | 判断是否为 owner |
| `is_user_project_leader` | 判断是否为 leader |
| `is_user_in_project` | 判断是否为项目成员 |
| `add_project_member` | 添加成员 |
| `update_project_member_role` | 修改成员角色 |
| `soft_delete_project_member` | 软删除成员（移除）|

### 2.2 Service 层（`project_service.py`）

- `_require_auth(token)`：统一解析 Token，失败抛 ForbiddenException
- `_is_admin(user)`：判断管理员
- `_is_project_manager(project_id, user_id)`：判断项目管理者（admin 或 owner 或 leader）
- `_can_access_project(project_id, user)`：判断可访问（admin 或成员）
- `list_projects`：分页列表 + 权限过滤 + keyword/status 过滤
- `create_project`：创建 + 写入 operation_logs
- `get_project_detail`：详情 + 权限校验
- `update_project`：更新 + operation_logs
- `delete_project`：软删除 + operation_logs
- `archive_project`：归档 + operation_logs
- `list_project_members`：成员列表 + 权限校验
- `add_project_member`：添加成员 + operation_logs
- `update_project_member_role`：改角色 + operation_logs + 禁止降级 owner
- `remove_project_member`：移除成员（软删除）+ operation_logs + 禁止移除 owner

### 2.3 Router 层（`projects.py`）

10 个接口，全部注册到 `APIRouter(prefix="/api/projects")`：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/projects` | 项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{project_id}` | 项目详情 |
| PUT | `/api/projects/{project_id}` | 更新项目 |
| DELETE | `/api/projects/{project_id}` | 软删除项目 |
| POST | `/api/projects/{project_id}/archive` | 归档项目 |
| GET | `/api/projects/{project_id}/members` | 成员列表 |
| POST | `/api/projects/{project_id}/members` | 添加成员 |
| PUT | `/api/projects/{project_id}/members/{member_id}` | 修改成员角色 |
| DELETE | `/api/projects/{project_id}/members/{member_id}` | 移除成员 |

---

## 三、数据库是否变化

**否**。本阶段未修改 `database/` 目录，未修改表结构。

涉及数据表（只读/写入）：

| 表 | 操作 | 说明 |
| --- | --- | --- |
| `projects` | SELECT / INSERT / UPDATE | 查询、创建、更新、软删除、归档 |
| `project_members` | SELECT / INSERT / UPDATE | 成员查询、添加、修改角色、软删除 |
| `users` | SELECT | 关联查询 owner 信息 |
| `operation_logs` | INSERT | 所有关键操作写入日志 |

---

## 四、新增接口列表

```
GET    /api/projects
POST   /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}
POST   /api/projects/{project_id}/archive
GET    /api/projects/{project_id}/members
POST   /api/projects/{project_id}/members
PUT    /api/projects/{project_id}/members/{member_id}
DELETE /api/projects/{project_id}/members/{member_id}
```

所有接口统一返回 `{"code": 0, "message": "success", "data": {...}}` 或错误格式。

---

## 五、权限规则说明

| 角色 | 项目列表 | 项目详情 | 更新/删除/归档 | 成员管理 |
|---|---|---|---|---|
| admin | 查看全部项目 | 可查看 | 可操作全部 | 可操作全部 |
| teacher | 只能查看参与的项目（作为 teacher 角色）| 需是成员 | 无权 | 无权 |
| project_leader | 只能查看参与的项目 | 需是成员 | 可操作本项目 | 可操作本项目 |
| student_member | 只能查看参与的项目 | 需是成员 | 无权 | 无权 |

- `_is_project_manager`：admin OR owner OR leader
- `_can_access_project`：admin OR 是项目成员
- 所有写操作（更新/删除/归档/添加成员/修改角色/移除成员）必须 `_is_project_manager`
- 所有读操作只需 `_can_access_project`

---

## 六、事务使用说明

以下操作使用 `get_db_cursor()` 上下文管理器的事务：

| 操作 | 事务范围 |
|---|---|
| 创建项目 | INSERT projects + INSERT project_members（在 `create_project` 同一 with 块内）|
| 更新项目 | 单条 UPDATE，无跨表 |
| 软删除项目 | 单条 UPDATE |
| 归档项目 | 单条 UPDATE |
| 添加成员 | 单条 INSERT |
| 修改成员角色 | 单条 UPDATE |
| 移除成员 | 单条 UPDATE |

`get_db_cursor()` 上下文管理器自动 commit 成功，失败自动 rollback。

---

## 七、操作日志写入说明

以下操作写入 `operation_logs`：

| 操作 | action_type | action_desc 示例 |
|---|---|---|
| 创建项目 | `project:create` | `创建项目: xxx` |
| 更新项目 | `project:update` | `更新项目: 5` |
| 删除项目 | `project:delete` | `删除项目: 5` |
| 归档项目 | `project:archive` | `归档项目: 5` |
| 添加成员 | `project:add_member` | `添加项目成员: user_id=3, role=member` |
| 修改成员角色 | `project:update_member` | `修改项目成员角色: member_id=7, role=reviewer` |
| 移除成员 | `project:remove_member` | `移除项目成员: member_id=7` |

---

## 八、依赖说明

本阶段无新增 Python 依赖，继续使用 Stage-03 的所有依赖。数据库使用已有的 `pymysql`。

---

## 九、启动命令

```bash
cd backend
pip install -r requirements.txt
python run.py
```

---

## 十、项目创建测试方法

```bash
# 先登录获取 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 创建项目
curl -X POST http://127.0.0.1:8000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"project_name":"测试课程项目","project_type":"course_project","description":"数据库课程设计"}'
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "project_id": 1,
    "project_name": "测试课程项目",
    "project_type": "course_project",
    "description": "数据库课程设计",
    "owner_id": 1,
    "owner_username": "admin",
    "owner_real_name": "系统管理员",
    "status": "active",
    ...
  }
}
```

---

## 十一、项目列表测试方法

```bash
# admin 查看全部项目
curl "http://127.0.0.1:8000/api/projects?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# 带关键字搜索
curl "http://127.0.0.1:8000/api/projects?keyword=课程&status=active" \
  -H "Authorization: Bearer $TOKEN"
```

期望分页格式：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

---

## 十二、项目成员管理测试方法

```bash
# 查看项目成员（需要先有一个普通用户，可通过 GET /api/users 获取 user_id）
curl "http://127.0.0.1:8000/api/projects/1/members" \
  -H "Authorization: Bearer $TOKEN"

# 添加成员（假设普通用户 user_id=2）
curl -X POST "http://127.0.0.1:8000/api/projects/1/members" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_id":2,"project_role":"member"}'

# 修改成员角色
curl -X PUT "http://127.0.0.1:8000/api/projects/1/members/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"project_role":"reviewer"}'

# 移除成员
curl -X DELETE "http://127.0.0.1:8000/api/projects/1/members/2" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十三、项目归档测试方法

```bash
curl -X POST "http://127.0.0.1:8000/api/projects/1/archive" \
  -H "Authorization: Bearer $TOKEN"
```

期望：`{"code": 0, "message": "success", "data": {"project_id": 1, "status": "archived", ...}}`

已归档项目再次归档返回：`{"code": 4000, "message": "项目已归档", "data": null}`

---

## 十四、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查。
2. **归档未调用存储过程**：`archive_project` 当前直接 `UPDATE projects SET status='archived'`，未调用 Stage-01 中定义的 `sp_archive_project` 存储过程，因为无法在当前环境验证存储过程是否已创建。如需改为调用存储过程，只需修改 `project_repo.archive_project` 中的 SQL 为 `CALL sp_archive_project(%s, %s)`。
3. **teacher 查看自己参与的项目**：`list_projects_for_user` 通过 `user_roles` 表中 `role_code='teacher'` 判断是否为教师，但 `teacher` 是 `user_roles` 的系统角色，不是 `project_members.project_role`。逻辑正确但需初始化数据确认教师用户已有 `teacher` 角色。
4. **非成员无权查看项目**：非项目成员访问项目详情、成员列表等均返回 `{"code": 4001, "message": "无权访问此项目"}`。

---

## 十五、需要 Codex 审查的重点

1. **参数化 SQL**：确认 `project_repo.py` 中所有 SQL 均使用 `%s` 占位符，无字符串拼接；`keyword` 变量构造 `f"%{keyword}%"` 仅为 `LIKE` 模式，不拼入列名，安全。
2. **软删除**：确认所有删除操作均为 `UPDATE ... SET is_deleted=1`，无物理 `DELETE`。
3. **事务**：确认 `create_project` 中 `INSERT projects` 和 `INSERT project_members` 在同一事务内。
4. **权限校验**：确认每条写操作（更新/删除/归档/成员管理）均经过 `_is_project_manager` 判断；每条读操作均经过 `_can_access_project` 判断。
5. **操作日志**：确认所有关键写操作均调用 `insert_operation_log`。
6. **禁止越界**：确认未实现任务管理、AI 调用、提示词模板、审核中心、成果库。
7. **统一响应格式**：确认所有接口返回 `{"code", "message", "data"}`。
8. **owner 保护**：确认 `remove_project_member` 禁止移除 owner；`update_project_member_role` 禁止将 owner 降级。
9. **无 password_hash 泄漏**：所有项目成员查询均通过 `list_project_members`（JOIN users）返回，不含 `password_hash`。

---

## 十六、验收清单

- [x] 项目列表支持分页、keyword、status 过滤
- [x] 项目列表按角色权限过滤（admin/teacher/普通成员）
- [x] 项目创建自动写入 project_members（角色 leader）
- [x] 项目创建写入 operation_logs
- [x] 项目创建使用事务
- [x] 项目详情需有权限
- [x] 项目更新需 admin/owner/leader
- [x] 项目更新写入 operation_logs
- [x] 项目删除为软删除
- [x] 项目删除写入 operation_logs
- [x] 项目归档写入 operation_logs
- [x] 成员列表需有权限
- [x] 添加成员需 admin/owner/leader
- [x] 添加成员不可重复
- [x] 添加成员写入 operation_logs
- [x] 修改成员角色需 admin/owner/leader
- [x] 修改成员角色禁止降级 owner
- [x] 修改成员角色写入 operation_logs
- [x] 移除成员为软删除
- [x] 移除成员禁止移除 owner
- [x] 移除成员写入 operation_logs
- [x] 所有 SQL 参数化
- [x] 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`
- [x] 未实现任务管理、AI 调用、提示词模板、审核中心、成果库

---

**本阶段完成后停止，不进入 Stage-05。**
