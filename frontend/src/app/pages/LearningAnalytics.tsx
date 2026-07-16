import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar } from "recharts";
import { TrendingUp, Target, BookOpen, MessageSquare, CheckCircle, Loader2, RotateCcw, Zap } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { statisticsApi, learningApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const RESOURCE_COLORS: Record<string, string> = {
  lecture: "#3b82f6",
  ppt: "#8b5cf6",
  quiz: "#ef4444",
  case: "#10b981",
  review: "#f59e0b",
  test: "#06b6d4",
  exercise: "#8b5cf6",
  code: "#10b981",
  slides: "#f59e0b",
  reference: "#06b6d4",
  other: "#6b7280",
  default: "#6b7280",
};

function getResourceColor(type: string): string {
  return RESOURCE_COLORS[type] ?? RESOURCE_COLORS.default;
}

function formatPct(value: number | undefined | null): string {
  if (value == null) return "—";
  return value > 1 ? `${Math.round(value)}%` : `${Math.round(value * 100)}%`;
}

export function LearningAnalytics() {
  const user = useAuthStore((state) => state.user);
  const roles = user?.roles ?? [];
  const isStudent = roles.includes("student_member") && !roles.some((role) => role === "teacher" || role === "admin");
  const { data: overview, loading: loadingOverview } = useApi(() => statisticsApi.learningOverview(), []);
  const { data: weakPoints } = useApi(() => statisticsApi.weakKnowledgePoints(5), []);
  const { data: resourceDist } = useApi(() => statisticsApi.resourceTypeDistribution(), []);
  const { data: trend } = useApi(() => statisticsApi.invocationTrend(7), []);
  const { data: reviewRates } = useApi(
    () => isStudent ? Promise.resolve([]) : statisticsApi.reviewRateByCourse(),
    [isStudent],
  );
  const {
    data: courses,
    loading: loadingCourses,
    error: coursesError,
    refetch: refetchCourses,
  } = useApi(() => learningApi.listCourses(), []);

  const firstCourseId = courses?.[0]?.id;
  const {
    data: learningPath,
    loading: loadingPath,
    error: pathError,
    refetch: refetchPath,
  } = useApi(
    () => firstCourseId ? learningApi.getLearningPath(firstCourseId) : Promise.resolve(null),
    [firstCourseId],
  );

  const loading = loadingOverview;

  const kpiCards = isStudent
    ? [
        { label: "我的综合掌握度", val: formatPct(overview?.avg_mastery), icon: Target, c: "text-blue-600", bg: "bg-blue-50" },
        { label: "进行中任务", val: overview ? `${overview.active_tasks}` : "—", icon: Zap, c: "text-orange-600", bg: "bg-orange-50" },
        { label: "已选课程", val: overview ? `${overview.course_count}` : "—", icon: CheckCircle, c: "text-cyan-600", bg: "bg-cyan-50" },
        { label: "可学习资源", val: overview ? `${overview.resource_count}` : "—", icon: BookOpen, c: "text-purple-600", bg: "bg-purple-50" },
        { label: "我的学习反馈", val: overview ? `${overview.feedback_count}` : "—", icon: MessageSquare, c: "text-emerald-600", bg: "bg-emerald-50" },
        { label: "我的辅学调用", val: overview ? `${overview.invocation_count}` : "—", icon: TrendingUp, c: "text-indigo-600", bg: "bg-indigo-50" },
      ]
    : [
        { label: "班级平均掌握度", val: formatPct(overview?.avg_mastery), icon: Target, c: "text-blue-600", bg: "bg-blue-50" },
        { label: "活跃任务数", val: overview ? `${overview.active_tasks}` : "—", icon: Zap, c: "text-orange-600", bg: "bg-orange-50" },
        { label: "课程资源数", val: overview ? `${overview.resource_count}` : "—", icon: BookOpen, c: "text-purple-600", bg: "bg-purple-50" },
        { label: "学生反馈数", val: overview ? `${overview.feedback_count}` : "—", icon: MessageSquare, c: "text-emerald-600", bg: "bg-emerald-50" },
        { label: "本人智能体调用", val: overview ? `${overview.invocation_count}` : "—", icon: TrendingUp, c: "text-indigo-600", bg: "bg-indigo-50" },
        { label: "资源审核通过率", val: formatPct(overview?.review_pass_rate), icon: CheckCircle, c: "text-cyan-600", bg: "bg-cyan-50" },
      ];

  const weakPointData = (weakPoints ?? []).map((wp) => ({
    name: wp.kp_name,
    score: Math.round(wp.avg_mastery * 100),
  }));

  const pieData = (resourceDist ?? []).map((d) => ({
    name: d.type_name || d.resource_type,
    value: d.count,
    color: getResourceColor(d.resource_type),
  }));

  const trendData = (trend ?? []).map((t) => ({
    name: t.date?.slice(5) ?? t.date,
    calls: t.invocation_count,
  }));

  const totalReviewed = (reviewRates ?? []).reduce((acc, r) => acc + r.total, 0);
  const totalApproved = (reviewRates ?? []).reduce((acc, r) => acc + r.approved, 0);
  const totalRejected = totalReviewed - totalApproved;
  const avgPassRate = reviewRates && reviewRates.length > 0
    ? Math.round((reviewRates.reduce((acc, r) => acc + r.pass_rate, 0) / reviewRates.length) * 100)
    : null;

  const pathNodes = learningPath?.nodes ?? [];
  const pathIsLoading = loadingCourses || Boolean(firstCourseId && loadingPath);
  const pathHasError = Boolean(coursesError || pathError);
  const retryLearningPath = () => {
    void refetchCourses();
    if (firstCourseId) void refetchPath();
  };
  return (
    <div className="space-y-6 max-w-[1400px] mx-auto pb-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpiCards.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="bg-white rounded-xl p-4 shadow-[0_4px_12px_rgba(15,23,42,0.03)] border border-slate-100 flex flex-col justify-center gap-3">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg ${item.bg} flex items-center justify-center shrink-0`}>
                  <Icon className={`w-4 h-4 ${item.c}`} />
                </div>
                <div className="text-xs font-medium text-slate-500">{item.label}</div>
              </div>
              <div className="text-2xl font-bold text-slate-900">
                {loading ? <span className="text-slate-300">—</span> : item.val}
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Knowledge path graph */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 min-h-[360px] flex flex-col">
          <h3 className="text-base font-bold text-slate-900 mb-6">知识点学习路径图谱</h3>
          <div className="flex-1 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center p-8 relative overflow-hidden">
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:20px_20px]" />

            {pathIsLoading ? (
              <div className="relative z-10 flex items-center gap-2 text-sm font-medium text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                正在加载学习路径...
              </div>
            ) : pathHasError ? (
              <div className="relative z-10 flex flex-col items-center gap-3 text-center">
                <p className="text-sm text-red-600">学习路径加载失败，请检查网络后重试。</p>
                <button
                  type="button"
                  onClick={retryLearningPath}
                  className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-red-200 bg-white px-3 text-sm font-bold text-red-700 transition hover:bg-red-50"
                >
                  <RotateCcw className="h-4 w-4" />
                  重试
                </button>
              </div>
            ) : pathNodes.length > 0 ? (
              <div className="relative z-10 w-full h-full flex flex-wrap items-center justify-center gap-6">
                {pathNodes.map((node, i) => {
                  const status = node.mastery_level >= 0.7 ? "ok" : node.mastery_level >= 0.4 ? "warn" : "danger";
                  return (
                    <React.Fragment key={node.id || i}>
                      <div className={`px-4 py-2 rounded-lg font-bold text-sm shadow-sm border
                        ${status === 'ok' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                          status === 'warn' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                          'bg-red-50 text-red-700 border-red-200'
                        }`}
                      >
                        {node.kp_name || node.name}
                      </div>
                      {i < pathNodes.length - 1 && <div className="w-8 h-0.5 bg-slate-300" />}
                    </React.Fragment>
                  );
                })}
              </div>
            ) : (
              <div className="relative z-10 text-sm text-slate-400">
                {!firstCourseId
                  ? isStudent
                    ? "尚未加入课程，暂无学习路径"
                    : "请先创建课程以查看学习路径"
                  : "暂无学习路径数据"}
              </div>
            )}
          </div>
        </div>

        {/* Weak points bar chart */}
        <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-base font-bold text-slate-900 mb-6">{isStudent ? "我的薄弱知识点" : "班级薄弱知识点 Top 5"}</h3>
          <div className="h-[280px]">
            {weakPointData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weakPointData} layout="vertical" margin={{ top: 0, right: 20, left: -20, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} width={80} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                  <Bar dataKey="score" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={20}>
                    {weakPointData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.score < 40 ? '#ef4444' : '#f59e0b'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-sm text-slate-400">暂无薄弱知识点数据</div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Resource type distribution pie */}
        <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-base font-bold text-slate-900 mb-2">资源类型分布</h3>
          <div className="h-[200px]">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                    {pieData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-sm text-slate-400">暂无数据</div>
            )}
          </div>
        </div>

        {/* Invocation trend line */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-base font-bold text-slate-900 mb-2">{isStudent ? "我的辅学调用趋势" : "本人智能体调用趋势"}</h3>
          <div className="h-[200px]">
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94A3B8' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94A3B8' }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="calls" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-sm text-slate-400">暂无调用数据</div>
            )}
          </div>
        </div>

        {/* Role-specific quality summary */}
        <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 flex flex-col justify-between">
          <h3 className="text-base font-bold text-slate-900 mb-4">{isStudent ? "我的学习概况" : "资源审核质量"}</h3>
          {isStudent ? (
            <>
              <div className="space-y-4 flex-1">
                {[
                  ["重点薄弱项", `${weakPointData.length} 个`],
                  ["进行中任务", `${overview?.active_tasks ?? 0} 项`],
                  ["可学习资源", `${overview?.resource_count ?? 0} 个`],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between border-b border-slate-100 pb-3 text-sm last:border-0">
                    <span className="text-slate-500">{label}</span>
                    <span className="font-bold text-slate-800">{value}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 border-t border-slate-100 pt-4 text-center text-xs text-slate-500">
                仅统计当前账号的学习记录
              </div>
            </>
          ) : reviewRates && reviewRates.length > 0 ? (
            <>
              <div className="space-y-4 flex-1">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-500">通过资源数</span>
                    <span className="font-bold text-emerald-600">{totalApproved}</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${totalReviewed > 0 ? Math.round((totalApproved / totalReviewed) * 100) : 0}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-500">退回修改数</span>
                    <span className="font-bold text-orange-600">{totalRejected}</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full">
                    <div className="h-full bg-orange-500 rounded-full" style={{ width: `${totalReviewed > 0 ? Math.round((totalRejected / totalReviewed) * 100) : 0}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-500">涉及课程数</span>
                    <span className="font-bold text-blue-600">{reviewRates.length}</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: "100%" }} />
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-slate-100">
                <div className="text-xs text-slate-500 text-center">
                  平均审核通过率 <span className="font-bold text-slate-800 text-sm ml-1">{formatPct(avgPassRate)}</span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center flex-1 text-sm text-slate-400">暂无审核数据</div>
          )}
        </div>
      </div>
    </div>
  );
}
