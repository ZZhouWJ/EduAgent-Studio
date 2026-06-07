# HANDOFF-017-FIX：Stage-17 文档修复

**阶段**：Stage-17 FIX（Stage-17 审查修复）
**执行人**：Cursor 收尾工程师
**日期**：2026-06-01
**状态**：已完成

---

## 一、Codex 审查未通过原因

根据 `cursor_and_codex_chat/reviews/REVIEW-017-final-polish-run-report.md`，本次修复针对以下 5 个阻塞问题：

1. **`docs/系统测试与结果分析素材.md` 不存在**：用户指定的课程报告测试素材文件缺失。
2. **旧接口路径残留**：`GET /api/artifacts`、`POST /api/outputs/{outputId}/save-as`、`GET /api/tasks` 等不存在接口在多个文档中出现。
3. **根 README.md 写有"用户注册"**：但系统无 `/api/auth/register` 接口。
4. **统计接口旧字段**：`total_projects`、`contribution_count` 等旧字段名在测试素材中未修正。
5. **非真实表名**：`tasks`、`reviews`、`artifacts`、`invocations` 等非 Schema 真实表名在截图清单中出现。

---

## 二、本次修改文件清单

### 新增文件（1 个）

| 文件路径 | 说明 |
|----------|------|
| `docs/系统测试与结果分析素材.md` | 新增，课程报告"系统测试与结果分析"章节完整素材，含环境、测试用例、截图清单 |

### 修改文件（7 个）

| 文件路径 | 修改内容 |
|----------|----------|
| `README.md` | 1. 功能模块表中"登录与权限管理"删除"用户注册"，改为"用户登录、用户信息查询、退出登录、角色权限控制、登录日志记录、密码哈希存储"<br>2. 演示账号说明补充"用户账号由初始化数据或管理员维护，当前系统不开放前台注册" |
| `frontend/README.md` | 1. 页面模块说明表中成果库对接接口从 `GET /api/artifacts` 改为 `GET /api/projects/{project_id}/artifacts`<br>2. 成果详情接口从 `GET /api/artifacts/{id}` 改为 `GET /api/artifacts/{adopted_id}`<br>3. 任务与版本页面说明修正为"任务列表入口（从项目详情进入）；任务详情：`GET /api/tasks/{id}`"<br>4. 目录结构中删除所有"（占位）"标注，改为当前已实现页面说明 |
| `frontend/scripts/route_list.md` | 1. `/artifacts` 对接接口从 `GET /api/artifacts` 改为 `GET /api/projects/{project_id}/artifacts`<br>2. `/artifacts/:adoptedId` 对接接口从 `GET /api/artifacts/{id}` 改为 `GET /api/artifacts/{adopted_id}`<br>3. `/tasks` 说明从"全局任务列表、搜索过滤"改为"任务列表入口，引导至项目空间查看详情"，删除不存在的 `GET /api/tasks` |
| `docs/系统演示流程.md` | 1. 步骤 11 中 `PUT /api/outputs/{outputId}` 改为 `PUT /api/outputs/{output_id}`<br>2. 步骤 11 中 `POST /api/outputs/{outputId}/save-as` 改为 `POST /api/outputs/{output_id}/save-as-new-version`<br>3. 步骤 12 中所有 `{outputId}` 改为 `{output_id}`<br>4. 步骤 13 中 `POST /api/outputs/{outputId}/submit-review` 改为 `{output_id}`<br>5. 步骤 16 中 `POST /api/outputs/{outputId}/adopt` 改为 `{output_id}`<br>6. 步骤 17 中 `GET /api/artifacts` 改为 `GET /api/projects/{project_id}/artifacts`<br>7. 步骤 17 中 `GET /api/artifacts/{adoptedId}` 改为 `GET /api/artifacts/{adopted_id}`<br>8. 步骤 19 数据库表名从 `projects/tasks/outputs/reviews` 改为 `projects/project_tasks/task_outputs/output_reviews` |
| `backend/scripts/test_report_material.md` | 1. TC-026 统计概览预期字段从 `{total_projects,...}` 改为 `{project_count,active_project_count,task_count,pending_review_count,invocation_count,success_invocation_count,artifact_count,total_tokens,total_cost}`<br>2. TC-027 成员贡献预期字段从 `{user_id,contribution_count,...}` 改为 `{user_id,real_name,project_count,task_created_count,task_assigned_count,output_created_count,review_count,artifact_adopted_count,invocation_count}`<br>3. 版本号从 v1.2 升级为 v1.3，补充 FIX 说明 |
| `docs/截图清单.md` | 1. 关键表名从 `tasks/reviews/artifacts/invocations` 改为真实表名 `project_tasks/output_reviews/review_requests/adopted_outputs/ai_invocations/operation_logs`<br>2. 表结构截图要求中 `tasks` 改为 `project_tasks`、`reviews` 改为 `output_reviews/review_requests`、`artifacts` 改为 `adopted_outputs`<br>3. 截图目录中表名对应文件从 `03_tasks表结构.png` 等改为 `03_project_tasks表结构.png` 等 |
| `docs/最终检查清单.md` | 1. 外键关系从 `projects ↔ tasks ↔ outputs ↔ reviews ↔ artifacts` 改为 `projects ↔ project_tasks ↔ task_outputs ↔ output_reviews/review_requests ↔ adopted_outputs`<br>2. README 密码检查项改为"无生产真实密码；演示账号密码仅来自初始化数据，需生产修改"<br>3. 新增检查项：README 中包含用户来源说明 |

