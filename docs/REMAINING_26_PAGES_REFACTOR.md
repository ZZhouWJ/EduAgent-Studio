# 剩余 26 页前端改造清单

> 范围：TeacherDashboard 已落地（基线）。本文覆盖其余 **26 个 .tsx 页面**的硬编码 const[] → 真后端派生 + 死按钮（`showToast("...TODO...")`）→ 真实动作的精确改动清单。
>
> 生成时间：2026-06-15 14:46 UTC+8
> 后端基线：`backend/database/seed_demo_data.py` 已跑通，登录用户名见下表。
> 演示账号：所有账号密码统一 `Pass@1234`（bcrypt `$2b$12$`）

---

## 0. 通用规则（所有页面都要套）

### 0.1 demo 账号表

| 角色 | username | real_name | user_id |
|---|---|---|---|
| 管理员 | `admin` | 系统管理员 | 33 |
| 老师 | `teacher_li` | 李建国 | 34 |
| 老师 | `teacher_wang` | 王雪 | 35 |
| 学生 | `student_zhang` | 张小明 | 36 |
| 学生 | `student_liu` | 刘洋 | 37 |
| 学生 | `student_chen` | 陈雨欣 | 38 |
| 学生 | `student_zhao` | 赵伟 | 39 |
| 学生 | `student_sun` | 孙佳 | 40 |
| 学生 | `student_zhou` | 周琪 | 41 |

> user_id 会在重跑 seed 时漂移（SET FOREIGN_KEY_CHECKS=0 也会让 AUTO_INCREMENT 增长），所以代码里**别硬编码 user_id**，统一走 `useAuthStore`。

### 0.2 已知的真实 API（可立即用）

| API 方法 | 路径 | 返回 | 用途 |
|---|---|---|---|
| `statisticsApi.overview()` | `/statistics/overview` | `StatisticsOverview` | 全局 KPI 计数 |
| `statisticsApi.learningOverview()` | `/statistics/learning-overview` | `LearningOverview` | 学习侧 KPI |
| `statisticsApi.weakKnowledgePoints(top_n)` | `/statistics/weak-knowledge-points` | `WeakKnowledgePoint[]` | 薄弱知识点 |
| `statisticsApi.masteryDistribution()` | `/statistics/mastery-distribution` | `MasteryDist[]` | 掌握度区间 |
| `statisticsApi.recentActivities({limit})` | `/statistics/recent-activities` | `RecentActivity[]` | 最近活动流 |
| `statisticsApi.modelCalls()` | `/statistics/model-calls` | `ModelCallStats[]` | 模型调用统计 |
| `statisticsApi.costs()` | `/statistics/costs` | `CostStats` | 成本 |
| `statisticsApi.reviews()` | `/statistics/reviews` | `ReviewStats` | 审核统计 |
| `statisticsApi.resourceTypeDistribution()` | `/statistics/resource-type-distribution` | `ResourceTypeDist[]` | 资源类型分布 |
| `statisticsApi.invocationTrend(days)` | `/statistics/invocation-trend` | `InvocationTrend[]` | 调用趋势 |
| `statisticsApi.reviewRateByCourse()` | `/statistics/review-rate-by-course` | `ReviewRateByCourse[]` | 按课程通过率 |
| `learningApi.listCourses()` | `/learning/courses` | `Course[]` | 学生可选课程 |
| `learningApi.listTasks({...})` | `/learning/tasks` | `{items, total}` | 学习任务 |
| `learningApi.getLearningPath(course_id)` | `/learning/courses/{id}/learning-path` | `LearningPathGraph` | 知识图谱 |
| `reviewsApi.getPending({...})` | `/reviews/pending` | `{items, total}` | 待审核资源 |
| `reviewsApi.getById(request_id)` | `/reviews/{id}` | `ReviewDetail` | 审核详情 |
| `reviewsApi.getIssueTags()` | `/issue-tags` | `IssueTag[]` | 问题标签 |
| `resourcesApi.list({...})` | `/learning/resources` | `{items, total}` | 学习资源 |
| `projectsApi.list({...})` | `/projects` | `{items, total}` | 项目列表 |
| `projectsApi.getTasks(project_id, {...})` | `/projects/{id}/tasks` | `{items, total}` | 项目的任务 |
| `projectsApi.getMembers(project_id)` | `/projects/{id}/members` | `ProjectMember[]` | 项目成员 |
| `feedbackApi.list({...})` | `/learning/feedbacks` | `{items, total}` | 反馈列表 |
| `feedbackApi.submit({...})` | `POST /learning/feedbacks` | – | 提交反馈（学生） |
| `usersApi.list({...})` | `/users` | `{items, total}` | 用户管理 |
| `usersApi.listRoles()` | `/roles` | `Role[]` | 角色列表 |
| `usersApi.listPermissions()` | `/permissions` | `Permission[]` | 权限列表 |
| `usersApi.updateStatus(id, status)` | `PUT /users/{id}/status` | – | 启停用户 |
| `usersApi.updateRoles(id, role_ids)` | `PUT /users/{id}/roles` | – | 改角色 |
| `promptsApi.getTaskTypes()` | `/task-types` | `PromptTaskType[]` | 任务类型 |
| `promptsApi.getTemplates({...})` | `/prompt-templates` | `{items, total}` | 提示词模板 |
| `promptsApi.getVersions(id)` | `/prompt-templates/{id}/versions` | `PromptVersion[]` | 版本历史 |
| `promptsApi.createTemplate(data)` | `POST /prompt-templates` | – | 新建模板 |
| `promptsApi.createVersion(id, data)` | `POST /prompt-templates/{id}/versions` | – | 新版本 |
| `promptsApi.activateVersion(tid, vid)` | `POST .../versions/{vid}/activate` | – | 激活版本 |
| `modelsApi.getProviders()` | `/model-providers` | `ModelProvider[]` | 模型服务商 |
| `modelsApi.getModels({...})` | `/ai-models` | `{items, total}` | AI 模型 |
| `modelsApi.getApiConfigs({...})` | `/api-configs` | `{items, total}` | API 配置 |
| `agentsApi.listAgents()` | `/agents/list` | `Agent[]` | 智能体列表 |
| `agentsApi.generate(data)` | `POST /agents/generate` | `WorkflowResult` | 启动工作流 |
| `agentsApi.getWorkflowStatus(run_id)` | `/agents/workflow/{id}` | `WorkflowResult` | 查工作流状态 |
| `agentsApi.saveResource(data)` | `POST /agents/save-resource` | – | 保存为资源 |
| `invocationsApi.getInvocations({...})` | `/invocations` | `{items, total}` | 调用记录 |
| `invocationsApi.getInvocationById(id)` | `/invocations/{id}` | `InvocationDetail` | 调用详情 |
| `logsApi.operationLogs({...})` | `/logs/operation` | `{items, total}` | 操作日志 |
| `logsApi.loginLogs({...})` | `/logs/login` | `{items, total}` | 登录日志 |
| `artifactsApi.list(project_id, {...})` | `/projects/{id}/artifacts` | `{items, total}` | 采纳成果 |
| `profilesApi.list({...})` | `/profiles/` | `{items, total}` | 学生画像列表 |
| `profilesApi.getById(id)` | `/profiles/{id}` | `ProfileDetail` | 画像详情 |

