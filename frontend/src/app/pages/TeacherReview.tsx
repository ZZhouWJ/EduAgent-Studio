import React from "react";
import { CheckCircle2, AlertCircle, AlertTriangle, MessageSquare, ShieldCheck, XCircle } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { reviewsApi, ReviewRequest, ReviewDetail } from "@/lib/api";
import { notify } from "@/lib/toast";
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

function ReviewCard({ item, selected, onClick }: {
  item: ReviewRequest;
  selected: boolean;
  onClick: () => void;
}) {
  const isHighRisk = item.request_status === "high_risk" || item.request_status === "pending_high";
  return (
    <div
      onClick={onClick}
      className={`cursor-pointer rounded-xl border p-4 transition-all ${
        selected
          ? "bg-blue-50 border-blue-200 shadow-sm"
          : "bg-white border-slate-200 hover:border-blue-300 hover:shadow-md"
      }`}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className={`font-bold text-[15px] ${selected ? "text-blue-900" : "text-slate-800"}`}>
          {item.output_title || "—"}
        </h3>
        {isHighRisk && (
          <span className="shrink-0 rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-bold text-red-700">高风险</span>
        )}
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        <span className="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
          学生：{item.submitter_real_name || item.submitter_username || "—"}
        </span>
        <span className={`rounded px-2 py-0.5 text-[11px] font-bold ${
          item.request_status === "approved" ? "bg-emerald-50 text-emerald-700" :
          item.request_status === "rejected" ? "bg-red-50 text-red-700" :
          "bg-orange-50 text-orange-700"
        }`}>
          {item.request_status === "approved" ? "已通过" :
           item.request_status === "rejected" ? "已驳回" :
           item.request_status === "revision_required" ? "需修改" : "待审核"}
        </span>
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">{formatTimeAgo(item.created_at)}提交</span>
      </div>
    </div>
  );
}

