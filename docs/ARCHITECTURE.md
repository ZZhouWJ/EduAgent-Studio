# EduAgent Studio 实施架构

> 作用：描述当前 `main` 分支的真实运行架构和系统边界。
>
> 最近核对：2026-07-17

## 1. 架构目标

EduAgent Studio 是面向高校课程的三角色 Web 平台。系统需要同时满足：

1. 学生可以从对话入口完成画像、辅导、路径、任务、资源与反馈。
2. 教师可以管理课程知识、编排多智能体生成资源，并在发布前核验内容与证据。
3. 管理员可以治理用户、模型、Prompt、成本、风险和审计。
4. AI 输出必须经过课程证据、内容安全、教师审核与数据域权限。
5. 外部模型不可用时必须显式降级，不得伪造讯飞或其他供应商结果。

## 2. 运行拓扑

```text
浏览器
  └─ React 18 SPA
       ├─ React Router 角色路由
       ├─ Zustand 认证与用户状态
       ├─ Axios REST 请求
       └─ Fetch/EventSource 风格 SSE 事件流
            │
            ▼
       Nginx SPA 托管与 /api 反向代理
            │
            ▼
       FastAPI 应用
       ├─ Auth + RBAC + 课程数据域
       ├─ Router -> Service -> Repository
       ├─ LangGraph 资源生成图
       ├─ Tutor Supervisor + Tool Registry
       ├─ LLM Gateway + 内容安全
       └─ 课程 RAG + 证据链
            │
            ├─ MySQL 8.4：业务、知识、画像、审核、审计
            ├─ Redis 7.4：缓存、Celery broker/result
            ├─ SQLite：LangGraph checkpoint
            └─ APP_DATA_DIR：课程文件与导出产物

Celery Worker / Beat
  └─ 复用 FastAPI 同一配置与 MySQL/Redis/数据目录
```

Docker Compose 运行栈只包含 MySQL、Redis、Backend、Celery Worker、Celery Beat 和 Frontend。PostgreSQL、pgvector 和 MinIO 不是当前依赖。

## 3. 前端分层

| 层 | 目录 | 职责 |
| --- | --- | --- |
| 应用与路由 | `frontend/src/app` | 懒加载页面、布局、错误边界和角色导航 |
| 产品页面 | `frontend/src/app/pages` | 学生、教师、管理员的完整工作流 |
| 通用组件 | `frontend/src/app/components` | 布局、表格、弹窗、对话、Markdown 和可视化 |
| API 客户端 | `frontend/src/lib/api` | 按业务域封装请求与 TypeScript 数据类型 |
| 认证状态 | `frontend/src/stores/auth.ts` | 当前用户、角色、Token 恢复与登出 |
| 设计基础 | `frontend/src/styles` | Tailwind 主题、可访问焦点、响应式密度和打印样式 |

前端的权限控制用于导航和交互，不是安全边界。所有真实权限和课程归属都由后端重新校验。

### 3.1 角色空间

| 角色 | 主入口 | 主要界面 |
| --- | --- | --- |
| 学生 | `/student` | Tutor、首页、画像、路径、任务、资源、反馈、报告 |
| 教师 | `/teacher` | 课程、学生、知识库、智能体工作台、审核、任务、反馈、分析 |
| 管理员 | `/admin` | 用户、角色、课程、模型、智能体、Prompt、审计、成本、治理、日志 |

## 4. 后端分层

| 层 | 职责 | 规则 |
| --- | --- | --- |
| Router | 解析 HTTP、依赖注入、身份与请求类型 | 不直接编写业务 SQL |
| Service | 业务校验、事务编排、智能体调用和状态转换 | 必须在变更前检查角色与数据域 |
| Repository | 参数化 SQL、分页、批量查询和事务内写入 | 不包含 HTTP 概念或模型调用 |
| Agent/LLM | LangGraph 节点、Tutor 编排、Prompt、Provider 和安全扫描 | 统一经 LLM Gateway，记录调用与失败降级 |
| RAG | 文档解析、分块、检索、知识点关联和引用校验 | 只将真实数据库 chunk ID 写入证据链 |