> ⚠️ **没有的端点**（后端没做，需要用 `setState` 改前端状态或留"演示中"占位）：`/agents/workflow/{id}/steps`、`/admin/system-services`（健康状态）、`/learning/path/{student_id}/today`、`/governance/risk-queue`、`/admin/audit/logs`。

### 0.3 死按钮改造模板

**Before**：
```tsx
<button onClick={() => showToast("智能体配置已保存（编辑功能 TODO）")}>保存</button>
```

**After（按目标分三类）**：

| 目标 | 模板 |
|---|---|
| 跳路由 | `<Link to="/path" className="...">{label}</Link>` 或 `navigate("/path")` |
| 调真 API | `const mut = useApi(() => agentsApi.generate({...}), []); ... onClick={() => mut.refetch()}` |
| 弹 Modal | `setOpen(true)` 触发已声明的 `useState` |
| 纯展示 | 删 onClick，让它就是个 div |

**4 个标准 onClick 模式**：

```tsx
// 模式 A：跳路由（最高频）
import { useNavigate } from "react-router";
const navigate = useNavigate();
<button onClick={() => navigate("/teacher/review")} className={primaryButton}>进入审核</button>

// 模式 B：调用 mutating API（POST/PUT/DELETE）
const { refetch: submitReview } = useApi(
  () => tasksApi.submitReview(outputId, { submit_note: "..." }),
  [],
);
<button onClick={async () => { try { await submitReview(); notify.success("已提交"); } catch (e) { notify.error(String(e)); } }}>提交审核</button>

// 模式 C：触发弹窗
const [open, setOpen] = React.useState(false);
<button onClick={() => setOpen(true)}>设置预算</button>
{open && <BudgetModal onClose={() => setOpen(false)} />}

// 模式 D：触发 refetch
const reviews = useApi(() => reviewsApi.getPending({ page_size: 10 }), []);
<button onClick={() => reviews.refetch()}>刷新</button>
```

### 0.4 ui-ux-pro-max critical 规则（只动这 6 条）

| 规则 | 改法 |
|---|---|
| **触摸目标 ≥44pt** | 所有 `<button>` `<a>` 加 `min-h-[44px]` 或 `min-h-11`（已是 44）。 `<Link>` 没 padding 的补 `py-2` |
| **图标统一 Lucide** | 项目已经在用 Lucide React ✅，**禁用 emoji 当图标** |
| **对比度 4.5:1** | 灰字 `text-slate-400` 改 `text-slate-500`；`text-slate-300` 改成 `text-slate-600` |
| **cursor-pointer** | 所有可点元素加 `cursor-pointer`（在 Tailwind 项目里用 `className` 已有 `transition`，检查无 `cursor-default`） |
| **焦点可见** | 检查 `focus:outline-none` 后面必须有 `focus:ring-2` |
| **响应式 4 档** | 检查关键页 grid `grid-cols-4` 在 mobile 是否 `grid-cols-1`（用 `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`） |

### 0.5 主数据 hook helper（建议加在 `lib/hooks.ts`）

```ts
// frontend/src/lib/hooks.ts (新建)
import { useApi } from "./useApi";
import { statisticsApi, learningApi, reviewsApi } from "./api";

/** 顶部 KPI 卡片 5 件套，所有 dashboard 复用。 */
export function useDashboardKpis() {
  const overview = useApi(() => statisticsApi.overview(), []);
  const learning = useApi(() => statisticsApi.learningOverview(), []);
  const weak = useApi(() => statisticsApi.weakKnowledgePoints(5), []);
  const mastery = useApi(() => statisticsApi.masteryDistribution(), []);
  const reviews = useApi(() => reviewsApi.getPending({ page_size: 5 }), []);
  return { overview, learning, weak, mastery, reviews };
}
```

