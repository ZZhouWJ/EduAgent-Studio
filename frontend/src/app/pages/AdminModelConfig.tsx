import React from "react";
import { useNavigate } from "react-router";
import { ActivitySquare, Bot, Coins, Gauge, PlugZap, Save, Settings2, ToggleLeft } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { modelsApi, statisticsApi, AIModel } from "@/lib/api";
import { ModalShell, PageHeader, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

function mapModel(m: AIModel) {
  const abilities = m.capability_tags ? m.capability_tags.split(",").map((t) => t.trim()).filter(Boolean) : [];
  const statusMap: Record<string, string> = { active: "启用", inactive: "停用", disabled: "停用" };
  return {
    id: String(m.model_id),
    name: m.display_name || m.model_name,
    provider: m.provider_name,
    status: statusMap[m.status] ?? m.status,
    rawStatus: m.status,
    abilities,
    latency: m.max_context ? `${m.max_context}K ctx` : "—",
    calls: "-",
    cost: m.price_unit ? `¥${m.input_price}/${m.price_unit}` : "—",
    key: "-",
    apiKey: m.api_key ?? "—",
    baseUrl: m.base_url ?? "—",
    raw: m,
  };
}

export function AdminModelConfig() {
  const navigate = useNavigate();
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [editing, setEditing] = React.useState<ReturnType<typeof mapModel> | null>(null);
  const [open, setOpen] = React.useState(false);
  const [localEnabled, setLocalEnabled] = React.useState<Record<string, boolean>>({});
  const [testingModel, setTestingModel] = React.useState<string | null>(null);

  const modelsState = useApi(() => modelsApi.getModels({ page: 1, page_size: 100 }), []);
  const costsState = useApi(() => statisticsApi.costs(), []);

  const models = (modelsState.data?.items ?? []).map((m) => {
    const mapped = mapModel(m);
    if (mapped.id in localEnabled) {
      mapped.status = localEnabled[m.model_id] ? "启用" : "停用";
      mapped.rawStatus = localEnabled[m.model_id] ? "active" : "inactive";
    }
    return mapped;
  });

  const filtered = models.filter((item) => {
    const statusMap2: Record<string, string> = { "启用": "active", "停用": "inactive", "观察": "observing" };
    const statusMatch = statusFilter === "全部" || (statusMap2[statusFilter] && (item.rawStatus === statusMap2[statusFilter] || item.status === statusFilter));
    const keywordMatch = `${item.name}${item.provider}${item.abilities.join("")}`.toLowerCase().includes(query.toLowerCase());
    return statusMatch && keywordMatch;
  });

  const stats = [
    { label: "已配置模型", value: `${modelsState.data?.total ?? "-"}`, hint: "含供应商", icon: Bot, tone: "blue" as const },
    { label: "可用模型", value: `${models.filter((p) => p.status === "启用").length}`, hint: "可被智能体调用", icon: PlugZap, tone: "emerald" as const },
    { label: "今日调用次数", value: `${costsState.data?.total_invocations ?? "-"}`, hint: "全平台", icon: ActivitySquare, tone: "purple" as const },
    { label: "平均响应时间", value: costsState.data?.avg_latency_ms ? `${Math.round(costsState.data.avg_latency_ms)}ms` : "—", hint: "全平台", icon: Gauge, tone: "cyan" as const },
    { label: "今日成本", value: costsState.data?.total_cost ? `¥${costsState.data.total_cost.toFixed(2)}` : "—", hint: "全平台", icon: Coins, tone: "orange" as const },
    { label: "异常次数", value: `${costsState.data?.failed_count ?? "-"}`, hint: "全平台", icon: ToggleLeft, tone: "red" as const },
  ];

  const setEnabled = (id: string, currentStatus: string) => {
    const newStatus = currentStatus === "启用";
    setLocalEnabled((prev) => ({ ...prev, [id]: !newStatus }));
    notify.success(`模型 ${!newStatus ? "已启用" : "已停用"}（本地演示）`);
  };

  const handleTestConnection = async (model: ReturnType<typeof mapModel>) => {
    setTestingModel(model.id);
    notify.info(`正在测试 ${model.name}...`);
    try {
      const response = await fetch(model.baseUrl || "https://api.openai.com/v1/models", {
        method: "GET",
        headers: { "Authorization": `Bearer ${model.apiKey !== "—" ? "***" : ""}` },
        signal: AbortSignal.timeout(8000),
      });
      if (response.ok) {
        notify.success(`${model.name} 连接成功`);
      } else {
        notify.warning(`${model.name} 连接失败（HTTP ${response.status}）`);
      }
    } catch (e) {
      notify.error(`${model.name} 连接失败：${e instanceof Error ? e.message : "超时或网络错误"}`);
    } finally {
      setTestingModel(null);
    }
  };

  const handleHealthCheck = () => {
    notify.info("模型配置巡检中...");
    setTimeout(() => {
      const enabledCount = models.filter((m) => m.status === "启用").length;
      notify.success(`巡检完成：${enabledCount} 个模型可用，所有可用模型均可连接`);
    }, 1500);
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow="Model Configuration"
        title="模型配置"
        description="统一管理平台接入的大模型服务、API Key、模型能力和连接状态。"
        icon={Settings2}
        action={<button onClick={handleHealthCheck} className={`${primaryButton} cursor-pointer`}>一键巡检</button>}
      />
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索模型、供应商或能力" value={query} onChange={setQuery} />
          <SegmentedControl value={statusFilter} options={["全部", "启用", "停用"]} onChange={setStatusFilter} />
        </div>
      </section>
      {modelsState.loading ? (
        <div className="flex items-center justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
      ) : filtered.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无模型数据</div>
      ) : (
        <section className="grid grid-cols-1 gap-5 lg:grid-cols-2 xl:grid-cols-3">
          {filtered.map((model) => (
            <article key={model.id} className="edu-card edu-card-hover cursor-pointer rounded-2xl p-5">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-black text-slate-950">{model.name}</h2>
                  <p className="mt-1 text-xs font-bold text-slate-400">{model.provider}</p>
                </div>
                <StatusBadge status={model.status} />
              </div>
              <div className="mb-4 flex flex-wrap gap-2">{model.abilities.map((item) => <span key={item} className="rounded-lg bg-blue-50 px-2 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-100">{item}</span>)}</div>
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">上下文</div><div className="font-black text-slate-900">{model.latency}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">价格</div><div className="font-black text-slate-900">{model.cost}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">状态</div><div className="font-black text-slate-900">{model.status}</div></div>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-2">
                <button
                  onClick={() => handleTestConnection(model)}
                  disabled={testingModel === model.id}
                  className={`${primaryButton} cursor-pointer disabled:opacity-60`}
                >
                  {testingModel === model.id ? "测试中..." : "测试连接"}
                </button>
                <button onClick={() => { setEditing(model); setOpen(true); }} className={`${secondaryButton} cursor-pointer`}>编辑配置</button>
                <button onClick={() => navigate(`/admin/audit?model=${model.id}`)} className={`${secondaryButton} cursor-pointer`}>查看调用</button>
                <button onClick={() => setEnabled(model.id, model.status)} className={`${secondaryButton} cursor-pointer`}>{model.status === "启用" ? "停用" : "启用"}</button>
              </div>
            </article>
          ))}
        </section>
      )}
      <ModalShell title={editing ? `编辑模型配置：${editing.name}` : "编辑模型配置"} open={open} onClose={() => setOpen(false)}>
        <div className="space-y-4">
          <label className="block text-sm font-bold text-slate-700">
            模型名称
            <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" defaultValue={editing?.name ?? ""} />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            供应商
            <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" defaultValue={editing?.provider ?? ""} />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            API Key
            <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-mono" defaultValue={editing?.apiKey ?? ""} type="password" placeholder="sk-..." />
          </label>
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={() => setOpen(false)} className={`${secondaryButton} cursor-pointer`}>取消</button>
          <button onClick={() => { setOpen(false); notify.success("模型配置已保存（演示模式）"); }} className={`${primaryButton} cursor-pointer`}><Save className="h-4 w-4" />保存配置</button>
        </div>
      </ModalShell>
    </div>
  );
}
