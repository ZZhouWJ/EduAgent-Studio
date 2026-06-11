# Superpowers Phase 2 & 3 执行计划

> **创建时间**：2026-06-12
> **创建人**：Cursor Agent
> **背景**：Phase 1 + Phase 2 已交付，Superpowers 流程已启用，撰写后续开发计划

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

- [ ] 前后端接口真实联调（大部分后端仍为 Mock 数据）
- [ ] 演示脚本完善（本计划完成后）

---

## Phase 3 待完成事项

### P0 — 必须完成（演示/提交前）

- [ ] **真实智能体逻辑**：将 5 个智能体从 Mock 返回替换为 LangGraph + LLM 调用
- [ ] **真实 LLM 接入**：配置真实 API Key（推荐 Qwen-Max 或 DeepSeek-V3）
- [ ] **前后端联调**：确保所有 Mock 接口改为真实后端调用
- [ ] **演示脚本录制**：按 docs/演示脚本.md 完成视频录制

### P1 — 重要（提交前建议完成）

- [ ] **对象存储**：实现 MinIO 或本地 `storage/` 目录保存生成的文件
- [ ] **数据库迁移**：将 A3 业务表从 MySQL 迁移至 PostgreSQL（`courses`、`knowledge_points`、`student_profiles` 等）
- [ ] **学习任务模块完善**：前端 `/tasks` 页面接入 `/api/learning/tasks` 接口
- [ ] **课程模块完善**：前端 `/courses` 页面接入 `/api/learning/courses` 接口

### P2 — 优化（有余力时完成）

- [ ] **智能体重试机制**：LLM 调用失败时自动重试 2-3 次
- [ ] **调用限流**：防止 LLM API 调用超过 QPM 限制
- [ ] **详细调用日志**：每个智能体调用的 prompt/response 存入数据库
- [ ] **提示词模板管理**：将提示词从代码中抽取到数据库，支持在线编辑
- [ ] **教师审核通知**：资源审核完成后，通知相关学生（邮件/站内信）

---

## Superpowers 流程回顾

### 已启用的 Superpowers Skills

根据 `~/.cursor/skills-cursor/` 中的 17 个 skill，以下技能已自动生效：

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

- **PR 流程**：`cursor/` 分支尚未合并到 `main`，建议开发完成后用 `split-to-prs` 拆分
- **代码审查**：`cursor/phase1-2-a3-migration` 分支未提交 PR，建议用 `requesting-code-review` 审查后再合并
- **Worktree 隔离**：后续开发建议用 `using-git-worktrees` 隔离工作区

---

## Phase 3 建议开发顺序

```
Phase 3 建议顺序（按依赖排序）：

1. 前后端联调（无依赖，最快出效果）
   → 确认所有 Mock 接口已接入
   → 确认 dashboard / profiles / agent-workbench 真实调用

2. 演示脚本录制（无依赖，独立完成）
   → 按 docs/演示脚本.md 操作
   → 录制 15 分钟演示视频

3. 真实 LLM 接入（依赖联调结果）
   → 配置 .env 中 LLM_API_KEY
   → 将 MockProvider 替换为 OpenAICompatibleProvider

4. 真实智能体逻辑（依赖真实 LLM）
   → 替换 5 个智能体的 generate_* 方法
   → 接入 LangGraph workflow 真实调用

5. 数据库迁移（可并行）
   → 执行 database/09_create_a3_tables.sql
   → 迁移 MySQL 数据到 PostgreSQL

6. 对象存储（可并行）
   → 配置 MinIO 或创建 storage/ 目录
   → 实现文件上传/下载 API
```

---

## 注意事项

1. **不要破坏 `main` 分支**：`cursor/phase1-2-a3-migration` 分支开发完成后，再合并
2. **持续提交**：`cursor/` 分支频繁 `git commit`，不要一次性提交大量变更
3. **演示优先**：所有开发前先确保演示脚本能完整跑通
4. **Superpowers 技能复用**：Phase 3 继续使用 `dispatching-parallel-agents` 并行开发各模块
