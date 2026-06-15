import React from "react";
import { useNavigate } from "react-router";
import { BookOpen, Database, FileText, GraduationCap, Library, UserRound, Users } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { coursesApi, learningApi, Course } from "@/lib/api";
import { notify } from "@/lib/toast";
import { DetailDrawer, PageHeader, PageShell, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton } from "../components/common/ProductUI";

function mapCourse(c: Course) {
  const statusMap: Record<string, string> = { active: "活跃", inactive: "停用", archived: "归档", draft: "草稿" };
  return {
    id: String(c.id),
    name: c.name,
    code: c.code || "-",
    owner: c.teacher || "-",
    department: c.semester || "-",
    students: c.student_count ?? 0,
    knowledgePoints: c.knowledge_point_count ?? 0,
    resources: "-",
    mastery: 0,
    status: statusMap[c.status] ?? c.status,
    rawStatus: c.status,
    summary: c.description || "暂无课程描述",
    chapters: c.tags?.length ? c.tags : ["课程内容待完善"],
    raw: c,
  };
}

function StatusUpdateModal({ courseId, currentStatus, onClose, onSuccess }: {
  courseId: string;
  currentStatus: string;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [status, setStatus] = React.useState(currentStatus);
  const [saving, setSaving] = React.useState(false);
  const options = [
    { value: "active", label: "活跃" },
    { value: "draft", label: "草稿" },
    { value: "archived", label: "归档" },
  ];

  const handleSave = async () => {
    if (status === currentStatus) { onClose(); return; }
    setSaving(true);
    try {
      await coursesApi.updateCourse(Number(courseId), { status });
      notify.success("课程状态已更新");
      onSuccess();
      onClose();
    } catch (e) {
      notify.error("更新失败：" + String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
        <h3 className="mb-4 text-lg font-black text-slate-950">更新课程状态</h3>
        <div className="mb-5 space-y-2">
          {options.map((o) => (
            <label key={o.value} className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 p-3 transition hover:border-blue-200 has-[:checked]:border-blue-400 has-[:checked]:bg-blue-50">
              <input type="radio" name="course-status" value={o.value} checked={status === o.value} onChange={() => setStatus(o.value)} className="h-4 w-4 accent-blue-600" />
              <span className="text-sm font-bold text-slate-700">{o.label}</span>
            </label>
          ))}
        </div>
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 cursor-pointer rounded-xl border border-slate-200 py-2.5 text-sm font-bold text-slate-600 transition hover:bg-slate-50">取消</button>
          <button onClick={handleSave} disabled={saving} className="flex min-h-11 flex-1 cursor-pointer items-center justify-center rounded-xl bg-blue-600 py-2.5 text-sm font-black text-white transition hover:bg-blue-700 disabled:opacity-60">
            {saving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>
    </div>
  );
}

export function AdminCourses() {
  const navigate = useNavigate();
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapCourse> | null>(null);
  const [showStatusModal, setShowStatusModal] = React.useState(false);
  const [pendingId, setPendingId] = React.useState<string | null>(null);

  const coursesState = useApi(() => learningApi.listCourses(), []);

  const courses = (coursesState.data ?? []).map(mapCourse);
  const filtered = courses.filter((course) => {
    const statusMatch = statusFilter === "全部" || course.status === statusFilter;
    const keywordMatch = `${course.name}${course.code}${course.owner}`.toLowerCase().includes(query.toLowerCase());
    return statusMatch && keywordMatch;
  });

  const stats = [
    { label: "课程总数", value: `${courses.length || "-"}`, hint: "平台课程", icon: BookOpen, tone: "blue" as const },
    { label: "活跃课程", value: `${courses.filter((c) => c.status === "活跃").length || "-"}`, hint: "最近 7 日有学习行为", icon: GraduationCap, tone: "emerald" as const },
    { label: "课程负责人", value: String(courses.filter((c) => c.owner && c.owner !== "-").length) || "-", hint: "已分配教师", icon: UserRound, tone: "purple" as const },
    { label: "课程知识点", value: `${courses.reduce((sum, c) => sum + c.knowledgePoints, 0) || "-"}`, hint: "结构化节点", icon: Database, tone: "cyan" as const },
    { label: "资源总量", value: "-", hint: "待接入资源", icon: Library, tone: "orange" as const },
    { label: "归档课程", value: `${courses.filter((c) => c.status === "归档").length || "-"}`, hint: "历史课程", icon: FileText, tone: "red" as const },
  ];

  const handleHealthCheck = async () => {
    try {
      const r1 = await fetch("/api/health");
      const j1 = await r1.json();
      const apiOk = j1.code === 0;
      try {
        const r2 = await fetch("/api/health/db");
        const j2 = await r2.json();
        const dbOk = j2.code === 0;
        if (apiOk && dbOk) {
          notify.success(`巡检完成：后端正常，数据库正常 (v${j2.data?.server_version ?? "?"})`);
        } else {
          notify.warning(`巡检完成：后端${apiOk ? "正常" : "异常"}，数据库${dbOk ? "正常" : "异常"}`);
        }
      } catch {
        notify.warning("巡检完成：后端正常，数据库连接失败");
      }
    } catch {
      notify.error("巡检失败：后端服务不可达");
    }
  };

  const handleUpdateStatus = (courseId: string, status: string) => {
    setPendingId(courseId);
    setSelected((prev) => prev ? { ...prev, rawStatus: status } : null);
    setShowStatusModal(true);
  };

  return (
    <PageShell>
      <PageHeader eyebrow="Admin Courses" title="课程管理" description="查看和维护平台内高校课程、知识库和资源建设状态。" icon={BookOpen} action={
        <button onClick={handleHealthCheck} className={`${primaryButton} cursor-pointer`}>
          运行建设巡检
        </button>
      } />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索课程、代码或负责人" value={query} onChange={setQuery} />
          <SegmentedControl value={statusFilter} options={["全部", "活跃", "停用", "归档", "草稿"]} onChange={setStatusFilter} />
        </div>
      </section>
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_0.82fr] lg:gap-6">
        <div className="edu-card hidden overflow-hidden rounded-2xl lg:block">
          {coursesState.loading ? (
            <div className="flex items-center justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : filtered.length === 0 ? (
            <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无课程数据</div>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-black text-slate-500">
                <tr>{["课程名称", "代码", "负责人", "学生", "知识点", "资源", "掌握度", "状态", "操作"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((course) => (
                  <tr key={course.id} className="cursor-pointer bg-white hover:bg-blue-50/40">
                    <td className="max-w-[260px] px-4 py-4 font-black text-slate-900">{course.name}</td>
                    <td className="px-4 py-4 font-mono text-xs font-bold text-slate-500">{course.code}</td>
                    <td className="px-4 py-4">{course.owner}</td>
                    <td className="px-4 py-4">{course.students}</td>
                    <td className="px-4 py-4">{course.knowledgePoints}</td>
                    <td className="px-4 py-4">{course.resources}</td>
                    <td className="px-4 py-4 font-black text-blue-700">{course.mastery}%</td>
                    <td className="px-4 py-4"><StatusBadge status={course.status} /></td>
                    <td className="px-4 py-4">
                      <button onClick={() => setSelected(course)} className="cursor-pointer text-xs font-black text-blue-700 hover:text-blue-800">查看详情</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <div className="space-y-4">
          {coursesState.loading ? (
            <div className="flex items-center justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : filtered.length === 0 ? (
            <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无课程数据</div>
          ) : (
            filtered.map((course) => (
              <button key={course.id} onClick={() => setSelected(course)} className="edu-card block w-full cursor-pointer rounded-2xl p-5 text-left transition hover:border-blue-200">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-base font-black text-slate-950">{course.name}</h3>
                    <p className="mt-1 text-xs text-slate-500">{course.department} / {course.owner}</p>
                  </div>
                  <StatusBadge status={course.status} />
                </div>
                <div className="mt-4"><ProgressBar value={course.mastery} tone={course.mastery >= 74 ? "emerald" : "orange"} /></div>
              </button>
            ))
          )}
        </div>
      </section>

      {selected && (
        <DetailDrawer title={selected.name} subtitle={`${selected.owner} / ${selected.department}`} open={!!selected} onClose={() => setSelected(null)}>
          <div className="space-y-5">
            <p className="text-sm leading-6 text-slate-600">{selected.summary}</p>
            <div className="grid grid-cols-2 gap-3">{selected.chapters.map((item) => <div key={item} className="rounded-xl bg-slate-50 p-3 text-sm font-bold text-slate-700">{item}</div>)}</div>
            <div className="grid grid-cols-2 gap-3">
              <button onClick={() => navigate("/admin/users")} className={`${primaryButton} cursor-pointer`}><Users className="h-4 w-4" />分配负责人</button>
              <button onClick={() => navigate(`/student/resources?course=${selected.id}`)} className={`${secondaryButton} cursor-pointer`}>查看课程资源</button>
              <button onClick={() => navigate(`/teacher/knowledge-base?course=${selected.id}`)} className={`${secondaryButton} cursor-pointer`}>查看课程知识库</button>
              <button onClick={() => handleUpdateStatus(selected.id, selected.rawStatus)} className={`${secondaryButton} cursor-pointer`}>更新状态</button>
            </div>
          </div>
        </DetailDrawer>
      )}

      {showStatusModal && pendingId && (
        <StatusUpdateModal
          courseId={pendingId}
          currentStatus={selected?.rawStatus ?? "active"}
          onClose={() => { setShowStatusModal(false); setPendingId(null); }}
          onSuccess={() => coursesState.refetch()}
        />
      )}
    </PageShell>
  );
}
