import React from "react";
import { CalendarClock, CheckSquare, ClipboardList, Plus, Save, Users } from "lucide-react";
import { courses, teacherTasks } from "../data/demoData";
import { EmptyState, ModalShell, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function TeacherTasks() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selectedId, setSelectedId] = React.useState(teacherTasks[0].id);
  const [items, setItems] = React.useState(teacherTasks);
  const [open, setOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const filtered = items.filter((item) => (status === "全部" || item.status === status) && `${item.title}${item.knowledge}${item.target}`.toLowerCase().includes(query.toLowerCase()));
  const selected = filtered.find((item) => item.id === selectedId) || filtered[0] || items[0];

  const addTask = () => {
    const created = {
      id: `tt-${Date.now()}`,
      title: "事务隔离级别强化测评",
      course: courses[0].name,
      knowledge: "事务隔离级别",
      target: "数据库 22-1 班重点学生",
      due: "06-21 20:00",
      completion: 0,
      status: "进行中",
    };
    setItems((current) => [created, ...current]);
    setSelectedId(created.id);
    setOpen(false);
    showToast("新学习任务已插入任务列表");
  };

  const stats = [
    { label: "已发布任务", value: `${items.length}`, hint: "覆盖 3 门课程", icon: ClipboardList, tone: "blue" as const },
    { label: "进行中任务", value: `${items.filter((item) => item.status === "进行中").length}`, hint: "本周跟踪", icon: CalendarClock, tone: "purple" as const },
    { label: "平均完成率", value: "58%", hint: "较上周 +6%", icon: CheckSquare, tone: "emerald" as const },
    { label: "低完成率任务", value: "1", hint: "需提醒", icon: Users, tone: "orange" as const },
    { label: "本周新增任务", value: "4", hint: "含 AI 推荐", icon: Plus, tone: "cyan" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow="Teacher Task Management"
        title="学习任务管理"
        description="面向班级或学生个体发布学习任务，并跟踪完成情况。"
        icon={ClipboardList}
        action={<button onClick={() => setOpen(true)} className={primaryButton}><Plus className="h-4 w-4" />新建任务</button>}
      />

      <section className="grid grid-cols-5 gap-4">
        {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
      </section>

      <section className="grid grid-cols-[0.9fr_1.1fr] gap-6">
        <div className="edu-card rounded-2xl p-5">
          <div className="mb-4 flex flex-wrap items-end gap-4">
            <SearchInput label="搜索任务、知识点或班级" value={query} onChange={setQuery} />
            <SegmentedControl value={status} options={["全部", "进行中", "低完成率"]} onChange={setStatus} />
          </div>
          <div className="custom-scrollbar max-h-[620px] space-y-3 overflow-y-auto pr-1">
            {filtered.length === 0 ? (
              <EmptyState title="没有匹配任务" description="更换筛选条件后可继续查看任务完成情况。" />
            ) : (
              filtered.map((task) => (
                <button key={task.id} onClick={() => setSelectedId(task.id)} className={`w-full rounded-2xl border p-4 text-left transition ${selected?.id === task.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"}`}>
                  <div className="mb-2 flex items-start justify-between gap-3">
                    <h3 className="text-sm font-black text-slate-900">{task.title}</h3>
                    <StatusBadge status={task.status} />
                  </div>
                  <p className="text-xs leading-5 text-slate-500">{task.course}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="rounded-lg bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600">{task.knowledge}</span>
                    <span className="rounded-lg bg-purple-50 px-2 py-1 text-[11px] font-bold text-purple-700">{task.target}</span>
                    <span className="rounded-lg bg-orange-50 px-2 py-1 text-[11px] font-bold text-orange-700">截止 {task.due}</span>
                  </div>
                  <div className="mt-3">
                    <div className="mb-1 flex justify-between text-xs font-bold text-slate-500">
                      <span>完成率</span>
                      <span>{task.completion}%</span>
                    </div>
                    <ProgressBar value={task.completion} tone={task.completion < 45 ? "orange" : "blue"} />
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-black text-slate-950">{selected.title}</h2>
              <p className="mt-1 text-sm text-slate-500">{selected.target} / {selected.due}</p>
            </div>
            <StatusBadge status={selected.status} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              ["任务目标", "巩固薄弱知识点，并在测评中达到 80% 正确率。"],
              ["推荐资源", "图解讲义、分层练习题、课程案例片段。"],
              ["测评要求", "完成概念判断题和案例分析题。"],
              ["学习反馈摘要", "学生主要困惑集中在概念边界和项目迁移。"],
            ].map(([title, desc]) => (
              <div key={title} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
                <h3 className="text-sm font-black text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-6">
            <h3 className="mb-3 text-sm font-black text-slate-950">学生完成情况</h3>
            <div className="grid grid-cols-4 gap-3">
              {["李明 64%", "王华 72%", "赵强 38%", "周敏 86%"].map((item) => (
                <div key={item} className="rounded-xl bg-white p-3 text-sm font-bold text-slate-700 ring-1 ring-slate-100">{item}</div>
              ))}
            </div>
          </div>
          <div className="mt-6 rounded-2xl border border-orange-100 bg-orange-50 p-4">
            <h3 className="text-sm font-black text-orange-900">未完成学生</h3>
            <p className="mt-2 text-sm leading-6 text-orange-800">赵强、刘佳、黄一鸣尚未开始，建议发送提醒或调整任务难度。</p>
          </div>
          <div className="mt-6 flex gap-3">
            <button onClick={() => showToast("已发送学习任务提醒")} className={primaryButton}>提醒未完成学生</button>
            <button onClick={() => showToast("学生完成数据已刷新")} className={secondaryButton}>刷新完成情况</button>
          </div>
        </div>
      </section>

      <ModalShell title="新建学习任务" open={open} onClose={() => setOpen(false)}>
        <div className="grid grid-cols-2 gap-4">
          {["选择课程", "选择知识点", "选择学生或班级", "关联资源", "设置截止时间", "测评要求"].map((label, index) => (
            <label key={label} className="text-sm font-bold text-slate-700">
              {label}
              <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700" defaultValue={index === 0 ? courses[0].name : index === 1 ? "事务隔离级别" : ""} />
            </label>
          ))}
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={() => setOpen(false)} className={secondaryButton}>取消</button>
          <button onClick={addTask} className={primaryButton}><Save className="h-4 w-4" />保存任务</button>
        </div>
      </ModalShell>
      {toast}
    </div>
  );
}
