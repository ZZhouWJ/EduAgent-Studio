import React from "react";
import { BellRing, Coins, Download, LineChart as LineChartIcon, PieChart, WalletCards } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "@/lib/useApi";
import { statisticsApi } from "@/lib/api";
import { ModalShell, PageHeader, PageShell, SegmentedControl, StatCard, primaryButton, secondaryButton, useInlineToast } from "@/components/common/ProductUI";

const DEMO_COURSES = ["全部课程", "数据库系统原理与 Web 项目实践", "人工智能导论"];
const DEMO_MODELS = ["全部模型", "Qwen-Max", "GPT-4o", "Claude-3.5"];

export function AdminCosts() {
  const [range, setRange] = React.useState("近 7 日");
  const [course, setCourse] = React.useState("全部课程");
  const [model, setModel] = React.useState("全部模型");
  const [open, setOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const costsState = useApi(() => statisticsApi.costs(), []);
  const distributionState = useApi(() => statisticsApi.costDistribution(), []);

  const costs = costsState.data;
  const distribution = distributionState.data ?? [];

  const stats = [
    { label: "今日成本", value: costs ? `¥${costs.total_cost.toFixed(2)}` : "-", hint: "预算可控", icon: Coins, tone: "blue" as const },
    { label: "Token 总消耗", value: costs ? `${(costs.total_tokens / 1000).toFixed(1)}K` : "-", hint: "输入输出合计", icon: WalletCards, tone: "purple" as const },
    { label: "输入成本", value: costs ? `¥${costs.input_cost.toFixed(2)}` : "-", hint: "模型输入", icon: PieChart, tone: "emerald" as const },
    { label: "输出成本", value: costs ? `¥${costs.output_cost.toFixed(2)}` : "-", hint: "模型输出", icon: LineChartIcon, tone: "cyan" as const },
    { label: "成本最高模型", value: costs?.cost_by_model?.[0]?.model_name ?? "-", hint: costs?.cost_by_model?.[0] ? `${((costs.cost_by_model[0].cost / Math.max(costs.total_cost, 1)) * 100).toFixed(0)}%` : "", icon: Coins, tone: "orange" as const },
    { label: "成本最高课程", value: costs?.cost_by_project?.[0]?.project_name?.slice(0, 8) ?? "-", hint: costs?.cost_by_project?.[0] ? `${((costs.cost_by_project[0].cost / Math.max(costs.total_cost, 1)) * 100).toFixed(0)}%` : "", icon: BellRing, tone: "red" as const },
  ];

  const barData = distribution.map((d) => ({
    agent: d.agent_name || d.agent,
    cost: d.tokens,
    ratio: d.ratio,
  }));

  const trendData = [
    { day: "周一", cost: 120, input: 42, output: 78 },
    { day: "周二", cost: 145, input: 55, output: 90 },
    { day: "周三", cost: 98, input: 38, output: 60 },
    { day: "周四", cost: 162, input: 60, output: 102 },
    { day: "周五", cost: 186, input: 68, output: 118 },
    { day: "周六", cost: 95, input: 35, output: 60 },
    { day: "周日", cost: 88, input: 30, output: 58 },
  ];

  return (
    <PageShell>
      <PageHeader eyebrow="Cost Analytics" title="成本统计" description="按模型、智能体、课程和角色分析大模型调用成本。" icon={Coins} action={<div className="flex flex-col gap-3 sm:flex-row"><button onClick={() => setOpen(true)} className={secondaryButton}>设置预算提醒</button><button onClick={() => showToast("成本报表已导出")} className={primaryButton}><Download className="h-4 w-4" />导出报表</button></div>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
          <SegmentedControl value={range} options={["今日", "近 7 日", "本月"]} onChange={setRange} />
          <select value={course} onChange={(event) => setCourse(event.target.value)} className="edu-focus-ring min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
            {DEMO_COURSES.map((item) => <option key={item}>{item}</option>)}
          </select>
          <select value={model} onChange={(event) => setModel(event.target.value)} className="edu-focus-ring min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
            {DEMO_MODELS.map((item) => <option key={item}>{item}</option>)}
          </select>
        </div>
      </section>
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:gap-6">
        <div className="edu-card rounded-2xl p-5 sm:p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">成本趋势折线图</h2>
          {costsState.loading || distributionState.loading ? (
            <div className="flex h-[320px] items-center justify-center"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : (
            <div className="h-[320px]"><ResponsiveContainer width="100%" height="100%"><LineChart data={trendData}><CartesianGrid stroke="#E2E8F0" vertical={false} /><XAxis dataKey="day" /><YAxis /><Tooltip /><Line type="monotone" dataKey="cost" name="成本" stroke="#2563EB" strokeWidth={3} /><Line type="monotone" dataKey="input" name="输入 Token" stroke="#7C3AED" strokeDasharray="5 5" /><Line type="monotone" dataKey="output" name="输出 Token" stroke="#F59E0B" strokeDasharray="4 4" /></LineChart></ResponsiveContainer></div>
          )}
        </div>
        <div className="edu-card rounded-2xl p-5 sm:p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">按智能体 Token 分布</h2>
          {barData.length > 0 ? (
            <div className="h-[320px]"><ResponsiveContainer width="100%" height="100%"><BarChart data={barData} layout="vertical" margin={{ left: 30 }}><XAxis type="number" hide /><YAxis dataKey="agent" type="category" width={110} /><Tooltip /><Bar dataKey="cost" name="Token" radius={[0, 8, 8, 0]}>{barData.map((_, index) => <Cell key={index} fill={["#2563EB", "#7C3AED", "#10B981", "#F59E0B", "#EF4444", "#06B6D4"][index % 6]} />)}</Bar></BarChart></ResponsiveContainer></div>
          ) : (
            <div className="flex h-[320px] items-center justify-center text-sm text-slate-400">暂无分布数据</div>
          )}
        </div>
      </section>
      <section className="edu-card overflow-hidden rounded-2xl">
        {costs?.cost_by_model && costs.cost_by_model.length > 0 && (
          <>
            <h3 className="px-4 pt-4 text-sm font-black text-slate-600">按模型成本排行</h3>
            <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs font-black text-slate-500"><tr>{["模型", "成本", "占比"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{costs.cost_by_model.map((row) => <tr key={row.model_name} className="bg-white hover:bg-blue-50/40"><td className="max-w-[280px] truncate px-4 py-4 font-black text-slate-900">{row.model_name}</td><td className="px-4 py-4 font-black text-blue-700">¥{row.cost.toFixed(2)}</td><td className="px-4 py-4">{((row.cost / Math.max(costs.total_cost, 1)) * 100).toFixed(1)}%</td></tr>)}</tbody></table>
          </>
        )}
        {(!costs?.cost_by_model || costs.cost_by_model.length === 0) && (
          <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无成本数据</div>
        )}
      </section>
      <ModalShell title="设置预算提醒" open={open} onClose={() => setOpen(false)}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2"><label className="text-sm font-bold text-slate-700">月度预算<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3" defaultValue="¥10,000" /></label><label className="text-sm font-bold text-slate-700">提醒阈值<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3" defaultValue="80%" /></label></div>
        <div className="mt-5 flex flex-col justify-end gap-3 sm:flex-row"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={() => { setOpen(false); showToast("预算提醒已保存"); }} className={primaryButton}>保存提醒</button></div>
      </ModalShell>
      {toast}
    </PageShell>
  );
}
