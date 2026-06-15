import React from "react";
import { Copy, FileText, History, Play, Plus, Save, WandSparkles } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { promptsApi, PromptTemplate, PromptVersion } from "@/lib/api";
import { DetailDrawer, ModalShell, PageHeader, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "@/components/common/ProductUI";

function mapTemplate(t: PromptTemplate) {
  return {
    id: String(t.template_id),
    name: t.template_name,
    agent: t.type_name,
    version: `v${t.current_version_no}`,
    enabled: t.is_active,
    updatedAt: t.updated_at ? new Date(t.updated_at).toLocaleString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }) : "-",
    raw: t,
  };
}

function mapVersion(v: PromptVersion) {
  return {
    id: String(v.version_id),
    no: `v${v.version_no}`,
    note: v.change_note ?? "-",
    active: v.is_active,
    createdAt: v.created_at ? new Date(v.created_at).toLocaleString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }) : "-",
    creator: v.creator_real_name ?? "-",
    raw: v,
  };
}

export function AdminPrompts() {
  const [query, setQuery] = React.useState("");
  const [taskTypeFilter, setTaskTypeFilter] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapTemplate> | null>(null);
  const [open, setOpen] = React.useState(false);
  const [historyOpen, setHistoryOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const templatesState = useApi(() => promptsApi.getTemplates({ page: 1, page_size: 100, keyword: query || undefined }), [query]);

  const versionsState = useApi(
    () => selected ? promptsApi.getVersions(Number(selected.id)) : Promise.resolve({ data: [] }),
    [selected?.id]
  );

  const templates = (templatesState.data?.items ?? []).map(mapTemplate);
  const taskTypeOptions = ["全部", ...Array.from(new Set(templates.map((t) => t.agent)))];
  const filtered = templates.filter((item) => {
    const typeMatch = taskTypeFilter === "全部" || item.agent === taskTypeFilter;
    const keywordMatch = `${item.name}${item.agent}${item.version}`.toLowerCase().includes(query.toLowerCase());
    return typeMatch && keywordMatch;
  });

  const selectedTemplate = selected ?? filtered[0] ?? null;
  const versions = (versionsState.data ?? []).map(mapVersion);

  const stats = [
    { label: "模板总数", value: `${templatesState.data?.total ?? "-"}`, hint: "覆盖主流程", icon: FileText, tone: "blue" as const },
    { label: "已启用模板", value: `${templates.filter((p) => p.enabled).length}`, hint: "可被调用", icon: WandSparkles, tone: "emerald" as const },
    { label: "最近更新", value: templates[0]?.updatedAt ?? "-", hint: "最新模板", icon: History, tone: "purple" as const },
    { label: "关联智能体", value: `${taskTypeOptions.length - 1}`, hint: "多智能体链路", icon: Play, tone: "cyan" as const },
    { label: "版本数量", value: `${versions.length}`, hint: "可追溯", icon: Copy, tone: "orange" as const },
  ];

  const handleSelectTemplate = (t: ReturnType<typeof mapTemplate>) => {
    setSelected(t);
    setHistoryOpen(false);
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader eyebrow="Prompt Templates" title="提示词模板" description="管理资源生成、画像诊断、教师审核和防幻觉检查等场景的提示词模板。" icon={FileText} action={<button onClick={() => setOpen(true)} className={primaryButton}><Plus className="h-4 w-4" />新建模板</button>} />
      <section className="grid grid-cols-5 gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="grid grid-cols-[360px_1fr] gap-6">
        <aside className="edu-card rounded-2xl p-5">
          <div className="mb-4 space-y-4"><SearchInput label="搜索模板" value={query} onChange={setQuery} /><SegmentedControl value={taskTypeFilter} options={taskTypeOptions} onChange={setTaskTypeFilter} /></div>
          {templatesState.loading ? (
            <div className="flex items-center justify-center py-8"><div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : filtered.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-400">暂无模板数据</div>
          ) : (
            <div className="custom-scrollbar max-h-[590px] space-y-2 overflow-y-auto pr-1">
              {filtered.map((item) => (
                <button key={item.id} onClick={() => handleSelectTemplate(item)} className={`w-full rounded-2xl border p-4 text-left transition ${selectedTemplate?.id === item.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"}`}>
                  <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-black text-slate-900">{item.name}</h3><StatusBadge status={item.enabled ? "启用" : "停用"} /></div>
                  <p className="mt-2 text-xs font-semibold text-slate-500">{item.agent} / {item.version}</p>
                </button>
              ))}
            </div>
          )}
        </aside>
        <main className="edu-card rounded-2xl p-6">
          {!selectedTemplate ? (
            <div className="flex items-center justify-center py-16 text-sm text-slate-400">请选择一个模板</div>
          ) : (
            <>
              <div className="mb-5 flex items-start justify-between gap-4">
                <div><h2 className="text-xl font-black text-slate-950">{selectedTemplate.name}</h2><p className="mt-1 text-sm text-slate-500">{selectedTemplate.agent} / {selectedTemplate.version} / {selectedTemplate.updatedAt}</p></div>
                <StatusBadge status={selectedTemplate.enabled ? "启用" : "停用"} />
              </div>
              <div className="mb-5 rounded-2xl border border-slate-100 bg-slate-950 p-5 font-mono text-sm leading-6 text-slate-200">
                {versions[0]?.raw?.prompt_content ?? "Prompt 内容通过版本历史加载"}
              </div>
              <div className="mt-5 grid grid-cols-4 gap-3">
                <button onClick={() => setOpen(true)} className={primaryButton}>编辑模板</button>
                <button onClick={() => showToast("模板副本已创建")} className={secondaryButton}><Copy className="h-4 w-4" />复制模板</button>
                <button onClick={() => setHistoryOpen(true)} className={secondaryButton}>版本历史</button>
                <button onClick={() => showToast("Prompt 已使用当前变量模拟渲染")} className={secondaryButton}><Play className="h-4 w-4" />模拟渲染</button>
              </div>
            </>
          )}
        </main>
      </section>
      <ModalShell title="编辑提示词模板" open={open} onClose={() => setOpen(false)}>
        <label className="block text-sm font-bold text-slate-700">Prompt 内容<textarea className="edu-focus-ring mt-2 h-40 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6" defaultValue="请基于输入变量生成结构化学习资源，并输出引用、难度和风险检查。" /></label>
        <div className="mt-5 flex justify-end gap-3"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={() => { setOpen(false); showToast("提示词模板已保存"); }} className={primaryButton}><Save className="h-4 w-4" />保存</button></div>
      </ModalShell>
      <DetailDrawer title="版本历史" subtitle={selectedTemplate?.name ?? ""} open={historyOpen} onClose={() => setHistoryOpen(false)}>
        {versionsState.loading ? (
          <div className="py-8 text-center text-sm text-slate-400">加载中...</div>
        ) : versions.length === 0 ? (
          <div className="py-8 text-center text-sm text-slate-400">暂无版本历史</div>
        ) : (
          versions.map((v) => (
            <div key={v.id} className="mb-3 rounded-2xl border border-slate-100 bg-white p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-700">{v.no} {v.active ? "（当前版本）" : ""}</span>
                <span className="text-xs text-slate-400">{v.createdAt} / {v.creator}</span>
              </div>
              <p className="mt-2 text-xs text-slate-500">{v.note}</p>
            </div>
          ))
        )}
      </DetailDrawer>
      {toast}
    </div>
  );
}
