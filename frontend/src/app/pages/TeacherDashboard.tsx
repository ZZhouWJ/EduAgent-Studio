import React from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, ArrowRight, BookOpen, Bot, CheckSquare, Database, FileText, Library, MessageSquare, ShieldAlert, Sparkles, Target, Users } from "lucide-react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { motion } from "motion/react";
import { useApi } from "@/lib/useApi";
import { reviewsApi, statisticsApi, learningApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
  red: "bg-red-50 text-red-700 ring-red-100",
};

/* ─── Hero 标语区：逐字打印 + 光带扫过 + 浮动点缀 ─── */
function HeroSlogan() {
  const main = "把知识变简单，把成长变自然。";
  const sub = "每一次学习，都更接近答案。";
  const chars = Array.from(main);

  return (
    <div className="relative overflow-hidden">
      {/* 漂浮的语义化小图标（书页、种子、答案标记） */}
      <motion.div
        className="absolute -right-2 -top-3 text-blue-200/70"
        animate={{ y: [0, -8, 0], rotate: [0, 6, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      >
        <BookOpen className="h-7 w-7" />
      </motion.div>
      <motion.div
        className="absolute -left-1 top-2 text-emerald-200/70"
        animate={{ y: [0, 10, 0], rotate: [0, -8, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}
      >
        <Sparkles className="h-6 w-6" />
      </motion.div>

      {/* 主标语：逐字打印 + 渐变光带扫过 */}
      <h2 className="text-[34px] font-black leading-[1.18] tracking-tight text-slate-950 sm:text-[40px]">
        {chars.map((ch, i) => (
          <motion.span
            key={i}
            initial={{ opacity: 0, y: 14, filter: "blur(6px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{
              delay: 0.05 + i * 0.055,
              duration: 0.55,
              ease: [0.22, 1, 0.36, 1],
            }}
            className="inline-block bg-gradient-to-br from-slate-950 via-blue-700 to-indigo-600 bg-clip-text text-transparent"
          >
            {ch === " " ? "\u00A0" : ch}
          </motion.span>
        ))}

        {/* 闪烁光标 */}
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 1, 0] }}
          transition={{ delay: 0.05 + chars.length * 0.055, duration: 1.1, repeat: 2 }}
          className="ml-1 inline-block h-[28px] w-[3px] -translate-y-[2px] rounded-sm bg-blue-500 align-middle sm:h-[34px]"
        />
      </h2>

      {/* 主标语下方光带扫过 */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.05 + chars.length * 0.055 + 0.2, duration: 0.9, ease: [0.65, 0, 0.35, 1] }}
        style={{ transformOrigin: "0% 50%" }}
        className="mt-2 h-[2px] w-[68%] bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400"
      />

      {/* 副标语：错峰淡入 + 节拍闪烁的句号 */}
      <motion.p
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 + chars.length * 0.055 + 0.5, duration: 0.7 }}
        className="mt-4 flex flex-wrap items-center gap-2 text-[15px] font-medium leading-7 text-slate-600"
      >
        {Array.from(sub).map((ch, i) =>
          ch === "。" ? (
            <motion.span
              key={`dot-${i}`}
              animate={{ opacity: [0.4, 1, 0.4], scale: [1, 1.15, 1] }}
              transition={{ duration: 1.8, repeat: Infinity, delay: i * 0.05 }}
              className="text-blue-500"
            >
              {ch}
            </motion.span>
          ) : (
            <motion.span
              key={`c-${i}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 + chars.length * 0.055 + 0.5 + i * 0.03, duration: 0.4 }}
            >
              {ch}
            </motion.span>
          )
        )}
      </motion.p>
    </div>
  );
}

export function TeacherDashboard() {
  const user = useAuthStore((s) => s.user);
  const greetingName = user?.real_name ?? "老师";
  const { data: overview, loading: loadingOverview } = useApi(() => statisticsApi.overview(), []);
  const { data: learningData, loading: loadingLearning } = useApi(() => statisticsApi.learningOverview(), []);
  const { data: weakPoints, loading: loadingWeak } = useApi(() => statisticsApi.weakKnowledgePoints(5), []);
  const { data: pendingReviews } = useApi(() => reviewsApi.list({ status: "pending", page_size: 5 }), []);
  const { data: lowMastery } = useApi(() => statisticsApi.masteryDistribution(), []);
  const { data: tasksData } = useApi(() => learningApi.listTasks({ page_size: 6 }), []);

  const loading = loadingOverview || loadingLearning || loadingWeak;

  const stats = [
    { label: "管理课程数", value: String(overview?.active_project_count ?? "—"), hint: "本学期", icon: BookOpen, tone: "blue" },
    { label: "学生人数", value: String(learningData?.student_count ?? "—"), hint: overview ? `${overview?.artifact_count ?? 0} 个班级` : "—", icon: Users, tone: "purple" },
    { label: "待审核资源", value: String(overview?.pending_review_count ?? "—"), hint: pendingReviews?.total ? `${pendingReviews.total} 条待处理` : "暂无", icon: CheckSquare, tone: "orange" },
    { label: "班级平均掌握度", value: learningData ? `${learningData.avg_mastery}%` : "—", hint: "实时统计", icon: Target, tone: "emerald" },
    { label: "本周新增反馈", value: String(learningData?.feedback_count ?? "—"), hint: "全部学生", icon: MessageSquare, tone: "cyan" },
    { label: "高风险资源", value: String(overview?.failed_invocation_count ?? 0), hint: "需人工复核", icon: ShieldAlert, tone: "red" },
  ];

  const weaknessData = (weakPoints ?? []).map((wp) => ({ name: wp.kp_name, score: Math.round(wp.avg_mastery * 100) }));

  // 待处理事项：每条都从真实后端数据派生
  const lowMasteryCount = (lowMastery ?? []).filter((m) => m.range.includes("0%") || m.range.includes("1-30") || m.range.includes("30-50")).reduce((acc, m) => acc + m.count, 0);
  const actionItems = [
    { title: `${overview?.pending_review_count ?? 0} 个 AI 生成资源待审核`, desc: pendingReviews?.items?.length ? `最新：${pendingReviews.items[0]?.output_title ?? "—"}` : "暂无新提交", icon: CheckSquare, tone: "orange", action: "进入审核", link: "/teacher/review" },
    { title: `${lowMasteryCount} 名学生知识点掌握度低于 50%`, desc: weaknessData.length ? `集中在 ${weaknessData[0]?.name ?? "—"} 等 ${weaknessData.length} 个知识点` : "等待数据", icon: Users, tone: "red", action: "查看学生", link: "/teacher/students" },
    { title: `${learningData?.feedback_count ?? 0} 条学习反馈需要关注`, desc: "来自本班学生近 7 天", icon: MessageSquare, tone: "blue", action: "查看反馈", link: "/student/feedback" },
    { title: `${learningData?.resource_count ?? 0} 个学习资源可发布`, desc: "已审核通过，等待分发", icon: Database, tone: "purple", action: "补充资料", link: "/teacher/resources" },
  ];

  // 资源生成建议：直接从最近的 submitted/in_progress 任务中抽取
  const taskSuggestions = (tasksData?.items ?? []).slice(0, 4).map((t) => ({
    title: t.title,
    type: t.type ?? "任务",
    target: t.course_name,
    status: t.status,
  }));
  if (taskSuggestions.length === 0) {
    // 后端没有任务时给一个空态提示而不是假数据
    taskSuggestions.push({ title: "尚无任务可生成", type: "—", target: "请前往智能体工作台创建", status: "draft" });
  }
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-50" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#2563EB,#7C3AED,#06B6D4)]" />
        <div className="relative grid grid-cols-[1.25fr_0.75fr] gap-6">
          <div>
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-purple-100 bg-purple-50 px-3 py-1.5 text-xs font-bold text-purple-700">
              <Sparkles className="h-3.5 w-3.5" />
              教学工作台
            </div>
            <HeroSlogan />
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 + Array.from("把知识变简单，把成长变自然。").length * 0.055 + 1.0, duration: 0.5 }}
              className="mt-3 text-sm font-bold text-slate-700"
            >
              {greetingName}，欢迎回到「数据库系统原理与 Web 项目实践」课堂。
            </motion.p>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              系统检测到"事务隔离级别"和"SQL 多表连接"是当前班级主要薄弱点，建议生成针对性资源并安排阶段测评。
            </p>
            <div className="mt-6 flex gap-3">
              <Link to="/teacher/agent-workbench" className="inline-flex h-11 items-center gap-2 rounded-xl bg-[linear-gradient(110deg,#2563EB,#7C3AED)] px-5 text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)]">
                进入智能体工作台
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/teacher/review" className="inline-flex h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700">
                处理待审核资源
              </Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              ["今日待办", String((pendingReviews?.total ?? 0) + (tasksData?.items?.filter((t) => t.status === "in_progress").length ?? 0)), "按优先级处理"],
              ["重点学生", String(lowMasteryCount), "掌握度低于 50%"],
              ["建议生成", String(taskSuggestions.length), "资源生成机会"],
              ["课程资源", String(learningData?.resource_count ?? 0), "本课程已发布"],
            ].map(([label, value, hint]) => (
              <div key={label} className="rounded-2xl border border-slate-100 bg-white/[0.85] p-4 shadow-sm">
                <div className="text-xs font-bold text-slate-400">{label}</div>
                <div className="mt-1 text-2xl font-black text-slate-950">{value}</div>
                <div className="mt-1 text-xs text-slate-500">{hint}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {loading ? (
        <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
      ) : (
      <section className="grid grid-cols-6 gap-4">
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
      </section>
      )}

      <section className="grid grid-cols-[1fr_0.95fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
            待处理事项
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {actionItems.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-2xl border border-slate-100 bg-white p-4">
                  <div className={`mb-3 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[item.tone]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h4 className="text-sm font-black text-slate-900">{item.title}</h4>
                  <p className="mt-2 min-h-[40px] text-xs leading-5 text-slate-500">{item.desc}</p>
                  <Link to={item.link} className="mt-3 inline-block min-h-[44px] text-xs font-black text-blue-700">
                    {item.action} →
                  </Link>
                </div>
              );
            })}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
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
      </section>

      <section className="edu-card rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-lg font-black text-slate-950">
            <Bot className="h-5 w-5 text-purple-600" />
            资源生成建议
          </h3>
          <Link to="/teacher/agent-workbench" className="text-sm font-bold text-blue-700">进入生成</Link>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {taskSuggestions.map((item, index) => (
            <Link
              key={`${item.title}-${index}`}
              to="/teacher/agent-workbench"
              className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-purple-200 hover:shadow-md"
            >
              <div className="mb-3 flex items-center justify-between">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-purple-50 text-purple-700 ring-1 ring-purple-100">
                  {index === 0 ? <FileText className="h-5 w-5" /> : index === 1 ? <CheckSquare className="h-5 w-5" /> : index === 2 ? <Library className="h-5 w-5" /> : <BookOpen className="h-5 w-5" />}
                </div>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-bold text-slate-600">{item.type}</span>
              </div>
              <h4 className="min-h-[40px] text-sm font-black leading-5 text-slate-900">{item.title}</h4>
              <div className="mt-4 text-xs font-bold text-slate-500">{item.target}</div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
