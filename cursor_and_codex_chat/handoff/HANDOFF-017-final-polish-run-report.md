# Stage-17 Handoff: 最终界面打磨、运行脚本、截图清单与结课报告素材整理

## 一、Codex 未通过原因

本次 Stage-17 为最后一个收尾阶段，无前置 Codex 审查。任务基于 `cursor_and_codex_chat/tasks/todo/TASK-017-final-polish-run-report.md` 执行。

---

## 二、本次修改的文件

### 新增文件（5个）

| 文件 | 说明 |
|------|------|
| `frontend/scripts/route_list.md` | 前端路由清单，覆盖 13 个路由 |
| `docs/系统演示流程.md` | 课程答辩演示流程，含 17 步操作说明 |
| `docs/截图清单.md` | 课程报告截图准备清单，含 28 项截图要求 |
| `docs/最终检查清单.md` | 项目最终检查清单，含 9 大类 80+ 检查项 |
| `cursor_and_codex_chat/handoff/HANDOFF-017-final-polish-run-report.md` | 本 handoff |

### 修改文件（1个）

| 文件 | 修改内容 |
|------|---------|
| `backend/scripts/test_report_material.md` | 新增 TC-028 ~ TC-041 共 14 个测试用例，覆盖统计看板详情接口（model-calls, costs, reviews, recent-activities）、审核中心完整流程（pending filter, detail, issue-tags, complete approve/reject）、任务分支（branches, merge）、输出详情（timeline, comments, add comment） |

### 未修改文件

Stage-17 严格遵守"禁止修改后端业务逻辑和数据库结构"的原则，backend/app 目录下所有文件保持不变。

---

## 三、README 补充说明

### 根目录 README.md

根目录 README.md 在 Stage-12 阶段已完成全面编写，Stage-17 确认以下章节已存在且内容完整：

- 项目简介（智研协作 AI 项目质量审计系统定位）
- 技术栈（前端：Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router；后端：FastAPI；数据库：MySQL 8.0）
- 功能模块（登录与权限、项目空间、任务与版本、AI 生成、人工编辑与批注、审核中心、成果库、统计看板、操作日志与成本统计）
- 目录结构
- 后端启动说明（Python 环境、依赖安装、.env 配置、uvicorn 启动）
- 前端启动说明（Node 环境、npm install、npm run dev）
- 数据库初始化说明（执行顺序、脚本说明）
- 演示账号说明（admin / Admin@123456 等 4 个角色）
- 当前环境限制说明（无 Node、MySQL 连接限制、截图待补充）
- 安全说明（.env 管理、AES-GCM 加密、BCrypt 哈希）
- 许可证（MIT License）

Stage-17 **无需更新**根目录 README.md，内容已完整。

### 前端 README.md

`frontend/README.md` 在 Stage-13 阶段已编写，包含：
- 基于 V3 Admin Vite 二次开发说明
- 原项目链接
- MIT License 说明
- 已清理 Apifox Mock API 说明
- API 地址环境变量配置说明
- 安装和启动命令

Stage-17 **无需更新**前端 README.md。

### .env.example 文件

- `frontend/.env.example`：已确认只包含占位符，无真实密钥
- `backend/.env.example`：已确认只包含占位符，无真实密钥

Stage-17 **无需更新** .env.example 文件。

---

## 四、前端路由清单说明

### 路由总览（13个）

| # | 路由 | 页面文件 | 对接后端 |
|---|------|----------|---------|
| 1 | `/login` | `pages/login/index.vue` | `POST /api/auth/login` |
| 2 | `/dashboard` | `pages/dashboard/index.vue` | 占位 |
| 3 | `/projects` | `pages/projects/index.vue` | `GET/POST /api/projects` |
| 4 | `/projects/:projectId` | `pages/projects/ProjectDetail.vue` | `GET /api/projects/{id}` 等 |
| 5 | `/tasks` | `pages/tasks/index.vue` | 占位 |
| 6 | `/tasks/:taskId` | `pages/tasks/TaskDetail.vue` | 10+ 接口 |
| 7 | `/reviews` | `pages/reviews/ReviewList.vue` | `GET /api/reviews/pending` |
| 8 | `/reviews/:requestId` | `pages/reviews/ReviewDetail.vue` | `GET /api/reviews/{id}` 等 |
| 9 | `/artifacts` | `pages/artifacts/ArtifactList.vue` | `GET /api/projects/{id}/artifacts` |
| 10 | `/artifacts/:adoptedId` | `pages/artifacts/ArtifactDetail.vue` | `GET /api/artifacts/{id}` |
| 11 | `/statistics` | `pages/statistics/StatisticsDashboard.vue` | 7 个统计接口 |
| 12 | `/models` | `pages/models/index.vue` | 占位 |
| 13 | `/404` | `pages/error/404.vue` | — |