export function TeacherReview() {
  const [selectedId, setSelectedId] = React.useState<number | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  // Form state
  const [accuracyScore, setAccuracyScore] = React.useState(5);
  const [completenessScore, setCompletenessScore] = React.useState(5);
  const [logicScore, setLogicScore] = React.useState(5);
  const [formatScore, setFormatScore] = React.useState(5);
  const [reviewComment, setReviewComment] = React.useState("");

  const { data: pendingData, loading: loadingPending, refetch: refetchPending } = useApi(
    () => reviewsApi.getPending({ page: 1, page_size: 50 }),
    []
  );
  const { data: detailData, loading: loadingDetail, refetch: refetchDetail } = useApi(
    () => selectedId != null ? reviewsApi.getById(selectedId) : Promise.resolve(null as ReviewDetail | null),
    [selectedId]
  );

  const pendingList = pendingData?.items ?? [];
  const currentItem = pendingList.find((r) => r.request_id === selectedId) ?? pendingList[0];
  const detail = detailData;

  const highRiskCount = pendingList.filter((r) => r.request_status === "pending_high" || r.request_status === "high_risk").length;

  const handleApprove = async () => {
    if (!selectedId) return;
    setSubmitting(true);
    try {
      await reviewsApi.complete(selectedId, {
        review_status: "approved",
        accuracy_score: accuracyScore,
        completeness_score: completenessScore,
        logic_score: logicScore,
        format_score: formatScore,
        review_comment: reviewComment,
      });
      notify.success("审核通过，已推送给学生");
      setReviewComment("");
      refetchPending();
      refetchDetail();
    } catch (e) {
      notify.error("操作失败：" + String(e));
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!selectedId) return;
    if (!reviewComment.trim()) {
      notify.warning("请填写驳回理由");
      return;
    }
    setSubmitting(true);
    try {
      await reviewsApi.complete(selectedId, {
        review_status: "revision_required",
        review_comment: reviewComment,
      });
      notify.success("已退回修改，学生会收到通知");
      setReviewComment("");
      refetchPending();
      refetchDetail();
    } catch (e) {
      notify.error("操作失败：" + String(e));
    } finally {
      setSubmitting(false);
    }
  };

  const handleSelectItem = (id: number) => {
    setSelectedId(id);
    setAccuracyScore(5);
    setCompletenessScore(5);
    setLogicScore(5);
    setFormatScore(5);
    setReviewComment("");
  };

  return (
    <div className="page-shell flex min-h-0 flex-col pb-6">
      {/* 页面内容直接开始 */}
      <div className="flex min-h-0 flex-1 flex-col gap-4 lg:flex-row lg:gap-6">
        {/* Left: Pending Review List */}
        <div className="flex w-full shrink-0 flex-col gap-4 lg:w-[400px]">
          <div className="mb-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-black text-slate-800">待审核资源 ({pendingList.length})</h2>
            <div className="flex gap-2">
              {highRiskCount > 0 && (
                <span className="rounded bg-red-50 px-2 py-1 text-xs font-bold text-red-600">{highRiskCount} 高风险</span>
              )}
              <span className="rounded bg-orange-50 px-2 py-1 text-xs font-bold text-orange-600">{pendingList.length - highRiskCount} 建议复核</span>
            </div>
          </div>

          <div className="custom-scrollbar flex-1 space-y-3 overflow-y-auto pb-4 pr-0 lg:pr-2">
            {loadingPending ? (
              <div className="flex h-32 items-center justify-center text-slate-400">加载中...</div>
            ) : pendingList.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-8 text-slate-400">
                <SafeLottie source="empty" className="h-20 w-28" speed={0.8} />
                <span className="text-sm">暂无待审核资源</span>
              </div>
            ) : (
              pendingList.map((item) => (
                <ReviewCard
                  key={item.request_id}
                  item={item}
                  selected={item.request_id === selectedId}
                  onClick={() => handleSelectItem(item.request_id)}
                />
              ))
            )}
          </div>
        </div>

        {/* Right: Review Detail Pane */}
        <div className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <div className="flex shrink-0 flex-col gap-3 border-b border-slate-100 bg-slate-50/50 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-6">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">待审核</span>
                <span className="text-sm text-slate-500">提交人：{currentItem?.submitter_real_name || currentItem?.submitter_username || "—"}</span>
              </div>
              <h2 className="text-xl font-black text-slate-900">{currentItem?.output_title || "—"}</h2>
            </div>
          </div>

          <div className="flex-1 space-y-6 overflow-y-auto p-4 sm:p-6">
            {loadingDetail && selectedId ? (
              <div className="flex h-48 items-center justify-center text-slate-400">加载详情中...</div>
            ) : detail ? (
              <>
                <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-6">
                  <div className="space-y-4">
                    <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
                      <h3 className="mb-2 flex items-center gap-2 font-bold text-emerald-800">
                        <ShieldCheck className="h-4 w-4" /> 内容预览
                      </h3>
                      <p className="whitespace-pre-wrap text-sm leading-relaxed text-emerald-700">
                        {detail.output_content?.slice(0, 500) || "—"}
                        {(detail.output_content?.length ?? 0) > 500 ? "..." : ""}
                      </p>
                    </div>

                    {detail.submit_note && (
                      <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                        <h3 className="mb-2 flex items-center gap-2 font-bold text-slate-800">
                          <MessageSquare className="h-4 w-4" /> 提交说明
                        </h3>
                        <p className="text-sm leading-relaxed text-slate-700">{detail.submit_note}</p>
                      </div>
                    )}
                  </div>

                  <div className="rounded-xl border border-orange-100 bg-orange-50 p-4">
                    <h3 className="mb-2 flex items-center gap-2 font-bold text-orange-800">
                      <AlertCircle className="h-4 w-4" /> 潜在风险提示
                    </h3>
                    <p className="text-sm leading-relaxed text-orange-700">
                      请根据资源内容判断是否存在事实准确性、引用覆盖率和难度适配性风险。
                    </p>
                    <button className="mt-3 self-start text-sm font-medium text-orange-600 hover:underline">
                      查看 AI 批注详情
                    </button>
                  </div>
                </div>

                <div className="border-t border-slate-100 pt-6">
                  <h3 className="mb-4 flex items-center gap-2 text-base font-black text-slate-900">
                    <CheckCircle2 className="h-5 w-5 text-blue-500" /> 教师审核表单
                  </h3>

                  <div className="max-w-3xl space-y-5">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      {[
                        { label: "内容准确性", score: accuracyScore, setter: setAccuracyScore },
                        { label: "内容完整性", score: completenessScore, setter: setCompletenessScore },
                        { label: "逻辑严谨性", score: logicScore, setter: setLogicScore },
                        { label: "格式规范性", score: formatScore, setter: setFormatScore },
                      ].map(({ label, score, setter }) => (
                        <div key={label}>
                          <label className="mb-2 block text-sm font-medium text-slate-700">{label}（{score}分）</label>
                          <input
                            type="range" min="1" max="5" value={score}
                            onChange={(e) => setter(Number(e.target.value))}
                            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-blue-600"
                          />
                          <div className="mt-1 flex justify-between text-xs text-slate-400">
                            <span>1分</span><span>3分</span><span>5分</span>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-700">审核意见 / 修改建议</label>
                      <textarea
                        className="edu-focus-ring h-24 w-full resize-none rounded-lg border border-slate-300 p-3 text-sm"
                        value={reviewComment}
                        onChange={(e) => setReviewComment(e.target.value)}
                        placeholder="填写审核意见（驳回时必须填写）"
                        aria-label="审核意见或修改建议"
                      />
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex h-48 flex-col items-center justify-center text-slate-400">
                <AlertTriangle className="mb-3 h-10 w-10" />
                <p className="text-sm">请从左侧选择一个待审核资源</p>
              </div>
            )}
          </div>

          {detail && (
            <div className="flex shrink-0 flex-col gap-3 border-t border-slate-100 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
              <label className="flex min-h-11 cursor-pointer items-center gap-2">
                <input type="checkbox" className="h-4 w-4 rounded text-blue-600 accent-blue-600" />
                <span className="text-sm font-medium text-slate-700">标记为优秀资源库模板</span>
              </label>

              <div className="flex flex-col gap-3 sm:flex-row">
                <button
                  onClick={handleReject}
                  disabled={submitting}
                  className="flex min-h-11 cursor-pointer items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-6 text-sm font-bold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
                >
                  <XCircle className="h-4 w-4" /> 退回修改
                </button>
                <button
                  onClick={handleApprove}
                  disabled={submitting}
                  className="flex min-h-11 cursor-pointer items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 text-sm font-bold text-white shadow-md shadow-blue-500/20 transition hover:bg-blue-700 disabled:opacity-60"
                >
                  {submitting ? "提交中..." : "审核通过并推送给学生"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
