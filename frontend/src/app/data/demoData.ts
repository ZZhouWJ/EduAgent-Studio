export const courses = [
  {
    id: "db-web",
    name: "数据库系统原理与 Web 项目实践",
    code: "DBS-2026-01",
    owner: "张老师",
    department: "计算机学院",
    students: 128,
    knowledgePoints: 16,
    resources: 642,
    mastery: 76,
    status: "活跃",
    updatedAt: "今天 10:24",
    classes: ["数据库 22-1 班", "数据库 22-2 班"],
    chapters: ["关系模型", "SQL 查询", "事务与并发控制", "Web 数据库项目实践"],
    weakPoints: ["事务隔离级别", "SQL 多表连接", "索引优化", "接口字段设计", "数据库范式"],
    summary: "围绕数据库基础、并发控制和 Web 项目实战，结合 RAG 知识库生成分层学习资源。",
  },
  {
    id: "ai-intro",
    name: "人工智能导论",
    code: "AI-2026-02",
    owner: "陈老师",
    department: "人工智能学院",
    students: 96,
    knowledgePoints: 22,
    resources: 318,
    mastery: 72,
    status: "活跃",
    updatedAt: "昨天 16:40",
    classes: ["智能 23-1 班"],
    chapters: ["搜索算法", "机器学习基础", "神经网络", "大模型应用"],
    weakPoints: ["梯度下降", "过拟合", "注意力机制", "评价指标", "提示词工程"],
    summary: "通过概念讲解、算法演示和案例实践帮助学生建立 AI 基础认知。",
  },
  {
    id: "se-practice",
    name: "软件工程课程实践",
    code: "SE-2026-03",
    owner: "刘老师",
    department: "软件学院",
    students: 84,
    knowledgePoints: 18,
    resources: 286,
    mastery: 69,
    status: "观察",
    updatedAt: "2 天前",
    classes: ["软件 22-3 班"],
    chapters: ["需求分析", "架构设计", "迭代管理", "质量保障"],
    weakPoints: ["需求边界", "接口契约", "测试用例", "项目排期", "评审记录"],
    summary: "面向团队项目实践，跟踪需求、任务、资源和学习反馈的闭环情况。",
  },
];

export const studentTasks = [
  {
    id: "task-isolation",
    title: "事务隔离级别基础理解",
    course: courses[0].name,
    knowledge: "事务隔离级别",
    reason: "最近测验对可重复读与串行化的边界理解不稳定。",
    estimate: "35 分钟",
    status: "进行中",
    progress: 64,
    resources: 3,
    section: "今日任务",
    objective: "用银行转账案例解释四类隔离级别，并能判断脏读、不可重复读和幻读。",
    quiz: "完成 5 道概念判断题，正确率达到 80%。",
    standard: "阅读讲义、完成测验并提交一条学习反馈。",
    agentReason: "学习画像显示事务概念掌握度 32%，且该知识点会影响后续并发控制实验。",
  },
  {
    id: "task-join",
    title: "SQL 多表连接补强练习",
    course: courses[0].name,
    knowledge: "SQL 多表连接",
    reason: "项目案例需要关联学生、课程和资源表。",
    estimate: "25 分钟",
    status: "进行中",
    progress: 48,
    resources: 2,
    section: "今日任务",
    objective: "掌握 inner join、left join 和条件过滤组合。",
    quiz: "完成 8 道查询改写题。",
    standard: "能独立写出课程资源推荐查询语句。",
    agentReason: "多表连接掌握度 46%，是学习事务案例前的依赖知识点。",
  },
  {
    id: "task-bank",
    title: "银行转账并发案例学习",
    course: courses[0].name,
    knowledge: "并发控制",
    reason: "把事务概念迁移到真实业务场景。",
    estimate: "20 分钟",
    status: "未开始",
    progress: 0,
    resources: 2,
    section: "本周任务",
    objective: "理解两个并发事务同时修改余额时的异常现象。",
    quiz: "完成案例排序题。",
    standard: "能说出锁、隔离级别和一致性的关系。",
    agentReason: "该案例能把抽象概念连接到 Web 数据库项目。",
  },
  {
    id: "task-fastapi",
    title: "FastAPI + PostgreSQL 综合实验准备",
    course: courses[0].name,
    knowledge: "Web 数据库项目实践",
    reason: "为课程项目冲刺准备接口和数据表设计。",
    estimate: "45 分钟",
    status: "已完成",
    progress: 100,
    resources: 4,
    section: "已完成任务",
    objective: "完成实验环境检查、接口字段对齐和数据库连接测试。",
    quiz: "提交实验准备清单。",
    standard: "能运行基础接口并完成一次查询。",
    agentReason: "上周项目实践反馈显示接口字段设计仍有易错点。",
  },
];

