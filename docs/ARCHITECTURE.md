# EduAgent Studio（智学工坊）架构文档

> 基于大语言模型的多智能体协作式个性化学习资源生成系统

---

## 目录

1. [总体架构](#1-总体架构)
2. [后端架构](#2-后端架构)
3. [多智能体系统](#3-多智能体系统)
4. [LLM 抽象层](#4-llm-抽象层)
5. [RAG 检索增强](#5-rag-检索增强)
6. [前端架构](#6-前端架构)
7. [数据库设计](#7-数据库设计)
8. [认证与安全](#8-认证与安全)
9. [部署架构](#9-部署架构)
10. [数据流全景](#10-数据流全景)

---

## 1. 总体架构

```
                     ┌─────────────────────────────────────┐
                     │        React 18 前端 (TypeScript)      │
                     │   Vite Dev Proxy: /api → localhost:8000 │
                     │   MUI v7 + Tailwind v4 + Zustand        │
                     └──────────────┬──────────────────────────┘
                                    │ HTTP REST + SSE (Stream)
                                    ▼
                     ┌─────────────────────────────────────┐
                     │      FastAPI 后端 (Python 3.12)       │
                     │          Uvicorn 0.40.0               │
                     │                                       │
                     │  Router → Service → Repository         │
                     │            ↓                           │
                     │    LangGraph StateGraph               │
                     │    (多智能体编排引擎)                     │
                     │            ↓                           │
                     │    LLM Gateway (Provider 注册表)        │
                     │            ↓                           │
                     │    RAG 检索器 (BM25)                    │
                     └──────┬──────────┬─────────────────────┘
                            │          │
              ┌─────────────┘          └─────────────┐
              ▼                                      ▼
   ┌──────────────────┐                  ┌──────────────────┐
   │  MySQL 5.7       │                  │  Redis 7         │
   │  (39 张业务表)    │                  │  (Celery Broker) │
   └──────────────────┘                  └──────────────────┘
              ▲
   ┌──────────────────┐                  ┌──────────────────┐
   │  PostgreSQL 16   │                  │  Celery Worker   │
   │  + pgvector      │                  │  (异步任务)       │
   │  (向量检索)       │                  │  (embedding/统计) │
   └──────────────────┘                  └──────────────────┘
```

### 技术栈总览

| 层级 | 技术选型 |
|------|----------|
| 前端 | React 18, TypeScript 5, Vite 6, MUI v7, Tailwind CSS v4, Zustand, React Router v7 |
| 后端 | FastAPI, Python 3.12, PyMySQL（无 ORM）, Pydantic v2 |
| 智能体编排 | LangGraph 1.1 (StateGraph + InMemory Checkpointer) |
| LLM | 统一 Gateway，支持 OpenAI/DeepSeek/Qwen/GLM/MiniMax/Mock |
| 异步任务 | Celery 5 + Redis 7 |
| 关系数据库 | MySQL 5.7 (39 张表 + 5 视图) |
| 向量数据库 | PostgreSQL 16 + pgvector（预留，当前未启用） |
| 对象存储 | MinIO（预留，当前使用文件系统） |
| 容器化 | Docker Compose (PostgreSQL, Redis, MinIO, Celery) |

---

## 2. 后端架构

### 2.1 目录结构

```
backend/
├── run.py                          # 开发启动入口 (uvicorn)
├── requirements.txt                # Python 依赖
├── .env                            # 环境变量（实际）
├── Dockerfile.celery               # Celery Worker 镜像
├── scripts/
│   └── test_api.py                 # API 测试脚本
└── app/
    ├── __init__.py
    ├── main.py                     # FastAPI 应用工厂
    ├── config.py                   # Pydantic Settings 配置
    ├── database.py                 # PyMySQL 连接管理
    ├── celery_app.py               # Celery 配置 + Beat 调度
    │
    ├── agents/                     # 多智能体核心
    │   ├── workflow.py             # LangGraph StateGraph 编排器
    │   ├── diagnosis_agent.py      # 诊断智能体
    │   ├── planning_agent.py       # 规划智能体
    │   ├── resource_generation_agent.py  # 资源生成智能体
    │   ├── assessment_agent.py     # 评测智能体
    │   └── teacher_review_agent.py # 教师审核智能体
    │
    ├── llm/                        # LLM 抽象层
    │   ├── gateway.py              # LLMGateway 统一入口
    │   ├── providers.py            # Provider 注册表
    │   ├── mock_provider.py        # Mock 测试 Provider
    │   ├── openai_compatible_provider.py  # OpenAI 兼容接口
    │   └── minimax_provider.py     # MiniMax 专用接口
    │
    ├── rag/                        # 检索增强生成
    │   ├── retriever.py            # BM25 检索器
    │   ├── document_loader.py      # 预置课程文档加载
    │   └── __init__.py
    │
    ├── routers/                    # API 路由层 (17 个模块)
    │   ├── auth.py
    │   ├── users.py
    │   ├── projects.py
    │   ├── tasks.py
    │   ├── prompts.py
    │   ├── models.py
    │   ├── invocations.py
    │   ├── reviews.py
    │   ├── artifacts.py
    │   ├── statistics.py
    │   ├── logs.py
    │   ├── profiles.py
    │   ├── agents.py
    │   ├── learning.py
    │   ├── feedbacks.py
    │   ├── resources.py
    │   └── storage.py
    │
    ├── services/                   # 业务逻辑层 (16 个模块)
    │   ├── agent_service.py
    │   ├── auth_service.py
    │   ├── learning_service.py
    │   ├── rag_service.py
    │   ├── storage_service.py
    │   └── ...
    │
    ├── repositories/               # 数据访问层 (15 个模块)
    │   ├── user_repo.py
    │   ├── project_repo.py
    │   ├── task_repo.py
    │   ├── learning_repo.py
    │   ├── profile_repo.py
    │   └── ...
    │
    ├── adapters/                   # 代码适配器 (Mock 实现)
    │   ├── base_adapter.py
    │   ├── mock_writer_adapter.py
    │   ├── mock_code_adapter.py
    │   └── mock_reviewer_adapter.py
    │
    ├── tasks/                      # Celery 异步任务
    │   ├── embedding_tasks.py
    │   ├── resource_tasks.py
    │   └── statistics_tasks.py
    │
    └── utils/                      # 工具模块
        ├── crypto.py               # AES-256-GCM 加密
        ├── password.py             # BCrypt 密码哈希
        ├── token.py                # JWT HS256
        ├── response.py             # 统一响应格式
        ├── exceptions.py           # 业务异常 + 全局处理器
        └── validators.py           # 输入验证
```

### 2.2 分层架构（三层）

```
┌──────────────────────────────────────────┐
│  Router 层 (routers/)                     │  HTTP 请求/响应处理
│  - 路径注册, 参数校验 (Pydantic), 依赖注入  │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│  Service 层 (services/)                   │  业务逻辑编排
│  - 事务管理, 权限校验, Agent 调用编排       │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│  Repository 层 (repositories/)           │  数据访问
│  - 原生 SQL, PyMySQL, DictCursor         │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│  MySQL 5.7                               │  持久化存储
└──────────────────────────────────────────┘
```

**关键设计决策：不使用 ORM**。所有 SQL 通过 PyMySQL + DictCursor 手写，Repository 返回 dict 而非对象。

### 2.3 应用工厂 (`main.py`)

```python
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="EduAgent Studio",
        version="1.0.0",
        docs_url="/docs",       # 非生产环境启用 Swagger UI
        redoc_url="/redoc",     # 非生产环境启用 ReDoc
    )

    # 中间件链 (仅 CORS)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

    # 全局异常处理
    register_exception_handlers(app)

    # 注册 17 个路由模块
    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    # ... 共 16 个路由挂载在 /api 下
    app.include_router(statistics.router)  # 特殊：路径已包含 /api 前缀

    return app
```

### 2.4 配置管理 (`config.py`)

使用 `pydantic-settings`，所有配置从环境变量读取：

| 领域 | 配置项 | 默认值 | 说明 |
|------|--------|--------|------|
| 应用 | `APP_NAME` | EduAgent Studio | 应用名称 |
| 应用 | `APP_ENV` | development | 环境标识 |
| 数据库 | `DB_HOST/PORT/USER/PASSWORD/NAME` | 127.0.0.1:3306 | MySQL 连接 |
| Redis | `REDIS_URL` | redis://127.0.0.1:6379/0 | Celery Broker |
| 服务器 | `SERVER_HOST/PORT` | 0.0.0.0:8000 | 监听地址 |
| LLM | `LLM_PROVIDER/API_KEY/BASE_URL/MODEL` | openai_compatible | LLM 配置 |
| 安全 | `JWT_SECRET_KEY` | (必须配置) | JWT 签名密钥 |
| 安全 | `API_KEY_SECRET` | (必须配置) | AES 加密主密钥 |
| PostgreSQL | `POSTGRES_URL` | (可选) | pgvector 连接 |

### 2.5 异步任务 (`celery_app.py`)

```
Celery App: "eduagent"
Broker:     Redis
Backend:    Redis

定时任务 (Celery Beat):
  ├── 每日成本汇总 (86400s)
  └── 每小时缓存清理 (3600s)

任务模块:
  ├── embedding_tasks   (向量嵌入)
  ├── resource_tasks    (资源生成)
  └── statistics_tasks  (统计汇总)
```

---

## 3. 多智能体系统

### 3.1 工作流编排 (workflow.py)

这是项目的**核心创新**。6 个智能体通过 LangGraph StateGraph 编排协作：

```
                        ┌─────────────────────┐
                        │      INIT           │
                        └─────────┬───────────┘
                                  │
                        ┌─────────▼───────────┐
                        │   SUPERVISOR        │  ← 编排路由中心
                        └─────────┬───────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                    │
     ┌────────▼────────┐  ┌──────▼──────┐   ┌────────▼────────┐
     │   DIAGNOSIS     │  │  PLANNING   │   │   GENERATION    │
     │   学生诊断        │→│  学习规划     │→│   资源生成        │
     └─────────────────┘  └─────────────┘   └─────────────────┘
              │                   │                    │
     ┌────────▼────────┐  ┌──────▼──────┐   ┌────────▼────────┐
     │   ASSESSMENT    │  │TEACHER_REVIEW│   │   REVISION      │
     │   学习评测        │→│  教师审核      │←──│   返工 (≤3次)    │
     └─────────────────┘  └──────┬───────┘   └─────────────────┘
                                  │
                          quality >= 7.0?
                                  │
                        ┌─────────▼───────────┐
                        │     COMPLETED       │
                        └─────────────────────┘
```

**监督路由策略**：

```
INIT → DIAGNOSIS → PLANNING → GENERATION → ASSESSMENT → TEACHER_REVIEW
                                                              │
                                      ┌───────────────────────┤
                                      │                       │
                              quality < 7.0             quality >= 7.0
                              count < 3                       │
                                      │                       │
                              ┌───────▼──────┐        ┌──────▼──────┐
                              │   REVISION   │        │  COMPLETED  │
                              └───────┬──────┘        └─────────────┘
                                      │
                              ┌───────▼──────┐
                              │TEACHER_REVIEW│  (重新审核)
                              └──────────────┘
```

### 3.2 工作流状态 (WorkflowState)

```python
class WorkflowState(TypedDict, total=False):
    # 输入参数
    run_id: str                              # 唯一运行 ID
    student_id: int                          # 学生 ID
    course_id: int                           # 课程 ID
    knowledge_point_ids: List[int]           # 目标知识点
    resource_type: str                       # 资源类型
    difficulty: str                          # 难度等级

    # 上下文数据
    student_profile: Dict                    # 学生画像
    knowledge_points: List[Dict]             # 知识点列表
    learning_history: List[Dict]             # 学习历史

    # Agent 输出
    diagnosis: Dict                          # 诊断结果
    learning_plan: Dict                      # 学习规划
    generated_resource: Dict                 # 生成资源
    assessment: Dict                         # 评测结果
    teacher_review: Dict                     # 审核结果

    # 流程控制
    current_step: str                        # 当前步骤 (enum)
    step_history: List[Dict]                 # 步骤执行历史
    revision_count: int                      # 返工计数器 (0-3)
    quality_score: float                     # 质量评分 (0-10)
    needs_revision: bool                     # 是否需要返工

    # 元信息
    metadata: Dict                           # 耗时、错误等
```

### 3.3 五个智能体

#### 诊断智能体 (DiagnosisAgent)

```
输入:  student_profile + knowledge_points + learning_history
输出:  {weak_points, strength_points, learning_difficulties,
        resource_needs, suggested_difficulty}
功能:  分析学生薄弱知识点，识别学习困难，建议资源类型
回退:  基于 mastery_level 的规则判断 (<0.5 = 薄弱)
```

#### 规划智能体 (PlanningAgent)

```
输入:  diagnosis + learning_goal + course_outline
输出:  {learning_path[{order, kp_id, kp_name, estimated_time,
        resource_type, priority}], resource_combination,
        learning_sequence, estimated_total_time}
功能:  生成个性化学习路径，包含步骤优先级和预估时间
回退:  按难度分配时长 (基础20min/进阶40min/高级60min)
```

#### 资源生成智能体 (ResourceGenerationAgent)

```
输入:  learning_path + resource_type + difficulty + student_profile
输出:  {resource_id, title, type, target_kp_ids, knowledge_points,
        difficulty, content(Markdown), estimated_learning_time}
功能:  生成 6 种类型资源 (lecture/quiz/ppt/case/review/test)
       每类有专用的指令模板和格式要求
回退:  生成骨架 Markdown 模板
```

#### 评测智能体 (AssessmentAgent)

```
输入:  test_results + learning_feedback + generated_resource + student_profile
输出:  {test_results, mastery_updates[{kp_id, old_mastery, new_mastery,
        change_reason}], feedback, suggestions, next_resource_recommendation}
功能:  分析测验结果/学习反馈，更新掌握度估计
回退:  基于准确率的规则 (>80%:+0.15, >60%:+0.05, <60%:-0.1)
```

#### 教师审核智能体 (TeacherReviewAgent)

```
输入:  generated_resource + course_objectives + difficulty_requirement
输出:  {quality_score(0-10), quality_checks[{check, passed, note}],
        risk_alerts[{level, message}], suggestions[], overall_comment}
功能:  6 维度质量评估 (准确性/完整性/逻辑性/规范性/可用性/难度适配)
       评分 < 7.0 触发 Revision 返工
回退:  5 项检查，4 通过 1 失败
```

### 3.4 状态持久化

```
InMemorySaver Checkpointer:
  - 使用 LangGraph 内置的内存 Checkpointer
  - 每个工作流通过 thread_id 标识
  - 支持暂停/恢复 (GET /api/agents/workflow/{run_id})
  - 每步结果自动落盘（内存中）
```

---

## 4. LLM 抽象层

### 4.1 设计

```
┌──────────────────────────────────────────┐
│            LLMGateway                     │
│  ┌────────────────────────────────────┐  │
│  │  _providers: Dict[str, BaseProvider] │  │
│  │                                      │  │
│  │  generate(messages, config)          │  │
│  │    → LLMCallResult                  │  │
│  └────────────────────────────────────┘  │
│                                          │
│  注册表:                                  │
│  ┌────────────────────────────────────┐  │
│  │  "mock"              → MockProvider │  │
│  │  "openai"            → OpenAIComp.. │  │
│  │  "openai_compatible" → OpenAIComp.. │  │
│  │  "minimax"           → MiniMaxProv. │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### 4.2 Provider 接口

```python
class BaseProvider:
    def generate(
        self,
        messages: List[Dict],     # [{"role": "user", "content": "..."}]
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMCallResult:
        ...

@dataclass
class LLMCallResult:
    content: str              # 响应内容
    model: str                # 模型名称
    provider: str             # Provider 名称
    input_tokens: int         # 输入 token 数
    output_tokens: int        # 输出 token 数
    total_tokens: int         # 总 token 数
    latency_ms: int           # 延迟 (毫秒)
    cost: float               # 费用 (USD)
    status: str               # "success" | "failed"
    error: Optional[str]      # 错误信息
```

### 4.3 三类 Provider

| Provider | 接口 | 适用场景 |
|----------|------|----------|
| **MockProvider** | 本地规则 | 开发/测试/演示，无 API 费用 |
| **OpenAICompatibleProvider** | POST /chat/completions | OpenAI / DeepSeek / Qwen / GLM 等 |
| **MiniMaxProvider** | POST /chat/completions | MiniMax M3 模型 |

---

## 5. RAG 检索增强

### 5.1 设计理念

**轻量级 RAG**，不依赖外部 Embedding API，使用 BM25 算法进行本地检索。

### 5.2 核心模块

```
┌─────────────────────────────────────────┐
│  rag_service.py                         │
│  get_context_for_agent(query, course_id, │
│      kp_name, top_k) → 格式化上下文      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  retriever.py                           │
│  CourseMaterialRetriever                 │
│  - BM25 算法 (k=1.5, b=0.75)            │
│  - 中文分词 (正则 + 停用词)              │
│  - 倒排索引 + 文档频率统计               │
│  - search(query, top_k, filter)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  document_loader.py                     │
│  - 13 个预置课程文档片段                  │
│  - 按知识点 (kp_name) 索引               │
│  - 覆盖课程 1：数据库系统原理             │
└──────────────────────────────────────────┘
```

### 5.3 BM25 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| k | 1.5 | 词频饱和参数 |
| b | 0.75 | 文档长度归一化 |

### 5.4 中文分词

```
正则分词: [一-鿿]+|[a-zA-Z0-9]+
停用词:   35 个常见中文虚词 (的/了/在/是/我/有/和/就/不/人/都/一/一个/上/也/很/到/说/要/去/你/会/着/没有/看/好/自己/这/他/她/它/们/那/些/还)
最小长度: 2 字符
```

---

## 6. 前端架构

### 6.1 目录结构

```
frontend/
├── index.html
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── .env.development
└── src/
    ├── main.tsx                      # ReactDOM 入口
    └── app/
        ├── App.tsx                   # RouterProvider
        ├── routes.tsx                # 全部路由定义
        ├── components/
        │   ├── Layout.tsx            # 三端布局 (学生/教师/管理员)
        │   └── ui/                   # 43 个 shadcn/ui 风格组件
        ├── pages/
        │   ├── Login.tsx
        │   ├── StudentDashboard.tsx
        │   ├── TeacherDashboard.tsx
        │   ├── AdminDashboard.tsx
        │   ├── AgentWorkbench.tsx     # 教师智能体工作台
        │   └── ...                    # 共 29 个页面组件
        ├── lib/
        │   ├── api.ts                # Axios 客户端
        │   └── api/                  # 18 个 API 模块
        ├── stores/
        │   └── auth.ts               # Zustand 认证状态
        └── styles/
            ├── index.css
            ├── tailwind.css
            └── theme.css
```

### 6.2 路由全景

```
/login                           → Login (无 Layout)

/ (Layout 包裹)
├── /student                     → StudentDashboard
│   ├── /student/profile         → StudentProfile
│   ├── /student/learning-path   → StudentLearningPath
│   ├── /student/tasks           → StudentTasks
│   ├── /student/resources       → ResourceLibrary
│   ├── /student/tutor           → StudentTutor
│   ├── /student/feedback        → LearningFeedback
│   └── /student/report          → LearningAnalytics
│
├── /teacher                     → TeacherDashboard
│   ├── /teacher/courses         → TeacherCourses
│   ├── /teacher/students        → StudentProfile
│   ├── /teacher/agent-workbench → AgentWorkbench
│   ├── /teacher/resources       → ResourceLibrary
│   ├── /teacher/review          → TeacherReview
│   ├── /teacher/tasks           → TeacherTasks
│   ├── /teacher/knowledge-base  → TeacherKnowledgeBase
│   └── /teacher/analytics       → LearningAnalytics
│
├── /admin                       → AdminDashboard
│   ├── /admin/users             → AdminUsers
│   ├── /admin/roles             → RolePermissionMap
│   ├── /admin/courses           → AdminCourses
│   ├── /admin/resources         → ResourceLibrary
│   ├── /admin/model-config      → AdminModelConfig
│   ├── /admin/agent-config      → AdminAgentConfig
│   ├── /admin/prompts           → AdminPrompts
│   ├── /admin/audit             → AdminAudit
│   ├── /admin/costs             → AdminCosts
│   ├── /admin/governance        → AdminGovernance
│   ├── /admin/logs              → AdminLogs
│   └── /admin/design-system     → DesignSystemUpdate
│
└── *                             → NotFound
```

### 6.3 三端布局

```
ROLE_CONFIG = {
  student: { brand: "智学工坊·学生", basePath: "/student", ... }
  teacher: { brand: "智学工坊·教师", basePath: "/teacher", ... }
  admin:   { brand: "智学工坊·管理", basePath: "/admin",   ... }
}

Layout 组件：
├── 侧边栏 (深色主题 #0F172A, 248px)
│   ├── 品牌 Header
│   ├── 状态小部件
│   ├── 分区导航菜单 (Section → NavItem[])
│   └── 角色权限指示器
├── 顶部 Header
│   ├── 搜索栏
│   ├── 角色切换按钮 (<Student | Teacher | Admin>)
│   ├── 通知铃铛
│   └── 用户下拉 (资料/登出)
└── <Outlet /> (路由内容区)
```

### 6.4 API 客户端

```
Axios Instance:
  baseURL:    /api (开发时 Vite Proxy 转发到 localhost:8000)
  timeout:    30s

Request Interceptor:
  → 从 localStorage 读取 eduagent_token
  → 注入 Bearer {token} 到 Authorization Header

Response Interceptor:
  → code === 0  → return data    (成功)
  → code !== 0  → reject(ApiError) (业务错误)
  → HTTP 401    → 清除 token, 跳转 /login
  → HTTP 403    → "无访问权限"
  → HTTP 404    → "请求地址不存在"
  → HTTP 5xx    → "服务器错误，请稍后重试"
  → Network Error → "网络错误，请检查网络连接"
```

### 6.5 状态管理

```typescript
// Zustand Store: useAuthStore
{
  token: string | null,
  user: UserInfo | null,
  loading: boolean,
  initialized: boolean,

  login(username, password) → UserInfo,
  logout() → void,
  fetchMe() → UserInfo | null,
  hasRole(role: "student" | "teacher" | "admin") → boolean,
}

// 持久化: localStorage key "eduagent-auth"
// 仅持久化 token 和 user 字段
```

### 6.6 组件库

| 类别 | 技术 |
|------|------|
| 主 UI 框架 | MUI v7 (Material Design) |
| 无头 UI | Radix UI (~25 个包: Dialog, DropdownMenu, Tabs, Accordion, ...) |
| 图标 | Lucide React, MUI Icons |
| 图表 | Recharts (ECharts 风格交互) |
| Toast | Sonner |
| 动画 | Motion (Framer Motion v12) |
| 表单 | React Hook Form |
| 拖拽 | React DnD |
| 主题 | next-themes (亮色/暗色切换) |

---

## 7. 数据库设计

### 7.1 表概览

**39 张表 + 5 个视图**，分为三个领域：

#### 核心业务表 (27 张)

| 表名 | 用途 |
|------|------|
| `users` | 用户表 (用户名, 密码哈希, 真实姓名, 学号, 邮箱) |
| `roles` | 角色表 (admin, teacher, project_leader, student_member) |
| `user_roles` | 用户-角色关联 |
| `permissions` | 权限表 (40 个权限码) |
| `role_permissions` | 角色-权限关联 |
| `projects` | 项目空间 |
| `project_members` | 项目成员 |
| `task_types` | 任务类型 (9 种) |
| `project_tasks` | 协作任务 |
| `task_branches` | 任务分支 |
| `task_outputs` | AI 输出版本 (支持版本链路) |
| `prompt_templates` | 提示词模板 |
| `prompt_versions` | 提示词版本 |
| `model_providers` | AI 模型供应商 |
| `ai_models` | AI 模型注册 |
| `api_configs` | API 密钥配置 (AES 加密存储) |
| `ai_invocations` | AI 调用记录 (审计表) |
| `review_requests` | 审核请求 |
| `output_reviews` | 输出审核 (多维度评分) |
| `issue_tags` | 问题标签 (10 个预置) |
| `output_issue_relations` | 输出-问题关联 |
| `output_comments` | 输出批注 |
| `adopted_outputs` | 采纳成果 |
| `merge_records` | 分支合并记录 |
| `cost_records` | 成本记录 (审计表) |
| `operation_logs` | 操作日志 (审计表) |
| `login_logs` | 登录日志 (审计表) |

#### A3 赛题专属表 (7 张)

| 表名 | 用途 |
|------|------|
| `courses` | 课程管理 (课程名, 代码, 授课教师) |
| `knowledge_points` | 知识点 (树形结构, 三级难度) |
| `student_profiles` | 学生画像 (学习目标, 偏好, 周学时) |
| `student_knowledge_mastery` | 知识点掌握度 (0-1) |
| `learning_resources` | 学习资源 (6 种类型, Markdown 内容) |
| `learning_feedbacks` | 学习反馈 (测验/自评/笔记/提问) |
| `learning_tasks` | 学习任务 (分配, 截止日期) |

#### 视图 (5 个)

| 视图 | 用途 |
|------|------|
| `v_artifacts` | 成果汇总视图 |
| `v_model_invocation_statistics` | 模型调用统计 |
| `v_pending_reviews` | 待审核列表 |
| `v_project_task_statistics` | 项目任务统计 |
| `v_user_permissions` | 用户权限汇总 |

### 7.2 通用设计模式

```sql
-- 所有表遵循统一模式
CREATE TABLE xxx (
    xxx_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ...           -- 业务字段
    is_deleted    TINYINT(1) NOT NULL DEFAULT 0,     -- 软删除
    deleted_at    DATETIME NULL,                      -- 删除时间
    deleted_by    INT UNSIGNED NULL,                   -- 删除人
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by    INT UNSIGNED NULL,
    updated_at    DATETIME NULL,
    updated_by    INT UNSIGNED NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 审计表 (ai_invocations, cost_records, operation_logs, login_logs)
-- 不做软删除，is_deleted/deleted_at 字段省略
```

---

## 8. 认证与安全

### 8.1 认证流程

```
1. 用户登录
   POST /api/auth/login {username, password}
   → 查询用户 → BCrypt 密码验证 → 查询角色
   → 生成 JWT (user_id, username, roles)
   → 写入 login_logs

2. 请求认证
   GET /api/xxx
   Header: Authorization: Bearer {token}
   → FastAPI Header 注入 → JWT 解析
   → get_current_user_dependency()
   → 验证成功：返回 user dict
   → 验证失败：抛出 UnauthorizedException

3. Token 管理
   前端: localStorage (eduagent_token)
   过期: 默认 24h (JWT_EXPIRE_MINUTES)
   登出: 仅清除 token，不维护黑名单 (不含敏感信息)
```

### 8.2 安全层

| 机制 | 实现 |
|------|------|
| 密码存储 | BCrypt ($2b$12$ 轮数) |
| Token | JWT HS256, 含 exp/iat 声明 |
| API Key | AES-256-GCM 加密, 密钥派生自 API_KEY_SECRET |
| 权限 | 40 个细粒度权限码 (project:create, task:view, model:invoke, ...) |
| 审计 | 完整操作日志 + 登录日志 + AI 调用记录 + 成本记录 |
| 软删除 | 所有业务表支持 is_deleted，可恢复 |
| 异常安全 | 生产环境不暴露内部错误细节 |

### 8.3 权限模型

```
Roles (4)          Permissions (40)
┌────────┐         ┌──────────────────────┐
│ admin  │──┬──────│ project:*            │
└────────┘  │      │ member:*             │
            │      │ task:*               │
┌────────┐  │      │ output:*             │
│ teacher│──┤      │ review:*             │
└────────┘  │      │ model:*              │
            │      │ template:*           │
┌──────────┐│      │ artifact:*           │
│ leader  │├───────│ user:*               │
└──────────┘│      │ log:*                │
            │      │ comment:*            │
┌────────┐  │      └──────────────────────┘
│ student│──┘
└────────┘

admin:    全部 40 个权限
teacher:  18 个权限 (含 model:invoke, template:manage, log:*)
leader:   24 个权限 (含 member:*, output:review, artifact:manage)
student:  15 个权限 (基础查询和创建)
```

---

## 9. 部署架构

### 9.1 Docker Compose 服务拓扑

```
services:

┌──────────────────────────────────────────────────────┐
│  PostgreSQL 16 + pgvector                             │
│  Port: 5432                                          │
│  DB: eduagent_studio                                 │
│  Init: ./database/pgvector/*.sql                     │
│  Volume: pgdata                                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Redis 7 Alpine                                      │
│  Port: 6379                                          │
│  Volume: redisdata                                   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  MinIO (对象存储)                                     │
│  API: 9000  Console: 9001                            │
│  User: eduagent / EduAgent2026MinIO                  │
│  Volume: miniodata                                   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Celery Worker                                       │
│  Build: backend/Dockerfile.celery                    │
│  Command: celery -A app.celery_app worker            │
│  Depends: Redis                                      │
│  Volume: ./backend:/app (bind mount)                 │
└──────────────────────────────────────────────────────┘

外部依赖 (非 Docker):
  ├── MySQL 5.7 (127.0.0.1:3306)
  └── FastAPI Server (python run.py, localhost:8000)
```

### 9.2 容器外服务

| 服务 | 运行方式 | 说明 |
|------|----------|------|
| FastAPI | `python run.py` | 本地开发启动，uvicorn hot reload |
| MySQL | Windows Service | 业务数据库，39 张表 |
| 前端 | `pnpm dev` | Vite Dev Server (5173)，API 代理到 8000 |

---

## 10. 数据流全景

### 10.1 同步工作流

```
┌────────┐    POST /api/agents/generate    ┌──────────┐
│ Frontend│ ───────────────────────────────→│  Router   │
│        │  {student_id, course_id, ...}   │  agents   │
│        │                                 └────┬─────┘
│        │                                      │
│        │                              ┌───────▼───────┐
│        │                              │ AgentService  │
│        │                              │ .generate()   │
│        │                              └───────┬───────┘
│        │                                      │
│        │                     ┌────────────────┼────────────────┐
│        │                     │                │                │
│        │              ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│        │              │ProfileRepo  │ │LearningRepo │ │FeedbackRepo│
│        │              │ 学生画像      │ │  知识点     │ │  学习历史    │
│        │              └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
│        │                     │                │                │
│        │                     └────────────────┼────────────────┘
│        │                                      │
│        │                              ┌───────▼───────┐
│        │                              │  run_workflow │
│        │                              │  (LangGraph)  │
│        │                              │               │
│        │                              │  ┌───────────┐│
│        │                              │  │ Supervisor││
│        │                              │  │  Router   ││
│        │                              │  └─────┬─────┘│
│        │                              │        │      │
│        │                              │  ┌─────▼─────┐│
│        │                              │  │ Diagnosis ││──→ LLM Gateway
│        │                              │  ├───────────┤│    ├─ Mock
│        │                              │  │ Planning  ││──→ ├─ OpenAI
│        │                              │  ├───────────┤│    └─ MiniMax
│        │                              │  │Generation ││──→
│        │                              │  ├───────────┤│    ┌─ RAG
│        │                              │  │Assessment ││──→ └─ BM25
│        │                              │  ├───────────┤│
│        │                              │  │Review     ││
│        │                              │  ├───────────┤│
│        │                              │  │Revision   ││ (loop ≤3)
│        │                              │  └───────────┘│
│        │                              └───────┬───────┘
│        │                                      │
│        │  {diagnosis, plan, resource,         │
│        │   assessment, review}                │
│  Frontend│ ←──────────────────────────────────┘
└────────┘
```

### 10.2 流式工作流 (SSE)

```
POST /api/agents/generate/stream

  ← event: data: {"node":"supervisor", "step":"init"}
  ← event: data: {"node":"diagnosis", "step":"diagnosis", "has_diagnosis":false}
  ← event: data: {"node":"diagnosis", "step":"diagnosis", "has_diagnosis":true}
  ← event: data: {"node":"planning", "step":"planning", "has_plan":true}
  ← event: data: {"node":"generation", "step":"generation", "has_resource":false}
  ← ... (重复直到完成)

  前端: 实时渲染每个步骤的进度和中间结果
```

### 10.3 请求生命周期

```
1. HTTP 请求到达 FastAPI
2. CORS 中间件处理
3. Router 匹配路径，执行依赖注入 (认证)
4. Pydantic 验证请求体
5. Service 执行业务逻辑
   a. Repository 查询/写入 MySQL
   b. LLM Gateway 调用 LLM (可选)
   c. RAG 检索器获取上下文 (可选)
6. 统一响应格式 {code, message, data}
7. 异常由全局 Exception Handler 捕获
```

---

## 附录

### A. 路由注册总览

| 前端路径 | 方法 | 后端实际路径 | 模块 |
|----------|------|-------------|------|
| `/api/auth/**` | * | `/api/auth/**` | auth |
| `/api/users/**` | * | `/api/users/**` | users |
| `/api/projects` | * | `/api` (路径偏差) | projects |
| `/api/tasks/**` | * | `/api/tasks/**` | tasks |
| `/api/task-types` | GET | `/api/task-types` | prompts |
| `/api/prompt-templates/**` | * | `/api/prompt-templates/**` | prompts |
| `/api/model-providers` | * | `/api/model-providers` | models |
| `/api/ai-models` | * | `/api/ai-models` | models |
| `/api/api-configs` | * | `/api/api-configs` | models |
| `/api/invocations/**` | * | `/api/invocations/**` | invocations |
| `/api/reviews/**` | * | `/api/reviews/**` | reviews |
| `/api/issue-tags` | GET | `/api/issue-tags` | reviews |
| `/api/statistics/**` | GET | `/api/statistics/**` | statistics |
| `/api/logs/**` | GET | `/api/logs/**` | logs |
| `/api/profiles/**` | * | `/api/profiles/**` | profiles |
| `/api/agents/**` | * | `/api/agents/**` | agents |
| `/api/learning/**` | * | `/api/learning/**` | learning, feedbacks, resources |
| `/api/storage/{id}` | GET | `/api/storage/{id}` | storage |

### B. 代码规模

| 维度 | 数量 |
|------|------|
| 后端 Python 源文件 | ~60+ |
| API 路由模块 | 17 |
| Service 模块 | 16 |
| Repository 模块 | 15 |
| API 端点总数 | 105 |
| 数据库表 | 39 |
| 数据库视图 | 5 |
| 前端页面组件 | 29 |
| 前端 UI 组件 | 43 |
| 前端 API 模块 | 18 |
| LLM Provider | 3 (Mock, OpenAI-Compatible, MiniMax) |
| 智能体 | 5 |
| 预置角色 | 4 |
| 预置权限 | 40 |
| SQL 迁移文件 | 11 |
| Docker 服务 | 4 |

---

*架构文档由 Claude Code 自动生成，基于代码静态分析和运行时验证。*