FastAPI 当前注册约 140 个 REST 端点，核心教育域包括 `profiles`、`learning`、`knowledge`、`agents`、`resources`、`tutor`、`feedbacks`、`statistics` 和 `platform_settings`。`projects`、`tasks`、`artifacts` 和通用 `reviews` 为历史协作能力的兼容 API，不作为 A3 主演示链路。

## 5. 两条 AI 工作流

### 5.1 教师资源生成图

```text
输入学生 + 课程 + 知识点 + 目标 + 资源类型
  → Diagnosis Agent
  → Planning Agent
  → Resource Generation Agent + 课程 RAG
  → Assessment Agent
  → Teacher Review Agent
  → 质量低于阈值？
       ├─ 是：Revision → 重新审查，最多 3 次
       └─ 否：输出草稿、建议、证据与可信等级
```

LangGraph 使用 `run_id` 作为 `thread_id`。Checkpoint 写入 `APP_DATA_DIR/agent_workflows.sqlite3`，即使 Backend 进程重启也可通过原 `run_id` 读取状态。每个节点记录状态、耗时、返工次数和错误摘要。

`POST /api/agents/generate/stream` 通过 SSE 推送节点进度；完成后可将资源与 `resource_evidence_links` 在同一事务中保存。

### 5.2 学生 Tutor Supervisor

```text
学生问题 + 课程 + 画像
  → 课程知识检索
  → 规则预筛选候选工具
  → 模型 tool calling 或意图降级路由
  → 执行检索/讲解/题目/代码/思维导图/PPT/图像/语音工具
  → 汇总回答、引用、内容块和执行轨迹
```

Supervisor 最多执行 8 个步骤，每次工具调用都记录耗时与成功状态。如供应商不支持 tool calling，系统使用已注册的意图路由，不会把无效模型 JSON 当成工具指令执行。

## 6. LLM Gateway 与外部服务

### 6.1 Provider

| Provider | 作用 | 运行前提 |
| --- | --- | --- |
| Mock | 本地开发和自动化测试 | 生产环境强制禁用 |
| OpenAI-compatible | DeepSeek、Qwen 等兼容 Chat Completions 的服务 | Base URL、Model、API Key |
| MiniMax | 专用 Provider 适配 | 有效凭证与模型名 |
| 讯飞星火 | 星火聊天与 tool calling | APP ID、API Key、API Secret 和服务权限 |

管理端保存的 API Key 使用 AES-GCM 加密，解密只发生在运行时配置解析中。当数据库中存在已启用模型配置时，其优先级高于环境默认值。

### 6.2 内容安全

LLM Gateway 在 Provider 调用前扫描用户输入，在执行工具或返回结果前扫描模型正文与 tool arguments。当命中 prompt injection、高危指令、网络攻击滥用、自伤指令、未成年人性内容或凭证泄露时：

- 调用标记失败；
- 不返回命中原文；
- 不执行 tool call；
- 日志只记录风险类别。

管理端治理开关会同步到当前 Gateway 运行时。

## 7. 课程 RAG 与证据链

```text
教师上传 PDF/DOCX/PPTX/TXT/MD
  → 文件类型、容量与安全文件名验证
  → 文本解析与分块
  → 知识点候选关联
  → 教师确认 kp_chunk_links
  → BM25 + 中文 2-4 字 n-gram 检索
  → 生成内容引用 [引用:chunk_id]
  → 校验 chunk 存在、课程归属和知识点匹配
  → 写入 resource_evidence_links
```

CS301 种子材料提供 9 个章节和 9 条已确认知识点关联。没有有效证据时，资源可信等级降为 `draft`，不会生成不存在的 chunk ID。

## 8. 数据与事务边界

