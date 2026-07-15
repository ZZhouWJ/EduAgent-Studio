import React from "react";
import { Link } from "react-router-dom";
import {
  Bot,
  Braces,
  FileCode2,
  GitBranch,
  RefreshCw,
  ScrollText,
  Settings2,
  Wrench,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { agentsApi } from "@/lib/api";
import {
  PageHeader,
  SearchInput,
  StatCard,
  StatusBadge,
  primaryButton,
  secondaryButton,
} from "../components/common/ProductUI";

interface AgentDefinition {
  id: string;
  name: string;
  description: string;
  type: string;
}

const WORKFLOW_STEPS = ["画像诊断", "知识定位", "路径规划", "资源生成", "测评生成", "审核辅助"];

export function AdminAgentConfig() {
  const [query, setQuery] = React.useState("");
  const agentsState = useApi(() => agentsApi.listAgents(), []);
  const agents = (agentsState.data ?? []) as AgentDefinition[];
  const filtered = agents.filter((agent) => (
    `${agent.name}${agent.id}${agent.type}${agent.description}`.toLowerCase().includes(query.toLowerCase())
  ));
  const tools = agents.filter((agent) => agent.type === "tool").length;
  const orchestrators = agents.length - tools;

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6 pb-6">
      <PageHeader
        title="智能体运行目录"
        description="查看当前注册的智能体、工具和教学工作流，并进入对应配置与审计页面。"
        icon={Bot}
        action={(
          <button type="button" onClick={() => void agentsState.refetch()} className={primaryButton}>
            <RefreshCw className={`h-4 w-4 ${agentsState.loading ? "animate-spin motion-reduce:animate-none" : ""}`} />
            刷新目录
          </button>
        )}
      />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="注册能力" value={agentsState.loading ? "—" : String(agents.length)} hint="实时注册表" icon={Braces} tone="blue" />
        <StatCard label="教学智能体" value={agentsState.loading ? "—" : String(orchestrators)} hint="负责规划与生成" icon={Bot} tone="emerald" />
        <StatCard label="可调用工具" value={agentsState.loading ? "—" : String(tools)} hint="知识与多模态能力" icon={Wrench} tone="cyan" />
        <StatCard label="主工作流节点" value={String(WORKFLOW_STEPS.length)} hint="生成与审核闭环" icon={GitBranch} tone="orange" />
      </section>

      <section className="grid gap-3 md:grid-cols-3">
        <Link to="/admin/model-config" className={`${secondaryButton} min-h-12 justify-start`}>
          <Settings2 className="h-4 w-4" />模型与密钥配置
        </Link>
        <Link to="/admin/prompts" className={`${secondaryButton} min-h-12 justify-start`}>
          <FileCode2 className="h-4 w-4" />Prompt 模板与版本
        </Link>
        <Link to="/admin/logs" className={`${secondaryButton} min-h-12 justify-start`}>
          <ScrollText className="h-4 w-4" />运行日志与审计
        </Link>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <SearchInput label="搜索智能体、工具或职责" value={query} onChange={setQuery} />
      </section>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
        {agentsState.loading ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-slate-500">正在加载运行目录</div>
        ) : filtered.length === 0 ? (
          <div className="flex min-h-64 items-center justify-center rounded-lg border border-dashed border-slate-300 text-sm text-slate-500">没有匹配的能力</div>
        ) : (
          <section className="grid gap-4 sm:grid-cols-2">
            {filtered.map((agent) => (
              <article key={agent.id} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition-colors hover:border-blue-300">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="text-base font-bold text-slate-950">{agent.name}</h2>
                    <p className="mt-1 truncate font-mono text-xs text-slate-500">{agent.id}</p>
                  </div>
                  <StatusBadge status="已注册" />
                </div>
                <p className="mt-4 min-h-16 text-sm leading-6 text-slate-600">{agent.description}</p>
                <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs">
                  <span className="font-semibold text-slate-500">能力类型</span>
                  <span className="rounded-md bg-slate-100 px-2 py-1 font-semibold text-slate-700">{agent.type || "agent"}</span>
                </div>
              </article>
            ))}
          </section>
        )}

        <aside className="h-fit rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 font-bold text-slate-950">
            <GitBranch className="h-5 w-5 text-blue-700" />
            教学主工作流
          </h2>
          <ol className="mt-5 space-y-1">
            {WORKFLOW_STEPS.map((step, index) => (
              <li key={step} className="relative flex items-center gap-3 py-2">
                {index < WORKFLOW_STEPS.length - 1 && <span className="absolute left-4 top-10 h-5 w-px bg-slate-200" aria-hidden="true" />}
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-bold text-blue-700">{index + 1}</span>
                <span className="text-sm font-semibold text-slate-700">{step}</span>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </div>
  );
}