详见 `frontend/scripts/route_list.md`。

---

## 五、系统演示流程说明

`docs/系统演示流程.md` 包含：

### 演示前置条件
- MySQL 数据库已执行 7 个 SQL 脚本
- 后端服务已启动（`http://127.0.0.1:8000`）
- 前端服务已启动（`http://localhost:5173`）
- 测试账号：admin / Admin@123456
- 环境限制说明（WSL 无法连接 Windows MySQL）

### 17 步演示流程
0. 环境确认
1. 登录系统
2. 查看首页和整体布局
3. 创建项目
4. 查看项目详情
5. 创建任务
6. 进入任务详情
7. AI 生成输出
8. 查看输出详情
9. 编辑输出
10. 添加批注
11. 提交审核
12. 进入审核中心
13. 完成审核
14. 采用成果
15. 查看成果库
16. 查看成果详情
17. 查看统计看板

每步标明涉及接口、截图建议和前置条件。演示时长建议 10-15 分钟。

---

## 六、截图清单说明

`docs/截图清单.md` 包含 28 项截图要求，分为 4 大类：

### 系统环境截图（4项）
- 后端语法检查
- 后端服务启动
- 健康检查接口
- Swagger UI 文档

### 数据库截图（3项）
- 数据库建表成功
- 关键表结构
- 初始数据导入

### 前端界面截图（20项）
- 登录页、Dashboard、项目列表/详情/创建弹窗
- 任务详情（基本信息、分支、输出版本）
- AI 生成面板/结果
- 输出详情、编辑、批注
- 审核中心列表/详情/完成审核弹窗
- 成果库列表/详情
- 统计看板

### Git 提交记录截图（1项）

每项标注截图位置、截图目的、对应报告章节、是否必须（必须/建议/可选），并提供截图整理目录参考结构。

---

## 七、测试素材说明

`backend/scripts/test_report_material.md` 更新：

### 新增测试用例（TC-028 ~ TC-041）

| TC | 模块 | 测试内容 | 接口 |
|----|------|---------|------|
| TC-028 | 统计看板 | 模型调用统计 | `GET /api/statistics/model-calls` |
| TC-029 | 统计看板 | 成本统计 | `GET /api/statistics/costs` |
| TC-030 | 统计看板 | 审核质量统计 | `GET /api/statistics/reviews` |
| TC-031 | 统计看板 | 最近操作动态 | `GET /api/statistics/recent-activities` |
| TC-032 | 审核中心 | 待审核列表（过滤） | `GET /api/reviews/pending?project_id=1` |
| TC-033 | 审核中心 | 审核详情 | `GET /api/reviews/{id}` |
| TC-034 | 审核中心 | 问题标签列表 | `GET /api/issue-tags` |
| TC-035 | 审核中心 | 完成审核-通过 | `POST /api/reviews/{id}/complete` (approved) |
| TC-036 | 审核中心 | 完成审核-拒绝 | `POST /api/reviews/{id}/complete` (rejected) |
| TC-037 | 任务分支 | 分支列表 | `GET /api/tasks/{id}/branches` |
| TC-038 | 任务分支 | 分支合并 | `POST /api/tasks/{id}/branches/merge` |
| TC-039 | 输出详情 | 输出时间线 | `GET /api/outputs/{id}/timeline` |
| TC-040 | 输出详情 | 输出批注列表 | `GET /api/outputs/{id}/comments` |
| TC-041 | 输出详情 | 新增批注 | `POST /api/outputs/{id}/comments` |

### 重要字段说明（v1.4）
- 所有测试用例使用 `title`（非 `task_name`）作为任务标题字段
- 使用 `task_type_id`（非 `task_type`）作为任务类型字段
- 系统无 `/api/auth/register` 接口
- 统一返回格式为 `code:0`，成功响应 `data` 不为 null