---

## 1. StudentDashboard.tsx

**文件**：`frontend/src/app/pages/StudentDashboard.tsx`  
**角色**：student  
**硬编码 const[]**：`STUDENT_STATS` (L23) / `TODAY_PATH` (L31) / `RESOURCES` (L39)

### 1.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `STUDENT_STATS` | 5 个硬编码 KPI 卡片 | 用 `useApi` 拉 5 个真实数据源 |
| `TODAY_PATH` | 5 个假学习任务 | 改用 `learningApi.listTasks({ page_size: 5 })` 取学生自己的任务 |
| `RESOURCES` | 4 个假资源卡片 | 改用 `resourcesApi.list({ page_size: 4 })` |
| 顶部"同学"打招呼 | L66 附近 `const studentName = "同学"` | 改成 `useAuthStore.user?.real_name ?? "同学"` |
| L69 课程名硬编码 | `"数据库系统原理与 Web 项目实践"` | 用 `learningApi.listCourses()` 第一个 course.name |

### 1.2 模板

```tsx
// imports 新增
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi, statisticsApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

// 删除 L23 STUDENT_STATS / L31 TODAY_PATH / L39 RESOURCES 三个 const

// 组件内 L54 之后
const user = useAuthStore((s) => s.user);
const greetingName = user?.real_name ?? "同学";
const { data: courses } = useApi(() => learningApi.listCourses(), []);
const { data: tasks } = useApi(() => learningApi.listTasks({ page_size: 5 }), []);
const { data: resources } = useApi(() => resourcesApi.list({ page_size: 4 }), []);
const { data: statsData } = useApi(() => statisticsApi.learningOverview(), []);

const courseName = courses?.[0]?.name ?? "（未选课）";
const studentStats = [
  { label: "综合掌握度", value: statsData ? `${Math.round(statsData.avg_mastery * 100)}%` : "—", hint: "实时统计", icon: BarChart3, tone: "blue" },
  { label: "待完成任务", value: String(tasks?.items?.filter(t => t.status !== "completed").length ?? 0), hint: `今日 ${tasks?.items?.filter(t => t.status === "in_progress").length ?? 0} 项`, icon: CheckCircle2, tone: "purple" },
  { label: "本周反馈", value: String(statsData?.feedback_count ?? 0), hint: "近 7 天", icon: Timer, tone: "emerald" },
  { label: "课程资源", value: String(resources?.total ?? 0), hint: "已发布", icon: FileText, tone: "orange" },
  { label: "薄弱知识点", value: String(statsData?.active_tasks ?? 0), hint: "优先处理", icon: Target, tone: "red" },
];

const todayPath = (tasks?.items ?? []).map((t) => ({
  title: t.title,
  time: t.due_date ? new Date(t.due_date).toLocaleDateString() : "无截止",
  reason: t.description || "—",
  type: t.type,
  status: t.status === "completed" ? "已完成" : t.status === "in_progress" ? "进行中" : "待完成",
}));

const resourcesCards = (resources?.items ?? []).map((r) => ({
  id: r.resource_id,
  title: r.resource_title,
  type: r.resource_type,
  minutes: r.difficulty,
  confidence: r.status === "approved" ? "已认证" : r.status,
  icon: FileText,
}));
```

### 1.3 死按钮

- 顶部 4 个"开始提问/查看全部"已经是 `<Link>` ✅  
- 资源卡片：把 `<div>` 包成 `<Link to={\`/student/resources/\${r.resource_id}\`}>` 真正跳转

---

## 2. AdminDashboard.tsx

**文件**：`frontend/src/app/pages/AdminDashboard.tsx`  
**角色**：admin  
**硬编码 const[]**：`SERVICES` (L8) / `RISKS` (L16) / `ENTRY` (L23)

### 2.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `SERVICES` | 5 个假健康状态 | **保留为默认占位**，加 5 秒轮询 `/api/health` 和 `/api/health/db` 覆盖状态 |
| `RISKS` | 4 行假数据 | 从 `statisticsApi.reviews()` 的 `top_issue_tags` 派生 |
| `ENTRY` | 5 个入口卡片（已经是 Link） | ✅ 保留不变 |

### 2.2 模板

```tsx
// imports
import { useApi } from "@/lib/useApi";
import { statisticsApi, ... } from "@/lib/api";

// SERVICES 保留为初始值，加 useEffect 轮询
const [services, setServices] = React.useState([
  { name: "后端服务", status: "检测中", desc: "—", icon: Server, key: "api" },
  { name: "数据库", status: "检测中", desc: "—", icon: Database, key: "db" },
  { name: "Redis", status: "未知", desc: "无独立健康端点", icon: ActivitySquare, key: "redis" },
  { name: "MinIO", status: "未知", desc: "无独立健康端点", icon: HardDrive, key: "minio" },
  { name: "模型服务", status: "—", desc: "—", icon: Bot, key: "llm" },
]);

React.useEffect(() => {
  const tick = async () => {
    setServices((prev) => prev.map((s) => {
      if (s.key === "api") return { ...s, status: "检测中", desc: "—" };
      return s;
    }));
    try {
      const r1 = await fetch("/api/health");
      const j1 = await r1.json();
      setServices((prev) => prev.map((s) => s.key === "api" ? { ...s, status: j1.code === 0 ? "正常" : "异常", desc: j1.data?.env ?? "—" } : s));
    } catch { /* 保持 */ }
    try {
      const r2 = await fetch("/api/health/db");
      const j2 = await r2.json();
      setServices((prev) => prev.map((s) => s.key === "db" ? { ...s, status: j2.code === 0 ? "正常" : "异常", desc: j2.code === 0 ? `v${j2.data?.server_version ?? "—"}` : "连接失败" } : s));
    } catch { /* 保持 */ }
  };
  tick();
  const h = setInterval(tick, 30000);
  return () => clearInterval(h);
}, []);

// RISKS → 真派生
const { data: reviews } = useApi(() => statisticsApi.reviews(), []);
const riskItems = (reviews?.top_issue_tags ?? []).slice(0, 4).map((t) => [
  `高频问题标签：${t.tag_name}`,
  String(t.count),
  t.severity === "high" ? "高风险" : t.severity === "medium" ? "中风险" : "低风险",
]);
// 兜底：reviews 还没回来时
const risks = riskItems.length > 0 ? riskItems : [
  ["尚无问题标签", "0", "等待数据"],
];
```

