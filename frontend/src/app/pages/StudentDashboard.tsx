import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpenCheck,
  CheckCircle2,
  ChevronRight,
  CircleDashed,
  Clock3,
  FileText,
  Library,
  PlayCircle,
  Target,
  Timer,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi, statisticsApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { SafeLottie } from "../components/SafeLottie";

function resourceIcon(type: string) {
  const t = type?.toLowerCase() ?? "";
  if (t.includes("讲义") || t.includes("文档")) return FileText;
  if (t.includes("练习") || t.includes("题目")) return CheckCircle2;
  if (t.includes("代码") || t.includes("案例")) return BookOpenCheck;
  if (t.includes("视频") || t.includes("动画")) return PlayCircle;
  return Library;
}

/* ─── KPI 卡 ──────────────────────────────────────── */
function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "slate",
}: {
  label: string;
  value: string;
  hint: string;
  icon: React.ComponentType<{ className?: string }>;
  tone?: "slate" | "blue" | "purple" | "emerald" | "amber" | "rose";
}) {
  const tones: Record<string, string> = {
    slate: "bg-slate-100 text-slate-700",
    blue: "bg-blue-50 text-blue-700",
    purple: "bg-violet-50 text-violet-700",
    emerald: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-700",
    rose: "bg-rose-50 text-rose-700",
  };
  return (
    <div className="edu-card edu-card-hover group p-5">
      <div className={`grid h-8 w-8 place-items-center rounded-md transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:rotate-[-4deg] ${tones[tone]}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="mt-5 text-[13px] font-medium text-slate-500">{label}</div>
      <div
        key={value}
        className="mt-1 inline-block text-[26px] font-semibold leading-[1.15] tracking-tight text-slate-900 edu-count-up"
      >
        {value}
      </div>
      <div className="mt-1.5 text-xs text-slate-400">{hint}</div>
    </div>
  );
}

export function StudentDashboard() {
  const user = useAuthStore((s) => s.user);
  const greetingName = user?.real_name ?? "同学";

  const { data: learningData } = useApi(() => learningApi.listCourses(), []);
  const { data: tasksData } = useApi(() => learningApi.listTasks({ page_size: 100 }), []);
  const { data: statsData } = useApi(() => statisticsApi.learningOverview(), []);
  const { data: resourcesData } = useApi(() => resourcesApi.list({ page_size: 4 }), []);

  const courseName = learningData?.[0]?.name ?? "（未选课）";
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
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6 ds-stagger">
      {/* ─── 标题区 ───────────────────────────────────── */}
      <header className="flex items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
            <BookOpenCheck className="h-3.5 w-3.5" />
            我的学习空间
          </div>
          <h1 className="mt-1.5 text-2xl font-semibold tracking-tight text-slate-900">
            {greetingName}，继续学习「{courseName}」
          </h1>
          <p className="mt-1.5 max-w-2xl text-sm text-slate-500">
            系统已根据你的画像和最近测评结果，更新了本周学习路径。今天优先处理薄弱知识点。
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/student/tutor"
            className="ds-press inline-flex h-9 items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3.5 text-[13px] font-medium text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50"
          >
            向 AI 提问
          </Link>
          <Link
            to="/student/learning-path"
            className="ds-press inline-flex h-9 items-center gap-1.5 rounded-md bg-slate-900 px-3.5 text-[13px] font-medium text-white transition-colors hover:bg-slate-800"
          >
            继续学习当前路径
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </header>

      {/* ─── KPI ──────────────────────────────────────── */}
      <section className="edu-stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard
          label="综合掌握度"
          value={statsData ? `${Math.round((statsData.avg_mastery ?? 0) * 100)}%` : "—"}
          hint="实时统计"
          icon={Target}
          tone="blue"
        />
        <StatCard
          label="待完成任务"
          value={String(pendingCount || "—")}
          hint={`今日 ${todayCount} 项`}
          icon={CheckCircle2}
          tone="purple"
        />
        <StatCard
          label="课程数量"
          value={String(learningData?.length ?? "—")}
          hint="已选课程"
          icon={Timer}
          tone="emerald"
        />
        <StatCard
          label="资源总数"
          value={String(resourcesData?.total ?? "—")}
          hint="已发布资源"
          icon={FileText}
          tone="amber"
        />
        <StatCard
          label="本周反馈"
          value={String(statsData?.feedback_count ?? "—")}
          hint="近 7 天"
          icon={Library}
          tone="rose"
        />
      </section>

      {/* ─── 今日学习路径 + 薄弱点 ──────────────────────── */}
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.55fr_1fr]">
        <div className="edu-card overflow-hidden p-0">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
            <div>
              <h2 className="text-[15px] font-semibold tracking-tight text-slate-900">今日学习路径</h2>
              <p className="mt-0.5 text-xs text-slate-500">按依赖关系拆分，完成后会自动触发画像更新。</p>
            </div>
            <Link
              to="/student/tasks"
              className="ds-link inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-900"
            >
              全部任务
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-10 text-sm text-slate-400">
              <CircleDashed className="mr-2 h-4 w-4 animate-spin" />
              加载中…
            </div>
          ) : inProgressTasks.length > 0 ? (
            <ol className="edu-stagger divide-y divide-slate-100">
              {inProgressTasks.map((step, index) => {
                const done = step.status === "completed";
                const inProgress = step.status === "in_progress";
                return (
                  <li key={step.id} className="ds-row-hover px-5 py-3.5">
                    <div className="flex items-start gap-3">
                      <div
                        className={`grid h-7 w-7 shrink-0 place-items-center rounded-md text-[11px] font-semibold tabular-nums ${
                          done
                            ? "bg-emerald-50 text-emerald-700"
                            : inProgress
                              ? "bg-slate-900 text-white"
                              : "bg-slate-100 text-slate-500"
                        }`}
                      >
                        {String(index + 1).padStart(2, "0")}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="truncate text-[13px] font-medium text-slate-900">
                            {step.title}
                          </h3>
                          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
                            {step.type}
                          </span>
                        </div>
                        <p className="mt-1 line-clamp-2 text-xs leading-snug text-slate-500">
                          {step.description || "—"}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-xs tabular-nums text-slate-500">
                          {step.due_date || "无截止"}
                        </div>
                        <div
                          className={`mt-1 inline-block rounded px-1.5 py-0.5 text-[10px] font-medium ${
                            done
                              ? "bg-emerald-50 text-emerald-700"
                              : inProgress
                                ? "bg-blue-50 text-blue-700"
                                : "bg-slate-100 text-slate-500"
                          }`}
                        >
                          {done ? "已完成" : inProgress ? "进行中" : "待完成"}
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ol>
          ) : (
            <div className="flex flex-col items-center gap-3 py-10 text-slate-400">
              <SafeLottie source="empty" className="h-24 w-32" speed={0.8} />
              <span className="text-sm">暂无进行中的任务</span>
              <Link to="/student/tasks" className="ds-link text-xs text-slate-500 hover:text-slate-900">
                去任务列表看看
              </Link>
            </div>
          )}
        </div>

        <div className="edu-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-amber-600" />
              <h2 className="text-[15px] font-semibold tracking-tight text-slate-900">我的薄弱点</h2>
            </div>
            <Link to="/student/learning-path" className="ds-link text-xs text-slate-500 hover:text-slate-900">
              查看学习路径
            </Link>
          </div>
          <ul className="edu-stagger divide-y divide-slate-100">
            {[
              { name: "事务隔离级别", score: 32, hint: "概念边界不清" },
              { name: "SQL 多表连接", score: 46, hint: "复杂查询仍需练习" },
              { name: "接口字段设计", score: 61, hint: "项目迁移易错" },
            ].map((w) => {
              const tone =
                w.score < 45 ? "rose" : w.score < 60 ? "amber" : "emerald";
              const toneMap: Record<string, string> = {
                rose: "bg-rose-50 text-rose-700",
                amber: "bg-amber-50 text-amber-700",
                emerald: "bg-emerald-50 text-emerald-700",
              };
              return (
                <li
                  key={w.name}
                  className="ds-row-hover flex items-center justify-between rounded-md -mx-2 px-2 py-2.5"
                >
                  <div>
                    <div className="text-[13px] font-medium text-slate-900">{w.name}</div>
                    <div className="mt-0.5 text-xs text-slate-500">{w.hint}</div>
                  </div>
                  <div
                    className={`grid h-9 w-12 place-items-center rounded text-[12px] font-semibold tabular-nums ${toneMap[tone]}`}
                  >
                    {w.score}%
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </section>

      {/* ─── 推荐学习资源 ──────────────────────────────── */}
      <section className="edu-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold tracking-tight text-slate-900">推荐学习资源</h2>
          <Link
            to="/student/resources"
            className="ds-link inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-900"
          >
            查看全部
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        {resourceCards.length > 0 ? (
          <div className="ds-stagger grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {resourceCards.map((r) => {
              const Icon = r.icon;
              return (
                <Link
                  key={r.id}
                  to={`/student/resources/${r.id}`}
                  className="ds-hover-lift ds-press group flex flex-col rounded-md border border-slate-200 bg-white p-3.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="grid h-7 w-7 place-items-center rounded bg-slate-100 text-slate-700">
                      <Icon className="h-3.5 w-3.5" />
                    </span>
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
                      {r.status}
                    </span>
                  </div>
                  <div className="mt-3 line-clamp-2 text-[13px] font-medium leading-snug text-slate-900">
                    {r.title}
                  </div>
                  <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
                    <span>{r.type}</span>
                    <ArrowRight className="h-3.5 w-3.5 opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 py-12 text-slate-400">
            <Library className="h-6 w-6" />
            <span className="text-sm">暂无学习资源</span>
          </div>
        )}
      </section>
    </div>
  );
}
