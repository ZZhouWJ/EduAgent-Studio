import React from "react";
import { Copy, FileText, History, Play, Plus, Save, WandSparkles } from "lucide-react";
import { promptTemplates } from "../data/demoData";
import { DetailDrawer, ModalShell, PageHeader, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function AdminPrompts() {
  const [query, setQuery] = React.useState("");
  const [agent, setAgent] = React.useState("全部");
  const [selected, setSelected] = React.useState(promptTemplates[0]);
  const [open, setOpen] = React.useState(false);
  const [historyOpen, setHistoryOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const agentOptions = ["全部", ...Array.from(new Set(promptTemplates.map((item) => item.agent)))];
  const filtered = promptTemplates.filter((item) => (agent === "全部" || item.agent === agent) && `${item.name}${item.agent}${item.version}`.toLowerCase().includes(query.toLowerCase()));
  const stats = [
    { label: "模板总数", value: `${promptTemplates.length}`, hint: "覆盖主流程", icon: FileText, tone: "blue" as const },
    { label: "已启用模板", value: `${promptTemplates.filter((p) => p.enabled).length}`, hint: "可被调用", icon: WandSparkles, tone: "emerald" as const },
    { label: "最近更新", value: "今天", hint: "3 个模板", icon: History, tone: "purple" as const },
    { label: "关联智能体", value: "6", hint: "多智能体链路", icon: Play, tone: "cyan" as const },
    { label: "版本数量", value: "32", hint: "可追溯", icon: Copy, tone: "orange" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader eyebrow="Prompt Templates" title="提示词模板" description="管理资源生成、画像诊断、教师审核和防幻觉检查等场景的提示词模板。" icon={FileText} action={<button onClick={() => setOpen(true)} className={primaryButton}><Plus className="h-4 w-4" />新建模板</button>} />
      <section className="grid grid-cols-5 gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="grid grid-cols-[360px_1fr] gap-6">
        <aside className="edu-card rounded-2xl p-5">
          <div className="mb-4 space-y-4"><SearchInput label="搜索模板" value={query} onChange={setQuery} /><SegmentedControl value={agent} options={agentOptions} onChange={setAgent} /></div>
          <div className="custom-scrollbar max-h-[590px] space-y-2 overflow-y-auto pr-1">
            {filtered.map((item) => (
              <button key={item.id} onClick={() => setSelected(item)} className={`w-full rounded-2xl border p-4 text-left transition ${selected.id === item.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"}`}>
                <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-black text-slate-900">{item.name}</h3><StatusBadge status={item.enabled ? "启用" : "停用"} /></div>
                <p className="mt-2 text-xs font-semibold text-slate-500">{item.agent} / {item.version}</p>
              </button>
            ))}
          </div>
        </aside>
        <main className="edu-card rounded-2xl p-6">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div><h2 className="text-xl font-black text-slate-950">{selected.name}</h2><p className="mt-1 text-sm text-slate-500">{selected.agent} / {selected.version} / {selected.updatedAt}</p></div>
            <StatusBadge status={selected.enabled ? "启用" : "停用"} />
          </div>
          <div className="mb-5 flex flex-wrap gap-2">{selected.variables.map((item) => <span key={item} className="rounded-lg bg-purple-50 px-2.5 py-1 text-xs font-bold text-purple-700 ring-1 ring-purple-100">{`{{${item}}}`}</span>)}</div>
          <h3 className="mb-3 text-sm font-black text-slate-950">Prompt 内容预览</h3>
          <div className="rounded-2xl border border-slate-100 bg-slate-950 p-5 font-mono text-sm leading-6 text-slate-200">
            你是 EduAgent Studio 的课程智能体。请基于课程证据、学生画像和任务目标生成结构化结果，并标注引用来源、风险提示和教师复核建议。
          </div>
          <div className="mt-5 grid grid-cols-4 gap-3">
            <button onClick={() => setOpen(true)} className={primaryButton}>编辑模板</button>
            <button onClick={() => showToast("模板副本已创建")} className={secondaryButton}><Copy className="h-4 w-4" />复制模板</button>
            <button onClick={() => setHistoryOpen(true)} className={secondaryButton}>版本历史</button>
            <button onClick={() => showToast("Prompt 已使用当前变量模拟渲染")} className={secondaryButton}><Play className="h-4 w-4" />模拟渲染</button>
          </div>
        </main>
      </section>
      <ModalShell title="编辑提示词模板" open={open} onClose={() => setOpen(false)}>
        <label className="block text-sm font-bold text-slate-700">Prompt 内容<textarea className="edu-focus-ring mt-2 h-40 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6" defaultValue="请基于输入变量生成结构化学习资源，并输出引用、难度和风险检查。" /></label>
        <div className="mt-5 flex justify-end gap-3"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={() => { setOpen(false); showToast("提示词模板已保存"); }} className={primaryButton}><Save className="h-4 w-4" />保存</button></div>
      </ModalShell>
      <DetailDrawer title="版本历史" subtitle={selected.name} open={historyOpen} onClose={() => setHistoryOpen(false)}>
        {["v3.1 当前版本", "v3.0 增加风险提示", "v2.8 增加引用覆盖率", "v2.5 优化教师复核建议"].map((item) => <div key={item} className="mb-3 rounded-2xl border border-slate-100 bg-white p-4 text-sm font-bold text-slate-700">{item}</div>)}
      </DetailDrawer>
      {toast}
    </div>
  );
}