### 2.3 死按钮

- L138 附近的"查看明细"如果是 `<button>` 改成 `<Link to="/admin/audit">`  
- L150 "查看全部" 已经是 `<Link>` ✅

---

## 3. AdminCosts.tsx

**文件**：`frontend/src/app/pages/AdminCosts.tsx`  
**角色**：admin  
**硬编码 const[]**：`DEMO_COURSES` (L8) / `DEMO_MODELS` (L9)

### 3.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `DEMO_COURSES` | 3 行假课程名 | 用 `learningApi.listCourses()` 派生 |
| `DEMO_MODELS` | 4 行假模型名 | 用 `modelsApi.getModels()` 派生 |

### 3.2 模板

```tsx
const { data: coursesData } = useApi(() => learningApi.listCourses(), []);
const { data: modelsData } = useApi(() => modelsApi.getModels({ page_size: 50 }), []);
const courseOptions = ["全部课程", ...(coursesData ?? []).map(c => c.name)];
const modelOptions = ["全部模型", ...(modelsData?.items ?? []).map(m => m.display_name)];
```

把 L8/L9 两个 const 完全删除。

### 3.3 死按钮

- "设置预算提醒" (L51 附近) — 后端无 budget 端点 → 改成弹本地 Modal（已声明 `open` state），输入金额后 `notify.success("已保存预算提醒 (${amount} 元)")`
- "导出报表" — `notify.info("已生成 CSV 导出 (mock)")` + 启动文件下载（用 `Blob` 造个示例 CSV）  
- "保存提醒" (L95) — `setOpen(false); notify.success("已保存")`

---

## 4. AdminGovernance.tsx

**文件**：`frontend/src/app/pages/AdminGovernance.tsx`  
**角色**：admin  
**硬编码 const[]**：`GOVERNANCE_RULES` (L6) / `RISK_QUEUE` (L13)

### 4.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `GOVERNANCE_RULES` | 4 行治理阈值 | 保留为产品配置常量（这些是平台规则，**不应来自数据库**），加 `可编辑` 按钮触发 Modal |
| `RISK_QUEUE` | 4 个假风险事项 | 派生自 `reviewsApi.getPending()` + `statisticsApi.reviews()` 的 `top_issue_tags` |

### 4.2 模板

```tsx
// 保留 GOVERNANCE_RULES 不动（这些是平台规则）

const { data: pendingReviews } = useApi(() => reviewsApi.getPending({ page_size: 4 }), []);
const { data: reviewsStats } = useApi(() => statisticsApi.reviews(), []);

const riskQueue = (pendingReviews?.items ?? []).map((p) => ({
  id: p.request_id,
  title: p.output_title,
  level: reviewsStats?.top_issue_tags?.find(t => t.severity === "high") ? "高风险" : "中风险",
  owner: p.submitter_real_name || p.submitter_username,
  reason: p.submit_note || "AI 生成内容待人工复核",
}));
// 兜底
const finalRiskQueue = riskQueue.length > 0 ? riskQueue : [
  { id: 0, title: "暂无待办风险事项", level: "—", owner: "—", reason: "等待数据" },
];
```

### 4.3 死按钮

- 治理规则卡片的"调整阈值"按钮：`notify.info("阈值编辑（演示模式）")`  
- 风险卡片的"处理"按钮：`navigate(\`/admin/audit?request=\${risk.id}\`)`

---

## 5. AgentWorkbench.tsx

**文件**：`frontend/src/app/pages/AgentWorkbench.tsx`  
**角色**：teacher / admin  
**硬编码 const[]**：`RESOURCE_TYPES` (L32) / `AGENT_STEPS` (L35) / `EVIDENCE` (L94) / `LOGS` (L101)

### 5.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `RESOURCE_TYPES` | 6 个资源类型 | 改用 `learningApi.listCourses()` 第一个课程 + 默认 6 个类型作为下拉 |
| `AGENT_STEPS` | 7 个假工作流步骤 | 派生自 `agentsApi.listAgents()` + 实时状态从 `agentsApi.getWorkflowStatus()` |
| `EVIDENCE` | 4 行假证据 | 派生自 `learningApi.getLearningPath(course_id)` 的 nodes |
| `LOGS` | 4 行假日志 | 用 `useState` 维护最近 4 条消息，触发 `runWorkflow` 时 push |

### 5.2 模板

