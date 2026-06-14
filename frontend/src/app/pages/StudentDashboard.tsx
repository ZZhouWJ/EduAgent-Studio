import React from "react";
import { Link } from "react-router";
import {
  ArrowRight,
  BarChart3,
  BookOpenCheck,
  Bot,
  CheckCircle2,
  Clock3,
  FileText,
  GraduationCap,
  HelpCircle,
  Library,
  PlayCircle,
  Route,
  Sparkles,
  Target,
  Timer,
} from "lucide-react";

const STUDENT_STATS = [
  { label: "综合掌握度", value: "64%", hint: "较上次 +4%", icon: BarChart3, tone: "blue" },
  { label: "待完成任务", value: "5", hint: "今日 2 项", icon: CheckCircle2, tone: "purple" },
  { label: "本周学习时长", value: "4.5h", hint: "目标 8h", icon: Timer, tone: "emerald" },
  { label: "最近测验分数", value: "45", hint: "需要巩固", icon: FileText, tone: "orange" },
  { label: "薄弱知识点", value: "3", hint: "优先处理", icon: Target, tone: "red" },
];

const TODAY_PATH = [
  { title: "复习 SQL 多表连接", time: "12 分钟", reason: "事务案例依赖多表查询能力", type: "微课复习", status: "已完成" },
  { title: "学习事务隔离级别图解讲义", time: "18 分钟", reason: "最近测验概念边界不清", type: "图解讲义", status: "当前" },
  { title: "完成 5 道概念判断题", time: "8 分钟", reason: "用即时测评确认理解", type: "分层练习", status: "待完成" },
  { title: "查看银行转账并发案例", time: "10 分钟", reason: "把抽象概念迁移到实践场景", type: "案例动画", status: "待完成" },
  { title: "提交学习反馈", time: "3 分钟", reason: "用于更新学生画像和下次推荐", type: "反馈表单", status: "待完成" },
];

const RESOURCES = [
  { title: "事务隔离级别图解讲义", type: "讲义", minutes: "18 分钟", confidence: "86%", icon: FileText },
  { title: "SQL 多表连接分层练习题", type: "练习", minutes: "12 分钟", confidence: "91%", icon: CheckCircle2 },
  { title: "FastAPI + PostgreSQL 实操案例", type: "代码案例", minutes: "35 分钟", confidence: "84%", icon: BookOpenCheck },
  { title: "银行转账并发动画脚本", type: "动画脚本", minutes: "10 分钟", confidence: "88%", icon: PlayCircle },
];

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  red: "bg-red-50 text-red-700 ring-red-100",
};

