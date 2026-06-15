import React from "react";
import { BookOpen, Database, FileText, GraduationCap, Library, UserRound, Users } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, Course } from "@/lib/api";
import { DetailDrawer, PageHeader, PageShell, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "@/components/common/ProductUI";

function mapCourse(c: Course) {
  const statusMap: Record<string, string> = { active: "活跃", inactive: "停用", archived: "归档" };
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
    summary: c.description || "暂无课程描述",
    chapters: c.tags?.length ? c.tags : ["课程内容待完善"],
    raw: c,
  };
}

export function AdminCourses() {
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapCourse> | null>(null);
  const { toast, showToast } = useInlineToast();

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
    { label: "课程负责人", value: "-", hint: "待接入用户", icon: UserRound, tone: "purple" as const },
    { label: "课程知识点", value: `${courses.reduce((sum, c) => sum + c.knowledgePoints, 0) || "-"}`, hint: "结构化节点", icon: Database, tone: "cyan" as const },
    { label: "资源总量", value: "-", hint: "待接入资源", icon: Library, tone: "orange" as const },
    { label: "低活跃课程", value: "-", hint: "需运营介入", icon: FileText, tone: "red" as const },
  ];

  return (
    <PageShell>
      <PageHeader eyebrow="Admin Courses" title="课程管理" description="查看和维护平台内高校课程、知识库和资源建设状态。" icon={BookOpen} action={<button onClick={() => showToast("课程建设巡检已完成")} className={primaryButton}>运行建设巡检</button>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索课程、代码或负责人" value={query} onChange={setQuery} />
          <SegmentedControl value={statusFilter} options={["全部", "活跃", "停用"]} onChange={setStatusFilter} />
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
                  <tr key={course.id} className="bg-white hover:bg-blue-50/40">
                    <td className="max-w-[260px] px-4 py-4 font-black text-slate-900">{course.name}</td>
                    <td className="px-4 py-4 font-mono text-xs font-bold text-slate-500">{course.code}</td>
                    <td className="px-4 py-4">{course.owner}</td>
                    <td className="px-4 py-4">{course.students}</td>
                    <td className="px-4 py-4">{course.knowledgePoints}</td>
                    <td className="px-4 py-4">{course.resources}</td>
                    <td className="px-4 py-4 font-black text-blue-700">{course.mastery}%</td>
                    <td className="px-4 py-4"><StatusBadge status={course.status} /></td>
                    <td className="px-4 py-4"><button onClick={() => setSelected(course)} className="text-xs font-black text-blue-700">查看详情</button></td>
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
              <button key={course.id} onClick={() => setSelected(course)} className="edu-card block w-full rounded-2xl p-5 text-left transition hover:border-blue-200">
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
      {selected && <DetailDrawer title={selected.name} subtitle={`${selected.owner} / ${selected.department}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-5">
          <p className="text-sm leading-6 text-slate-600">{selected.summary}</p>
          <div className="grid grid-cols-2 gap-3">{selected.chapters.map((item) => <div key={item} className="rounded-xl bg-slate-50 p-3 text-sm font-bold text-slate-700">{item}</div>)}</div>
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => showToast("负责人分配已保存（TODO - 后端无课程管理接口）")} className={primaryButton}><Users className="h-4 w-4" />分配负责人</button>
            <button onClick={() => showToast("已打开课程资源视图")} className={secondaryButton}>查看课程资源</button>
            <button onClick={() => showToast("已打开课程知识库视图")} className={secondaryButton}>查看课程知识库</button>
            <button onClick={() => showToast("课程状态已更新（TODO）")} className={secondaryButton}>更新状态</button>
          </div>
        </div>
      </DetailDrawer>}
      {toast}
    </PageShell>
  );
}