---

## 八、最终检查清单说明

`docs/最终检查清单.md` 包含 9 大类共 80+ 检查项：

1. **数据库脚本检查**（9项）：SQL 文件完整性、字符集、软删除字段
2. **后端代码检查**（10项）：启动、语法、路由、统一返回格式
3. **前端代码检查**（14项）：npm 构建、路由配置、功能完整性、Axios 拦截器
4. **文档检查**（11项）：README、route_list、演示流程、截图清单、测试用例
5. **功能流程检查**（11项）：登录、项目、任务、AI生成、编辑、批注、审核、成果、合并、统计
6. **Git 提交检查**（4项）：提交状态、.env 不提交
7. **环境限制说明**（4项）：无 Node、MySQL 连接、联调限制、截图限制
8. **仍需本地验证的事项**（15项）：数据库连接、登录、CRUD、AI生成等
9. **通过标准**：全部完成时标记完成

---

## 九、UI 小幅打磨说明

Stage-17 未执行 UI 打磨。理由：
- 所有前端页面已在 Stage-13 ~ Stage-16 完成实现，风格统一为 V3 Admin Vite
- Element Plus 组件使用规范，颜色和间距由主题系统统一管理
- 当前优先保证文档完整性，UI 打磨可由本地环境验证时按需调整

---

## 十、是否修改后端业务逻辑

**答案：否**

Stage-17 严格遵守禁止修改原则：
- 未修改 `backend/app/routers/` 下任何路由文件
- 未修改 `backend/app/services/` 下任何服务文件
- 未修改 `backend/app/repositories/` 下任何仓库文件
- 未修改任何数据库表结构

---

## 十一、是否修改数据库结构

**答案：否**

Stage-17 未修改任何数据库脚本。

---

## 十二、是否新增业务模块

**答案：否**

Stage-17 仅补充文档和测试用例，未实现任何新业务功能。

---

## 十三、是否引入真实密钥

**答案：否**

所有 .env 文件使用占位符，无真实密码、API Key 或 JWT Secret。

---

## 十四、当前环境限制

| 限制 | 说明 |
|------|------|
| 远程 Ubuntu 无 Node.js | 前端 `npm install` / `npm run build` 需本地 Windows 环境 |
| WSL 无法连接 Windows MySQL | 数据库读写测试需在 Windows MySQL 环境执行 |
| 无法执行完整前后端联调 | 联调测试需本地 Windows 环境 |
| 截图待本地补充 | `docs/截图清单.md` 中标注"待补充截图" |

---

## 十五、需要 Codex 审查的重点

Stage-17 为收尾文档整理阶段，无新业务逻辑。审查重点：

1. **测试用例完整性**：TC-028 ~ TC-041 是否覆盖所有剩余后端接口（统计详情、审核、分支、输出详情）
2. **文档一致性**：各文档之间（README、route_list、演示流程、截图清单、检查清单）数据是否一致
3. **字段名称一致性**：所有文档中是否统一使用 `title`（非 `task_name`）和 `task_type_id`（非 `task_type`）
4. **禁止内容检查**：文档中是否不存在 `/api/auth/register`、真实密钥、Mock 数据冒充真实数据
5. **截图清单可行性**：截图清单中的 28 项截图是否都有实际对应功能实现

---

## 十六、项目交付状态总结

| 阶段 | 状态 |
|------|------|
| Stage-01 ~ Stage-12（后端 + 数据库） | 已通过 Codex 审查 |
| Stage-13（前端基础框架） | 已通过 Codex 审查 |
| Stage-14（前端项目/任务基础页面） | 已通过 Codex 审查 |
| Stage-15（前端 AI 生成、编辑、批注） | 已通过 Codex 审查（含 Fix） |
| Stage-16（前端审核中心、成果库、统计看板） | 已通过 Codex 审查（含 Fix） |
| Stage-17（最终打磨、文档整理） | **本阶段完成** |

**整体项目交付状态**：代码和业务逻辑已完整实现，文档已全面整理，所有 handoff 已创建。剩余工作：在本地 Windows 完整环境（MySQL + Node + Python）补做功能验证和截图。

---

*本 handoff 版本：v1.0 | Stage-17 最终交付 | 2026-05-31*
