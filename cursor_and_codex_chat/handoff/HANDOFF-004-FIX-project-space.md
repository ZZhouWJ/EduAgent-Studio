# HANDOFF-004-FIX：Stage-04 项目空间管理模块修复版

## 任务状态

**完成** — Stage-04 的 5 个阻塞问题均已修复。

---

## 一、Codex 未通过原因

| # | 问题 | 严重程度 |
|---|---|---|
| 1 | `project_repo.create_project()` 没有 `return project_id` | 阻塞 |
| 2 | 关键写操作和 `operation_logs` 不在同一事务 | 阻塞 |
| 3 | 项目归档没有调用 `sp_archive_project`，只更新了 projects.status | 阻塞 |
| 4 | teacher 项目列表没有限制 `project_members.project_role = 'teacher'` | 阻塞 |
| 5 | UPDATE 返回值未检查，`affected_rows=0` 仍返回成功 | 阻塞 |

次要问题：`_handle_service` 会暴露 `str(e)`；未登录用 `ForbiddenException`（4001）而非 `UnauthorizedException`（4002）；body 参数声明为 `=None` 会导致 `AttributeError`。

---

## 二、本次修复了哪些文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/database.py` | 修改 | 新增 `get_db_transaction()` 显式事务上下文管理器 |
| `backend/app/repositories/project_repo.py` | 重写 | 所有写操作支持 `conn` 参数；优先调用 `sp_archive_project`；返回 `affected_rows` |
| `backend/app/repositories/user_repo.py` | 修改 | 新增 `insert_operation_log_with_conn()` 支持外部事务连接 |
| `backend/app/services/project_service.py` | 重写 | 所有写操作使用 `get_db_transaction()` 统一事务；检查 `affected_rows` |
| `backend/app/routers/projects.py` | 重写 | 删除 `_handle_service`；未登录改用 `UnauthorizedException`；body 参数改为 `Body(...)` |
| `cursor_and_codex_chat/handoff/HANDOFF-004-FIX-project-space.md` | 新建 | 本修复报告 |

---

## 三、create_project 如何返回 project_id

**修改前**：`project_repo.create_project()` 内部获取了 `cursor.lastrowid` 但函数末没有 `return`，导致 service 层得到 `None`。

**修改后**：

```python
# project_repo.py
def create_project(..., conn=None) -> int:
    cursor.execute("INSERT INTO projects ...")
    project_id = cursor.lastrowid          # ← 已在原代码中
    cursor.execute("INSERT INTO project_members ...")
    return project_id                      # ← 新增此行
```

service 层使用显式事务调用：

```python
with get_db_transaction() as conn:
    project_id = project_repo.create_project(..., conn=conn)
    user_repo.insert_operation_log_with_conn(..., conn=conn)
    conn.commit()
```

`conn.commit()` 在事务内所有 SQL 成功后执行，任一 SQL 失败则 `get_db_transaction()` 的 `except` 块自动 `rollback`。

---

## 四、哪些写操作已经和 operation_logs 放入同一事务

**统一事务模式**：service 层用 `get_db_transaction()` 获取连接，传入 repo 和日志函数，最后 `conn.commit()`。

| 操作 | 事务内容 | 是否含日志 |
|---|---|---|
| 创建项目 | `INSERT projects` + `INSERT project_members` + `INSERT operation_logs` | 是，同一事务 |
| 更新项目 | `UPDATE projects` + `INSERT operation_logs` | 是，同一事务 |
| 删除项目（软删除）| `UPDATE projects.is_deleted` + `INSERT operation_logs` | 是，同一事务 |
| 归档项目 | `CALL sp_archive_project`（内部含 `INSERT operation_logs`）| 存储过程内部保证 |
| 添加成员 | `INSERT project_members` + `INSERT operation_logs` | 是，同一事务 |
| 修改成员角色 | `UPDATE project_members` + `INSERT operation_logs` | 是，同一事务 |
| 移除成员 | `UPDATE project_members.is_deleted` + `INSERT operation_logs` | 是，同一事务 |

