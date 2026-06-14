import React from "react";
import { Search, Filter, FileText, CheckCircle2, AlertCircle, PlayCircle, Code, ListTree, MoreVertical } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { resourcesApi } from "@/lib/api";

interface Resource {
  title: string
  type: string
  course: string
  student: string
  tag: string
  diff: string
  status: string
  conf: number
  refs: number
  time: string
  icon: React.ComponentType<{ className?: string }>
  iconColor: string
  iconBg: string
}

const TYPE_ICON_MAP: Record<string, { icon: React.ComponentType<{ className?: string }>; iconColor: string; iconBg: string }> = {
  "课程讲义": { icon: FileText, iconColor: "text-blue-500", iconBg: "bg-blue-50" },
  "题库": { icon: ListTree, iconColor: "text-purple-500", iconBg: "bg-purple-50" },
  "代码案例": { icon: Code, iconColor: "text-emerald-500", iconBg: "bg-emerald-50" },
  "视频脚本": { icon: PlayCircle, iconColor: "text-orange-500", iconBg: "bg-orange-50" },
};

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

export function ResourceLibrary() {
  const [typeFilter, setTypeFilter] = React.useState("");
  const { data, loading } = useApi(() => resourcesApi.list({ type: typeFilter || undefined, page_size: 100 }), [typeFilter]);

  const resources: Resource[] = (data?.items ?? []).map((r) => {
    const iconInfo = TYPE_ICON_MAP[r.resource_type] ?? { icon: FileText, iconColor: "text-slate-500", iconBg: "bg-slate-50" };
    return {
      title: r.resource_title,
      type: r.resource_type,
      course: r.course_name,
      student: "—",
      tag: "—",
      diff: r.difficulty,
      status: r.status,
      conf: 80,
      refs: 0,
      time: formatTimeAgo(r.created_at),
      icon: iconInfo.icon,
      iconColor: iconInfo.iconColor,
      iconBg: iconInfo.iconBg,
    };
  });

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto h-full flex flex-col">
      <div className="shrink-0">
        <h1 className="text-2xl font-bold text-slate-900">学习资源库</h1>
        <p className="text-slate-500 mt-1 text-sm">统一管理由多智能体生成并经教师审核的个性化学习资源。</p>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 flex items-center justify-between gap-4 shrink-0">
        <div className="flex gap-2 items-center flex-1">
          <div className="relative max-w-xs w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              aria-label="搜索资源标题"
              className="w-full h-9 pl-9 pr-3 rounded-lg bg-slate-50 border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
          <select className="h-9 px-3 rounded-lg bg-slate-50 border border-slate-200 text-sm outline-none w-32">
            <option>所有课程</option>
          </select>
          <select className="h-9 px-3 rounded-lg bg-slate-50 border border-slate-200 text-sm outline-none w-32">
            <option>所有学生</option>
          </select>
          <select className="h-9 px-3 rounded-lg bg-slate-50 border border-slate-200 text-sm outline-none w-32">
            <option>全部状态</option>
            <option>已通过</option>
            <option>待审核</option>
            <option>被退回</option>
          </select>
        </div>
        <button className="h-9 px-4 flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50">
          <Filter className="w-4 h-4" /> 更多筛选
        </button>
      </div>

      <div className="flex gap-2 shrink-0 border-b border-slate-200">
        {["全部", "课程讲义", "思维导图", "分层练习题", "代码实操案例", "PPT 大纲", "视频/动画脚本"].map((tab, i) => (
          <button 
            key={tab} 
            onClick={() => setTypeFilter(tab === "全部" ? "" : tab)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              (tab === "全部" && !typeFilter) || (typeFilter === tab)
                ? "border-blue-600 text-blue-600" 
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
      ) : (
      <div className="flex-1 overflow-y-auto min-h-0 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 auto-rows-max">
        {resources.length === 0 ? (
          <div className="col-span-full flex items-center justify-center h-32 text-slate-400">暂无资源</div>
        ) : (
        resources.map((res, i) => {
          const Icon = res.icon;
          return (
            <div key={i} className="bg-white rounded-2xl p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col group">
              <div className="flex justify-between items-start mb-4">
                <div className={`w-10 h-10 rounded-xl ${res.iconBg} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${res.iconColor}`} />
                </div>
                <button className="text-slate-400 hover:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreVertical className="w-5 h-5" />
                </button>
              </div>
              
              <h3 className="font-bold text-slate-900 text-[15px] leading-tight mb-2 line-clamp-2">{res.title}</h3>
              
              <div className="flex flex-wrap gap-1.5 mb-4">
                <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600">{res.tag}</span>
                <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-600">{res.type}</span>
              </div>

              <div className="mt-auto space-y-2.5 mb-4">
                <div className="flex justify-between text-xs text-slate-500">
                  <span>适用学生</span>
                  <span className="font-medium text-slate-700">{res.student}</span>
                </div>
                <div className="flex justify-between text-xs text-slate-500">
                  <span>难度 & 来源</span>
                  <span className="font-medium text-slate-700">{res.diff} · {res.refs}引</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">可信度</span>
                  <div className="flex items-center gap-1.5">
                    <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${res.conf}%` }}></div>
                    </div>
                    <span className="font-bold text-emerald-600">{res.conf}%</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {res.status === "已通过" && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
                  {res.status === "待审核" && <AlertCircle className="w-4 h-4 text-orange-500" />}
                  {res.status === "被退回" && <AlertCircle className="w-4 h-4 text-red-500" />}
                  <span className={`text-xs font-bold ${
                    res.status === "已通过" ? "text-emerald-600" :
                    res.status === "待审核" ? "text-orange-600" : "text-red-600"
                  }`}>{res.status}</span>
                </div>
                <span className="text-[11px] text-slate-400">{res.time}</span>
              </div>
            </div>
          );
        })
        )}
      </div>
      )}
    </div>
  );
}
