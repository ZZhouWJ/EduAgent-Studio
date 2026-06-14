import React from "react";
import { ActivitySquare, Bot, CheckCircle2, Clock3, GitBranch, Play, Save, Settings2, ShieldCheck } from "lucide-react";
import { agents } from "../data/demoData";
import { ModalShell, PageHeader, ProgressBar, SearchInput, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function AdminAgentConfig() {
  const [query, setQuery] = React.useState("");
  const [items, setItems] = React.useState(agents);
  const [editing, setEditing] = React.useState(agents[0]);
  const [open, setOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const filtered = items.filter((agent) => `${agent.name}${agent.model}${agent.prompt}${agent.duty}`.toLowerCase().includes(query.toLowerCase()));
  const toggle = (id: string) => {
    setItems((current) => current.map((agent) => agent.id === id ? { ...agent, enabled: !agent.enabled } : agent));
    showToast("智能体启用状态已更新");
  };

  const stats = [
    { label: "智能体数量", value: `${items.length}`, hint: "核心链路", icon: Bot, tone: "blue" as const },
    { label: "启用智能体", value: `${items.filter((a) => a.enabled).length}`, hint: "可执行", icon: CheckCircle2, tone: "emerald" as const },
    { label: "工作流数量", value: "4", hint: "教学主流程", icon: GitBranch, tone: "purple" as const },
    { label: "今日执行次数", value: "1,998", hint: "自动编排", icon: ActivitySquare, tone: "cyan" as const },
    { label: "平均成功率", value: "93%", hint: "近 24 小时", icon: ShieldCheck, tone: "orange" as const },
    { label: "异常次数", value: "6", hint: "已审计", icon: Clock3, tone: "red" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader eyebrow="Agent Configuration" title="智能体配置" description="管理画像诊断、知识定位、路径规划、资源生成、测评生成和审核辅助智能体。" icon={Bot} action={<button onClick={() => showToast("测试工作流执行成功，已生成模拟链路日志")} className={primaryButton}><Play className="h-4 w-4" />测试运行工作流</button>} />
      <section className="grid grid-cols-6 gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4"><SearchInput label="搜索智能体、模型或模板" value={query} onChange={setQuery} /></section>
      <section className="grid grid-cols-[1fr_360px] gap-6">
        <div className="grid grid-cols-2 gap-5">
          {filtered.map((agent) => (
            <article key={agent.id} className="edu-card edu-card-hover rounded-2xl p-5">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div><h2 className="text-lg font-black text-slate-950">{agent.name}</h2><p className="mt-1 text-sm leading-6 text-slate-500">{agent.duty}</p></div>
                <StatusBadge status={agent.enabled ? "启用" : "停用"} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">模型</div><div className="font-black text-slate-900">{agent.model}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">模板</div><div className="truncate font-black text-slate-900">{agent.prompt}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">今日调用</div><div className="font-black text-slate-900">{agent.calls}</div></div>
                <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-slate-400">平均耗时</div><div className="font-black text-slate-900">{agent.duration}</div></div>
              </div>
              <div className="mt-4"><div className="mb-2 flex justify-between text-xs font-bold text-slate-500"><span>成功率</span><span>{agent.success}%</span></div><ProgressBar value={agent.success} tone="emerald" /></div>
              <div className="mt-5 grid grid-cols-3 gap-2">
                <button onClick={() => toggle(agent.id)} className={secondaryButton}>{agent.enabled ? "停用" : "启用"}</button>
                <button onClick={() => { setEditing(agent); setOpen(true); }} className={secondaryButton}>编辑</button>
                <button onClick={() => showToast(`${agent.name} 日志已打开`)} className={primaryButton}>日志</button>
              </div>
            </article>
          ))}
        </div>
        <aside className="edu-card rounded-2xl p-5">
          <h2 className="mb-5 flex items-center gap-2 text-base font-black text-slate-950"><GitBranch className="h-5 w-5 text-blue-700" />工作流图</h2>
          <div className="space-y-3">
            {["画像诊断", "知识定位", "路径规划", "资源生成", "测评生成", "审核辅助"].map((step, index) => (
              <div key={step} className="flex items-center gap-3">
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-blue-50 text-xs font-black text-blue-700 ring-1 ring-blue-100">{index + 1}</div>
                <div className="flex-1 rounded-xl border border-slate-100 bg-white p-3 text-sm font-black text-slate-800">{step}</div>
              </div>
            ))}
          </div>
        </aside>
      </section>
      <ModalShell title={`编辑智能体：${editing.name}`} open={open} onClose={() => setOpen(false)}>
        <div className="space-y-4">
          {["职责说明", "使用模型", "Prompt 模板", "失败重试次数"].map((label, index) => <label key={label} className="block text-sm font-bold text-slate-700">{label}<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" defaultValue={index === 0 ? editing.duty : index === 1 ? editing.model : index === 2 ? editing.prompt : "2"} /></label>)}
          <div className="flex justify-end gap-3"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={() => { setOpen(false); showToast("智能体配置已保存"); }} className={primaryButton}><Save className="h-4 w-4" />保存</button></div>
        </div>
      </ModalShell>
      {toast}
    </div>
  );
}