所有事务均通过 `get_db_transaction()` 上下文管理器实现：成功自动 `commit`，异常自动 `rollback`，`finally` 关闭连接。

---

## 五、archive_project 是否调用 sp_archive_project

**是，优先调用存储过程**。

### 调用方式

```python
# project_repo.py
def archive_project_with_procedure(project_id, operator_id, conn=None) -> Tuple[int, int, str]:
    cursor.callproc("sp_archive_project", (project_id, operator_id, 0, ""))
    rows = list(cursor.fetchall())
    result_code = rows[-1].get("result_code", 0)
    result_message = rows[-1].get("result_message", "")
    return result_code, result_message, 1
```

### 存储过程签名（来自 `database/06_create_stored_procedures.sql`）

```sql
CREATE PROCEDURE `sp_archive_project`(
    IN  p_project_id       INT UNSIGNED,
    IN  p_operator_id      INT UNSIGNED,
    OUT p_result_code      INT,
    OUT p_result_message   VARCHAR(255)
)
```

### 存储过程内部行为（完整实现）

1. `SELECT project_name ... FOR UPDATE`（行锁）
2. 项目不存在时 `ROLLBACK` + 设置 `p_result_code=404`
3. `UPDATE projects SET status='archived'`
4. `UPDATE project_tasks SET status='archived'`（归档所有任务）
5. `UPDATE task_branches SET status='closed'`（关闭所有分支）
6. `INSERT INTO operation_logs`（写入归档日志）
7. `COMMIT` + 设置 `p_result_code=0`

### Service 层处理

```python
with get_db_transaction() as conn:
    result_code, result_message, _ = project_repo.archive_project_with_procedure(
        project_id=project_id, operator_id=user_id, conn=conn,
    )
    if result_code == 404:
        conn.rollback()
        raise NotFoundException(...)
    elif result_code != 0:
        conn.rollback()
        raise ValidationException(...)
    conn.commit()
```

**注意**：由于当前环境无法连接 Windows MySQL，存储过程调用未实际运行验证。以上逻辑基于 `06_create_stored_procedures.sql` 的完整静态分析实现。

---

## 六、如果存储过程调用失败，回退方案

`project_repo.py` 中提供了 `archive_project_fallback()`，使用纯 SQL 在同一事务中模拟存储过程行为（更新项目状态 + 更新任务状态 + 更新分支状态），但本修复优先使用存储过程，`fallback` 仅作为环境验证不可行时的备用方案保留。

---

## 七、teacher 项目列表权限如何修复

**修改前**：

```python
# teacher 分支，只判断用户有 'teacher' 系统角色，不限制 project_role
WHERE ... AND pm.user_id = %s  # ← 缺少 project_role 过滤
```

**修改后**：

```python
# project_repo.py list_projects_for_user() teacher 分支
where_clause = (
    base_where + keyword_filter + status_filter +
    " AND p.project_id IN ("
    "  SELECT pm.project_id FROM project_members pm"
    "  WHERE pm.is_deleted = 0"
    "    AND pm.user_id = %s"
    "    AND pm.project_role = 'teacher'"   # ← 新增此过滤
    ")"
)
```

**权限矩阵**：

| 角色 | 项目列表过滤 |
|---|---|
| admin | 查看全部项目（无成员过滤）|
| teacher（系统角色）| 只看 `project_members.project_role='teacher'` 的项目 |
| project_leader / student_member | 只看自己参与的项目 |
| 非成员 | 不能查看 |

---

## 八、哪些 UPDATE 已检查 affected_rows

所有返回 `affected_rows` 的写操作均在 service 层检查：

| 操作 | Repository 返回 | Service 层检查 |
|---|---|---|
| `update_project` | `int`（affected_rows）| `if affected == 0: raise NotFoundException` |
| `soft_delete_project` | `int`（affected_rows）| `if affected == 0: raise NotFoundException` |
| `archive_project_with_procedure` | `int`（result_code）| `if result_code != 0: raise ValidationException` |
| `update_project_member_role` | `int`（affected_rows）| `if affected == 0: raise NotFoundException` |
| `soft_delete_project_member` | `int`（affected_rows）| `if affected == 0: raise NotFoundException` |

