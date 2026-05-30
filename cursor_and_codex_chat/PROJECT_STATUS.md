# 项目当前状态

## 当前阶段

Stage-07 模型管理、Mock 模型调用、调用日志和成本记录模块：已发布任务，等待 Cursor 开发。

Stage-06 提示词模板管理模块已通过 Codex 审查。

## 审查结果摘要

- Stage-06 9 个接口已实现并注册；
- 任务类型列表默认过滤 `is_deleted = 0` 和 `status = 'active'`；
- 提示词模板列表支持分页、任务类型过滤和关键字搜索；
- 提示词模板创建、更新、软删除均有权限控制、事务和 `operation_logs`；
- 提示词版本创建、列表、启用功能完整；
- 启用版本会更新 `prompt_templates.current_version_id`；
- SQL 集中在 `prompt_repo.py`，未发现用户输入拼接 SQL；
- 未发现本轮越界修改 `database/`、`frontend/` 或 `docs/01_数据库Schema冻结说明.md`；
- 未发现 AI 调用、审核中心、成果库、统计看板或前端页面越界实现；
- Python 语法编译检查通过。

## 当前技术栈

- 前端：Vue3 + Vite + Element Plus + Pinia + Vue Router + ECharts
- 后端：Python FastAPI
- 数据库：MySQL 8.0
- 数据库访问：参数化 SQL / Repository 层
- 模型调用：Mock ModelAdapter + 可选真实模型 API

## 当前任务

- `TASK-007-model-invocation-log.md`：模型管理、Mock 模型调用、调用日志和成本记录模块

## 未完成内容

- Windows MySQL 环境下补做 Stage-01 SQL 顺序导入验证
- Stage-02/Stage-03/Stage-04/Stage-05/Stage-06 后端服务运行级验证和接口 curl 验证
- Stage-07 模型调用与调用日志
- Stage-08 人工编辑与乐观锁
- Stage-09 审核中心
- Stage-10 成果库
- Stage-11 统计看板
- Stage-12 测试与报告截图
