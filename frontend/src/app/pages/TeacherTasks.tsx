import React from "react";
import { BookOpen, CalendarClock, CheckSquare, ClipboardList, Plus, RefreshCw, Save, Users } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi } from "@/lib/api";
import { taskTypeLabel } from "@/lib/educationLabels";
import { EmptyState, ModalShell, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

const STATUS_LABELS: Record<string, string> = {
  in_progress: "进行中",
  completed: "已完成",
  assigned: "已发布",
  draft: "草稿",
};

export function TeacherTasks() {
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [selectedId, setSelectedId] = React.useState<number | null>(null);

  // 新建任务 Modal
  const [modalOpen, setModalOpen] = React.useState(false);
  const [form, setForm] = React.useState({
    course_id: 0,
    title: "",
    description: "",
    due_date: "",
  });
  const [submitting, setSubmitting] = React.useState(false);

  const { data: taskData, loading: loadingTasks, refetch: reloadTasks } = useApi(
    () => learningApi.listTasks({ page_size: 50 }),
    []
  );
  const { data: courseData } = useApi(() => learningApi.listCourses(), []);

  const courses = courseData ?? [];

  const items = (taskData?.items ?? []).map((t) => ({
    id: t.id,
    title: t.title,
    course: t.course_name,
    type: taskTypeLabel(t.type),
    due: t.due_date ? t.due_date.replace("T", " ").slice(0, 16) : "—",
    completion: Math.round((t.completion_rate ?? 0) * 100),
    status: STATUS_LABELS[t.status] ?? t.status,
    rawStatus: t.status,
    priority: t.priority,
    description: t.description ?? "",
    raw: t,
  }));

  const normalized = query.trim().toLowerCase();
  const statusFiltered = items.filter((item) => {
    if (statusFilter === "全部") return true;
    if (statusFilter === "低完成率") return item.completion < 45;
    return item.status === statusFilter;
  });
  const searched = statusFiltered.filter(
    (item) => `${item.title}${item.type}${item.course}`.toLowerCase().includes(normalized)
  );

  const selected = searched.find((item) => item.id === selectedId) ?? searched[0];

  const inProgressCount = items.filter((i) => i.rawStatus === "in_progress").length;
  const lowCompletionCount = items.filter((i) => i.completion < 45).length;
  const avgCompletion = items.length > 0
    ? Math.round(items.reduce((sum, i) => sum + i.completion, 0) / items.length)
    : 0;
  const coveredCourseCount = new Set(items.map((item) => item.raw.course_id)).size;

  const stats = [
    { label: "已发布任务", value: `${items.length}`, hint: "覆盖多门课程", icon: ClipboardList, tone: "blue" as const },
    { label: "进行中任务", value: `${inProgressCount}`, hint: "本周跟踪", icon: CalendarClock, tone: "purple" as const },
    { label: "平均完成率", value: `${avgCompletion}%`, hint: "整体情况", icon: CheckSquare, tone: "emerald" as const },
    { label: "低完成率任务", value: `${lowCompletionCount}`, hint: "需提醒", icon: Users, tone: "orange" as const },
    { label: "涉及课程", value: `${coveredCourseCount}`, hint: "本人课程范围", icon: BookOpen, tone: "cyan" as const },
  ];

  const handleCreateTask = async () => {
    if (!form.course_id) { notify.warning("请选择课程"); return; }
    if (!form.title.trim()) { notify.warning("请填写任务标题"); return; }
    setSubmitting(true);
    try {
      await learningApi.createTask({
        course_id: form.course_id,
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        due_date: form.due_date || undefined,
      });
      notify.success("任务创建成功");
      setModalOpen(false);
      setForm({ course_id: 0, title: "", description: "", due_date: "" });
      reloadTasks();
    } catch (e: any) {
      notify.error("创建失败：" + (e?.message || String(e)));
    } finally {
      setSubmitting(false);
    }
  };

  const handleRefresh = () => {
    reloadTasks();
    notify.success("任务列表已刷新");
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow=""
        title="学习任务管理"
        description="面向班级或学生个体发布学习任务，并跟踪完成情况。"
        icon={ClipboardList}
        action={<button onClick={() => setModalOpen(true)} className={`${primaryButton} cursor-pointer`}><Plus className="h-4 w-4" />新建任务</button>}
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
              <SegmentedControl value={statusFilter} options={["全部", "进行中", "已完成", "低完成率"]} onChange={setStatusFilter} />
            </div>
            <div className="custom-scrollbar max-h-[620px] space-y-3 overflow-y-auto pr-1">
              {searched.length === 0 ? (
                <EmptyState title="没有匹配任务" description="更换筛选条件后可继续查看任务完成情况。" />
              ) : (
                searched.map((task) => (
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
                      {task.priority === "high" && <span className="rounded-lg bg-red-50 px-2 py-1 text-[11px] font-bold text-red-700">紧急</span>}
                      {task.priority === "medium" && <span className="rounded-lg bg-orange-50 px-2 py-1 text-[11px] font-bold text-orange-700">中等</span>}
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
                    <p className="mt-1 text-sm text-slate-500">{selected.course} / 截止 {selected.due}</p>
                  </div>
                  <StatusBadge status={selected.status} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    ["任务目标", selected.description || "暂无描述"],
                    ["任务类型", selected.type],
                    ["当前完成率", `${selected.completion}%`],
                    ["优先级别", selected.priority === "high" ? "紧急" : selected.priority === "medium" ? "中等" : "普通"],
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
                    onClick={handleRefresh}
                    className={`${secondaryButton} cursor-pointer`}
                  >
                    <RefreshCw className="h-4 w-4" />
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

      {/* 新建任务 Modal */}
      <ModalShell title="新建学习任务" open={modalOpen} onClose={() => setModalOpen(false)}>
        <div className="space-y-4">
          {/* 课程选择 */}
          <label className="text-sm font-bold text-slate-700">
            课程 <span className="text-red-500">*</span>
            <select
              className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700"
              value={form.course_id}
              onChange={(e) => setForm(f => ({ ...f, course_id: Number(e.target.value) }))}
            >
              <option value={0}>— 选择课程 —</option>
              {courses.map((c: any) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </label>

          {/* 任务标题 */}
          <label className="text-sm font-bold text-slate-700">
            任务标题 <span className="text-red-500">*</span>
            <input
              className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700"
              placeholder="例如：SQL 多表连接练习"
              value={form.title}
              onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
            />
          </label>

          {/* 任务描述 */}
          <label className="text-sm font-bold text-slate-700">
            任务描述
            <textarea
              className="edu-focus-ring mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
              rows={3}
              placeholder="描述任务要求和目标..."
              value={form.description}
              onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
            />
          </label>

          {/* 截止时间 */}
          <label className="text-sm font-bold text-slate-700">
            截止时间
            <input
              type="datetime-local"
              className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700"
              value={form.due_date}
              onChange={(e) => setForm(f => ({ ...f, due_date: e.target.value }))}
            />
          </label>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button onClick={() => setModalOpen(false)} className={`${secondaryButton} cursor-pointer`}>取消</button>
          <button
            onClick={handleCreateTask}
            disabled={submitting}
            className={`${primaryButton} cursor-pointer flex items-center gap-2`}
          >
            {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            {submitting ? "创建中..." : "保存任务"}
          </button>
        </div>
      </ModalShell>
    </div>
  );
}

function Loader2({ className }: { className?: string }) {
  return <span className={`inline-block animate-spin ${className}`}>⟳</span>;
}
