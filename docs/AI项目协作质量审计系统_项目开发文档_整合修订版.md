# 《智研协作：面向高校项目协作的 AI 任务生成与质量审计管理系统》项目开发文档初稿

## 0. 文档说明

本文档用于指导《数据库管理实务》课程结课设计项目的选题论证、系统开发、数据库设计、界面设计、测试验收与课程报告撰写。本文档并非最终课程报告，而是项目开发阶段的总体方案说明，后续可在此基础上继续细化为需求规格说明书、数据库设计说明书、系统测试报告和最终课程报告。

本项目的核心定位不是“普通大模型聊天平台”，也不是“API 转发平台”，而是一个面向高校课程项目、科研训练、创新创业竞赛和团队材料协作场景的 AI 任务管理与质量审计系统。系统将大模型调用过程转化为可管理、可追踪、可审核、可版本化的项目协作流程，从而解决学生团队使用 AI 工具时存在的记录分散、质量不可控、版本混乱、结果难复用、模型效果难比较等问题。

---

# 一、项目背景与建设意义

## 1.1 项目背景

近年来，大模型工具已经广泛进入高校学生的课程学习、科研训练、学科竞赛和创新创业项目中。学生团队经常使用 ChatGPT、DeepSeek、Kimi、通义千问、Gemini 等模型完成资料整理、论文润色、代码解释、实验报告撰写、项目申报书修改、PPT 文案生成等任务。

然而，在实际使用过程中，AI 工具的使用方式往往比较分散：

1. 团队成员分别在不同平台使用不同模型；
2. 同一个项目的 AI 生成内容散落在个人聊天记录、Word 文档、微信文件和本地文本中；
3. 提示词不可复用，不同成员反复编写类似指令；
4. 模型输出质量参差不齐，存在空泛、幻觉、事实错误和格式不规范等问题；
5. 项目负责人难以判断哪些 AI 输出可以进入最终材料；
6. 指导教师或团队负责人难以追踪 AI 使用过程；
7. 项目材料在多次修改后缺少清晰的版本演进记录。

因此，仅仅提供一个“可以调用大模型”的工具并不能真正解决高校项目协作中的痛点。更有价值的系统应当把 AI 调用过程纳入项目管理体系，把每一次 AI 生成看作一次可记录、可比较、可审核、可追溯的项目任务成果。

## 1.2 建设意义

本项目拟设计并实现“智研协作：面向高校项目协作的 AI 任务生成与质量审计管理系统”。系统以项目空间为单位组织任务，以 Git 式版本管理思想管理 AI 输出结果，将“任务创建—模型生成—结果提交—质量审核—版本合并—成果归档”的过程结构化、数据库化和可视化。

系统建设意义主要体现在以下方面：

1. **提升团队协作效率**
   通过项目空间、成员分工、任务分配、AI 输出记录和结果归档，将团队成员分散的 AI 使用行为集中管理。

2. **提升 AI 输出质量**
   通过质量审核、问题标注、多维评分和结果采用机制，避免未经审核的 AI 内容直接进入课程报告、竞赛材料或科研文档。

3. **增强使用过程可追溯性**
   系统记录模型、提示词、输入内容、输出内容、调用时间、调用成本、审核意见和版本变化，便于后期复盘与说明。

4. **实现多模型效果比较**
   同一任务可调用多个模型，系统保存不同模型结果，并支持评分对比，为团队选择合适模型提供依据。

5. **体现数据库课程设计价值**
   系统涉及用户、角色、项目、成员、任务、模型、提示词、调用记录、审核记录、版本记录、统计分析等多类数据对象，适合进行规范化数据库设计、嵌入式 SQL 实现和图形化系统开发。

---

# 二、项目名称与定位

## 2.1 项目名称

建议项目名称：

**智研协作：面向高校项目协作的 AI 任务生成与质量审计管理系统**

英文简称可使用：

**AI-Collab Audit System**

## 2.2 项目定位

本系统定位为：

> 面向高校课程项目、科研训练、创新创业竞赛和团队文档协作场景的人机协同项目内容管理平台。系统通过项目空间、Git 式版本管理、提示词模板、多模型调用、人工编辑、质量审核和统计分析，实现项目内容从 AI 辅助生成、人工修改、负责人审核到教师指导确认的全过程管理。

需要特别说明的是，本系统不是“纯 AI 自动生成平台”。AI 在系统中承担的是辅助生成、启发构思、初稿补全、文本润色和多模型对比等作用；项目成员、项目负责人和指导教师仍然是项目内容的主要责任主体。系统强调“AI 生成 + 人工修改 + 审核确认 + 版本追踪”的协同机制，而不是让 AI 直接替代人的判断和创作。

## 2.3 系统边界

本项目不是以下系统：

1. 不是普通聊天机器人；
2. 不是纯 AI 自动写作平台；
3. 不是 API Key 转卖或分发平台；
4. 不是完整的企业级 AI 工作流平台；
5. 不是用于训练大模型的平台；
6. 不是面向全社会开放的商业 SaaS 平台。

本项目重点实现以下能力：

1. 项目空间管理；
2. Git 式任务版本管理；
3. 提示词模板管理；
4. 多模型调用记录管理；
5. AI 输出质量审核；
6. 人工修改、批注与版本保存；
7. 成果采用与归档；
8. 调用日志、成本、模型效果统计；
9. 多角色权限控制；
10. 基于关系型数据库的增删改查、事务、视图、触发器与存储过程设计。

## 2.4 参考项目调研与可借鉴内容

为了避免项目设计停留在概念层面，本系统在方案设计阶段参考了若干成熟开源项目。参考的目的不是复制其代码或复刻其完整功能，而是提炼其中适合课程设计落地的功能结构、数据库对象、交互方式和页面风格。由于本课程设计以数据库管理系统为核心，因此借鉴重点应放在“业务对象如何建模、调用记录如何管理、用户权限如何控制、界面如何展示数据”上。

### 2.4.1 LiteLLM

项目链接：

