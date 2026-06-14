import React from "react";
import { Link } from "react-router";
import { AlertTriangle, ArrowRight, BookOpen, Bot, CheckSquare, Database, FileText, Library, MessageSquare, ShieldAlert, Sparkles, Target, Users } from "lucide-react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const TEACHER_STATS = [
  { label: "管理课程数", value: "3", hint: "本学期", icon: BookOpen, tone: "blue" },
  { label: "学生人数", value: "128", hint: "2 个班级", icon: Users, tone: "purple" },
  { label: "待审核资源", value: "12", hint: "3 个高优先级", icon: CheckSquare, tone: "orange" },
  { label: "班级平均掌握度", value: "76%", hint: "较上周 +2.4%", icon: Target, tone: "emerald" },
  { label: "本周新增反馈", value: "45", hint: "5 条需关注", icon: MessageSquare, tone: "cyan" },
  { label: "高风险资源", value: "3", hint: "需人工复核", icon: ShieldAlert, tone: "red" },
];

const WEAKNESS_DATA = [
  { name: "事务隔离", score: 38 },
  { name: "多表连接", score: 46 },
  { name: "数据库范式", score: 52 },
  { name: "索引优化", score: 55 },
  { name: "接口设计", score: 61 },
];

const ACTION_ITEMS = [
  { title: "3 个 AI 生成资源待审核", desc: "其中 1 个资源引用覆盖率低于 70%", icon: CheckSquare, tone: "orange", action: "进入审核" },
  { title: "12 名学生事务隔离级别掌握度低于 50%", desc: "建议发布基础图解讲义和判断题", icon: Users, tone: "red", action: "查看学生" },
  { title: "5 条学习反馈需要关注", desc: "集中在可重复读、串行化和幻读概念", icon: MessageSquare, tone: "blue", action: "查看反馈" },
  { title: "课程知识库有 2 份资料待补充", desc: "实验说明和教师 PPT 页码缺少结构化标注", icon: Database, tone: "purple", action: "补充资料" },
];

const GENERATION_SUGGESTIONS = [
  { title: "事务隔离级别图解讲义", type: "讲义", target: "12 名薄弱学生" },
  { title: "多表连接分层练习题", type: "题库", target: "全班巩固" },
  { title: "银行转账并发案例", type: "案例", target: "项目实践组" },
  { title: "FastAPI + PostgreSQL 综合实验", type: "实验", target: "课程项目冲刺" },
];

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
  red: "bg-red-50 text-red-700 ring-red-100",
};

export function TeacherDashboard() {
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-50" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#2563EB,#7C3AED,#06B6D4)]" />
        <div className="relative grid grid-cols-[1.25fr_0.75fr] gap-6">
          <div>
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-purple-100 bg-purple-50 px-3 py-1.5 text-xs font-bold text-purple-700">
              <Sparkles className="h-3.5 w-3.5" />
              教学工作台
            </div>
            <h2 className="text-[30px] font-black leading-tight text-slate-950">张老师，欢迎回到教学工作台。</h2>
            <p className="mt-2 text-sm font-bold text-slate-700">当前课程：数据库系统原理与 Web 项目实践</p>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              系统检测到“事务隔离级别”和“SQL 多表连接”是当前班级主要薄弱点，建议生成针对性资源并安排阶段测评。
            </p>
            <div className="mt-6 flex gap-3">
              <Link to="/teacher/agent-workbench" className="inline-flex h-11 items-center gap-2 rounded-xl bg-[linear-gradient(110deg,#2563EB,#7C3AED)] px-5 text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)]">
                进入智能体工作台
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/teacher/review" className="inline-flex h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700">
                处理待审核资源
              </Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              ["今日待办", "4", "按优先级处理"],
              ["重点学生", "12", "掌握度低于 50%"],
              ["建议生成", "4", "资源生成机会"],
              ["知识库缺口", "2", "资料待补充"],
            ].map(([label, value, hint]) => (
              <div key={label} className="rounded-2xl border border-slate-100 bg-white/[0.85] p-4 shadow-sm">
                <div className="text-xs font-bold text-slate-400">{label}</div>
                <div className="mt-1 text-2xl font-black text-slate-950">{value}</div>
                <div className="mt-1 text-xs text-slate-500">{hint}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-6 gap-4">
        {TEACHER_STATS.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="edu-card edu-card-hover rounded-2xl p-4">
              <div className={`mb-4 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[stat.tone]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="text-sm font-semibold text-slate-500">{stat.label}</div>
              <div className="mt-1 text-[26px] font-black leading-8 text-slate-950">{stat.value}</div>
              <div className="mt-1 text-xs font-medium text-slate-400">{stat.hint}</div>
            </div>
          );
        })}
      </section>

      <section className="grid grid-cols-[1fr_0.95fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
            待处理事项
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {ACTION_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-2xl border border-slate-100 bg-white p-4">
                  <div className={`mb-3 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[item.tone]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h4 className="text-sm font-black text-slate-900">{item.title}</h4>
                  <p className="mt-2 min-h-[40px] text-xs leading-5 text-slate-500">{item.desc}</p>
                  <button className="mt-3 text-xs font-black text-blue-700">{item.action}</button>
                </div>
              );
            })}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h3 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Target className="h-5 w-5 text-red-600" />
            班级薄弱点分析
          </h3>
          <div className="h-[285px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={WEAKNESS_DATA} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis dataKey="name" type="category" width={86} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#475569", fontWeight: 600 }} />
                <Tooltip cursor={{ fill: "#F8FAFC" }} contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }} />
                <Bar dataKey="score" name="掌握度" radius={[0, 8, 8, 0]} barSize={22}>
                  {WEAKNESS_DATA.map((entry) => (
                    <Cell key={entry.name} fill={entry.score < 45 ? "#EF4444" : entry.score < 60 ? "#F59E0B" : "#10B981"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="edu-card rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-lg font-black text-slate-950">
            <Bot className="h-5 w-5 text-purple-600" />
            资源生成建议
          </h3>
          <Link to="/teacher/agent-workbench" className="text-sm font-bold text-blue-700">进入生成</Link>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {GENERATION_SUGGESTIONS.map((item, index) => (
            <div key={item.title} className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-purple-200 hover:shadow-md">
              <div className="mb-3 flex items-center justify-between">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-purple-50 text-purple-700 ring-1 ring-purple-100">
                  {index === 0 ? <FileText className="h-5 w-5" /> : index === 1 ? <CheckSquare className="h-5 w-5" /> : index === 2 ? <Library className="h-5 w-5" /> : <BookOpen className="h-5 w-5" />}
                </div>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-bold text-slate-600">{item.type}</span>
              </div>
              <h4 className="min-h-[40px] text-sm font-black leading-5 text-slate-900">{item.title}</h4>
              <div className="mt-4 text-xs font-bold text-slate-500">{item.target}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