---

## 三、是否创建 docs/系统测试与结果分析素材.md

**是**。已创建 `docs/系统测试与结果分析素材.md`，包含：

1. **测试环境**（硬件/OS/后端/前端/数据库，含环境限制说明）
2. **测试目标**（6 项）
3. **测试范围**（6 类，含覆盖状态）
4. **功能测试用例**（37 个 TC，覆盖认证/项目/任务/AI生成/编辑批注/审核/成果库/统计看板）
5. **数据库测试用例**（13 个 DB，涵盖建库建表/完整性/视图/存储过程）
6. **权限测试用例**（5 个 AU）
7. **事务测试用例**（4 个 TX）
8. **前后端联调测试用例**（10 个 FE）
9. **测试截图清单**（30 个 SS，分 4 类）
10. **已知环境限制**（4 项）
11. **未完成项说明**（含诚实声明）
12. **接口响应格式规范**（统一 code:0，明确不得用 code:200）

---

## 四、是否清理 GET /api/artifacts

**是**。已在以下文件中修正：

| 文件 | 修正内容 |
|------|---------|
| `frontend/README.md` | 改为 `GET /api/projects/{project_id}/artifacts` |
| `frontend/scripts/route_list.md` | 改为 `GET /api/projects/{project_id}/artifacts` |
| `docs/系统演示流程.md` | 改为 `GET /api/projects/{project_id}/artifacts` |
| `docs/系统测试与结果分析素材.md` | 全程使用正确接口路径 |

---

## 五、是否清理 /save-as 旧接口

**是**。`docs/系统演示流程.md` 中步骤 11 的 `POST /api/outputs/{outputId}/save-as` 已改为 `POST /api/outputs/{output_id}/save-as-new-version`。

同时将所有路径参数命名从 CamelCase（`outputId`）统一改为 snake_case（`output_id`）。

---

## 六、是否清理 GET /api/tasks

**是**。已在以下文件中修正：

| 文件 | 修正内容 |
|------|---------|
| `frontend/README.md` | 任务与版本页面说明改为"任务列表入口（从项目详情进入）" |
| `frontend/scripts/route_list.md` | 说明改为"任务列表入口，引导至项目空间查看详情"，不再标注 `GET /api/tasks` |

---

## 七、是否删除 README 中"用户注册"

**是**。`README.md` 功能模块表中已将"用户注册、登录、角色权限（学生/负责人/指导老师/管理员）"改为"用户登录、用户信息查询、退出登录、角色权限控制、登录日志记录、密码哈希存储"。演示账号说明部分也补充了"当前系统不开放前台注册"。

---

## 八、是否修复统计旧字段

**是**。`backend/scripts/test_report_material.md` 中：

| 旧字段 | 修正为 |
|--------|---------|
| `total_projects` | `project_count` |
| `contribution_count`（笼统） | `project_count`, `task_created_count`, `task_assigned_count`, `output_created_count`, `review_count`, `artifact_adopted_count`, `invocation_count` |

版本号升级为 v1.3，FIX 说明中列出了所有修正。

---

## 九、是否修复截图清单 / 最终检查清单非真实表名

