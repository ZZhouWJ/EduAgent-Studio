# REVIEW-017 最终界面打磨、运行脚本、截图清单与结课报告素材审查报告

## 1. 审查结论

**需要继续修改。**

Stage-17 的收尾文档和说明材料已经覆盖了大部分最终交付内容，且未发现新增后端接口、数据库结构修改或大规模业务重构。但本轮仍发现若干会影响最终验收和课程答辩材料准确性的阻塞问题：

1. 用户指定审查的 `docs/系统测试与结果分析素材.md` 不存在；
2. 多个文档仍残留旧接口路径或不存在接口，例如 `GET /api/artifacts`、`POST /api/outputs/{outputId}/save-as`、`GET /api/tasks`；
3. 根 README 仍写有“用户注册”，与当前系统无注册接口的事实冲突；
4. 测试素材中统计接口预期字段仍使用旧字段，如 `total_projects`、`contribution_count`；
5. 部分截图清单和 README 仍使用非真实表名或“占位”表述，和当前最终实现不一致。

因此本轮暂不允许进入最终验收。

## 2. Stage-17 是否遵守任务范围

**基本遵守。**

根据 `HANDOFF-017-final-polish-run-report.md`，本阶段主要新增或修改：

- `README.md`
- `frontend/README.md`
- `frontend/.env.example`
- `frontend/scripts/route_list.md`
- `docs/系统演示流程.md`
- `docs/截图清单.md`
- `docs/最终检查清单.md`
- `backend/scripts/test_report_material.md`
- `frontend/src/pages/dashboard/index.vue` 文案

未发现 Stage-17 声明新增后端接口、新数据库表、新业务模块或新的大模型调用能力。Dashboard 修改属于小幅文案打磨，符合范围。

说明：远程仓库长期存在大量历史未提交修改，`git status` 中仍显示 backend、database、docs 等目录为 modified，无法仅凭当前工作区状态判断这些变更是否由 Stage-17 产生。本报告以 handoff、实际文件内容和 Stage-17 审查对象为准。

## 3. 根 README 是否完整

**不完全通过。**

根 `README.md` 已包含项目名称、简介、技术栈、目录结构、后端/前端启动、数据库初始化、演示账号和环境限制说明。

阻塞问题：

- 功能模块表中仍写有“用户注册、登录、角色权限”，但当前系统没有 `/api/auth/register`，也不提供注册功能。应改为“用户登录、当前用户、退出登录、角色权限、登录日志”等符合实际实现的表述。

其他说明：

- README 中演示账号密码来自初始化数据说明，属于课程演示账号，不按真实密钥泄露处理；但生产环境修改默认密码的提醒已存在。
- README 已说明远程 Ubuntu 无 Node、Windows MySQL 需本地验证、截图待补充，没有虚构当前远程环境已全部联调通过。

## 4. backend README 是否完整

**基本通过。**

`backend/README.md` 保留了数据库 01-07 初始化顺序、`.env` 配置、启动命令、健康检查、WSL / Windows MySQL 说明和统一返回格式。

未发现：

- `/api/auth/register`；
- `code: 200` 作为系统统一返回格式；
- 真实数据库密码、真实 JWT Secret 或完整 API Key。

## 5. frontend README 是否完整

**需要修改。**

`frontend/README.md` 已说明基于 V3 Admin Vite 二次开发、MIT License、NOTICE、Apifox Mock API 清理、环境变量配置、安装和构建命令。

阻塞问题：

1. 页面模块说明中 `/artifacts` 对接后端写为 `/api/artifacts`，但真实成果列表接口是 `GET /api/projects/{project_id}/artifacts`。
2. 目录结构中仍把 `projects`、`tasks`、`reviews`、`artifacts`、`statistics`、`models` 等页面标为“占位”，与当前前端已实现核心页面的状态冲突。
3. `/tasks` 页面说明为对接 `/api/tasks`，但当前后端没有全局 `GET /api/tasks` 路由；前端实际任务列表主要通过项目详情中的 `GET /api/projects/{project_id}/tasks` 获取。

## 6. .env.example 是否安全

**通过。**

已检查：

- `backend/.env.example`
- `frontend/.env.example`
- `frontend/.env.production`
- `frontend/.env.staging`

结论：