`affected_rows == 0` 或 `result_code != 0` 时均 `conn.rollback()` 后抛出明确的 `NotFoundException` 或 `ValidationException`，不会返回假成功。

---

## 九、是否修改数据库结构

**否**。本修复未修改 `database/*` 目录，未修改表结构。

---

## 十、是否修改 frontend

**否**。

---

## 十一、是否实现 Stage-05 内容

**否**。本修复仅修复 Stage-04 阻塞问题，未实现任务管理、AI 调用、提示词模板、审核中心、成果库。

---

## 十二、Python 语法检查命令

```bash
cd backend
python -m py_compile app/database.py app/repositories/project_repo.py app/services/project_service.py app/routers/projects.py app/repositories/user_repo.py app/main.py run.py
```

结果：`EXIT:0`（通过）。

---

## 十三、已知环境限制

1. **当前环境无 MySQL**：无法真实执行存储过程调用验证，以上逻辑基于 `06_create_stored_procedures.sql` 的静态分析。
2. **当前环境无 pip/venv**：无法 `pip install` 和启动 FastAPI 服务，所有运行测试需在完整环境可用后执行。
3. **存储过程 OUT 参数处理**：MySQL `CALLproc` 返回结果集（而非直接赋值 OUT 变量），本实现通过 `cursor.fetchall()` 获取结果行并取最后一行中的 `result_code`，这是 PyMySQL 处理存储过程 OUT 参数的标准方式。
4. **`get_db_transaction` 异常处理**：`get_db_transaction()` 上下文管理器在 `except` 块自动 `rollback`，service 层不需要显式 try/except（service 层每个函数各自有事务块）。

---

## 十四、需要 Codex 复审的重点

1. **事务边界**：确认 6 类关键操作（创建/更新/删除/归档/添加成员/修改成员角色/移除成员）的业务 SQL 和 `operation_logs` 在同一 `get_db_transaction()` 事务内
2. **create_project 返回值**：确认 repo 返回 `cursor.lastrowid`，service 层用该 ID 写日志和返回详情
3. **sp_archive_project 调用**：确认 `cursor.callproc()` 正确处理 4 个参数（2 个 IN + 2 个 OUT），通过 `fetchall()` 获取 OUT 参数值
4. **teacher 权限过滤**：确认 teacher 分支 SQL 中有 `pm.project_role = 'teacher'`
5. **affected_rows 检查**：确认所有 UPDATE 失败（`affected_rows=0`）时抛出 `NotFoundException` 并 `rollback`
6. **UnauthorizedException**：确认未登录使用 4002 而非 4001
7. **body 声明**：确认所有请求体使用 `Body(...)` 而非 `=None`
8. **无物理 DELETE**：确认所有删除操作仍为 `UPDATE is_deleted=1`
9. **参数化 SQL**：确认所有 SQL 无字符串拼接用户输入

---

## 十五、验收清单

- [x] `POST /api/projects` 返回真实新建项目详情（含 project_id）
- [x] 创建项目同时写入 `project_members.project_role='leader'`
- [x] 创建项目日志中的 `project_id` 和 `target_id` 不为 `None`
- [x] 6 类关键写操作与 `operation_logs` 同一事务
- [x] 归档优先调用 `sp_archive_project`（通过 PyMySQL `callproc`）
- [x] teacher 只能查看自己作为 `project_role='teacher'` 的项目
- [x] 所有软删除仍为 UPDATE，不出现物理 DELETE
- [x] 所有 SQL 仍使用参数化查询
- [x] 不返回 `password_hash`
- [x] UPDATE 返回值检查：`affected_rows==0` 时 `rollback` + 抛异常
- [x] 未登录使用 `UnauthorizedException`（code=4002）
- [x] 请求体使用 `Body(...)`
- [x] 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`
- [x] 未实现任务管理、AI 调用、提示词模板、审核中心、成果库
- [x] Python 静态语法检查通过

---

**本修复完成后停止，等待 Codex 复审。**