export function StudentDashboard() {
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-60" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#2563EB,#06B6D4,#7C3AED)]" />
        <div className="relative grid grid-cols-[1.35fr_0.65fr] gap-6">
          <div>
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
              <GraduationCap className="h-3.5 w-3.5" />
              我的学习空间
            </div>
            <h2 className="text-[30px] font-black leading-tight text-slate-950">
              李明，今天继续学习“数据库系统原理与 Web 项目实践”
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              系统已根据你的画像和最近测评结果，为你更新了本周学习路径。今天优先处理事务隔离级别和多表连接的薄弱点。
            </p>
            <div className="mt-6 flex gap-3">
              <Link to="/student/learning-path" className="inline-flex h-11 items-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)] transition hover:bg-blue-700">
                继续学习当前路径
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/student/tutor" className="inline-flex h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700 transition hover:border-blue-200 hover:text-blue-700">
                向 AI 提问
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {[
              ["综合掌握度", "64%", "当前课程整体水平"],
              ["本周学习目标", "事务与并发控制专题", "建议先补概念边界"],
              ["今日推荐时长", "45 分钟", "拆成 5 个轻任务"],
            ].map(([label, value, hint]) => (
              <div key={label} className="rounded-2xl border border-slate-100 bg-white/80 p-4 shadow-sm">
                <div className="text-xs font-bold text-slate-400">{label}</div>
                <div className="mt-1 text-lg font-black text-slate-900">{value}</div>
                <div className="mt-1 text-xs text-slate-500">{hint}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-5 gap-4">
        {STUDENT_STATS.map((stat) => {
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

      <section className="grid grid-cols-[1.45fr_0.95fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-black text-slate-950">今日学习路径</h3>
              <p className="mt-1 text-sm text-slate-500">按依赖关系拆分，完成后会自动触发画像更新。</p>
            </div>
            <Route className="h-5 w-5 text-blue-500" />
          </div>

          <div className="space-y-3">
            {TODAY_PATH.map((step, index) => (
              <div key={step.title} className="grid grid-cols-[36px_1fr_auto] items-start gap-3 rounded-2xl border border-slate-100 bg-slate-50/70 p-3">
                <div className={`grid h-9 w-9 place-items-center rounded-xl text-xs font-black ring-1 ${step.status === "已完成" ? "bg-emerald-50 text-emerald-700 ring-emerald-100" : step.status === "当前" ? "bg-blue-600 text-white ring-blue-200" : "bg-white text-slate-500 ring-slate-200"}`}>
                  {index + 1}
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 className="text-sm font-black text-slate-900">{step.title}</h4>
                    <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-bold text-slate-500 ring-1 ring-slate-100">{step.type}</span>
                  </div>
                  <p className="mt-1 text-xs leading-5 text-slate-500">推荐原因：{step.reason}</p>
                </div>
                <div className="text-right">
                  <div className="text-xs font-black text-slate-700">{step.time}</div>
                  <div className={`mt-1 rounded-full px-2 py-0.5 text-[11px] font-bold ${step.status === "当前" ? "bg-blue-50 text-blue-700" : step.status === "已完成" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                    {step.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <div className="edu-card rounded-2xl p-6">
            <h3 className="mb-4 flex items-center gap-2 text-base font-black text-slate-950">
              <Target className="h-5 w-5 text-orange-600" />
              我的薄弱点
            </h3>
            <div className="space-y-3">
              {[
                ["事务隔离级别", "32%", "概念边界不清"],
                ["SQL 多表连接", "46%", "复杂查询仍需练习"],
                ["接口字段设计", "61%", "项目迁移易错"],
              ].map(([name, score, hint]) => (
                <div key={name} className="rounded-xl border border-slate-100 bg-white p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-black text-slate-800">{name}</span>
                    <span className="text-xs font-black text-orange-700">{score}</span>
                  </div>
                  <div className="text-xs text-slate-500">{hint}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-[linear-gradient(135deg,#EFF6FF,#F5F3FF)] p-6 shadow-[0_10px_30px_rgba(37,99,235,0.08)]">
            <div className="mb-3 grid h-11 w-11 place-items-center rounded-2xl bg-white text-blue-700 shadow-sm ring-1 ring-blue-100">
              <Bot className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-black text-slate-950">遇到问题？向学习智能体提问</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              可以直接问：“可重复读和串行化到底有什么区别？”
            </p>
            <Link to="/student/tutor" className="mt-4 inline-flex h-10 items-center gap-2 rounded-xl bg-slate-950 px-4 text-sm font-bold text-white">
              开始提问
              <HelpCircle className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <section className="edu-card rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-lg font-black text-slate-950">
            <Library className="h-5 w-5 text-blue-600" />
            推荐学习资源
          </h3>
          <Link to="/student/resources" className="text-sm font-bold text-blue-700">查看全部</Link>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {RESOURCES.map((resource) => {
            const Icon = resource.icon;
            return (
              <div key={resource.title} className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-blue-200 hover:shadow-md">
                <div className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
                  <Icon className="h-5 w-5" />
                </div>
                <h4 className="min-h-[40px] text-sm font-black leading-5 text-slate-900">{resource.title}</h4>
                <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
                  <span>{resource.type} · {resource.minutes}</span>
                  <span className="font-black text-emerald-700">{resource.confidence}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
