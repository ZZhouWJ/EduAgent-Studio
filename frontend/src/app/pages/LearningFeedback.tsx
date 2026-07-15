import React from "react";
import { Link } from "react-router-dom";
import { BookOpen, Target, Star, ChevronRight, HelpCircle, FileText, CheckCircle2, PlayCircle, PlusCircle, MessageSquare, RefreshCw, BookOpenCheck, ListTree } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { feedbackApi, resourcesApi, statisticsApi } from "@/lib/api";
import type { MasteryChange, RecommendedResource } from "@/lib/api/learning";
import { notify } from "@/lib/toast";

function resourceIcon(type: string) {
  const t = (type ?? "").toLowerCase();
  if (t.includes("讲义") || t.includes("文档")) return FileText;
  if (t.includes("练习") || t.includes("题目")) return CheckCircle2;
  if (t.includes("代码") || t.includes("案例")) return BookOpenCheck;
  if (t.includes("视频") || t.includes("动画")) return PlayCircle;
  if (t.includes("思维导图") || t.includes("图")) return ListTree;
  return BookOpen;
}

const MASTERY_LABELS = ["", "较低", "一般", "较高"];
const DIFFICULTY_LABELS: Record<string, string> = {
  too_easy: "太简单",
  appropriate: "适中",
  too_hard: "太难",
};

