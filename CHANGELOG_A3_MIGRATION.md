# EduAgent Studio — A3 Migration Changelog

## [Phase 1] 2026-06-11

### 重大变更

#### 项目重命名
- 项目名称从「AI-Collab-Audit-System」更名为「EduAgent Studio（智学工坊）」
- 系统定位从「AI 项目质量审计」改为「个性化学习资源生成与多智能体协作」

#### 技术架构升级
- 新增 PostgreSQL + pgvector 支持（两阶段方案 Phase 1）
- 新增多智能体编排层（LangGraph + 5个智能体）
- 新增统一 LLM Gateway（支持 Mock 和 OpenAI-compatible API）
- 新增向量检索基础设施（pgvector）

### 新增功能

#### 前端
- 新增学生画像页面（列表 + 详情）
- 新增智能体工作台页面（配置 + 执行 + 结果展示）
- 重写 Dashboard 首页（A3 业务流程 + 指标卡）
- 重写登录页（智学工坊 EduAgent Studio）
- 重写侧边栏菜单（A3 语义）
- 新增学习资源库页面
- 新增教师审核中心页面
- 新增学习分析看板页面

#### 后端
- 新增 `/api/profiles` 路由（学生画像 CRUD）
- 新增 `/api/agents` 路由（多智能体工作流）
- 新增 `/api/learning` 路由（学习任务、课程）
- 新增 `backend/app/agents/` 模块（5个智能体 + 工作流）
- 新增 `backend/app/llm/` 模块（LLM Gateway + Mock Provider）

#### 数据库
- 新增 6 张 A3 专用表（courses、knowledge_points、student_profiles 等）
- 新增 A3 初始化数据（3门课程、13个知识点、4个学习任务）

### 改造功能

#### 前端
- 所有页面文案 A3 化
- 所有路由标题 A3 化
- 统计卡片指标 A3 化

#### 后端
- FastAPI title/description 更新
- 注册新路由 profiles、agents、learning

#### 文档
- 完全重写 README.md
- 新建 A3 赛题适配说明、技术架构选型说明、多智能体设计、演示脚本、开发检查清单
- 归档旧课程报告到 docs/archive_old_course_project/

### 待完成（Phase 2）
- 学习反馈与测评模块
- 学习分析看板图表
- Redis + Celery 异步任务
- MinIO 对象存储集成
- MySQL 业务表迁移到 PostgreSQL
- 真实大模型接入（当前为 Mock）

## [Previous] AI-Collab-Audit-System
见 docs/archive_old_course_project/ 中的历史文档。
