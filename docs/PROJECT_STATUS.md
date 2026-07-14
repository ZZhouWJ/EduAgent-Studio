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
| 产品定位 | **面向高校课程的 AI 学习智能体操作系统**（教师用多智能体编排生成资源，学生用 Tutor Copilot 答疑） |
| 核心主线 | 课程知识空间 → 学习画像 → **（教师）多智能体编排生成资源** → 资源工厂 → **（学生）Tutor Copilot 答疑** → 效果闭环 → 治理审计 |

> **注意**：多智能体编排（5 Agent + LangGraph workflow）是**教师端**功能，用于生成个性化资源；**学生端**使用 Tutor Supervisor（单 Supervisor + 工具注册表）进行实时答疑。
| 开发阶段 | 核心链路打通中，补充关键缺口（P0优先） |
| 最近更新 | 2026-07-14 |

---

## 二、产品架构（成熟版）

> EduAgent Studio 不是资源生成工具，而是"面向高校课程的学习智能体操作系统"。

### 2.1 七大核心模块

| 模块 | 定位 | 状态 |
|------|------|------|
| **课程知识空间** | 教师上传资料，系统自动解析、切分、标注知识点、建立可检索知识库 | ✅ 后端已完成 |
| **学生学习画像** | 学生通过对话、测验、学习行为持续形成动态画像（6+维度） | ⚠️ 待升级 |
| **资源生成工厂** | 针对不同学生和知识点生成讲义、题库、案例、PPT、视频脚本、思维导图、复习计划 | ⚠️ 由 Tutor Supervisor 按需调用，非独立流水线 |
| **学习辅导 Copilot** | **（学生端）** 学生持续提问，Tutor Supervisor 自动调用工具生成多模态答疑内容 | ⚠️ 框架完成，但knowledge_context未注入LLM，image/tts/ppt工具是Stub |
| **学习效果闭环** | 学生学习、反馈、测验后，系统更新画像、调整路径、重排推荐资源 | ⚠️ 部分完成 |
| **治理与审计** | 教师审核、引用溯源、防幻觉、成本统计、模型调用日志全部可见 | ✅ 基础完成 |

### 2.2 数据流主线（核心链路）

> **架构说明**：多智能体协作是**学生端**答疑时的动态能力，不是教师端流水线。
> 赛题要求："通过与学生的智能交互，大模型结合 AI 前沿技术和工具...须由不同角色的智能体协作完成"

