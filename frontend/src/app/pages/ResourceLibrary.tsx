import React from "react";
import { useSearchParams } from "react-router-dom";
import { Search, FileText, CheckCircle2, AlertCircle, PlayCircle, Code, ListTree, X, Calendar, BookOpen, Archive, Send, History, LoaderCircle } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi } from "@/lib/api";
import { notify } from "@/lib/toast";
import { useAuthStore } from "@/stores/auth";
import { SafeLottie } from "../components/SafeLottie";
import { ResourceRenderer } from "../components/resource/ResourceRenderer";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerClose } from "../components/ui/drawer";
import { PageHero } from "../components/common/PageHero";

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
  if (["quiz", "test", "error_analysis", "learning_card"].includes(t)) return ListTree;
  if (["code_case", "case", "experiment_report"].includes(t)) return Code;
  if (t === "video_script") return PlayCircle;
  return FileText;
}

const RESOURCE_TYPE_OPTIONS = [
  { value: "", label: "全部" },
  { value: "lecture", label: "课程讲义" },
  { value: "mindmap", label: "思维导图" },
  { value: "quiz", label: "练习题" },
  { value: "case", label: "案例材料" },
  { value: "code_case", label: "代码实操" },
  { value: "ppt", label: "PPT 大纲" },
  { value: "video_script", label: "视频脚本" },
  { value: "experiment_report", label: "实验报告" },
  { value: "error_analysis", label: "错题解析" },
  { value: "learning_card", label: "学习卡片" },
  { value: "review", label: "复习计划" },
  { value: "test", label: "阶段测验" },
  { value: "other", label: "其他" },
] as const;

const RESOURCE_TYPE_LABELS = Object.fromEntries(
  RESOURCE_TYPE_OPTIONS.filter((item) => item.value).map((item) => [item.value, item.label]),
) as Record<string, string>;

