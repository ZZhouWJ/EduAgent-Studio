import React from "react";
import { Link } from "react-router";
import { ActivitySquare, ArrowRight, Bot, CheckCircle2, CircleAlert, Coins, Database, HardDrive, Library, LockKeyhole, Server, Settings2, ShieldAlert, TerminalSquare, Users } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "../lib/useApi";
import { statisticsApi } from "../lib/api";

const SERVICES = [
  { name: "后端服务", status: "正常", desc: "响应 128ms", icon: Server },
  { name: "数据库", status: "正常", desc: "连接池 46%", icon: Database },
  { name: "Redis", status: "正常", desc: "命中率 94%", icon: ActivitySquare },
  { name: "MinIO", status: "正常", desc: "存储 68%", icon: HardDrive },
  { name: "模型服务", status: "轻微拥塞", desc: "排队 12 个请求", icon: Bot },
];

const RISKS = [
  ["高风险生成内容", "2", "涉及事实准确性和安全边界"],
  ["低可信度资源", "5", "引用覆盖率低于 70%"],
  ["待教师复核资源", "12", "已通知课程负责人"],
  ["异常调用记录", "3", "同一账号高频请求"],
];

const ENTRY = [
  { title: "模型配置", desc: "统一管理 OpenAI-compatible / 讯飞星火", icon: Settings2, path: "/admin/model-config" },
  { title: "智能体配置", desc: "编排诊断、生成、审核辅助智能体", icon: Bot, path: "/admin/agent-config" },
  { title: "提示词模板", desc: "维护课程资源生成和审核 Prompt", icon: TerminalSquare, path: "/admin/prompts" },
  { title: "调用审计", desc: "按用户、角色、模型追踪调用行为", icon: ActivitySquare, path: "/admin/audit" },
  { title: "成本统计", desc: "按课程、角色和模型核算成本", icon: Coins, path: "/admin/costs" },
];

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  red: "bg-red-50 text-red-700 ring-red-100",
};

