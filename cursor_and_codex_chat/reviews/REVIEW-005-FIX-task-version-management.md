# REVIEW-005-FIX 任务与版本管理模块复审报告

## 1. 审查结论

审查结论：通过。

Cursor 已修复 `REVIEW-005-task-version-management.md` 中列出的 5 个阻塞问题。Stage-05 Fix 静态复审通过，允许进入 Stage-06。

已发布：

- `cursor_and_codex_chat/tasks/todo/TASK-006-prompt-template.md`

## 2. 5 个阻塞问题是否全部修复

结论：已全部修复。

### 2.1 get_output_by_id() 字段错误

结论：已修复。

检查结果：

- `task_repo.get_output_by_id()` 不再使用不存在的 `t.task_title`；
- 已改为 `t.title AS task_title`；
- 代码范围内未发现错误的 `t.task_title` 引用；
- 输出详情接口不会再因该字段名导致 SQL 报错。

### 2.2 版本时间线是否只返回指定 output_id 的父版本链

结论：已修复。

检查结果：

- 时间线查询从指定 `output_id` 作为 CTE 锚点开始；
- 递归方向为沿 `parent_output_id` 向上追溯父版本；
- `ORDER BY depth DESC` 返回最早父版本到当前版本；
- 不再从当前任务下所有根版本开始；
- 不再返回兄弟版本、子版本或同任务下其他无关版本链；
- service 层先通过目标 output 查询 task，再校验当前用户是否有权访问该 output 所属项目；
- 正常应用数据下不会泄露其他项目版本。

说明：数据库层面仅有 `parent_output_id` 自引用外键，没有约束父版本必须与子版本属于同一 task。当前创建接口已校验父版本归属当前 task，因此按应用路径创建的数据是安全的。若后续需要抵御历史脏数据，可在递归 SQL 中追加 `p.task_id = pc.task_id` 作为防御性条件。

### 2.3 时间线 SQL 是否集中在 task_repo.py

结论：已修复。

检查结果：

- `WITH RECURSIVE` 时间线 SQL 已移入 `backend/app/repositories/task_repo.py` 的 `get_output_parent_chain()`；
- `task_service.py` 不再直接写时间线 SQL；
- service 层仅负责鉴权、调用 repository 和转换返回结构；
- 符合 Repository 层集中 SQL 的要求。

### 2.4 edit_summary 是否保存

结论：已修复。

检查结果：

- `tasks.py` 将 `body.edit_summary` 传入 service；
- `task_service.create_manual_output()` 接收并传给 repository；
- `task_repo.create_manual_output()` 插入 `task_outputs.edit_summary`；
- 输出详情转换中返回 `edit_summary`；
- 未发现静默丢弃用户提交 `edit_summary` 的问题。

### 2.5 version_no 是否在事务内计算

结论：已修复，课程版可接受。

检查结果：

- `version_no` 生成已移入 `create_manual_output()` 的 `get_db_transaction()` 内；
- `get_next_version_no_for_update()` 使用同一个事务连接 `conn`；
- 版本号计算、`task_outputs` 插入、`operation_logs` 写入均在同一事务中；
- 未修改数据库结构；
- 当前使用 `SELECT MAX(version_no) ... FOR UPDATE`，相较事务外计算已修复主要并发风险。

残余风险说明：

- 在极端并发和不同 MySQL 隔离级别下，聚合查询 `MAX(version_no) FOR UPDATE` 对空结果集/间隙锁的行为依赖 InnoDB 锁策略。课程版可接受；如后续进入生产级，应考虑锁定 `project_tasks` 当前任务行后再计算版本号，或通过数据库唯一约束配合重试机制进一步增强。

## 3. 是否发现新问题

未发现新的阻塞问题。

非阻塞建议：

- 时间线递归 SQL 可追加 `p.task_id = pc.task_id`，防御历史脏数据或手工 SQL 造成的跨任务父链；
- 后续可校验任务创建/更新时的 `assignee_id` 是否属于当前项目成员，提升权限语义严谨性。

## 4. 是否发现越界修改

未发现本轮越界修改。

检查结果：

- 未发现 Stage-05 Fix 修改 `database/`；
- 未发现修改 `frontend/`；
- 未发现修改 `docs/01_数据库Schema冻结说明.md`；
- 未发现 AI 调用；
- 未发现提示词模板实现；
- 未发现审核中心实现；
- 未发现成果库实现；
- 未发现 Stage-06 内容提前实现。

说明：`git status` 中仍可见 `database/` 与 `docs/01_数据库Schema冻结说明.md` 的历史未提交修改，但文件时间检查显示这些不是本轮 Fix 产生的修改。

## 5. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py app/services/project_service.py app/repositories/project_repo.py
```

结果：通过。

环境限制：当前 Ubuntu/WSL 环境无法访问 Windows MySQL，本轮未执行真实 SQL 和接口联调。按用户要求进行静态审查，不因此阻塞 Stage-05 通过。

## 6. 是否允许进入 Stage-06

允许。

Stage-05 任务与版本管理模块通过 Fix 复审，可以进入 Stage-06：提示词模板管理模块。
