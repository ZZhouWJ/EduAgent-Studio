import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { AlertTriangle, ArrowRight, BookOpen, CheckSquare, Database, FileText, GraduationCap, Library, MessageSquare, ShieldAlert, Target, Users } from "lucide-react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "@/lib/useApi";
import { reviewsApi, statisticsApi, learningApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  slate: "bg-slate-100 text-slate-700 ring-slate-200",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
  red: "bg-red-50 text-red-700 ring-red-100",
};

export function TeacherDashboard() {
  const user = useAuthStore((s) => s.user);
  const greetingName = user?.real_name ?? "老师";
  const { data: overview, loading: loadingOverview } = useApi(() => statisticsApi.overview(), []);
  const { data: learningData, loading: loadingLearning } = useApi(() => statisticsApi.learningOverview(), []);
  const { data: weakPoints, loading: loadingWeak } = useApi(() => statisticsApi.weakKnowledgePoints(5), []);
  const { data: pendingReviews } = useApi(() => reviewsApi.getPending({ page_size: 5 }), []);
  const { data: lowMastery } = useApi(() => statisticsApi.masteryDistribution(), []);
  const { data: tasksData } = useApi(() => learningApi.listTasks({ page_size: 6 }), []);

  const loading = loadingOverview || loadingLearning || loadingWeak;

  const stats = [
    { label: "管理课程数", value: String(learningData?.course_count ?? "—"), hint: "本人负责", icon: BookOpen, tone: "blue" },
    { label: "学生人数", value: String(learningData?.student_count ?? "—"), hint: learningData ? `覆盖 ${learningData.course_count} 门课程` : "—", icon: Users, tone: "slate" },
    { label: "待审核产出", value: String(pendingReviews?.total ?? "—"), hint: pendingReviews?.total ? `${pendingReviews.total} 条待处理` : "暂无", icon: CheckSquare, tone: "orange" },
    { label: "班级平均掌握度", value: learningData ? `${Math.round(learningData.avg_mastery * 100)}%` : "—", hint: "实时统计", icon: Target, tone: "emerald" },
    { label: "累计学习反馈", value: String(learningData?.feedback_count ?? "—"), hint: "本人课程范围", icon: MessageSquare, tone: "cyan" },
    { label: "失败调用", value: String(overview?.failed_invocation_count ?? 0), hint: "需检查调用日志", icon: ShieldAlert, tone: "red" },
  ];

  const weaknessData = (weakPoints ?? []).map((wp) => ({ name: wp.kp_name, score: Math.round(wp.avg_mastery * 100) }));

  const lowMasteryCount = (lowMastery ?? [])
    .filter((bucket) => bucket.range === "0-20%" || bucket.range === "20-40%")
    .reduce((total, bucket) => total + bucket.count, 0);
  const actionItems = [
    { title: `${pendingReviews?.total ?? 0} 个项目产出待审核`, desc: pendingReviews?.items?.length ? `最新：${pendingReviews.items[0]?.output_title ?? "—"}` : "暂无新提交", icon: CheckSquare, tone: "orange", action: "进入审核", link: "/teacher/review" },
    { title: `${lowMasteryCount} 名学生综合掌握度低于 40%`, desc: weaknessData.length ? `集中在 ${weaknessData[0]?.name ?? "—"} 等 ${weaknessData.length} 个知识点` : "等待数据", icon: Users, tone: "red", action: "查看学生", link: "/teacher/students" },
    { title: `${learningData?.feedback_count ?? 0} 条累计学习反馈`, desc: "来自本人课程范围内的学生记录", icon: MessageSquare, tone: "blue", action: "查看反馈", link: "/teacher/feedback" },
    { title: `${learningData?.resource_count ?? 0} 个课程资源`, desc: "包含草稿、待审核与已发布状态", icon: Database, tone: "slate", action: "管理资源", link: "/teacher/resources" },
  ];

  const taskSuggestions = (tasksData?.items ?? []).slice(0, 4).map((t) => ({
    title: t.title,
    type: t.type ?? "任务",
    target: t.course_name,
    status: t.status,
  }));
  if (taskSuggestions.length === 0) {
    taskSuggestions.push({ title: "尚无任务可生成", type: "—", target: "请前往工作台创建", status: "draft" });
  }
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="edu-card relative overflow-hidden rounded-2xl p-7"
      >
        <div className="relative grid grid-cols-[1.25fr_0.75fr] items-center gap-6">
          <div>
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600">
              教学工作台
            </div>
            <h2 className="text-[28px] font-semibold leading-[1.25] tracking-tight text-slate-900 sm:text-[32px]">
              {greetingName}，欢迎回到课堂
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              {learningData?.course_count
                ? `当前管理 ${learningData.course_count} 门课程，${learningData.student_count ?? 0} 名学生。`
                : "正在加载课程信息..."}
              {(weakPoints ?? []).length > 0
                ? ` 系统检测到"${weakPoints?.[0]?.kp_name}"等知识点为班级主要薄弱点，建议生成针对性资源并安排阶段测评。`
                : ""}
            </p>
            <div className="mt-6 flex gap-3">
              <Link to="/teacher/agent-workbench" className="inline-flex h-10 items-center gap-2 rounded-lg bg-slate-900 px-4 text-sm font-semibold text-white transition-colors hover:bg-slate-800">
                生成个性化资源
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/teacher/review" className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50">
                处理待审核资源
              </Link>
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <div className="flex h-32 items-center justify-center rounded-xl border border-slate-200 bg-gradient-to-br from-blue-50 to-slate-50">
              <GraduationCap className="h-14 w-14 text-blue-200" strokeWidth={1} />
          </div>
          <div className="grid grid-cols-2 gap-2">
              {[
                ["今日待办", String((pendingReviews?.total ?? 0) + (tasksData?.items?.filter((t) => t.status === "in_progress").length ?? 0)), "按优先级处理"],
                ["重点学生", String(lowMasteryCount), "掌握度低于 40%"],
                ["任务参考", String(taskSuggestions.length), "可用于生成资源"],
                ["课程资源", String(learningData?.resource_count ?? 0), "本人课程范围"],
              ].map(([label, value, hint]) => (
                <div key={label} className="rounded-lg border border-slate-200 bg-white px-3 py-2.5">
                  <div className="text-[11px] font-semibold text-slate-400">{label}</div>
                  <div className="mt-0.5 text-lg font-semibold text-slate-900">{value}</div>
                  <div className="text-[11px] text-slate-500">{hint}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      {loading ? (
        <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
      ) : (
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="grid grid-cols-6 gap-4"
      >
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="edu-card edu-card-hover rounded-2xl p-4">
              <div className={`mb-4 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[stat.tone]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="text-sm font-semibold text-slate-500">{stat.label}</div>
              <div className="mt-1 text-[26px] font-black leading-8 text-slate-950">{stat.value}</div>
              <div className="mt-1 text-xs font-medium text-slate-400">{stat.hint}</div>
            </div>
          );
        })}
      </motion.section>
      )}

      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="grid grid-cols-[1fr_0.95fr] gap-6"
      >
        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-lg font-semibold text-slate-900">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
            待处理事项
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {actionItems.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className={`mb-3 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[item.tone]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">{item.title}</h4>
                  <p className="mt-2 min-h-[40px] text-xs leading-5 text-slate-500">{item.desc}</p>
                  <Link to={item.link} className="mt-3 inline-block min-h-[44px] text-xs font-semibold text-slate-700 hover:text-slate-900">
                    {item.action} →
                  </Link>
                </div>
              );
            })}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-lg font-semibold text-slate-900">
            <Target className="h-5 w-5 text-red-600" />
            班级薄弱点分析
          </h3>
          <div className="h-[285px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weaknessData} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis dataKey="name" type="category" width={86} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#475569", fontWeight: 600 }} />
                <Tooltip cursor={{ fill: "#F8FAFC" }} contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
                <Bar dataKey="score" name="掌握度" radius={[0, 8, 8, 0]} barSize={22}>
                  {weaknessData.map((entry) => (
                    <Cell key={entry.name} fill={entry.score < 45 ? "#EF4444" : entry.score < 60 ? "#F59E0B" : "#10B981"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="edu-card rounded-2xl p-6"
      >
        <div className="mb-5 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
            资源生成建议
          </h3>
          <Link to="/teacher/agent-workbench" className="text-sm font-semibold text-slate-700 hover:text-slate-900">进入智能体工坊</Link>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {taskSuggestions.map((item, index) => (
            <Link
              key={`${item.title}-${index}`}
              to="/teacher/agent-workbench"
              className="rounded-xl border border-slate-200 bg-white p-4 transition hover:border-slate-300 hover:shadow-sm"
            >
              <div className="mb-3 flex items-center justify-between">
                <div className="grid h-10 w-10 place-items-center rounded-lg border border-slate-200 bg-slate-50 text-slate-700">
                  {index === 0 ? <FileText className="h-5 w-5" /> : index === 1 ? <CheckSquare className="h-5 w-5" /> : index === 2 ? <Library className="h-5 w-5" /> : <BookOpen className="h-5 w-5" />}
                </div>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">{item.type}</span>
              </div>
              <h4 className="min-h-[40px] text-sm font-semibold leading-5 text-slate-900">{item.title}</h4>
              <div className="mt-4 text-xs text-slate-500">{item.target}</div>
            </Link>
          ))}
        </div>
      </motion.section>
    </div>
  );
}
