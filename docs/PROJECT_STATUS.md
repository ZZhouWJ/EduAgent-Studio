# EduAgent Studio 项目状态跟踪文档

> 本文件是项目的核心状态跟踪文档，供 AI 智能体在每次工作时读取并更新。
> **重要**：AI 智能体在开始任何工作前必须先读取本文档。

---

## 一、项目基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 智学工坊 EduAgent Studio |
| 赛题编号 | A3 - 基于大模型的个性化资源生成与学习多智能体系统开发 |
| 出题企业 | 科大讯飞股份有限公司 |
| 产品定位 | **面向高校课程的 AI 学习智能体操作系统**（不是资源生成工具） |
| 核心主线 | 课程知识空间 → 学习画像 → 智能体编排 → 资源工厂 → Copilot → 效果闭环 → 治理审计 |
| 开发阶段 | 第一优先级：核心链路打通中 |
| 最近更新 | 2026-07-07 |

---

## 二、产品架构（成熟版）

> EduAgent Studio 不是资源生成工具，而是"面向高校课程的学习智能体操作系统"。

### 2.1 七大核心模块

| 模块 | 定位 | 状态 |
|------|------|------|
| **课程知识空间** | 教师上传资料，系统自动解析、切分、标注知识点、建立可检索知识库 | ✅ 后端已完成 |
| **学生学习画像** | 学生通过对话、测验、学习行为持续形成动态画像（6+维度） | ⚠️ 待升级 |
| **智能体编排中心** | 多个智能体围绕真实任务协作：诊断、检索、规划、生成、审核、评估、推荐 | ⚠️ 待升级 |
| **资源生成工厂** | 针对不同学生和知识点生成讲义、题库、案例、PPT、视频脚本、思维导图、复习计划 | ✅ 基础完成 |
| **学习辅导 Copilot** | 学生持续提问，系统结合画像和课程知识库回答 | ❌ 待独立实现 |
| **学习效果闭环** | 学生学习、反馈、测验后，系统更新画像、调整路径、重排推荐资源 | ⚠️ 部分完成 |
| **治理与审计** | 教师审核、引用溯源、防幻觉、成本统计、模型调用日志全部可见 | ✅ 基础完成 |

### 2.2 数据流主线（核心链路）

```
教师上传课程资料 → 知识库（解析/切分/索引）
        ↓
学生通过对话构建画像 → Learner Memory（6+维度动态画像）
        ↓
画像 + 知识库 → 智能体编排中心（诊断/检索/规划/生成/审核）
        ↓
生成资源（绑定证据来源）→ 教师审核 → 发布给学生
        ↓
学生收到个性化路径和资源 → 学习与反馈
        ↓
画像更新 → 路径调整 → 推荐重排 → Tutor Copilot 持续辅导
        ↓
管理端：调用审计、成本统计、内容安全
```

---

## 三、成熟版开发方案（8个模块）

### 3.1 模块一：课程知识库 Knowledge Workspace

**目标**：课程知识库从静态 RAG 升级为用户上传后动态构建的真实知识库

**现状**：`backend/app/rag/` 仅有代码内置 `COURSE_MATERIALS`，无用户上传

**新增数据表**：
- `course_materials` - 课程资料元数据
- `course_material_chunks` - 文档切分块
- `knowledge_ingestion_jobs` - 解析任务
- `knowledge_point_bindings` - 知识点绑定

**新增后端模块**：
- `backend/app/routers/knowledge.py` - 知识库 API
- `backend/app/services/knowledge_service.py` - 知识库服务
- `backend/app/repositories/knowledge_repo.py` - 知识库数据访问
- `backend/app/rag/parser.py` - 文档解析器
- `backend/app/rag/chunker.py` - 文档切分器

**新增前端页面**：
- 改 `TeacherKnowledgeBase.tsx`：上传/解析/检索/证据预览

**功能清单**：
- [x] 教师上传 PDF / Markdown / Word / PPT
- [x] 系统识别文件类型并解析
- [x] 按章节/段落切 chunk
- [ ] 自动匹配课程知识点
- [x] 每个 chunk 保存：课程/知识点/来源文件/页码/内容/检索关键词
- [x] 检索返回证据片段（不只是模型答案）
- [x] 检索测试界面展示命中文档、chunk、页码、相关度
- [x] 数据库表 course_materials / course_material_chunks
- [x] Knowledge Repository / Service / Router 完整实现
- [x] retriever.py 优先查数据库，fallback 到静态 COURSE_MATERIALS

