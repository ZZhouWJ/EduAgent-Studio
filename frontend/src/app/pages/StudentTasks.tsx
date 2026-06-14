import React from "react";
import { Link } from "react-router";
import { BookOpenCheck, CheckCircle2, Clock3, FileText, MessageSquare, PlayCircle, Target } from "lucide-react";
import { studentTasks } from "../data/demoData";
import { DetailDrawer, EmptyState, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

const statusOptions = ["全部", "进行中", "未开始", "已完成"];

export function StudentTasks() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selected, setSelected] = React.useState<(typeof studentTasks)[number] | null>(null);
  const [completed, setCompleted] = React.useState<string[]>([]);
  const { toast, showToast } = useInlineToast();

  const normalized = query.trim().toLowerCase();
  const tasks = studentTasks
    .map((task) => (completed.includes(task.id) ? { ...task, status: "已完成", progress: 100 } : task))
    .filter((task) => (status === "全部" ? true : task.status === status))
    .filter((task) => !normalized || `${task.title}${task.knowledge}`.toLowerCase().includes(normalized));

  const stats = [
    { label: "待完成任务", value: "3", hint: "今日 2 项", icon: Target, tone: "orange" as const },
    { label: "进行中任务", value: "2", hint: "平均进度 56%", icon: PlayCircle, tone: "blue" as const },
    { label: "已完成任务", value: `${1 + completed.length}`, hint: "本周持续更新", icon: CheckCircle2, tone: "emerald" as const },
    { label: "今日建议学习时长", value: "45 分钟", hint: "拆分为轻任务", icon: Clock3, tone: "purple" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow="Student Learning Tasks"
        title="学习任务"
        description="根据你的学习画像和课程进度，系统为你安排了个性化学习任务。"
        icon={BookOpenCheck}
        action={<Link to="/student/resources" className={primaryButton}>进入推荐资源</Link>}
      />

      <section className="grid grid-cols-4 gap-4">
        {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
      </section>

      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索任务名称或知识点" value={query} onChange={setQuery} />
          <SegmentedControl value={status} options={statusOptions} onChange={setStatus} />
          <button onClick={() => showToast("已刷新任务推荐，学习画像保持同步")} className={secondaryButton}>刷新推荐</button>
        </div>
      </section>

      {tasks.length === 0 ? (
        <EmptyState title="没有匹配的学习任务" description="调整搜索词或状态筛选后，系统会重新展示符合条件的任务。" action={<button className={secondaryButton} onClick={() => { setQuery(""); setStatus("全部"); }}>清空筛选</button>} />
      ) : (
        ["今日任务", "本周任务", "已完成任务"].map((section) => {
          const sectionTasks = tasks.filter((task) => task.section === section || (completed.includes(task.id) && section === "已完成任务"));
          if (sectionTasks.length === 0) return null;

          return (
            <section key={section} className="edu-card rounded-2xl p-6">
              <div className="mb-5 flex items-center justify-between">
                <h2 className="text-lg font-black text-slate-950">{section}</h2>
                <span className="text-xs font-bold text-slate-400">{sectionTasks.length} 项</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {sectionTasks.map((task) => (
                  <button key={task.id} onClick={() => setSelected(task)} className="rounded-2xl border border-slate-100 bg-white p-4 text-left transition hover:border-blue-200 hover:shadow-md">
                    <div className="mb-3 flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-base font-black text-slate-900">{task.title}</h3>
                        <p className="mt-1 text-xs leading-5 text-slate-500">{task.course}</p>
                      </div>
                      <StatusBadge status={completed.includes(task.id) ? "已完成" : task.status} />
                    </div>
                    <div className="mb-3 flex flex-wrap gap-2">
                      <span className="rounded-lg bg-blue-50 px-2 py-1 text-xs font-bold text-blue-700">{task.knowledge}</span>
                      <span className="rounded-lg bg-slate-100 px-2 py-1 text-xs font-bold text-slate-600">{task.estimate}</span>
                      <span className="rounded-lg bg-purple-50 px-2 py-1 text-xs font-bold text-purple-700">{task.resources} 个资源</span>
                    </div>
                    <p className="min-h-[40px] text-xs leading-5 text-slate-500">推荐原因：{task.reason}</p>
                    <div className="mt-4">
                      <div className="mb-2 flex justify-between text-xs font-bold text-slate-500">
                        <span>任务进度</span>
                        <span>{completed.includes(task.id) ? 100 : task.progress}%</span>
                      </div>
                      <ProgressBar value={completed.includes(task.id) ? 100 : task.progress} tone={task.progress === 100 ? "emerald" : "blue"} />
                    </div>
                  </button>
                ))}
              </div>
            </section>
          );
        })
      )}

      {selected && <DetailDrawer title={selected.title} subtitle={`${selected.course} / ${selected.knowledge}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-5">
          {[
            ["任务目标", selected.objective],
            ["测验要求", selected.quiz],
            ["完成标准", selected.standard],
            ["智能体推荐理由", selected.agentReason],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
              <h3 className="text-sm font-black text-slate-900">{label}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{value}</p>
            </div>
          ))}
          <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-black text-blue-900">
              <FileText className="h-4 w-4" />
              推荐资源
            </h3>
            <div className="space-y-2 text-sm font-semibold text-blue-800">
              <div>事务隔离级别图解讲义</div>
              <div>SQL 多表连接分层练习题</div>
              <div>银行转账并发实验案例</div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Link to="/student/resources" className={primaryButton}>开始学习</Link>
            <button onClick={() => { setCompleted((items) => Array.from(new Set([...items, selected.id]))); showToast("任务已标记完成"); }} className={secondaryButton}>标记完成</button>
            <Link to="/student/feedback" className={secondaryButton}>
              <MessageSquare className="h-4 w-4" />
              提交反馈
            </Link>
          </div>
        </div>
      </DetailDrawer>}
      {toast}
    </div>
  );
}