export function LearningFeedback() {
  const [selfMastery, setSelfMastery] = React.useState<"较高" | "一般" | "较低">("一般");
  const [rating, setRating] = React.useState(3);
  const [hasDoubt, setHasDoubt] = React.useState(true);
  const [notes, setNotes] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [masteryChanges, setMasteryChanges] = React.useState<MasteryChange[] | null>(null);
  const [nextResources, setNextResources] = React.useState<RecommendedResource[] | null>(null);

  const { data: feedbackData, loading } = useApi(() => feedbackApi.list({ page: 1, page_size: 20 }), []);
  const { data: weakPoints } = useApi(() => statisticsApi.weakKnowledgePoints(5), []);
  const { data: resourcesData } = useApi(() => resourcesApi.list({ page_size: 4 }), []);

  const latestFeedback = feedbackData?.items?.[0];
  const resourceCards = (resourcesData?.items ?? []).map((r) => ({
    id: r.resource_id,
    title: r.resource_title,
    type: r.resource_type || "资源",
    icon: resourceIcon(r.resource_type),
  }));

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const result = await feedbackApi.submit({
        feedback_type: "self_assessment",
        content: notes,
        self_mastery: selfMastery === "较高" ? 3 : selfMastery === "一般" ? 2 : 1,
        difficulty_rating: rating >= 4 ? "appropriate" : rating >= 2 ? "appropriate" : "too_hard",
      });
      notify.success("反馈已提交，画像将自动更新");
      if (result) {
        setMasteryChanges(result.mastery_changes ?? []);
        setNextResources(result.next_resources ?? []);
      }
      setNotes("");
      setRating(3);
      setSelfMastery("一般");
      setHasDoubt(true);
    } catch (e) {
      notify.error("提交失败：" + String(e));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 pb-6">
      {/* Current Feedback / Latest */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
        <div className="absolute top-0 right-0 h-full w-64 bg-gradient-to-l from-blue-50 to-transparent pointer-events-none" />
        <div className="mb-4 flex items-center gap-2">
          <span className="rounded bg-blue-100 px-2 py-1 text-xs font-bold text-blue-700">当前任务</span>
        </div>
        {loading ? (
          <div className="py-4 text-sm text-slate-400">加载中...</div>
        ) : latestFeedback ? (
          <>
            <h2 className="mb-6 text-xl font-black text-slate-900">{latestFeedback.resource_title || "学习反馈"}</h2>
            <div className="flex flex-wrap gap-4">
              <div className="flex min-w-[200px] flex-1 items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                <BookOpen className="mt-0.5 h-5 w-5 cursor-pointer text-blue-500" />
                <div>
                  <div className="mb-1 text-sm font-medium text-slate-900">课程</div>
                  <div className="text-sm text-slate-600">{latestFeedback.course_name}</div>
                </div>
              </div>
              <div className="flex min-w-[150px] flex-1 items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                <Target className="mt-0.5 h-5 w-5 cursor-pointer text-red-500" />
                <div>
                  <div className="mb-1 text-sm font-medium text-slate-900">自评掌握度</div>
                  <div className="text-sm font-bold text-slate-700">{MASTERY_LABELS[latestFeedback.self_mastery ?? 2] ?? "—"}（{latestFeedback.self_mastery ?? 2}/3）</div>
                </div>
              </div>
              <div className="flex min-w-[200px] flex-1 items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                <HelpCircle className="mt-0.5 h-5 w-5 cursor-pointer text-purple-500" />
                <div>
                  <div className="mb-1 text-sm font-medium text-slate-900">反馈类型</div>
                  <div className="text-sm text-slate-600">{latestFeedback.feedback_type}</div>
                </div>
              </div>
              {latestFeedback.difficulty_rating && (
                <div className="flex min-w-[150px] flex-1 items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <Star className="mt-0.5 h-5 w-5 cursor-pointer text-yellow-500" />
                  <div>
                    <div className="mb-1 text-sm font-medium text-slate-900">难度评价</div>
                    <div className="text-sm text-slate-600">{DIFFICULTY_LABELS[latestFeedback.difficulty_rating] ?? latestFeedback.difficulty_rating}</div>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <h2 className="mb-6 text-xl font-black text-slate-900">暂无反馈记录</h2>
        )}
      </div>

      <div className="flex flex-col gap-6 lg:flex-row">
        {/* Middle: Feedback Form */}
        <div className="flex-1 rounded-2xl border border-slate-100 bg-white p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <h3 className="mb-6 flex items-center gap-2 text-lg font-black text-slate-900">
            <MessageSquare className="h-5 w-5 cursor-pointer text-blue-600" />
            学生自评与反馈
          </h3>

          <div className="max-w-2xl space-y-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="mb-3 block text-sm font-medium text-slate-700">理解程度自评</label>
                <div className="flex gap-2">
                  {(["较高", "一般", "较低"] as const).map((level) => (
                    <button
                      key={level}
                      onClick={() => setSelfMastery(level)}
                      className={`flex-1 cursor-pointer rounded-lg border py-2 text-sm transition-colors ${
                        selfMastery === level
                          ? level === "较高"
                            ? "border-emerald-200 bg-emerald-50 font-bold text-emerald-700"
                            : level === "一般"
                            ? "border-slate-300 bg-slate-100 font-bold text-slate-700"
                            : "border-orange-200 bg-orange-50 font-bold text-orange-700"
                          : "border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="mb-3 block text-sm font-medium text-slate-700">资源满意度</label>
                <div className="flex h-10 items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      onClick={() => setRating(star)}
                      className={`h-6 w-6 cursor-pointer transition-colors ${star <= rating ? "fill-yellow-400 text-yellow-400" : "text-slate-200"}`}
                    />
                  ))}
                  <span className="ml-2 text-sm text-slate-500">{rating} 星</span>
                </div>
              </div>
            </div>

            <div>
              <label className="mb-3 block text-sm font-medium text-slate-700">是否仍有疑问</label>
              <div className="flex gap-4">
                {[{ label: "是，还需要进一步学习", val: true }, { label: "否，已经基本掌握", val: false }].map(({ label, val }) => (
                  <label key={label} className="flex cursor-pointer items-center gap-2">
                    <input
                      type="radio"
                      name="doubt"
                      checked={hasDoubt === val}
                      onChange={() => setHasDoubt(val)}
                      className="h-4 w-4 cursor-pointer accent-blue-600"
                    />
                    <span className="text-sm text-slate-700">{label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-3 block text-sm font-medium text-slate-700">学习备注 / 难点描述</label>
              <textarea
                className="edu-focus-ring h-24 w-full resize-none rounded-lg border border-slate-300 bg-slate-50 p-3 text-sm"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="请描述学习中的难点..."
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex h-10 cursor-pointer items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 font-bold text-white shadow-md shadow-blue-500/20 transition-colors hover:bg-blue-700 disabled:bg-blue-300"
            >
              {submitting ? "提交中..." : "提交反馈"}
            </button>

            {/* 画像已更新 */}
            {masteryChanges && masteryChanges.length > 0 && (
              <div className="edu-card bg-emerald-50 p-4 mt-4">
                <h4 className="font-bold text-emerald-800">✅ 画像已更新</h4>
                <div className="mt-2 space-y-1">
                  {masteryChanges.map((change, i) => (
                    <div key={i} className="text-sm">
                      <span className="font-medium">{change.kp_name}</span>
                      <span className="text-slate-500">: </span>
                      <span className="text-emerald-600">{Math.round(change.before * 100)}%</span>
                      <span className="text-slate-400"> → </span>
                      <span className="text-emerald-600 font-bold">{Math.round(change.after * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 推荐资源已调整 */}
            {nextResources && nextResources.length > 0 && (
              <div className="edu-card bg-blue-50 p-4 mt-4">
                <h4 className="font-bold text-blue-800">📚 推荐资源已调整</h4>
                <p className="text-sm text-blue-600 mt-1">基于你的反馈，系统推荐以下资源：</p>
                <div className="mt-2 space-y-2">
                  {nextResources.map((r) => (
                    <div key={r.resource_id} className="flex items-center justify-between bg-white rounded-lg p-2">
                      <div>
                        <span className="font-medium text-slate-800">{r.title}</span>
                        <span className="text-xs text-slate-500 ml-2">{r.type}</span>
                      </div>
                      <span className="text-xs text-blue-600">{r.reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right: Profile Suggestions */}
        <div className="w-full shrink-0 space-y-4 lg:w-[400px]">
          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            <h3 className="mb-4 flex items-center gap-2 text-base font-semibold text-slate-900">
              <RefreshCw className="h-5 w-5 cursor-pointer text-slate-500" />
              画像更新建议
            </h3>
            {weakPoints && weakPoints.length > 0 ? (
              <ul className="space-y-3 text-sm text-slate-700">
                {weakPoints.map((kp) => (
                  <li key={kp.kp_id} className="flex items-start gap-2">
                    <ChevronRight className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer text-slate-400" />
                    <span>
                      <span className="font-semibold text-red-600">{kp.kp_name}</span> 掌握度
                      <span className="font-semibold text-red-600"> {Math.round(kp.avg_mastery * 100)}%</span>
                      ，建议优先复习
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">暂无薄弱知识点数据</p>
            )}
            <div className="mt-5 flex items-center justify-end border-t border-slate-100 pt-4">
              <button
                onClick={() => notify.success("画像已确认更新")}
                className="flex h-9 cursor-pointer items-center gap-1 rounded-lg bg-slate-900 px-4 text-xs font-semibold text-white transition-colors hover:bg-slate-800"
              >
                <CheckCircle2 className="h-3.5 w-3.5" /> 确认更新画像
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Recommended Resources */}
      <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
        <h3 className="mb-6 flex cursor-pointer items-center gap-2 text-lg font-black text-slate-900">
          <Target className="h-5 w-5 text-emerald-600" />
          下一步推荐资源（基于反馈生成）
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {resourceCards.length > 0 ? resourceCards.map((res) => {
            const Icon = res.icon;
            return (
              <Link
                key={res.id}
                to={`/student/resources/${res.id}`}
                className="group cursor-pointer rounded-xl border border-slate-200 bg-white p-4 transition-all hover:-translate-y-1 hover:border-emerald-300 hover:shadow-md"
              >
                <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                  <Icon className="h-4 w-4 cursor-pointer text-blue-500" />
                </div>
                <h4 className="mb-2 min-h-[40px] text-sm font-black leading-snug text-slate-800 transition-colors group-hover:text-emerald-700">{res.title}</h4>
                <div className="mt-4 flex items-center justify-between">
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">{res.type}</span>
                  <PlusCircle className="h-4 w-4 text-slate-300 transition-colors group-hover:text-emerald-500" />
                </div>
              </Link>
            );
          }) : (
            <div className="col-span-4 flex flex-col items-center justify-center py-12 text-center">
              <BookOpen className="mb-3 h-10 w-10 cursor-pointer text-slate-300" />
              <p className="text-sm font-medium text-slate-400">暂无推荐资源</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