- 未发现真实数据库密码；
- 未发现真实 API Key；
- 未发现真实 JWT Secret；
- 未发现完整 `sk-` 密钥；
- 未发现真实 token；
- 未发现 `mock.apifox.com` 或 Apifox Mock 地址；
- 前端使用 `VITE_BASE_URL`，与当前 request 封装的环境变量方向一致；
- 后端使用 `SERVER_HOST / SERVER_PORT`，与当前配置方向一致。

## 7. 前端路由清单是否完整

**不通过，需要修正接口说明。**

`frontend/scripts/route_list.md` 覆盖了 `/login`、`/dashboard`、`/projects`、`/projects/:projectId`、`/tasks`、`/tasks/:taskId`、`/reviews`、`/reviews/:requestId`、`/artifacts`、`/artifacts/:adoptedId`、`/statistics`、`/models`、`/404` 和 `/403`。

阻塞问题：

1. `/artifacts` 的对接接口写为 `GET /api/artifacts`，但后端真实接口是 `GET /api/projects/{project_id}/artifacts`。
2. `/tasks` 的对接接口写为 `GET /api/tasks`，但后端没有全局任务列表接口；当前页面只是引导用户到项目空间查看任务。

这些会误导测试人员按不存在接口截图或测试。

## 8. 系统演示流程是否可用

**不通过，需要修正旧接口。**

`docs/系统演示流程.md` 已覆盖登录、首页、项目、任务、AI 生成、编辑批注、审核、成果库、统计看板、数据库和后端展示，整体结构适合答辩。

阻塞问题：

1. 人工编辑步骤中仍写 `POST /api/outputs/{outputId}/save-as`。最终验收路径应使用 `POST /api/outputs/{output_id}/save-as-new-version`。
2. 成果库步骤中仍写 `GET /api/artifacts`。真实成果列表接口是 `GET /api/projects/{project_id}/artifacts`。
3. 成果详情接口应写为 `GET /api/artifacts/{adopted_id}`，建议统一参数命名为后端字段名。

## 9. 截图清单是否完整

**基本完整，但需修正真实表名。**

`docs/截图清单.md` 已覆盖数据库、后端、前端、Git 等 24 项截图，且每项包含截图位置、目的、对应报告章节和是否必须。

需要修改：

- 数据库关键表截图中仍使用 `tasks`、`reviews`、`artifacts`、`invocations` 等非当前 Schema 的真实表名。建议改为：
  - `project_tasks`
  - `review_requests` / `output_reviews`
  - `adopted_outputs`
  - `ai_invocations`

否则报告截图清单会引导学生去截不存在或不准确的表。

## 10. 系统测试与结果分析素材是否正确

**不通过。**

阻塞问题：

1. 用户指定审查的 `docs/系统测试与结果分析素材.md` 文件不存在。当前只更新了 `backend/scripts/test_report_material.md`，但没有生成 docs 下对应课程报告素材文件。
2. `backend/scripts/test_report_material.md` 中统计接口预期字段仍有旧字段：
   - `GET /api/statistics/overview` 预期写 `{total_projects,...}`，应改为 `project_count`、`active_project_count`、`task_count`、`pending_review_count`、`invocation_count`、`artifact_count`、`total_tokens`、`total_cost` 等真实字段；
   - `GET /api/statistics/member-contributions` 预期写 `contribution_count`，真实字段应为 `project_count`、`task_created_count`、`task_assigned_count`、`output_created_count`、`review_count`、`artifact_adopted_count`、`invocation_count`。
3. 测试素材中部分接口预期返回形态仍偏旧，例如项目列表/任务列表应按当前后端真实 `items` 或数组返回形态精确描述，避免误导测试截图。

已确认：

- 未发现 `/api/auth/register` 被作为真实接口使用；
- 创建任务字段已使用 `task_type_id` 和 `title`；
- 文档明确说明当前环境限制和待本地验证，没有虚构当前远程环境已全部通过。

## 11. 最终检查清单是否完整

**基本完整，但存在内部矛盾与旧表名问题。**

`docs/最终检查清单.md` 已覆盖数据库、后端、前端、文档、业务功能、API、安全、测试材料、开源合规、课程报告材料。

需要修改：

