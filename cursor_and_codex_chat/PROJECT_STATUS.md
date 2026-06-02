# 项目当前状态

## 当前阶段

**最终验收准备。**

Stage-01 到 Stage-17 已完成开发、审查、修复复审与最终收尾文档复审。`REVIEW-017-FIX-R2-final-polish-run-report.md` 已确认最后一个旧接口文档残留问题修复完成。

## 阶段完成标记

- 后端阶段完成：Stage-01 到 Stage-12 已完成并通过对应审查/复审。
- 前端阶段完成：Stage-13 到 Stage-16 已完成并通过对应审查/复审。
- 文档与截图素材完成：Stage-17 已完成最终润色、运行说明、API 路由清单、截图清单、最终检查清单和课程报告素材整理。
- 当前进入最终验收准备。
- 仍需在本地 Windows MySQL + Node 环境补做实际运行截图和联调验证。

## 当前技术栈

- 前端：Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router + ECharts，基于 V3 Admin Vite 开源模板二次开发；
- 后端：Python FastAPI；
- 数据库：MySQL 8.0；
- 数据库访问：参数化 SQL / Repository 层；
- 模型调用：Mock ModelAdapter，支持模型调用日志与成本记录；
- 文档材料：README、API 路由清单、测试报告素材、截图清单、最终检查清单已整理。

## 最终验收前待补做

1. 在 Windows MySQL 环境按顺序执行：
   - `database/01_create_database.sql`
   - `database/02_create_tables.sql`
   - `database/03_create_indexes.sql`
   - `database/04_insert_initial_data.sql`
   - `database/05_create_views.sql`
   - `database/06_create_stored_procedures.sql`
   - `database/07_test_queries.sql`
2. 在本地 Python 环境安装后端依赖并启动 FastAPI；
3. 在本地 Node 环境安装前端依赖并执行构建；
4. 联调登录、项目、任务、AI 生成、编辑批注、审核、成果库、统计看板等关键路径；
5. 按截图清单补齐课程报告所需截图；
6. 将本地实际运行结果补入系统测试与结果分析材料。

## 环境限制说明

远程 Ubuntu / WSL 环境当前无法直接访问 Windows MySQL，也缺少 Node 运行环境，因此远程审查阶段主要完成静态审查、后端 py_compile 和文档一致性检查。最终运行截图与接口联调验证需要在本地 Windows MySQL + Node 环境补做。
