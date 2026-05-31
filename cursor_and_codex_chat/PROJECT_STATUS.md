# 项目当前状态

## 当前阶段

Stage-11 统计看板与课程展示数据模块：**已发布 `TASK-011-statistics-dashboard.md`，等待 Cursor 开发。**

Stage-10 成果库与分支合并模块已通过 Fix R2 复审。

## Stage-10 Fix R2 复审结果摘要

- Python 语法检查通过；
- `manual_merge` 中 `target_branch_id -> active` 已接收 affected_rows；
- `affected == 0` 时会 rollback 并抛出 `NotFoundException`；
- `source_branch -> merged` 的 affected_rows 检查仍保留；
- `merge_records` 与 `operation_logs` 在分支状态检查之后写入；
- 允许进入 Stage-11。

## 当前技术栈

- 前端：Vue3 + Vite + Element Plus + Pinia + Vue Router + ECharts
- 后端：Python FastAPI
- 数据库：MySQL 8.0
- 数据库访问：参数化 SQL / Repository 层
- 模型调用：Mock ModelAdapter + 可选真实模型 API

## 当前任务

- `TASK-011-statistics-dashboard.md`：统计看板与课程展示数据模块

## 未完成内容

- Windows MySQL 环境下补做 Stage-01 SQL 顺序导入验证
- Stage-02/Stage-03/Stage-04/Stage-05/Stage-06/Stage-07/Stage-08/Stage-09/Stage-10 后端服务运行级验证和接口 curl 验证
- Stage-11 统计看板与课程展示数据模块
- Stage-12 测试与报告截图

