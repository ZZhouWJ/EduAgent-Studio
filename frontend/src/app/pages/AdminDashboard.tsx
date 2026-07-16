import React from "react";
import { Link } from "react-router-dom";
import { ActivitySquare, ArrowRight, Bot, CircleAlert, Coins, Database, Library, LockKeyhole, Server, Settings2, ShieldAlert, TerminalSquare, Users } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "@/lib/useApi";
import { statisticsApi } from "@/lib/api";
import { SafeLottie } from "../components/SafeLottie";

interface ServiceItem {
  name: string;
  status: string;
  desc: string;
  icon: React.ComponentType<{ className?: string }>;
  key: string;
}

const INITIAL_SERVICES: ServiceItem[] = [
  { name: "后端服务", status: "检测中", desc: "—", icon: Server, key: "api" },
  { name: "数据库", status: "检测中", desc: "—", icon: Database, key: "db" },
  { name: "Redis", status: "检测中", desc: "—", icon: ActivitySquare, key: "redis" },
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
  slate: "bg-slate-100 text-slate-700 ring-slate-200",
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
    <div className="edu-card rounded-2xl p-4">
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
  const [services, setServices] = React.useState<ServiceItem[]>(INITIAL_SERVICES);

  // Poll health endpoints every 30 seconds
  React.useEffect(() => {
    const tick = async () => {
      setServices((prev) => prev.map((s) => {
        if (["api", "db", "redis"].includes(s.key)) return { ...s, status: "检测中", desc: "—" };
        return s;
      }));
      try {
        const r1 = await fetch("/api/health");
        const j1 = await r1.json();
        setServices((prev) => prev.map((s) =>
          s.key === "api"
            ? { ...s, status: j1.code === 0 ? "正常" : "异常", desc: j1.data?.env ?? "—" }
            : s
        ));
      } catch {
        setServices((prev) => prev.map((s) => s.key === "api" ? { ...s, status: "异常", desc: "连接失败" } : s));
      }
      try {
        const r2 = await fetch("/api/health/db");
        const j2 = await r2.json();
        setServices((prev) => prev.map((s) =>
          s.key === "db"
            ? {
                ...s,
                status: j2.code === 0 ? "正常" : "异常",
                desc: j2.code === 0 ? `v${j2.data?.server_version ?? "—"}` : "连接失败",
              }
            : s
        ));
      } catch {
        setServices((prev) => prev.map((s) => s.key === "db" ? { ...s, status: "异常", desc: "连接失败" } : s));
      }
      try {
        const r3 = await fetch("/api/health/redis");
        const j3 = await r3.json();
        setServices((prev) => prev.map((s) =>
          s.key === "redis"
            ? { ...s, status: j3.code === 0 ? "正常" : "异常", desc: j3.code === 0 ? "连接可用" : "连接失败" }
            : s
        ));
      } catch {
        setServices((prev) => prev.map((s) => s.key === "redis" ? { ...s, status: "异常", desc: "连接失败" } : s));
      }
    };
    tick();
    const h = setInterval(tick, 30000);
    return () => clearInterval(h);
  }, []);

  const platformOverview = useApi(() => statisticsApi.getPlatformOverview(), []);
  const modelCalls = useApi(() => statisticsApi.modelCalls(), []);
  const resourceStats = useApi(() => statisticsApi.getResourceStats(), []);

  const loading = platformOverview.loading || modelCalls.loading || resourceStats.loading;

  const abnormalCallCount = (modelCalls.data ?? []).reduce(
    (total, model) => total + Number(model.failed_count || 0) + Number(model.timeout_count || 0),
    0,
  );
  const blockedCallCount = (modelCalls.data ?? []).reduce(
    (total, model) => total + Number(model.blocked_count || 0),
    0,
  );
  const risks = [
    {
      title: "待教师复核资源",
      value: resourceStats.data?.pending ?? 0,
      level: (resourceStats.data?.pending ?? 0) > 0 ? "待处理" : "正常",
    },
    {
      title: "审核退回资源",
      value: resourceStats.data?.rejected ?? 0,
      level: (resourceStats.data?.rejected ?? 0) > 0 ? "需复查" : "正常",
    },
    {
      title: "异常模型调用",
      value: abnormalCallCount,
      level: abnormalCallCount > 0 ? "需排查" : "正常",
    },
    {
      title: "治理策略拦截",
      value: blockedCallCount,
      level: blockedCallCount > 0 ? "已拦截" : "正常",
    },
  ];

  const stats = [
    {
      label: "课程总数",
      value: loading ? "-" : `${platformOverview.data?.course_count ?? 0}`,
      hint: `学生 ${platformOverview.data?.student_count ?? 0} 人`,
      icon: Users,
      tone: "blue",
    },
    {
      label: "学习资源总数",
      value: loading ? "-" : `${platformOverview.data?.resource_count ?? 0}`,
      hint: `待审核 ${platformOverview.data?.pending_resources ?? 0} 个`,
      icon: Library,
      tone: "emerald",
    },
    {
      label: "今日调用次数",
      value: loading ? "-" : `${platformOverview.data?.today_invocations ?? 0}`,
      hint: `总调用 ${platformOverview.data?.invocation_count ?? 0} 次`,
      icon: Bot,
      tone: "cyan",
    },
    {
      label: "Token 总消耗",
      value: loading ? "-" : `${platformOverview.data ? (platformOverview.data.total_tokens / 1000).toFixed(1) + "K" : "-"}`,
      hint: "输入 + 输出合计",
      icon: ActivitySquare,
      tone: "orange",
    },
    {
      label: "总成本",
      value: loading ? "-" : `¥${platformOverview.data?.total_cost?.toFixed(2) ?? "0.00"}`,
      hint: "平台运营成本",
      icon: Coins,
      tone: "purple",
    },
    {
      label: "内容安全风险",
      value: loading ? "-" : `${platformOverview.data?.pending_resources ?? 0}`,
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
      <section className="edu-card relative overflow-hidden rounded-2xl p-7">
        <div className="relative flex items-center justify-between gap-6">
          <div className="min-w-0">
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600">
              <LockKeyhole className="h-3.5 w-3.5" />
              系统运营总览
            </div>
            <h1 className="text-[30px] font-semibold text-slate-900">管理员首页 · 系统运营面板</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              面向平台运维和内容治理，集中监控用户、课程、资源、模型调用、成本和内容安全风险。
            </p>
            <Link to="/admin/governance" className="mt-5 inline-flex h-10 items-center gap-2 rounded-lg bg-slate-900 px-4 text-sm font-semibold text-white transition-colors hover:bg-slate-800">
              查看治理面板
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="hidden h-40 w-40 shrink-0 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50/60 lg:block">
            <SafeLottie source="dashboard" className="h-full w-full" speed={0.7} />
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {stats.map((stat) => (
          <OverviewCard key={stat.label} {...stat} />
        ))}
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Server className="h-5 w-5 text-emerald-600" />
            系统运行状态
          </h2>
          <div className="space-y-3">
            {services.map((service) => {
              const Icon = service.icon;
              const warn = service.status !== "正常" && service.status !== "未知" && service.status !== "—" && service.status !== "检测中";
              const isPending = service.status === "检测中";
              return (
                <div key={service.key} className="flex items-center gap-3 rounded-2xl border border-slate-100 bg-white p-4">
                  <div className={`grid h-10 w-10 place-items-center rounded-xl ring-1 ${isPending ? "bg-slate-100 text-slate-400 ring-slate-200" : warn ? "bg-orange-50 text-orange-700 ring-orange-100" : "bg-emerald-50 text-emerald-700 ring-emerald-100"}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-black text-slate-900">{service.name}</div>
                    <div className="mt-1 text-xs text-slate-500">{service.desc}</div>
                  </div>
                  <div className={`rounded-full px-2 py-1 text-[11px] font-black ${isPending ? "bg-slate-100 text-slate-500" : warn ? "bg-orange-50 text-orange-700" : "bg-emerald-50 text-emerald-700"}`}>
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

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_1.25fr]">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <CircleAlert className="h-5 w-5 text-red-600" />
            内容安全与审核风险
          </h2>
          <div className="space-y-3">
            {risks.map((risk) => {
              const isNormal = risk.level === "正常";
              return (
                <div key={risk.title} className="rounded-2xl border border-slate-100 bg-white p-4">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-black text-slate-900">{risk.title}</div>
                    <div className={`text-xl font-black ${isNormal ? "text-emerald-600" : "text-orange-600"}`}>{risk.value}</div>
                  </div>
                  <div className={`mt-1 text-xs ${isNormal ? "text-emerald-600" : "text-slate-500"}`}>{risk.level}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 text-lg font-black text-slate-950">模型与智能体配置入口</h2>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
            {ENTRY.map((entry) => {
              const Icon = entry.icon;
              return (
                <Link key={entry.title} to={entry.path} className="cursor-pointer rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-blue-200 hover:shadow-md">
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
