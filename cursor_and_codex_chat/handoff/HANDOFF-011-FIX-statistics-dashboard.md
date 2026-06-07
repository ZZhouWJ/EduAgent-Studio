# HANDOFF-011-FIX：Stage-11 统计看板与课程展示数据模块修复版

## 任务状态

**完成** — Stage-11 Fix 修复问题均已处理。

---

## 一、Codex 未通过原因

| # | 问题 | 严重程度 |
|---|---|---|
| 1 | `ai_invocations.is_deleted` 字段不存在（Schema 中 ai_invocations 是审计表无软删）| 阻塞 |
| 2 | `task_outputs.project_id` 字段不存在（task_outputs 只有 task_id）| 阻塞 |
| 3 | 项目统计返回字段缺少 `approved_output_count`、`invocation_count`、`total_cost` | 阻塞 |
| 4 | 模型调用统计缺少 `call_count` 字段 | 阻塞 |
| 5 | 非 admin 无 project_id 时成员贡献统计只返回本人，不符合项目成员贡献排行场景 | 阻塞 |

---

## 二、本次修复的问题列表

1. **移除 `ai_invocations.is_deleted`**：3 处已删除（model-calls 简单场景、复杂场景 JOIN、成员贡献的 invocation_count 子查询）
2. **修复 `task_outputs.project_id`**：output_created_count 改为通过 `task_outputs.task_id → project_tasks.project_id` 关联
3. **补齐项目统计字段**：新增 `approved_output_count`、`invocation_count`、`total_cost`
4. **补齐 call_count**：模型调用统计两处均新增 `call_count` 别名
5. **修复成员贡献统计权限**：非 admin 无 project_id 时限制在参与项目范围，返回所有成员贡献排行

---

## 三、本次修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/repositories/statistics_repo.py` | 5 处 SQL 修复（详见下文） |
| `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-statistics-dashboard.md` | 新建 |

**说明**：未修改 `database/*`、`frontend/*`、`docs/*`、`statistics_service.py`、`statistics.py`。

---

## 四、ai_invocations.is_deleted 如何修复

**修复前（3 处报错）**：

1. model-calls 简单场景：使用 `ai_invocations WHERE project_id = %s AND is_deleted = 0`
2. model-calls 复杂场景 JOIN：`ai.model_id = ai.model_id AND ai.is_deleted = 0`
3. 成员贡献 invocation_count：`ai.project_id = pm.project_id AND ai.created_by = pm.user_id AND ai.is_deleted = 0`

**修复后**：

1. 简单场景：`ai_invocations WHERE project_id = %s`（无 is_deleted 条件）
2. 复杂场景 JOIN：`ai.model_id = ai.model_id`（无 is_deleted 条件）
3. invocation_count 子查询：`ai.project_id = pm.project_id AND ai.created_by = pm.user_id`（无 is_deleted 条件）

**说明**：`ai_invocations` 是审计表（Schema 说明无业务软删），通过关联 `projects`/`project_tasks` 的 `is_deleted` 字段间接过滤无效记录。

---

## 五、task_outputs.project_id 如何修复

**修复前（报错）**：

```sql
(SELECT COUNT(*) FROM task_outputs o
 WHERE o.project_id = pm.project_id   -- task_outputs 没有 project_id！
   AND o.created_by = pm.user_id
   AND o.is_deleted = 0)
```

**修复后（正确关联）**：

```sql
(SELECT COUNT(*) FROM task_outputs o
 INNER JOIN project_tasks pt ON o.task_id = pt.task_id AND pt.is_deleted = 0
 WHERE pt.project_id = pm.project_id
   AND o.created_by = pm.user_id
   AND o.is_deleted = 0)
```

---

## 六、项目统计补齐了哪些字段

`GET /api/statistics/projects` SQL 补齐字段：