[https://github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)

项目类型：

多模型统一调用网关 / AI Gateway。

核心特点：

1. 使用统一接口调用多家大模型供应商；
2. 支持 OpenAI 兼容格式；
3. 支持虚拟 Key、成本追踪、Guardrails、负载均衡和管理面板；
4. 适合解决多供应商 API 调用不统一的问题。

本系统可借鉴内容：

1. 统一模型适配器思想：设计 `ModelAdapter`，将不同模型调用封装为统一接口；
2. 模型供应商表：`model_providers`；
3. 模型信息表：`ai_models`；
4. 调用记录表：`ai_invocations`；
5. 成本记录表：`cost_records`；
6. 模型状态管理：启用、停用、维护中；
7. 调用状态管理：成功、失败、超时、被安全规则拦截。

不建议照搬内容：

1. 不做完整企业级网关；
2. 不做复杂负载均衡；
3. 不做 API Key 二次分发业务；
4. 不追求支持上百个模型，课程阶段接入 1 个真实模型 + 2 到 3 个 Mock 模型即可。

### 2.4.2 One API

项目链接：

[https://github.com/songquanpeng/one-api](https://github.com/songquanpeng/one-api)

项目类型：

LLM API 管理与分发系统。

核心特点：

1. 支持多个主流模型渠道；
2. 支持渠道管理、用户分组、令牌管理、额度管理和用量统计；
3. 可将不同模型统一为类似 OpenAI API 的调用形式。

本系统可借鉴内容：

1. 渠道管理思想：模型供应商和具体模型分离；
2. 用户额度思想：可为用户设置调用次数或 Token 上限；
3. 用量统计思想：按用户、项目、模型、日期统计调用情况；
4. 调用日志管理：记录调用时间、模型、输入输出长度、状态和异常原因；
5. 管理后台结构：用户管理、模型管理、日志管理、系统设置。

不建议照搬内容：

1. 不做 Key 转售或二次分发；
2. 不把系统定位为 API 中转站；
3. 不引入充值、商业计费、代理分销等功能；
4. 报告中应强调“教学实验场景下的调用审计与项目管理”，避免被误解为商业 API 分发平台。

### 2.4.3 New API

项目链接：

[https://github.com/QuantumNous/new-api](https://github.com/QuantumNous/new-api)

项目类型：

统一 AI 模型聚合与分发平台。

核心特点：

1. 支持将多种模型转换成 OpenAI、Claude 或 Gemini 兼容格式；
2. 支持用户管理、Token 分组、模型限制、数据看板和后台管理；
3. 相比 One API，界面和管理功能更加现代化。

本系统可借鉴内容：

1. 首页数据看板设计；
2. 模型调用占比统计；
3. 用户调用排行；
4. 模型访问权限限制；
5. 用户组与项目组思想；
6. 管理员后台布局：侧边栏 + 数据卡片 + 表格 + 图表。

不建议照搬内容：

1. 不做商业化额度售卖；
2. 不做复杂倍率计费；
3. 不做完整模型聚合代理；
4. 仅保留适合数据库课程展示的统计和权限模块。

### 2.4.4 Dify

项目链接：

[https://github.com/langgenius/dify](https://github.com/langgenius/dify)

项目类型：

开源 LLM 应用开发平台。

核心特点：

1. 集成 AI Workflow、RAG、Agent、模型管理和可观测性；
2. 支持从原型快速构建到应用部署；
3. 强调提示词、工作流和应用发布。

本系统可借鉴内容：

1. 任务模板思想：摘要、翻译、报告润色、SQL 解释、项目申报书优化等；
2. 提示词模板管理：模板名称、适用任务、版本、启用状态、使用次数；
3. 工作流思想：任务创建 → 模型生成 → 结果保存 → 审核 → 成果归档；
4. 模型管理页面：供应商、模型名称、能力标签、状态；
5. 应用开发平台的页面组织方式。

不建议照搬内容：

1. 不做完整 Agent 平台；
2. 不做复杂 RAG 知识库；
3. 不做可视化工作流编排器；
4. 课程阶段只实现“任务模板 + 提示词版本 + 输出审核”的轻量版本。

### 2.4.5 Langfuse

项目链接：

[https://github.com/langfuse/langfuse](https://github.com/langfuse/langfuse)

项目类型：

LLM 工程平台 / 可观测性与评测平台。

核心特点：

1. 支持 LLM 调用链路追踪；
2. 支持 Prompt 管理；
3. 支持评测、实验、数据集和调试；
4. 适合团队协作改进 LLM 应用质量。

本系统可借鉴内容：

1. 调用审计思想：每次调用都应保存输入、输出、模型、耗时、Token 和状态；
2. Prompt 版本管理：提示词不是静态文本，而是可以迭代的版本对象；
3. 输出质量评测：准确性、完整性、逻辑性、规范性、可用性、风险性；
4. 人工反馈记录：审核人、评分、问题标签、修改意见；
5. 模型效果分析：按任务类型统计不同模型平均分。

不建议照搬内容：

1. 不做完整 trace 链路系统；
2. 不做复杂实验平台；
3. 不做在线自动评测集；
4. 以数据库课程所需的审核记录、评分统计和日志查询为主。

### 2.4.6 Helicone

项目链接：

[https://github.com/Helicone/helicone](https://github.com/Helicone/helicone)

项目类型：

AI Gateway 与 LLM 可观测性平台。

核心特点：

1. 支持通过统一网关访问多个模型；
2. 支持请求日志、成本跟踪、延迟分析、Prompt 管理和自动 fallback；
3. 强调模型调用的成本、性能和可靠性监控。

本系统可借鉴内容：

1. 成本统计：按用户、项目、模型统计 Token 和估算费用；
2. 延迟统计：保存响应耗时，计算平均响应时间；
3. 错误分析：记录失败原因、超时原因和异常模型；
4. fallback 思想：模型 A 失败后可切换到备用模型 B；
5. 调用日志筛选：按项目、模型、状态、时间范围查询。

不建议照搬内容：

1. 不做生产级网关；
2. 不做复杂缓存策略；
3. 不做企业合规认证；
4. fallback 可以作为选做功能，不作为课程设计必需功能。

### 2.4.7 Open WebUI

项目链接：

[https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)

项目文档：

[https://docs.openwebui.com/](https://docs.openwebui.com/)

项目类型：

自托管 AI WebUI / 多模型聊天界面。

核心特点：

1. 支持 Ollama 和 OpenAI 兼容 API；
2. 支持本地模型与云模型；
3. 支持多用户、角色权限、模型访问控制；
4. 技术结构上采用 SvelteKit 前端和 Python/FastAPI 后端并行开发。

本系统可借鉴内容：

1. 多用户登录与权限控制；
2. 模型选择器；
3. 左侧导航与会话 / 任务列表；
4. Markdown 渲染、代码块展示、流式输出体验；
5. 模型访问权限控制；
6. 本地优先、可自部署的系统定位；
7. FastAPI 后端结构思想。

不建议照搬内容：

1. 不直接复制其 SvelteKit 前端源码；
2. 不把本系统做成纯聊天系统；
3. 不照搬其品牌、图标和专有视觉资产；
4. 使用其设计思想时，应改造成“项目任务详情页”和“审核中心”，而不是普通聊天会话页。

### 2.4.8 LobeChat

项目链接：

[https://github.com/lobehub/lobe-chat](https://github.com/lobehub/lobe-chat)

项目文档：

[https://lobehub.com/docs](https://lobehub.com/docs)

项目类型：

现代化多模型 AI 聊天框架。

核心特点：

1. 界面现代、交互精致，适合作为前端审美参考；
2. 支持多个模型供应商；
3. 支持多模态、语音、插件和知识库等能力；
4. 技术栈主要为 Next.js + React + Ant Design / Lobe UI + Zustand + SWR。

本系统可借鉴内容：

1. 现代化界面风格：圆角卡片、清爽留白、模型头像、状态标签；
2. 模型选择与模型能力标签展示；
3. 任务 / 会话列表布局；
4. 右侧参数设置抽屉；
5. Markdown 结果展示；
6. 响应式页面布局；
7. Prompt 模板卡片与模型卡片设计。

不建议照搬内容：

1. 不直接迁移 React / Next.js 源码；
2. 不复制其 UI 组件库代码；
3. 不复制品牌、Logo、图标和默认主题；
4. 不做完整聊天框架，而是借鉴其视觉设计并服务于本系统的项目任务流程。

## 2.5 借鉴边界与合规说明

本项目在产品设计层面参考了 LiteLLM、One API、New API、Dify、Langfuse、Helicone、Open WebUI、LobeChat 等成熟开源项目的功能思想、交互结构、页面组织方式和数据管理思路；在前端工程实现层面，基于 V3 Admin Vite 这一成熟 Vue3 开源后台模板进行二次开发。

需要明确的是，本项目并不是对上述 AI 平台的简单复制，也不是对 LobeChat 或 Open WebUI 源码的迁移。本项目的核心业务仍然围绕高校项目协作、AI 任务生成、版本管理、质量审核、成果采用和数据库管理展开。参考项目主要用于帮助确定产品形态、交互结构、后台布局和可观测性设计。

前端模板使用遵守以下原则：

1. 保留 V3 Admin Vite 的 LICENSE、NOTICE 与来源说明；
2. 在 frontend/README.md 或 NOTICE.md 中标明原项目名称、GitHub 链接和许可证；
3. 不使用原模板 Logo、品牌名和无关业务页面；
4. 不将模板包装成完全原创项目；
5. 删除或禁用模板自带 Mock API、Mock 数据和演示页面；
6. 将系统名称、菜单、路由、登录接口和页面内容替换为本项目内容；
7. 不复制 LobeChat / Open WebUI 的 React、Next.js、SvelteKit 源码；
8. 前端模板只作为后台基础工程和 UI 底座，核心业务、数据库设计、接口逻辑和页面内容由本项目自主设计实现。

因此，本项目的合规边界可以概括为：

- 对 LobeChat / Open WebUI：只参考界面审美和交互方式，不迁移源码；
- 对 V3 Admin Vite：在遵守 MIT License 的前提下，基于其开源模板代码进行二次开发；
- 对本项目业务：系统品牌、菜单、接口、权限、数据库和业务页面均围绕"智研协作 AI 项目质量审计系统"重新设计。


## 2.6 基于 Vue3 开源后台模板的前端实现方案

### 2.6.1 基本结论

LobeChat 和 Open WebUI 在 AI 产品体验方面具有较高参考价值，尤其是现代化布局、模型选择、任务列表、内容展示和权限管理等交互方式。但二者的技术栈分别偏向 React / Next.js 和 SvelteKit，并不适合直接迁移到本项目的 Vue3 技术路线中。

因此，本项目采用更稳妥的实现方式：以 V3 Admin Vite 作为 Vue3 前端模板底座，在其成熟的后台管理工程结构基础上进行裁剪和二次开发。系统保留模板的基础布局、路由、状态管理、菜单结构和样式体系，同时替换为本项目的系统品牌、登录接口、业务菜单和占位页面。

### 2.6.2 前端模板方案

| 内容 | 实际方案 |
|---|---|
| 前端基础模板 | V3 Admin Vite |
| 原项目链接 | https://github.com/un-pany/v3-admin-vite |
| 许可证 | MIT License |
| 技术栈 | Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router |
| 使用方式 | 保留基础布局、路由、菜单、状态管理和样式体系，删除无关示例页面 |
| 品牌替换 | 替换为"智研协作 AI 项目质量审计系统" |
| 接口替换 | 模板 Mock API 替换为本项目 FastAPI 后端接口 |
| 合规方式 | 保留 LICENSE / NOTICE / 来源说明 |
| 不使用内容 | 不使用原模板 Logo、Mock 数据、无关业务页面；不复制 LobeChat / Open WebUI 源码 |

### 2.6.3 选择 V3 Admin Vite 的原因

选择 V3 Admin Vite 作为前端基础模板，主要基于以下考虑：

1. 技术栈与本项目一致，均基于 Vue3、Vite、Element Plus、Pinia 和 Vue Router；
2. 后台管理布局成熟，适合项目管理、任务管理、审核中心、成果库和统计看板等页面；
3. 工程结构完整，便于后续继续扩展业务页面；
4. 相比直接迁移 LobeChat / Open WebUI 源码，技术风险更低；
5. 保留开源许可证和来源说明后，能够满足课程项目的合规要求；
6. 页面视觉效果更成熟，有利于课程答辩截图和系统展示。

### 2.6.4 与 LobeChat / Open WebUI 的关系

LobeChat 和 Open WebUI 仍然作为本系统的 AI 产品体验参考对象，但本项目不直接复用其源码。具体来说：

1. 参考 LobeChat 的现代化 AI 产品审美、圆角卡片、任务内容展示和模型标签风格；
2. 参考 Open WebUI 的简洁登录体验、多用户管理和模型访问控制思想；
3. 不迁移 LobeChat 的 React / Next.js 组件；
4. 不迁移 Open WebUI 的 SvelteKit 前端源码；
5. 不使用二者 Logo、品牌素材或默认视觉资产；
6. 结合本项目业务，将相关设计思想改造为项目任务、输出版本、审核中心和成果库页面。

### 2.6.5 最终判断

基于 V3 Admin Vite 进行前端二次开发，比完全从零手写前端页面更适合本课程项目。该方式既能获得成熟后台系统的界面质感和工程结构，又能通过菜单、接口、权限、页面内容和业务流程改造，体现本项目自身的数据库设计和业务创新。

因此，前端实现策略不是"复刻 LobeChat / Open WebUI 源码"，也不是完全手写普通后台页面，而是：

> 基于 V3 Admin Vite 开源 Vue3 后台模板二次开发，参考成熟 AI 平台的视觉与交互风格，服务于本项目的 AI 项目协作质量审计业务。

---


## 2.7 人机协同内容生产机制

为了避免系统被误解为“AI 自动代写平台”，本项目将内容生产过程明确设计为人机协同模式。系统中所有项目内容均可以存在三类来源：

1. **AI 生成内容**：由模型根据任务背景、提示词模板和输入材料生成的初稿；
2. **人工编辑内容**：由项目成员、项目负责人或指导教师直接撰写、修改或补充的内容；
3. **混合协同内容**：先由 AI 生成初稿，再经过人工修改、审核和确认后形成的版本。

在该机制下，AI 输出不会自动进入最终成果库，必须经过人工修改或审核确认后才能被采用。系统保留每一次生成、编辑、审核、退回、采用和回滚记录，使项目成果既能体现 AI 辅助效率，又能体现人的判断、修改和责任。

### 2.7.1 不同角色的人工参与方式

| 角色            | 人工参与方式                      | 作用           |
| ------------- | --------------------------- | ------------ |
| 学生项目成员        | 新建人工版本、修改 AI 初稿、补充背景材料、提交审核 | 完成具体任务内容生产   |
| 项目负责人 / 质量审核员 | 对成员提交内容进行修改、批注、退回、采用或合并     | 控制项目成果质量     |
| 指导教师          | 查看成果版本、添加指导意见、批注关键问题、确认重要成果 | 提供方向性指导与质量把关 |
| 系统管理员         | 不参与内容创作，仅维护用户、模型、模板、权限和日志   | 保障系统运行与数据安全  |

### 2.7.2 人工编辑与版本记录

系统应支持以下人工编辑功能：

1. 项目成员可以基于 AI 输出创建人工修改版；
2. 项目成员可以完全不调用 AI，直接创建人工内容版本；
3. 项目负责人可以对成员提交的内容进行二次修改；
4. 指导教师可以对关键成果添加批注和指导意见；
5. 每次人工修改均形成新的输出版本；
6. 每个版本记录来源类型，包括 AI生成、人工编辑、AI+人工混合；
7. 系统记录修改人、修改时间、修改说明和父版本；
8. 审核通过的版本才能进入项目成果库。

### 2.7.3 推荐新增或强化的数据字段

在人机协同机制下，`task_outputs` 输出版本表需要重点保留以下字段：

| 字段名                | 含义                  |
| ------------------ | ------------------- |
| source_type        | 内容来源：AI生成、人工编辑、混合修改 |
| parent_output_id   | 父版本，用于追踪版本来源        |
| editor_id          | 最近编辑人               |
| edit_summary       | 修改说明                |
| content            | 当前版本内容              |
| created_at         | 版本创建时间              |
| is_final_candidate | 是否作为候选最终成果          |

可选新增 `output_comments` 批注表，用于保存负责人和指导教师对内容的逐段批注意见：

| 字段名          | 含义                   |
| ------------ | -------------------- |
| comment_id   | 批注编号                 |
| output_id    | 被批注的输出版本             |
| commenter_id | 批注人                  |
| comment_type | 批注类型，如修改建议、事实问题、格式问题 |
| comment_text | 批注内容                 |
| status       | 未处理、已处理、已关闭          |
| created_at   | 批注时间                 |

### 2.7.4 人机协同业务流程

典型流程如下：

1. 项目成员创建任务；
2. 成员可以选择 AI 生成初稿，也可以直接人工撰写；
3. 如果使用 AI，系统保存模型输出为 AI 生成版本；
4. 成员基于 AI 版本进行人工修改，形成混合版本；
5. 成员填写修改说明并提交审核；
6. 项目负责人审核内容，可直接修改、批注、退回或采用；
7. 指导教师可对重要成果添加指导意见；
8. 审核通过后，版本进入项目成果库；
9. 系统保留完整版本链路，支持查看每个成果从 AI 初稿到人工确认的演进过程。

该设计使系统从“AI 生成工具”升级为“人机协同项目成果管理平台”，更符合高校项目真实工作方式，也更容易体现系统的教育价值和管理价值。

# 三、核心创新：基于 Git 思想的 AI 项目管理机制

## 3.1 为什么引入 Git 思想

Git 是软件开发中非常成熟的版本控制方案，具有分支、提交、合并、回滚、审查和版本追踪等核心机制。高校项目协作中的文档、报告、代码说明和 AI 生成内容同样存在版本管理问题。因此，本系统借鉴 Git 的管理思想，将 AI 生成内容纳入类似“分支—提交—审核—合并”的流程。

## 3.2 Git 思想与本系统业务对象映射

| Git 概念                       | 本系统对应对象                 | 说明                           |
| ---------------------------- | ----------------------- | ---------------------------- |
| Repository 仓库                | Project 项目空间            | 一个课程项目、竞赛项目或科研项目对应一个项目空间     |
| Branch 分支                    | Task Branch 任务分支        | 每个具体任务可以从项目主线派生出任务分支         |
| Issue 问题/任务                  | Project Task 项目任务       | 项目成员需要完成的 AI 辅助任务            |
| Commit 提交                    | Output Version 输出版本     | 每次 AI 生成、人工撰写、人工修改或人工合并都形成一个结果版本 |
| Pull Request / Merge Request | Review Request 审核请求     | 成员将结果提交给负责人审核                |
| Code Review                  | Output Review 质量审核      | 审核员对 AI 输出进行评分、标注和反馈         |
| Merge 合并                     | Adopt Output 采用结果       | 审核通过后，将结果合并到项目成果库            |
| Tag / Release                | Project Artifact 项目成果版本 | 形成阶段性成果，如需求分析 v1.0、报告初稿 v2.0 |
| Revert 回滚                    | Version Rollback 版本回退   | 如果采用结果存在问题，可回退到历史版本          |
| Commit Log                   | Operation Log 操作日志      | 保存成员操作、生成、审核、合并等记录           |

## 3.3 Git 式业务流程

本系统的核心业务流程如下：

1. 项目负责人创建项目空间；
2. 邀请项目成员加入项目；
3. 项目负责人创建任务，例如“生成数据库需求分析初稿”；
4. 系统为该任务创建任务分支；
5. 项目成员可以选择任务模板和模型执行 AI 生成，也可以直接创建人工内容版本；
6. 每一次 AI 生成、人工撰写、人工修改或人工合并都作为一个输出版本保存；
7. 成员可以在多个模型输出之间比较，也可以基于其中一个输出继续人工修改；
8. 成员选择较优版本或人工修改版提交审核；
9. 质量审核员或项目负责人进行审核，可批注、退回、修改或采用；
10. 指导教师可对重要版本添加指导意见；
11. 审核通过后，该结果被合并到项目成果库；
12. 审核不通过时，结果被退回修改，成员可重新生成或继续人工修改；
13. 项目结束时，可导出成果版本、调用记录、人工修改记录和审核记录。

## 3.4 实现策略

为了控制课程项目开发难度，本系统不强制依赖真实 Git 命令，也不要求部署 GitLab 或 Gitea。系统内部通过关系型数据库模拟 Git 的核心思想，包括分支表、版本表、审核表和采用结果表。

可选增强方案：

1. 支持导出 Markdown 文件；
2. 支持将最终成果保存为本地文件；
3. 后续可扩展为真实 Git 仓库同步，但课程设计阶段不作为必做项。

---

# 四、用户角色与使用价值

## 4.1 角色设计总览

系统设计四类核心角色：

| 角色            | 说明                   | 核心价值                 |
| ------------- | -------------------- | -------------------- |
| 学生项目成员        | 课程项目、科研项目、竞赛团队中的普通成员 | 使用 AI 完成具体任务，并沉淀任务成果 |
| 项目负责人 / 质量审核员 | 负责项目管理和结果把关的成员       | 审核 AI 输出质量，决定是否采用    |
| 指导教师          | 对项目过程进行指导和监督         | 查看项目进展、AI 使用记录和成果质量  |
| 系统管理员         | 维护平台、模型、用户、模板和日志     | 保障系统安全、成本可控和数据规范     |

## 4.2 学生项目成员的使用价值

学生项目成员使用本系统的原因不是“聊天”，而是为了更高效地完成项目任务。

学生项目成员的痛点包括：

1. 不知道如何编写高质量提示词；
2. 不知道哪个模型适合当前任务；
3. AI 输出结果容易散落在不同平台；
4. 生成结果反复修改后缺少版本记录；
5. 团队成员之间难以共享 AI 生成过程；
6. 项目负责人无法知道某段内容的生成来源和修改过程。

系统为学生项目成员提供：

1. 项目空间统一归档；
2. 任务模板和提示词模板；
3. 多模型结果生成；
4. 输出版本保存；
5. 结果提交审核；
6. 历史版本查看；
7. 被采用成果查看；
8. 个人任务完成情况统计。

## 4.3 项目负责人 / 质量审核员的使用价值

项目负责人或质量审核员不是为了“随便打分”，而是为了控制项目材料质量。

其主要痛点包括：

1. 团队成员提交的 AI 内容质量不稳定；
2. AI 生成内容可能空泛、错误或不符合格式；
3. 无法判断某个结果是否可以进入最终报告；
4. 多模型结果难以比较；
5. 项目成果缺少清晰的采用记录。

系统为项目负责人 / 质量审核员提供：

1. 待审核任务列表；
2. 输出内容多维评分；
3. 错误类型标注；
4. 修改意见填写；
5. 采用、退回、需修改等状态流转；
6. 多模型输出对比；
7. 项目成果库管理；
8. 团队成员贡献统计。

## 4.4 指导教师的使用价值

指导教师使用系统的目的不是管理具体 API，而是了解学生团队的项目推进过程和 AI 使用规范性。

系统为指导教师提供：

1. 查看项目任务列表；
2. 查看项目成果版本；
3. 查看 AI 使用记录；
4. 查看审核意见和采用记录；
5. 对关键任务给出指导意见；
6. 了解团队成员分工与贡献。

## 4.5 系统管理员的使用价值

系统管理员负责平台基础数据和安全管理。

系统管理员可完成：

1. 用户管理；
2. 角色权限管理；
3. 模型供应商管理；
4. 模型信息维护；
5. API 配置维护；
6. 提示词模板维护；
7. 调用额度管理；
8. 调用日志审计；
9. 成本统计；
10. 异常操作处理。

---

# 五、系统总体功能设计

## 5.1 功能模块总览

系统功能分为九个模块：

1. 用户登录与权限管理模块；
2. 项目空间管理模块；
3. Git 式任务与版本管理模块；
4. AI 任务生成模块；
5. 提示词模板管理模块；
6. 多模型管理与调用日志模块；
7. 输出质量审核模块；
8. 项目成果库模块；
9. 数据统计与可视化模块。

## 5.2 用户登录与权限管理模块

功能包括：

1. 用户登录（POST /api/auth/login）；
2. 用户信息查询（GET /api/auth/me）；
3. 退出登录（POST /api/auth/logout）；
4. 密码哈希存储（bcrypt）；
5. 角色分配；
6. 权限控制；
7. 登录日志记录；
8. 用户状态管理。

> 注：本系统不开放用户自主注册功能，由系统管理员分配账号。

角色权限示例：

| 功能   | 学生项目成员 | 项目负责人 | 指导教师   | 系统管理员 |
| ---- | ------ | ----- | ------ | ----- |
| 创建项目 | 可选     | 是     | 否      | 是     |
| 加入项目 | 是      | 是     | 是      | 是     |
| 创建任务 | 是      | 是     | 可选     | 是     |
| 调用模型 | 是      | 是     | 可选     | 是     |
| 提交审核 | 是      | 是     | 否      | 是     |
| 审核结果 | 否      | 是     | 是      | 是     |
| 管理模型 | 否      | 否     | 否      | 是     |
| 管理模板 | 否      | 可选    | 可选     | 是     |
| 查看统计 | 查看个人   | 查看项目  | 查看指导项目 | 查看全部  |

## 5.3 项目空间管理模块

项目空间是系统的核心组织单位。一个项目空间可以对应：

1. 一门课程的结课设计；
2. 一个大创 / 国创项目；
3. 一个数学建模竞赛项目；
4. 一个科研论文阅读项目；
5. 一个实验报告或软件开发项目。

功能包括：

1. 创建项目；
2. 修改项目信息；
3. 设置项目类型；
4. 设置项目负责人；
5. 邀请成员；
6. 设置成员角色；
7. 查看项目任务；
8. 查看项目成果；
9. 项目归档。

## 5.4 Git 式任务与版本管理模块

该模块体现系统主要创新。

功能包括：

1. 创建项目任务；
2. 为任务生成任务分支；
3. 保存每一次 AI 输出版本；
4. 保存人工修改版本；
5. 查看版本差异摘要；
6. 提交审核请求；
7. 审核通过后合并到成果库；
8. 支持历史版本回退；
9. 保存版本操作日志。

任务状态设计：

| 状态                | 含义    |
| ----------------- | ----- |
| draft             | 草稿    |
| running           | 生成中   |
| generated         | 已生成   |
| submitted         | 已提交审核 |
| approved          | 审核通过  |
| rejected          | 审核拒绝  |
| revision_required | 需修改   |
| adopted           | 已采用   |
| archived          | 已归档   |

## 5.5 AI 任务生成模块

功能包括：

1. 选择项目；
2. 选择任务类型；
3. 选择提示词模板；
4. 输入任务背景；
5. 选择一个或多个模型；
6. 调用模型生成结果；
7. 保存输入、输出、模型、时间、状态；
8. 记录调用 Token、耗时和估算成本；
9. 失败时记录异常信息；
10. 可选：失败后调用备用模型。

任务类型示例：

| 任务类型     | 使用场景           |
| -------- | -------------- |
| 需求分析生成   | 数据库课程报告、软件项目文档 |
| 数据库表设计建议 | 数据库课程设计        |
| SQL 代码解释 | 数据库学习与调试       |
| 论文摘要润色   | 科研论文与课程论文      |
| 文献内容总结   | 文献阅读           |
| PPT 文案优化 | 创新创业竞赛         |
| 项目申报书修改  | 大创 / 国创项目      |
| 实验报告总结   | 课程实验           |
| 代码注释生成   | 程序设计项目         |

## 5.6 提示词模板管理模块

提示词模板是系统区别于普通聊天工具的重要部分。

功能包括：

1. 新增提示词模板；
2. 修改模板内容；
3. 设置模板适用任务类型；
4. 设置模板版本号；
5. 启用 / 停用模板；
6. 查看模板使用次数；
7. 查看模板平均评分；
8. 复制模板生成新版本。

模板字段包括：

1. 模板名称；
2. 模板类型；
3. 模板内容；
4. 适用场景；
5. 创建人；
6. 当前版本；
7. 是否启用；
8. 创建时间；
9. 更新时间。

## 5.7 多模型管理与调用日志模块

功能包括：

1. 维护模型供应商；
2. 维护模型名称；
3. 维护模型能力标签；
4. 维护模型状态；
5. 配置 API 信息；
6. 保存调用日志；
7. 查看模型调用次数；
8. 查看调用成功率；
9. 查看平均响应时间；
10. 查看估算调用成本。

模型能力标签示例：

1. 中文写作；
2. 代码能力；
3. 长文本处理；
4. 逻辑推理；
5. 文献总结；
6. 数据分析；
7. PPT 文案；
8. SQL 生成。

## 5.8 输出质量审核模块

功能包括：

1. 查看待审核输出；
2. 查看任务背景；
3. 查看模型输出结果；
4. 查看提示词和模型信息；
5. 多维度评分；
6. 标注错误类型；
7. 填写审核意见；
8. 通过、退回、需修改；
9. 审核记录留痕；
10. 生成模型质量统计。

评分维度建议：

| 维度  | 说明               |
| --- | ---------------- |
| 准确性 | 是否存在事实错误或逻辑错误    |
| 完整性 | 是否覆盖任务要求         |
| 逻辑性 | 结构是否清晰，推理是否连贯    |
| 规范性 | 是否符合课程报告、论文或材料格式 |
| 可用性 | 是否可以进入最终项目成果     |
| 风险性 | 是否存在幻觉、敏感信息或不当内容 |

错误类型标签示例：

1. 内容空泛；
2. 事实错误；
3. 逻辑混乱；
4. 格式不规范；
5. 任务偏离；
6. 重复啰嗦；
7. 缺少依据；
8. 风险内容；
9. SQL 错误；
10. 代码不可运行。

## 5.9 项目成果库模块

项目成果库保存审核通过并被采用的结果。

功能包括：

1. 查看已采用内容；
2. 按项目、任务类型、版本查看成果；
3. 设置成果版本号；
4. 导出 Markdown / Word 文本内容；
5. 查看成果来源；
6. 查看采用前的审核记录；
7. 回滚到历史版本；
8. 归档项目成果。

## 5.10 数据统计与可视化模块

首页仪表盘可展示：

1. 项目总数；
2. 任务总数；
3. 今日 AI 调用次数；
4. 调用成功率；
5. 平均响应时间；
6. Token 消耗量；
7. 估算调用成本；
8. 待审核任务数；
9. 不同模型调用占比；
10. 不同任务类型分布；
11. 模型平均评分排行；
12. 成员任务贡献排行；
13. 项目成果版本数量。

---

# 六、数据库设计方案

## 6.1 数据库设计原则

数据库设计遵循以下原则：

1. 满足第三范式，减少数据冗余；
2. 每张表设置主键；
3. 重要关联字段设置外键；
4. 关键字段设置非空约束；
5. 用户名、角色名、模型名称等设置唯一约束；
6. 状态字段采用枚举值或检查约束；
7. 金额、Token 数、评分等字段设置合理数据类型；
8. 涉及多表变更的操作使用事务；
9. 保留创建时间、更新时间、创建人等审计字段；
10. 对高频查询字段建立索引；
11. 对核心业务数据采用软删除机制，避免物理删除破坏历史追踪链路；
12. 对多人协作编辑场景采用乐观锁机制，避免并发覆盖。

## 6.1.1 软删除与审计字段设计

由于本系统定位为“质量审计”和“全过程可追溯”的人机协同项目内容管理系统，核心业务数据不宜直接执行物理删除。项目、任务、输出版本、审核记录、调用日志等数据之间存在复杂外键关联，如果随意物理删除，可能导致历史调用记录、版本链路、审核记录和成果追踪信息丢失。

因此，系统采用软删除机制。对于核心业务表，统一增加如下审计字段：

| 字段名 | 类型 | 说明 |
|---|---|---|
| is_deleted | bit / tinyint | 是否删除，0 表示未删除，1 表示已删除 |
| deleted_at | datetime | 删除时间 |
| deleted_by | int | 删除人，外键关联 users |
| created_at | datetime | 创建时间 |
| created_by | int | 创建人，外键关联 users |
| updated_at | datetime | 更新时间 |
| updated_by | int | 更新人，外键关联 users |

系统删除项目、任务、输出版本等核心数据时，不直接执行 `DELETE`，而是执行逻辑更新。

MySQL 示例：

```sql
UPDATE project_tasks
SET 
    is_deleted = 1,
    deleted_at = NOW(),
    deleted_by = ?
WHERE task_id = ?;
```

SQL Server 示例：

```sql
UPDATE project_tasks
SET 
    is_deleted = 1,
    deleted_at = GETDATE(),
    deleted_by = @user_id
WHERE task_id = @task_id;
```

常规查询时统一过滤已删除数据：

```sql
SELECT *
FROM project_tasks
WHERE is_deleted = 0;
```

对于 `operation_logs`、`login_logs`、`ai_invocations`、`cost_records` 等审计型数据，原则上不允许普通用户删除；即使管理员执行清理，也应采用归档策略而非直接删除。该设计能够有效避免由于物理删除导致的外键约束错误和历史追踪链路断裂，符合系统“全过程记录、可追溯、可审计”的设计目标。

## 6.2 核心实体

系统核心实体包括：

1. 用户；
2. 角色；
3. 权限；
4. 项目；
5. 项目成员；
6. 任务；
7. 任务分支；
8. 任务类型；
9. 提示词模板；
10. 提示词版本；
11. 模型供应商；
12. AI 模型；
13. API 配置；
14. 模型调用记录；
15. 任务输出版本；
16. 审核请求；
17. 审核记录；
18. 问题标签；
19. 输出问题关联；
20. 输出批注；
21. 采用成果；
22. 合并记录；
23. 成本记录；
24. 操作日志；
25. 登录日志。

## 6.3 建议数据表清单

| 序号 | 表名 | 中文含义 | 主要作用 |
|---|---|---|---|
| 1 | users | 用户表 | 保存系统用户基础信息 |
| 2 | roles | 角色表 | 保存角色名称与说明 |
| 3 | user_roles | 用户角色关联表 | 实现用户与角色的多对多关系 |
| 4 | permissions | 权限表 | 保存系统功能权限 |
| 5 | role_permissions | 角色权限关联表 | 分配角色权限 |
| 6 | projects | 项目空间表 | 保存课程项目、竞赛项目、科研项目等 |
| 7 | project_members | 项目成员表 | 保存项目成员与项目内角色 |
| 8 | project_tasks | 项目任务表 | 保存具体 AI 辅助任务和人工任务 |
| 9 | task_branches | 任务分支表 | 模拟 Git 分支机制 |
| 10 | task_types | 任务类型表 | 保存任务分类 |
| 11 | prompt_templates | 提示词模板表 | 保存模板基础信息 |
| 12 | prompt_versions | 提示词版本表 | 保存模板版本内容 |
| 13 | model_providers | 模型供应商表 | 保存供应商信息 |
| 14 | ai_models | AI 模型表 | 保存模型名称、能力、状态和计费信息 |
| 15 | api_configs | API 配置表 | 保存加密后的 API 配置信息 |
| 16 | ai_invocations | AI 调用记录表 | 保存每次模型调用记录 |
| 17 | task_outputs | 任务输出版本表 | 保存 AI 生成、人工编辑和混合修改结果 |
| 18 | review_requests | 审核请求表 | 保存提交审核记录 |
| 19 | output_reviews | 输出审核表 | 保存评分和审核意见 |
| 20 | issue_tags | 问题标签表 | 保存错误类型标签 |
| 21 | output_issue_relations | 输出问题关联表 | 保存输出与问题标签关系 |
| 22 | output_comments | 输出批注表 | 保存负责人和指导教师批注意见 |
| 23 | merge_records | 分支合并记录表 | 保存分支冲突处理和人工合并记录 |
| 24 | adopted_outputs | 采用成果表 | 保存审核通过并采用的内容 |
| 25 | cost_records | 成本记录表 | 保存调用成本与用量 |
| 26 | operation_logs | 操作日志表 | 保存用户关键操作日志 |
| 27 | login_logs | 登录日志表 | 保存登录记录 |

## 6.4 关键表结构说明

### 6.4.1 users 用户表

`users` 表用于保存系统用户基础信息，包括学生项目成员、项目负责人、指导教师和系统管理员。

| 字段名 | 类型 | 说明 |
|---|---|---|
| user_id | int | 主键，自增 |
| username | varchar | 用户名，唯一 |
| password_hash | varchar | 密码哈希 |
| real_name | varchar | 真实姓名 |
| student_no | varchar | 学号，可为空 |
| email | varchar | 邮箱 |
| phone | varchar | 手机号 |
| status | varchar | 正常、禁用 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| created_by | int | 创建人 |
| updated_at | datetime | 更新时间 |
| updated_by | int | 更新人 |
| deleted_at | datetime | 删除时间 |
| deleted_by | int | 删除人 |

### 6.4.2 roles 角色表

`roles` 表用于保存系统角色信息。

| 字段名 | 类型 | 说明 |
|---|---|---|
| role_id | int | 主键 |
| role_name | varchar | 角色名称，唯一 |
| role_code | varchar | 角色编码，如 student、leader、teacher、admin |
| description | text | 角色说明 |
| status | varchar | 启用、停用 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 6.4.3 user_roles 用户角色关联表

`user_roles` 表用于实现用户与角色之间的多对多关系。

| 字段名 | 类型 | 说明 |
|---|---|---|
| user_role_id | int | 主键 |
| user_id | int | 用户 ID，外键关联 users |
| role_id | int | 角色 ID，外键关联 roles |
| assigned_by | int | 分配人 |
| assigned_at | datetime | 分配时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.4 permissions 权限表

`permissions` 表用于保存系统功能权限。

| 字段名 | 类型 | 说明 |
|---|---|---|
| permission_id | int | 主键 |
| permission_name | varchar | 权限名称 |
| permission_code | varchar | 权限编码，如 project:create、task:review |
| module_name | varchar | 所属模块 |
| description | text | 权限说明 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |

### 6.4.5 role_permissions 角色权限关联表

`role_permissions` 表用于实现角色与权限之间的多对多关系。

| 字段名 | 类型 | 说明 |
|---|---|---|
| role_permission_id | int | 主键 |
| role_id | int | 角色 ID，外键关联 roles |
| permission_id | int | 权限 ID，外键关联 permissions |
| assigned_at | datetime | 分配时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.6 projects 项目空间表

`projects` 表是系统的核心业务表，用于保存课程项目、科研项目、竞赛项目等项目空间。

| 字段名 | 类型 | 说明 |
|---|---|---|
| project_id | int | 主键 |
| project_name | varchar | 项目名称 |
| project_type | varchar | 课程项目、科研项目、竞赛项目等 |
| description | text | 项目说明 |
| owner_id | int | 项目负责人，外键关联 users |
| status | varchar | draft、active、archived |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| created_by | int | 创建人 |
| updated_at | datetime | 更新时间 |
| updated_by | int | 更新人 |
| deleted_at | datetime | 删除时间 |
| deleted_by | int | 删除人 |

### 6.4.7 project_members 项目成员表

`project_members` 表用于保存项目空间中的成员关系和项目内角色。

| 字段名 | 类型 | 说明 |
|---|---|---|
| member_id | int | 主键 |
| project_id | int | 项目 ID，外键关联 projects |
| user_id | int | 用户 ID，外键关联 users |
| project_role | varchar | 项目角色，如 member、leader、reviewer、teacher |
| joined_at | datetime | 加入时间 |
| status | varchar | 正常、已退出、待确认 |
| contribution_score | decimal(5,2) | 贡献度评分，可选 |
| is_deleted | bit | 是否软删除 |

### 6.4.8 project_tasks 项目任务表

`project_tasks` 表用于保存具体任务，包括 AI 生成任务、人工撰写任务、审核任务等。

| 字段名 | 类型 | 说明 |
|---|---|---|
| task_id | int | 主键 |
| project_id | int | 所属项目 |
| task_type_id | int | 任务类型 |
| title | varchar | 任务标题 |
| description | text | 任务描述 |
| creator_id | int | 创建人 |
| assignee_id | int | 负责人 |
| status | varchar | draft、running、submitted、approved、adopted、archived 等 |
| priority | varchar | 优先级 |
| due_date | datetime | 截止时间 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| created_by | int | 创建人 |
| updated_at | datetime | 更新时间 |
| updated_by | int | 更新人 |
| deleted_at | datetime | 删除时间 |
| deleted_by | int | 删除人 |

### 6.4.9 task_branches 任务分支表

`task_branches` 表用于模拟 Git 分支机制。

| 字段名 | 类型 | 说明 |
|---|---|---|
| branch_id | int | 主键 |
| project_id | int | 所属项目 |
| task_id | int | 所属任务 |
| branch_name | varchar | 分支名称 |
| base_output_id | int | 基于哪个输出版本创建，可为空 |
| created_by | int | 创建人 |
| status | varchar | active、merged、closed |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |

### 6.4.10 task_types 任务类型表

`task_types` 表用于管理系统支持的任务类型。

| 字段名 | 类型 | 说明 |
|---|---|---|
| task_type_id | int | 主键 |
| type_name | varchar | 任务类型名称 |
| type_code | varchar | 类型编码 |
| description | text | 类型说明 |
| default_template_id | int | 默认提示词模板 |
| status | varchar | 启用、停用 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |

### 6.4.11 prompt_templates 提示词模板表

`prompt_templates` 表保存提示词模板基础信息。

| 字段名 | 类型 | 说明 |
|---|---|---|
| template_id | int | 主键 |
| template_name | varchar | 模板名称 |
| task_type_id | int | 适用任务类型 |
| description | text | 模板说明 |
| created_by | int | 创建人 |
| is_active | bit | 是否启用 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 6.4.12 prompt_versions 提示词版本表

`prompt_versions` 表保存模板版本内容，使提示词可以持续迭代。

| 字段名 | 类型 | 说明 |
|---|---|---|
| prompt_version_id | int | 主键 |
| template_id | int | 所属模板 |
| version_no | varchar | 版本号 |
| prompt_content | text / nvarchar(max) | 提示词内容 |
| change_note | text | 修改说明 |
| created_by | int | 创建人 |
| created_at | datetime | 创建时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.13 model_providers 模型供应商表

`model_providers` 表用于保存模型供应商信息。

| 字段名 | 类型 | 说明 |
|---|---|---|
| provider_id | int | 主键 |
| provider_name | varchar | 供应商名称，如 OpenAI、DeepSeek、通义千问 |
| provider_code | varchar | 供应商编码 |
| base_url | varchar | API 基础地址 |
| website | varchar | 官方网站 |
| description | text | 说明 |
| status | varchar | 启用、停用 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 6.4.14 ai_models 模型表

`ai_models` 表用于保存具体 AI 模型信息。为支撑成本统计，表中需保存输入单价、输出单价和计价单位。

| 字段名 | 类型 | 说明 |
|---|---|---|
| model_id | int | 主键 |
| provider_id | int | 所属供应商 |
| model_name | varchar | 模型名称 |
| display_name | varchar | 展示名称 |
| capability_tags | varchar | 能力标签 |
| max_context | int | 最大上下文长度 |
| input_price | decimal(10,6) | 输入 Token 单价 |
| output_price | decimal(10,6) | 输出 Token 单价 |
| price_unit | varchar | 计价单位，如 1K_TOKENS、1M_TOKENS |
| status | varchar | 启用、停用、维护中 |
| is_deleted | bit | 是否软删除 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

成本估算公式如下：

```text
estimated_cost =
(input_tokens / price_base) * input_price
+
(output_tokens / price_base) * output_price
```

其中，`price_base` 由 `price_unit` 决定。课程设计阶段可统一采用“每千 Token”为计价单位，即 `price_base = 1000`。

### 6.4.15 api_configs API 配置表

`api_configs` 表用于保存模型供应商 API 配置信息。为避免 API Key 泄露，系统不保存明文 Key。

| 字段名 | 类型 | 说明 |
|---|---|---|
| api_config_id | int | 主键 |
| provider_id | int | 供应商 ID |
| config_name | varchar | 配置名称 |
| encrypted_api_key | text | 加密后的 API Key |
| key_iv | varchar | AES-GCM 随机向量 |
| key_tag | varchar | AES-GCM 认证标签 |
| key_version | varchar | 密钥版本号 |
| key_mask | varchar | 脱敏展示值，如 sk-****abcd |
| quota_limit | int | 调用额度限制 |
| used_quota | int | 已使用额度 |
| status | varchar | 启用、停用 |
| created_by | int | 创建人 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.16 ai_invocations 调用记录表

`ai_invocations` 表用于保存每次模型调用记录。

| 字段名 | 类型 | 说明 |
|---|---|---|
| invocation_id | int | 主键 |
| task_id | int | 所属任务 |
| branch_id | int | 所属分支 |
| model_id | int | 调用模型 |
| prompt_version_id | int | 使用的提示词版本 |
| input_text | longtext / nvarchar(max) | 输入内容 |
| output_text | longtext / nvarchar(max) | 输出内容 |
| input_tokens | int | 输入 Token 数 |
| output_tokens | int | 输出 Token 数 |
| latency_ms | int | 响应耗时 |
| status | varchar | success、failed、timeout |
| error_message | text | 错误信息 |
| created_by | int | 调用人 |
| created_at | datetime | 调用时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.17 task_outputs 输出版本表

`task_outputs` 表用于保存 AI 生成、人工编辑和人机协同修改形成的所有内容版本，是系统实现 Git 式版本管理和人机协同内容追踪的核心表。

| 字段名 | 类型 | 说明 |
|---|---|---|
| output_id | int | 主键 |
| task_id | int | 所属任务 |
| branch_id | int | 所属分支 |
| invocation_id | int | 来源模型调用，可为空 |
| version_no | varchar | 版本号，如 v1.0、v1.1 |
| output_title | varchar | 输出标题 |
| content | longtext / nvarchar(max) | 输出内容 |
| source_type | varchar | AI生成、人工编辑、混合修改、人工合并 |
| parent_output_id | int | 父版本 |
| lock_version | int | 乐观锁版本号 |
| last_modified_at | datetime | 最近修改时间 |
| last_modified_by | int | 最近修改人 |
| edit_summary | text | 修改说明 |
| is_final_candidate | bit | 是否为候选最终成果 |
| status | varchar | draft、submitted、approved、rejected、adopted、conflict_pending |
| is_deleted | bit | 是否软删除 |
| created_by | int | 创建人 |
| created_at | datetime | 创建时间 |
| deleted_at | datetime | 删除时间 |
| deleted_by | int | 删除人 |

其中，`parent_output_id` 用于追踪版本来源，形成版本树结构；`source_type` 用于区分内容来源；`lock_version` 用于实现多人协作编辑中的乐观锁控制，避免多人同时修改同一草稿时发生覆盖。

#### 乐观锁控制机制

当成员、负责人或指导教师编辑同一个输出版本时，系统采用乐观锁机制保证数据一致性。用户打开编辑页面时，前端同时获取当前版本的 `lock_version`。保存时，后端根据 `output_id` 和旧的 `lock_version` 执行更新。

MySQL 示例：

```sql
UPDATE task_outputs
SET 
    content = ?,
    lock_version = lock_version + 1,
    last_modified_at = NOW(),
    last_modified_by = ?,
    edit_summary = ?
WHERE 
    output_id = ?
    AND lock_version = ?;
```

SQL Server 示例：

```sql
UPDATE task_outputs
SET 
    content = @content,
    lock_version = lock_version + 1,
    last_modified_at = GETDATE(),
    last_modified_by = @user_id,
    edit_summary = @edit_summary
WHERE 
    output_id = @output_id
    AND lock_version = @old_lock_version;
```

如果 SQL 执行后影响行数为 0，说明该版本已被其他用户修改，系统应提示：

> 当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。

该设计能够避免多人协作时出现内容互相覆盖的问题，也体现了数据库系统中的并发控制思想。

### 6.4.18 review_requests 审核请求表

`review_requests` 表用于记录项目成员提交审核的行为。

| 字段名 | 类型 | 说明 |
|---|---|---|
| request_id | int | 主键 |
| output_id | int | 被提交审核的输出版本 |
| task_id | int | 所属任务 |
| project_id | int | 所属项目 |
| submitter_id | int | 提交人 |
| reviewer_id | int | 指定审核人，可为空 |
| request_status | varchar | pending、approved、rejected、revision_required |
| submit_note | text | 提交说明 |
| created_at | datetime | 提交时间 |
| reviewed_at | datetime | 审核时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.19 output_reviews 输出审核表

`output_reviews` 表用于保存评分和审核意见。

| 字段名 | 类型 | 说明 |
|---|---|---|
| review_id | int | 主键 |
| output_id | int | 被审核输出 |
| reviewer_id | int | 审核人 |
| accuracy_score | decimal(4,2) | 准确性评分 |
| completeness_score | decimal(4,2) | 完整性评分 |
| logic_score | decimal(4,2) | 逻辑性评分 |
| format_score | decimal(4,2) | 规范性评分 |
| usability_score | decimal(4,2) | 可用性评分 |
| risk_score | decimal(4,2) | 风险评分 |
| review_status | varchar | approved、rejected、revision_required |
| review_comment | text | 审核意见 |
| reviewed_at | datetime | 审核时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.20 issue_tags 问题标签表

`issue_tags` 表用于保存审核过程中常见的问题类型。

| 字段名 | 类型 | 说明 |
|---|---|---|
| tag_id | int | 主键 |
| tag_name | varchar | 标签名称 |
| tag_code | varchar | 标签编码 |
| description | text | 标签说明 |
| severity | varchar | 严重程度，如 low、medium、high |
| created_at | datetime | 创建时间 |
| is_deleted | bit | 是否软删除 |

示例标签包括：事实错误、逻辑混乱、内容空泛、格式不规范、缺少依据、SQL 错误、代码不可运行等。

### 6.4.21 output_issue_relations 输出问题关联表

`output_issue_relations` 表用于记录某个输出版本存在的问题标签。

| 字段名 | 类型 | 说明 |
|---|---|---|
| relation_id | int | 主键 |
| output_id | int | 输出版本 ID |
| review_id | int | 审核记录 ID |
| tag_id | int | 问题标签 ID |
| created_at | datetime | 创建时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.22 output_comments 输出批注表

`output_comments` 表用于保存负责人和指导教师对输出内容的批注意见。

| 字段名 | 类型 | 说明 |
|---|---|---|
| comment_id | int | 主键 |
| output_id | int | 被批注的输出版本 |
| commenter_id | int | 批注人 |
| comment_type | varchar | 批注类型，如修改建议、事实问题、格式问题 |
| comment_text | text | 批注内容 |
| status | varchar | 未处理、已处理、已关闭 |
| created_at | datetime | 批注时间 |
| updated_at | datetime | 更新时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.23 merge_records 分支合并记录表

`merge_records` 表用于记录多个版本发生分支冲突时，项目负责人如何处理版本合并。

| 字段名 | 类型 | 说明 |
|---|---|---|
| merge_id | int | 主键 |
| project_id | int | 所属项目 |
| task_id | int | 所属任务 |
| base_output_id | int | 共同父版本 |
| source_output_id | int | 来源版本 A |
| target_output_id | int | 来源版本 B |
| merged_output_id | int | 合并后版本 |
| merge_strategy | varchar | 采用A、采用B、手动合并、分别采用 |
| merge_comment | text | 合并说明 |
| merged_by | int | 合并人 |
| merged_at | datetime | 合并时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.24 adopted_outputs 采用成果表

`adopted_outputs` 表用于保存审核通过并被采用的项目成果。

| 字段名 | 类型 | 说明 |
|---|---|---|
| adopted_id | int | 主键 |
| project_id | int | 所属项目 |
| task_id | int | 所属任务 |
| output_id | int | 被采用版本 |
| artifact_title | varchar | 成果标题 |
| artifact_type | varchar | 需求分析、报告段落、PPT文案等 |
| release_version | varchar | 成果版本号 |
| adopted_by | int | 采用人 |
| adopted_at | datetime | 采用时间 |
| is_deleted | bit | 是否软删除 |

### 6.4.25 cost_records 成本记录表

`cost_records` 表用于保存每次模型调用产生的 Token 用量和估算成本，为首页统计、项目成本分析和模型使用审计提供依据。

| 字段名 | 类型 | 说明 |
|---|---|---|
| cost_id | int | 主键 |
| invocation_id | int | 对应模型调用记录，外键关联 ai_invocations |
| project_id | int | 所属项目 |
| task_id | int | 所属任务 |
| model_id | int | 使用模型 |
| user_id | int | 调用用户 |
| input_tokens | int | 输入 Token 数 |
| output_tokens | int | 输出 Token 数 |
| total_tokens | int | 总 Token 数 |
| input_cost | decimal(12,6) | 输入部分估算成本 |
| output_cost | decimal(12,6) | 输出部分估算成本 |
| total_cost | decimal(12,6) | 总估算成本 |
| currency | varchar | 货币单位，如 CNY、USD |
| created_at | datetime | 创建时间 |
| is_deleted | bit | 是否软删除 |

该表的成本数据由 `ai_models` 表中的 `input_price`、`output_price` 和实际 Token 数计算得到。

### 6.4.26 operation_logs 操作日志表

`operation_logs` 表用于记录系统中的关键操作，包括创建项目、生成内容、人工修改、提交审核、审核通过、成果采用、项目归档等行为。

| 字段名 | 类型 | 说明 |
|---|---|---|
| log_id | int | 主键 |
| user_id | int | 操作用户，外键关联 users |
| project_id | int | 所属项目，可为空 |
| task_id | int | 所属任务，可为空 |
| target_type | varchar | 操作对象类型，如 project、task、output、review |
| target_id | int | 操作对象 ID |
| action_type | varchar | 操作类型，如 create、update、approve、archive |
| action_desc | text | 操作描述 |
| old_value | text | 修改前内容，可为空 |
| new_value | text | 修改后内容，可为空 |
| ip_address | varchar | 操作 IP |
| user_agent | varchar | 浏览器或客户端信息 |
| created_at | datetime | 操作时间 |

该表是系统“全过程可追溯”的核心支撑，不建议对日志进行物理删除。

### 6.4.27 login_logs 登录日志表

`login_logs` 表用于记录用户登录行为，便于系统安全审计。

| 字段名 | 类型 | 说明 |
|---|---|---|
| login_id | int | 主键 |
| user_id | int | 用户 ID |
| username | varchar | 登录用户名 |
| login_status | varchar | success、failed |
| failure_reason | varchar | 失败原因 |
| ip_address | varchar | 登录 IP |
| user_agent | varchar | 客户端信息 |
| login_time | datetime | 登录时间 |

## 6.5 大文本存储策略

AI 输入输出通常包含 Markdown、代码、报告段落、论文摘要、项目申报书片段等长文本内容，可能远超普通 `varchar` 字段长度。因此，系统需要对大文本存储进行专门设计。

### 6.5.1 初期存储方案

课程设计阶段，为降低开发复杂度，系统将 AI 输入、AI 输出、人工修改内容和审核意见直接存储在数据库大文本字段中。

| 数据库 | 推荐字段类型 |
|---|---|
| MySQL | TEXT / MEDIUMTEXT / LONGTEXT |
| SQL Server | NVARCHAR(MAX) |

其中，普通任务描述可使用 `TEXT`，AI 输出内容和人工修改正文建议使用 `MEDIUMTEXT` 或 `LONGTEXT`；若采用 SQL Server，可统一使用 `NVARCHAR(MAX)` 存储长文本。

### 6.5.2 后期优化方案

如果系统后续继续开发并进入比赛展示或真实使用阶段，随着长文档、附件、图片和项目材料增多，可考虑引入对象存储。

| 内容类型 | 存储方式 |
|---|---|
| 短文本、标题、摘要 | 直接存数据库 |
| 长篇 Markdown、代码、报告正文 | 对象存储 + 数据库存储引用路径 |
| 附件、Word、PDF、图片 | OSS / MinIO / 本地文件系统 |
| 数据库字段 | 保存文件 URL、哈希值、大小、版本号 |

可写入文档的正式表述：

> 系统初期为降低开发复杂度，将 AI 输入输出、人工修改内容和审核意见存储在数据库大文本字段中。MySQL 可采用 `MEDIUMTEXT` 或 `LONGTEXT`，SQL Server 可采用 `NVARCHAR(MAX)`。若后续系统进入真实应用或比赛展示阶段，随着长文档、附件和多媒体材料增多，可将大文本和附件迁移至 OSS、MinIO 或本地对象存储，数据库仅保存文件路径、哈希值、版本号和元数据，以提升查询效率和系统可维护性。

# 七、关键业务事务设计

## 7.1 AI 任务生成事务

当用户执行一次 AI 生成时，系统应当完成以下操作：

1. 插入调用记录；
2. 保存模型输出；
3. 生成输出版本；
4. 计算并保存成本记录；
5. 更新任务状态；
6. 写入操作日志。

这些操作应当放在同一个事务中，保证数据一致性。如果模型调用失败，则记录失败状态和错误信息，不生成正式输出版本。

## 7.2 人工编辑版本保存事务

当成员、负责人或指导教师对输出内容进行人工修改时，系统应当完成以下操作：

1. 校验当前用户是否具有编辑权限；
2. 基于 `lock_version` 执行乐观锁校验；
3. 保存新的内容版本或更新当前草稿；
4. 记录 `source_type`、`parent_output_id`、`edit_summary`；
5. 更新任务状态；
6. 写入操作日志。

若乐观锁校验失败，说明该内容已被其他成员修改，系统不允许直接覆盖，而应提示用户刷新后重新编辑或另存为新版本。

## 7.3 输出提交审核事务

用户提交输出审核时，系统应当：

1. 创建审核请求；
2. 修改输出状态为 submitted；
3. 修改任务状态为 submitted；
4. 写入操作日志。

## 7.4 审核完成事务

审核员审核通过后，系统应当：

1. 插入审核记录（reviews 表）；
2. 修改审核请求状态为 approved（review_requests.request_status）；
3. 修改输出状态为 approved（task_outputs.status）；
4. 写入操作日志。

## 7.5 成果采用事务

项目负责人或指导教师确认采用该输出后，系统应当：

1. 将输出写入 `adopted_outputs` 成果表；
2. 修改任务状态为 adopted；
3. 修改任务分支状态为 merged；
4. 写入操作日志。

## 7.6 审核退回事务

审核员退回输出时，系统应当：

1. 插入审核记录；
2. 标注问题标签；
3. 修改输出状态为 revision_required 或 rejected；
4. 修改任务状态；
5. 写入操作日志。

## 7.7 分支冲突处理机制

由于系统采用 Git 式版本管理思想，同一任务下可能出现多名成员同时基于同一个 AI 初稿进行修改的情况。例如，成员 A 和成员 B 同时基于版本 v1.0 创建了不同的修改版本，并分别提交审核。此时系统不能简单覆盖任何一方的结果，而应保留多个版本并交由项目负责人处理。

### 7.6.1 冲突产生场景

| 场景 | 说明 |
|---|---|
| 同源分支并行修改 | 两个成员基于同一个父版本修改 |
| 同一任务多个候选版本 | 多个版本同时提交审核 |
| 已有版本被采用后，又有旧分支提交 | 新提交版本基于过期父版本 |
| 负责人和成员同时修改 | 双方编辑同一份草稿 |

### 7.6.2 冲突处理策略

系统采用“保留版本、标记冲突、人工决策、记录合并”的策略。

具体规则如下：

1. 系统不直接覆盖已有成果；
2. 多个候选版本均保存在 `task_outputs` 表中；
3. 若两个版本基于同一个父版本且都提交审核，后提交版本可标记为 `conflict_pending`；
4. 项目负责人通过版本对比页面查看两个版本；
5. 项目负责人可以选择采用 A 版本、采用 B 版本、分别采用，或手动合并生成 C 版本；
6. 手动合并后必须生成新的 `task_outputs` 记录；
7. 合并过程写入 `merge_records` 表；
8. 所有冲突处理行为写入 `operation_logs` 表。

推荐状态设计：

| 状态 | 含义 |
|---|---|
| conflict_pending | 存在分支冲突，等待负责人处理 |
| merged_manually | 已由负责人手动合并 |
| superseded | 已被其他版本替代 |
| adopted_separately | 作为独立成果采用 |

文档表述可写为：

> 当系统检测到多个输出版本基于同一父版本并同时提交审核时，不直接覆盖任何版本，而是将其标记为分支冲突。项目负责人可通过版本对比页面查看不同版本差异，并选择采用其中一个版本、退回版本、分别采用，或手动合并生成新的输出版本。所有冲突处理行为均写入合并记录表和操作日志，以保证项目成果演进过程可追溯。

## 7.8 项目一键归档事务

项目完成后，项目负责人或管理员可以执行项目归档操作。归档过程涉及项目、任务、分支等多张表状态更新，应通过事务保证一致性。归档成功后，系统应写入操作日志；若任一步骤失败，应回滚全部更新。

# 八、系统技术架构

## 8.1 推荐技术路线

为了兼顾开发效率、界面美观度和数据库课程要求，推荐采用 Web 系统架构：

1. 前端：基于 V3 Admin Vite 开源模板二次开发，底层采用 Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router；
2. 后端：Python FastAPI；
3. 数据库：MySQL 或 SQL Server；
4. 数据库访问：使用参数化 SQL 或轻量封装，避免完全依赖 ORM；
5. 图表：ECharts；
6. 大模型接口：封装为统一 ModelAdapter；
7. 版本管理：Git 管理源代码，数据库模拟 Git 式任务版本。

本项目最终确认采用 Web 技术路线，不再优先考虑桌面 GUI 方案。选择 Web 方案的原因如下：

1. V3 Admin Vite 模板提供成熟的后台布局、路由守卫、状态管理和样式体系，开发效率高；
2. Element Plus 对表格、表单、弹窗、抽屉、标签、时间线等管理系统组件支持较好；
3. FastAPI 适合构建清晰的 REST API，便于前后端分离；
4. MySQL / SQL Server 能充分体现关系型数据库设计、约束、事务和 SQL 查询能力；
5. ECharts 适合完成课程报告中需要展示的可视化统计图；
6. 前后端分离结构更便于截图展示、功能测试和后期维护。

本项目不改造 LobeChat / Open WebUI 源码，但前端基础工程采用 V3 Admin Vite 开源 Vue3 后台模板进行二次开发。该模板采用 MIT 许可证，合规风险低。

最终技术栈确定为：

```text
前端（基于 V3 Admin Vite）：
  Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router + UnoCSS + Sass
后端：
  Python FastAPI
数据库：
  MySQL 或 SQL Server
数据库访问：
  参数化 SQL / 轻量 Repository 层
大模型接口：
  Mock ModelAdapter + 可选真实模型 API
图表：
  ECharts
```

该路线既能保证界面美观，也能突出数据库课程设计要求。


## 8.2 系统分层架构

系统分为五层：

1. 表现层：负责页面展示和用户交互；
2. 接口层：负责接收前端请求，进行参数校验；
3. 业务层：处理项目、任务、审核、调用等业务逻辑；
4. 数据访问层：通过嵌入式 SQL 与数据库交互；
5. 外部服务层：统一封装大模型 API 调用。

## 8.3 后端目录结构建议

```text
backend/
  app/
    main.py
    config.py
    database.py
    routers/
      auth.py
      users.py
      projects.py
      tasks.py
      prompts.py
      models.py
      invocations.py
      reviews.py
      statistics.py
    services/
      auth_service.py
      project_service.py
      task_service.py
      model_service.py
      invocation_service.py
      review_service.py
      statistics_service.py
    repositories/
      user_repo.py
      project_repo.py
      task_repo.py
      prompt_repo.py
      model_repo.py
      invocation_repo.py
      review_repo.py
    adapters/
      base_adapter.py
      mock_adapter.py
      qwen_adapter.py
      deepseek_adapter.py
    utils/
      password.py
      token.py
      validators.py
      logger.py
  requirements.txt
  run.py
```

## 8.4 前端目录结构建议

前端项目基于 V3 Admin Vite 模板裁剪和改造，具体目录以实际模板结构为准。课程报告中重点说明本项目在模板基础上完成了系统品牌替换、认证接口适配、菜单重构、Mock API 清理和业务占位页设计。

建议目录结构如下：

```text
frontend/
  package.json
  vite.config.ts
  index.html
  .env.example
  .env.production
  .env.staging
  LICENSE
  NOTICE.md
  README.md
  src/
    main.ts
    App.vue
    router/
    store/
    api/
    layout/
    views/
    components/
    styles/
    utils/
```

其中：

1. `router/` 保存前端路由与路由守卫；
2. `store/` 保存 Pinia 用户状态和权限信息；
3. `api/` 封装 Axios 请求和后端接口；
4. `layout/` 保存后台基础布局；
5. `views/` 保存登录页、首页和各业务占位页；
6. `components/` 保存通用组件；
7. `.env.production` 和 `.env.staging` 已清理原模板 Mock API，接口地址改为本项目后端地址或占位符。


## 8.5 数据库脚本结构

```text
database/
  01_create_database.sql
  02_create_tables.sql
  03_create_indexes.sql
  04_insert_initial_data.sql
  05_create_views.sql
  06_create_stored_procedures.sql
  07_test_queries.sql
```

---

# 九、界面设计方案

## 9.1 整体界面风格

系统界面基于 V3 Admin Vite 的成熟后台管理风格进行二次设计，整体采用现代化后台平台布局，包括左侧导航栏、顶部用户信息栏、卡片式内容区、状态标签、表格容器和统一主题色。

视觉上，系统参考 New API、LobeChat、Open WebUI 等 AI 平台的产品质感，但不复用其源码和品牌素材。页面目标不是做成普通学生管理系统，而是呈现为一个成熟的 AI 项目协作与质量审计平台。

界面设计重点包括：

1. 登录页突出系统名称和 AI 项目协作定位；
2. 后台采用左侧导航 + 顶部用户信息栏 + 内容区布局；
3. 首页使用流程卡片展示项目空间、AI 生成、人工编辑、审核中心、成果库和统计看板；
4. 业务页面在当前阶段先做占位，后续逐步对接真实接口；
5. 原 V3 Admin Vite 模板的 Mock API、Mock 数据和无关演示页面已移除或禁用；
6. 页面风格应适合课程答辩截图和系统展示。


## 9.2 页面清单

| 页面     | 主要内容              |
| ------ | ----------------- |
| 登录页    | 用户登录、角色识别         |
| 首页仪表盘  | 项目、任务、模型调用、审核统计   |
| 项目列表页  | 查看、创建、归档项目        |
| 项目详情页  | 项目信息、成员、任务、成果     |
| 任务创建页  | 创建 AI 辅助任务        |
| 任务详情页  | 任务说明、分支、模型输出、版本历史 |
| 多模型生成页 | 选择模型和模板，生成多个结果    |
| 版本时间线页 | 查看输出版本演进过程        |
| 审核中心页  | 查看待审核输出，评分和反馈     |
| 成果库页   | 查看已采用内容和版本        |
| 提示词模板页 | 管理模板和模板版本         |
| 模型管理页  | 管理模型供应商和模型状态      |
| 调用日志页  | 查询调用记录、失败记录和成本    |
| 用户管理页  | 管理用户、角色、状态        |

## 9.3 首页仪表盘设计

首页展示：

1. 项目总数；
2. 进行中项目数；
3. 今日 AI 调用次数；
4. 待审核任务数；
5. 本月 Token 消耗；
6. 估算调用成本；
7. 模型调用占比饼图；
8. 任务类型分布柱状图；
9. 模型平均评分排行；
10. 最近任务动态表。

## 9.4 任务详情页设计

任务详情页是系统核心页面，应包含：

1. 任务标题；
2. 任务描述；
3. 所属项目；
4. 任务状态；
5. 分支信息；
6. 模型输出结果列表；
7. 版本时间线；
8. 提交审核按钮；
9. 审核意见；
10. 采用状态。

## 9.5 审核中心页面设计

审核中心页面应包含：

1. 待审核列表；
2. 输出内容预览；
3. 原始输入；
4. 使用模型；
5. 使用提示词模板；
6. 多维评分表单；
7. 问题标签选择；
8. 审核意见输入框；
9. 通过 / 退回 / 需修改按钮。

---

# 十、嵌入式 SQL 与典型查询设计

## 10.1 查询项目任务列表

```sql
SELECT
    t.task_id,
    t.title,
    tt.type_name,
    u.real_name AS assignee_name,
    t.status,
    t.priority,
    t.created_at
FROM project_tasks t
JOIN task_types tt ON t.task_type_id = tt.task_type_id
LEFT JOIN users u ON t.assignee_id = u.user_id
WHERE t.project_id = ?
  AND t.is_deleted = 0
ORDER BY t.created_at DESC;
```

## 10.2 查询待审核输出

```sql
SELECT
    rr.request_id,
    p.project_name,
    t.title AS task_title,
    o.output_title,
    u.real_name AS submitter_name,
    rr.request_status,
    rr.created_at
FROM review_requests rr
JOIN task_outputs o ON rr.output_id = o.output_id
JOIN project_tasks t ON o.task_id = t.task_id
JOIN projects p ON t.project_id = p.project_id
JOIN users u ON rr.submitter_id = u.user_id
WHERE rr.request_status = 'pending'
  AND rr.is_deleted = 0
  AND o.is_deleted = 0
ORDER BY rr.created_at ASC;
```

## 10.3 查询模型调用统计

```sql
SELECT
    m.display_name,
    COUNT(i.invocation_id) AS call_count,
    SUM(CASE WHEN i.status = 'success' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN i.status <> 'success' THEN 1 ELSE 0 END) AS failed_count,
    AVG(i.latency_ms) AS avg_latency,
    SUM(COALESCE(i.input_tokens, 0) + COALESCE(i.output_tokens, 0)) AS total_tokens
FROM ai_invocations i
JOIN ai_models m ON i.model_id = m.model_id
JOIN project_tasks t ON i.task_id = t.task_id AND t.is_deleted = 0
JOIN projects p ON t.project_id = p.project_id AND p.is_deleted = 0
GROUP BY m.display_name
ORDER BY call_count DESC;
```

## 10.4 查询模型平均评分

```sql
SELECT
    m.display_name,
    AVG((r.accuracy_score + r.completeness_score + r.logic_score + r.format_score + r.usability_score) / 5.0) AS avg_score
FROM output_reviews r
JOIN task_outputs o ON r.output_id = o.output_id
JOIN ai_invocations i ON o.invocation_id = i.invocation_id
JOIN ai_models m ON i.model_id = m.model_id
WHERE r.is_deleted = 0
  AND o.is_deleted = 0
GROUP BY m.display_name
ORDER BY avg_score DESC;
```

## 10.5 查询项目成果库

```sql
SELECT
    a.adopted_id,
    a.artifact_title,
    a.artifact_type,
    a.release_version,
    t.title AS source_task,
    u.real_name AS adopted_by_name,
    a.adopted_at
FROM adopted_outputs a
JOIN project_tasks t ON a.task_id = t.task_id
JOIN users u ON a.adopted_by = u.user_id
WHERE a.project_id = ?
  AND a.is_deleted = 0
ORDER BY a.adopted_at DESC;
```

## 10.6 查询输出版本演进时间线

为了支持 Git 式版本管理，系统需要能够查询某个输出版本的完整演进路径。例如，一个版本可能经历：

> AI 初稿 → 成员修改版 → 负责人修改版 → 教师批注版 → 最终采用版

该过程可以通过 `task_outputs.parent_output_id` 字段形成版本树，并使用递归查询获得完整版本链路。

### MySQL 8.0 及以上版本递归查询示例

```sql
WITH RECURSIVE version_tree AS (
    SELECT 
        output_id,
        parent_output_id,
        task_id,
        version_no,
        output_title,
        source_type,
        created_by,
        created_at,
        content,
        0 AS depth
    FROM task_outputs
    WHERE output_id = ?
      AND is_deleted = 0

    UNION ALL

    SELECT 
        parent.output_id,
        parent.parent_output_id,
        parent.task_id,
        parent.version_no,
        parent.output_title,
        parent.source_type,
        parent.created_by,
        parent.created_at,
        parent.content,
        child.depth + 1 AS depth
    FROM task_outputs parent
    JOIN version_tree child
        ON child.parent_output_id = parent.output_id
    WHERE parent.is_deleted = 0
)
SELECT 
    vt.output_id,
    vt.parent_output_id,
    vt.version_no,
    vt.output_title,
    vt.source_type,
    u.real_name AS creator_name,
    vt.created_at,
    vt.depth
FROM version_tree vt
LEFT JOIN users u ON vt.created_by = u.user_id
ORDER BY vt.depth DESC;
```

### SQL Server 递归 CTE 示例

```sql
WITH version_tree AS (
    SELECT 
        output_id,
        parent_output_id,
        task_id,
        version_no,
        output_title,
        source_type,
        created_by,
        created_at,
        content,
        0 AS depth
    FROM task_outputs
    WHERE output_id = @output_id
      AND is_deleted = 0

    UNION ALL

    SELECT 
        parent.output_id,
        parent.parent_output_id,
        parent.task_id,
        parent.version_no,
        parent.output_title,
        parent.source_type,
        parent.created_by,
        parent.created_at,
        parent.content,
        child.depth + 1 AS depth
    FROM task_outputs parent
    JOIN version_tree child
        ON child.parent_output_id = parent.output_id
    WHERE parent.is_deleted = 0
)
SELECT 
    vt.output_id,
    vt.parent_output_id,
    vt.version_no,
    vt.output_title,
    vt.source_type,
    u.real_name AS creator_name,
    vt.created_at,
    vt.depth
FROM version_tree vt
LEFT JOIN users u ON vt.created_by = u.user_id
ORDER BY vt.depth DESC;
```

该查询能够从当前版本向上追溯父版本，形成完整的版本演进链。该设计体现了系统对递归查询和复杂版本关系的支持，也能作为课程报告中展示数据库查询能力的重要示例。

## 10.7 视图设计：项目任务统计视图

为了简化首页仪表盘和项目详情页的数据查询，可创建项目任务统计视图。

```sql
CREATE VIEW v_project_task_statistics AS
SELECT 
    p.project_id,
    p.project_name,
    COUNT(t.task_id) AS total_tasks,
    SUM(CASE WHEN t.status = 'draft' THEN 1 ELSE 0 END) AS draft_tasks,
    SUM(CASE WHEN t.status = 'submitted' THEN 1 ELSE 0 END) AS submitted_tasks,
    SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) AS approved_tasks,
    SUM(CASE WHEN t.status = 'adopted' THEN 1 ELSE 0 END) AS adopted_tasks
FROM projects p
LEFT JOIN project_tasks t 
    ON p.project_id = t.project_id
    AND t.is_deleted = 0
WHERE p.is_deleted = 0
GROUP BY p.project_id, p.project_name;
```

该视图可直接用于首页展示项目任务数量、待审核数量和已采用成果数量，减少前端复杂联表查询。

## 10.8 触发器设计：审核通过后自动写入操作日志

为了增强数据库层面的审计能力，可设计触发器：当 `output_reviews` 中插入审核通过记录时，自动向 `operation_logs` 表插入一条审核通过日志。

### MySQL 触发器示例

```sql
DELIMITER $$

CREATE TRIGGER trg_after_output_review_approved
AFTER INSERT ON output_reviews
FOR EACH ROW
BEGIN
    IF NEW.review_status = 'approved' THEN
        INSERT INTO operation_logs (
            user_id,
            target_type,
            target_id,
            action_type,
            action_desc,
            created_at
        )
        VALUES (
            NEW.reviewer_id,
            'task_output',
            NEW.output_id,
            'approve',
            CONCAT('输出版本 ', NEW.output_id, ' 审核通过'),
            NOW()
        );
    END IF;
END$$

DELIMITER ;
```

### SQL Server 触发器示例

```sql
CREATE TRIGGER trg_after_output_review_approved
ON output_reviews
AFTER INSERT
AS
BEGIN
    INSERT INTO operation_logs (
        user_id,
        target_type,
        target_id,
        action_type,
        action_desc,
        created_at
    )
    SELECT
        reviewer_id,
        'task_output',
        output_id,
        'approve',
        CONCAT('输出版本 ', output_id, ' 审核通过'),
        GETDATE()
    FROM inserted
    WHERE review_status = 'approved';
END;
```

该触发器体现了系统在数据库层面对关键业务行为进行自动审计的能力。

## 10.9 存储过程设计：项目一键归档

项目完成后，项目负责人或管理员可以执行项目归档操作。归档过程会同时更新项目状态、任务状态、任务分支状态，并写入操作日志。由于该操作涉及多表更新，应通过事务和存储过程保证一致性。

### MySQL 存储过程示例

```sql
DELIMITER $$

CREATE PROCEDURE sp_archive_project(
    IN p_project_id INT,
    IN p_operator_id INT
)
BEGIN
    START TRANSACTION;

    UPDATE projects
    SET 
        status = 'archived',
        updated_at = NOW(),
        updated_by = p_operator_id
    WHERE project_id = p_project_id
      AND is_deleted = 0;

    UPDATE project_tasks
    SET 
        status = 'archived',
        updated_at = NOW(),
        updated_by = p_operator_id
    WHERE project_id = p_project_id
      AND is_deleted = 0;

    UPDATE task_branches
    SET 
        status = 'closed'
    WHERE project_id = p_project_id
      AND is_deleted = 0;

    INSERT INTO operation_logs (
        user_id,
        project_id,
        target_type,
        target_id,
        action_type,
        action_desc,
        created_at
    )
    VALUES (
        p_operator_id,
        p_project_id,
        'project',
        p_project_id,
        'archive',
        '项目执行一键归档操作',
        NOW()
    );

    COMMIT;
END$$

DELIMITER ;
```

### SQL Server 存储过程示例

```sql
CREATE PROCEDURE sp_archive_project
    @project_id INT,
    @operator_id INT
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        UPDATE projects
        SET 
            status = 'archived',
            updated_at = GETDATE(),
            updated_by = @operator_id
        WHERE project_id = @project_id
          AND is_deleted = 0;

        UPDATE project_tasks
        SET 
            status = 'archived',
            updated_at = GETDATE(),
            updated_by = @operator_id
        WHERE project_id = @project_id
          AND is_deleted = 0;

        UPDATE task_branches
        SET status = 'closed'
        WHERE project_id = @project_id
          AND is_deleted = 0;

        INSERT INTO operation_logs (
            user_id,
            project_id,
            target_type,
            target_id,
            action_type,
            action_desc,
            created_at
        )
        VALUES (
            @operator_id,
            @project_id,
            'project',
            @project_id,
            'archive',
            '项目执行一键归档操作',
            GETDATE()
        );

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
```

该存储过程体现了系统对事务完整性、多表状态一致性和关键操作审计的支持。

# 十一、系统开发计划

## 11.1 第一阶段：需求分析与方案确定

任务：

1. 明确项目名称；
2. 明确系统角色；
3. 明确业务流程；
4. 明确功能模块；
5. 绘制系统用例图；
6. 编写需求分析文档。

输出物：

1. 项目开发文档；
2. 功能需求表；
3. 非功能需求表；
4. 用例图。

## 11.2 第二阶段：数据库设计

任务：

1. 识别核心实体；
2. 绘制 E-R 图；
3. 设计逻辑表结构；
4. 设计主外键关系；
5. 设计约束和索引；
6. 编写建库建表 SQL；
7. 插入初始化数据。

输出物：

1. E-R 图；
2. 数据库表结构说明；
3. 建库建表 SQL；
4. 初始化数据 SQL。

## 11.3 第三阶段：后端开发

任务：

1. 搭建后端项目；
2. 实现数据库连接；
3. 实现用户登录；
4. 实现项目管理接口；
5. 实现任务管理接口；
6. 实现提示词模板接口；
7. 实现模型调用接口；
8. 实现审核接口；
9. 实现统计接口。

输出物：

1. 后端源代码；
2. 接口测试截图；
3. 嵌入式 SQL 示例。

## 11.4 第四阶段：前端开发

本阶段前端开发不再从零搭建普通后台页面，而是基于 V3 Admin Vite 开源 Vue3 后台模板进行裁剪和二次开发。

任务：

1. 引入并裁剪 V3 Admin Vite 模板；
2. 保留 LICENSE / NOTICE 与来源说明；
3. 替换系统品牌和菜单；
4. 移除模板 Mock API、Mock 数据和无关演示页面；
5. 适配后端登录接口；
6. 实现路由守卫与用户状态；
7. 实现后台整体布局；
8. 实现项目、任务、模型、审核、成果库、统计等占位页面；
9. 后续逐步接入真实业务接口。

输出物：

1. 基于 V3 Admin Vite 二次开发的前端源代码；
2. 前端模板来源与许可证说明；
3. 登录页和后台布局截图；
4. 关键占位页面截图；
5. 后续业务页面开发计划。


## 11.5 第五阶段：系统测试与报告撰写

任务：

1. 设计测试用例；
2. 测试登录功能；
3. 测试项目创建；
4. 测试任务创建；
5. 测试模型生成；
6. 测试审核流程；
7. 测试成果采用；
8. 测试统计图表；
9. 整理截图；
10. 撰写课程报告。

输出物：

1. 测试用例表；
2. 测试截图；
3. 完整课程报告；
4. 项目源代码；
5. 数据库脚本。

---

# 十二、Git 源代码管理方案

## 12.1 仓库结构

```text
AI-Collab-Audit-System/
  README.md
  docs/
    project_development_doc.md
    database_design.md
    test_report.md
  backend/
  frontend/
  database/
  screenshots/
  report/
  .gitignore
```

## 12.2 分支管理策略

建议使用简化版 Git Flow：

| 分支                 | 作用          |
| ------------------ | ----------- |
| main               | 稳定版本，用于最终提交 |
| dev                | 日常开发集成分支    |
| feature/database   | 数据库设计与脚本    |
| feature/backend    | 后端接口开发      |
| feature/frontend   | 前端页面开发      |
| feature/review     | 审核模块开发      |
| feature/statistics | 统计图表模块开发    |
| docs/report        | 报告文档撰写      |

## 12.3 Commit 规范

建议使用以下提交格式：

```text
feat: 新增项目任务管理接口
fix: 修复登录状态判断错误
docs: 更新数据库设计说明
style: 优化首页仪表盘布局
refactor: 重构模型调用适配器
test: 增加审核流程测试数据
sql: 新增任务输出版本表
```

## 12.4 版本里程碑

| 版本   | 内容               |
| ---- | ---------------- |
| v0.1 | 完成需求分析和数据库初稿     |
| v0.2 | 完成建表 SQL 和初始化数据  |
| v0.3 | 完成用户登录、项目管理、任务管理 |
| v0.4 | 完成模型调用和输出版本保存    |
| v0.5 | 完成审核中心和成果库       |
| v0.6 | 完成统计图表和系统美化      |
| v1.0 | 完成测试、报告和最终提交     |

---

# 十三、测试方案

## 13.1 测试类型

系统测试包括：

1. 登录测试；
2. 权限测试；
3. 数据增删改查测试；
4. 项目空间管理测试；
5. 任务创建测试；
6. 模型调用测试；
7. 输出版本保存测试；
8. 审核流程测试；
9. 成果采用测试；
10. 统计查询测试；
11. 异常输入测试；
12. 数据一致性测试。

## 13.2 典型测试用例

| 测试编号 | 测试功能  | 输入         | 预期结果        |
| ---- | ----- | ---------- | ----------- |
| T01  | 用户登录  | 正确用户名和密码   | 登录成功，进入首页   |
| T02  | 用户登录  | 错误密码       | 登录失败，提示错误   |
| T03  | 创建项目  | 输入项目名称和类型  | 项目创建成功      |
| T04  | 创建任务  | 选择项目和任务类型  | 任务创建成功      |
| T05  | AI 生成 | 选择模型和模板    | 生成结果并保存输出版本 |
| T06  | 提交审核  | 选择某个输出版本   | 审核请求创建成功    |
| T07  | 审核通过  | 填写评分和意见    | 输出进入成果库     |
| T08  | 审核退回  | 标注问题并退回    | 任务状态变为需修改   |
| T09  | 查看统计  | 进入首页       | 显示调用次数和模型评分 |
| T10  | 权限控制  | 普通成员访问模型管理 | 拒绝访问        |

---

# 十四、系统安全与合规设计

## 14.1 API Key 安全

为避免 API Key 泄露，系统不在数据库中保存明文密钥。管理员配置 API Key 后，后端使用 **AES-256-GCM 对称加密算法**对密钥进行加密，数据库仅保存密文、随机向量、认证标签和密钥版本号。

设计原则如下：

1. API Key 入库前使用 AES-256-GCM 加密；
2. 主密钥不存入数据库，而是保存在服务器环境变量或独立配置文件中；
3. 数据库中只保存密文、随机向量 IV、认证标签 Tag 和密钥版本号；
4. 前端页面永远不返回完整 API Key；
5. 管理员只能看到脱敏后的 Key，例如 `sk-****abcd`；
6. 调用模型时由后端在内存中临时解密使用；
7. 操作日志不记录明文 Key；
8. 支持密钥轮换，即更换主密钥后更新 `key_version`。

`api_configs` 表字段设计中应包含 `encrypted_api_key`、`key_iv`、`key_tag`、`key_version` 和 `key_mask` 等字段。主加密密钥通过服务器环境变量维护，不写入数据库和源代码仓库。模型调用时由后端在内存中临时解密并使用，调用结束后不在日志中输出明文密钥。

## 14.2 用户数据安全

1. 密码使用哈希存储；
2. 登录状态使用 Token 或 Session 管理；
3. 根据角色控制访问范围；
4. 项目成员只能查看自己参与的项目；
5. 操作日志记录关键行为；
6. 登录失败次数过多时可进行临时锁定；
7. 所有涉及权限的数据查询都应校验当前用户所属项目和角色。

## 14.3 AI 使用合规

1. 系统不用于倒卖 API Key；
2. 系统不承诺模型为自研模型；
3. 系统不使用模型输出训练竞品模型；
4. 系统提示用户不要输入敏感隐私数据；
5. 系统保留模型调用记录，用于质量审计和异常排查；
6. AI 输出不能直接进入最终成果库，必须经过人工修改、审核或确认；
7. 平台应在用户界面提示“AI 结果仅供参考，最终内容由项目成员和审核人负责”。

## 14.4 审计数据保护

1. `operation_logs`、`login_logs`、`ai_invocations` 和 `cost_records` 原则上不允许普通用户删除；
2. 管理员执行日志清理时应先导出归档；
3. 关键审计表可按学期、项目或年份进行归档；
4. 归档后的日志仍应能够支持项目复盘和课程报告检查。

# 十五、项目可行性分析

## 15.1 技术可行性

系统采用成熟的 Web 开发技术和关系型数据库技术，前端、后端、数据库和大模型接口均有成熟方案。即使实际 API 调用受限，也可以使用 Mock 模型适配器模拟不同模型返回结果，不影响数据库流程、界面展示和系统测试。

## 15.1.1 技术栈风险与降级方案

本系统采用 Vue3 + Element Plus + FastAPI + MySQL / SQL Server 的技术路线。该路线在后台管理系统开发中较为成熟，适合实现表格、表单、弹窗、权限菜单、数据看板和日志查询等功能。

但 AI 产品中常见的流式输出、打字机效果、Markdown 长文本渲染、代码高亮和多模型并发调用等功能，对前端交互和后端接口设计有一定要求。为保证课程设计按期完成，系统采用“核心功能优先、交互效果渐进增强”的策略。

| 功能 | 风险 | 降级方案 |
|---|---|---|
| 流式输出 | SSE / WebSocket 实现复杂 | 课程版可降级为整段返回 |
| 打字机效果 | 状态控制和渲染性能要求较高 | 可取消动画，直接展示文本 |
| Markdown 渲染 | 长文本可能影响性能 | 使用 markdown-it / md-editor-v3 |
| 代码高亮 | 需要额外依赖 | 使用 highlight.js 或 shiki |
| 多模型并发调用 | 调用失败、超时、费用不可控 | 先使用 Mock 模型，真实 API 只接 1 个 |
| 版本差异对比 | 文本 diff 实现复杂 | 初期用版本时间线和修改说明代替 |
| 长文本存储 | 数据库表可能膨胀 | 初期 TEXT，后期对象存储 |

正式表述：

> 本系统前端采用 Vue3 + Element Plus 实现后台管理界面，该技术路线在表格、表单、弹窗、权限菜单、数据看板等管理系统场景中较为成熟。但对于 AI 产品中常见的流式输出、打字机效果、长 Markdown 渲染和代码高亮等交互，Element Plus 并非专门组件库，开发时可能需要引入额外依赖或自定义组件。为保证课程设计按期完成，系统采用“核心功能优先、交互效果渐进增强”的策略：课程版可先实现整段返回后渲染、普通 Markdown 展示和版本时间线，后续比赛版再逐步增强流式输出、代码高亮、文本 Diff 和多模型并发生成等能力。

## 15.2 业务可行性

高校学生在课程项目、科研竞赛和报告撰写中已经大量使用 AI 工具，AI 使用过程管理具有现实需求。系统以项目协作为切入点，避免了普通聊天平台的空泛问题，能够真实服务课程设计、大创项目、数学建模、实验报告和竞赛材料撰写等场景。

## 15.3 开发可行性

课程设计阶段可以采用“核心功能优先”的策略：

必做功能：

1. 登录；
2. 项目管理；
3. 任务管理；
4. 提示词模板；
5. 模型调用模拟；
6. 输出版本保存；
7. 人工编辑与批注；
8. 审核流程；
9. 统计图表。

选做功能：

1. 真实 API 接入；
2. 版本差异对比；
3. Markdown 导出；
4. 成本精确计算；
5. 模型失败自动 fallback。

# 十六、课程报告可写结构

最终课程报告可按以下结构撰写。

## 摘要

简述项目背景、系统目标、技术路线、数据库设计和实现结果。

## 一、需求分析

1. 项目背景；
2. 用户角色分析；
3. 功能需求；
4. 非功能需求；
5. 系统业务流程。

## 二、系统设计与技术实现

1. 系统总体架构；
2. 功能模块设计；
3. Git 式任务管理机制；
4. 人机协同内容生产机制；
5. 数据库概念结构设计；
6. 数据库逻辑结构设计；
7. 数据库物理结构设计；
8. 关键 SQL、视图、触发器与存储过程设计；
9. 前后端实现说明。

## 三、系统测试与结果分析

1. 测试环境；
2. 测试用例；
3. 登录与权限测试；
4. 项目管理测试；
5. AI 任务生成测试；
6. 人工编辑与版本管理测试；
7. 审核流程测试；
8. 成果库测试；
9. 统计图表测试；
10. 测试结果分析。

## 四、数据库运行与维护

1. 数据库备份与恢复策略；
2. 数据库用户权限管理；
3. API Key 加密与密钥维护；
4. 操作日志与登录日志审计；
5. 软删除与数据归档策略；
6. 索引维护与查询性能优化；
7. 长文本与附件存储维护；
8. 异常数据检查与数据一致性维护。

## 五、实验结论与总结

1. 系统完成情况；
2. 项目创新点；
3. 不足与改进；
4. 后续扩展方向；
5. 个人收获与体会。

该结构与实验要求中的“系统需求分析、概念结构设计、逻辑结构设计、物理结构设计、数据库实施、系统功能实现、数据库运行与维护”相对应，能够避免报告结构缺项。

# 十七、项目亮点总结

本系统相较于传统数据库课程设计选题，具有以下亮点：

1. **场景新颖**：面向高校项目中真实存在的 AI 使用管理问题；
2. **业务闭环完整**：覆盖项目、任务、生成、人工编辑、审核、采用、归档全过程；
3. **数据库对象丰富**：涉及用户、角色、权限、项目、任务、模型、提示词、调用、审核、成果、日志、成本等多类实体；
4. **Git 思想融合**：将成熟的软件版本管理思想引入 AI 输出内容管理；
5. **人机协同明确**：AI 只负责辅助生成和启发，成员、负责人和教师共同参与修改、审核和确认；
6. **多角色权限明确**：学生成员、项目负责人、指导教师、管理员职责清晰；
7. **全过程软删除与审计追踪**：核心业务表采用软删除机制，避免物理删除导致版本链路、审核记录和调用日志断裂；
8. **数据库高级特性应用**：系统设计了视图、触发器和存储过程，用于统计查询、自动审计和项目归档事务处理；
9. **并发控制机制**：通过乐观锁字段避免多人同时编辑同一输出版本时发生内容覆盖；
10. **成本统计机制**：通过模型计费字段和成本记录表实现 Token 用量与估算成本分析；
11. **安全密钥管理**：API Key 采用 AES-256-GCM 加密存储，并通过环境变量维护主密钥；
12. **可视化效果好**：适合设计首页看板、模型统计、任务分布、评分排行等图表；
13. **报告可写性强**：需求分析、E-R 图、表结构、事务、测试用例、运行维护和总结均有充分内容；
14. **实现难度可控**：可以先用 Mock 模型完成流程，再选择性接入真实 API；
15. **后续扩展空间大**：可继续发展为高校项目 AI 协作平台、教师指导平台或创新创业比赛原型。

# 十八、建议最终开发范围

为了保证课程设计按时完成并具有高质量展示效果，建议最终实现范围如下：

## 必须完成

1. 用户登录与角色控制；
2. 项目空间管理；
3. 项目成员管理；
4. AI 任务创建；
5. 提示词模板选择；
6. 至少三个模型的模拟调用；
7. 至少一个真实模型 API 可选接入；
8. AI 输出版本保存；
9. 输出提交审核；
10. 审核评分与问题标注；
11. 审核通过后进入成果库；
12. 调用日志查询；
13. 首页统计图表；
14. 数据库建表脚本与初始化数据；
15. 系统测试截图和报告。

## 可以选做

1. 模型失败自动切换；
2. 输出版本差异对比；
3. Markdown 导出；
4. 成本精确计算；
5. 指导教师批注意见；
6. 项目成果版本发布。

---

# 十九、初步结论

本项目以“高校项目协作中的 AI 使用管理”为真实业务场景，以 Git 式版本管理思想为核心创新，以关系型数据库为基础支撑，设计并实现一个集项目管理、AI 生成、质量审核、版本归档和统计分析于一体的信息管理系统。

相比传统图书管理、学生管理、超市管理等常见选题，本项目具有更强的时代特征和应用价值；相比普通大模型聊天平台，本项目又通过项目空间、任务版本、质量审核和成果归档形成了明确的业务闭环。该系统既能够满足数据库课程对表结构设计、主外键约束、嵌入式 SQL、增删改查、事务一致性和图形化界面的要求，也能够体现学生对当前 AI 应用发展趋势的理解和创新实践能力。

因此，该项目适合作为《数据库管理实务》课程结课设计选题，并具有较高的完成度展示空间和报告撰写价值。
