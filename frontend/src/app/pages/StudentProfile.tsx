import React from "react";
import { User, Target, Book, Brain, Library, AlertTriangle, XCircle, Clock, Wrench, RefreshCw, MessageCircle, ArrowRight } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { profilesApi } from "@/lib/api";

export function StudentProfile() {
  const { data, loading } = useApi(() => profilesApi.list({ page: 1, page_size: 1 }), []);
  const profile = data?.items?.[0];

  if (loading) {
    return (
      <div className="flex flex-col gap-6 max-w-[1400px] mx-auto">
        <div className="text-slate-400 p-12 text-center">加载画像数据中...</div>
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">学生画像</h1>
        <p className="text-slate-500 mt-1 text-sm">通过自然语言对话、学习行为和测评反馈动态构建学生画像。</p>
      </div>

      <div className="flex gap-6 flex-col xl:flex-row items-start">
        {/* Left: Basic Info */}
        <div className="w-full xl:w-[280px] bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 shrink-0">
          <div className="flex flex-col items-center mb-6">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center border-4 border-white shadow-md mb-3">
              <User className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">{profile?.student_name ?? "学生"}</h2>
            <div className="flex items-center gap-2 mt-1.5">
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">学号: {profile?.student_no ?? "N/A"}</span>
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-600">{profile?.course_name ?? "课程"}</span>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">当前课程</div>
              <div className="text-sm font-semibold text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-100">
                {profile?.course_name ?? "暂无课程"}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">学习目标</div>
              <div className="text-sm text-slate-700">{profile?.learning_goal ?? "暂无目标"}</div>
            </div>
            <div>
              <div className="flex justify-between items-end mb-1">
                <div className="text-xs font-medium text-slate-500">综合掌握度</div>
                <div className="text-sm font-bold text-blue-600">{profile?.mastery_score ?? 0}%</div>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${profile?.mastery_score ?? 0}%` }}></div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span>画像更新时间</span>
            <span>{profile?.last_updated?.split("T")[0] ?? "N/A"}</span>
          </div>
        </div>

        {/* Middle: Dimensions Grid */}
        <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            {
              icon: Book, title: "知识基础", color: "text-blue-500", bg: "bg-blue-50",
              items: profile?.strong_points?.map((p) => p.kp_name || p.name || "未知").concat(
                profile?.weak_points?.slice(0, 1).map((p) => `薄弱: ${p.kp_name || p.name}`) ?? []
              ).slice(0, 2) ?? ["暂无数据"],
              conf: profile?.mastery_score ?? 0
            },
            {
              icon: Target, title: "学习目标", color: "text-purple-500", bg: "bg-purple-50",
              items: [profile?.learning_goal ?? "暂无目标"].concat(profile?.interests ?? []).slice(0, 2),
              conf: 92
            },
            {
              icon: Brain, title: "认知风格", color: "text-indigo-500", bg: "bg-indigo-50",
              items: profile?.preferences?.slice(0, 2) ?? ["暂无偏好数据"],
              conf: 81
            },
            {
              icon: Library, title: "资源偏好", color: "text-emerald-500", bg: "bg-emerald-50",
              items: profile?.resource_preferences?.slice(0, 3) ?? ["暂无偏好"],
              conf: 85
            },
            {
              icon: AlertTriangle, title: "薄弱知识点", color: "text-orange-500", bg: "bg-orange-50",
              items: profile?.weak_points?.map((p) => `${p.kp_name || p.name} (${p.mastery}%)`).slice(0, 3) ?? ["暂无薄弱点"],
              conf: profile?.weak_points?.[0]?.mastery ?? 90
            },
            {
              icon: XCircle, title: "当前水平", color: "text-red-500", bg: "bg-red-50",
              items: [profile?.current_level ?? "暂无评估"].concat(
                profile?.weak_points?.[0]?.reason ? [`原因: ${profile.weak_points[0].reason}`] : []
              ).slice(0, 2),
              conf: 78
            },
            {
              icon: Clock, title: "学习时间约束", color: "text-cyan-500", bg: "bg-cyan-50",
              items: profile?.weekly_hours ? [`每周 ${profile.weekly_hours} 小时`] : ["暂无时间数据"],
              conf: 74
            },
            {
              icon: Wrench, title: "实践能力水平", color: "text-teal-500", bg: "bg-teal-50",
              items: profile?.interests?.slice(0, 2) ?? ["暂无实践数据"],
              conf: 80
            }
          ].map((dim, idx) => {
            const Icon = dim.icon;
            return (
              <div key={idx} className="bg-white rounded-2xl p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 flex flex-col">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-8 h-8 rounded-lg ${dim.bg} flex items-center justify-center`}>
                    <Icon className={`w-4 h-4 ${dim.color}`} />
                  </div>
                  <h3 className="font-bold text-slate-800">{dim.title}</h3>
                </div>
                
                <div className="flex-1 space-y-1.5 mb-4">
                  {dim.items.map((item, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${dim.color.replace('text-', 'bg-')}`}></div>
                      {item}
                    </div>
                  ))}
                </div>

                <div className="mt-auto">
                  <div className="flex justify-between items-end mb-1">
                    <div className="text-xs text-slate-400">置信度</div>
                    <div className={`text-xs font-bold ${dim.color}`}>{dim.conf}%</div>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${dim.color.replace('text-', 'bg-')}`} style={{ width: `${dim.conf}%` }}></div>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-2 text-right">来源：学习对话 / 历史测验</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Conversational Profile Builder */}
        <div className="w-full xl:w-[340px] bg-white rounded-2xl flex flex-col shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 shrink-0 h-[680px]">
          <div className="p-5 border-b border-slate-100 flex items-center gap-2 bg-gradient-to-r from-blue-50 to-transparent rounded-t-2xl">
            <MessageCircle className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-900">画像构建对话</h2>
          </div>

          <div className="flex-1 p-5 overflow-y-auto space-y-5 bg-slate-50/50">
            {/* Student Message */}
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                <User className="w-4 h-4 text-blue-600" />
              </div>
              <div className="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700 leading-relaxed">
                我现在学数据库，SQL 查询还可以，但事务和并发控制不太懂；我更喜欢案例讲解，不太喜欢纯理论；希望两周内完成课程复习。
              </div>
            </div>

            {/* System Message */}
            <div className="flex gap-3 flex-row-reverse">
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center shrink-0">
                <Brain className="w-4 h-4 text-purple-600" />
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white p-3 rounded-2xl rounded-tr-none shadow-sm text-sm leading-relaxed">
                已从你的描述中抽取 5 个画像特征：知识基础、薄弱点、资源偏好、学习目标、时间约束。
              </div>
            </div>

            {/* Extraction Results */}
            <div className="bg-white border border-blue-100 rounded-xl p-4 shadow-sm ml-11">
              <div className="text-xs font-bold text-blue-800 mb-3 pb-2 border-b border-blue-50">本次抽取结果</div>
              <ul className="space-y-2 text-sm">
                <li className="flex gap-2 text-slate-600"><span className="text-blue-500 font-medium shrink-0">薄弱点：</span>事务、并发控制</li>
                <li className="flex gap-2 text-slate-600"><span className="text-blue-500 font-medium shrink-0">偏好：</span>案例讲解</li>
                <li className="flex gap-2 text-slate-600"><span className="text-blue-500 font-medium shrink-0">目标：</span>两周复习</li>
                <li className="flex gap-2 text-slate-600"><span className="text-blue-500 font-medium shrink-0">建议资源：</span>图解讲义 + 代码案例 + 分层练习题</li>
              </ul>
            </div>
          </div>

          <div className="p-4 border-t border-slate-100 bg-white rounded-b-2xl space-y-2">
            <div className="relative">
              <input 
                type="text" 
                aria-label="继续输入学习情况"
                className="w-full h-10 pl-3 pr-10 rounded-lg bg-slate-50 border border-slate-200 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 text-blue-600 hover:text-blue-700">
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
            <div className="flex gap-2 pt-2">
              <button className="flex-1 h-9 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1">
                <RefreshCw className="w-3.5 h-3.5" /> 更新画像
              </button>
              <button className="flex-1 h-9 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
                生成路径
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Knowledge Mastery */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
        <h2 className="text-lg font-bold text-slate-900 mb-5">知识点掌握度</h2>
        <div className="flex flex-wrap gap-4">
          {[
            { name: "SQL 查询", val: 82, color: "bg-emerald-500", bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" },
            { name: "FastAPI 接口设计", val: 61, color: "bg-yellow-500", bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200" },
            { name: "索引优化", val: 55, color: "bg-orange-500", bg: "bg-orange-50", text: "text-orange-700", border: "border-orange-200" },
            { name: "多表连接", val: 46, color: "bg-orange-500", bg: "bg-orange-50", text: "text-orange-700", border: "border-orange-200" },
            { name: "事务", val: 38, color: "bg-red-500", bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
            { name: "隔离级别", val: 32, color: "bg-red-500", bg: "bg-red-50", text: "text-red-700", border: "border-red-200" }
          ].map((kp, i) => (
            <div key={i} className={`flex flex-col gap-2 p-3 rounded-xl border ${kp.border} ${kp.bg} min-w-[160px] flex-1 max-w-[200px]`}>
              <div className="flex justify-between items-center">
                <span className={`text-sm font-bold ${kp.text}`}>{kp.name}</span>
                <span className={`text-sm font-black ${kp.text}`}>{kp.val}%</span>
              </div>
              <div className="w-full h-1.5 bg-white/50 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${kp.color}`} style={{ width: `${kp.val}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
