# Superpowers Phase 2 & 3 执行计划

> **创建时间**：2026-06-12
> **创建人**：Cursor Agent
> **背景**：Phase 1 + Phase 2 已交付，Phase 3 持续推进中

---

## Phase 2 完成情况回顾

### Phase 2 新增功能（已交付 ✅）

- 学习反馈模块：`/feedback` 页面 + `/api/learning/feedbacks` 接口
- 学习分析看板：`/analytics` 页面 + 6 个 ECharts 图表
- 资源详情页：`/resources/:id` + `/api/learning/resources` 接口
- Celery 异步任务框架：embedding / resource / statistics 三类任务
- 旧页面 A3 化：7 个页面的文案和语义改造
- 后端统计接口：7 个新 A3 统计接口

### Phase 2 尚未覆盖

- [ ] 前后端接口真实联调（大部分后端仍为 Mock 数据）— ⚠️ 部分完成
- [ ] 演示脚本完善（本计划完成后）— ✅ 已完成

---

## Phase 3 执行记录

### ✅ 已完成

| 提交 | 时间 | 内容 |
|------|------|------|
| `ceee55e` | 12:23 | LangGraph 标准版 + 对象存储 + 前端完整联调 |
| `e1cb659` | 12:46 | 学习任务/课程模块完善 + PostgreSQL 迁移脚本 |

#### 完成详情

**LangGraph StateGraph 标准版**：
- Supervisor 条件路由（非线性执行路径）
- 自动返工循环（质量 < 7.0 → 最多 3 次）
- SQLite Checkpoint 持久化（断点暂停/恢复）
- SSE 流式推送（前端实时显示每个节点执行状态）
- `_map_workflow_result()` 字段映射（learning_plan→plan 等）

**对象存储**：
- `storage_router`：`GET /api/storage/{file_id}` 文件下载
- `storage_service`：修复相对路径问题，文件存储到 `backend/data/storage/`
- `save_resource()` 对接 `storage_service`，统一持久化

**前端完整联调**：
- `agents.ts`：重写 `WorkflowResult` 接口 + 完整字段定义
- `agent-workbench`：SSE 流式执行链路 + 5 个 Tab 完整展示 + 保存后下载按钮
- `analytics`：6 个图表全部接 `statisticsApi` + `Promise.allSettled` 容错
- `ResourceDetail.vue`：`onMounted` 调用 `resourcesApi.getById()`
- `resources/index.vue`：新建资源列表页

**课程模块**：
- `backend/app/services/learning_service.py`：3 门课程 + 14 知识点 + 10 学习任务
- `backend/app/routers/learning.py`：4 个端点（courses list/get、tasks list/get）
- `frontend/src/api/learning.ts`：完整 TypeScript 接口定义
- `frontend/src/pages/courses/index.vue`：课程卡片网格 + 知识点标签 + 统计概览
- `frontend/src/pages/courses/CourseDetail.vue`：课程详情 + 知识点表格 + 平均掌握度

**学习任务模块**：
- 重写 `frontend/src/pages/tasks/index.vue`：projectsApi → learningApi 真实调用
- 新增课程选择器 + 状态筛选 + 完成率进度条 + 逾期提醒

**PostgreSQL 迁移**：
- `database/11_postgresql_migration.sql`：7 张 A3 业务表 schema + 种子数据
- `database/README_A3.md`：更新 Phase 3 执行说明

---

## Phase 3 待完成事项

### P0 — 必须完成（演示/提交前）

- [x] **真实智能体逻辑**（LangGraph + LLM）— ✅ 已完成
- [ ] **真实 LLM 接入**：配置 `.env` 中 API Key（推荐 DeepSeek-V3）
- [ ] **前后端联调**：确保所有 Mock 接口改为真实后端调用
- [ ] **演示脚本录制**：按 `docs/演示脚本.md` 完成视频录制

### P1 — 重要（提交前建议完成）

- [x] **对象存储** — ✅ 已完成
- [x] **PostgreSQL 迁移脚本** — ✅ schema 已完成，数据迁移需手动执行
- [x] **学习任务模块完善** — ✅ 已完成
- [x] **课程模块完善** — ✅ 已完成

### P2 — 优化（有余力时完成）

- [ ] **LLM 重试机制**：调用失败时自动重试 2-3 次
- [ ] **调用限流**：防止 LLM API 超过 QPM 限制
- [ ] **详细调用日志**：每个智能体调用的 prompt/response 存入数据库
- [ ] **提示词模板管理**：将提示词从代码中抽取到数据库，支持在线编辑
- [ ] **教师审核通知**：资源审核完成后，通知相关学生（站内信）

---

## Superpowers 流程回顾

### 已启用的 Superpowers Skills

| Skill | 触发场景 | 状态 |
|-------|---------|------|
| `using-superpowers` | 每次对话开头 | ✅ 已理解 |
| `brainstorming` | 每次创意/功能开发前 | ✅ 已理解 |
| `writing-plans` | 多步骤任务开始前 | ✅ 已理解 |
| `test-driven-development` | 实现功能/bugfix 前 | ✅ 已理解 |
| `systematic-debugging` | 遇到 bug 时 | ✅ 已理解 |
| `verification-before-completion` | 声称工作完成前 | ✅ 已理解 |
| `receiving-code-review` | 收到代码审查反馈时 | ✅ 已理解 |
| `requesting-code-review` | 提交 PR 前 | ⏳ 待提交 PR |
| `finishing-a-development-branch` | 开发完成时 | ⏳ 待合并 |
| `dispatching-parallel-agents` | 2+ 并行任务时 | ✅ Phase 2 已使用 |
| `subagent-driven-development` | 执行计划中的独立任务时 | ✅ Phase 2 已使用 |
| `executing-plans` | 执行有检查点的计划时 | ✅ Phase 2 已使用 |
| `split-to-prs` | 拆分 PR 时 | ⏳ 待使用 |
| `babysit` | PR merge-ready 维护时 | ⏳ 待使用 |
| `using-git-worktrees` | 需要隔离工作区时 | ⏳ 待使用 |
| `create-skill` | 创建新 skill 时 | ⏳ 待使用 |
| `create-rule` | 创建 Cursor rule 时 | ✅ `frontend/.cursor/rules/` 已存在 |

### 未启用的流程

- **PR 流程**：`cursor/phase1-2-a3-migration` 持续 commit，建议开发完成后用 `split-to-prs` 拆分
- **代码审查**：建议用 `requesting-code-review` 审查后再合并到 `main`
- **Worktree 隔离**：后续开发建议用 `using-git-worktrees` 隔离工作区

---

## 注意事项

1. **不要破坏 `main` 分支**：`cursor/phase1-2-a3-migration` 分支开发完成后，再合并
2. **持续提交**：`cursor/` 分支频繁 `git commit`，不要一次性提交大量变更
3. **演示优先**：所有开发前先确保演示脚本能完整跑通
4. **Superpowers 技能复用**：Phase 3 继续使用 `dispatching-parallel-agents` 并行开发各模块
