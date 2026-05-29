# HANDOFF-004-FIX-R2：Stage-04 项目空间管理归档修复版

## 任务状态

**完成** — 归档存储过程 OUT 参数读取问题已修复。

---

## 一、Codex 本轮唯一阻塞原因

`archive_project_with_procedure()` 使用 `cursor.callproc()` + `cursor.fetchall()` 读取 `sp_archive_project` 的 OUT 参数，但 PyMySQL 中 `callproc()` 不会暴露 OUT 参数，`fetchall()` 通常返回空列表。当前代码在 `fetchall()` 为空时默认 `result_code=0`，导致存储过程设置 404/500 时仍被误判为成功。

---

## 二、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/project_repo.py` | 修改 | 修复 `archive_project_with_procedure()` OUT 读取；补齐 `archive_project_fallback()` operation_logs 写入；修正返回类型 |
| `backend/app/services/project_service.py` | 修改 | 适配新的 repo 返回签名（`Tuple[int, str]`） |
| `cursor_and_codex_chat/handoff/HANDOFF-004-FIX-R2-project-space.md` | 新建 | 本修复报告 |

---

## 三、sp_archive_project 的真实参数签名

来自 `database/06_create_stored_procedures.sql`：

```sql
CREATE PROCEDURE `sp_archive_project`(
    IN  p_project_id       INT UNSIGNED,
    IN  p_operator_id      INT UNSIGNED,
    OUT p_result_code      INT,
    OUT p_result_message   VARCHAR(255)
)
```

返回值含义：
- `p_result_code=0`：归档成功
- `p_result_code=404`：项目不存在
- `p_result_code=500`：归档失败（SQL 异常）

---

## 四、修复前为什么会误判成功

```python
# 修复前代码
cursor.callproc("sp_archive_project", (project_id, operator_id, 0, ""))
rows = list(cursor.fetchall())
if rows:
    result_code = rows[-1].get("result_code", 0)   # ← 拿不到
    result_message = rows[-1].get("result_message", "")
else:
    result_code = 0                                  # ← 默认值：误判成功！
    result_message = ""
```

问题：
- PyMySQL 的 `callproc()` 在存储过程无 `SELECT` 结果集时，`fetchall()` 返回空列表
- 存储过程内部通过 `SET p_result_code=...` 设置 OUT 参数，但这不会产生结果集
- 代码在 `fetchall()` 为空时默认 `result_code=0`，把 404/500 当成功处理

---

## 五、修复后如何读取 OUT 参数

使用 **MySQL 会话变量**方式：

```python
# 步骤1：初始化会话变量
cursor.execute("SET @p_result_code = 0, @p_result_msg = ''")

# 步骤2：调用存储过程（OUT 参数由会话变量承接）
cursor.execute(
    "CALL sp_archive_project(%s, %s, @p_result_code, @p_result_msg)",
    (project_id, operator_id),
)

# 步骤3：读取会话变量（OUT 参数值）
cursor.execute("SELECT @p_result_code AS result_code, @p_result_msg AS result_message")
row = cursor.fetchone()

if row is None:
    # 无法读取，返回错误
    return 500, "归档结果未知（无法读取存储过程返回码）"

result_code = int(row["result_code"])
result_message = str(row["result_message"])
```

**为什么不用 `cursor.callproc()`？**

PyMySQL 的 `callproc()` 只能获取存储过程的 `SELECT` 结果集，无法读取通过 `SET @var` 设置的 OUT 参数。而 `cursor.execute()` 直接执行 SQL 语句后，可以通过后续的 `SELECT @var` 读取被存储过程修改的会话变量。

---

## 六、result_code == 0 和 != 0 分别如何处理

| result_code | 含义 | service 层处理 |
|---|---|---|
| `0` | 归档成功 | `conn.commit()`，返回项目详情 |
| `404` | 项目不存在 | `conn.rollback()`，抛出 `NotFoundException` |
| 其他非零值（如 `500`）| 归档失败 | `conn.rollback()`，抛出 `ValidationException` |

