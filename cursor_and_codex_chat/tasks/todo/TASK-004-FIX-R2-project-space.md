# TASK-004-FIX-R2 项目空间管理归档修复任务

## 任务目标

修复 Stage-04 Fix 复审中唯一剩余阻塞点：项目归档接口调用 `sp_archive_project` 后必须可靠读取存储过程 OUT 参数，不得在归档失败时误返回成功。

## 背景

Codex 在 `REVIEW-004-FIX-project-space.md` 中确认：

- 创建项目返回 `project_id` 已修复；
- 关键写操作与 `operation_logs` 同事务已修复；
- teacher 项目列表权限已修复；
- UPDATE affected_rows 检查已修复；
- 仍需修复项目归档存储过程 OUT 参数读取逻辑。

## 允许修改文件

- `backend/app/repositories/project_repo.py`
- `backend/app/services/project_service.py`
- `cursor_and_codex_chat/handoff/HANDOFF-004-FIX-R2-project-space.md`

如确有必要，可少量修改：

- `backend/app/database.py`

但必须在 handoff 中说明原因。

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

- 任务管理；
- AI 调用；
- 提示词模板；
- 审核中心；
- 成果库；
- 前端页面；
- Stage-05 内容。

## 必须修复的问题

### 1. 正确读取 sp_archive_project 的 OUT 参数

`database/06_create_stored_procedures.sql` 中定义为：

```sql
CREATE PROCEDURE sp_archive_project(
    IN  p_project_id INT UNSIGNED,
    IN  p_operator_id INT UNSIGNED,
    OUT p_result_code INT,
    OUT p_result_message VARCHAR(255)
)
```

当前 `cursor.callproc(...); cursor.fetchall()` 不能可靠读取 OUT 参数。

请改为可靠方式，例如：

```sql
CALL sp_archive_project(%s, %s, @result_code, @result_message);
SELECT @result_code AS result_code, @result_message AS result_message;
```

或使用 PyMySQL 官方可行的等价方式读取 `@_sp_archive_project_2`、`@_sp_archive_project_3`。

### 2. 不得默认归档成功

如果无法读取 `result_code` 或 `result_message`：

- 不得默认 `result_code = 0`；
- 应抛出清晰异常或返回非 0 错误；
- service 层不得向前端返回成功。

### 3. service 层必须按真实结果处理

`project_service.archive_project()` 必须：

- `result_code == 0` 时返回成功；
- `result_code == 404` 时返回项目不存在；
- `result_code != 0` 时返回清晰错误；
- 不得吞掉存储过程错误。

### 4. 修正返回类型和返回值顺序

请修正 `archive_project_with_procedure()` 的类型注解和返回值，使其与实际使用一致。

推荐返回：

```python
Tuple[int, str]
```

即：

```python
return result_code, result_message
```

### 5. 处理 fallback 方法

如果保留 `archive_project_fallback()`：

- 必须补齐 `operation_logs` 写入；
- 必须保证 `projects`、`project_tasks`、`task_branches`、`operation_logs` 在同一事务；
- 必须检查项目状态更新 affected_rows；
- 或者在 handoff 中明确该方法未启用，不作为 Stage-04 验收依据。

## 验收要求

1. `archive_project_with_procedure()` 使用可靠方式读取 OUT 参数；
2. 存储过程返回 404/500 时不会返回成功；
3. 归档成功时项目状态由存储过程更新为 `archived`；
4. 归档成功时相关任务归档、分支关闭、操作日志写入均由存储过程完成；
5. 不修改 `database/`；
6. 不修改 `frontend/`；
7. 不实现 Stage-05 内容；
8. Python 语法检查通过。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/repositories/project_repo.py app/services/project_service.py app/routers/projects.py app/main.py run.py
```

如当前环境可连接 MySQL，请补充实际归档接口或存储过程调用验证，并在 handoff 中记录结果。
