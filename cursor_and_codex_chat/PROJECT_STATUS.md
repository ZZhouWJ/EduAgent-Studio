# 项目当前状态

## 当前阶段

Stage-11 统计看板与课程展示数据模块：**Codex 审查不通过，已发布 `TASK-011-FIX-statistics-dashboard.md`，等待 Cursor 修复。**

Stage-10 成果库与分支合并模块已通过 Fix R2 复审。

## Stage-11 审查结果摘要

- Python 语法检查通过；
- 7 个统计接口已实现并注册；
- 阻塞问题 1：`statistics_repo.py` 引用了不存在的 `ai_invocations.is_deleted`；
- 阻塞问题 2：成员贡献统计引用了不存在的 `task_outputs.project_id`；
- 阻塞问题 3：项目统计返回字段缺少 `member_count`、`task_count`、`output_count`、`approved_output_count`、`invocation_count`、`total_cost` 等验收字段；
- 阻塞问题 4：模型调用统计缺少 `call_count` 字段；
- 阻塞问题 5：非 admin 无 project_id 时，成员贡献统计只返回当前用户本人，不符合项目成员贡献排行场景；
- 暂不允许进入 Stage-12。

## 当前技术栈

- 前端：Vue3 + Vite + Element Plus + Pinia + Vue Router + ECharts
- 后端：Python FastAPI
- 数据库：MySQL 8.0
- 数据库访问：参数化 SQL / Repository 层
- 模型调用：Mock ModelAdapter + 可选真实模型 API

## 当前任务

- `TASK-011-FIX-statistics-dashboard.md`：修复统计看板与课程展示数据模块审查问题

## 未完成内容

- Windows MySQL 环境下补做 Stage-01 SQL 顺序导入验证
- Stage-02/Stage-03/Stage-04/Stage-05/Stage-06/Stage-07/Stage-08/Stage-09/Stage-10/Stage-11 后端服务运行级验证和接口 curl 验证
- Stage-11 Fix 复审
- Stage-12 后端整体联调、运行验证与课程报告素材整理

