import React from "react";
import { Link } from "react-router";
import { ActivitySquare, ArrowRight, Bot, CheckCircle2, CircleAlert, Coins, Database, HardDrive, Library, LockKeyhole, Server, Settings2, ShieldAlert, TerminalSquare, Users } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const ADMIN_STATS = [
  { label: "用户总数", value: "1,284", hint: "学生 1,108 / 教师 86", icon: Users, tone: "blue" },
  { label: "课程总数", value: "42", hint: "本月新增 5 门", icon: Database, tone: "purple" },
  { label: "学习资源总数", value: "8,642", hint: "AI 生成 72%", icon: Library, tone: "emerald" },
  { label: "今日智能体调用", value: "3,480", hint: "峰值 14:00", icon: Bot, tone: "cyan" },
  { label: "今日模型成本", value: "¥186", hint: "预算使用 43%", icon: Coins, tone: "orange" },
  { label: "内容安全风险", value: "7", hint: "2 条高优先级", icon: ShieldAlert, tone: "red" },
];

const OPS_DATA = [
  { name: "00:00", calls: 220, tokens: 42, cost: 18 },
  { name: "04:00", calls: 160, tokens: 28, cost: 12 },
  { name: "08:00", calls: 520, tokens: 84, cost: 36 },
  { name: "12:00", calls: 760, tokens: 118, cost: 52 },
  { name: "16:00", calls: 690, tokens: 106, cost: 45 },
  { name: "20:00", calls: 430, tokens: 71, cost: 23 },
];

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

export function AdminDashboard() {
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
        {ADMIN_STATS.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="edu-card edu-card-hover rounded-2xl p-4">
              <div className={`mb-4 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[stat.tone]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="text-sm font-semibold text-slate-500">{stat.label}</div>
              <div className="mt-1 text-[24px] font-black leading-8 text-slate-950">{stat.value}</div>
              <div className="mt-1 text-xs font-medium text-slate-400">{stat.hint}</div>
            </div>
          );
        })}
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
          <h2 className="mb-5 text-lg font-black text-slate-950">调用与成本趋势</h2>
          <div className="h-[318px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={OPS_DATA} margin={{ top: 8, right: 16, left: -18, bottom: 0 }}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748B" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#94A3B8" }} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
                <Line type="monotone" dataKey="calls" name="调用次数" stroke="#2563EB" strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="tokens" name="Token 消耗" stroke="#7C3AED" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                <Line type="monotone" dataKey="cost" name="成本变化" stroke="#F59E0B" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
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
