import React from "react";
import { BookOpen, Database, FileText, GraduationCap, Library, UserRound, Users } from "lucide-react";
import { courses } from "../data/demoData";
import { DetailDrawer, PageHeader, PageShell, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function AdminCourses() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selected, setSelected] = React.useState<(typeof courses)[number] | null>(null);
  const { toast, showToast } = useInlineToast();

  const filtered = courses.filter((course) => (status === "全部" || course.status === status) && `${course.name}${course.code}${course.owner}`.toLowerCase().includes(query.toLowerCase()));
  const stats = [
    { label: "课程总数", value: "42", hint: "平台课程", icon: BookOpen, tone: "blue" as const },
    { label: "活跃课程", value: "36", hint: "最近 7 日有学习行为", icon: GraduationCap, tone: "emerald" as const },
    { label: "课程负责人", value: "86", hint: "教师账号", icon: UserRound, tone: "purple" as const },
    { label: "课程知识点", value: "628", hint: "结构化节点", icon: Database, tone: "cyan" as const },
    { label: "资源总量", value: "8,642", hint: "AI 生成 72%", icon: Library, tone: "orange" as const },
    { label: "低活跃课程", value: "4", hint: "需运营介入", icon: FileText, tone: "red" as const },
  ];

  return (
    <PageShell>
      <PageHeader eyebrow="Admin Courses" title="课程管理" description="查看和维护平台内高校课程、知识库和资源建设状态。" icon={BookOpen} action={<button onClick={() => showToast("课程建设巡检已完成")} className={primaryButton}>运行建设巡检</button>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索课程、代码或负责人" value={query} onChange={setQuery} />
          <SegmentedControl value={status} options={["全部", "活跃", "观察"]} onChange={setStatus} />
        </div>
      </section>
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_0.82fr] lg:gap-6">
        <div className="edu-card hidden overflow-hidden rounded-2xl lg:block">
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
        </div>
        <div className="space-y-4">
          {filtered.map((course) => (
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
          ))}
        </div>
      </section>
      {selected && <DetailDrawer title={selected.name} subtitle={`${selected.owner} / ${selected.department}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-5">
          <p className="text-sm leading-6 text-slate-600">{selected.summary}</p>
          <div className="grid grid-cols-2 gap-3">{selected.chapters.map((item) => <div key={item} className="rounded-xl bg-slate-50 p-3 text-sm font-bold text-slate-700">{item}</div>)}</div>
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => showToast("负责人分配已保存")} className={primaryButton}><Users className="h-4 w-4" />分配负责人</button>
            <button onClick={() => showToast("已打开课程资源视图")} className={secondaryButton}>查看课程资源</button>
            <button onClick={() => showToast("已打开课程知识库视图")} className={secondaryButton}>查看课程知识库</button>
            <button onClick={() => showToast("课程状态已更新")} className={secondaryButton}>更新状态</button>
          </div>
        </div>
      </DetailDrawer>}
      {toast}
    </PageShell>
  );
}
