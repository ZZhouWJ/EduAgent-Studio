import React from "react";
import {
  AlertTriangle,
  BookOpenCheck,
  CheckCircle2,
  ClipboardCheck,
  FileCheck2,
  MessageSquare,
  RotateCcw,
  XCircle,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import {
  resourcesApi,
  reviewsApi,
  type LearningResource,
  type ReviewDetail,
  type ReviewRequest,
} from "@/lib/api";
import { notify } from "@/lib/toast";
import { SafeLottie } from "../components/SafeLottie";
import { ResourceRenderer } from "../components/resource/ResourceRenderer";

type ReviewMode = "resource" | "project";
type ScoreKey = "accuracy" | "completeness" | "logic" | "format" | "usability";
type Scores = Record<ScoreKey, number>;

const DEFAULT_SCORES: Scores = {
  accuracy: 8,
  completeness: 8,
  logic: 8,
  format: 8,
  usability: 8,
};

const SCORE_FIELDS: Array<{ key: ScoreKey; label: string }> = [
  { key: "accuracy", label: "内容准确性" },
  { key: "completeness", label: "内容完整性" },
  { key: "logic", label: "逻辑严谨性" },
  { key: "format", label: "格式规范性" },
  { key: "usability", label: "教学可用性" },
];

const RESOURCE_TYPE_LABELS: Record<string, string> = {
  lecture: "课程讲义",
  mindmap: "思维导图",
  quiz: "练习题",
  case: "案例材料",
  code_case: "代码实操",
  ppt: "PPT 大纲",
  video_script: "视频脚本",
  experiment_report: "实验报告",
  error_analysis: "错题解析",
  learning_card: "学习卡片",
  review: "复习计划",
  test: "阶段测验",
  other: "其他",
};

const DIFFICULTY_LABELS: Record<string, string> = {
  basic: "基础",
  intermediate: "标准",
  advanced: "进阶",
};

function formatTimeAgo(dateStr?: string | null): string {
  if (!dateStr) return "刚刚";
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return dateStr;
  const diff = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (diff < 60) return `${diff}秒前`;
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  return `${Math.floor(diff / 86400)}天前`;
}

function ScoreFields({ scores, onChange }: { scores: Scores; onChange: (key: ScoreKey, value: number) => void }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {SCORE_FIELDS.map(({ key, label }) => (
        <div key={key}>
          <label className="mb-2 block text-sm font-medium text-slate-700">
            {label}（{scores[key]} 分）
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={scores[key]}
            onChange={(event) => onChange(key, Number(event.target.value))}
            aria-label={label}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-blue-600"
          />
          <div className="mt-1 flex justify-between text-xs text-slate-400">
            <span>1</span><span>5</span><span>10</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyReview({ message }: { message: string }) {
  return (
    <div className="flex h-48 flex-col items-center justify-center gap-2 text-slate-400">
      <SafeLottie source="empty" className="h-20 w-28" speed={0.8} />
      <span className="text-sm">{message}</span>
    </div>
  );
}

function ReviewError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex h-48 flex-col items-center justify-center gap-3 px-6 text-center">
      <AlertTriangle className="h-8 w-8 text-red-500" />
      <p className="text-sm text-slate-600">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 text-sm font-bold text-slate-700 hover:bg-slate-50"
      >
        <RotateCcw className="h-4 w-4" /> 重试
      </button>
    </div>
  );
}

function ResourceReviewCard({ item, selected, onClick }: {
  item: LearningResource;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-lg border p-4 text-left transition ${
        selected
          ? "border-blue-200 bg-blue-50 shadow-sm"
          : "border-slate-200 bg-white hover:border-blue-300 hover:shadow-sm"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className={`text-[15px] font-bold leading-5 ${selected ? "text-blue-900" : "text-slate-800"}`}>
          {item.resource_title}
        </h3>
        <span className="shrink-0 rounded bg-orange-50 px-2 py-0.5 text-[11px] font-bold text-orange-700">待审核</span>
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
        <span className="rounded bg-slate-100 px-2 py-0.5 font-medium text-slate-600">{item.course_name}</span>
        <span className="rounded bg-blue-50 px-2 py-0.5 font-medium text-blue-700">
          {RESOURCE_TYPE_LABELS[item.resource_type] ?? item.resource_type}
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-400">{formatTimeAgo(item.review_submitted_at ?? item.created_at)}提交</p>
    </button>
  );
}

function LearningResourceReviewPanel() {
  const [selectedId, setSelectedId] = React.useState<number | null>(null);
  const [scores, setScores] = React.useState<Scores>(DEFAULT_SCORES);
  const [reviewComment, setReviewComment] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);

  const pendingState = useApi(
    () => resourcesApi.list({ status: "pending_review", page: 1, page_size: 100 }),
    [],
  );
  const pendingList = pendingState.data?.items ?? [];

  React.useEffect(() => {
    if (pendingList.length === 0) {
      setSelectedId(null);
      return;
    }
    if (!selectedId || !pendingList.some((item) => item.resource_id === selectedId)) {
      setSelectedId(pendingList[0].resource_id);
    }
  }, [pendingList, selectedId]);

  const detailState = useApi(
    () => selectedId ? resourcesApi.getById(selectedId) : Promise.resolve(null),
    [selectedId],
  );
  const selectedSummary = pendingList.find((item) => item.resource_id === selectedId) ?? null;
  const detail = detailState.data;
  const pendingReview = detail?.review_history?.find((review) => review.review_status === "pending") ?? null;

  const handleSelect = (resourceId: number) => {
    setSelectedId(resourceId);
    setScores(DEFAULT_SCORES);
    setReviewComment("");
  };

  const finishReview = async (decision: "approved" | "rejected") => {
    if (!selectedId) return;
    if (decision === "rejected" && !reviewComment.trim()) {
      notify.warning("退回资源时必须填写审核意见");
      return;
    }

    setSubmitting(true);
    try {
      await resourcesApi.completeReview(selectedId, {
        decision,
        accuracy_score: decision === "approved" ? scores.accuracy : undefined,
        completeness_score: decision === "approved" ? scores.completeness : undefined,
        logic_score: decision === "approved" ? scores.logic : undefined,
        format_score: decision === "approved" ? scores.format : undefined,
        usability_score: decision === "approved" ? scores.usability : undefined,
        review_comment: reviewComment.trim() || undefined,
      });
      notify.success(decision === "approved" ? "资源审核通过，已向学生开放" : "资源已退回修改");
      setSelectedId(null);
      setReviewComment("");
      setScores(DEFAULT_SCORES);
      await pendingState.refetch();
    } catch (error) {
      notify.error(error instanceof Error ? error.message : "审核提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 lg:flex-row lg:gap-6">
      <aside className="flex w-full shrink-0 flex-col gap-3 lg:w-[380px]">
        <div className="flex items-center justify-between">
          <h2 className="font-black text-slate-800">待审核学习资源</h2>
          <span className="rounded bg-orange-50 px-2 py-1 text-xs font-bold text-orange-700">{pendingList.length} 项</span>
        </div>
        <div className="custom-scrollbar flex-1 space-y-3 overflow-y-auto pb-4 pr-0 lg:pr-2">
          {pendingState.loading ? (
            <div className="flex h-32 items-center justify-center text-sm text-slate-400">加载中...</div>
          ) : pendingState.error ? (
            <ReviewError message={pendingState.error.message} onRetry={() => void pendingState.refetch()} />
          ) : pendingList.length === 0 ? (
            <EmptyReview message="暂无待审核学习资源" />
          ) : pendingList.map((item) => (
            <ResourceReviewCard
              key={item.resource_id}
              item={item}
              selected={item.resource_id === selectedId}
              onClick={() => handleSelect(item.resource_id)}
            />
          ))}
        </div>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]" aria-label="学习资源审核详情">
        <header className="shrink-0 border-b border-slate-100 bg-slate-50/70 p-4 sm:p-6">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded bg-orange-100 px-2 py-0.5 font-bold text-orange-700">待审核</span>
            {selectedSummary && <span className="text-slate-500">{selectedSummary.course_name}</span>}
            {pendingReview && <span className="text-slate-500">送审人：{pendingReview.submitter_name}</span>}
          </div>
          <h2 className="mt-2 text-xl font-black text-slate-900">{selectedSummary?.resource_title ?? "选择一项资源开始审核"}</h2>
        </header>

        <div className="custom-scrollbar flex-1 overflow-y-auto">
          {detailState.loading && selectedId ? (
            <div className="flex h-48 items-center justify-center text-sm text-slate-400">加载详情中...</div>
          ) : detailState.error ? (
            <ReviewError message={detailState.error.message} onRetry={() => void detailState.refetch()} />
          ) : detail ? (
            <>
              <div className="border-b border-slate-100 p-4 sm:p-6">
                <div className="mb-4 flex flex-wrap gap-2 text-xs">
                  <span className="rounded bg-blue-50 px-2 py-1 font-medium text-blue-700">
                    {RESOURCE_TYPE_LABELS[detail.resource_type] ?? detail.resource_type}
                  </span>
                  <span className="rounded bg-slate-100 px-2 py-1 font-medium text-slate-600">
                    难度：{DIFFICULTY_LABELS[detail.difficulty] ?? detail.difficulty}
                  </span>
                  {detail.target_kp_names?.map((name) => (
                    <span key={name} className="rounded bg-emerald-50 px-2 py-1 font-medium text-emerald-700">{name}</span>
                  ))}
                </div>
                {pendingReview?.submit_note && (
                  <div className="mb-5 flex items-start gap-2 border-l-2 border-blue-300 pl-3 text-sm text-slate-600">
                    <MessageSquare className="mt-0.5 h-4 w-4 shrink-0 text-blue-500" />
                    <span>送审说明：{pendingReview.submit_note}</span>
                  </div>
                )}
                <ResourceRenderer resource={detail} />
              </div>

              <div className="p-4 sm:p-6">
                <h3 className="mb-5 flex items-center gap-2 text-base font-black text-slate-900">
                  <ClipboardCheck className="h-5 w-5 text-blue-600" /> 质量评价
                </h3>
                <div className="max-w-4xl space-y-5">
                  <ScoreFields
                    scores={scores}
                    onChange={(key, value) => setScores((current) => ({ ...current, [key]: value }))}
                  />
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="resource-review-comment">
                      审核意见 / 修改建议
                    </label>
                    <textarea
                      id="resource-review-comment"
                      value={reviewComment}
                      onChange={(event) => setReviewComment(event.target.value)}
                      maxLength={2000}
                      rows={4}
                      placeholder="记录事实核验、难度适配或教学使用建议（退回时必填）"
                      className="edu-focus-ring w-full resize-none rounded-lg border border-slate-300 p-3 text-sm"
                    />
                  </div>
                </div>
              </div>
            </>
          ) : (
            <EmptyReview message="请从左侧选择一个待审核学习资源" />
          )}
        </div>

        {detail && (
          <footer className="flex shrink-0 flex-col gap-3 border-t border-slate-100 bg-slate-50 p-4 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={() => void finishReview("rejected")}
              disabled={submitting}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-6 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
            >
              <XCircle className="h-4 w-4" /> 退回修改
            </button>
            <button
              type="button"
              onClick={() => void finishReview("approved")}
              disabled={submitting}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-blue-600 px-7 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-60"
            >
              <CheckCircle2 className="h-4 w-4" /> {submitting ? "提交中..." : "审核通过并开放"}
            </button>
          </footer>
        )}
      </section>
    </div>
  );
}

function ProjectReviewCard({ item, selected, onClick }: {
  item: ReviewRequest;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-lg border p-4 text-left transition ${
        selected ? "border-blue-200 bg-blue-50 shadow-sm" : "border-slate-200 bg-white hover:border-blue-300 hover:shadow-sm"
      }`}
    >
      <h3 className={`text-[15px] font-bold leading-5 ${selected ? "text-blue-900" : "text-slate-800"}`}>
        {item.output_title || "未命名输出"}
      </h3>
      <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
        <span className="rounded bg-slate-100 px-2 py-0.5 font-medium text-slate-600">
          提交人：{item.submitter_real_name || item.submitter_username || "—"}
        </span>
        <span className="rounded bg-orange-50 px-2 py-0.5 font-bold text-orange-700">待审核</span>
      </div>
      <p className="mt-3 text-xs text-slate-400">{formatTimeAgo(item.created_at)}提交</p>
    </button>
  );
}

function ProjectOutputReviewPanel() {
  const [selectedId, setSelectedId] = React.useState<number | null>(null);
  const [scores, setScores] = React.useState<Scores>(DEFAULT_SCORES);
  const [reviewComment, setReviewComment] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);

  const pendingState = useApi(() => reviewsApi.getPending({ page: 1, page_size: 50 }), []);
  const pendingList = pendingState.data?.items ?? [];

  React.useEffect(() => {
    if (pendingList.length === 0) {
      setSelectedId(null);
      return;
    }
    if (!selectedId || !pendingList.some((item) => item.request_id === selectedId)) {
      setSelectedId(pendingList[0].request_id);
    }
  }, [pendingList, selectedId]);

  const detailState = useApi(
    () => selectedId ? reviewsApi.getById(selectedId) : Promise.resolve(null as ReviewDetail | null),
    [selectedId],
  );
  const currentItem = pendingList.find((item) => item.request_id === selectedId) ?? null;

  const handleSelect = (requestId: number) => {
    setSelectedId(requestId);
    setScores(DEFAULT_SCORES);
    setReviewComment("");
  };

  const finishReview = async (reviewStatus: "approved" | "revision_required") => {
    if (!selectedId) return;
    if (reviewStatus === "revision_required" && !reviewComment.trim()) {
      notify.warning("退回输出时必须填写修改意见");
      return;
    }

    setSubmitting(true);
    try {
      await reviewsApi.complete(selectedId, {
        review_status: reviewStatus,
        accuracy_score: reviewStatus === "approved" ? scores.accuracy : undefined,
        completeness_score: reviewStatus === "approved" ? scores.completeness : undefined,
        logic_score: reviewStatus === "approved" ? scores.logic : undefined,
        format_score: reviewStatus === "approved" ? scores.format : undefined,
        usability_score: reviewStatus === "approved" ? scores.usability : undefined,
        review_comment: reviewComment.trim() || undefined,
      });
      notify.success(reviewStatus === "approved" ? "项目输出审核通过" : "项目输出已退回修改");
      setSelectedId(null);
      setReviewComment("");
      setScores(DEFAULT_SCORES);
      await pendingState.refetch();
    } catch (error) {
      notify.error(error instanceof Error ? error.message : "审核提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 lg:flex-row lg:gap-6">
      <aside className="flex w-full shrink-0 flex-col gap-3 lg:w-[380px]">
        <div className="flex items-center justify-between">
          <h2 className="font-black text-slate-800">待审核项目输出</h2>
          <span className="rounded bg-orange-50 px-2 py-1 text-xs font-bold text-orange-700">{pendingList.length} 项</span>
        </div>
        <div className="custom-scrollbar flex-1 space-y-3 overflow-y-auto pb-4 pr-0 lg:pr-2">
          {pendingState.loading ? (
            <div className="flex h-32 items-center justify-center text-sm text-slate-400">加载中...</div>
          ) : pendingState.error ? (
            <ReviewError message={pendingState.error.message} onRetry={() => void pendingState.refetch()} />
          ) : pendingList.length === 0 ? (
            <EmptyReview message="暂无待审核项目输出" />
          ) : pendingList.map((item) => (
            <ProjectReviewCard
              key={item.request_id}
              item={item}
              selected={item.request_id === selectedId}
              onClick={() => handleSelect(item.request_id)}
            />
          ))}
        </div>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]" aria-label="项目输出审核详情">
        <header className="shrink-0 border-b border-slate-100 bg-slate-50/70 p-4 sm:p-6">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded bg-orange-100 px-2 py-0.5 font-bold text-orange-700">待审核</span>
            {currentItem && (
              <span className="text-slate-500">提交人：{currentItem.submitter_real_name || currentItem.submitter_username || "—"}</span>
            )}
          </div>
          <h2 className="mt-2 text-xl font-black text-slate-900">{currentItem?.output_title ?? "选择一项输出开始审核"}</h2>
        </header>

        <div className="custom-scrollbar flex-1 overflow-y-auto">
          {detailState.loading && selectedId ? (
            <div className="flex h-48 items-center justify-center text-sm text-slate-400">加载详情中...</div>
          ) : detailState.error ? (
            <ReviewError message={detailState.error.message} onRetry={() => void detailState.refetch()} />
          ) : detailState.data ? (
            <>
              <div className="border-b border-slate-100 p-4 sm:p-6">
                {detailState.data.submit_note && (
                  <div className="mb-5 flex items-start gap-2 border-l-2 border-blue-300 pl-3 text-sm text-slate-600">
                    <MessageSquare className="mt-0.5 h-4 w-4 shrink-0 text-blue-500" />
                    <span>提交说明：{detailState.data.submit_note}</span>
                  </div>
                )}
                <div className="whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">
                  {detailState.data.output_content || "暂无输出内容"}
                </div>
              </div>
              <div className="p-4 sm:p-6">
                <h3 className="mb-5 flex items-center gap-2 text-base font-black text-slate-900">
                  <ClipboardCheck className="h-5 w-5 text-blue-600" /> 质量评价
                </h3>
                <div className="max-w-4xl space-y-5">
                  <ScoreFields
                    scores={scores}
                    onChange={(key, value) => setScores((current) => ({ ...current, [key]: value }))}
                  />
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="project-review-comment">
                      审核意见 / 修改建议
                    </label>
                    <textarea
                      id="project-review-comment"
                      value={reviewComment}
                      onChange={(event) => setReviewComment(event.target.value)}
                      maxLength={2000}
                      rows={4}
                      placeholder="记录审核结论或需要修改的内容（退回时必填）"
                      className="edu-focus-ring w-full resize-none rounded-lg border border-slate-300 p-3 text-sm"
                    />
                  </div>
                </div>
              </div>
            </>
          ) : (
            <EmptyReview message="请从左侧选择一个待审核项目输出" />
          )}
        </div>

        {detailState.data && (
          <footer className="flex shrink-0 flex-col gap-3 border-t border-slate-100 bg-slate-50 p-4 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={() => void finishReview("revision_required")}
              disabled={submitting}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-6 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
            >
              <XCircle className="h-4 w-4" /> 退回修改
            </button>
            <button
              type="button"
              onClick={() => void finishReview("approved")}
              disabled={submitting}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-blue-600 px-7 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-60"
            >
              <CheckCircle2 className="h-4 w-4" /> {submitting ? "提交中..." : "审核通过"}
            </button>
          </footer>
        )}
      </section>
    </div>
  );
}

export function TeacherReview() {
  const [mode, setMode] = React.useState<ReviewMode>("resource");

  return (
    <div className="page-shell flex min-h-0 flex-col gap-4 pb-6">
      <div className="flex shrink-0 items-center gap-1 self-start rounded-lg border border-slate-200 bg-white p-1" role="tablist" aria-label="审核类型">
        <button
          type="button"
          role="tab"
          aria-selected={mode === "resource"}
          onClick={() => setMode("resource")}
          className={`inline-flex min-h-10 items-center gap-2 rounded-md px-4 text-sm font-bold transition ${
            mode === "resource" ? "bg-blue-600 text-white" : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          <BookOpenCheck className="h-4 w-4" /> 学习资源
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "project"}
          onClick={() => setMode("project")}
          className={`inline-flex min-h-10 items-center gap-2 rounded-md px-4 text-sm font-bold transition ${
            mode === "project" ? "bg-blue-600 text-white" : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          <FileCheck2 className="h-4 w-4" /> 项目输出
        </button>
      </div>

      {mode === "resource" ? <LearningResourceReviewPanel /> : <ProjectOutputReviewPanel />}
    </div>
  );
}