| 数据域 | 主要实体 | 一致性要求 |
| --- | --- | --- |
| 身份与权限 | users、roles、permissions、auth_sessions | 登出后会话立即失效，角色变更留审计 |
| 课程与知识 | courses、knowledge_points、course_materials、course_material_chunks | 课程所有权贯穿查询和变更 |
| 画像与学习 | student_profiles、student_knowledge_mastery、learning_task_progress | 对话应用与画像更新原子化，记录前后快照 |
| 资源与审核 | learning_resources、learning_resource_reviews、resource_evidence_links | 状态机、审核记录和证据写入不得部分成功 |
| Tutor 与反馈 | tutor_sessions、tutor_messages、learning_feedbacks | 学生只能读写自己的会话与反馈 |
| 治理与审计 | model_invocations、operation_logs、login_logs、platform_settings | 敏感密钥不回显，日志不记录明文凭证 |

数据库使用 PyMySQL 和参数化 SQL。需要多步写入的服务在单个 `get_db_transaction()` 上完成，任一步失败时回滚。

## 9. 认证、授权与隔离

1. 登录成功后生成 JWT，同时在 `auth_sessions` 保存可撤销会话。
2. 受保护 API 同时验证 Token 签名、过期时间、用户状态和会话状态。
3. 角色控制 admin/teacher/student 能力范围；课程数据域进一步限制教师只管理自己的课程，学生只访问已关联课程。
4. 资源详情、证据、工作流状态和存储文件都在返回前重新校验所有权。
5. 用户密码使用 BCrypt，输入长度限制在 BCrypt 安全边界内。

## 10. 故障和降级

| 失败 | 行为 |
| --- | --- |
| MySQL 不可用 | `/api/health/db` 返回 503，业务请求统一错误，不泄露连接凭证 |
| Redis 不可用 | `/api/health/redis` 返回 503，异步任务暂停，同步 API 依据业务可继续 |
| LLM 不可用 | Gateway 返回失败结果，不将空响应伪装成成功内容 |
| 讯飞多模态凭证缺失 | UI 显示不可用原因，不生成假图片或音频 URL |
| 课程证据不足 | 资源降级为草稿，要求教师补充材料或核验 |
| 单个 Agent 失败 | 步骤标记 failed，保留已完成 checkpoint 与通用错误摘要 |
| SSE 中断 | 已完成节点保留在 checkpoint，前端可查询 `run_id` 状态 |

## 11. 部署与配置

### 11.1 必需配置

| 配置 | 要求 |
| --- | --- |
| `DB_PASSWORD` | 通过 `.env` 或密钥管理注入 |
| `JWT_SECRET_KEY` | 生产环境至少 32 字符随机值 |
| `API_KEY_SECRET` | 至少 32 字符，与 JWT 密钥独立 |
| `CORS_ORIGINS` | 明确的 Web 来源列表，生产禁止 `*` |
| `LLM_PROVIDER` | 生产禁止 `mock` |
| 模型凭证 | 按 Provider 配置环境变量或管理端加密配置 |

### 11.2 网络边界

- 默认将 MySQL、Redis、Backend 和 Frontend 绑定到 `127.0.0.1`。
- 公网访问由 HTTPS 反向代理终止 TLS，不直接暴露 MySQL 和 Redis。
- 生产环境禁用 Swagger/Redoc，仅保留健康端点给调度器。
- 课程文件和 SQLite checkpoint 位于 `backend_data` 持久卷，不写入容器临时层。

## 12. 发布验证

```bash
cd backend
PYTHONPATH=. python -m unittest discover -s tests -v
python -m compileall -q app tests
pip check

cd ../frontend
npm run lint
npm run build
npm audit --omit=dev

curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/db
curl http://127.0.0.1:8000/api/health/redis
```

浏览器验收要覆盖三角色全路由、桌面与移动视口、SSE 进度、资源审核、证据查看和登出后会话失效。当前实测基线见 `docs/PROJECT_STATUS.md`，详细用例见 `docs/测试说明书.md`。

## 13. 架构约束

1. 不将早期 Vue/PostgreSQL/pgvector 计划恢复为当前实施架构。
2. 新的 AI 生成入口必须经过 LLM Gateway、内容安全、课程证据和教师审核。
3. 新的数据访问必须使用 Repository 和参数化 SQL，跨表变更必须明确事务边界。
4. 新的角色页面必须同时补齐后端权限和课程所有权测试。
5. 文档不得用“已接入”描述未配置真实凭证的外部服务验收结果。
