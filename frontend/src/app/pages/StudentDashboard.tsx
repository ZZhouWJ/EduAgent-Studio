import { Link } from "react-router-dom";
import { motion } from "motion/react";
import {
  ArrowRight,
  BookOpenCheck,
  CheckCircle2,
  ChevronRight,
  CircleDashed,
  FileText,
  Library,
  PlayCircle,
  Target,
  Timer,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi, statisticsApi, profilesApi } from "@/lib/api";
import { SafeLottie } from "../components/SafeLottie";
import { MetricTile } from "../components/common/MetricTile";

function resourceIcon(type: string) {
  const t = type?.toLowerCase() ?? "";
  if (t.includes("讲义") || t.includes("文档")) return FileText;
  if (t.includes("练习") || t.includes("题目")) return CheckCircle2;
  if (t.includes("代码") || t.includes("案例")) return BookOpenCheck;
  if (t.includes("视频") || t.includes("动画")) return PlayCircle;
  return Library;
}

export function StudentDashboard() {
  const { data: learningData } = useApi(() => learningApi.listCourses(), []);
  const { data: tasksData } = useApi(() => learningApi.listTasks({ page_size: 100 }), []);
  const { data: statsData } = useApi(() => statisticsApi.learningOverview(), []);
  const { data: resourcesData } = useApi(() => resourcesApi.list({ page_size: 4 }), []);
  const { data: weakPoints } = useApi(() => statisticsApi.weakKnowledgePoints(5), []);
  const { data: profileData } = useApi(() => profilesApi.getMyProfile(), []);

  const profileId = profileData?.profile_id ?? 0;
  const courseId = profileData?.course_id ?? 0;
  const { data: recommendedResources } = useApi(
    () => (profileId && courseId ? learningApi.getRecommendedResources(profileId, courseId) : Promise.resolve(null)),
    [profileId, courseId]
  );

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
      {/* ─── KPI ──────────────────────────────────────── */}
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <MetricTile
          label="综合掌握度"
          value={statsData ? `${Math.round((statsData.avg_mastery ?? 0) * 100)}%` : "—"}
          hint="实时统计"
          icon={Target}
          tone="blue"
          delay={0}
        />
        <MetricTile
          label="待完成任务"
          value={String(pendingCount || "—")}
          hint={`今日 ${todayCount} 项`}
          icon={CheckCircle2}
          tone="purple"
          delay={0.06}
        />
        <MetricTile
          label="课程数量"
          value={String(learningData?.length ?? "—")}
          hint="已选课程"
          icon={Timer}
          tone="emerald"
          delay={0.12}
        />
        <MetricTile
          label="资源总数"
          value={String(resourcesData?.total ?? "—")}
          hint="已发布资源"
          icon={FileText}
          tone="orange"
          delay={0.18}
        />
        <MetricTile
          label="累计反馈"
          value={String(statsData?.feedback_count ?? "—")}
          hint="历史反馈总数"
          icon={Library}
          tone="slate"
          delay={0.24}
        />
      </section>

      {/* ─── 今日学习路径 + 薄弱点 ──────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="grid grid-cols-1 gap-4 lg:grid-cols-[1.55fr_1fr]"
      >
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
            {(weakPoints ?? []).length > 0 ? (weakPoints ?? []).map((wp) => {
              const score = Math.round(wp.avg_mastery * 100);
              const tone =
                score < 45 ? "rose" : score < 60 ? "amber" : "emerald";
              const toneMap: Record<string, string> = {
                rose: "bg-rose-50 text-rose-700",
                amber: "bg-amber-50 text-amber-700",
                emerald: "bg-emerald-50 text-emerald-700",
              };
              const hint = score < 45 ? "急需加强" : score < 60 ? "仍需练习" : "接近掌握";
              return (
                <li
                  key={wp.kp_id}
                  className="ds-row-hover flex items-center justify-between rounded-md -mx-2 px-2 py-2.5"
                >
                  <div>
                    <div className="text-[13px] font-medium text-slate-900">{wp.kp_name}</div>
                    <div className="mt-0.5 text-xs text-slate-500">{hint}</div>
                  </div>
                  <div
                    className={`grid h-9 w-12 place-items-center rounded text-[12px] font-semibold tabular-nums ${toneMap[tone]}`}
                  >
                    {score}%
                  </div>
                </li>
              );
            }) : (
              <li className="flex items-center justify-center py-6 text-sm text-slate-400">暂无薄弱点数据</li>
            )}
          </ul>
        </div>
      </motion.section>

      {/* ─── 推荐学习资源 ──────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.45, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="edu-card p-5"
      >
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
      </motion.section>

      {/* ─── 今日推荐资源 ──────────────────────────── */}
      {recommendedResources && recommendedResources.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          className="edu-card p-5"
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-[15px] font-semibold tracking-tight text-slate-900">今日推荐资源</h2>
            <span className="rounded bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-600">
              基于最新画像
            </span>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {recommendedResources.map((r) => {
              const Icon = resourceIcon(r.type ?? "");
              return (
                <Link
                  key={r.resource_id}
                  to={`/student/resources/${r.resource_id}`}
                  className="ds-hover-lift ds-press group flex flex-col rounded-md border border-slate-200 bg-white p-3.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="grid h-7 w-7 place-items-center rounded bg-emerald-50 text-emerald-700">
                      <Icon className="h-3.5 w-3.5" />
                    </span>
                    <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-600">
                      {r.type}
                    </span>
                  </div>
                  <div className="mt-3 line-clamp-2 text-[13px] font-medium leading-snug text-slate-900">
                    {r.title}
                  </div>
                  {r.reason && (
                    <div className="mt-2 text-[11px] text-emerald-600">{r.reason}</div>
                  )}
                  <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
                    <span>{r.estimated_minutes ? `${r.estimated_minutes} 分钟` : ""}</span>
                    <ArrowRight className="h-3.5 w-3.5 opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </Link>
              );
            })}
          </div>
        </motion.section>
      )}
    </div>
  );
}
