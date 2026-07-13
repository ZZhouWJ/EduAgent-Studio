import React, { useState, useEffect } from "react";
import { User, Target, Book, Brain, Library, AlertTriangle, XCircle, Clock, Wrench, RefreshCw, History } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { profilesApi } from "@/lib/api";

export function StudentProfile() {
  // 学生端：直接获取当前登录用户的画像，不暴露选择器
  const { data: profile, loading: profileLoading, refetch: reloadProfile } = useApi(
    () => profilesApi.getMyProfile(),
    []
  );

  // 画像更新记录
  const [updateRecords, setUpdateRecords] = useState<any[]>([]);
  const [loadingRecords, setLoadingRecords] = useState(false);

  // 加载画像更新记录
  useEffect(() => {
    if (profile && typeof profile === 'object' && 'profile_id' in profile) {
      setLoadingRecords(true);
      profilesApi.getFeedbackHistory((profile as any).profile_id)
        .then(res => setUpdateRecords(res.data || []))
        .catch(console.error)
        .finally(() => setLoadingRecords(false));
    } else {
      setUpdateRecords([]);
    }
  }, [profile]);

  if (profileLoading) {
    return (
      <div className="flex flex-col gap-6 max-w-[1400px] mx-auto">
        <div className="text-slate-400 p-12 text-center">加载画像数据中...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-[1600px] mx-auto min-h-full py-6">
      {/* 三栏布局：占满剩余高度 */}
      <div className="flex gap-6 flex-col xl:flex-row items-stretch flex-1 min-h-0">
        {/* Left: Basic Info */}
        <div className="w-full xl:w-[280px] bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 xl:shrink-0 flex flex-col">
          <div className="flex flex-col items-center mb-6 shrink-0">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center border-4 border-white shadow-md mb-3">
              <User className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">{(profile as any)?.student_name ?? "学生"}</h2>
            <div className="flex items-center gap-2 mt-1.5">
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">学号: {(profile as any)?.student_no ?? "N/A"}</span>
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-600">{(profile as any)?.course_name ?? "课程"}</span>
            </div>
          </div>

          <div className="space-y-4 flex-1">
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">当前课程</div>
              <div className="text-sm font-semibold text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-100">
                {(profile as any)?.course_name ?? "暂无课程"}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">学习目标</div>
              <div className="text-sm text-slate-700">{(profile as any)?.learning_goal ?? "暂无目标"}</div>
            </div>
            <div>
              <div className="flex justify-between items-end mb-1">
                <div className="text-xs font-medium text-slate-500">综合掌握度</div>
                <div className="text-sm font-bold text-blue-600">{Math.round(((profile as any)?.mastery_score ?? 0) * 100)}%</div>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.round(((profile as any)?.mastery_score ?? 0) * 100)}%` }}></div>
              </div>
            </div>
          </div>

          <div className="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span>画像更新时间</span>
            <span>{(profile as any)?.last_updated ? String((profile as any).last_updated).split("T")[0] : "N/A"}</span>
          </div>
        </div>

        {/* Middle: Dimensions Grid */}
        <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4 min-h-0 h-full">
          {[
            {
              icon: Book, title: "知识基础", color: "text-blue-500", bg: "bg-blue-50",
              items: (profile as any)?.strong_points?.map((p: any) => p.kp_name || p.name || "未知").concat(
                (profile as any)?.weak_points?.slice(0, 1).map((p: any) => `薄弱: ${p.kp_name || p.name}`) ?? []
              ).slice(0, 2) ?? ["暂无数据"],
              source: "基于测验得分和薄弱点分析计算得出"
            },
            {
              icon: Target, title: "学习目标", color: "text-purple-500", bg: "bg-purple-50",
              items: [(profile as any)?.learning_goal ?? "暂无目标"].concat((profile as any)?.interests ?? []).slice(0, 2),
              source: "根据学习对话和自评反馈提取"
            },
            {
              icon: Brain, title: "认知风格", color: "text-indigo-500", bg: "bg-indigo-50",
              items: ((profile as any)?.preferences ?? []).slice(0, 2).length > 0 ? (profile as any).preferences.slice(0, 2) : ["暂无偏好数据"],
              source: "从学习行为和资源使用偏好推断"
            },
            {
              icon: Library, title: "资源偏好", color: "text-emerald-500", bg: "bg-emerald-50",
              items: ((profile as any)?.resource_preferences ?? []).slice(0, 3).length > 0 ? (profile as any).resource_preferences.slice(0, 3) : ["暂无偏好"],
              source: "根据历史学习记录和反馈统计"
            },
            {
              icon: AlertTriangle, title: "薄弱知识点", color: "text-orange-500", bg: "bg-orange-50",
              items: ((profile as any)?.weak_points ?? []).map((p: any) => {
                const val = typeof p.mastery === 'number' && p.mastery <= 1 ? Math.round(p.mastery * 100) : (p.mastery ?? 0);
                return `${p.kp_name || p.name || "未知"} (${val}%)`;
              }).slice(0, 3) || ["暂无薄弱点"],
              source: "来自测验结果和作业表现分析"
            },
            {
              icon: XCircle, title: "当前水平", color: "text-red-500", bg: "bg-red-50",
              items: [(profile as any)?.current_level ?? "暂无评估"].concat(
                (profile as any)?.weak_points?.[0]?.reason ? [`原因: ${(profile as any).weak_points[0].reason}`] : []
              ).slice(0, 2),
              source: "综合历次测验和作业得分评定"
            },
            {
              icon: Clock, title: "学习时间约束", color: "text-cyan-500", bg: "bg-cyan-50",
              items: (profile as any)?.weekly_hours ? [`每周 ${(profile as any).weekly_hours} 小时`] : ["暂无时间数据"],
              source: "根据学习计划和自评信息记录"
            },
            {
              icon: Wrench, title: "实践能力水平", color: "text-teal-500", bg: "bg-teal-50",
              items: ((profile as any)?.interests ?? []).slice(0, 2).length > 0 ? (profile as any).interests.slice(0, 2) : ["暂无实践数据"],
              source: "从代码练习和项目作业中评估"
            }
          ].map((dim, idx) => {
            const Icon = dim.icon;
            return (
              <div key={idx} className="bg-white rounded-2xl p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 flex flex-col flex-1 min-h-0">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-8 h-8 rounded-lg ${dim.bg} flex items-center justify-center`}>
                    <Icon className={`w-4 h-4 ${dim.color}`} />
                  </div>
                  <h3 className="font-bold text-slate-800">{dim.title}</h3>
                </div>

                <div className="flex-1 space-y-1.5 mb-4">
                  {dim.items.map((item: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${dim.color.replace('text-', 'bg-')}`}></div>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-auto text-[10px] text-slate-400 leading-relaxed">
                  {dim.source}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Profile Update Records */}
        <div className="w-full xl:w-[180px] bg-white rounded-2xl flex flex-col shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 xl:shrink-0 min-h-0">
          <div className="p-5 border-b border-slate-100 flex items-center gap-2 bg-gradient-to-r from-blue-50 to-transparent rounded-t-2xl shrink-0">
            <History className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-900">画像更新记录</h2>
            <button
              onClick={reloadProfile}
              className="ml-auto p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              title="刷新"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {/* 更新记录列表 */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50/50 min-h-0">
            {loadingRecords && (
              <div className="text-center text-slate-400 text-sm py-8">
                <div className="w-6 h-6 border-2 border-slate-300 border-t-blue-500 rounded-full animate-spin mx-auto mb-2"></div>
                加载中...
              </div>
            )}

            {!loadingRecords && updateRecords.length === 0 && (
              <div className="text-center text-slate-400 text-sm py-8">
                <History className="w-10 h-10 mx-auto mb-2 opacity-50" />
                <p>暂无更新记录</p>
                <p className="text-xs mt-1">完成学习任务并提交反馈后，这里将显示画像更新历史</p>
              </div>
            )}

            {updateRecords.map((record) => {
              const feedbackTypeColors: Record<string, string> = {
                quiz_result: "bg-emerald-50 border-emerald-200 text-emerald-800",
                self_report: "bg-blue-50 border-blue-200 text-blue-800",
                study_note: "bg-purple-50 border-purple-200 text-purple-800",
                question: "bg-orange-50 border-orange-200 text-orange-800",
              };
              const colorClass = feedbackTypeColors[record.feedback_type] || "bg-slate-50 border-slate-200 text-slate-800";

              const date = new Date(record.created_at);
              const dateStr = date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
              const timeStr = date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });

              return (
                <div key={record.feedback_id} className={`rounded-xl border p-4 ${colorClass}`}>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <div className="font-medium text-sm">{record.feedback_type_label}</div>
                      <div className="text-xs opacity-70">{record.course_name}</div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs font-medium">{dateStr}</div>
                      <div className="text-[10px] opacity-60">{timeStr}</div>
                    </div>
                  </div>

                  {record.quiz_score != null && (
                    <div className="flex items-center gap-1.5 text-xs mb-1">
                      <span className="opacity-70">测验得分</span>
                      <span className="font-bold">{(record.quiz_score * 100).toFixed(0)}%</span>
                    </div>
                  )}

                  {record.self_mastery != null && (
                    <div className="flex items-center gap-1.5 text-xs mb-1">
                      <span className="opacity-70">自评掌握度</span>
                      <span className="font-bold">{(record.self_mastery * 100).toFixed(0)}%</span>
                    </div>
                  )}

                  {record.difficulty_rating && (
                    <div className="flex items-center gap-1.5 text-xs mb-1">
                      <span className="opacity-70">难度评价</span>
                      <span className="font-medium">
                        {record.difficulty_rating === "too_easy" ? "太简单" :
                         record.difficulty_rating === "too_hard" ? "太难" : "适中"}
                      </span>
                    </div>
                  )}

                  {record.resource_title && (
                    <div className="text-xs opacity-70 mt-1">
                      关联资源：{record.resource_title}
                    </div>
                  )}

                  {record.content && (
                    <div className="text-xs mt-2 pt-2 border-t border-current/10 line-clamp-2 opacity-80">
                      {record.content}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* 底部说明 */}
          <div className="p-4 border-t border-slate-100 bg-slate-50 rounded-b-2xl shrink-0">
            <p className="text-xs text-slate-400 text-center">
              画像根据学习反馈自动更新，无需手动编辑
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
