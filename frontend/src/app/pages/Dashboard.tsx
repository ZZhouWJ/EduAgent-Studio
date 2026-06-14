import React from "react";
import { Link } from "react-router";
import {
  Activity,
  ArrowRight,
  BarChart2,
  BookOpen,
  Bot,
  BrainCircuit,
  CheckCircle2,
  FileCheck2,
  GitBranch,
  Layers3,
  Library,
  LineChart as LineChartIcon,
  Network,
  Route,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
} from "lucide-react";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, BarChart, Bar, Cell } from "recharts";

const STATS = [
  { label: "课程数", value: "3", change: "+1", hint: "本周新增实践课", icon: BookOpen, color: "text-blue-700", bg: "bg-blue-50", ring: "ring-blue-100" },
  { label: "学生数", value: "128", change: "+12", hint: "画像持续更新", icon: Users, color: "text-purple-700", bg: "bg-purple-50", ring: "ring-purple-100" },
  { label: "学习资源", value: "246", change: "+34", hint: "讲义/题库/案例", icon: Library, color: "text-emerald-700", bg: "bg-emerald-50", ring: "ring-emerald-100" },
  { label: "智能体调用", value: "1,284", change: "+156", hint: "多智能体编排", icon: Bot, color: "text-indigo-700", bg: "bg-indigo-50", ring: "ring-indigo-100" },
  { label: "平均掌握度", value: "76%", change: "+2.4%", hint: "课程目标达成", icon: BarChart2, color: "text-orange-700", bg: "bg-orange-50", ring: "ring-orange-100" },
  { label: "审核通过率", value: "92%", change: "+1.2%", hint: "Human-in-loop", icon: CheckCircle2, color: "text-cyan-700", bg: "bg-cyan-50", ring: "ring-cyan-100" },
];

const FLOW_STEPS = [
  { title: "学生画像", desc: "六维特征随学随新", icon: Users, tone: "blue" },
  { title: "智能体诊断", desc: "识别薄弱点与目标", icon: BrainCircuit, tone: "purple" },
  { title: "路径规划", desc: "生成依赖学习路径", icon: Route, tone: "indigo" },
  { title: "资源生成", desc: "讲义、题库、案例、脚本", icon: Layers3, tone: "emerald" },
  { title: "教师审核", desc: "证据追溯与风险把关", icon: ShieldCheck, tone: "orange" },
  { title: "学习反馈", desc: "测评驱动画像更新", icon: FileCheck2, tone: "cyan" },
];

const AGENT_DATA = [
  { name: "周一", calls: 120, pass: 74 },
  { name: "周二", calls: 180, pass: 78 },
  { name: "周三", calls: 150, pass: 81 },
  { name: "周四", calls: 240, pass: 86 },
  { name: "周五", calls: 210, pass: 88 },
  { name: "周六", calls: 280, pass: 91 },
  { name: "周日", calls: 310, pass: 92 },
];

const WEAK_POINTS = [
  { name: "事务隔离级别", score: 38 },
  { name: "SQL 多表连接", score: 46 },
  { name: "数据库范式", score: 52 },
  { name: "索引优化", score: 55 },
  { name: "接口字段设计", score: 61 },
];

const RECENT_RESOURCES = [
  { title: "事务隔离级别图解讲义", type: "课程讲义", confidence: 86 },
  { title: "SQL 多表连接分层练习题", type: "题库", confidence: 91 },
  { title: "FastAPI + PostgreSQL 实操案例", type: "代码案例", confidence: 84 },
  { title: "数据库课程复习路径", type: "学习路径", confidence: 88 },
];

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  indigo: "bg-indigo-50 text-indigo-700 ring-indigo-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
};

