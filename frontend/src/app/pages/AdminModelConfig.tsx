import React from "react";
import { useNavigate } from "react-router-dom";
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
    latency: m.max_context ? `${m.max_context >= 1000 ? `${Number((m.max_context / 1000).toFixed(1))}K` : m.max_context} ctx` : "—",
    calls: "-",
    cost: m.price_unit ? `¥${m.input_price}/${m.price_unit}` : "—",
    raw: m,
  };
}

export function AdminModelConfig() {
  const navigate = useNavigate();
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [editing, setEditing] = React.useState<ReturnType<typeof mapModel> | null>(null);
  const [open, setOpen] = React.useState(false);
  const [saving, setSaving] = React.useState(false);
  const [updatingId, setUpdatingId] = React.useState<string | null>(null);
  const [form, setForm] = React.useState({
    displayName: "",
    capabilityTags: "",
    maxContext: "4096",
    inputPrice: "0",
    outputPrice: "0",
    priceUnit: "1K_TOKENS",
    status: "active" as "active" | "disabled",
  });

  const modelsState = useApi(() => modelsApi.getModels({ page: 1, page_size: 100 }), []);
  const providersState = useApi(() => modelsApi.getProviders(), []);
  const configsState = useApi(() => modelsApi.getApiConfigs({ page: 1, page_size: 500 }), []);
  const costsState = useApi(() => statisticsApi.costs(), []);
  const modelCallsState = useApi(() => statisticsApi.modelCalls(), []);

  const activeProviderIds = new Set(
    (providersState.data ?? [])
      .filter((provider) => provider.status === "active")
      .map((provider) => provider.provider_id),
  );
  const configuredProviderIds = new Set(
    (configsState.data?.items ?? [])
      .filter((config) => config.status === "active")
      .map((config) => config.provider_id),
  );
  const models = (modelsState.data?.items ?? []).map((rawModel) => {
    const model = mapModel(rawModel);
    const isReady = rawModel.status === "active"
      && activeProviderIds.has(rawModel.provider_id)
      && configuredProviderIds.has(rawModel.provider_id);
    return {
      ...model,
      status: rawModel.status !== "active" ? "停用" : isReady ? "可用" : "待配置",
    };
  });

  const filtered = models.filter((item) => {
    const statusMatch = statusFilter === "全部" || item.status === statusFilter;
    const keywordMatch = `${item.name}${item.provider}${item.abilities.join("")}`.toLowerCase().includes(query.toLowerCase());
    return statusMatch && keywordMatch;
  });

  const stats = [
    { label: "已配置模型", value: `${modelsState.data?.total ?? "-"}`, hint: "含供应商", icon: Bot, tone: "blue" as const },
    { label: "可用模型", value: `${models.filter((model) => model.status === "可用").length}`, hint: "凭证与供应商均正常", icon: PlugZap, tone: "emerald" as const },
    { label: "调用次数", value: `${modelCallsState.data?.reduce((sum, item) => sum + item.call_count, 0) ?? "-"}`, hint: "全平台累计", icon: ActivitySquare, tone: "purple" as const },
    { label: "平均响应时间", value: modelCallsState.data?.length ? `${Math.round(modelCallsState.data.reduce((sum, item) => sum + item.avg_latency_ms, 0) / modelCallsState.data.length)}ms` : "—", hint: "按模型平均", icon: Gauge, tone: "cyan" as const },
    { label: "累计成本", value: costsState.loading ? "—" : `¥${(costsState.data?.total_cost ?? 0).toFixed(2)}`, hint: "全平台累计", icon: Coins, tone: "orange" as const },
    { label: "异常次数", value: `${modelCallsState.data?.reduce((sum, item) => sum + item.failed_count, 0) ?? "-"}`, hint: "全平台", icon: ToggleLeft, tone: "red" as const },
  ];

  const updateModel = async (model: ReturnType<typeof mapModel>, status: "active" | "disabled") => {
    await modelsApi.updateModel(Number(model.id), {
      display_name: model.raw.display_name,
      capability_tags: model.raw.capability_tags,
      max_context: model.raw.max_context ?? 4096,
      input_price: model.raw.input_price,
      output_price: model.raw.output_price,
      price_unit: model.raw.price_unit,
      status,
    });
  };

  const setEnabled = async (model: ReturnType<typeof mapModel>) => {
    const nextStatus = model.rawStatus === "active" ? "disabled" : "active";
    setUpdatingId(model.id);
    try {
      await updateModel(model, nextStatus);
      notify.success(`模型已${nextStatus === "active" ? "启用" : "停用"}`);
      await modelsState.refetch();
    } catch (error) {
      notify.error("状态更新失败：" + String(error));
    } finally {
      setUpdatingId(null);
    }
  };

  const handleCheckConfig = (model: ReturnType<typeof mapModel>) => {
    const provider = providersState.data?.find((item) => item.provider_id === model.raw.provider_id);
    const hasCredential = (configsState.data?.items ?? []).some(
      (item) => item.provider_id === model.raw.provider_id && item.status === "active",
    );
    if (model.rawStatus !== "active") {
      notify.warning(`${model.name} 当前已停用`);
    } else if (provider?.status !== "active") {
      notify.warning(`${model.name} 的供应商当前不可用`);
    } else if (hasCredential) {
      notify.success(`${model.name} 配置完整，可供智能体调用`);
    } else {
      notify.warning(`${model.name} 尚未配置启用的服务端凭证`);
    }
  };

  const handleHealthCheck = () => {
    const enabled = models.filter((model) => model.rawStatus === "active");
    const ready = enabled.filter((model) => model.status === "可用");
    if (ready.length === enabled.length) {
      notify.success(`配置巡检完成：${ready.length} 个启用模型配置完整`);
    } else {
      notify.warning(`配置巡检完成：${ready.length}/${enabled.length} 个启用模型配置完整`);
    }
  };

  const openEditor = (model: ReturnType<typeof mapModel>) => {
    setEditing(model);
    setForm({
      displayName: model.raw.display_name,
      capabilityTags: model.raw.capability_tags ?? "",
      maxContext: String(model.raw.max_context ?? 4096),
      inputPrice: String(model.raw.input_price),
      outputPrice: String(model.raw.output_price),
      priceUnit: model.raw.price_unit || "1K_TOKENS",
      status: model.rawStatus === "active" ? "active" : "disabled",
    });
    setOpen(true);
  };

  const handleSave = async () => {
    if (!editing || !form.displayName.trim()) {
      notify.warning("请填写模型显示名称");
      return;
    }
    const maxContext = Number(form.maxContext);
    const inputPrice = Number(form.inputPrice);
    const outputPrice = Number(form.outputPrice);
    if (![maxContext, inputPrice, outputPrice].every(Number.isFinite) || maxContext < 1 || inputPrice < 0 || outputPrice < 0) {
      notify.warning("请检查上下文长度和价格配置");
      return;
    }
    setSaving(true);
    try {
      await modelsApi.updateModel(Number(editing.id), {
        display_name: form.displayName.trim(),
        capability_tags: form.capabilityTags.trim() || undefined,
        max_context: maxContext,
        input_price: inputPrice,
        output_price: outputPrice,
        price_unit: form.priceUnit,
        status: form.status,
      });
      notify.success("模型配置已保存");
      setOpen(false);
      await modelsState.refetch();
    } catch (error) {
      notify.error("保存失败：" + String(error));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        title="模型配置"
        description="统一管理平台接入的大模型服务、API Key、模型能力和连接状态。"
        icon={Settings2}
        action={<button onClick={handleHealthCheck} className={`${primaryButton} cursor-pointer`}>一键巡检</button>}
      />
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索模型、供应商或能力" value={query} onChange={setQuery} />
          <SegmentedControl value={statusFilter} options={["全部", "可用", "待配置", "停用"]} onChange={setStatusFilter} />
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
                  onClick={() => handleCheckConfig(model)}
                  className={`${primaryButton} cursor-pointer`}
                >
                  检查配置
                </button>
                <button onClick={() => openEditor(model)} className={`${secondaryButton} cursor-pointer`}>编辑配置</button>
                <button onClick={() => navigate(`/admin/audit?model=${model.id}`)} className={`${secondaryButton} cursor-pointer`}>查看调用</button>
                <button disabled={updatingId === model.id} onClick={() => setEnabled(model)} className={`${secondaryButton} cursor-pointer disabled:cursor-not-allowed disabled:opacity-50`}>{updatingId === model.id ? "更新中..." : model.rawStatus === "active" ? "停用" : "启用"}</button>
              </div>
            </article>
          ))}
        </section>
      )}
      <ModalShell title={editing ? `编辑模型配置：${editing.name}` : "编辑模型配置"} open={open} onClose={() => setOpen(false)}>
        <div className="space-y-4">
          <label className="block text-sm font-bold text-slate-700">
            模型名称
            <input className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.displayName} onChange={(event) => setForm((value) => ({ ...value, displayName: event.target.value }))} />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            供应商
            <input readOnly className="mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-100 px-3 text-sm text-slate-500" value={editing?.provider ?? ""} />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            能力标签
            <input className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.capabilityTags} onChange={(event) => setForm((value) => ({ ...value, capabilityTags: event.target.value }))} placeholder="多个标签使用逗号分隔" />
          </label>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <label className="block text-sm font-bold text-slate-700">最大上下文
              <input type="number" min="1" className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.maxContext} onChange={(event) => setForm((value) => ({ ...value, maxContext: event.target.value }))} />
            </label>
            <label className="block text-sm font-bold text-slate-700">输入价格
              <input type="number" min="0" step="0.000001" className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.inputPrice} onChange={(event) => setForm((value) => ({ ...value, inputPrice: event.target.value }))} />
            </label>
            <label className="block text-sm font-bold text-slate-700">输出价格
              <input type="number" min="0" step="0.000001" className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.outputPrice} onChange={(event) => setForm((value) => ({ ...value, outputPrice: event.target.value }))} />
            </label>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block text-sm font-bold text-slate-700">价格单位
              <select className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.priceUnit} onChange={(event) => setForm((value) => ({ ...value, priceUnit: event.target.value }))}>
                <option value="1K_TOKENS">每千 Token</option>
                <option value="1M_TOKENS">每百万 Token</option>
              </select>
            </label>
            <label className="block text-sm font-bold text-slate-700">状态
              <select className="edu-focus-ring mt-2 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={form.status} onChange={(event) => setForm((value) => ({ ...value, status: event.target.value as "active" | "disabled" }))}>
                <option value="active">启用</option>
                <option value="disabled">停用</option>
              </select>
            </label>
          </div>
          <p className="text-xs leading-5 text-slate-500">服务凭证由后端加密保存，不在模型编辑表单中回显。</p>
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={() => setOpen(false)} className={`${secondaryButton} cursor-pointer`}>取消</button>
          <button disabled={saving} onClick={handleSave} className={`${primaryButton} cursor-pointer disabled:cursor-not-allowed disabled:opacity-50`}><Save className="h-4 w-4" />{saving ? "保存中..." : "保存配置"}</button>
        </div>
      </ModalShell>
    </div>
  );
}