```tsx
const [logs, setLogs] = React.useState<string[]>([]);
const { data: agents } = useApi(() => agentsApi.listAgents(), []);
const { data: courses } = useApi(() => learningApi.listCourses(), []);
const courseId = courses?.[0]?.id ?? 1;
const { data: path } = useApi(
  () => courseId ? learningApi.getLearningPath(courseId) : Promise.resolve(null),
  [courseId],
);

const resourceTypes = ["课程讲义", "思维导图", "分层练习题", "代码实操案例", "PPT 大纲", "视频/动画脚本"];
const agentSteps = (agents ?? []).map((a, i) => ({
  id: a.id,
  name: a.name,
  status: i === 0 ? "已完成" : i === 1 ? "运行中" : "等待中",
  summary: a.description,
  icon: Bot,
  state: i === 0 ? "done" : i === 1 ? "running" : "waiting",
  evidence: "",
}));

const evidence = (path?.nodes ?? []).slice(0, 4).map((n) => ({
  title: `${n.kp_code}: ${n.kp_name}`,
  match: `${Math.round((n.mastery_level ?? 0) * 100)}%`,
}));
```

### 5.3 死按钮

- "运行工作流" / "开始生成"：`agentsApi.generate(...)` 启动 → `setLogs([...logs, \`步骤 \${i} 完成\`])` 模拟步骤
- "保存为草稿"：`agentsApi.saveResource({...})` → `notify.success("已保存到资源库")`
- "复制提示词"：写到剪贴板 `navigator.clipboard.writeText(content)` → `notify.success("已复制")`
- "查看资源"：`navigate(\`/teacher/resources\`)` 

---

## 6. LearningAnalytics.tsx

**文件**：`frontend/src/app/pages/LearningAnalytics.tsx`  
**角色**：teacher / student  
**硬编码 const[]**：`PIE_DATA` (L5) / `LINE_DATA` (L12) / `BAR_DATA` (L17)

### 6.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `PIE_DATA` | 4 个假资源类型分布 | 用 `statisticsApi.resourceTypeDistribution()` |
| `LINE_DATA` | 7 天假调用量 | 用 `statisticsApi.invocationTrend(7)` |
| `BAR_DATA` | 5 个假掌握度 | 用 `statisticsApi.weakKnowledgePoints(5)` |

### 6.2 模板

```tsx
import { useApi } from "@/lib/useApi";
import { statisticsApi } from "@/lib/api";

const { data: resourceDist } = useApi(() => statisticsApi.resourceTypeDistribution(), []);
const { data: invocationTrend } = useApi(() => statisticsApi.invocationTrend(7), []);
const { data: weakKps } = useApi(() => statisticsApi.weakKnowledgePoints(5), []);

const RESOURCE_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#06b6d4'];
const pieData = (resourceDist ?? []).map((r, i) => ({
  name: r.type_name,
  value: r.count,
  color: RESOURCE_COLORS[i % RESOURCE_COLORS.length],
}));
const lineData = (invocationTrend ?? []).map((d) => ({
  name: d.date.slice(5),  // MM-DD
  calls: d.invocation_count,
}));
const barData = (weakKps ?? []).map((w) => ({
  name: w.kp_name,
  score: Math.round(w.avg_mastery * 100),
}));
```

---

## 7. Login.tsx

**文件**：`frontend/src/app/pages/Login.tsx`  
**角色**：所有  
**硬编码 const[]**：`FLOW` (L21) / `ROLE_ENTRIES` (L23)

### 7.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `FLOW` | 7 步流程图 | 保留（产品 UI 元素） |
| `ROLE_ENTRIES` | 3 个角色 demo 账号 | **更新为新 seed 账号** |

### 7.2 模板

把 L23-L60 的 `ROLE_ENTRIES` 整块替换为：

```tsx
const ROLE_ENTRIES = [
  {
    role: "管理员",
    desc: "全平台管理、用户/角色、模型/智能体配置、调用审计与成本",
    account: "admin / Pass@1234",
    path: () => loginAndGo("admin", "Pass@1234"),
    icon: ShieldCheck,
    cls: "bg-red-50 text-red-700 ring-red-100",
  },
  {
    role: "教师体验",
    desc: "管理课程、生成资源、审核 AI 内容和查看教学分析",
    account: "teacher_li / Pass@1234",
    path: () => loginAndGo("teacher_li", "Pass@1234"),
    icon: Users,
    cls: "bg-purple-50 text-purple-700 ring-purple-100",
  },
  {
    role: "学生体验",
    desc: "查看个性化学习路径、推荐资源和学习反馈",
    account: "student_zhang / Pass@1234",
    path: () => loginAndGo("student_zhang", "Pass@1234"),
    icon: GraduationCap,
    cls: "bg-blue-50 text-blue-700 ring-blue-100",
  },
];

// 加 helper（在组件外）
async function loginAndGo(username: string, password: string) {
  try {
    const user = await useAuthStore.getState().login(username, password);
    const target = user.roles.includes("admin") ? "/admin"
      : user.roles.includes("teacher") ? "/teacher"
      : user.roles.includes("student_member") ? "/student" : "/";
    window.location.href = target;
  } catch (e) {
    notify.error("登录失败：" + String(e));
  }
}
```

### 7.3 死按钮

- "立即体验"按钮：调用上面的 `loginAndGo(...)`（已带 `await`）
- L218 `href="#"` 的内联链接：换成 `<Link to="/docs">` 或 `<a href="/docs" target="_blank">`

---

## 8. RolePermissionMap.tsx

**文件**：`frontend/src/app/pages/RolePermissionMap.tsx`  
**角色**：admin  
**硬编码 const[]**：`PERMISSIONS` (L5)

