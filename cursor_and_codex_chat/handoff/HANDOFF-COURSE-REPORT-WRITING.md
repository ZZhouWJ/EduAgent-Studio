# HANDOFF-COURSE-REPORT-WRITING

## 1. 本次阅读的主要资料

已读取本地模板 `副本报告封面（2026).docx`，确认《数据库管理实务》课程报告结构、评分要求和格式要求。已核对远程 README、backend/README、frontend/README、docs 目录主要项目说明、演示流程、截图清单、系统测试素材、最终检查清单、项目开发文档，数据库 01-08 脚本，backend/scripts/route_list.md，backend/scripts/test_report_material.md，frontend/scripts/route_list.md，后端 routers/services/repositories 摘要，前端 router/api/pages，PROJECT_STATUS.md、TASK_BOARD.md，以及最近成熟产品修复审查与 handoff。

## 2. 报告生成文件

- docs/数据库管理实务课程报告.md
- docs/数据库管理实务课程报告_图片占位清单.md
- docs/数据库管理实务课程报告_待补截图清单.md
- cursor_and_codex_chat/handoff/HANDOFF-COURSE-REPORT-WRITING.md

## 3. 报告章节结构

摘要、一 需求分析、二 系统设计与技术实现、三 系统测试与结果分析、四 实验结论与总结、附录。

## 4. 图片占位数量

共 11 个图片占位。

## 5. 待补截图数量

共 24 个截图点。

## 6. 已基于代码确认的内容

- 27 张真实数据表、5 个视图、5 个存储过程和 3 个触发器已从 SQL 脚本确认。
- 后端路由模块包括 auth、users、projects、tasks、prompts、models、invocations、reviews、artifacts、statistics、logs。
- 前端页面包括登录、注册、Dashboard、项目、任务、AI生成、提示词、审核、成果、调用审计、成本、统计、模型、用户、日志、个人中心和 403。
- 注册接口为 `/api/auth/register`，包含 `confirm_password` 校验。
- 创建任务字段为 `title` 和 `task_type_id`。
- 正式另存接口为 `/api/outputs/{output_id}/save-as-new-version`。
- 提示词搜索参数为 `keyword`。
- 登录日志失败原因字段为 `failure_reason`。

## 7. 仍需本地运行验证的内容

- Windows MySQL 执行 database/01 到 07。
- 可选执行 `database/import_prompts.py` 初始化提示词模板。
- 后端服务启动、`/api/health`、`/api/health/db`。
- 前端 `npm install`、`npm run dev` 或 `npm run build`。
- 登录注册、项目、任务、AI生成、编辑批注、审核、成果采用、分支合并、统计看板等完整联调截图。

## 8. 是否虚构运行结果

否。

## 9. 是否修改业务代码

否。

## 10. 是否修改数据库结构

否。

## 11. 需要用户后续补充的内容

请在本地 Windows MySQL + Node 环境完成数据库导入、后端启动、前端启动、核心业务流程联调和截图，然后按照 `docs/数据库管理实务课程报告_待补截图清单.md` 补入最终报告。
