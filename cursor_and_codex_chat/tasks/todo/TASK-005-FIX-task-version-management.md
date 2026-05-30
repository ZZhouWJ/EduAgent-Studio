# TASK-005-FIX 任务与版本管理模块修复任务

## 任务目标

修复 Stage-05 审查中发现的任务与版本管理阻塞问题，使输出版本详情、版本时间线、人工输出版本创建满足验收要求。

本修复任务只允许修复 Stage-05 问题，不得进入 Stage-06。

## 允许修改文件

- `backend/app/repositories/task_repo.py`
- `backend/app/services/task_service.py`
- `backend/app/routers/tasks.py`
- `cursor_and_codex_chat/handoff/HANDOFF-005-FIX-task-version-management.md`

如确实需要调整路由注册，可少量修改：

- `backend/app/main.py`

但必须在 handoff 中说明原因。

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. AI 调用；
2. 提示词模板；
3. 审核中心；
4. 成果库；
5. 前端页面；
6. 统计看板；
7. Stage-06 内容。

## 必须修复的问题

### 1. 修复输出详情 SQL 字段错误

`task_repo.get_output_by_id()` 当前使用了不存在的字段：

```sql
t.task_title
```

`project_tasks` 表中字段名是：

```sql
title
```

请修复为：

```sql
t.title AS task_title
```

验收要求：

- `GET /api/outputs/{output_id}` 不会因为字段不存在报错；
- `create_manual_output()` 创建成功后能正常返回输出详情；
- `get_output_timeline()` 前置查询不会被该错误影响。

### 2. 修复版本时间线逻辑

当前时间线从当前任务下所有 `parent_output_id IS NULL` 的根版本开始递归，会返回整个任务的版本树。

必须改为只返回目标 `output_id` 的版本链：

- 从目标 `output_id` 开始向上递归查 `parent_output_id`；
- 或使用等价方式，只返回目标 output 的祖先链；
- 返回顺序必须是最早父版本 -> 当前版本；
- 不得返回同一任务下其他无关版本链；
- 不得泄露其他项目或其他任务的数据。

建议字段：

- `output_id`
- `parent_output_id`
- `version_no`
- `output_title`
- `source_type`
- `created_by`
- `created_at`
- `depth`

### 3. 将时间线 SQL 移入 repository

版本时间线 SQL 目前写在 `task_service.py` 中，违反 Stage-05 的分层要求。

请在 `task_repo.py` 中新增类似函数：

```python
def get_output_timeline(output_id: int, task_id: int) -> List[Dict[str, Any]]:
    ...
```

service 层只负责：

- 鉴权；
- 调用 repository；
- 转换返回结构；
- 抛出业务异常。

### 4. 保存 edit_summary

`CreateManualOutputRequest` 已包含 `edit_summary`，但当前 service/repository 没有保存。

请修复：

- router 将 `body.edit_summary` 传给 service；
- service 将 `edit_summary` 传给 repository；
- repository 插入 `task_outputs.edit_summary`；
- 如为空可保存 `NULL` 或合理默认值，但不得丢弃用户提交的值。

### 5. 修复 version_no 重复风险

当前 `get_next_version_no()` 在事务外执行 `MAX(version_no) + 1`，并发创建时可能生成重复版本号。

请将版本号生成纳入创建输出版本事务，并采取可避免重复的方案，例如：

- 在事务内对当前任务相关输出记录加锁后计算；
- 或锁定对应任务记录后计算；
- 或在数据库已有约束范围内使用其他可靠方案。

不得修改数据库 Schema。

### 6. 保持 operation_logs 同事务

修复后仍必须保证：

- 创建人工输出版本；
- 写入 `operation_logs`；
- 版本号生成所需锁定/查询；

在同一个事务内完成。

## 验收要求

1. 11 个 Stage-05 接口仍完整存在；
2. `GET /api/outputs/{output_id}` SQL 字段正确；
3. `GET /api/outputs/{output_id}/timeline` 只返回目标 output 的父链；
4. 时间线 SQL 位于 `task_repo.py`；
5. 人工输出版本能保存 `edit_summary`;
6. `version_no` 生成不再在事务外完成；
7. 不修改 `database/`；
8. 不修改 `frontend/`；
9. 不实现 Stage-06；
10. Python 语法检查通过。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py
```

如当前环境可连接 MySQL，请补充：

- 创建人工输出版本；
- 查询输出详情；
- 创建父子版本；
- 查询指定子版本时间线；
- 验证时间线不会返回同任务其他无关版本链。

如当前环境无法连接 Windows MySQL，请在 handoff 中明确说明，并给出静态验证结果。