| 字段 | 数据来源 |
|---|---|
| `member_count` | 来自视图 `v.total_members`（别名）|
| `task_count` | 来自视图 `v.total_tasks`（别名）|
| `output_count` | 来自视图 `v.total_outputs`（别名）|
| `approved_output_count` | LEFT JOIN 子查询：`task_outputs.status = 'approved'` |
| `artifact_count` | 来自视图 `v.total_adopted`（别名）|
| `invocation_count` | LEFT JOIN 子查询：`COUNT(ai_invocations)` |
| `total_cost` | LEFT JOIN 子查询：`SUM(cost_records.total_cost)` |

所有聚合使用 `LEFT JOIN` 子查询避免笛卡尔积重复计数，`COALESCE(..., 0)` 处理空值。

---

## 七、模型调用统计是否补齐 call_count

**是**。两处均已补齐：

1. **简单场景**（直接用视图）：显式 SELECT 中包含 `v.total_invocations AS call_count`
2. **复杂场景**（直接 JOIN 过滤）：`COUNT(DISTINCT ai.invocation_id) AS call_count`

同时保留 `total_invocations` 以兼容视图原字段名。

返回字段完整列表：

- `model_id`、`model_name`、`display_name`、`provider_name`
- `call_count`（验收要求）
- `total_invocations`（视图原字段）
- `success_count`、`failed_count`、`timeout_count`、`blocked_count`
- `total_input_tokens`、`total_output_tokens`、`total_tokens`
- `avg_latency_ms`、`success_rate`

---

## 八、非 admin 无 project_id 时成员贡献统计规则如何修复

**修复前**：

```python
if not is_admin:
    member_filter = " AND pm.user_id = %s"  # 只返回当前用户本人！
    params.append(user_id)
```

**修复后**：

```python
if project_id is not None:
    # 指定了 project_id：只统计该项目
    project_scope_filter = " AND pm.project_id = %s"
    params.append(project_id)
elif not is_admin:
    # 非 admin 未指定 project_id：限制在参与项目范围内
    project_scope_filter = " AND pm.project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)"
    params.append(user_id)
# admin 无 project_id 时：无 project_scope_filter，查全部
```

**四种场景**：

| 角色 | project_id | 行为 |
|---|---|---|
| admin | 未指定 | 查看全局所有成员贡献排行 |
| admin | 指定 | 查看指定项目所有成员贡献排行 |
| 非 admin | 指定 | 校验参与该项目 → 返回该项目所有成员贡献排行 |
| 非 admin | 未指定 | **限制在参与项目范围 → 返回参与项目内所有成员贡献排行** |

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

1. **`ai_invocations.is_deleted`**：全局搜索 `statistics_repo.py` 确认无任何 `ai_invocations.is_deleted` 引用
2. **`task_outputs.project_id`**：确认 output_created_count 通过 `project_tasks` 获取 project_id
3. **项目统计字段**：确认 `approved_output_count`、`invocation_count`、`total_cost` 均在 SELECT 中
4. **call_count**：确认两处 model-calls 逻辑均包含 `call_count`
5. **成员贡献权限**：确认非 admin 无 project_id 时不过滤 `pm.user_id`，而是限制 `pm.project_id IN (子查询)`
6. **LEFT JOIN 子查询**：确认 `approved_output_count`、`invocation_count`、`total_cost` 使用子查询 LEFT JOIN 而非直接多表 JOIN（避免笛卡尔积）
7. **无越界**：确认未修改 `database/*`、`frontend/*`、`docs/*`

---

## 十五、验收清单

- [x] `ai_invocations.is_deleted` 已从 3 处删除
- [x] `task_outputs.project_id` 改为 `task_outputs → project_tasks` 关联
- [x] 项目统计补齐 `approved_output_count`
- [x] 项目统计补齐 `invocation_count`
- [x] 项目统计补齐 `total_cost`
- [x] 模型调用统计补齐 `call_count`（两处）
- [x] 非 admin 无 project_id 时返回参与项目范围所有成员
- [x] Python 语法检查通过
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`

---

**本修复完成后停止，等待 Codex 复审。**
