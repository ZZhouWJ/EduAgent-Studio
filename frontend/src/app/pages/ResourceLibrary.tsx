import React from "react";
import { useSearchParams } from "react-router-dom";
import { Search, FileText, CheckCircle2, AlertCircle, PlayCircle, Code, ListTree, MoreVertical, X, Calendar, BookOpen } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi } from "@/lib/api";
import { SafeLottie } from "../components/SafeLottie";
import { ResourceRenderer } from "../components/resource/ResourceRenderer";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerClose } from "../components/ui/drawer";

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
  pending_review: "待审核",
  rejected: "被退回",
  draft: "草稿",
  archived: "已归档",
};

export function ResourceLibrary() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [typeFilter, setTypeFilter] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("");
  const [courseFilter, setCourseFilter] = React.useState(() => searchParams.get("course") ?? "");
  const [keyword, setKeyword] = React.useState("");
  const [selectedResource, setSelectedResource] = React.useState<(typeof resources)[0] | null>(null);

  React.useEffect(() => {
    const course = searchParams.get("course") ?? "";
    setCourseFilter((current) => current === course ? current : course);
  }, [searchParams]);

  const handleCourseFilterChange = (value: string) => {
    setCourseFilter(value);
    const next = new URLSearchParams(searchParams);
    if (value) next.set("course", value);
    else next.delete("course");
    setSearchParams(next, { replace: true });
  };

  const { data: drawerResource, loading: detailLoading } = useApi(
    () => selectedResource ? resourcesApi.getById(selectedResource.id) : Promise.resolve(null),
    [selectedResource?.id]
  );

  const handleResourceClick = (resource: typeof resources[0]) => {
    if (!resource?.id) return
    setSelectedResource(resource)
  }

  const { data, loading } = useApi(
    () => resourcesApi.list({
      type: typeFilter || undefined,
      status: statusFilter || undefined,
      course_id: Number(courseFilter) || undefined,
      page_size: 100,
    }),
    [typeFilter, courseFilter]
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
            onChange={(e) => handleCourseFilterChange(e.target.value)}
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
            <option value="pending_review">待审核</option>
            <option value="rejected">被退回</option>
          </select>
        </div>
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
              res.rawStatus === "pending_review" ? "text-orange-600" : "text-red-600";
            return (
              <div
                key={res.id}
                onClick={() => handleResourceClick(res)}
                className="group flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] transition-all hover:-translate-y-1 hover:shadow-lg cursor-pointer"
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
                    {res.rawStatus === "pending_review" && <AlertCircle className="h-4 w-4 cursor-pointer text-orange-500" />}
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

      {/* Detail Drawer */}
      <Drawer open={!!selectedResource} onOpenChange={(open) => !open && setSelectedResource(null)}>
        <DrawerContent className="max-h-[85vh]">
          <DrawerHeader>
            <DrawerTitle className="text-lg font-black">{selectedResource?.title}</DrawerTitle>
            <DrawerClose asChild>
              <button className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
                <X className="h-5 w-5" />
              </button>
            </DrawerClose>
          </DrawerHeader>
          <div className="flex-1 overflow-y-auto p-4">
            {detailLoading ? (
              <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
            ) : drawerResource ? (
              <>
                <div className="mb-4 flex flex-wrap gap-2">
                  <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                    <BookOpen className="h-3 w-3" />
                    {drawerResource.course_name}
                  </span>
                  <span className="inline-flex items-center gap-1 rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-600">
                    {drawerResource.resource_type}
                  </span>
                  <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                    <Calendar className="h-3 w-3" />
                    {new Date(drawerResource.created_at).toLocaleDateString("zh-CN")}
                  </span>
                </div>
                <ResourceRenderer resource={drawerResource} />
              </>
            ) : (
              <div className="text-center text-slate-400 py-8">暂无详情</div>
            )}
          </div>
        </DrawerContent>
      </Drawer>
    </div>
  );
}
