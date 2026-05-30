# HANDOFF-005-FIX：Stage-05 任务与版本管理模块修复版

## 任务状态

**完成** — Stage-05 的 5 个阻塞问题均已修复。

---

## 一、Codex 未通过原因

| # | 问题 | 严重程度 |
|---|---|---|
| 1 | `task_repo.get_output_by_id()` 使用了不存在的字段 `t.task_title` | 阻塞 |
| 2 | 版本时间线返回整个任务下所有根版本展开的树，而非指定 output_id 的父链 | 阻塞 |
| 3 | 时间线 SQL 写在 `task_service.py`，违反 Repository 层集中 SQL 规则 | 阻塞 |
| 4 | 人工输出版本接口未保存 `edit_summary` | 阻塞 |
| 5 | `version_no` 在事务外计算，并发创建时可能重复 | 阻塞 |

---

## 二、本次修复的问题列表

1. `t.task_title` → `t.title AS task_title`
2. 时间线递归从 `output_id` 向上追溯父链（而非查所有根版本）
3. 时间线 SQL 移入 `task_repo.get_output_parent_chain()`
4. `edit_summary` 通过 `conn` 传入并写入 `task_outputs.edit_summary`
5. `version_no` 计算移入事务内，使用 `SELECT ... FOR UPDATE` 锁

---

## 三、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/task_repo.py` | 重写 | 修复 `t.task_title`；新增 `get_output_parent_chain()`；新增 `get_next_version_no_for_update()`（事务内）；`create_manual_output()` 增加 `edit_summary` 参数；删除旧的 `get_next_version_no()` |
| `backend/app/services/task_service.py` | 重写 | 删除内联 SQL（时间线）；改用 `task_repo.get_output_parent_chain()`；`create_manual_output()` 接收并传递 `edit_summary`；`version_no` 改为事务内 `get_next_version_no_for_update()` |
| `backend/app/routers/tasks.py` | 修改 | `create_manual_output()` handler 增加 `edit_summary=body.edit_summary` 传参 |
| `cursor_and_codex_chat/handoff/HANDOFF-005-FIX-task-version-management.md` | 新建 | 本修复报告 |

---

## 四、get_output_by_id() 字段错误如何修复

**修改前**（错误）：

```sql
t.task_title   -- 不存在的字段名
```

**修改后**（正确）：

```sql
t.title AS task_title   -- project_tasks.title 别名
```

所有使用 `project_tasks` 标题的 SQL 均使用 `t.title AS task_title`。

---

## 五、版本时间线现在如何只返回指定 output_id 的父版本链

### 修复前（错误）

递归从所有 `parent_output_id IS NULL` 的根版本开始，查整个 task 下所有版本树。

### 修复后（正确）

使用 WITH RECURSIVE，从目标 `output_id` 向上递归找 `parent_output_id`：

```sql
WITH RECURSIVE parent_chain AS (
    -- 锚点：当前 output
    SELECT
        o.output_id, o.parent_output_id, o.task_id,
        o.version_no, o.output_title, o.source_type,
        o.created_by, o.created_at, 0 AS depth
    FROM task_outputs o
    WHERE o.output_id = %s AND o.is_deleted = 0

    UNION ALL

    -- 递归：找父版本（通过 parent_output_id JOIN）
    SELECT
        p.output_id, p.parent_output_id, p.task_id,
        p.version_no, p.output_title, p.source_type,
        p.created_by, p.created_at, pc.depth + 1 AS depth
    FROM task_outputs p
    INNER JOIN parent_chain pc ON p.output_id = pc.parent_output_id
    WHERE p.is_deleted = 0
)
SELECT ... ORDER BY depth DESC
```

结果按 `depth DESC` 返回（最深=最老的父版本），service 层不反转（已经是正确顺序）。

### 效果示例

假设版本链：root(v1) → child(v2) → grandchild(v3)

`depth` 值：root=1, child=2, grandchild=3

`ORDER BY depth DESC`：grandchild(3) → child(2) → root(1)  （最新 → 最老）

这正是"从最早父版本到当前版本"的语义。

---

## 六、时间线 SQL 是否已移入 task_repo.py

**是**。`task_service.py` 中不再有任何内联 SQL。

service 层调用 `task_repo.get_output_parent_chain(output_id)` 获取结果。

---

## 七、edit_summary 是否已保存到 task_outputs.edit_summary

**是**。调用链完整：

