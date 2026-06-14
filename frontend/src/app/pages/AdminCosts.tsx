import React from "react";
import { BellRing, Coins, Download, LineChart as LineChartIcon, PieChart, WalletCards } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { costRows, costTrend, courses, modelProviders } from "../data/demoData";
import { ModalShell, PageHeader, PageShell, SegmentedControl, StatCard, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function AdminCosts() {
  const [range, setRange] = React.useState("近 7 日");
  const [course, setCourse] = React.useState("全部课程");
  const [model, setModel] = React.useState("全部模型");
  const [open, setOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();
  const stats = [
    { label: "今日成本", value: "¥186", hint: "预算 43%", icon: Coins, tone: "blue" as const },
    { label: "本周成本", value: "¥1,142", hint: "较上周 +8%", icon: WalletCards, tone: "purple" as const },
    { label: "本月成本", value: "¥4,860", hint: "预算剩余 52%", icon: PieChart, tone: "emerald" as const },
    { label: "单次平均成本", value: "¥0.18", hint: "资源生成最高", icon: LineChartIcon, tone: "cyan" as const },
    { label: "成本最高模型", value: "Qwen", hint: "38%", icon: Coins, tone: "orange" as const },
    { label: "成本最高课程", value: "数据库", hint: "52%", icon: BellRing, tone: "red" as const },
  ];
  return (
    <PageShell>
      <PageHeader eyebrow="Cost Analytics" title="成本统计" description="按模型、智能体、课程和角色分析大模型调用成本。" icon={Coins} action={<div className="flex flex-col gap-3 sm:flex-row"><button onClick={() => setOpen(true)} className={secondaryButton}>设置预算提醒</button><button onClick={() => showToast("成本报表已导出")} className={primaryButton}><Download className="h-4 w-4" />导出报表</button></div>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
          <SegmentedControl value={range} options={["今日", "近 7 日", "本月"]} onChange={setRange} />
          <select value={course} onChange={(event) => setCourse(event.target.value)} className="edu-focus-ring min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
            {["全部课程", ...courses.map((c) => c.name)].map((item) => <option key={item}>{item}</option>)}
          </select>
          <select value={model} onChange={(event) => setModel(event.target.value)} className="edu-focus-ring min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
            {["全部模型", ...modelProviders.map((m) => m.name)].map((item) => <option key={item}>{item}</option>)}
          </select>
        </div>
      </section>
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:gap-6">
        <div className="edu-card rounded-2xl p-5 sm:p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">成本趋势折线图</h2>
          <div className="h-[320px]"><ResponsiveContainer width="100%" height="100%"><LineChart data={costTrend}><CartesianGrid stroke="#E2E8F0" vertical={false} /><XAxis dataKey="day" /><YAxis /><Tooltip /><Line type="monotone" dataKey="cost" name="成本" stroke="#2563EB" strokeWidth={3} /><Line type="monotone" dataKey="input" name="输入 Token" stroke="#7C3AED" strokeDasharray="5 5" /><Line type="monotone" dataKey="output" name="输出 Token" stroke="#F59E0B" strokeDasharray="4 4" /></LineChart></ResponsiveContainer></div>
        </div>
        <div className="edu-card rounded-2xl p-5 sm:p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">按课程成本排行</h2>
          <div className="h-[320px]"><ResponsiveContainer width="100%" height="100%"><BarChart data={costRows} layout="vertical" margin={{ left: 30 }}><XAxis type="number" hide /><YAxis dataKey="agent" type="category" width={110} /><Tooltip /><Bar dataKey="cost" name="成本" radius={[0, 8, 8, 0]}>{costRows.map((_, index) => <Cell key={index} fill={["#2563EB", "#7C3AED", "#10B981", "#F59E0B"][index]} />)}</Bar></BarChart></ResponsiveContainer></div>
        </div>
      </section>
      <section className="edu-card overflow-hidden rounded-2xl">
        <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs font-black text-slate-500"><tr>{["课程", "智能体", "模型", "调用次数", "输入 Token", "输出 Token", "成本", "占比"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{costRows.map((row) => <tr key={`${row.course}-${row.agent}`} className="bg-white hover:bg-blue-50/40"><td className="max-w-[280px] truncate px-4 py-4 font-black text-slate-900">{row.course}</td><td className="px-4 py-4">{row.agent}</td><td className="px-4 py-4">{row.model}</td><td className="px-4 py-4">{row.calls}</td><td className="px-4 py-4">{row.input}</td><td className="px-4 py-4">{row.output}</td><td className="px-4 py-4 font-black text-blue-700">¥{row.cost}</td><td className="px-4 py-4">{row.ratio}</td></tr>)}</tbody></table>
      </section>
      <ModalShell title="设置预算提醒" open={open} onClose={() => setOpen(false)}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2"><label className="text-sm font-bold text-slate-700">月度预算<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3" defaultValue="¥10,000" /></label><label className="text-sm font-bold text-slate-700">提醒阈值<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3" defaultValue="80%" /></label></div>
        <div className="mt-5 flex flex-col justify-end gap-3 sm:flex-row"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={() => { setOpen(false); showToast("预算提醒已保存"); }} className={primaryButton}>保存提醒</button></div>
      </ModalShell>
      {toast}
    </PageShell>
  );
}