export const knowledgeDocuments = [
  { id: "doc-6", name: "第 6 章 事务与并发控制.pdf", type: "PDF", chunks: 28, coverage: 92, updatedAt: "今天 09:30", owner: "张老师" },
  { id: "doc-join", name: "SQL 多表连接讲义.md", type: "Markdown", chunks: 18, coverage: 87, updatedAt: "昨天 15:18", owner: "张老师" },
  { id: "doc-normal", name: "数据库范式课程 PPT.pptx", type: "PPT", chunks: 22, coverage: 76, updatedAt: "3 天前", owner: "张老师" },
  { id: "doc-api", name: "FastAPI 接口设计实验指导书.md", type: "Markdown", chunks: 26, coverage: 81, updatedAt: "4 天前", owner: "实验助教" },
  { id: "doc-bank", name: "银行转账并发实验案例.md", type: "Markdown", chunks: 34, coverage: 85, updatedAt: "上周", owner: "张老师" },
];

export const knowledgePoints = ["关系模型", "SQL 查询", "多表连接", "子查询", "数据库范式", "事务", "并发控制", "事务隔离级别", "索引优化", "Web 数据库项目实践"];

export const users = [
  { id: "u-001", name: "李明", username: "student01", role: "学生", department: "计算机学院", course: courses[0].name, lastLogin: "今天 08:42", status: "启用" },
  { id: "u-002", name: "王华", username: "student02", role: "学生", department: "计算机学院", course: courses[0].name, lastLogin: "昨天 21:10", status: "启用" },
  { id: "u-003", name: "张老师", username: "teacher01", role: "教师", department: "计算机学院", course: courses[0].name, lastLogin: "今天 09:01", status: "启用" },
  { id: "u-004", name: "陈老师", username: "teacher02", role: "教师", department: "人工智能学院", course: courses[1].name, lastLogin: "今天 11:18", status: "启用" },
  { id: "u-005", name: "王教授", username: "admin", role: "管理员", department: "教务中心", course: "全平台", lastLogin: "今天 07:55", status: "启用" },
  { id: "u-006", name: "赵强", username: "student03", role: "学生", department: "软件学院", course: courses[2].name, lastLogin: "5 天前", status: "停用" },
];

export const teacherTasks = [
  { id: "tt-1", title: "事务隔离级别基础讲义学习", course: courses[0].name, knowledge: "事务隔离级别", target: "数据库 22-1 班重点学生", due: "06-18 20:00", completion: 62, status: "进行中" },
  { id: "tt-2", title: "SQL 多表连接分层练习", course: courses[0].name, knowledge: "多表连接", target: "数据库 22-1 班", due: "06-17 22:00", completion: 74, status: "进行中" },
  { id: "tt-3", title: "综合实验准备清单", course: courses[0].name, knowledge: "Web 数据库项目实践", target: "项目实践组", due: "06-20 18:00", completion: 38, status: "低完成率" },
];

export const modelProviders = [
  { id: "mock", name: "Mock Provider", provider: "本地演示", abilities: ["文本生成", "流式输出"], status: "启用", latency: "86ms", calls: 428, cost: "¥0", key: "mk_****_local" },
  { id: "openai", name: "OpenAI-compatible", provider: "API 网关", abilities: ["文本生成", "代码生成", "多模态", "流式输出"], status: "启用", latency: "620ms", calls: 1320, cost: "¥96" },
  { id: "spark", name: "讯飞星火", provider: "讯飞开放平台", abilities: ["文本生成", "流式输出"], status: "启用", latency: "510ms", calls: 980, cost: "¥54" },
  { id: "deepseek", name: "DeepSeek", provider: "DeepSeek API", abilities: ["文本生成", "代码生成"], status: "观察", latency: "740ms", calls: 462, cost: "¥18" },
  { id: "qwen", name: "Qwen", provider: "DashScope", abilities: ["文本生成", "多模态"], status: "启用", latency: "580ms", calls: 516, cost: "¥24" },
  { id: "minimax", name: "MiniMax", provider: "MiniMax API", abilities: ["文本生成"], status: "停用", latency: "0ms", calls: 0, cost: "¥0" },
];

export const agents = [
  { id: "profile", name: "画像诊断智能体", model: "OpenAI-compatible", prompt: "学生画像抽取模板", enabled: true, calls: 420, success: 96, duration: "2.1s", duty: "聚合作业、测评和反馈，识别薄弱点。" },
  { id: "retrieve", name: "知识定位智能体", model: "讯飞星火", prompt: "防幻觉检查模板", enabled: true, calls: 388, success: 94, duration: "1.8s", duty: "检索课程知识库并返回引用证据。" },
  { id: "path", name: "路径规划智能体", model: "OpenAI-compatible", prompt: "学习路径规划模板", enabled: true, calls: 260, success: 93, duration: "2.8s", duty: "根据依赖关系生成个性化学习路径。" },
  { id: "resource", name: "资源生成智能体", model: "Qwen", prompt: "课程讲义生成模板", enabled: true, calls: 512, success: 91, duration: "4.6s", duty: "生成讲义、题库、案例和视频脚本。" },
  { id: "quiz", name: "测评生成智能体", model: "DeepSeek", prompt: "分层练习题生成模板", enabled: true, calls: 176, success: 89, duration: "3.9s", duty: "生成测验题、答案解析和错因标签。" },
  { id: "review", name: "教师审核辅助智能体", model: "讯飞星火", prompt: "教师审核建议模板", enabled: true, calls: 242, success: 95, duration: "2.4s", duty: "检查事实一致性、难度适配和引用覆盖。" },
];