1. `tasks.py` router：`edit_summary=body.edit_summary` 传给 service
2. `task_service.py`：`edit_summary` 参数透传给 repo
3. `task_repo.py` `create_manual_output()`：`edit_summary` 写入 INSERT 的 VALUES

```python
# router
edit_summary=body.edit_summary,

# service
def create_manual_output(..., edit_summary: Optional[str] = None, ...):
    task_repo.create_manual_output(..., edit_summary=edit_summary, ...)

# repo
def create_manual_output(..., edit_summary: Optional[str], ...):
    cursor.execute("""
        INSERT INTO task_outputs ...
            (..., edit_summary, ...)
        VALUES (..., %s, ...)
    """, (..., edit_summary, ...))
```

---

## 八、version_no 是否已在事务内计算

**是**。修复后的调用链：

```python
with get_db_transaction() as conn:
    # 1. 版本号生成（带 FOR UPDATE 锁）
    next_version = task_repo.get_next_version_no_for_update(
        task_id=task_id,
        conn=conn,
    )

    # 2. 插入新版本
    output_id = task_repo.create_manual_output(
        ..., version_no=next_version, ...
    )

    # 3. 写日志
    user_repo.insert_operation_log_with_conn(..., conn=conn)

    # 4. 提交
    conn.commit()
```

---

## 九、是否使用 SELECT ... FOR UPDATE

**是**。`get_next_version_no_for_update()` 使用：

```python
cursor.execute(
    """
    SELECT MAX(version_no) AS max_ver FROM task_outputs
    WHERE task_id = %s AND is_deleted = 0
    FOR UPDATE
    """,
    (task_id,),
)
```

`FOR UPDATE` 锁住当前 task 的所有未删除输出版本行（InnoDB 间隙锁机制），防止并发事务同时分配相同 version_no。

---

## 十、是否修改数据库结构

**否**。

---

## 十一、是否修改 frontend

**否**。

---

## 十二、是否实现 AI 调用

**否**。

---

## 十三、是否实现提示词模板

**否**。

---

## 十四、是否实现审核中心或成果库

**否**。

---

## 十五、Python 语法检查命令

```bash
cd backend
python -m py_compile app/repositories/task_repo.py app/services/task_service.py app/routers/tasks.py app/main.py
```

结果：`EXIT:0`（通过）。

---

## 十六、当前环境限制

1. **当前 Ubuntu/WSL 无法访问 Windows MySQL**：无法执行真实 SQL 验证，所有验证基于静态代码审查
2. **MySQL 8.0 依赖**：`WITH RECURSIVE` 要求 MySQL 8.0+，当前假设数据库为 MySQL 8.0
3. **`FOR UPDATE` 锁范围**：`SELECT ... FOR UPDATE` 在当前 task 下所有 `is_deleted=0` 的 `task_outputs` 行上加记录锁，阻止并发版本号分配

---

## 十七、需要 Codex 复审的重点

1. **字段修复**：`t.title AS task_title` 确认存在于所有相关 SQL
2. **时间线递归方向**：确认递归是"向上找父版本"（`child.parent_output_id → parent.output_id`），不是"向下查子版本"
3. **时间线返回顺序**：`ORDER BY depth DESC` 确认返回从最早到当前的顺序
4. **SQL 集中**：确认 `task_service.py` 中无内联 SQL
5. **edit_summary 链路**：router → service → repo 完整链路确认
6. **version_no 事务内**：`FOR UPDATE` 锁确认在事务内，`get_next_version_no_for_update` 在 `conn` 传入后调用
7. **事务一致性**：确认 `version_no 计算 + 版本插入 + 日志插入` 在同一事务
8. **无越界**：确认未实现 AI 调用、提示词模板、审核中心、成果库

---

## 十八、验收清单

- [x] `GET /api/outputs/{output_id}` SQL 字段 `t.title AS task_title` 正确
- [x] 时间线从目标 output_id 向上追溯父版本链，不返回无关版本
- [x] 时间线 SQL 位于 `task_repo.py`，`task_service.py` 无内联 SQL
- [x] 人工输出版本能保存 `edit_summary`
- [x] `version_no` 生成在事务内（`SELECT ... FOR UPDATE`）
- [x] 所有写操作与 `operation_logs` 同一事务
- [x] 所有 SQL 参数化
- [x] 未修改 `database/*`、`frontend/*`
- [x] 未实现 AI 调用、提示词模板、审核中心、成果库
- [x] Python 语法检查通过

---

**本修复完成后停止，等待 Codex 复审。**
