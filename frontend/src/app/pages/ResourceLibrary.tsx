import React from "react";
import { Search, Filter, FileText, CheckCircle2, AlertCircle, PlayCircle, Code, ListTree, MoreVertical } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi } from "@/lib/api";
import { SafeLottie } from "../components/SafeLottie";

function formatTimeAgo(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (diff < 60) return `${diff}秒前`;
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    return `${Math.floor(diff / 86400)}天前`;
  } catch {
    return dateStr;
  }
}

function resourceIcon(type: string) {
  const t = (type ?? "").toLowerCase();
  if (t.includes("讲义") || t.includes("文档")) return FileText;
  if (t.includes("练习") || t.includes("题库")) return ListTree;
  if (t.includes("代码") || t.includes("案例")) return Code;
  if (t.includes("视频") || t.includes("动画")) return PlayCircle;
  return FileText;
}

const STATUS_LABELS: Record<string, string> = {
  approved: "已通过",
  pending: "待审核",
  rejected: "被退回",
  draft: "草稿",
};

export function ResourceLibrary() {
  const [typeFilter, setTypeFilter] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("");
  const [courseFilter, setCourseFilter] = React.useState("");
  const [keyword, setKeyword] = React.useState("");

  const { data, loading } = useApi(
    () => resourcesApi.list({
      type: typeFilter || undefined,
      course_id: courseFilter ? Number(courseFilter) : undefined,
      page_size: 100,
    }),
    [typeFilter, statusFilter, courseFilter]
  );
  const coursesState = useApi(() => learningApi.listCourses(), []);

  const courses = coursesState.data ?? [];

  const resources = (data?.items ?? []).map((r) => ({
    id: r.resource_id,
    title: r.resource_title,
    type: r.resource_type || "资源",
    course: r.course_name,
    status: STATUS_LABELS[r.status] ?? r.status,
    rawStatus: r.status,
    difficulty: r.difficulty || "—",
    time: formatTimeAgo(r.created_at),
    icon: resourceIcon(r.resource_type ?? ""),
  }));

  // Dynamic tabs from real data
  const allTypes = Array.from(new Set(resources.map((r) => r.type))).filter(Boolean);
  const tabs = ["全部", ...allTypes];

  const filtered = resources.filter((r) => {
    const statusMatch = !statusFilter || r.rawStatus === statusFilter;
    const keywordMatch = !keyword || r.title.toLowerCase().includes(keyword.toLowerCase());
    return statusMatch && keywordMatch;
  });

  return (
    <div className="mx-auto flex h-full max-w-[1400px] flex-col space-y-6 pb-6">
      <div className="shrink-0">
        <h1 className="text-2xl font-black text-slate-900">学习资源库</h1>
        <p className="mt-1 text-sm text-slate-500">统一管理由多智能体生成并经教师审核的个性化学习资源。</p>
      </div>

      {/* Filters */}
      <div className="flex shrink-0 items-center justify-between gap-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
        <div className="flex items-center gap-2 flex-1">
          <div className="relative w-full max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              aria-label="搜索资源标题"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="h-9 w-full cursor-text pl-9 pr-3 rounded-lg border border-slate-200 bg-slate-50 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              placeholder="搜索资源标题..."
            />
          </div>
          <select
            className="h-9 cursor-pointer rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm"
            value={courseFilter}
            onChange={(e) => setCourseFilter(e.target.value)}
          >
            <option value="">所有课程</option>
            {courses.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <select
            className="h-9 cursor-pointer rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">全部状态</option>
            <option value="approved">已通过</option>
            <option value="pending">待审核</option>
            <option value="rejected">被退回</option>
          </select>
        </div>
        <button className="flex h-9 cursor-pointer items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 text-sm font-medium text-slate-600 transition hover:bg-slate-50">
          <Filter className="h-4 w-4" /> 更多筛选
        </button>
      </div>

      {/* Type Tabs */}
      <div className="flex shrink-0 gap-2 border-b border-slate-200">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setTypeFilter(tab === "全部" ? "" : tab)}
            className={`cursor-pointer border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
              (tab === "全部" && !typeFilter) || typeFilter === tab
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Resource Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 py-10 text-slate-400">
          <SafeLottie source="empty" className="h-24 w-32" speed={0.8} />
          <span className="text-sm">暂无资源</span>
        </div>
      ) : (
        <div className="auto-rows-max grid grid-cols-1 gap-4 overflow-y-auto min-h-0 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((res) => {
            const Icon = res.icon;
            const statusColor =
              res.rawStatus === "approved" ? "text-emerald-600" :
              res.rawStatus === "pending" ? "text-orange-600" : "text-red-600";
            return (
              <div
                key={res.id}
                className="group flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] transition-all hover:-translate-y-1 hover:shadow-lg"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
                    <Icon className="h-5 w-5 cursor-pointer text-blue-500" />
                  </div>
                  <button className="text-slate-400 opacity-0 transition-opacity group-hover:opacity-100">
                    <MoreVertical className="h-5 w-5 cursor-pointer" />
                  </button>
                </div>

                <h3 className="mb-2 line-clamp-2 text-[15px] font-black leading-tight text-slate-900">{res.title}</h3>

                <div className="mb-4 flex flex-wrap gap-1.5">
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">{res.course}</span>
                  <span className="rounded bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-600">{res.type}</span>
                </div>

                <div className="mt-auto mb-4 space-y-2.5">
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>难度</span>
                    <span className="font-medium text-slate-700">{res.difficulty}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-slate-100 pt-3">
                  <div className="flex items-center gap-1.5">
                    {res.rawStatus === "approved" && <CheckCircle2 className="h-4 w-4 cursor-pointer text-emerald-500" />}
                    {res.rawStatus === "pending" && <AlertCircle className="h-4 w-4 cursor-pointer text-orange-500" />}
                    {res.rawStatus === "rejected" && <AlertCircle className="h-4 w-4 cursor-pointer text-red-500" />}
                    <span className={`text-xs font-bold ${statusColor}`}>{res.status}</span>
                  </div>
                  <span className="text-[11px] text-slate-400">{res.time}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