const DIFFICULTY_LABELS: Record<string, string> = {
  basic: "基础",
  intermediate: "标准",
  advanced: "进阶",
};

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
  const [submitNote, setSubmitNote] = React.useState("");
  const [submittingReview, setSubmittingReview] = React.useState(false);
  const requestedKpId = Number(searchParams.get("kp_id")) || 0;
  const requestedKpName = searchParams.get("kp_name") ?? "";
  const user = useAuthStore((state) => state.user);
  const isAdmin = user?.roles?.includes("admin") ?? false;
  const isTeacher = user?.roles?.includes("teacher") ?? false;
  const canManageReviews = isTeacher || isAdmin;
  const pageRole = isAdmin ? "admin" : isTeacher ? "teacher" : "student";
  const pageCopy = isAdmin
    ? {
        eyebrow: "资源管理",
        description: "查看全平台课程资源，按课程、类型与审核状态定位内容并跟踪审核记录。",
      }
    : isTeacher
      ? {
          eyebrow: "教学资源",
          description: "管理本人课程资源，查看生成内容、审核状态与历史记录，并将草稿提交审核。",
        }
      : {
          eyebrow: "推荐资源",
          description: "浏览与你当前课程和学习进度匹配的已审核资源，并按类型或课程快速筛选。",
        };

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

  const { data: drawerResource, loading: detailLoading, refetch: refetchDetail } = useApi(
    () => selectedResource ? resourcesApi.getById(selectedResource.id) : Promise.resolve(null),
    [selectedResource?.id]
  );

  const handleResourceClick = (resource: typeof resources[0]) => {
    if (!resource?.id) return
    setSelectedResource(resource)
    const next = new URLSearchParams(searchParams);
    next.set("resource", String(resource.id));
    setSearchParams(next, { replace: true });
  }

  const { data, loading, refetch: refetchResources } = useApi(
    () => resourcesApi.list({
      type: typeFilter || undefined,
      status: statusFilter || undefined,
      course_id: Number(courseFilter) || undefined,
      kp_id: requestedKpId || undefined,
      page_size: 100,
    }),
    [typeFilter, statusFilter, courseFilter, requestedKpId]
  );
  const coursesState = useApi(() => learningApi.listCourses(), []);

  const courses = coursesState.data ?? [];

  const resources = React.useMemo(() => (data?.items ?? []).map((r) => ({
    id: r.resource_id,
    title: r.resource_title,
    type: RESOURCE_TYPE_LABELS[r.resource_type] ?? r.resource_type ?? "资源",
    course: r.course_name,
    status: STATUS_LABELS[r.status] ?? r.status,
    rawStatus: r.status,
    difficulty: DIFFICULTY_LABELS[r.difficulty] ?? r.difficulty ?? "—",
    time: formatTimeAgo(r.created_at),
    icon: resourceIcon(r.resource_type ?? ""),
  })), [data?.items]);

  const requestedResourceId = Number(searchParams.get("resource")) || 0;

  const clearKnowledgePointFilter = () => {
    const next = new URLSearchParams(searchParams);
    next.delete("kp_id");
    next.delete("kp_name");
    setSearchParams(next, { replace: true });
  };

  React.useEffect(() => {
    if (!requestedResourceId || loading) return;
    const requested = resources.find((resource) => resource.id === requestedResourceId);
    if (requested) {
      setSelectedResource((current) => current?.id === requested.id ? current : requested);
      return;
    }
    const next = new URLSearchParams(searchParams);
    next.delete("resource");
    setSearchParams(next, { replace: true });
  }, [loading, requestedResourceId, resources, searchParams, setSearchParams]);

  const filtered = resources.filter((r) => {
    const statusMatch = !statusFilter || r.rawStatus === statusFilter;
    const keywordMatch = !keyword || r.title.toLowerCase().includes(keyword.toLowerCase());
    return statusMatch && keywordMatch;
  });

  const handleSubmitReview = async () => {
    if (!drawerResource || !canManageReviews) return;
    setSubmittingReview(true);
    try {
      await resourcesApi.submitReview(drawerResource.resource_id, submitNote);
      notify.success("资源已提交审核");
      setSubmitNote("");
      await Promise.all([refetchDetail(), refetchResources()]);
    } catch (error) {
      notify.error(error instanceof Error ? error.message : "提交审核失败");
    } finally {
      setSubmittingReview(false);
    }
  };

  return (
    <div className="mx-auto flex h-full max-w-[1400px] flex-col space-y-6 pb-6">
      <PageHero
        eyebrow={pageCopy.eyebrow}
        title="学习资源库"
        description={pageCopy.description}
        icon={BookOpen}
        role={pageRole}
      />
      {/* Filters */}
      <div className="flex shrink-0 flex-col items-stretch justify-between gap-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-[0_8px_24px_rgba(15,23,42,0.04)] sm:flex-row sm:items-center">
        <div className="flex flex-1 flex-col items-stretch gap-2 sm:flex-row sm:items-center">
          <div className="relative w-full sm:max-w-xs">
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
            aria-label="筛选课程"
            className="h-9 w-full cursor-pointer rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm sm:w-auto"
            value={courseFilter}
            onChange={(e) => handleCourseFilterChange(e.target.value)}
          >
            <option value="">所有课程</option>
            {courses.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <select
            aria-label="筛选状态"
            className="h-9 w-full cursor-pointer rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm sm:w-auto"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">全部状态</option>
            <option value="draft">草稿</option>
            <option value="approved">已通过</option>
            <option value="pending_review">待审核</option>
            <option value="rejected">被退回</option>
            <option value="archived">已归档</option>
          </select>
        </div>
        {requestedKpId > 0 && (
          <div className="flex min-h-9 items-center justify-between gap-2 rounded-lg bg-emerald-50 px-3 text-xs font-bold text-emerald-800 sm:justify-start">
            <span className="truncate">知识点：{requestedKpName || `#${requestedKpId}`}</span>
            <button type="button" onClick={clearKnowledgePointFilter} aria-label="清除知识点筛选" className="rounded p-1 hover:bg-emerald-100">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Type Tabs */}
      <div className="flex shrink-0 gap-2 overflow-x-auto border-b border-slate-200">
        {RESOURCE_TYPE_OPTIONS.map((tab) => (
          <button
            key={tab.value || "all"}
            onClick={() => setTypeFilter(tab.value)}
            className={`shrink-0 cursor-pointer border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
              typeFilter === tab.value
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Resource Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 py-10 text-slate-400">
          <SafeLottie source="empty" className="h-24 w-32" speed={0.8} />
          <span className="text-sm">{requestedKpId ? "当前知识点暂无已审核资源" : "暂无资源"}</span>
        </div>
      ) : (
        <div className="auto-rows-max grid grid-cols-1 gap-4 overflow-y-auto min-h-0 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((res) => {
            const Icon = res.icon;
            const statusColor =
              res.rawStatus === "approved" ? "text-emerald-600" :
              res.rawStatus === "pending_review" ? "text-orange-600" :
              res.rawStatus === "rejected" ? "text-red-600" : "text-slate-600";
            return (
              <div
                key={res.id}
                onClick={() => handleResourceClick(res)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    handleResourceClick(res);
                  }
                }}
                role="button"
                tabIndex={0}
                aria-label={`查看资源：${res.title}`}
                className="group flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] transition-all hover:-translate-y-1 hover:shadow-lg cursor-pointer"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
                    <Icon className="h-5 w-5 cursor-pointer text-blue-500" />
                  </div>
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
                    {res.rawStatus === "draft" && <FileText className="h-4 w-4 text-slate-500" />}
                    {res.rawStatus === "archived" && <Archive className="h-4 w-4 text-slate-500" />}
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
      <Drawer
        open={!!selectedResource}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedResource(null);
            setSubmitNote("");
            const next = new URLSearchParams(searchParams);
            next.delete("resource");
            setSearchParams(next, { replace: true });
          }
        }}
      >
        <DrawerContent className="max-h-[85vh]">
          <DrawerHeader>
            <DrawerTitle className="text-lg font-black">{selectedResource?.title}</DrawerTitle>
            <DrawerClose asChild>
              <button aria-label="关闭资源详情" className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
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
                    {RESOURCE_TYPE_LABELS[drawerResource.resource_type] ?? drawerResource.resource_type}
                  </span>
                  <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                    <Calendar className="h-3 w-3" />
                    {new Date(drawerResource.created_at).toLocaleDateString("zh-CN")}
                  </span>
                  <span className={`inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-bold ${
                    drawerResource.status === "approved" ? "bg-emerald-50 text-emerald-700" :
                    drawerResource.status === "pending_review" ? "bg-orange-50 text-orange-700" :
                    drawerResource.status === "rejected" ? "bg-red-50 text-red-700" :
                    "bg-slate-100 text-slate-600"
                  }`}>
                    {STATUS_LABELS[drawerResource.status] ?? drawerResource.status}
                  </span>
                </div>
                <ResourceRenderer resource={drawerResource} />

                {canManageReviews && (drawerResource.review_history?.length ?? 0) > 0 && (
                  <section className="mt-6 border-t border-slate-200 pt-5" aria-labelledby="resource-review-history">
                    <h3 id="resource-review-history" className="mb-3 flex items-center gap-2 text-sm font-black text-slate-900">
                      <History className="h-4 w-4 text-slate-500" /> 审核记录
                    </h3>
                    <div className="space-y-4">
                      {drawerResource.review_history?.map((review) => (
                        <div key={review.review_id} className="border-l-2 border-slate-200 pl-4">
                          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
                            <span className={`font-bold ${
                              review.review_status === "approved" ? "text-emerald-700" :
                              review.review_status === "rejected" ? "text-red-700" : "text-orange-700"
                            }`}>
                              {review.review_status === "approved" ? "审核通过" : review.review_status === "rejected" ? "退回修改" : "等待审核"}
                            </span>
                            <span className="text-slate-500">
                              {new Date(review.submitted_at).toLocaleString("zh-CN")}
                            </span>
                            <span className="text-slate-500">送审人：{review.submitter_name}</span>
                            {review.reviewer_name && <span className="text-slate-500">审核人：{review.reviewer_name}</span>}
                          </div>
                          {review.submit_note && <p className="mt-2 text-sm text-slate-600">送审说明：{review.submit_note}</p>}
                          {review.review_comment && <p className="mt-2 text-sm font-medium text-slate-700">审核意见：{review.review_comment}</p>}
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {canManageReviews && ["draft", "rejected"].includes(drawerResource.status) && (
                  <section className="mt-6 border-t border-slate-200 pt-5" aria-labelledby="submit-resource-review">
                    <h3 id="submit-resource-review" className="text-sm font-black text-slate-900">提交教师审核</h3>
                    <p className="mt-1 text-xs leading-5 text-slate-500">提交后资源进入待审核状态，通过后才会出现在学生资源库。</p>
                    <label className="mt-3 block text-xs font-medium text-slate-700" htmlFor="resource-submit-note">送审说明（可选）</label>
                    <textarea
                      id="resource-submit-note"
                      value={submitNote}
                      onChange={(event) => setSubmitNote(event.target.value)}
                      maxLength={500}
                      rows={3}
                      placeholder="说明适用对象、教学目标或需要重点核验的内容"
                      className="edu-focus-ring mt-2 w-full resize-none rounded-lg border border-slate-300 p-3 text-sm text-slate-800"
                    />
                    <div className="mt-3 flex justify-end">
                      <button
                        type="button"
                        onClick={handleSubmitReview}
                        disabled={submittingReview}
                        className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {submittingReview ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                        {submittingReview ? "提交中..." : "提交审核"}
                      </button>
                    </div>
                  </section>
                )}

                {canManageReviews && drawerResource.status === "pending_review" && (
                  <div className="mt-6 flex items-start gap-2 border-t border-slate-200 pt-5 text-sm text-orange-700">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    资源正在等待教师审核，审核完成前不会向学生开放。
                  </div>
                )}
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
