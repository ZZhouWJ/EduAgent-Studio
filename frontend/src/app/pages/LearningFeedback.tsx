import React from "react";
import { BookOpen, Clock, Target, Star, ChevronRight, HelpCircle, FileText, CheckCircle2, PlayCircle, PlusCircle, MessageSquare, RefreshCw } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { feedbackApi } from "@/lib/api";
import { useInlineToast } from "../components/common/ProductUI";

export function LearningFeedback() {
  const { toast, showToast } = useInlineToast();
  const [selfMastery, setSelfMastery] = React.useState("一般");
  const [rating, setRating] = React.useState(3);
  const [hasDoubt, setHasDoubt] = React.useState(true);
  const [notes, setNotes] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);

  const { data: feedbackData, loading } = useApi(() => feedbackApi.list({ page: 1, page_size: 20 }), []);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await feedbackApi.submit({
        feedback_type: "self_assessment",
        content: notes,
        self_mastery: selfMastery === "较高" ? 3 : selfMastery === "一般" ? 2 : 1,
        difficulty_rating: rating >= 4 ? "easy" : rating >= 2 ? "medium" : "hard",
      });
      showToast("反馈已提交，画像将自动更新");
      setNotes("");
      setRating(3);
      setSelfMastery("一般");
      setHasDoubt(true);
    } catch {
      showToast("提交失败，请重试");
    } finally {
      setSubmitting(false);
    }
  };

  const latestFeedback = feedbackData?.items?.[0];

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto pb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">学习反馈与测评</h1>
        <p className="text-slate-500 mt-1 text-sm">跟踪学生学习效果，驱动画像更新和个性化资源推荐。</p>
      </div>

      {/* Top: Current Task & Result */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-blue-50 to-transparent pointer-events-none"></div>
        
        <div className="flex items-center gap-2 mb-4">
          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-bold">当前任务</span>
        </div>
        {loading ? (
          <div className="text-slate-400 text-sm py-4">加载中...</div>
        ) : latestFeedback ? (
          <>
            <h2 className="text-xl font-bold text-slate-900 mb-6">{latestFeedback.resource_title || "学习反馈"}</h2>
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px] p-4 bg-slate-50 border border-slate-100 rounded-xl flex items-start gap-3">
                <BookOpen className="w-5 h-5 text-blue-500 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-slate-900 mb-1">课程</div>
                  <div className="text-sm text-slate-600">{latestFeedback.course_name}</div>
                </div>
              </div>
              <div className="flex-1 min-w-[150px] p-4 bg-slate-50 border border-slate-100 rounded-xl flex items-start gap-3">
                <Target className="w-5 h-5 text-red-500 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-slate-900 mb-1">自评掌握度</div>
                  <div className="text-sm font-bold text-slate-700">{latestFeedback.self_mastery ?? 2}/3</div>
                </div>
              </div>
              <div className="flex-1 min-w-[200px] p-4 bg-slate-50 border border-slate-100 rounded-xl flex items-start gap-3">
                <HelpCircle className="w-5 h-5 text-purple-500 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-slate-900 mb-1">反馈类型</div>
                  <div className="text-sm text-slate-600">{latestFeedback.feedback_type}</div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-xl font-bold text-slate-900 mb-6">暂无反馈记录</h2>
          </>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Middle: Feedback Form */}
        <div className="flex-1 bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            学生自评与反馈
          </h3>

          <div className="space-y-6 max-w-2xl">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">理解程度自评</label>
                <div className="flex gap-2">
                  {(["较高", "一般", "较低"] as const).map((level) => (
                    <button
                      key={level}
                      onClick={() => setSelfMastery(level)}
                      className={`flex-1 py-2 border rounded-lg text-sm transition-colors ${
                        selfMastery === level
                          ? level === "较高"
                            ? "bg-emerald-50 border-emerald-200 text-emerald-700 font-bold"
                            : level === "一般"
                            ? "bg-slate-100 border-slate-300 text-slate-700 font-bold"
                            : "bg-orange-50 border-orange-200 text-orange-700 font-bold"
                          : "bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">资源满意度</label>
                <div className="flex items-center gap-2 h-10">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      onClick={() => setRating(star)}
                      className={`w-6 h-6 cursor-pointer transition-colors ${star <= rating ? "text-yellow-400 fill-yellow-400" : "text-slate-200"}`}
                    />
                  ))}
                  <span className="ml-2 text-sm text-slate-500">{rating} 星</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-3">是否仍有疑问</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="doubt"
                    checked={hasDoubt === true}
                    onChange={() => setHasDoubt(true)}
                    className="text-blue-600 w-4 h-4 focus:ring-blue-500"
                  />
                  <span className="text-sm text-slate-700">是，还需要进一步学习</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="doubt"
                    checked={hasDoubt === false}
                    onChange={() => setHasDoubt(false)}
                    className="text-blue-600 w-4 h-4 focus:ring-blue-500"
                  />
                  <span className="text-sm text-slate-700">否，已经基本掌握</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-3">学习备注 / 难点描述</label>
              <textarea
                className="w-full h-24 p-3 rounded-lg border border-slate-300 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm resize-none bg-slate-50"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="请描述学习中的难点..."
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="h-10 px-8 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg font-bold shadow-md shadow-blue-500/20 transition-colors"
            >
              {submitting ? "提交中..." : "提交反馈"}
            </button>
          </div>
        </div>

        {/* Right: AI Analysis & Update */}
        <div className="w-full lg:w-[400px] shrink-0 space-y-6">
          <div className="bg-gradient-to-br from-indigo-900 to-slate-900 rounded-2xl p-6 shadow-lg border border-indigo-800 text-white">
            <h3 className="text-base font-bold mb-4 flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-indigo-400" />
              画像更新建议
            </h3>
            <ul className="space-y-3 text-sm text-indigo-100">
              <li className="flex items-start gap-2">
                <ChevronRight className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <span>事务隔离级别掌握度从 38% <span className="text-red-400 font-bold">下调为 32%</span></span>
              </li>
              <li className="flex items-start gap-2">
                <ChevronRight className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <span>标记“幻读”为核心薄弱概念</span>
              </li>
              <li className="flex items-start gap-2">
                <ChevronRight className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <span>推荐更基础的图解讲义</span>
              </li>
              <li className="flex items-start gap-2">
                <ChevronRight className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <span>推荐增加判断题和银行转账并发案例</span>
              </li>
            </ul>
            <div className="mt-5 pt-4 border-t border-indigo-800 flex justify-end">
              <button className="h-8 px-4 bg-indigo-500 hover:bg-indigo-400 text-white text-xs font-bold rounded flex items-center gap-1 transition-colors">
                <CheckCircle2 className="w-3.5 h-3.5" /> 确认更新画像
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Recommended Next Steps */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
        <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
          <Target className="w-5 h-5 text-emerald-600" />
          下一步推荐资源 (基于反馈生成)
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { title: "基础图解讲义（幻读专题）", type: "讲义", icon: FileText, c: "text-blue-500", bg: "bg-blue-50" },
            { title: "幻读与不可重复读判断题", type: "题库", icon: CheckCircle2, c: "text-purple-500", bg: "bg-purple-50" },
            { title: "银行转账脏读实操案例", type: "案例", icon: BookOpen, c: "text-emerald-500", bg: "bg-emerald-50" },
            { title: "四种隔离级别动画分镜脚本", type: "视频", icon: PlayCircle, c: "text-orange-500", bg: "bg-orange-50" },
          ].map((res, i) => {
            const Icon = res.icon;
            return (
              <div key={i} className="group p-4 rounded-xl border border-slate-200 hover:border-emerald-300 hover:shadow-md transition-all cursor-pointer bg-white">
                <div className={`w-8 h-8 rounded-lg ${res.bg} flex items-center justify-center mb-3`}>
                  <Icon className={`w-4 h-4 ${res.c}`} />
                </div>
                <h4 className="font-bold text-slate-800 text-sm mb-2 leading-snug group-hover:text-emerald-700 transition-colors">{res.title}</h4>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">{res.type}</span>
                  <PlusCircle className="w-4 h-4 text-slate-300 group-hover:text-emerald-500 transition-colors" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
    {toast}
  );
}
