import React from "react";
import { BellRing, Coins, Download, LineChart as LineChartIcon, PieChart, WalletCards } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "@/lib/useApi";
import { learningApi, modelsApi, platformSettingsApi, statisticsApi, type BudgetAlertSettingsUpdate } from "@/lib/api";
import { ModalShell, PageHeader, PageShell, SegmentedControl, StatCard, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

const COLORS = ["#2563EB", "#7C3AED", "#10B981", "#F59E0B", "#EF4444", "#06B6D4"];

const DEFAULT_BUDGET_ALERT: BudgetAlertSettingsUpdate = {
  monthly_budget: 10000,
  alert_threshold_percent: 80,
  enabled: true,
};

function downloadCsv(rows: Record<string, string | number>[], filename: string) {
  const headers = Object.keys(rows[0] ?? {});
  const csv = [
    headers.join(","),
    ...rows.map((r) => headers.map((h) => `"${r[h] ?? ""}"`).join(","))
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export function AdminCosts() {
  const [range, setRange] = React.useState("近 7 日");
  const [courseFilter, setCourseFilter] = React.useState("全部课程");
  const [modelFilter, setModelFilter] = React.useState("全部模型");
  const [open, setOpen] = React.useState(false);
  const [savingBudget, setSavingBudget] = React.useState(false);
  const [budgetForm, setBudgetForm] = React.useState<BudgetAlertSettingsUpdate>(DEFAULT_BUDGET_ALERT);

  const costsState = useApi(() => statisticsApi.costs(), []);
  const distributionState = useApi(() => statisticsApi.costDistribution(), []);
  const costByModelState = useApi(() => statisticsApi.getCostByModel(), []);
  const coursesState = useApi(() => learningApi.listCourses(), []);
  const modelsState = useApi(() => modelsApi.getModels({ page_size: 50 }), []);
  const budgetState = useApi(() => platformSettingsApi.getBudgetAlert(), []);

  const costs = costsState.data;
  const distribution = distributionState.data ?? [];
  const courses = coursesState.data ?? [];
  const models = modelsState.data?.items ?? [];

  const courseOptions = ["全部课程", ...courses.map((c) => c.name)];
  const modelOptions = ["全部模型", ...models.map((m) => m.display_name || m.model_name)];

  const stats = [
    { label: "今日成本", value: costs ? `¥${(costs.total_cost ?? 0).toFixed(2)}` : "—", hint: "预算可控", icon: Coins, tone: "blue" as const },
    { label: "Token 总消耗", value: costs ? `${((costs.total_tokens ?? 0) / 1000).toFixed(1)}K` : "—", hint: "输入输出合计", icon: WalletCards, tone: "purple" as const },
    { label: "输入成本", value: costs ? `¥${(costs.input_cost ?? 0).toFixed(2)}` : "—", hint: "模型输入", icon: PieChart, tone: "emerald" as const },
    { label: "输出成本", value: costs ? `¥${(costs.output_cost ?? 0).toFixed(2)}` : "—", hint: "模型输出", icon: LineChartIcon, tone: "cyan" as const },
    { label: "成本最高模型", value: costs?.cost_by_model?.[0]?.model_name?.slice(0, 10) ?? "—", hint: costs?.cost_by_model?.[0] ? `${(((costs?.cost_by_model?.[0]?.total_cost ?? 0) / Math.max(costs?.total_cost ?? 1, 1)) * 100).toFixed(0)}%` : "", icon: Coins, tone: "orange" as const },
    { label: "成本最高课程", value: costs?.cost_by_project?.[0]?.project_name?.slice(0, 10) ?? "—", hint: costs?.cost_by_project?.[0] ? `${(((costs?.cost_by_project?.[0]?.total_cost ?? 0) / Math.max(costs?.total_cost ?? 1, 1)) * 100).toFixed(0)}%` : "", icon: BellRing, tone: "red" as const },
  ];

  const barData = distribution.map((d) => ({
    agent: d.agent_name || d.agent || "—",
    cost: d.tokens,
    ratio: d.ratio,
  }));

  const barChartData = barData.length > 0 ? barData : [
    { agent: "暂无数据", cost: 0, ratio: 0 },
  ];

  const handleExport = () => {
    const rows = [
      { 日期: range, 模型: modelFilter, 课程: courseFilter,
        总成本: costs?.total_cost ?? 0, Token消耗: costs?.total_tokens ?? 0 },
      ...(costs?.cost_by_model ?? []).map((r) => ({
        模型: r.model_name, 成本: r.total_cost ?? 0, 占比: `${(((r.total_cost ?? 0) / Math.max(costs?.total_cost ?? 1, 1)) * 100).toFixed(1)}%`
      }))
    ];
    downloadCsv(rows, `成本报表_${new Date().toISOString().slice(0, 10)}.csv`);
    notify.success("成本报表已导出");
  };

  const openBudgetEditor = () => {
    if (!budgetState.data) {
      notify.error(budgetState.error ? "预算配置加载失败" : "预算配置正在加载");
      return;
    }
    setBudgetForm({
      monthly_budget: budgetState.data.monthly_budget,
      alert_threshold_percent: budgetState.data.alert_threshold_percent,
      enabled: budgetState.data.enabled,
    });
    setOpen(true);
  };

  const saveBudgetAlert = async () => {
    if (budgetForm.monthly_budget <= 0) {
      notify.warning("月度预算必须大于 0");
      return;
    }
    setSavingBudget(true);
    try {
      await platformSettingsApi.updateBudgetAlert(budgetForm);
      await budgetState.refetch();
      setOpen(false);
      notify.success("预算提醒已保存");
    } catch (error) {
      notify.error("保存失败：" + (error instanceof Error ? error.message : String(error)));
    } finally {
      setSavingBudget(false);
    }
  };

  return (
    <PageShell>
      <PageHeader title="成本统计" description="按模型、智能体、课程和角色分析大模型调用成本。" icon={Coins}
        action={<div className="flex flex-col gap-3 sm:flex-row">
          <button
            onClick={openBudgetEditor}
            disabled={budgetState.loading}
            className={`${secondaryButton} cursor-pointer disabled:cursor-wait disabled:opacity-60`}
          >
            设置预算提醒
          </button>
          <button onClick={handleExport} className={`${primaryButton} cursor-pointer`}><Download className="h-4 w-4" />导出报表</button>
        </div>}
      />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
          <SegmentedControl value={range} options={["今日", "近 7 日", "本月"]} onChange={setRange} />
          <select value={courseFilter} onChange={(e) => setCourseFilter(e.target.value)} className="edu-focus-ring min-h-11 cursor-pointer rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
            {courseOptions.map((c, i) => <option key={c || i}>{c}</option>)}
          </select>
          <select value={modelFilter} onChange={(e) => setModelFilter(e.target.value)} className="edu-focus-ring min-h-11 cursor-pointer rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
            {modelOptions.map((m, i) => <option key={m || i}>{m}</option>)}
          </select>
        </div>
      </section>
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:gap-6">
        <div className="edu-card rounded-2xl p-5 sm:p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">成本趋势折线图</h2>
          {(costsState.loading || distributionState.loading) ? (
            <div className="flex h-[320px] items-center justify-center"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : (
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={barData} margin={{ left: -10, right: 16 }}>
                  <CartesianGrid stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="agent" tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 12, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
                  <Line type="monotone" dataKey="cost" name="Token" stroke="#2563EB" strokeWidth={3} />
                  <Line type="monotone" dataKey="ratio" name="占比" stroke="#7C3AED" strokeWidth={2} strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="edu-card rounded-2xl p-5 sm:p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">按智能体 Token 分布</h2>
          {barChartData.length > 0 && barChartData[0].cost > 0 ? (
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartData} layout="vertical" margin={{ left: 80, right: 16 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="agent" type="category" width={110} tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
                  <Bar dataKey="cost" name="Token" radius={[0, 8, 8, 0]}>
                    {barChartData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-[320px] items-center justify-center text-sm text-slate-400">暂无分布数据</div>
          )}
        </div>
      </section>
      <section className="edu-card overflow-hidden rounded-2xl">
        {costByModelState.data && costByModelState.data.length > 0 ? (
          <>
            <h3 className="px-4 pt-4 text-sm font-black text-slate-600">按模型成本排行</h3>
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-black text-slate-500">
                <tr>{["模型", "调用次数", "Token消耗", "成本", "占比"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {costByModelState.data.map((row) => (
                  <tr key={row.model} className="cursor-pointer bg-white hover:bg-blue-50/40">
                    <td className="max-w-[280px] truncate px-4 py-4 font-black text-slate-900">{row.model}</td>
                    <td className="px-4 py-4">{row.call_count ?? 0}</td>
                    <td className="px-4 py-4">{(row.total_tokens ?? 0).toLocaleString()}</td>
                    <td className="px-4 py-4 font-black text-blue-700">¥{(row.total_cost ?? 0).toFixed(4)}</td>
                    <td className="px-4 py-4">{(((row.total_cost ?? 0) / Math.max(costs?.total_cost ?? 1, 1)) * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        ) : (
          <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无成本数据</div>
        )}
      </section>
      <ModalShell title="设置预算提醒" open={open} onClose={() => !savingBudget && setOpen(false)}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className="text-sm font-bold text-slate-700">
            月度预算（元）
            <input
              type="number"
              min="0.01"
              max="1000000000"
              step="100"
              value={budgetForm.monthly_budget}
              onChange={(event) => setBudgetForm((current) => ({
                ...current,
                monthly_budget: Number(event.target.value),
              }))}
              className="edu-focus-ring mt-2 h-10 w-full cursor-text rounded-xl border border-slate-200 bg-slate-50 px-3 tabular-nums"
            />
          </label>
          <label className="text-sm font-bold text-slate-700">
            提醒阈值（%）
            <span className="float-right tabular-nums text-blue-700">{budgetForm.alert_threshold_percent}%</span>
            <input
              type="range"
              min="1"
              max="100"
              value={budgetForm.alert_threshold_percent}
              onChange={(event) => setBudgetForm((current) => ({
                ...current,
                alert_threshold_percent: Number(event.target.value),
              }))}
              className="mt-4 h-2 w-full cursor-pointer accent-blue-600"
            />
          </label>
        </div>
        <div className="mt-4 flex items-center justify-between gap-4 rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
          <div>
            <div className="text-sm font-black text-slate-900">启用预算提醒</div>
            <p className="mt-1 text-xs leading-5 text-slate-500">
              成本达到阈值后生成治理提醒并进入审计范围。
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={budgetForm.enabled}
            onClick={() => setBudgetForm((current) => ({ ...current, enabled: !current.enabled }))}
            className={`relative h-7 w-12 shrink-0 cursor-pointer rounded-full transition ${
              budgetForm.enabled ? "bg-blue-600" : "bg-slate-300"
            }`}
          >
            <span className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow-sm transition ${
              budgetForm.enabled ? "left-6" : "left-1"
            }`} />
          </button>
        </div>
        <div className="mt-5 flex flex-col justify-end gap-3 sm:flex-row">
          <button
            onClick={() => setOpen(false)}
            disabled={savingBudget}
            className={`${secondaryButton} cursor-pointer disabled:cursor-not-allowed disabled:opacity-60`}
          >
            取消
          </button>
          <button
            onClick={saveBudgetAlert}
            disabled={savingBudget}
            className={`${primaryButton} cursor-pointer disabled:cursor-wait disabled:opacity-60`}
          >
            {savingBudget ? "正在保存..." : "保存提醒"}
          </button>
        </div>
      </ModalShell>
    </PageShell>
  );
}