**验收标准**：
- 上传一份数据库课程 Markdown/PDF
- 后端生成 chunks
- 检索"事务隔离级别"能返回对应片段
- Agent 生成资源时引用上传资料

**优先级**：🔴 P0（所有后续功能依赖此模块）

---

### 3.2 模块二：学生画像 Learner Memory

**目标**：学生画像从静态卡片升级为动态 Learner Memory，对话式构建

**现状**：`student_profiles` 表有 6 维度，但无对话式构建界面

**新增数据表**：
- `profile_dialog_messages` - 对话历史
- `profile_extraction_events` - 抽取事件
- `profile_update_history` - 画像更新历史

**新增后端模块**：
- `backend/app/routers/profiles.py` - 新增 dialog 相关接口
- `backend/app/services/profile_dialog_service.py` - 对话服务

**新增接口**：
- `POST /api/profiles/{id}/dialog` - 发送对话消息
- `GET /api/profiles/{id}/dialog` - 获取对话历史
- `POST /api/profiles/{id}/apply-extraction` - 应用抽取结果到画像

**画像维度（固定为产品能力）**：
1. 知识基础（knowledge_base）
2. 当前水平（current_level）
3. 薄弱知识点（weak_points）
4. 易错点（error_prone_points）
5. 学习目标（learning_goal）
6. 认知风格（cognitive_style）
7. 资源偏好（resource_preferences）
8. 学习时间约束（time_constraints）
9. 实践能力（practice_level）
10. 学习动机（motivation）

**前端改造**：
- [x] 改 `StudentProfile.tsx`：真实消息流 + 抽取结果确认卡
- [x] 改 `profilesApi`：新增 dialog 方法

**功能清单**：
- [x] 学生输入自然语言描述学习情况
- [x] 后端调用 LLM 抽取结构化画像数据
- [x] 前端展示"抽取结果确认卡"
- [x] 用户确认后写入 `student_profiles`
- [ ] 后续测验、反馈、答疑也会写入学习事件

**验收标准**：
- 对话能保存到 `profile_dialog_messages`
- 抽取结果能应用到 `student_profiles`
- 应用后刷新页面，画像维度变化仍存在
- 画像至少展示 6 个维度

**优先级**：🔴 P0（核心链路第二步）

---

### 3.3 模块三：智能体编排中心 Agent Orchestration Console

**目标**：智能体工作台从"流程动画"升级为真正的执行控制台

**现状**：`AgentWorkbench.tsx` 有流程展示，但存在重复生成问题

**当前问题**：
- SSE 完成后又调用 `agentsApi.generate()` 造成重复生成
- 工具调用、证据绑定、任务状态不够产品化
- 学生下拉框是输入框，不够友好

**新增数据表**：
- `agent_runs` - 智能体运行记录
- `agent_run_steps` - 步骤记录
- `agent_tool_calls` - 工具调用记录
- `agent_evidence_refs` - 证据引用记录

**工作流状态标准化**：
```ts
{
  run_id: string,
  task_id: string,
  current_node: string,
  node_status: "waiting" | "running" | "done" | "error",
  input_snapshot: object,
  output_snapshot: object,
  evidence_refs: string[],
  token_usage: number,
  cost: number,
  latency: number,
  quality_score: number,
  revision_count: number
}
```

**后端改造**：
- 改 `workflow.py`：`done` 事件返回完整 `result`
- 改 `agents.py`：接收 `generation_goal` 和 `enable_review` 参数

**前端改造**：
- 改 `AgentWorkbench.tsx`：收到 `done` 直接 `setResult`，删二次生成
- 学生下拉框改为真实 `profilesApi.list()`
- 知识点改为完整 checkbox 列表
- 资源结果 Markdown 渲染 + 证据来源 + 质量分 + 耗时