```python
# service 层
result_code, result_message = project_repo.archive_project_with_procedure(...)
if result_code == 404:
    conn.rollback()
    raise NotFoundException(message="项目不存在")
elif result_code != 0:
    conn.rollback()
    raise ValidationException(message=f"归档失败: {result_message}")
conn.commit()
```

---

## 七、如果 SELECT OUT 参数为空时如何处理

`row is None`（SELECT 会话变量无结果）说明无法确认存储过程归档结果，此时视为失败：

```python
if row is None:
    return 500, "归档结果未知（无法读取存储过程返回码）"
```

这确保不会在无法判断归档结果时返回假成功。

---

## 八、archive_project_fallback 修复说明

`archive_project_fallback()`（回退方案）本次也进行了修复：

1. **补齐 operation_logs 写入**：原来缺失，现在有完整的 INSERT 语句
2. **修正返回值类型**：`Tuple[int, int, str]` → `Tuple[int, str]`
3. **项目不存在时 rollback 而非 commit**：找不到项目不应视为成功
4. **operation_logs 写入与其他更新在同一事务内**：所有变更一起提交

当前 service 层未调用 `fallback`，仅优先使用 `archive_project_with_procedure`。如果未来因环境原因需要切换到 fallback，`fallback` 现在已满足所有归档要求。

---

## 九、是否修改 database

**否**。

---

## 十、是否修改 frontend

**否**。

---

## 十一、是否实现 Stage-05 内容

**否**。

---

## 十二、Python 语法检查命令

```bash
cd backend
python -m py_compile app/repositories/project_repo.py app/services/project_service.py app/routers/projects.py app/main.py run.py
```

结果：`EXIT:0`（通过）。

---

## 十三、已知环境限制

1. **当前 Ubuntu 无法访问 Windows MySQL**：无法实际执行 `CALL sp_archive_project` 和验证 OUT 参数读取
2. **存储过程未在当前环境验证**：会话变量读取 OUT 参数的逻辑基于 PyMySQL 官方文档和 MySQL 会话变量机制静态实现
3. **PyMySQL OUT 参数处理方式**：标准方式是 `SET @var` + `CALL` + `SELECT @var`，这在 PyMySQL 文档和实践中均得到确认
4. **CALL 后的结果集**：MySQL 中 `CALL proc()` 可能返回存储过程中任何 `SELECT` 的结果集，会话变量读取应单独执行

---

## 十四、需要 Codex 复审的重点

1. **OUT 参数读取方式**：确认使用 `SET @var` + `execute(CALL ... @out)` + `SELECT @var` 而非 `callproc() + fetchall()`
2. **不会误判成功**：确认 `row is None`（SELECT 无结果）时返回 `result_code=500` 而非默认成功
3. **result_code 分支处理**：确认 404 → `NotFoundException`，非零 → `ValidationException`，0 → `commit`
4. **fallback operation_logs**：确认 `archive_project_fallback()` 现在写入 `operation_logs`
5. **类型注解一致**：确认 repo 返回 `Tuple[int, str]`，service 解包为 `result_code, result_message`
6. **事务安全**：确认存储过程调用和外部事务（`get_db_transaction`）正确配合

---

## 十五、验收清单

- [x] OUT 参数使用会话变量方式读取（`SET @var` + `execute(CALL)` + `SELECT @var`）
- [x] `cursor.callproc()` 不再用于读取 OUT 参数
- [x] `row is None`（无法读取）返回 `result_code=500`，不默认成功
- [x] `result_code=0` → 成功
- [x] `result_code=404` → `NotFoundException` + `rollback`
- [x] `result_code!=0` → `ValidationException` + `rollback`
- [x] `archive_project_fallback()` 补齐 `operation_logs` 写入
- [x] `fallback` 项目不存在时 `rollback` 而非 `commit`
- [x] repo 和 service 返回类型签名一致（`Tuple[int, str]`）
- [x] 未修改 `database/*`、`frontend/*`
- [x] 未实现 Stage-05 内容
- [x] Python 语法检查通过

---

**本修复完成后停止，等待 Codex 复审。**