function OverviewCard({ label, value, hint, icon, tone }: {
  label: string; value: string; hint: string; icon: React.ComponentType<{ className?: string }>; tone: string;
}) {
  const Icon = icon;
  return (
    <div className="edu-card edu-card-hover rounded-2xl p-4">
      <div className={`mb-4 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[tone]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-sm font-semibold text-slate-500">{label}</div>
      <div className="mt-1 text-[24px] font-black leading-8 text-slate-950">{value}</div>
      <div className="mt-1 text-xs font-medium text-slate-400">{hint}</div>
    </div>
  );
}

export function AdminDashboard() {
  const overview = useApi(() => statisticsApi.overview(), []);
  const recentActivities = useApi(() => statisticsApi.recentActivities({ limit: 10 }), []);
  const modelCalls = useApi(() => statisticsApi.modelCalls(), []);
  const costs = useApi(() => statisticsApi.costs(), []);

  const loading = overview.loading || recentActivities.loading || modelCalls.loading || costs.loading;

  const stats = [
    {
      label: "项目总数",
      value: loading ? "-" : `${overview.data?.project_count ?? 0}`,
      hint: `活跃 ${overview.data?.active_project_count ?? 0} 个`,
      icon: Users,
      tone: "blue",
    },
    {
      label: "任务总数",
      value: loading ? "-" : `${overview.data?.task_count ?? 0}`,
      hint: "平台任务",
      icon: Database,
      tone: "purple",
    },
    {
      label: "学习资源总数",
      value: loading ? "-" : `${overview.data?.artifact_count ?? 0}`,
      hint: "AI 生成资源",
      icon: Library,
      tone: "emerald",
    },
    {
      label: "今日调用次数",
      value: loading ? "-" : `${overview.data?.invocation_count ?? 0}`,
      hint: `成功率 ${overview.data ? Math.round((overview.data.success_invocation_count / Math.max(overview.data.invocation_count, 1)) * 100) : 0}%`,
      icon: Bot,
      tone: "cyan",
    },
    {
      label: "Token 总消耗",
      value: loading ? "-" : `${overview.data ? (overview.data.total_tokens / 1000).toFixed(1) + "K" : "-"}`,
      hint: "输入 + 输出合计",
      icon: ActivitySquare,
      tone: "orange",
    },
    {
      label: "内容安全风险",
      value: loading ? "-" : `${overview.data?.pending_review_count ?? 0}`,
      hint: "待教师复核",
      icon: ShieldAlert,
      tone: "red",
    },
  ];

  const opsChartData = modelCalls.data?.slice(0, 10).map((m) => ({
    name: m.display_name.length > 8 ? m.display_name.slice(0, 8) : m.display_name,
    calls: m.call_count,
    tokens: Math.round((m.total_input_tokens + m.total_output_tokens) / 1000),
    cost: m.avg_latency_ms,
  })) ?? [];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-45" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#0F172A,#2563EB,#10B981)]" />
        <div className="relative flex items-start justify-between gap-6">
          <div>
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-700">
              <LockKeyhole className="h-3.5 w-3.5" />
              系统运营总览
            </div>
            <h1 className="text-[30px] font-black text-slate-950">管理员首页 / 系统运营面板</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              面向平台运维和 AI 治理，集中监控用户、课程、资源、模型调用、成本和内容安全风险。
            </p>
          </div>
          <Link to="/admin/governance" className="inline-flex h-11 shrink-0 items-center gap-2 rounded-xl bg-slate-950 px-5 text-sm font-black text-white">
            查看 AI 治理
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-6 gap-4">
        {stats.map((stat) => (
          <OverviewCard key={stat.label} {...stat} />
        ))}
      </section>

      <section className="grid grid-cols-[0.9fr_1.1fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Server className="h-5 w-5 text-emerald-600" />
            系统运行状态
          </h2>
          <div className="space-y-3">
            {SERVICES.map((service) => {
              const Icon = service.icon;
              const warn = service.status !== "正常";
              return (
                <div key={service.name} className="flex items-center gap-3 rounded-2xl border border-slate-100 bg-white p-4">
                  <div className={`grid h-10 w-10 place-items-center rounded-xl ring-1 ${warn ? "bg-orange-50 text-orange-700 ring-orange-100" : "bg-emerald-50 text-emerald-700 ring-emerald-100"}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-black text-slate-900">{service.name}</div>
                    <div className="mt-1 text-xs text-slate-500">{service.desc}</div>
                  </div>
                  <div className={`rounded-full px-2 py-1 text-[11px] font-black ${warn ? "bg-orange-50 text-orange-700" : "bg-emerald-50 text-emerald-700"}`}>
                    {service.status}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">模型调用统计</h2>
          {loading ? (
            <div className="flex h-[318px] items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" />
            </div>
          ) : opsChartData.length > 0 ? (
            <div className="h-[318px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={opsChartData} margin={{ top: 8, right: 16, left: -18, bottom: 0 }}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748B" }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#94A3B8" }} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
                  <Line type="monotone" dataKey="calls" name="调用次数" stroke="#2563EB" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="tokens" name="Token(K)" stroke="#7C3AED" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-[318px] items-center justify-center text-sm text-slate-400">暂无调用数据</div>
          )}
        </div>
      </section>

      <section className="grid grid-cols-[1fr_1.25fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <CircleAlert className="h-5 w-5 text-red-600" />
            内容安全与审核风险
          </h2>
          <div className="space-y-3">
            {RISKS.map(([title, value, desc]) => (
              <div key={title} className="rounded-2xl border border-slate-100 bg-white p-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-black text-slate-900">{title}</div>
                  <div className="text-xl font-black text-red-600">{value}</div>
                </div>
                <div className="mt-1 text-xs text-slate-500">{desc}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">模型与智能体配置入口</h2>
          <div className="grid grid-cols-5 gap-3">
            {ENTRY.map((entry) => {
              const Icon = entry.icon;
              return (
                <Link key={entry.title} to={entry.path} className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-blue-200 hover:shadow-md">
                  <div className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-sm font-black text-slate-900">{entry.title}</h3>
                  <p className="mt-2 text-xs leading-5 text-slate-500">{entry.desc}</p>
                </Link>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