**功能清单**：
- [x] SSE `done` 事件直接设置结果，不二次生成
- [x] 学生下拉框显示姓名、掌握度、薄弱点
- [x] 知识点完整 checkbox 列表
- [x] 生成结果 Markdown 渲染
- [x] 展示证据来源、质量评分、返工次数、生成耗时
- [ ] "保存资源"写入资源库
- [ ] 保存后能在 `/teacher/resources` 查到

**验收标准**：
- 启动生成后，执行链路逐步变绿
- SSE 完成后不再二次生成
- 生成结果可保存
- 保存后资源库出现新资源

**优先级**：🔴 P0（核心链路第三步）

---

### 3.4 模块四：资源生成工厂 Resource Factory

**目标**：资源生成不只是返回 Markdown，不同类型要有差异化展示

**现状**：资源列表有类型区分，详情页无差异化渲染

**新增组件**：
- `frontend/src/app/components/resource/ResourceRenderer.tsx`

**资源类型与渲染方式**：

| 类型 | 渲染方式 |
|------|---------|
| lecture（讲义） | Markdown 正文 + 引用来源 |
| quiz（题库） | 题目卡片 + 答案折叠 |
| code_case（代码案例） | 代码块 + 运行步骤 |
| ppt（PPT大纲） | 分镜卡片 |
| video_script（视频脚本） | 镜头脚本分段 |
| mindmap（思维导图） | 树状结构 |
| review（复习计划） | 时间轴 |
| test（阶段测验） | 测验卡片 |

**功能清单**：
- [x] `ResourceRenderer` 按 `resource_type` 分发渲染
- [x] 讲义 Markdown 渲染
- [x] 题库题目卡片 + 答案折叠
- [x] 代码案例高亮 + 步骤
- [x] 证据来源可见
- [x] PPT 分镜卡片展示
- [x] 视频脚本分段展示
- [x] 思维导图树状结构
- [x] 复习计划时间轴展示
- [x] 测验卡片交互答题

**验收标准**：
- 至少 5 类资源有不同展示样式
- Markdown 不再纯文本显示
- 证据来源可见

**优先级**：🟡 P1

---

### 3.5 模块五：学习路径图谱 Adaptive Learning Path

**目标**：学习路径从静态路线升级为可视化图谱 + 动态调整

**现状**：`planning_agent.py` 有路径规划逻辑，但无前端图谱展示

**新增组件**：
- `frontend/src/app/components/learning/LearningPathGraph.tsx`

**图谱节点颜色规则**：
- 🟢 绿色：`mastery >= 0.75`（已掌握）
- 🟠 橙色：`0.5 <= mastery < 0.75`（待巩固）
- 🔴 红色：`mastery < 0.5`（薄弱点）
- 🔵 蓝色描边：当前推荐学习节点

**路径生成逻辑**：
1. 读取学生画像
2. 读取知识点依赖
3. 找出低掌握度知识点
4. 找前置知识点
5. 匹配资源偏好
6. 排出学习顺序

**前端**：
- `/student/learning-path`：图谱 + 今日学习顺序 + 推荐资源

**功能清单**：
- [x] 知识图谱可视化
- [x] 节点颜色反映掌握度
- [x] 点击薄弱点能看到推荐资源
- [x] 反馈后刷新，节点颜色能变化

**验收标准**：
- 学生端能看到知识点依赖图
- 点击薄弱点能看到推荐资源
- 反馈后刷新，节点颜色能变化

**优先级**：🟡 P1

---

### 3.6 模块六：学习辅导 Copilot Tutor Chat

**目标**：Tutor 从借资源生成接口答疑，升级为独立学习辅导智能体

**现状**：`StudentTutor.tsx` 调用 `agentsApi.generate()`，不是真正答疑

**新增后端模块**：
- [x] `backend/app/services/tutor_service.py` - Tutor Service 实现 chat/feedback/sessions
- [x] `backend/app/routers/tutor.py` - Tutor Router 实现 REST API
- [x] `database/15_create_tutor_sessions.sql` - 答疑会话表

**接口**：
- `POST /api/tutor/chat` - 答疑
- `POST /api/tutor/feedback` - 反馈
- `GET /api/tutor/sessions` - 会话历史

**回答结构**：
```json
{
  "answer": "Markdown 正文",
  "explanation_level": "basic",
  "citations": [{"chunk_id": "", "content": "", "source": ""}],
  "diagram": {},
  "practice_questions": [],
  "recommended_resources": [],
  "profile_updates": []
}
```

