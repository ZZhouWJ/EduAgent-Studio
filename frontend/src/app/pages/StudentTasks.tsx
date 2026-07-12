import React from "react";
import { Link } from "react-router-dom";
import { BookOpenCheck, CheckCircle2, Clock3, FileText, MessageSquare, PlayCircle, Target } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi } from "@/lib/api";
import { DetailDrawer, EmptyState, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

const STATUS_LABELS: Record<string, string> = {
  in_progress: "进行中",
  completed: "已完成",
  not_started: "未开始",
};

const STATUS_OPTIONS = ["全部", "进行中", "未开始", "已完成"];

function resourceIcon(type: string) {
  const t = (type ?? "").toLowerCase();
  if (t.includes("讲义") || t.includes("文档")) return FileText;
  if (t.includes("练习") || t.includes("题")) return CheckCircle2;
  if (t.includes("代码") || t.includes("案例")) return BookOpenCheck;
  if (t.includes("视频") || t.includes("动画")) return PlayCircle;
  return FileText;
}

export function StudentTasks() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selected, setSelected] = React.useState<{
    id: number; title: string; course_name: string; type: string;
    status: string; priority: string; description: string; course_id: number;
  } | null>(null);
  const [completed, setCompleted] = React.useState<string[]>([]);
  const [markingId, setMarkingId] = React.useState<string | null>(null);

  const { data: tasksData, loading, refetch } = useApi(
    () => learningApi.listTasks({ page_size: 100 }),
    []
  );
  const { data: resourcesData } = useApi(
    () => resourcesApi.list({ course_id: selected?.course_id, page_size: 10 }),
    [selected?.course_id]
  );

  const allTasks = React.useMemo(() => {
    return (tasksData?.items ?? []).map((task) => ({
      ...task,
      id: task.id,
      course: task.course_name,
      knowledge: task.type,
      displayStatus: STATUS_LABELS[task.status] ?? task.status,
      progress: task.status === "completed" ? 100 : task.status === "in_progress" ? 50 : 0,
      section:
        completed.includes(String(task.id)) ? "已完成任务" :
        task.status === "in_progress" ? "今日任务" :
        task.status === "not_started" ? "本周任务" :
        "本周任务",
    }));
  }, [tasksData, completed]);

  const normalized = query.trim().toLowerCase();
  const tasks = allTasks
    .filter((task) => (status === "全部" ? true : task.displayStatus === status))
    .filter((task) => !normalized || `${task.title}${task.knowledge}`.toLowerCase().includes(normalized));

  const taskSections = ["今日任务", "本周任务", "已完成任务"];

  const stats = [
    { label: "待完成任务", value: String(allTasks.filter((t) => t.status === "not_started" && !completed.includes(String(t.id))).length), hint: "本周任务", icon: Target, tone: "orange" as const },
    { label: "进行中任务", value: String(allTasks.filter((t) => t.status === "in_progress" && !completed.includes(String(t.id))).length), hint: "今日任务", icon: PlayCircle, tone: "blue" as const },
    { label: "已完成任务", value: String(allTasks.filter((t) => t.status === "completed" || completed.includes(String(t.id))).length), hint: "本周持续更新", icon: CheckCircle2, tone: "emerald" as const },
    { label: "今日建议时长", value: `${Math.max(30, allTasks.filter((t) => t.status === "in_progress").length * 15)} 分钟`, hint: "轻量化拆分", icon: Clock3, tone: "purple" as const },
  ];

  const recommendedResources = (resourcesData?.items ?? []).slice(0, 3).map((r) => ({
    title: r.resource_title,
    type: r.resource_type || "资源",
    icon: resourceIcon(r.resource_type),
  }));

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        title="学习任务"
        description="根据你的学习画像和课程进度，系统为你安排了个性化学习任务。"
        icon={BookOpenCheck}
        action={<Link to="/student/resources" className={`${primaryButton} cursor-pointer`}>进入推荐资源</Link>}
      />

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>

      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索任务名称或知识点" value={query} onChange={setQuery} />
          <SegmentedControl value={status} options={STATUS_OPTIONS} onChange={setStatus} />
          <button onClick={() => { refetch(); notify.info("任务列表已刷新"); }} className={`${secondaryButton} cursor-pointer`}>刷新推荐</button>
        </div>
      </section>

      {loading ? (
        <div className="edu-card rounded-2xl p-12 text-center">
          <div className="text-slate-400">加载任务数据中...</div>
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState
          title="没有匹配的学习任务"
          description="调整搜索词或状态筛选后，系统会重新展示符合条件的任务。"
          action={<button className={`${secondaryButton} cursor-pointer`} onClick={() => { setQuery(""); setStatus("全部"); }}>清空筛选</button>}
        />
      ) : (
        taskSections.map((section) => {
          const sectionTasks = tasks.filter((task) => task.section === section);
          if (sectionTasks.length === 0) return null;
          return (
            <section key={section} className="edu-card rounded-2xl p-6">
              <div className="mb-5 flex items-center justify-between">
                <h2 className="text-lg font-black text-slate-950">{section}</h2>
                <span className="text-xs font-bold text-slate-400">{sectionTasks.length} 项</span>
              </div>
              <div className="edu-stagger grid grid-cols-2 gap-4">
                {sectionTasks.map((task) => {
                  const isDone = completed.includes(String(task.id)) || task.progress === 100;
                  return (
                    <button
                      key={task.id}
                      onClick={() => setSelected({
                        id: task.id,
                        title: task.title,
                        course_name: task.course_name,
                        type: task.type,
                        status: task.displayStatus,
                        priority: task.priority,
                        description: task.description,
                        course_id: task.course_id,
                      })}
                      className={`group cursor-pointer rounded-2xl border bg-white p-4 text-left transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-lg ${
                        isDone
                          ? "border-emerald-200 bg-emerald-50/40 hover:border-emerald-300"
                          : "border-slate-100 hover:border-blue-200"
                      }`}
                    >
                      <div className="mb-3 flex items-start justify-between gap-3">
                        <div>
                          <h3 className="text-base font-black text-slate-900">{task.title}</h3>
                          <p className="mt-1 text-xs leading-5 text-slate-500">{task.course}</p>
                        </div>
                        <StatusBadge status={task.displayStatus} />
                      </div>
                      <div className="mb-3 flex flex-wrap gap-2">
                        <span className="rounded-lg bg-blue-50 px-2 py-1 text-xs font-bold text-blue-700">{task.knowledge}</span>
                        {task.priority && task.priority !== "low" && (
                          <span className={`rounded-lg px-2 py-1 text-xs font-bold ${task.priority === "high" ? "bg-red-50 text-red-700" : "bg-orange-50 text-orange-700"}`}>
                            {task.priority === "high" ? "紧急" : "中等"}
                          </span>
                        )}
                      </div>
                      <p className="min-h-[40px] text-xs leading-5 text-slate-500">
                        {task.description || "暂无描述"}
                      </p>
                      <div className="mt-4">
                        <div className="mb-2 flex justify-between text-xs font-bold text-slate-500">
                          <span>任务进度</span>
                          <span className="tabular-nums transition-colors duration-300">{isDone ? 100 : task.progress}%</span>
                        </div>
                        <ProgressBar
                          value={isDone ? 100 : task.progress}
                          tone={isDone ? "emerald" : "blue"}
                          animate={!isDone && task.progress > 0 && task.progress < 100}
                        />
                      </div>
                    </button>
                  );
                })}
              </div>
            </section>
          );
        })
      )}

      {selected && (
        <DetailDrawer
          title={selected.title}
          subtitle={`${selected.course_name} / ${selected.type}`}
          open={!!selected}
          onClose={() => setSelected(null)}
        >
          <div className="space-y-5">
            {[
              ["任务描述", selected.description || "暂无描述"],
              ["任务类型", selected.type],
              ["优先级", selected.priority === "high" ? "紧急" : selected.priority === "medium" ? "中等" : "一般"],
              ["当前状态", selected.status],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
                <h3 className="text-sm font-black text-slate-900">{label}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{value}</p>
              </div>
            ))}
            {recommendedResources.length > 0 && (
              <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-black text-blue-900">
                  <FileText className="h-4 w-4" />
                  推荐资源
                </h3>
                <div className="space-y-2 text-sm font-semibold text-blue-800">
                  {recommendedResources.map((r) => (
                    <div key={r.title} className="flex items-center gap-2">
                      <r.icon className="h-4 w-4 cursor-pointer text-blue-600" />
                      <span>{r.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="grid grid-cols-3 gap-3">
              <Link to="/student/resources" className={`${primaryButton} cursor-pointer text-center`}>开始学习</Link>
              <button
                onClick={() => {
                  const id = String(selected.id);
                  setCompleted((items) => Array.from(new Set([...items, id])));
                  setMarkingId(id);
                  notify.success("任务已标记完成");
                  window.setTimeout(() => setMarkingId(null), 1400);
                }}
                className={`${secondaryButton} cursor-pointer transition-all duration-300 ${
                  markingId === String(selected.id)
                    ? "!bg-emerald-500 !text-white !ring-emerald-400"
                    : ""
                }`}
              >
                {markingId === String(selected.id) ? "已完成 ✓" : "标记完成"}
              </button>
              <Link to="/student/feedback" className={`${secondaryButton} flex cursor-pointer items-center justify-center gap-1`}>
                <MessageSquare className="h-4 w-4" />
                提交反馈
              </Link>
            </div>
          </div>
        </DetailDrawer>
      )}
    </div>
  );
}