### 8.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| `PERMISSIONS` | 4 个角色的可见/隐藏功能列表 | 派生自 `usersApi.listRoles()` + `usersApi.listPermissions()` |

### 8.2 模板

```tsx
const { data: roles } = useApi(() => usersApi.listRoles(), []);
const { data: perms } = useApi(() => usersApi.listPermissions(), []);

const permissionsView = (roles ?? []).map((r) => ({
  role: r.role_name,
  tone: "blue",
  icon: GraduationCap,  // 按 role_code 选不同图标
  visible: (perms ?? []).slice(0, 8).map(p => p.permission_name),
  hidden: ["用户管理", "系统模型成本", "全平台调用审计"].filter(() => r.role_code !== "admin"),
  principle: roleHint(r.role_code),
}));

function roleHint(code: string) {
  return {
    student_member: "陪伴感、路径感、学习目标清晰。",
    project_leader: "项目协作、任务推进、成果采纳。",
    teacher: "诊断、生成、审核闭环。",
    admin: "全平台治理与监控。",
  }[code] ?? "—";
}
```

### 8.3 死按钮

- 每张卡片的"查看权限矩阵" → `navigate(\`/admin/users?role=\${r.role_id}\`)`

---

## 9. AdminAgentConfig.tsx

**文件**：`frontend/src/app/pages/AdminAgentConfig.tsx`  
**角色**：admin  
**硬编码 const[]**：（无顶层 const）— 但**有大量 `showToast` 死按钮**

### 9.1 改动

| 块 | 当前 | 改成 |
|---|---|---|
| L43 "启用状态：TODO" | `showToast(...)` 占位 | 改 `useState` 维护 enabled 状态，toggle 时 `setAgents(... → {enabled: !agent.enabled})` + `notify.success("已切换")` |
| L48 "测试运行工作流" | `showToast` | `agentsApi.listAgents()` 校验连通性 → `notify.info("N 个智能体在线")` |
| L74 "日志" | `showToast` | 弹本地 Modal 显示假日志（用 `useState`） |
| L95 "保存" | `showToast("...TODO...")` | 当前后端无 update 端点 → 保留 `notify.success("已保存（演示模式）")` + **移除"编辑功能 TODO"字样** |

### 9.2 模板

```tsx
// 启用/停用：纯前端状态
const [agents, setAgents] = React.useState(initialAgents);
const toggle = (id: string) => {
  setAgents(prev => prev.map(a => a.id === id ? { ...a, enabled: !a.enabled } : a));
  notify.success("状态已更新");
};

// 测试运行
const runTest = async () => {
  const list = await agentsApi.listAgents();
  notify.info(`已连接 ${list.length} 个智能体`);
};

// 保存
const save = () => {
  setOpen(false);
  notify.success("智能体配置已保存（演示模式）");
};
```

---

## 10. AdminUsers.tsx

**文件**：`frontend/src/app/pages/AdminUsers.tsx`  
**角色**：admin  
**硬编码 const[]**：（无）

### 10.1 改动

- 把表里的所有假用户行替换为 `useApi(() => usersApi.list({ page_size: 50 }))`
- "启用/停用"按钮 → `usersApi.updateStatus(user_id, status)` + refetch
- "编辑角色" → 弹 Modal + `usersApi.updateRoles(user_id, role_ids)`
- "新增用户" → 弹 Modal（演示模式，**后端 users 路由** 没看到 create；用 `notify.success("已创建（演示模式）")`）

---

## 11. AdminCourses.tsx

**文件**：`frontend/src/app/pages/AdminCourses.tsx`  
**角色**：admin  
**硬编码 const[]**：（无）

### 11.1 改动

- 课程列表 → `learningApi.listCourses()`（注意 `learningApi` 是**学生侧**的，可能要直接查 `courses` 表，**先尝试 learningApi，不行的话后端加 `coursesApi`**）
- "分配负责人" L115 → 弹 Modal + dropdown 选 teacher → `notify.success("已分配")`  
- "查看课程资源" L116 → `navigate(\`/student/resources?course=\${courseId}\`)`  
- "查看课程知识库" L117 → `navigate(\`/teacher/knowledge-base?course=\${courseId}\`)`  
- "更新状态" L118 → 弹 Modal 改 status → `notify.success("已更新")`（**后端无 update 端点**，演示模式）  
- "运行建设巡检" L52 → 调 `/api/health/db` + `/api/health` → `notify.info("巡检完成")`

> ⚠️ **后端缺 `coursesApi.list/update`**，需要：
> ```python
> # backend/app/routers/courses.py
> @router.get("")  → list
> @router.put("/{id}")  → update status
> ```
> 这是必须的 5 行后端补充。

---

## 12. AdminPrompts.tsx

**文件**：`frontend/src/app/pages/AdminPrompts.tsx`  
**角色**：admin  
**硬编码 const[]**：（无）

### 12.1 改动

- 模板列表 → `promptsApi.getTemplates({ page_size: 50 })`
- "新建模板" → `promptsApi.createTemplate({...})` + refetch
- "编辑模板" → 弹 Modal + `promptsApi.updateTemplate(id, {...})` 
- "版本历史" → `promptsApi.getVersions(template_id)` + 弹 Modal
- "复制模板" → `navigator.clipboard.writeText(JSON.stringify(template, null, 2))` + `notify.success("已复制")`
- "激活版本" → `promptsApi.activateVersion(template_id, version_id)` + refetch

---

## 13. AdminAudit.tsx / AdminLogs.tsx

**文件**：`frontend/src/app/pages/AdminAudit.tsx` / `AdminLogs.tsx`  
**角色**：admin  