**多模态卡片**（先不做真视频）：
- 图解说明：返回结构化步骤图
- 代码实操：返回代码块
- 练习题：返回题目 JSON

**功能清单**：
- [x] 独立 Tutor Chat 接口 (`tutorApi.chat()`)
- [x] 结合画像和课程知识库回答
- [x] 回答带引用来源 (CitationsCard)
- [x] "没理解"降低解释难度，推荐基础资源 (handleFeedback)
- [x] 回答中出现图解/练习/代码之一 (PracticeCard, ResourcesCard)

**验收标准**：
- 学生问"可重复读和串行化区别"，回答带课程知识库引用
- 点"没理解"，系统降低解释难度，推荐基础资源

**优先级**：🟡 P1（加分项）

---

### 3.7 模块七：反馈驱动推荐重排

**目标**：评估反馈后动态调整学习资源推送策略和学习计划

**现状**：`feedbacks.py` 能更新 mastery，但"评估→调整推送"未闭环

**后端改造**：
- 改 `feedbacks.py` 返回：`updated_profile` + `mastery_changes` + `next_resources` + `path_adjustment`
- 新增 `LearningService.recommend_resources(profile_id, course_id)`

**推荐逻辑**：
1. 低 mastery 知识点优先
2. 匹配学生资源偏好
3. 未学习过的资源
4. 教师审核通过资源

**前端改造**：
- 改 `LearningFeedback.tsx`：展示"画像已更新" + "推荐策略变化"
- 改 `StudentDashboard.tsx`："今日学习路径"从推荐接口取

**功能清单**：
- [ ] 提交 quiz_score < 60，对应知识点 mastery 降低
- [ ] 推荐资源切换到基础讲义/练习题
- [ ] 学习路径中该知识点变为优先学习
- [ ] 前端展示"原推荐 → 新推荐"对比

**验收标准**：
- 提交低分反馈后，推荐资源切换
- 路径中该知识点优先级提升

**优先级**：🟠 P2（加分项）

---

### 3.8 模块八：管理端指标真实化

**目标**：管理端从假数据看板升级为真实平台运营指标

**现状**：管理端有页面但部分数据可能是 mock

**需真实化的指标**：
- 今日调用次数
- 平均延迟
- Token 成本
- RAG 命中率
- 资源生成成功率
- 审核通过率

**功能清单**：
- [ ] 成本统计从 `cost_records` 真实聚合
- [ ] 调用统计从 `invocations` 真实聚合
- [ ] RAG 命中率从检索日志计算

**优先级**：🟠 P2

---

## 四、赛题要求覆盖状态

### 4.1 必做要求完成度：14/16 (87.5%)

| # | 赛题要求 | 状态 | 实现文件 | 备注 |
|---|---------|------|---------|------|
| 1 | 面向高等教育学习场景 | ✅ 已完成 | `database/` | 3门课程 |
| 2 | 以具体高校课程为切入点 | ✅ 已完成 | `database/` | 数据库原理等 |
| 3 | 学生画像不少于6个维度 | ✅ 已完成 | `student_profiles`表 | 10个维度 |
| 4 | 对话式学习画像自主构建 | ✅ 已完成 | `StudentProfile.tsx` + `profiles.ts` | 模块二 |
| 5 | 画像随学随新、动态更新 | ✅ 已完成 | `feedbacks.py` | UPSERT |
| 6 | 开发智能学习多智能体系统 | ✅ 已完成 | `workflow.py` | 5智能体 |
| 7 | 多智能体协同生成资源 | ✅ 已完成 | `workflow.py` | D→P→G→A→TR |
| 8 | 至少生成5种类型资源 | ✅ 已完成 | `resource_generation_agent.py` | 6种 |
| 9 | 个性化学习路径规划 | ⚠️ 部分 | `planning_agent.py` | 无图谱 |
| 10 | 学习资源精准推送 | ⚠️ 部分 | `learning_service.py` | 未闭环 |
| 11 | 流式输出或进度追踪 | ✅ 已完成 | `workflow.py` | SSE |
| 12 | Markdown渲染 | ✅ 已完成 | `marked` | AgentWorkbench |
| 13 | 多模态内容卡片化展示 | ⚠️ 部分 | `ResourceLibrary.tsx` | 无详情渲染 |
| 14 | 防幻觉与内容安全过滤 | ✅ 已完成 | `rag/` | BM25+evidence |
| 15 | 生成资源时绑定知识库依据 | 🔴 **待完成** | — | 模块一 |
| 16 | 至少一门完整课程知识库 | 🔴 **待完成** | — | 模块一 |