**是**。已修正：

| 文件 | 修正内容 |
|------|---------|
| `docs/截图清单.md` | `tasks` → `project_tasks`、`reviews` → `output_reviews`/`review_requests`、`artifacts` → `adopted_outputs`、`invocations` → `ai_invocations` |
| `docs/最终检查清单.md` | 外键关系描述改为真实表名链 |

---

## 十、是否修改后端业务代码

**答案：否**

本次未修改 `backend/app/` 下任何文件（routers、services、repositories、adapters、utils、config、database、main）。

---

## 十一、是否修改前端业务代码

**答案：否**

本次未修改 `frontend/src/` 下任何文件，仅修改文档类文件。

---

## 十二、是否修改数据库结构

**答案：否**

本次未修改 `database/` 目录下任何 SQL 脚本，未新增或变更任何表结构、索引、视图或存储过程。

---

## 十三、是否进入新阶段

**答案：否**

本次仅修复 Stage-17 文档问题，不进入 Stage-18 或任何新阶段。

---

## 十四、当前环境限制说明

| 限制项 | 影响范围 |
|--------|----------|
| 远程环境无 Node | `npm install` / `npm run dev` / `npm run build` 无法执行；前端构建截图待本地补做 |
| WSL2 无法访问 Windows MySQL | 涉及 DB 的接口测试（TC-001 等）无法验证；数据库截图待本地补做 |
| MySQL 未初始化 | `database/01-07` 未执行；建表截图待本地补做 |

所有限制均已在 `docs/系统测试与结果分析素材.md` 和 `README.md` 中如实说明。

---

## 十五、需要 Codex 复审的重点

1. **`docs/系统测试与结果分析素材.md` 是否完整**：是否覆盖了所有 11 个必需章节？37 个功能测试用例 + 13 个数据库测试用例 + 5 个权限测试用例 + 4 个事务测试用例 + 10 个前后端联调用例是否足够？
2. **README.md "用户注册"是否已清除**：功能模块表和演示账号说明中是否还有任何暗示系统支持注册的文字？
3. **旧接口路径是否已全部清理**：全文搜索 `GET /api/artifacts`、`POST /api/outputs/.../save-as`（不带 `-new-version`）、`GET /api/tasks` 是否还有遗漏？
4. **统计字段是否已全部修正**：全文搜索 `total_projects`、`contribution_count` 是否还有遗漏？
5. **表名是否已全部修正**：全文搜索 `tasks`、`reviews`、`artifacts`、`invocations` 是否还有作为表名出现（而非业务名称）？
6. **统一返回格式是否一致**：所有接口预期结果是否统一使用 `code:0`？是否有任何 `code: 200`？
7. **`/api/auth/register` 是否已清除**：除了历史 handoff/review 文档中的 changelog 备注，正文文档中是否还有？
8. **frontend README 中"占位"是否已清除**：页面目录结构中是否已无"（占位）"标注？
9. **`/tasks` 页面说明是否已修正**：不再写不存在的 `GET /api/tasks`？
10. **新增的 `docs/系统测试与结果分析素材.md` 是否与 `backend/scripts/test_report_material.md` 协同一致**？

---

## 十六、修复后交付物汇总

| 交付物 | 文件路径 | 状态 |
|--------|----------|------|
| 根 README | `README.md` | 已修正（无用户注册，auth 描述正确）|
| 前端 README | `frontend/README.md` | 已修正（接口路径正确，无占位标注）|
| 前端路由清单 | `frontend/scripts/route_list.md` | 已修正 |
| 系统演示流程 | `docs/系统演示流程.md` | 已修正（save-as-new-version，正确接口）|
| 截图清单 | `docs/截图清单.md` | 已修正（真实表名）|
| 最终检查清单 | `docs/最终检查清单.md` | 已修正（真实表名，密码说明）|
| 后端测试素材 | `backend/scripts/test_report_material.md` | 已修正（v1.3，统计字段正确）|
| 系统测试素材 | `docs/系统测试与结果分析素材.md` | 新增 |
| Handoff | `cursor_and_codex_chat/handoff/HANDOFF-017-FIX-final-polish-run-report.md` | 本文件 |

---

*本文件为 Stage-17 FIX 阶段交接文档，供 Codex 复审使用。复审通过后重新提交最终验收。*
