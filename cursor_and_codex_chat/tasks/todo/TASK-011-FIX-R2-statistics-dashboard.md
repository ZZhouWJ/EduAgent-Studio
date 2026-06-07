# TASK-011-FIX-R2：修复统计看板第二次审查问题

## 任务状态

Codex 第二次修复复审不通过，已发布 TASK-011-FIX-R3。

## 一、任务目标

修复 Codex 复审指出的 2 个剩余阻塞问题：

1. `GET /api/statistics/projects?project_id=...` 返回字段不完整
2. `GET /api/statistics/model-calls` 的 project_id 过滤参数错位

## 二、修复内容

### P0-1：项目统计单条返回字段补齐

`get_project_stats_by_id()` 重写为独立 SQL，返回 9 个统一字段：
`project_id, project_name, member_count, task_count, output_count, approved_output_count, artifact_count, invocation_count, total_cost`

### P0-2：模型调用统计过滤逻辑重写

`get_model_call_stats()` 彻底重写：
- 移除 `project_join`、`sub_params` 等残留变量
- 参数顺序与 SQL 占位符严格对应
- `ai.project_id` 过滤在所有路径中可靠生效
- 非 admin 无 `project_id` 时通过 `project_members` 子查询限制范围

## 三、修改文件

- `backend/app/repositories/statistics_repo.py`
- `cursor_and_codex_chat/handoff/HANDOFF-011-FIX-R2-statistics-dashboard.md`
