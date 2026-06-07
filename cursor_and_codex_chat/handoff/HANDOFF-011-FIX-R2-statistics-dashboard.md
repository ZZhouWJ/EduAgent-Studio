# HANDOFF-011-FIX-R2：Stage-11 统计看板第二次修复版

## 任务状态

**完成** — Stage-11 Fix R2 两个剩余问题已修复。

---

## 一、Codex 本轮剩余未通过原因

| # | 问题 | 严重程度 |
|---|---|---|
| P0-1 | `GET /api/statistics/projects?project_id=...` 走 `get_project_stats_by_id()` 返回字段不完整，缺少 `approved_output_count`、`invocation_count`、`total_cost` | 阻塞 |
| P0-2 | `GET /api/statistics/model-calls` 的 `project_id` 过滤存在参数错位、`project_join` 未使用、`sub_params` 残留等逻辑错误 | 阻塞 |

---

## 二、本次修复的问题列表

1. **`get_project_stats_by_id()`**：重写为与 `list_project_stats()` 字段完全对齐的 SQL
2. **`get_model_call_stats()`**：彻底重写，移除 `project_join`、`sub_params` 等残留变量，修复参数顺序

---

## 三、本次修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/repositories/statistics_repo.py` | 重写 `get_project_stats_by_id()` + 重写 `get_model_call_stats()` |
| `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-R2-statistics-dashboard.md` | 新建 |

**说明**：未修改 `database/*`、`frontend/*`、`docs/*`、`statistics_service.py`、`statistics.py`。

---

## 四、`get_project_stats_by_id()` 如何补齐字段

**修复前**：使用 `v_project_task_statistics` 视图，只返回 `total_members`、`total_tasks`、`total_outputs`、`total_adopted AS artifact_count`，缺少验收要求的 9 个字段。

**修复后**：重写为独立 SQL，9 个字段全部来自子查询：

| 字段 | 来源 |
|---|---|
| `project_id` | `projects.project_id` |
| `project_name` | `projects.project_name` |
| `member_count` | LEFT JOIN 子查询：`COUNT(project_members)`，`is_deleted = 0` |
| `task_count` | LEFT JOIN 子查询：`COUNT(project_tasks)`，`is_deleted = 0` |
| `output_count` | LEFT JOIN 子查询：`COUNT(DISTINCT task_outputs.output_id)`，通过 `task_outputs.task_id → project_tasks` |
| `approved_output_count` | LEFT JOIN 子查询：`COUNT(DISTINCT task_outputs.output_id)`，`status = 'approved'` |
| `artifact_count` | LEFT JOIN 子查询：`COUNT(adopted_outputs)`，`is_deleted = 0` |
| `invocation_count` | LEFT JOIN 子查询：`COUNT(ai_invocations)` |
| `total_cost` | LEFT JOIN 子查询：`SUM(cost_records.total_cost)` |

所有子查询使用 `LEFT JOIN` + `COALESCE(..., 0)` 避免 NULL 和笛卡尔积。

---

## 五、单项目统计和项目列表统计字段是否已统一

**是**。两者均返回以下 9 个字段：

- `project_id`
- `project_name`
- `member_count`
- `task_count`
- `output_count`
- `approved_output_count`
- `artifact_count`
- `invocation_count`
- `total_cost`

差异：`get_project_stats_by_id()` 仅返回单条，`list_project_stats()` 返回列表。

---

## 六、`model-calls` 的 project_id 过滤如何修复

**修复前问题**：

- `project_join` 变量被构造但从未使用
- `sub_params = list(params)` 产生后从未使用
- 带 `project_id + date_from/date_to` 时，`params` 顺序与 SQL 占位符错位
- 非 admin 带 `project_id` 时，`params` 中 `project_id` 排在 `user_id` 前，可能绑定到错误位置
- admin 带 `project_id` 时，先查 model_id 再从视图返回全局统计（跨项目）

**修复后逻辑**：