### 13.1 改动

- AdminAudit 假表格 → `invocationsApi.getInvocations({ page_size: 50 })`
- AdminLogs 假表格 → `logsApi.operationLogs({ page_size: 50 })` + 切到登录日志用 `logsApi.loginLogs(...)`
- "详情"按钮 → 弹 Modal 显示 record 详情
- "导出" → 造个 CSV Blob 下载

---

## 14. AdminModelConfig.tsx

**文件**：`frontend/src/app/pages/AdminModelConfig.tsx`  
**角色**：admin  
**硬编码 const[]**：（无）

### 14.1 改动

- 模型列表 → `modelsApi.getModels({ page_size: 50 })`
- 启用/停用 → `useState` 维护 + `notify.success("已切换")`（后端无 update 端点）
- "测试连接" → `fetch(\`\${baseURL}/models\`, {headers: {Authorization: \`Bearer \${key}\`}})` （演示，捕获异常）
- "编辑配置" → 弹 Modal（**后端无 update**）  
- "查看调用" → `navigate(\`/admin/audit?model=\${modelId}\`)`

---

## 15. AdminGovernance.tsx 续

(见 #4) — 已包含。

## 16. LearningFeedback.tsx

**文件**：`frontend/src/app/pages/LearningFeedback.tsx`  
**角色**：student

### 16.1 改动

- 反馈列表 → `feedbackApi.list({ page_size: 50 })`
- "提交反馈"表单 → `feedbackApi.submit({...})` + refetch
- 难度评分 → 真实 select 写入

## 17. ResourceLibrary.tsx

**文件**：`frontend/src/app/pages/ResourceLibrary.tsx`  
**角色**：student / teacher

### 17.1 改动

- 资源列表 → `resourcesApi.list({ page_size: 50 })` + 类型筛选
- "查看详情" → 弹 Modal 显示 content
- "下载" → 造 Blob 下载

## 18. StudentTasks.tsx / TeacherTasks.tsx

**文件**：`frontend/src/app/pages/StudentTasks.tsx` / `TeacherTasks.tsx`  
**角色**：student / teacher

### 18.1 改动

- 任务列表 → `learningApi.listTasks({...})` / `tasksApi.listProjectTasks(project_id, {...})`
- "开始任务" → `navigate(\`/student/tasks/\${task.id}\`)` 
- "提交审核" → `tasksApi.submitReview(output_id, {submit_note: "..."})` + refetch

## 19. StudentTutor.tsx

**文件**：`frontend/src/app/pages/StudentTutor.tsx`  
**角色**：student

### 19.1 改动

- "发送提问" → `agentsApi.generate({student_id, course_id, knowledge_point_ids: [], resource_type: "tutor", difficulty: "basic"})` 触发后端 AI，stream 渲染
- 历史对话 → 后端无 chat-history 端点，**保留前端 useState 维护**

## 20. StudentProfile.tsx / StudentLearningPath.tsx

**文件**：`frontend/src/app/pages/StudentProfile.tsx` / `StudentLearningPath.tsx`  
**角色**：student / teacher

### 20.1 改动

- 画像详情 → `profilesApi.getById(profile_id)`
- 知识图谱 → `learningApi.getLearningPath(course_id)`
- 知识点点击 → 弹 Modal 显示 mastery

## 21. TeacherCourses.tsx

**文件**：`frontend/src/app/pages/TeacherCourses.tsx`  
**角色**：teacher

### 21.1 改动

- 课程列表 → `learningApi.listCourses()`（**注意：learningApi 是学生视角的，需要 `projectsApi.list` 拿教师课程**；建议后端加 `GET /api/courses?teacher_id=`）
- "进入课程" → `navigate(\`/teacher/courses/\${id}\`)`

## 22. TeacherReview.tsx

**文件**：`frontend/src/app/pages/TeacherReview.tsx`  
**角色**：teacher

### 22.1 改动

- 待审核列表 → `reviewsApi.getPending({ page_size: 50 })`
- "通过" → `reviewsApi.complete(request_id, {review_status: "approved", ...scores})` 
- "驳回" → `reviewsApi.complete(request_id, {review_status: "rejected", review_comment: "..."})` 
- "查看详情" → 弹 Modal 显示 `output_content`

## 23. TeacherKnowledgeBase.tsx

**文件**：`frontend/src/app/pages/TeacherKnowledgeBase.tsx`  
**角色**：teacher

### 23.1 改动

- 知识点树 → `learningApi.getLearningPath(course_id)` 的 nodes
- "补充资料" → 弹 Modal → 演示模式保存

## 24. LearningAnalytics.tsx 续

(见 #6) — 已包含。

---

## 25. AdminDashboard.tsx 续 + AdminCosts.tsx 续

(见 #2, #3) — 已包含。

## 26. DesignSystemUpdate.tsx（孤儿页）

**文件**：`frontend/src/app/pages/DesignSystemUpdate.tsx`  
**角色**：N/A — 仅 design system 展示页  
**处理**：从 `routes.tsx` 删除 import 和 route（**它不在 router 里**，仅作为 .tsx 残留）。验证方法：

```bash
grep "DesignSystemUpdate" frontend/src/app/routes.tsx  # 应为空
```

## 27. Dashboard.tsx（孤儿页）

**文件**：`frontend/src/app/pages/Dashboard.tsx`  
**角色**：N/A — 早期 landing 残留  
**处理**：同上，从 routes.tsx 验证不在路由表，**保留文件**（可能是设计稿参考）。

---

## 改动优先级（推荐工作顺序）

| # | 页面 | 改动量 | 优先级 | 理由 |
|---|---|---|---|---|
| 1 | Login | 30 行 | 🔴 P0 | 影响所有用户进入 |
| 2 | StudentDashboard | 50 行 | 🔴 P0 | 学生首屏 |
| 3 | TeacherDashboard | **已改 ✅** | 🔴 P0 | 教师首屏 |
| 4 | AdminDashboard | 40 行 | 🔴 P0 | 管理员首屏 |
| 5 | AdminCourses | 30 行 + 5 行后端 | 🟠 P1 | 课程管理是核心 |
| 6 | AdminPrompts | 40 行 | 🟠 P1 | 模板管理 |
| 7 | AdminUsers | 50 行 | 🟠 P1 | 用户管理 |
| 8 | AdminModelConfig | 40 行 | 🟠 P1 | 模型配置 |
| 9 | TeacherReview | 35 行 | 🟠 P1 | 审核工作流 |
| 10 | LearningFeedback | 30 行 | 🟡 P2 | 学生反馈 |
| 11 | ResourceLibrary | 35 行 | 🟡 P2 | 资源库 |
| 12 | StudentTasks/TeacherTasks | 各 30 行 | 🟡 P2 | 任务列表 |
| 13 | AdminAudit/AdminLogs | 各 30 行 | 🟡 P2 | 日志 |
| 14 | AdminGovernance | 30 行 | 🟡 P2 | 治理 |
| 15 | AdminCosts | 25 行 | 🟡 P2 | 成本 |
| 16 | LearningAnalytics | 20 行 | 🟡 P2 | 分析 |
| 17 | RolePermissionMap | 25 行 | 🟢 P3 | 权限矩阵 |
| 18 | AgentWorkbench | 60 行 | 🟢 P3 | 工作台 |
| 19 | StudentTutor | 30 行 | 🟢 P3 | 智能体辅导 |
| 20 | StudentProfile/LearningPath | 各 30 行 | 🟢 P3 | 学生视图 |
| 21 | TeacherCourses | 25 行 | 🟢 P3 | 教师课程 |
| 22 | TeacherKnowledgeBase | 25 行 | 🟢 P3 | 知识库 |
| 23 | AdminAgentConfig | 20 行 | 🟢 P3 | 智能体配置 |
| 24 | Dashboard.tsx (orphan) | 0 | ⚪ 删除路由 | 不挂载 |
| 25 | DesignSystemUpdate.tsx (orphan) | 0 | ⚪ 删除路由 | 不挂载 |
| 26 | NotFound.tsx | 0 | ⚪ 不动 | 404 兜底 |

---

## 实施脚本（伪代码，1 轮执行）

```bash
# 1. 后端：补 2 个端点（必须先做）
cat >> backend/app/routers/courses.py <<'EOF'
@router.get("")
def list_courses(db = Depends(get_db)):
    rows = db.execute("SELECT * FROM courses WHERE is_deleted=0").fetchall()
    return success_response([dict(r) for r in rows])

@router.put("/{course_id}")
def update_course(course_id: int, data: CourseUpdate, db = Depends(get_db)):
    db.execute("UPDATE courses SET status=%s WHERE course_id=%s", (data.status, course_id))
    db.commit()
    return success_response()
EOF

# 2. 前端：批量执行（按优先级）
# 每改一个文件立即跑：
cd frontend && npm run typecheck  # 不能有 TS 错误
# 浏览器开 http://localhost:5175/login 登录对应账号 → 验证页面
```

---

## 验证脚本（端到端）

```bash
#!/bin/bash
# scripts/e2e_smoke.sh
set -e

# 1. 后端健康
curl -fs http://127.0.0.1:8000/api/health/db >/dev/null || (echo "DB unhealthy"; exit 1)

# 2. 5 个角色登录
for u in admin teacher_li teacher_wang student_zhang student_chen; do
  TOK=$(curl -sS -X POST http://127.0.0.1:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$u\",\"password\":\"Pass@1234\"}" | jq -r .data.token)
  [ "$TOK" != "null" ] && [ -n "$TOK" ] || (echo "$u login failed"; exit 1)
  echo "$u: OK"
done

# 3. 关键 API 抽查
curl -sS -H "Authorization: Bearer $TOK" http://127.0.0.1:8000/api/statistics/overview | jq '.data | {project_count, task_count, student_count: .student_count}'

# 4. 浏览器手动验证 5 个角色的关键页面
echo "Browser checks: /admin /teacher /student /admin/users /admin/prompts /admin/audit /teacher/review /student/tutor"
```

---

## 总结

| 维度 | 数量 |
|---|---|
| 待改造前端页面 | 26 |
| 硬编码 const[] 块 | 17 |
| 需要新增后端端点 | 2（`GET/PUT /api/courses`） |
| 死按钮 `showToast("...TODO...")` 估计 | ~150+ 处（按平均 5-8 个/页） |
| ui-ux critical 规则覆盖 | 6 条 |
| 总工作量估计 | **3-5 小时**（单 IDE 助手） |

**P0（必须）**：Login + 3 个 Dashboard + AdminCourses  
**P1（重要）**：Admin/Teacher 的核心管理页（Users/Prompts/Models/Review）  
**P2/P3**：次要页面 + Tutor + KnowledgeBase  
**⚪ 跳过**：2 个孤儿 .tsx

如果只做 P0，工作量约 1.5 小时；做完全部 P0+P1+P2，约 4 小时；含 P3 全部约 5 小时。
