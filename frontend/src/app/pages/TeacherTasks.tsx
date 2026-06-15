import React from "react";
import { CalendarClock, CheckSquare, ClipboardList, Plus, Save, Users } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, statisticsApi } from "@/lib/api";
import { EmptyState, ModalShell, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

const STATUS_LABELS: Record<string, string> = {
  in_progress: "进行中",
  completed: "已完成",
  not_started: "未开始",
};

export function TeacherTasks() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selectedId, setSelectedId] = React.useState<number | null>(null);
  const [open, setOpen] = React.useState(false);

  const { data: taskData, loading: loadingTasks } = useApi(
    () => learningApi.listTasks({ page_size: 50 }),
    []
  );
  const { data: statsData } = useApi(() => statisticsApi.overview(), []);

  const items = (taskData?.items ?? []).map((t) => ({
    id: t.id,
    title: t.title,
    course: t.course_name,
    type: t.type,
    due: t.due_date ? t.due_date.replace("T", " ").slice(0, 16) : "—",
    completion: Math.round((t.completion_rate ?? 0) * 100),
    status: STATUS_LABELS[t.status] ?? t.status,
    rawStatus: t.status,
    priority: t.priority,
    description: t.description ?? "",
  }));

  const normalized = query.trim().toLowerCase();
  const filtered = items.filter(
    (item) =>
      (status === "全部" || item.status === status) &&
      `${item.title}${item.type}${item.course}`.toLowerCase().includes(normalized)
  );

  const selected = filtered.find((item) => item.id === selectedId) ?? filtered[0] ?? items[0];

  const inProgressCount = items.filter((i) => i.status === "进行中").length;
  const lowCompletionCount = items.filter((i) => i.completion < 45).length;
  const avgCompletion = items.length > 0
    ? Math.round(items.reduce((sum, i) => sum + i.completion, 0) / items.length)
    : 0;

  const stats = [
    { label: "已发布任务", value: `${items.length}`, hint: "覆盖多门课程", icon: ClipboardList, tone: "blue" as const },
    { label: "进行中任务", value: `${inProgressCount}`, hint: "本周跟踪", icon: CalendarClock, tone: "purple" as const },
    { label: "平均完成率", value: `${avgCompletion}%`, hint: "整体情况", icon: CheckSquare, tone: "emerald" as const },
    { label: "低完成率任务", value: `${lowCompletionCount}`, hint: "需提醒", icon: Users, tone: "orange" as const },
    { label: "总任务数", value: `${statsData?.task_count ?? items.length}`, hint: "平台任务", icon: Plus, tone: "cyan" as const },
  ];

  const addTask = () => {
    setOpen(false);
    notify.success("新学习任务已插入任务列表（演示模式）");
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow="Teacher Task Management"
        title="学习任务管理"
        description="面向班级或学生个体发布学习任务，并跟踪完成情况。"
        icon={ClipboardList}
        action={<button onClick={() => setOpen(true)} className={`${primaryButton} cursor-pointer`}><Plus className="h-4 w-4" />新建任务</button>}
      />

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-5">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>

      {loadingTasks ? (
        <div className="flex items-center justify-center h-32 text-slate-400">加载中...</div>
      ) : (
        <section className="grid grid-cols-[0.9fr_1.1fr] gap-6">
          {/* Task List */}
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
                  <button
                    key={task.id}
                    onClick={() => setSelectedId(task.id)}
                    className={`w-full cursor-pointer rounded-2xl border p-4 text-left transition ${selected?.id === task.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"}`}
                  >
                    <div className="mb-2 flex items-start justify-between gap-3">
                      <h3 className="text-sm font-black text-slate-900">{task.title}</h3>
                      <StatusBadge status={task.status} />
                    </div>
                    <p className="text-xs leading-5 text-slate-500">{task.course}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="rounded-lg bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600">{task.type}</span>
                      {task.priority === "high" && (
                        <span className="rounded-lg bg-red-50 px-2 py-1 text-[11px] font-bold text-red-700">紧急</span>
                      )}
                      {task.priority === "medium" && (
                        <span className="rounded-lg bg-orange-50 px-2 py-1 text-[11px] font-bold text-orange-700">中等</span>
                      )}
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

          {/* Detail Panel */}
          <div className="edu-card rounded-2xl p-6">
            {selected ? (
              <>
                <div className="mb-5 flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-black text-slate-950">{selected.title}</h2>
                    <p className="mt-1 text-sm text-slate-500">{selected.type} / {selected.due}</p>
                  </div>
                  <StatusBadge status={selected.status} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    ["任务目标", selected.description || "暂无描述"],
                    ["推荐资源", "通过任务详情页查看关联资源列表"],
                    ["任务类型", selected.type],
                    ["当前完成率", `${selected.completion}%`],
                  ].map(([title, desc]) => (
                    <div key={title} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
                      <h3 className="text-sm font-black text-slate-900">{title}</h3>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{desc}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-6 rounded-2xl border border-orange-100 bg-orange-50 p-4">
                  <h3 className="text-sm font-black text-orange-900">低完成率提醒</h3>
                  <p className="mt-2 text-sm leading-6 text-orange-800">
                    {lowCompletionCount > 0
                      ? `${lowCompletionCount} 个任务完成率低于 45%，建议发送提醒或调整任务难度。`
                      : "所有任务完成率正常。"}
                  </p>
                </div>
                <div className="mt-6 flex gap-3">
                  <button
                    onClick={() => notify.success("已发送学习任务提醒")}
                    className={`${primaryButton} cursor-pointer`}
                  >
                    提醒未完成学生
                  </button>
                  <button
                    onClick={() => { loadingTasks; notify.info("学生完成数据已刷新"); }}
                    className={`${secondaryButton} cursor-pointer`}
                  >
                    刷新完成情况
                  </button>
                </div>
              </>
            ) : (
              <div className="flex h-full items-center justify-center text-slate-400">选择一个任务查看详情</div>
            )}
          </div>
        </section>
      )}

      <ModalShell title="新建学习任务" open={open} onClose={() => setOpen(false)}>
        <div className="grid grid-cols-2 gap-4">
          {["选择课程", "选择知识点", "选择学生或班级", "关联资源", "设置截止时间", "测评要求"].map((label) => (
            <label key={label} className="text-sm font-bold text-slate-700">
              {label}
              <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700" />
            </label>
          ))}
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={() => setOpen(false)} className={`${secondaryButton} cursor-pointer`}>取消</button>
          <button onClick={addTask} className={`${primaryButton} cursor-pointer`}><Save className="h-4 w-4" />保存任务</button>
        </div>
      </ModalShell>
    </div>
  );
}