```
参数顺序（与 SQL 占位符严格对应）：
  [1] ai.project_id = %s        ← project_id 明确传入时
      或  ai.project_id IN (...%) ← 非 admin 无 project_id 时
  [2] ai.created_at >= %s       ← date_from
  [3] ai.created_at <= %s       ← date_to

admin 有 project_id：params = [project_id]，WHERE 有 ai.project_id = %s
admin 无 project_id：params = []，无 project 过滤条件
非 admin 有 project_id：params = [project_id]，WHERE 有 ai.project_id = %s
非 admin 无 project_id：先查 project_ids → params = [id1, id2, ...]，WHERE 有 ai.project_id IN (...%)
```

**所有 4 种组合参数顺序与占位符完全对应，无错位风险。**

---

## 七、`model-calls` 的 `date_from`/`date_to` 参数顺序如何保证正确

**修复后**：

1. 所有参数统一追加到 `params` 列表末尾
2. 所有条件统一追加到 `conditions` 列表
3. `where_clause = " AND ".join(c for c in conditions if c)` 动态拼接
4. SQL 中占位符按 `conditions` 追加顺序出现

```python
conditions = ["m.is_deleted = 0", project_filter, date_filter]
# order: [is_deleted, project, date_from, date_to]
# params: [project_id(s), date_from, date_to]
```

无论条件是否缺失，参数顺序始终与占位符顺序一致。

---

## 八、非 admin 不带 `project_id` 时如何限制为参与项目范围

**修复后**：

```python
elif not is_admin:
    # 非 admin 无 project_id：限制在参与项目范围内
    member_sql = """
        SELECT DISTINCT project_id FROM project_members
        WHERE user_id = %s AND is_deleted = 0
    """
    # 先查参与项目列表
    # 构建 ai.project_id IN (%s, %s, ...)
    # params = [id1, id2, ...]
```

先在 repo 层查询 `project_members` 获取该用户参与的项目 ID 列表，再作为 `ai.project_id IN (...)` 条件过滤，严格限制统计范围。

service 层 `check_user_can_access_project()` 在有明确 `project_id` 时做权限校验，无 `project_id` 时 repo 层做范围限制。

---

## 九、是否修改 database

**否**。

---

## 十、是否修改 frontend

**否**。

---

## 十一、是否实现 Stage-12 内容

**否**。

---

## 十二、Python 语法检查命令

```bash
cd backend
python -m py_compile app/repositories/statistics_repo.py app/services/statistics_service.py
```

结果：`EXIT:0`（通过）。

---

## 十三、当前环境限制

- 当前环境无 MySQL，无法真实执行 SQL 验证，基于静态代码审查
- 未修改 `database/` 目录，未修改表结构

---

## 十四、需要 Codex 复审的重点

1. **`get_project_stats_by_id()` 字段**：确认返回 9 个字段 `project_id, project_name, member_count, task_count, output_count, approved_output_count, artifact_count, invocation_count, total_cost`
2. **`list_project_stats()` 字段**：确认两者字段名完全一致
3. **`model-calls` 参数顺序**：确认 4 种组合（admin/non-admin × project_id 有/无）的 `params` 顺序与 `conditions` 顺序一致
4. **无残留变量**：确认 `project_join`、`sub_params` 等变量已从函数中移除
5. **无跨项目统计**：`ai.project_id` 过滤是否在所有路径中都存在
6. **非 admin 范围限制**：无 `project_id` 时是否通过 `project_members` 子查询限制
7. **service 层权限校验**：`project_id` 传入时 service 层 `check_user_can_access_project()` 是否仍生效
8. **无越界**：确认未修改 `database/*`、`frontend/*`、`docs/*`

---

## 十五、验收清单

- [x] `get_project_stats_by_id()` 返回 9 个统一字段
- [x] `list_project_stats()` 与 `get_project_stats_by_id()` 字段名一致
- [x] `get_model_call_stats()` 移除 `project_join`、`sub_params`
- [x] `model-calls` 参数顺序与占位符一致
- [x] `model-calls` 无跨项目统计
- [x] 非 admin 无 `project_id` 通过 `project_members` 限制范围
- [x] Python 语法检查通过
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`

---

**本修复完成后停止，等待 Codex 复审。**
