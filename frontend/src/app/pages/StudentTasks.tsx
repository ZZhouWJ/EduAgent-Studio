import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { BookOpenCheck, CheckCircle2, Clock3, FileText, MessageSquare, PlayCircle, Target } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, resourcesApi } from "@/lib/api";
import { resourceTypeLabel, taskTypeLabel } from "@/lib/educationLabels";
import { DetailDrawer, EmptyState, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";
import { PageHero } from "../components/common/PageHero";

const STATUS_LABELS: Record<string, string> = {
  assigned: "未开始",
  in_progress: "进行中",
  completed: "已完成",
  not_started: "未开始",
  draft: "草稿",
  archived: "已归档",
};

const STATUS_OPTIONS = ["全部", "进行中", "未开始", "已完成"];

function resourceIcon(type: string) {
  const t = (type ?? "").toLowerCase();
  if (["lecture", "mindmap", "ppt", "review"].includes(t) || t.includes("讲义") || t.includes("文档")) return FileText;
  if (["quiz", "test", "error_analysis", "learning_card"].includes(t) || t.includes("练习") || t.includes("题")) return CheckCircle2;
  if (["code_case", "case", "experiment_report"].includes(t) || t.includes("代码") || t.includes("案例")) return BookOpenCheck;
  if (t === "video_script" || t.includes("视频") || t.includes("动画")) return PlayCircle;
  return FileText;
}

export function StudentTasks() {
  const navigate = useNavigate();
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selected, setSelected] = React.useState<{
    id: number; title: string; course_name: string; type: string;
    status: string; rawStatus: string; priority: string; description: string;
    course_id: number; canUpdate: boolean;
  } | null>(null);
  const [updatingTaskId, setUpdatingTaskId] = React.useState<number | null>(null);

  const { data: tasksData, loading, refetch } = useApi(
    () => learningApi.listTasks({ page_size: 100 }),
    []
  );
  const { data: resourcesData } = useApi(
    () => selected?.course_id
      ? resourcesApi.list({ course_id: selected.course_id, page_size: 10 })
      : Promise.resolve({ items: [], total: 0 }),
    [selected?.course_id]
  );

  const allTasks = React.useMemo(() => {
    return (tasksData?.items ?? []).map((task) => ({
      ...task,
      id: task.id,
      course: task.course_name,
      knowledge: taskTypeLabel(task.type),
      displayStatus: STATUS_LABELS[task.status] ?? task.status,
      progress: task.status === "completed" ? 100 : task.status === "in_progress" ? 50 : 0,
      section:
        task.status === "completed" ? "已完成任务" :
        task.status === "in_progress" ? "今日任务" :
        "本周任务",
    }));
  }, [tasksData]);

  const normalized = query.trim().toLowerCase();
  const tasks = allTasks
    .filter((task) => (status === "全部" ? true : task.displayStatus === status))
    .filter((task) => !normalized || `${task.title}${task.knowledge}`.toLowerCase().includes(normalized));

  const taskSections = ["今日任务", "本周任务", "已完成任务"];

  const stats = [
    { label: "待完成任务", value: String(allTasks.filter((t) => ["assigned", "not_started"].includes(t.status)).length), hint: "本周任务", icon: Target, tone: "orange" as const },
    { label: "进行中任务", value: String(allTasks.filter((t) => t.status === "in_progress").length), hint: "今日任务", icon: PlayCircle, tone: "blue" as const },
    { label: "已完成任务", value: String(allTasks.filter((t) => t.status === "completed").length), hint: "本周持续更新", icon: CheckCircle2, tone: "emerald" as const },
    { label: "今日建议时长", value: `${Math.max(30, allTasks.filter((t) => t.status === "in_progress").length * 15)} 分钟`, hint: "轻量化拆分", icon: Clock3, tone: "purple" as const },
  ];

  const recommendedResources = (resourcesData?.items ?? []).slice(0, 3).map((r) => ({
    id: r.resource_id,
    title: r.resource_title,
    type: resourceTypeLabel(r.resource_type),
    icon: resourceIcon(r.resource_type),
  }));

  const updateTaskStatus = async (taskId: number, nextStatus: "in_progress" | "completed") => {
    setUpdatingTaskId(taskId);
    try {
      const updated = await learningApi.updateTaskStatus(taskId, nextStatus);
      setSelected((current) => current?.id === taskId
        ? {
            ...current,
            rawStatus: updated.status,
            status: STATUS_LABELS[updated.status] ?? updated.status,
          }
        : current
      );
      await refetch();
      notify.success(nextStatus === "completed" ? "任务已完成" : "任务已开始");
      return true;
    } catch (error) {
      notify.error(error instanceof Error ? error.message : "任务状态更新失败");
      return false;
    } finally {
      setUpdatingTaskId(null);
    }
  };

  const startLearning = async () => {
    if (!selected) return;
    if (selected.canUpdate && selected.rawStatus === "assigned") {
      const updated = await updateTaskStatus(selected.id, "in_progress");
      if (!updated) return;
    }
    const firstResourceId = recommendedResources[0]?.id;
    navigate(firstResourceId ? `/student/resources?resource=${firstResourceId}` : "/student/resources");
  };

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHero
        eyebrow="学习任务"
        title="个性化学习任务"
        description="根据你的学习画像和课程进度，系统为你安排了个性化学习任务。"
        icon={BookOpenCheck}
        role="student"
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
                  const isDone = task.status === "completed";
                  return (
                    <button
                      key={task.id}
                      onClick={() => setSelected({
                        id: task.id,
                        title: task.title,
                        course_name: task.course_name,
                        type: taskTypeLabel(task.type),
                        status: task.displayStatus,
                        rawStatus: task.status,
                        priority: task.priority,
                        description: task.description,
                        course_id: task.course_id,
                        canUpdate: task.assignee_id !== null,
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
                    <Link
                      key={r.id}
                      to={`/student/resources?resource=${r.id}`}
                      className="flex min-h-10 items-center gap-2 rounded-lg px-2 transition hover:bg-blue-100"
                    >
                      <r.icon className="h-4 w-4 cursor-pointer text-blue-600" />
                      <span className="line-clamp-2">{r.title}</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <button
                type="button"
                onClick={startLearning}
                disabled={updatingTaskId === selected.id}
                className={`${primaryButton} cursor-pointer text-center disabled:cursor-wait disabled:opacity-60`}
              >
                {updatingTaskId === selected.id && selected.rawStatus === "assigned" ? "正在开始..." : "开始学习"}
              </button>
              <button
                type="button"
                onClick={() => updateTaskStatus(selected.id, "completed")}
                disabled={!selected.canUpdate || selected.rawStatus === "completed" || updatingTaskId === selected.id}
                className={`${secondaryButton} cursor-pointer transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-60`}
              >
                {selected.rawStatus === "completed"
                  ? "已完成"
                  : !selected.canUpdate
                    ? "仅供查看"
                    : updatingTaskId === selected.id
                      ? "正在更新..."
                      : "标记完成"}
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
