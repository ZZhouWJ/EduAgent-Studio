# REVIEW-017-FIX 最终收尾文档复审报告

## 1. 审查结论

**需要继续修改。**

Stage-17 Fix 已修复上轮大部分阻塞问题：`docs/系统测试与结果分析素材.md` 已创建，根 README 的“用户注册”已清理，统计字段和主要文档中的成果列表接口也已修正。但本轮仍发现一个明确阻塞点：

- `backend/scripts/route_list.md` 仍将 `POST /api/outputs/{output_id}/save-as` 作为真实接口列出。

本轮复审要求明确将 `/save-as` 作为旧接口清理，允许它只出现在“不要使用旧接口”的反面说明中，不能作为正式路由清单中的真实接口出现。因此暂不允许进入最终验收。

## 2. docs/系统测试与结果分析素材.md 是否已创建

**已创建，内容基本完整。**

`docs/系统测试与结果分析素材.md` 已存在，并包含：

1. 测试环境；
2. 测试目标；
3. 测试范围；
4. 功能测试用例；
5. 数据库测试用例；
6. 权限测试用例；
7. 事务测试用例；
8. 前后端联调测试用例；
9. 测试截图清单；
10. 已知环境限制；
11. 未完成项说明；
12. 统一返回格式说明。

文档已说明远程环境无 Node，无法执行 `npm install / npm run build`；也说明 Windows MySQL 需在本地可连接环境补做实际导入与接口联调。未发现虚构远程环境已完整跑通。

## 3. 旧接口 GET /api/artifacts、/save-as、GET /api/tasks 是否已清理

**未全部清理。**

已修复项：

- 成果列表已改为 `GET /api/projects/{project_id}/artifacts`；
- 成果详情使用 `GET /api/artifacts/{adopted_id}`；
- 另存新版本文档大多已改为 `POST /api/outputs/{output_id}/save-as-new-version`；
- `/tasks` 页面说明已改为任务入口，不再声明全局 `GET /api/tasks` 任务列表接口。

仍存在的阻塞项：

- `backend/scripts/route_list.md` 第 93 行仍列出：

```text
POST /api/outputs/{output_id}/save-as
```

并标注为“基于已有输出另存为新版本（兼容路径）”。本轮要求 `/save-as` 不得作为真实接口或测试用例出现，因此该条必须移除，或改成明确的“历史兼容路径，不作为验收/文档推荐接口使用”的反面说明，并且正式接口清单只保留 `POST /api/outputs/{output_id}/save-as-new-version`。

说明：

- 搜索到的 `GET /api/artifacts/{adopted_id}` 属于正确成果详情接口，不按旧成果列表接口处理。
- 搜索到的 `GET /api/tasks/{id}`、`GET /api/tasks/{id}/branches`、`GET /api/tasks/{id}/outputs` 属于正确任务详情相关接口，不按全局 `GET /api/tasks` 处理。
- `/api/auth/register`、`task_name`、`task_type`、`code: 200` 仅出现在“不得使用/已修正”的反面说明中，未发现作为真实接口或真实字段使用。

## 4. README 中“用户注册”是否已清理

**已清理。**

根 `README.md` 功能模块表已改为：

- 用户登录；
- 用户信息查询；
- 退出登录；
- 角色权限控制；
- 登录日志记录；
- 密码哈希存储。

未发现 README 中继续把“用户注册”作为系统功能，也未发现 `/api/auth/register` 作为真实接口。

## 5. test_report_material.md 旧统计字段是否已修复

**已修复。**

`backend/scripts/test_report_material.md` 中：

- `TC-026` 统计概览已使用 `project_count`、`active_project_count`、`task_count`、`pending_review_count`、`invocation_count`、`success_invocation_count`、`artifact_count`、`total_tokens`、`total_cost`；
- `TC-027` 成员贡献统计已使用 `user_id`、`real_name`、`project_count`、`task_created_count`、`task_assigned_count`、`output_created_count`、`review_count`、`artifact_adopted_count`、`invocation_count`；
- `total_projects`、`contribution_count` 仅出现在 Stage-17 FIX 说明的“旧字段 -> 新字段”反面说明中，不作为真实预期字段。

## 6. 截图清单 / 最终检查清单非真实表名是否已修复

**已修复。**

`docs/截图清单.md` 和 `docs/最终检查清单.md` 已将数据库表名调整为真实表名，包括：

- `project_tasks`；
- `task_branches`；
- `task_outputs`；
- `output_comments`；
- `output_reviews`；
- `review_requests`；
- `adopted_outputs`；
- `ai_invocations`；
- `operation_logs`。

未发现 `tasks`、`reviews`、`artifacts`、`invocations` 继续作为数据库真实表名使用。若这些词作为业务页面或业务模块名称出现，不构成问题。

## 7. 是否发现新的旧接口或旧字段

发现 1 个必须修复的旧接口残留：

- `backend/scripts/route_list.md` 中仍将 `/api/outputs/{output_id}/save-as` 列为正式接口。

非阻塞建议：

- `docs/系统测试与结果分析素材.md` 中个别请求体可以继续细化，例如输出编辑应使用 `lock_version`，新增批注应使用 `comment_type/comment_text`。这不属于上轮阻塞点，但建议最终提交前一并校准，以免测试人员按错误请求体截图。

## 8. 是否发现真实密钥泄露

**未发现。**

本轮检查未发现：

- 真实数据库密码；
- 真实 API Key；
- 真实 JWT Secret；
- 完整 `sk-` 开头密钥；
- 真实 token；
- Apifox Mock API 地址。

涉及 `password_hash`、`encrypted_api_key`、`key_iv`、`key_tag` 的命中均来自 Schema 或安全说明，不属于泄露。

## 9. 是否发现越界修改

未发现 Stage-17 Fix 新增后端接口、新数据库表、新业务模块、恢复 Apifox Mock API 或声称远程已完成 Node / Windows MySQL 联调。

说明：远程工作区存在大量历史未提交的 `backend/app/*`、`frontend/src/*`、`database/*` 修改，无法仅凭 `git status` 判断是否为本轮变更。根据 `HANDOFF-017-FIX-final-polish-run-report.md`，本轮声明仅修复文档类文件；本报告未发现与 handoff 冲突的新增业务实现。

## 10. 后端语法检查

已执行：

```bash
cd backend
python3 scripts/check_backend.py
python3 -m py_compile run.py app/main.py app/config.py app/database.py
```

结果：

- `check_backend.py`：49/49 个 Python 文件通过；
- `run.py app/main.py app/config.py app/database.py` 额外 py_compile 通过。

前端构建未执行，原因：远程环境 `node` 不存在，返回 `node: command not found`。已按静态审查处理。

## 11. 是否允许进入最终验收

**暂不允许。**

## 12. 必须修复的问题

1. 修改 `backend/scripts/route_list.md`，移除正式接口清单中的：

```text
POST /api/outputs/{output_id}/save-as
```

2. 正式文档与测试材料中只保留验收指定路径：

```text
POST /api/outputs/{output_id}/save-as-new-version
```

3. 如果确实需要说明历史兼容路径，只能放在“历史兼容说明 / 不作为验收接口 / 不推荐在测试和截图中使用”的反面说明中，不能作为正式路由清单接口。

本轮不移动 `TASK-017-final-polish-run-report.md` 到 `tasks/done`，不更新 `TASK_BOARD.md`，不更新 `PROJECT_STATUS.md`。
