import React from "react";
import { CheckCircle2, AlertCircle, Eye, AlertTriangle, MessageSquare, ShieldCheck, Download, MoreHorizontal } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { reviewsApi } from "@/lib/api";

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

export function TeacherReview() {
  const [selectedId, setSelectedId] = React.useState<number | null>(null);
  const { data: pendingData, loading: loadingPending } = useApi(() => reviewsApi.getPending({ page: 1, page_size: 20 }), []);
  const { data: selectedDetail, loading: loadingDetail } = useApi(
    () => selectedId != null ? reviewsApi.getById(selectedId) : Promise.resolve(null),
    [selectedId]
  );

  const pendingList = pendingData?.items ?? [];
  const currentItem = selectedDetail ?? pendingList.find((r) => r.request_id === selectedId) ?? pendingList[0];
  return (
    <div className="page-shell flex min-h-0 flex-col pb-6">
      <div className="shrink-0">
        <h1 className="text-2xl font-bold text-slate-900">教师审核中心</h1>
        <p className="text-slate-500 mt-1 text-sm">对 AI 生成的学习资源进行准确性、适配性和安全性审核。</p>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-4 lg:flex-row lg:gap-6">
        {/* Left: Pending Review List */}
        <div className="flex w-full shrink-0 flex-col gap-4 lg:w-[400px]">
          <div className="mb-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-bold text-slate-800">待审核资源 (12)</h2>
            <div className="flex gap-2">
              <span className="px-2 py-1 rounded bg-red-50 text-red-600 text-xs font-bold">3 高风险</span>
              <span className="px-2 py-1 rounded bg-orange-50 text-orange-600 text-xs font-bold">9 建议复核</span>
            </div>
          </div>
          
          <div className="custom-scrollbar flex-1 space-y-3 overflow-y-auto pb-4 pr-0 lg:pr-2">
            {loadingPending ? (
              <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
            ) : pendingList.length === 0 ? (
              <div className="flex items-center justify-center h-32 text-slate-400">暂无待审核资源</div>
            ) : (
            pendingList.map((item) => (
              <div key={item.request_id} onClick={() => setSelectedId(item.request_id)} className={`p-4 rounded-xl border transition-all cursor-pointer ${
                item.request_id === selectedId 
                  ? "bg-blue-50 border-blue-200 shadow-sm" 
                  : "bg-white border-slate-200 hover:border-blue-300 hover:shadow-md"
              }`}>
                <div className="flex justify-between items-start mb-2">
                  <h3 className={`font-bold text-[15px] ${item.request_id === selectedId ? "text-blue-900" : "text-slate-800"}`}>{item.output_title}</h3>
                </div>
                <div className="flex flex-wrap gap-2 mb-3">
                  <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[11px]">学生：{item.submitter_real_name}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">{formatTimeAgo(item.created_at)}提交</span>
                </div>
              </div>
            ))
            )}
          </div>
        </div>

        {/* Right: Review Detail Pane */}
        <div className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <div className="flex shrink-0 flex-col gap-3 border-b border-slate-100 bg-slate-50/50 p-4 sm:p-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-bold">课程讲义</span>
                <span className="text-sm text-slate-500">适用学生：{currentItem?.submitter_real_name ?? "—"}</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900">{currentItem?.output_title ?? "—"}</h2>
            </div>
            <div className="flex gap-2">
              <button className="flex min-h-11 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-600 hover:bg-slate-50">
                <Eye className="w-4 h-4" /> 预览资源
              </button>
            </div>
          </div>

          <div className="flex-1 space-y-6 overflow-y-auto p-4 sm:p-6">
            {loadingDetail ? (
              <div className="flex items-center justify-center h-48 text-slate-400">加载详情中...</div>
            ) : (
            <>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-6">
              <div className="space-y-4">
                <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                  <h3 className="font-bold text-emerald-800 flex items-center gap-2 mb-2">
                    <ShieldCheck className="w-4 h-4" /> 智能体审核建议
                  </h3>
                  <p className="text-sm text-emerald-700 leading-relaxed">
                    本讲义内容准确度高，未检测到幻觉。难度匹配“李明”当前的薄弱点。但建议教师检查案例是否足够通俗易懂。
                  </p>
                </div>

                <div>
                  <h3 className="font-bold text-slate-800 mb-3 text-sm">证据来源追溯</h3>
                  <div className="space-y-2">
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700">1. 第 6 章：事务与并发控制 (命中率 92%)</div>
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700">2. 实验 4：银行转账并发控制实验 (命中率 85%)</div>
                  </div>
                </div>
              </div>

              <div className="bg-orange-50 rounded-xl p-4 border border-orange-100 flex flex-col">
                <h3 className="font-bold text-orange-800 flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4" /> 潜在风险提示
                </h3>
                <ul className="space-y-2 text-sm text-orange-700 list-disc pl-4 mb-4">
                  <li>“串行化”的性能影响说明可能偏难</li>
                  <li>缺少 MySQL 默认隔离级别的明确提示</li>
                </ul>
                <button className="mt-auto self-start text-orange-600 text-sm font-medium hover:underline">
                  查看 AI 批注详情
                </button>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-6">
              <h3 className="font-bold text-slate-900 mb-4 text-base flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-blue-500" /> 教师审核表单
              </h3>
              
              <div className="space-y-5 max-w-3xl">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">内容准确性评分</label>
                    <select className="w-full h-10 px-3 rounded-lg border border-slate-300 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm">
                      <option>5 - 完全准确</option>
                      <option>4 - 基本准确</option>
                      <option>3 - 存在瑕疵</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">难度适配性评分</label>
                    <select className="w-full h-10 px-3 rounded-lg border border-slate-300 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm">
                      <option>5 - 非常适合</option>
                      <option>4 - 比较适合</option>
                      <option>3 - 偏难/偏易</option>
                    </select>
                  </div>
                </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">是否适合当前学生 ({currentItem?.submitter_real_name ?? "—"})</label>
                  <div className="flex flex-wrap gap-4">
                    <label className="flex min-h-11 cursor-pointer items-center gap-2">
                      <input type="radio" name="fit" className="text-blue-600 w-4 h-4 focus:ring-blue-500" defaultChecked />
                      <span className="text-sm text-slate-700">适合</span>
                    </label>
                    <label className="flex min-h-11 cursor-pointer items-center gap-2">
                      <input type="radio" name="fit" className="text-blue-600 w-4 h-4 focus:ring-blue-500" />
                      <span className="text-sm text-slate-700">不适合</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">审核意见 / 修改建议</label>
                  <textarea 
                    className="w-full h-24 p-3 rounded-lg border border-slate-300 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm resize-none"
                    aria-label="审核意见或修改建议"
                    defaultValue="内容不错，但建议补充 MySQL 默认隔离级别的说明。可以增加一题脏读判断题作为测验。"
                  />
                </div>
              </div>
            </div>
            </>
            )}
          </div>

          <div className="flex shrink-0 flex-col gap-3 border-t border-slate-100 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
            <label className="flex min-h-11 cursor-pointer items-center gap-2">
              <input type="checkbox" className="text-blue-600 rounded w-4 h-4 focus:ring-blue-500" />
              <span className="text-sm font-medium text-slate-700">标记为优秀资源库模板</span>
            </label>

            <div className="flex flex-col gap-3 sm:flex-row">
              <button className="min-h-11 rounded-lg border border-slate-300 bg-white px-6 text-sm font-bold text-slate-700 transition-colors hover:bg-slate-50">
                退回修改
              </button>
              <button className="min-h-11 rounded-lg bg-blue-600 px-8 text-sm font-bold text-white shadow-md shadow-blue-500/20 transition-colors hover:bg-blue-700">
                审核通过并推送给学生
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