export function Dashboard() {
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] bg-white">
        <div className="absolute inset-0 edu-grid-bg opacity-70" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#2563EB,#7C3AED,#06B6D4)]" />
        <div className="relative grid min-h-[210px] grid-cols-[1.28fr_0.72fr] gap-8 p-8">
          <div className="flex min-w-0 flex-col justify-center">
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
              <Sparkles className="h-3.5 w-3.5" />
              软件杯 A3 · 多智能体个性化学习闭环
            </div>
            <h2 className="text-[32px] font-black leading-tight text-slate-950">
              智学工坊 <span className="edu-gradient-text">EduAgent Studio</span>
            </h2>
            <p className="mt-2 text-lg font-semibold text-slate-700">
              面向高校专业课程的多智能体个性化学习资源生成平台
            </p>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              基于学生画像、课程知识库和多智能体协作，自动完成学习诊断、路径规划、资源生成、教师审核与学习反馈优化。
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                to="/agent-workbench"
                className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-[linear-gradient(110deg,#2563EB,#7C3AED)] px-5 text-sm font-bold text-white shadow-[0_14px_30px_rgba(37,99,235,0.25)] transition hover:shadow-[0_18px_36px_rgba(37,99,235,0.32)]"
              >
                进入智能体工作台
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/student-profile"
                className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700 shadow-sm transition hover:border-blue-200 hover:text-blue-700"
              >
                查看学生画像
              </Link>
            </div>
          </div>

          <div className="relative hidden min-h-[184px] overflow-hidden rounded-[22px] border border-blue-100 bg-[linear-gradient(140deg,#F8FAFC,#EFF6FF_58%,#F5F3FF)] p-5 shadow-inner xl:block">
            <div className="absolute inset-4 rounded-[18px] border border-white/80" />
            <div className="relative flex h-full flex-col justify-between">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Agent Orchestration</div>
                  <div className="mt-1 text-lg font-black text-slate-900">可信资源生成链路</div>
                </div>
                <div className="grid h-11 w-11 place-items-center rounded-2xl bg-white text-purple-700 shadow-sm ring-1 ring-purple-100">
                  <Network className="h-5 w-5" />
                </div>
              </div>

              <div className="relative mt-4 grid grid-cols-3 gap-3">
                <div className="absolute left-[16%] right-[16%] top-1/2 h-px bg-gradient-to-r from-blue-200 via-purple-300 to-cyan-200" />
                {[
                  { label: "画像", icon: Users, cls: "text-blue-700 bg-blue-50 ring-blue-100" },
                  { label: "智能体", icon: Bot, cls: "text-purple-700 bg-purple-50 ring-purple-100" },
                  { label: "资源", icon: Library, cls: "text-cyan-700 bg-cyan-50 ring-cyan-100" },
                ].map((node) => {
                  const Icon = node.icon;
                  return (
                    <div key={node.label} className="relative rounded-2xl border border-white bg-white/[0.85] p-3 text-center shadow-sm">
                      <div className={`mx-auto grid h-10 w-10 place-items-center rounded-xl ring-1 ${node.cls}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="mt-2 text-sm font-bold text-slate-800">{node.label}</div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2">
                <div className="rounded-xl bg-white/80 px-3 py-2 ring-1 ring-slate-100">
                  <div className="text-[11px] text-slate-500">证据覆盖</div>
                  <div className="text-base font-black text-blue-700">82%</div>
                </div>
                <div className="rounded-xl bg-white/80 px-3 py-2 ring-1 ring-slate-100">
                  <div className="text-[11px] text-slate-500">低风险</div>
                  <div className="text-base font-black text-emerald-700">94%</div>
                </div>
                <div className="rounded-xl bg-white/80 px-3 py-2 ring-1 ring-slate-100">
                  <div className="text-[11px] text-slate-500">待审核</div>
                  <div className="text-base font-black text-orange-700">12</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        {STATS.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="edu-card edu-card-hover rounded-2xl p-4">
              <div className="mb-4 flex items-start justify-between">
                <div className={`grid h-11 w-11 place-items-center rounded-xl ${stat.bg} ${stat.color} ring-1 ${stat.ring}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className="rounded-full bg-emerald-50 px-2 py-1 text-[11px] font-black text-emerald-700 ring-1 ring-emerald-100">
                  {stat.change}
                </span>
              </div>
              <div className="text-sm font-semibold text-slate-500">{stat.label}</div>
              <div className="mt-1 text-[28px] font-black leading-9 text-slate-950">{stat.value}</div>
              <div className="mt-1 text-xs font-medium text-slate-400">{stat.hint}</div>
            </div>
          );
        })}
      </section>

      <section className="edu-card rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-black text-slate-950">学习闭环流程</h3>
            <p className="mt-1 text-sm text-slate-500">从画像到资源再回到画像更新，形成可演示的闭环证据链。</p>
          </div>
          <GitBranch className="h-5 w-5 text-slate-300" />
        </div>
        <div className="grid grid-cols-6 gap-3">
          {FLOW_STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="relative">
                {index < FLOW_STEPS.length - 1 && (
                  <ArrowRight className="absolute -right-5 top-9 z-10 hidden h-4 w-4 text-slate-300 xl:block" />
                )}
                <div className="h-full rounded-2xl border border-slate-100 bg-slate-50/70 p-4 transition hover:border-blue-200 hover:bg-white hover:shadow-sm">
                  <div className={`mb-3 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[step.tone]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="text-sm font-black text-slate-900">{step.title}</div>
                  <div className="mt-1 min-h-[36px] text-xs leading-[18px] text-slate-500">{step.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-[0.95fr_1.05fr_1.1fr]">
        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-base font-black text-slate-950">
            <Activity className="h-5 w-5 text-orange-600" />
            薄弱知识点 Top 5
          </h3>
          <div className="space-y-3">
            {WEAK_POINTS.map((item, index) => (
              <div key={item.name} className="rounded-xl border border-slate-100 bg-slate-50/80 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="grid h-6 w-6 place-items-center rounded-lg bg-orange-100 text-xs font-black text-orange-700">
                      {index + 1}
                    </span>
                    <span className="text-sm font-bold text-slate-700">{item.name}</span>
                  </div>
                  <span className="text-xs font-black text-orange-700">{item.score}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white">
                  <div
                    className={item.score < 40 ? "h-full rounded-full bg-red-500" : "h-full rounded-full bg-orange-500"}
                    style={{ width: `${item.score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-base font-black text-slate-950">
            <Library className="h-5 w-5 text-blue-600" />
            最近生成资源
          </h3>
          <div className="space-y-3">
            {RECENT_RESOURCES.map((resource) => (
              <div key={resource.title} className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-3 transition hover:border-blue-200 hover:bg-blue-50/40">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
                  <BookOpen className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-black text-slate-800">{resource.title}</div>
                  <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
                    <span>{resource.type}</span>
                    <span className="h-1 w-1 rounded-full bg-slate-300" />
                    <span>可信度 {resource.confidence}%</span>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-300" />
              </div>
            ))}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-base font-black text-slate-950">
              <LineChartIcon className="h-5 w-5 text-purple-600" />
              智能体调用趋势
            </h3>
            <span className="rounded-full bg-purple-50 px-2 py-1 text-xs font-bold text-purple-700 ring-1 ring-purple-100">
              7 日
            </span>
          </div>
          <div className="h-[238px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={AGENT_DATA} margin={{ top: 8, right: 12, left: -18, bottom: 0 }}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748B" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#94A3B8" }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0", boxShadow: "0 12px 28px rgba(15,23,42,0.12)" }}
                  labelStyle={{ color: "#0F172A", fontWeight: 700 }}
                />
                <Line type="monotone" dataKey="calls" name="调用次数" stroke="#7C3AED" strokeWidth={3} dot={{ r: 4, fill: "#7C3AED", stroke: "#fff", strokeWidth: 2 }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="pass" name="审核通过率" stroke="#06B6D4" strokeWidth={2} strokeDasharray="5 5" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="edu-card rounded-2xl p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-base font-black text-slate-950">知识薄弱度横向对比</h3>
            <p className="mt-1 text-sm text-slate-500">使用显式数值标签，避免仅靠颜色表达风险。</p>
          </div>
          <Target className="h-5 w-5 text-slate-300" />
        </div>
        <div className="h-[190px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={WEAK_POINTS} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis dataKey="name" type="category" width={120} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#475569", fontWeight: 600 }} />
              <Tooltip cursor={{ fill: "#F8FAFC" }} contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
              <Bar dataKey="score" name="掌握度" radius={[0, 8, 8, 0]} barSize={20}>
                {WEAK_POINTS.map((entry) => (
                  <Cell key={entry.name} fill={entry.score < 40 ? "#EF4444" : entry.score < 60 ? "#F59E0B" : "#10B981"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