1. 文档检查中写“README 中无真实密码 | 无 `Admin@123456` 等明文密码”，但根 README 和前端 README 按演示账号说明列出了默认账号密码。建议改为“无生产真实密码；演示账号密码仅来源于初始化测试数据并标注需生产修改”。
2. 数据库关系中使用 `projects ↔ tasks ↔ outputs ↔ reviews ↔ artifacts`，建议改为真实表名或业务名分开说明，例如 `projects ↔ project_tasks ↔ task_outputs ↔ review_requests/output_reviews ↔ adopted_outputs`。

## 12. 是否发现真实密钥泄露

**未发现。**

本轮检查的 README、环境变量样例、docs、backend/scripts、frontend/scripts 和 handoff 中未发现：

- 真实数据库密码；
- 真实 API Key；
- 真实 JWT Secret；
- 完整 `sk-` 密钥；
- 真实 token；
- 服务器密码或私密账号凭据。

说明：默认演示账号密码来自初始化数据说明，应保留用于课程演示，但需明确不属于生产密钥，生产环境必须修改。

## 13. 是否发现旧接口或旧字段残留

**发现，需要修复。**

必须清理或修正：

1. `README.md`：`用户注册`。
2. `frontend/README.md`：`/api/artifacts`、`/api/tasks`、页面目录“占位”表述。
3. `frontend/scripts/route_list.md`：`GET /api/artifacts`、`GET /api/tasks`。
4. `docs/系统演示流程.md`：`POST /api/outputs/{outputId}/save-as`、`GET /api/artifacts`。
5. `backend/scripts/test_report_material.md`：统计字段 `total_projects`、`contribution_count`。
6. `docs/截图清单.md` / `docs/最终检查清单.md`：数据库截图或关系说明中的旧表名。

## 14. 是否发现越界修改

未发现 Stage-17 明确新增后端接口、新数据库表、新业务模块或大规模重构。

`backend/scripts/test_report_material.md` 属于文档类脚本材料，修改范围可接受。

## 15. 启动或静态检查

已执行后端检查：

```bash
cd backend
python3 scripts/check_backend.py
python3 -m py_compile run.py app/main.py app/config.py app/database.py
```

结果：

- `check_backend.py`：49/49 个 Python 文件通过；
- 额外 py_compile：通过。

前端构建：

```bash
cd frontend
node -v
```

远程环境返回：

```text
node: command not found
```

因此无法执行 `npm install` 或 `npm run build`。本轮已按静态审查处理，并将远程无 Node 的限制记入报告。

## 16. 是否允许进入最终验收

**不允许。**

## 17. 必须修复的问题

1. 新增或补齐 `docs/系统测试与结果分析素材.md`，内容应与 `backend/scripts/test_report_material.md` 协同，包含测试环境、测试目标、功能/数据库/权限/事务/联调测试用例、截图清单、环境限制和未完成项说明。
2. 修正根 `README.md` 的“用户注册”表述，改为当前真实认证能力。
3. 修正 `frontend/README.md`：
   - `/artifacts` 对接接口改为 `GET /api/projects/{project_id}/artifacts`；
   - `/tasks` 页面不要写不存在的 `GET /api/tasks`；
   - 目录结构中删除“占位”表述，改为当前已实现页面说明。
4. 修正 `frontend/scripts/route_list.md`：
   - `/artifacts` 对接接口改为 `GET /api/projects/{project_id}/artifacts`；
   - `/tasks` 页面说明为“项目内任务列表入口/引导页”，不要标注不存在的 `GET /api/tasks`。
5. 修正 `docs/系统演示流程.md`：
   - `save-as` 改为 `save-as-new-version`；
   - `GET /api/artifacts` 改为 `GET /api/projects/{project_id}/artifacts`；
   - 参数命名统一为 `output_id`、`adopted_id` 等后端字段。
6. 修正 `backend/scripts/test_report_material.md` 中统计接口预期字段：
   - overview 使用 `project_count` 等真实字段；
   - member-contributions 使用 `task_created_count`、`output_created_count`、`artifact_adopted_count` 等真实字段；
   - 其他预期返回形态按后端真实响应校正。
7. 修正 `docs/截图清单.md` 和 `docs/最终检查清单.md` 中的旧表名或泛化表名，改为当前 Schema 真实表名。
8. 修复后重新提交 handoff，说明哪些文档已清理旧接口、旧字段和旧表名。

本轮不创建 `tasks/done/TASK-017-final-polish-run-report.md`，也不更新 `TASK_BOARD.md` / `PROJECT_STATUS.md`。
