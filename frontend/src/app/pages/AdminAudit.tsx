import React from "react";
import { ActivitySquare, Download, Gauge, ShieldAlert, Timer, WalletCards } from "lucide-react";
import { useApi } from "../lib/useApi";
import { invocationsApi, Invocation } from "../lib/api";
import { DetailDrawer, PageHeader, PageShell, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, useInlineToast } from "../components/common/ProductUI";

function mapInvocation(i: Invocation) {
  const statusMap: Record<string, string> = { success: "成功", failed: "失败", pending: "进行中" };
  return {
    id: String(i.invocation_id),
    time: i.created_at ? new Date(i.created_at).toLocaleString("zh-CN") : "-",
    user: i.invoker_real_name ?? "-",
    role: "-",
    agent: i.task_title || i.project_name || "-",
    model: i.display_name || i.model_name || "-",
    input: i.input_tokens ?? 0,
    output: i.output_tokens ?? 0,
    latency: i.latency_ms ? `${(i.latency_ms / 1000).toFixed(1)}s` : "-",
    cost: i.cost ? `¥${i.cost.toFixed(4)}` : "-",
    hit: "-",
    safety: i.status === "success" ? "通过" : i.status === "failed" ? "失败" : "-",
    status: statusMap[i.status] ?? i.status,
    raw: i,
  };
}

export function AdminAudit() {
  const [query, setQuery] = React.useState("");
  const [riskFilter, setRiskFilter] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapInvocation> | null>(null);
  const { toast, showToast } = useInlineToast();

  const invocationsState = useApi(() => invocationsApi.getInvocations({ page: 1, page_size: 50 }), []);

  const invocations = (invocationsState.data?.items ?? []).map(mapInvocation);
  const filtered = invocations.filter((log) => {
    const filterMatch = riskFilter === "全部" || log.status === riskFilter || log.safety === riskFilter;
    const keywordMatch = `${log.user}${log.agent}${log.model}`.toLowerCase().includes(query.toLowerCase());
    return filterMatch && keywordMatch;
  });

  const totalTokens = invocations.reduce((sum, i) => sum + i.input + i.output, 0);
  const totalCost = invocations.reduce((sum, i) => sum + (i.raw?.cost ?? 0), 0);
  const successCount = invocations.filter((i) => i.status === "成功").length;
  const stats = [
    { label: "今日调用", value: `${invocationsState.data?.total ?? "-"}`, hint: "智能体与模型", icon: ActivitySquare, tone: "blue" as const },
    { label: "成功率", value: invocations.length ? `${Math.round((successCount / invocations.length) * 100)}%` : "-", hint: "近 24 小时", icon: ShieldAlert, tone: "emerald" as const },
    { label: "平均响应时间", value: "-", hint: "待计算", icon: Timer, tone: "purple" as const },
    { label: "Token 消耗", value: totalTokens > 0 ? `${(totalTokens / 1000).toFixed(1)}K` : "-", hint: "输入输出合计", icon: Gauge, tone: "cyan" as const },
    { label: "风险调用", value: `${invocations.filter((i) => i.status === "失败").length}`, hint: "失败记录", icon: ShieldAlert, tone: "red" as const },
    { label: "今日成本", value: totalCost > 0 ? `¥${totalCost.toFixed(2)}` : "-", hint: "预算可控", icon: WalletCards, tone: "orange" as const },
  ];

  return (
    <PageShell>
      <PageHeader eyebrow="AI Audit" title="调用审计" description="追踪每一次智能体调用、模型使用、Token 消耗、响应时间和风险状态。" icon={ActivitySquare} action={<button onClick={() => showToast("审计日志已导出为模拟报表")} className={primaryButton}><Download className="h-4 w-4" />导出审计日志</button>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4"><div className="flex flex-wrap items-end gap-4"><SearchInput label="搜索用户、智能体或模型" value={query} onChange={setQuery} /><SegmentedControl value={riskFilter} options={["全部", "成功", "失败", "进行中"]} onChange={setRiskFilter} /></div></section>
      {invocationsState.loading ? (
        <div className="flex items-center justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
      ) : filtered.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无调用记录</div>
      ) : (
        <>
          <section className="edu-card hidden overflow-hidden rounded-2xl lg:block">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-black text-slate-500"><tr>{["调用时间", "用户", "角色", "智能体", "模型", "输入", "输出", "响应", "成本", "命中", "安全", "状态", "操作"].map((h) => <th key={h} className="px-3 py-3">{h}</th>)}</tr></thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((log) => <tr key={log.id} className="bg-white hover:bg-blue-50/40">
                  <td className="px-3 py-4 font-mono text-xs">{log.time}</td><td className="px-3 py-4 font-black text-slate-900">{log.user}</td><td className="px-3 py-4">{log.role}</td><td className="px-3 py-4">{log.agent}</td><td className="px-3 py-4">{log.model}</td><td className="px-3 py-4">{log.input}</td><td className="px-3 py-4">{log.output}</td><td className="px-3 py-4">{log.latency}</td><td className="px-3 py-4">{log.cost}</td><td className="px-3 py-4">{log.hit}</td><td className="px-3 py-4">{log.safety}</td><td className="px-3 py-4"><StatusBadge status={log.status} /></td><td className="px-3 py-4"><button onClick={() => setSelected(log)} className="text-xs font-black text-blue-700">详情</button></td>
                </tr>)}
              </tbody>
            </table>
          </section>
          <section className="grid gap-3 lg:hidden">
            {filtered.map((log) => (
              <button key={log.id} onClick={() => setSelected(log)} className="edu-card w-full rounded-2xl p-4 text-left">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-black text-slate-950">{log.agent}</div>
                    <div className="mt-1 text-xs font-semibold text-slate-500">{log.user} · {log.role} · {log.model}</div>
                  </div>
                  <StatusBadge status={log.status} />
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                  <div className="rounded-xl bg-slate-50 p-3">
                    <div className="font-bold text-slate-400">Token</div>
                    <div className="mt-1 font-black text-slate-800">{log.input + log.output}</div>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-3">
                    <div className="font-bold text-slate-400">成本</div>
                    <div className="mt-1 font-black text-blue-700">{log.cost}</div>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-3">
                    <div className="font-bold text-slate-400">响应</div>
                    <div className="mt-1 font-black text-slate-800">{log.latency}</div>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-3">
                    <div className="font-bold text-slate-400">安全</div>
                    <div className="mt-1 font-black text-slate-800">{log.safety}</div>
                  </div>
                </div>
                <div className="mt-3 truncate font-mono text-[11px] font-bold text-slate-400">{log.time}</div>
              </button>
            ))}
          </section>
        </>
      )}
      {selected && <DetailDrawer title="调用详情" subtitle={`${selected.user} / ${selected.agent}`} open={!!selected} onClose={() => setSelected(null)}>
        {[
          ["请求摘要", `用户 ${selected.user} 调用 ${selected.agent}，使用模型 ${selected.model}。`],
          ["Token 消耗", `输入 ${selected.input} / 输出 ${selected.output}`],
          ["安全检查结果", selected.safety],
          ["成本明细", `${selected.input + selected.output} tokens / ${selected.cost}`],
          ["调用链路", "入口请求 → 智能体编排 → 模型调用 → 安全检查 → 结果落库"],
        ].map(([title, desc]) => <div key={title} className="mb-3 rounded-2xl border border-slate-100 bg-white p-4"><h3 className="text-sm font-black text-slate-900">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-600">{desc}</p></div>)}
      </DetailDrawer>}
      {toast}
    </PageShell>
  );
}
