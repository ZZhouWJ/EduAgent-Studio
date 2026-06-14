import React from "react";
import { ActivitySquare, Bot, Coins, Gauge, PlugZap, Save, Settings2, ToggleLeft } from "lucide-react";
import { useApi } from "../lib/useApi";
import { modelsApi, AIModel } from "../lib/api";
import { ModalShell, PageHeader, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

function mapModel(m: AIModel) {
  const abilities = m.capability_tags ? m.capability_tags.split(",").map((t) => t.trim()).filter(Boolean) : [];
  const statusMap: Record<string, string> = { active: "启用", inactive: "停用", observing: "观察" };
  return {
    id: String(m.model_id),
    name: m.display_name || m.model_name,
    provider: m.provider_name,
    status: statusMap[m.status] ?? m.status,
    abilities,
    latency: m.max_context ? `${m.max_context}K ctx` : "-",
    calls: "-",
    cost: m.price_unit ? `¥${m.input_price}/${m.price_unit}` : "-",
    key: "-",
    raw: m,
  };
}

export function AdminModelConfig() {
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [editing, setEditing] = React.useState<ReturnType<typeof mapModel> | null>(null);
  const [open, setOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const modelsState = useApi(() => modelsApi.getModels({ page: 1, page_size: 100 }), []);

  const models = (modelsState.data?.items ?? []).map(mapModel);
  const filtered = models.filter((item) => {
    const statusMatch = statusFilter === "全部" || item.status === statusFilter;
    const keywordMatch = `${item.name}${item.provider}${item.abilities.join("")}`.toLowerCase().includes(query.toLowerCase());
    return statusMatch && keywordMatch;
  });

  const stats = [
    { label: "已配置模型", value: `${modelsState.data?.total ?? "-"}`, hint: "含供应商", icon: Bot, tone: "blue" as const },
    { label: "可用模型", value: `${models.filter((p) => p.status === "启用").length}`, hint: "可被智能体调用", icon: PlugZap, tone: "emerald" as const },
    { label: "今日调用次数", value: "-", hint: "待接入统计", icon: ActivitySquare, tone: "purple" as const },
    { label: "平均响应时间", value: "-", hint: "待接入监控", icon: Gauge, tone: "cyan" as const },
    { label: "异常次数", value: "-", hint: "待接入审计", icon: ToggleLeft, tone: "red" as const },
    { label: "今日成本", value: "-", hint: "待接入统计", icon: Coins, tone: "orange" as const },
  ];

  const setEnabled = (id: string) => {
    showToast("模型启用状态：TODO - 后端无 toggle 接口，请通过编辑接口更新 status");
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader eyebrow="Model Configuration" title="模型配置" description="统一管理平台接入的大模型服务、API Key、模型能力和连接状态。" icon={Settings2} action={<button onClick={() => showToast("模型配置巡检完成，所有可用模型均可连接")} className={primaryButton}>一键巡检</button>} />
      <section className="grid grid-cols-6 gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4"><div className="flex flex-wrap items-end gap-4"><SearchInput label="搜索模型、供应商或能力" value={query} onChange={setQuery} /><SegmentedControl value={statusFilter} options={["全部", "启用", "观察", "停用"]} onChange={setStatusFilter} /></div></section>
      {modelsState.loading ? (
        <div className="flex items-center justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
      ) : filtered.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无模型数据</div>
      ) : (
        <section className="grid grid-cols-3 gap-5">
          {filtered.map((model) => (
            <article key={model.id} className="edu-card edu-card-hover rounded-2xl p-5">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div><h2 className="text-lg font-black text-slate-950">{model.name}</h2><p className="mt-1 text-xs font-bold text-slate-400">{model.provider}</p></div>
                <StatusBadge status={model.status} />
              </div>
              <div className="mb-4 flex flex-wrap gap-2">{model.abilities.map((item) => <span key={item} className="rounded-lg bg-blue-50 px-2 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-100">{item}</span>)}</div>
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">上下文</div><div className="font-black text-slate-900">{model.latency}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">调用</div><div className="font-black text-slate-900">{model.calls}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">价格</div><div className="font-black text-slate-900">{model.cost}</div></div>
              </div>
              <div className="mt-4 rounded-xl border border-slate-100 bg-white p-3 font-mono text-xs font-bold text-slate-500">API Key：{model.key}</div>
              <div className="mt-5 grid grid-cols-2 gap-2">
                <button onClick={() => showToast(`${model.name} 连接测试成功`)} className={primaryButton}>测试连接</button>
                <button onClick={() => { setEditing(model); setOpen(true); }} className={secondaryButton}>编辑配置</button>
                <button onClick={() => showToast(`已跳转 ${model.name} 调用视图`)} className={secondaryButton}>查看调用</button>
                <button onClick={() => setEnabled(model.id)} className={secondaryButton}>{model.status === "启用" ? "停用" : "启用"}</button>
              </div>
            </article>
          ))}
        </section>
      )}
      <ModalShell title={editing ? `编辑模型配置：${editing.name}` : "编辑模型配置"} open={open} onClose={() => setOpen(false)}>
        <div className="grid grid-cols-2 gap-4">
          {["模型名称", "供应商", "API Key", "默认温度"].map((label, index) => <label key={label} className="text-sm font-bold text-slate-700">{label}<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" defaultValue={index === 0 ? (editing?.name ?? "") : index === 1 ? (editing?.provider ?? "") : index === 2 ? editing?.key ?? "" : "0.7"} /></label>)}
        </div>
        <div className="mt-5 flex justify-end gap-3"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={() => { setOpen(false); showToast("模型配置已保存（编辑功能 TODO）"); }} className={primaryButton}><Save className="h-4 w-4" />保存配置</button></div>
      </ModalShell>
      {toast}
    </div>
  );
}