### 4.2 加分要求完成度：1/2 (50%)

| # | 加分要求 | 状态 | 实现文件 | 备注 |
|---|---------|------|---------|------|
| 17 | 智能辅导（多模态答疑） | 🔴 **待完成** | — | 模块六 |
| 18 | 学习效果评估→推送策略动态调整 | ⚠️ 部分 | `assessment_agent.py` | 未闭环 |

### 4.3 文档要求完成度：3/3 (100%)

| # | 文档要求 | 状态 | 文件 |
|---|---------|------|------|
| 19 | 系统开发说明书 | ✅ | `docs/系统总体设计.md` |
| 20 | 测试说明书 | ✅ | `docs/测试说明书.md` |
| 21 | AI Coding工具说明 | ✅ | `docs/AI_Coding工具使用说明.md` |

---

## 五、技术栈落地状态

| 技术 | 状态 | 说明 |
|------|------|------|
| React 18 + Vite + TS | ✅ 已落地 | 前端正常运行 |
| FastAPI + Pydantic | ✅ 已落地 | 后端正常运行 |
| MySQL | ✅ 已落地 | 业务表 |
| PostgreSQL + pgvector | ⚠️ 预留 | docker有配置，BM25替代已实现 |
| LangGraph | ✅ 已落地 | workflow.py完整 |
| LLM Gateway | ✅ 已落地 | Mock+OpenAI+MiniMax |
| Redis + Celery | ⚠️ 部分 | docker有，代码未接入 |
| BM25 RAG | ✅ 已落地 | 内置COURSE_MATERIALS |
| Markdown渲染 | ✅ 已完成 | marked已集成 |
| Tailwindcss Typography | ✅ 已完成 | @tailwindcss/typography |
| 角色隔离 | ✅ 已完成 | student_member/teacher/admin |

---

## 六、核心文件清单

### 智能体核心
- `backend/app/agents/workflow.py` (641行) - LangGraph完整实现
- `backend/app/agents/resource_generation_agent.py` (317行) - 6类资源生成
- `backend/app/agents/diagnosis_agent.py` (194行) - 学习诊断+RAG
- `backend/app/agents/planning_agent.py` - 学习路径规划
- `backend/app/agents/assessment_agent.py` - 学习效果评估
- `backend/app/agents/teacher_review_agent.py` - 教师审核

### RAG（待升级为真实知识库）
- `backend/app/rag/document_loader.py` (518行) - 内置COURSE_MATERIALS
- `backend/app/rag/retriever.py` (185行) - BM25检索

### 数据层
- `backend/app/repositories/statistics_learning_repo.py` (309行)
- `database/10_insert_a3_initial_data.sql` - 种子数据

### 前端
- `frontend/src/app/pages/AgentWorkbench.tsx` - 智能体工作台
- `frontend/src/app/pages/StudentProfile.tsx` - 学生画像（待升级）
- `frontend/src/app/pages/TeacherKnowledgeBase.tsx` - 知识库（待升级）
- `frontend/src/app/pages/LearningAnalytics.tsx` - 学习分析
- `frontend/src/app/pages/ResourceLibrary.tsx` - 资源库
- `frontend/src/lib/router-guard.tsx` - 角色隔离

---

## 七、推荐开发顺序

### 第一优先级（核心链路，必须先跑通）

| 顺序 | 模块 | 理由 |
|------|------|------|
| 1 | 模块一：课程知识库 | 所有后续功能依赖此模块 |
| 2 | 模块二：对话式画像构建 | 画像是智能体决策依据 |
| 3 | 模块三：修AgentWorkbench | 让智能体真正协作 |

### 第二优先级（链路跑通后加体验）

