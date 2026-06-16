import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  BookOpenCheck,
  Bot,
  CheckCircle2,
  Clock3,
  FileText,
  GraduationCap,
  HelpCircle,
  Library,
  PlayCircle,
  Route,
  Sparkles,
  Target,
  Timer,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi, statisticsApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  red: "bg-red-50 text-red-700 ring-red-100",
};

function resourceIcon(type: string) {
  const t = type?.toLowerCase() ?? "";
  if (t.includes("讲义") || t.includes("文档")) return FileText;
  if (t.includes("练习") || t.includes("题目")) return CheckCircle2;
  if (t.includes("代码") || t.includes("案例")) return BookOpenCheck;
  if (t.includes("视频") || t.includes("动画")) return PlayCircle;
  return Library;
}

export function StudentDashboard() {
  const user = useAuthStore((s) => s.user);
  const greetingName = user?.real_name ?? "同学";

  const { data: learningData } = useApi(() => learningApi.listCourses(), []);
  const { data: tasksData } = useApi(() => learningApi.listTasks({ page_size: 100 }), []);
  const { data: statsData } = useApi(() => statisticsApi.learningOverview(), []);
  const { data: resourcesData } = useApi(() => resourcesApi.list({ page_size: 4 }), []);

  const courseName = learningData?.[0]?.name ?? "（未选课）";
  const courseId = learningData?.[0]?.id;

  const tasks = tasksData?.items ?? [];
  const inProgressTasks = tasks.filter((t) => t.status === "in_progress").slice(0, 5);
  const pendingCount = tasks.filter((t) => t.status !== "completed").length;
  const todayCount = tasks.filter((t) => t.status === "in_progress").length;

  const resourceCards = (resourcesData?.items ?? []).map((r) => ({
    id: r.resource_id,
    title: r.resource_title,
    type: r.resource_type || "资源",
    minutes: String(r.difficulty ?? "—"),
    status: r.status === "approved" ? "已认证" : r.status,
    icon: resourceIcon(r.resource_type ?? ""),
  }));

  const loading = !learningData || !tasksData || !statsData || !resourcesData;

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      {/* Hero */}
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-60" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#2563EB,#06B6D4,#7C3AED)]" />
        <div className="relative grid grid-cols-[1.35fr_0.65fr] gap-6">
          <div>
            <div className="mb-4 flex w-fit cursor-pointer items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
              <GraduationCap className="h-3.5 w-3.5" />
              我的学习空间
            </div>
            <h2 className="text-[30px] font-black leading-tight text-slate-950">
              {greetingName}，今天继续学习「{courseName}」
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              系统已根据你的画像和最近测评结果，为你更新了本周学习路径。今天优先处理薄弱知识点，提升整体掌握度。
            </p>
            <div className="mt-6 flex gap-3">
              <Link to="/student/learning-path" className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)] transition hover:bg-blue-700">
                继续学习当前路径
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/student/tutor" className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700 transition hover:border-blue-200 hover:text-blue-700">
                向 AI 提问
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {[
              ["综合掌握度", statsData ? `${Math.round((statsData.avg_mastery ?? 0) * 100)}%` : "—", "当前课程整体水平"],
              ["本周学习目标", "薄弱知识点突破", "建议先补概念边界"],
              ["今日推荐时长", "45 分钟", "拆成 5 个轻任务"],
            ].map(([label, value, hint]) => (
              <div key={label} className="rounded-2xl border border-slate-100 bg-white/80 p-4 shadow-sm">
                <div className="text-xs font-bold text-slate-400">{label}</div>
                <div className="mt-1 text-lg font-black text-slate-900">{value}</div>
                <div className="mt-1 text-xs text-slate-500">{hint}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* KPI Cards */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {[
          { label: "综合掌握度", value: statsData ? `${Math.round((statsData.avg_mastery ?? 0) * 100)}%` : "—", hint: "实时统计", icon: BarChart3, tone: "blue" },
          { label: "待完成任务", value: String(pendingCount || "—"), hint: `今日 ${todayCount} 项`, icon: CheckCircle2, tone: "purple" },
          { label: "课程数量", value: String(learningData?.length ?? "—"), hint: "已选课程", icon: Timer, tone: "emerald" },
          { label: "资源总数", value: String(resourcesData?.total ?? "—"), hint: "已发布资源", icon: FileText, tone: "orange" },
          { label: "本周反馈", value: String(statsData?.feedback_count ?? "—"), hint: "近 7 天", icon: Target, tone: "red" },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="edu-card edu-card-hover cursor-pointer rounded-2xl p-4">
              <div className={`mb-4 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[stat.tone]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="text-sm font-semibold text-slate-500">{stat.label}</div>
              <div className="mt-1 text-[26px] font-black leading-8 text-slate-950">{stat.value}</div>
              <div className="mt-1 text-xs font-medium text-slate-400">{stat.hint}</div>
            </div>
          );
        })}
      </section>

      {/* Tasks + Weak Points */}
      <section className="grid grid-cols-[1.45fr_0.95fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-black text-slate-950">今日学习路径</h3>
              <p className="mt-1 text-sm text-slate-500">按依赖关系拆分，完成后会自动触发画像更新。</p>
            </div>
            <Route className="h-5 w-5 cursor-pointer text-blue-500" />
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" />
            </div>
          ) : inProgressTasks.length > 0 ? (
            <div className="space-y-3">
              {inProgressTasks.map((step, index) => (
                <div key={step.id} className="grid grid-cols-[36px_1fr_auto] items-start gap-3 rounded-2xl border border-slate-100 bg-slate-50/70 p-3">
                  <div className={`grid h-9 w-9 place-items-center rounded-xl text-xs font-black ring-1 ${step.status === "completed" ? "bg-emerald-50 text-emerald-700 ring-emerald-100" : step.status === "in_progress" ? "bg-blue-600 text-white ring-blue-200" : "bg-white text-slate-500 ring-slate-200"}`}>
                    {index + 1}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="text-sm font-black text-slate-900">{step.title}</h4>
                      <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-bold text-slate-500 ring-1 ring-slate-100">{step.type}</span>
                    </div>
                    <p className="mt-1 text-xs leading-5 text-slate-500">{step.description || "—"}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-black text-slate-700">{step.due_date || "无截止"}</div>
                    <div className={`mt-1 rounded-full px-2 py-0.5 text-[11px] font-bold ${step.status === "in_progress" ? "bg-blue-50 text-blue-700" : step.status === "completed" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                      {step.status === "completed" ? "已完成" : step.status === "in_progress" ? "进行中" : "待完成"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock3 className="mb-3 h-10 w-10 text-slate-300" />
              <p className="text-sm font-medium text-slate-400">暂无进行中的任务</p>
              <Link to="/student/tasks" className="mt-3 text-sm font-bold text-blue-600">去任务列表看看</Link>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-6">
          <div className="edu-card rounded-2xl p-6">
            <h3 className="mb-4 flex cursor-pointer items-center gap-2 text-base font-black text-slate-950">
              <Target className="h-5 w-5 text-orange-600" />
              我的薄弱点
            </h3>
            <div className="space-y-3">
              {[
                ["事务隔离级别", "32%", "概念边界不清"],
                ["SQL 多表连接", "46%", "复杂查询仍需练习"],
                ["接口字段设计", "61%", "项目迁移易错"],
              ].map(([name, score, hint]) => (
                <div key={name} className="cursor-pointer rounded-xl border border-slate-100 bg-white p-3 transition hover:border-orange-200">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-black text-slate-800">{name}</span>
                    <span className="text-xs font-black text-orange-700">{score}</span>
                  </div>
                  <div className="text-xs text-slate-500">{hint}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-[linear-gradient(135deg,#EFF6FF,#F5F3FF)] p-6 shadow-[0_10px_30px_rgba(37,99,235,0.08)]">
            <div className="mb-3 grid h-11 w-11 cursor-pointer place-items-center rounded-2xl bg-white text-blue-700 shadow-sm ring-1 ring-blue-100">
              <Bot className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-black text-slate-950">遇到问题？向学习智能体提问</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              可以直接问："可重复读和串行化到底有什么区别？"
            </p>
            <Link to="/student/tutor" className="mt-4 inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-xl bg-slate-950 px-4 text-sm font-bold text-white transition hover:bg-slate-800">
              开始提问
              <HelpCircle className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Resources */}
      <section className="edu-card rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="flex cursor-pointer items-center gap-2 text-lg font-black text-slate-950">
            <Library className="h-5 w-5 text-blue-600" />
            推荐学习资源
          </h3>
          <Link to="/student/resources" className="cursor-pointer text-sm font-bold text-blue-700 hover:text-blue-800">查看全部</Link>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {resourceCards.length > 0 ? resourceCards.map((resource) => {
            const Icon = resource.icon;
            return (
              <Link
                key={resource.id}
                to={`/student/resources/${resource.id}`}
                className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-blue-200 hover:shadow-md cursor-pointer"
              >
                <div className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
                  <Icon className="h-5 w-5" />
                </div>
                <h4 className="min-h-[40px] text-sm font-black leading-5 text-slate-900">{resource.title}</h4>
                <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
                  <span>{resource.type}</span>
                  <span className="font-black text-emerald-700">{resource.status}</span>
                </div>
              </Link>
            );
          }) : (
            <div className="col-span-4 flex flex-col items-center justify-center py-12 text-center">
              <Library className="mb-3 h-10 w-10 text-slate-300" />
              <p className="text-sm font-medium text-slate-400">暂无学习资源</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