export const promptTemplates = [
  { id: "p1", name: "学生画像抽取模板", agent: "画像诊断智能体", version: "v2.3", variables: ["student_profile", "quiz_records", "feedback"], editor: "王教授", updatedAt: "今天 09:12", enabled: true },
  { id: "p2", name: "学习路径规划模板", agent: "路径规划智能体", version: "v1.8", variables: ["weak_points", "knowledge_graph", "time_budget"], editor: "张老师", updatedAt: "昨天 18:30", enabled: true },
  { id: "p3", name: "课程讲义生成模板", agent: "资源生成智能体", version: "v3.1", variables: ["topic", "student_level", "evidence"], editor: "张老师", updatedAt: "今天 10:03", enabled: true },
  { id: "p4", name: "分层练习题生成模板", agent: "测评生成智能体", version: "v2.0", variables: ["topic", "difficulty", "rubric"], editor: "实验助教", updatedAt: "3 天前", enabled: true },
  { id: "p5", name: "代码案例生成模板", agent: "资源生成智能体", version: "v1.6", variables: ["framework", "schema", "learning_goal"], editor: "刘老师", updatedAt: "上周", enabled: true },
  { id: "p6", name: "教师审核建议模板", agent: "教师审核辅助智能体", version: "v2.5", variables: ["resource", "evidence", "risk_rules"], editor: "王教授", updatedAt: "昨天 11:44", enabled: true },
  { id: "p7", name: "防幻觉检查模板", agent: "知识定位智能体", version: "v2.2", variables: ["answer", "references", "threshold"], editor: "王教授", updatedAt: "今天 08:56", enabled: true },
];

export const auditLogs = [
  { id: "a1", time: "14:22:10", user: "张老师", role: "教师", agent: "资源生成智能体", model: "Qwen", input: 2380, output: 4180, latency: "4.8s", cost: "¥0.42", hit: "82%", safety: "通过", status: "成功" },
  { id: "a2", time: "14:18:36", user: "李明", role: "学生", agent: "AI 学习辅导", model: "OpenAI-compatible", input: 920, output: 1460, latency: "2.6s", cost: "¥0.18", hit: "88%", safety: "通过", status: "成功" },
  { id: "a3", time: "14:11:02", user: "student_0842", role: "学生", agent: "资源生成智能体", model: "Mock Provider", input: 120, output: 260, latency: "0.2s", cost: "¥0", hit: "0%", safety: "高频", status: "风险" },
  { id: "a4", time: "13:58:44", user: "陈老师", role: "教师", agent: "路径规划智能体", model: "讯飞星火", input: 1880, output: 2320, latency: "3.1s", cost: "¥0.28", hit: "76%", safety: "通过", status: "成功" },
];

export const costRows = [
  { course: courses[0].name, agent: "资源生成智能体", model: "Qwen", calls: 512, input: 380000, output: 620000, cost: 96, ratio: "38%" },
  { course: courses[0].name, agent: "AI 学习辅导", model: "OpenAI-compatible", calls: 820, input: 410000, output: 570000, cost: 84, ratio: "33%" },
  { course: courses[1].name, agent: "路径规划智能体", model: "讯飞星火", calls: 260, input: 160000, output: 240000, cost: 42, ratio: "16%" },
  { course: courses[2].name, agent: "教师审核辅助智能体", model: "DeepSeek", calls: 176, input: 120000, output: 180000, cost: 34, ratio: "13%" },
];

export const costTrend = [
  { day: "06-08", cost: 142, input: 32, output: 51 },
  { day: "06-09", cost: 168, input: 38, output: 62 },
  { day: "06-10", cost: 156, input: 35, output: 58 },
  { day: "06-11", cost: 196, input: 48, output: 72 },
  { day: "06-12", cost: 214, input: 54, output: 81 },
  { day: "06-13", cost: 186, input: 47, output: 70 },
];

export const operationLogs = [
  { id: "l1", time: "14:28:09", actor: "张老师", role: "教师", type: "资源日志", object: "事务隔离级别图解讲义", ip: "10.12.4.21", result: "成功", risk: "低" },
  { id: "l2", time: "14:20:14", actor: "王教授", role: "管理员", type: "系统配置日志", object: "模型配置 OpenAI-compatible", ip: "10.8.1.6", result: "成功", risk: "低" },
  { id: "l3", time: "14:16:53", actor: "李明", role: "学生", type: "画像日志", object: "学习反馈更新", ip: "10.31.8.93", result: "成功", risk: "低" },
  { id: "l4", time: "14:11:02", actor: "student_0842", role: "学生", type: "资源日志", object: "高频资源生成请求", ip: "10.31.8.101", result: "拦截", risk: "高" },
  { id: "l5", time: "13:58:44", actor: "陈老师", role: "教师", type: "审核日志", object: "人工智能导论练习题", ip: "10.12.9.18", result: "成功", risk: "低" },
];