| 顺序 | 模块 | 理由 |
|------|------|------|
| 4 | 模块四：资源类型渲染器 | 不同资源不同展示 |
| 5 | 模块五：学习路径图谱 | 可视化路径调整 |
| 6 | 模块六：Tutor Chat | 接通画像和知识库的Copilot |

### 第三优先级（最后完善）

| 顺序 | 模块 | 理由 |
|------|------|------|
| 7 | 模块七：反馈驱动推荐重排 | 画像更新后的真实效果 |
| 8 | 模块八：管理端指标真实化 | 平台运营能力 |

---

## 八、版本历史

| 日期 | 更新内容 | 负责人 |
|------|---------|--------|
| 2026-07-08 | 完成模块六：Tutor Chat 前端 - tutorApi 独立答疑接口、CitationsCard/PracticeCard/ResourcesCard 多模态卡片、Markdown 渲染、学生画像上下文、反馈机制 | Claude |
| 2026-07-08 | 完成模块四：ResourceRenderer 资源类型差异化渲染器 - 8类渲染器组件、ResourceLibrary 详情抽屉集成、EvidenceSources 证据来源组件 | Claude |
| 2026-07-08 | 完成模块五：学习路径图谱 - LearningPathGraph ECharts组件、节点颜色规则（绿/橙/红/蓝）、两栏布局改造、今日学习顺序列表、节点点击跳转资源页 | Claude |
| 2026-07-08 | 完成模块三：AgentWorkbench 执行闭环修复 - SSE done 事件返回完整结果、移除二次生成、学生下拉框、知识点 checkbox 列表、Markdown 渲染 | Claude |
| 2026-07-08 | 完成模块一后端：数据库表 + KnowledgeRepo/Service/Router + parser.py + retriever.py | Claude |
| 2026-07-08 | 完成模块一前端：knowledge API + TeacherKnowledgeBase 三栏布局 | Claude |
| 2026-07-08 | 完成模块二前端：profilesApi 新增 dialog 方法 + StudentProfile 真实消息流 | Claude |
| 2026-07-07 | 重写本文档：成熟版产品架构 + 8个开发模块 + 核心链路 | Claude |
| 2026-07-07 | 修复角色值匹配问题 (student_member vs student) | Claude |
| 2026-07-07 | 修复角色隔离Bug：移除DEV_BYPASS、禁用ROLE_SWITCH | Claude |
| 2026-07-07 | 添加Markdown渲染集成 (marked + typography) | Claude |
| 2026-06-16 | 完成核心功能开发（5智能体+LangGraph+RAG+LLM Gateway） | 开发团队 |

---

## 九、AI 智能体工作指南

### 读取本文件
在开始任何工作时，AI 智能体**必须**首先读取本文件了解：
1. 当前开发阶段和优先级
2. 正在进行的模块
3. 已完成和待完成的功能

### 更新本文件
完成工作后，AI 智能体**必须**更新本文件：
1. 如果完成了某个功能清单中的条目，将 `[ ]` 改为 `[x]`
2. 如果发现了新的缺口或问题，在相应部分添加条目
3. 在"版本历史"部分添加更新记录

### 开发原则
1. **先跑通核心链路**：先做模块一+二+三，确保数据流打通
2. **复用现有代码**：优先在现有 Repository/Service 上扩展，不另起架构
3. **不破坏现有功能**：修改前验证不影响现有流程
4. **保持文档同步**：代码变更后同步更新本文档

### 赛题要求优先级
1. **必做要求（16项）**：优先确保全部完成，尤其是模块一、二
2. **加分要求（2项）**：在时间允许的情况下完善（模块六、七）
3. **文档要求（3项）**：确保全部完成

### 演示主线建议
成熟版演示应该讲一个完整故事：
```
教师上传课程资料 → 知识库建立
↓ 
学生通过对话构建画像 
↓
系统识别学生薄弱点 
↓
教师在智能体工作台为该学生生成个性化资源 
↓
多智能体执行：诊断、检索、规划、生成、审核 
↓
资源生成后绑定证据来源 
↓
教师审核通过 
↓
学生收到个性化路径和资源 
↓
学生向Tutor提问 
↓
学生做反馈或测验 
↓
系统更新画像并调整学习路径 
↓
管理端看到调用审计、成本和质量数据
```