```
教师上传课程资料 → 知识库（解析/切分/索引）
        ↓
学生通过对话构建画像 → Learner Memory（6+维度动态画像）
        ↓
画像 + 知识库 → 学生提问
        ↓
Tutor Supervisor 协调多工具/多技能循环（动态选择，以需求满足为终止条件）
  ↙ 工具：retrieve_knowledge / quiz_agent / mindmap_agent / code_case_agent / ...
  ↘ 技能：explanation_skill / error_analysis_agent / planning_agent / ...
        ↓
学生收到多模态答疑（文字+卡片+图解+练习题+...）
        ↓
画像更新 → 路径调整 → Tutor Copilot 持续辅导
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
- [x] 自动匹配课程知识点（BM25 匹配 → kp_chunk_links）
- [x] 每个 chunk 保存：课程/知识点/来源文件/页码/内容/检索关键词
- [x] 检索返回证据片段（不只是模型答案）
- [x] 检索测试界面展示命中文档、chunk、页码、相关度
- [x] 数据库表 course_materials / course_material_chunks
- [x] Knowledge Repository / Service / Router 完整实现
- [x] retriever.py 优先查数据库，fallback 到静态 COURSE_MATERIALS
- [x] 证据优先生成链路：_retrieve_evidence → prompt注入 → 引用校验 → evidence_links写入DB
- [x] 知识点-Chunk 绑定管理界面（TeacherKnowledgeBase.tsx）
- [x] 资源审核面板展示可信度 + 引用来源（AgentWorkbench.tsx）

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

### 3.3 模块三：Tutor Supervisor 动态多智能体编排

**目标**：学生提问时，Tutor Supervisor 动态协调多工具/多技能循环，以用户需求满足为终止条件

**现状**：`tutor_supervisor.py` 已有框架，但以下缺口待修复：
- `knowledge_context` 未注入 LLM（缺口A）
- image_agent / tts_tool / ppt_agent 是 Stub（缺口B）
- 嵌入语法无兜底（缺口C）
- 最大步数 8 步限制应改为"需求满足即终止"

**核心设计**：
- **终止条件**：模型输出纯文本回答（无 tool_calls）即为需求满足，不再强制限制步数
- **工具选择**：两级路由（规则预筛选 → 模型自主选择），模型按需调用工具
- **进度展示**：GPT/Gemini 风格底部动画，显示当前调用的工具名称

**与赛题的对应关系**：
> 赛题原文："通过**与学生的智能交互**，大模型结合 AI 前沿技术和工具，...**须由不同角色的智能体协作完成**"
> → Tutor Supervisor 就是这个"不同角色的智能体协作"的具体实现

**已有文件**：
- `tutor_supervisor.py` — Supervisor 主循环（Tool Calling）
- `tool_registry.py` — 统一工具/技能注册表
- `tutor_tool_handlers.py` — 各工具处理器
- `StudentTutor.tsx` — 前端答疑页面

**功能清单**：
- [x] Supervisor Tool Calling 循环
- [x] 两级路由（规则预筛选 + 模型自主选择）
- [x] SSE 事件流（supervisor.tool_choice / tool.started / tool.completed）
- [x] 内容块嵌入语法（:::type:block_id:::）
- [x] 执行轨迹展示（ExecutionTrace）
- [ ] **knowledge_context 注入 LLM**（缺口A）
- [ ] **image_agent 真实实现**（缺口B）
- [ ] **tts_tool 真实实现**（缺口B）
- [ ] **ppt_agent 真实实现**（缺口B）
- [ ] **GPT/Gemini 风格底部思考动画**（前端）

**验收标准**：
- 学生问"用思维导图整理 SQL JOIN"，Tutor 自动调用 mindmap_agent，底部显示"正在生成思维导图..."
- 学生问"出一道练习题"，Tutor 自动调用 quiz_agent
- 学生问复杂问题，Tutor 链式调用 retrieve_knowledge → quiz_agent → explanation_skill
- 过程中底部进度条类似 GPT/Gemini 对话框的转圈动画

**优先级**：🔴 P0（核心链路，竞赛演示核心）

---

### 3.4 模块四：资源生成工厂 Resource Factory

**目标**：资源生成不只是返回 Markdown，不同类型要有差异化展示

**现状**：✅ 差异化渲染组件已完整实现，`ResourceRenderer` 支持 8 类资源

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

**现状**：`LearningPathGraph.tsx` 存在于学习分析页面，但 Tutor 答疑页面无路径图谱集成

**已有组件**：
- `frontend/src/app/components/learning/LearningPathGraph.tsx` — 用于学习分析页

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
- `/analytics`：图谱 + 今日学习顺序 + 推荐资源（已实现）

**功能清单**：
- [x] 知识图谱可视化（学习分析页）
- [x] 节点颜色反映掌握度
- [x] 点击薄弱点能看到推荐资源
- [x] 反馈后刷新，节点颜色能变化
- [ ] **Tutor 答疑页面集成路径图谱**（待实现）

**验收标准**：
- 学生端能看到知识点依赖图
- 点击薄弱点能看到推荐资源
- 反馈后刷新，节点颜色能变化

**优先级**：🟡 P1

---

### 3.6 模块六：Tutor 前端体验（GPT/Gemini 风格进度展示）

**目标**：学生在提问时能看到类似 GPT/Gemini 对话框底部的动态进度动画

**现状**：已有 ExecutionTrace 展示执行轨迹，但缺少 GPT/Gemini 风格的底部思考动画

**GPT/Gemini 风格动画设计**：
```
┌─────────────────────────────────────────────┐
│  正在思考...                                │
│  ○ retrieve_knowledge                       │
│  ◉ 正在生成思维导图...                      │
│  ○ quiz_agent                              │
└─────────────────────────────────────────────┘
```
- **动画**：底部固定区域，显示当前正在执行的工具名称 + 转圈动画
- **工具图标**：每个工具显示小图标（🔍检索 🧠思维导图 📝练习题 💻代码）
- **完成状态**：工具完成后打勾，切换到下一个
- **流式文本**：模型输出的文字实时显示在气泡中

**已有基础**：
- `StudentTutor.tsx` 中的 `ExecutionTrace` 组件（工具调用轨迹）
- SSE `tool.started` / `tool.completed` 事件流
- `activeEvents` 状态管理

**待实现**：
- [ ] 底部固定思考动画条（类似 GPT 的"正在思考..."）
- [ ] 实时流式文字渲染（Markdown 逐字显示）
- [ ] 工具图标 + 状态动画
- [ ] "需求满足"时动画收起，显示最终回答

**验收标准**：
- 学生提问后，底部立即显示"正在思考..."
- 调用工具时，底部显示"正在检索知识库..." → "正在生成思维导图..." → ...
- 工具完成后显示 ✓，切换下一个
- 全部完成后，动画收起，回答以气泡形式显示

**优先级**：🔴 P0（核心演示体验）

---

### 3.7 模块七：（已废弃：教师端 LangGraph 流水线）

> ⚠️ `workflow.py`（LangGraph 多智能体流水线）和 `AgentWorkbench.tsx`（教师端工作台）已从赛题实现中移除。
> 赛题要求的多智能体协作是**学生端** Tutor Supervisor 的动态工具调用，不是教师端的固定流水线。

**已有功能去向**：
- `resource_generation_agent.py` → 由 Tutor Supervisor 在答疑时按需调用，非独立流水线
- `AgentWorkbench.tsx` → 页面保留但非核心演示路径
- `workflow.py` → 代码保留，不再被主动使用

---

### 3.8 模块八：反馈驱动推荐重排
- 代码实操 → ContentBlockRenderer (CodeCaseBlock)
- 练习题 → ContentBlockRenderer (QuizBlock)
- 图片生成 → image_agent（**Stub**，待实现）
- 语音合成 → tts_tool（**Stub**，待实现）
- PPT大纲 → ppt_agent（**Stub**，待实现）

**功能清单**：
- [x] 独立 Tutor Chat SSE 流式接口 (`tutorApi.chat()`)
- [x] Supervisor 多工具 Agent 编排 (`tutor_supervisor.py`)
- [x] 执行轨迹展示（ExecutionTrace）
- [x] 内容块卡片渲染（ContentBlockRenderer）
- [x] 回答带引用来源 (CitationsCard)
- [x] "没理解"降低解释难度，推荐基础资源 (handleFeedback)
- [x] 学习路径图谱（LearningPathGraph，在学习分析页，Tutor页未集成）
- [ ] **knowledge_context 注入 LLM**（缺口A）
- [ ] **image_agent 真实实现**（缺口B）
- [ ] **tts_tool 真实实现**（缺口B）
- [ ] **ppt_agent 真实实现**（缺口B）
- [ ] **嵌入语法兜底**（缺口C）

**验收标准**：
- 学生问"可重复读和串行化区别"，回答带课程知识库引用（**knowledge_context 注入后生效**）
- 点"没理解"，系统降低解释难度，推荐基础资源
- 能生成真实图片/音频/PPT（**Stub 替换后生效**）

**优先级**：🔴 P0（核心链路，关乎竞赛演示质量）

---

### 3.7 模块七：反馈驱动推荐重排

**目标**：评估反馈后动态调整学习资源推送策略和学习计划

**现状**：⚠️ 部分完成。后端反馈逻辑存在，但"评估→调整→学生感知→再次评估"完整闭环未实现

**后端改造**：
- ✅ 改 `feedbacks.py` 返回：`updated_profile` + `mastery_changes` + `next_resources` + `path_adjustment`
- ✅ 新增 `LearningService.recommend_resources(profile_id, course_id)`
- ✅ 新增 `LearningRepository.get_recommended_resources(profile_id, course_id, limit)`

**推荐逻辑**：
1. 低 mastery 知识点优先
2. 匹配学生资源偏好
3. 未学习过的资源
4. 教师审核通过资源

**前端改造**：
- 改 `LearningFeedback.tsx`：展示"画像已更新" + "推荐策略变化"
- 改 `StudentDashboard.tsx`："今日学习路径"从推荐接口取

**功能清单**：
- [x] 提交 quiz_score < 60，对应知识点 mastery 降低
- [x] 推荐资源切换到基础讲义/练习题
- [x] 学习路径中该知识点变为优先学习
- [x] 前端展示"原推荐 → 新推荐"对比

**验收标准**：
- 提交低分反馈后，推荐资源切换
- 路径中该知识点优先级提升

**优先级**：🟠 P2（加分项）

---

### 3.8 模块八：管理端指标真实化

**目标**：管理端从假数据看板升级为真实平台运营指标

**现状**：✅ 后端已完成

**新增后端模块**：
- `backend/app/repositories/statistics_repo.py` - 新增 `get_platform_stats()`、`get_cost_by_model()`、`get_rag_hit_rate()`、`get_resource_stats()` 方法
- `backend/app/services/statistics_service.py` - 新增 `get_platform_overview()`、`get_cost_by_model_api()`、`get_resource_stats_api()` 方法
- `backend/app/routers/statistics.py` - 新增 `/api/statistics/platform`、`/api/statistics/cost-by-model`、`/api/statistics/resources` 接口

**新增前端改造**：
- `frontend/src/lib/api/statistics.ts` - 新增 `PlatformOverview`、`CostByModel`、`ResourceStats` 类型及 API 方法
- `frontend/src/app/pages/AdminDashboard.tsx` - 使用 `getPlatformOverview()` 真实 API
- `frontend/src/app/pages/AdminCosts.tsx` - 使用 `getCostByModel()` 真实 API

**功能清单**：
- [x] 成本统计从 `cost_records` 真实聚合 (`get_platform_stats`)
- [x] 调用统计从 `ai_invocations` 真实聚合 (`get_platform_stats`)
- [x] 资源统计从 `learning_resources` 真实聚合 (`get_resource_stats`)
- [x] 按模型成本统计 (`get_cost_by_model`)
- [x] RAG 命中率统计 (`get_rag_hit_rate`)
- [x] 前端 AdminDashboard 使用真实 API
- [x] 前端 AdminCosts 使用 `getCostByModel()` API

**优先级**：🟠 P2

---

## 四、赛题要求覆盖状态

### 4.1 必做要求完成度：约 10/16 ⚠️

> 修订时间：2026-07-14。文档原声称 16/16 (100%) 与实际不符，以下为真实状态。

| # | 赛题要求 | 状态 | 实现文件 | 缺口说明 |
|---|---------|------|---------|---------|
| 1 | 面向高等教育学习场景 | ✅ 已完成 | `database/` | 3门课程 |
| 2 | 以具体高校课程为切入点 | ✅ 已完成 | `database/` | 数据库系统原理为主场景 |
| 3 | 学生画像不少于6个维度 | ✅ 已完成 | `student_profiles`表 | 10个维度 |
| 4 | 对话式学习画像自主构建 | ✅ 已完成 | `StudentProfile.tsx` + `profiles.ts` | 对话流+确认卡 |
| 5 | 画像随学随新、动态更新 | ✅ 已完成 | `feedbacks.py` | UPSERT 写入 |
| 6 | 开发智能学习多智能体系统 | ✅ 已完成 | `tutor_supervisor.py` | Tool Calling 循环 + 工具注册表 |
| 7 | 多智能体协同生成资源 | ✅ 已完成 | `tutor_supervisor.py` | 学生提问时动态协调多工具协作 |
| 8 | 至少生成5种类型资源 | ✅ 已完成 | `resource_generation_agent.py` | 6种资源类型 |
| 9 | 个性化学习路径规划 | ⚠️ 部分 | `planning_agent.py` | Agent存在，但Tutor页面无图谱可视化 |
| 10 | 学习资源精准推送 | ⚠️ 部分 | `learning_service.py` | 推荐逻辑存在，闭环不完整 |
| 11 | 流式输出或进度追踪 | ✅ 已完成 | `workflow.py` + `tutor_supervisor.py` | SSE 完整事件流 |
| 12 | Markdown渲染 | ✅ 已完成 | `marked` + `ReactMarkdown` | AgentWorkbench + StudentTutor |
| 13 | 多模态内容卡片化展示 | ⚠️ 部分 | `ContentBlockRenderer.tsx` | 渲染器已实现，但内嵌嵌入依赖LLM遵守指令，稳定性有限 |
| 14 | 防幻觉与内容安全过滤 | ⚠️ 部分 | `rag/retriever.py` + `resource_generation_agent.py` | evidence链路代码存在，未端到端验证 |
| 15 | 生成资源时绑定知识库依据 | ⚠️ 部分 | `evidence_repo.py` + `kp_chunk_links` 表 | **关键缺口**：`knowledge_context`从未注入LLM messages |
| 16 | 至少一门完整课程知识库 | ⚠️ 部分 | `rag/document_loader.py` | 内置COURSE_MATERIALS（非用户上传），BM25可用 |

### 4.2 加分要求完成度：0/2 🔴

| # | 加分要求 | 状态 | 实现文件 | 缺口说明 |
|---|---------|------|---------|---------|
| 17 | 智能辅导（多模态答疑） | ⚠️ 框架完成，质量不足 | `tutor_supervisor.py` + `ContentBlockRenderer.tsx` | 答疑框架已建立，但image_agent/tts_tool是Stub；`knowledge_context`未注入LLM；内嵌嵌入依赖LLM遵守指令 |
| 18 | 学习效果评估→推送策略动态调整 | ⚠️ 部分完成 | `assessment_agent.py` + `LearningFeedback.tsx` | 评估逻辑存在，但"评估→调整→学生感知→再次评估"完整闭环未实现 |

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

## 七、推荐开发顺序（修订版 2026-07-14）

> ⚠️ **重大变更**：删除了教师端 LangGraph 流水线（workflow.py），多智能体协作全部聚焦学生端 Tutor Supervisor。

### 第一优先级（核心链路 P0）

| 顺序 | 模块 | 理由 |
|------|------|------|
| 1 | 模块六：Tutor 前端进度动画 | **最高优先**。GPT/Gemini风格底部思考动画是核心演示亮点 |
| 2 | 模块三：Tutor Supervisor 关键缺口修复 | knowledge_context注入LLM、Stub工具替换、嵌入语法兜底 |
| 3 | 模块一：课程知识库端到端验证 | knowledge_context 注入LLM后，检索结果才能真正被模型用到 |

### 第二优先级（链路质量提升 P1）

| 顺序 | 模块 | 理由 |
|------|------|------|
| 4 | 模块四：资源类型渲染器 | 不同资源已有差异化渲染，完善细节 |
| 5 | 模块五：学习路径图谱接入 Tutor | planning_agent 已有，Tutor页面集成图谱 |
| 6 | 模块二：对话式画像构建 | 对话流已完成，完善细节 |

### 第三优先级（加分项 P2）

| 顺序 | 模块 | 理由 |
|------|------|------|
| 7 | 模块八：反馈驱动推荐重排完整闭环 | 评估→调整→学生感知链路 |
| 8 | 管理端指标真实化 | 已有真实化实现 |

---

## 八、版本历史

| 日期 | 更新内容 | 负责人 |
|------|---------|--------|
| 2026-07-14 | **架构重大修正 + 文档全面更新**：(1) 删除教师端 LangGraph 流水线（workflow.py）从赛题核心，多智能体协作是学生端 Tutor Supervisor 的动态能力；(2) 必做要求 #6/#7 重新归属到 tutor_supervisor.py；(3) 模块三改为 Tutor Supervisor 动态编排；(4) 新增模块六：Tutor 前端进度动画（GPT/Gemini风格）；(5) 模块七废弃教师端流水线；(5) 全面修正各项完成度状态；(6) 新增缺口清单及优先级；(7) 开发顺序调整为 P0=Tutor前端动画，P1=Supervisor缺口修复，P2=其他 | Claude |
| 2026-07-08 | **证据优先生成链路（模块一收尾）**：新建 `kp_chunk_links`+`resource_evidence_links` 表 + 扩展 chunks/materials 字段；新建 `evidence_repo.py`（BM25匹配+CRUD）；改造 `knowledge_service.py` 解析后自动 BM25 匹配知识点写入 `kp_chunk_links`；改造 `resource_generation_agent.py` 新增 `_retrieve_evidence()`/`_verify_citations()`/`_format_evidence_context()`，prompt 注入教材原文，输出 trustworthiness + evidence_links；改造 `workflow.py` 串联 `course_id` 传递 + evidence_links 写入；改造 `agent_service.py` 保存资源时写入 `learning_resources` 表 + evidence_links；新增 `/knowledge/kp-chunk-links/pending` 等 4 个后端 API；TeacherKnowledgeBase.tsx 新增绑定管理面板；AgentWorkbench.tsx 展示可信度 + 引用来源 + 草稿警告 | Claude |
| 2026-07-08 | 完成模块八：管理端指标真实化 - statistics_repo.py 新增 get_platform_stats/get_cost_by_model/get_rag_hit_rate/get_resource_stats 方法、statistics_service.py 新增对应 service 方法、statistics.py 新增 3 个 API 路由、前端 AdminDashboard/AdminCosts 使用真实 API | Claude |
| 2026-07-08 | 完成模块七：反馈驱动推荐重排 - feedbacks.py 扩展返回值、LearningService.recommend_resources()、LearningRepository.get_recommended_resources()、学习路径调整逻辑 | Claude |
| 2026-07-08 | 完成模块七前端：LearningFeedback.tsx 提交后展示"画像已更新"+推荐策略变化卡片、StudentDashboard.tsx 新增今日推荐资源区块、learning.ts 新增 getRecommendedResources 方法 | Claude |
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
1. **P0 优先修复缺口**：先修复 Tutor Chat 的 knowledge_context 注入和 Stub 工具问题，确保核心演示链路质量
2. **复用现有代码**：优先在现有 Repository/Service 上扩展，不另起架构
3. **不破坏现有功能**：修改前验证不影响现有流程
4. **保持文档同步**：代码变更后同步更新本文档

### 赛题要求优先级
1. **P0（必做缺口修复）**：knowledge_context 注入LLM、image/tts/ppt Stub 替换
2. **P1（必做要求完善）**：学习路径图谱接入Tutor、推送闭环
3. **P2（加分项）**：完整多模态答疑、学习效果动态调整

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
↓  ← 当前缺口：knowledge_context未注入LLM；图片/语音工具是Stub
学生做反馈或测验
↓
系统更新画像并调整学习路径
↓
管理端看到调用审计、成本和质量数据
```

> ⚠️ Tutor 答疑环节存在关键缺口，演示前需优先修复（详见 `docs/A3当前实现状态与缺口清单.md` 第七节）
