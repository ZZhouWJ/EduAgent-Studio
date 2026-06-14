import React from "react";
import { Link } from "react-router";
import { BarChart3, BookOpen, Bot, Database, FileText, GraduationCap, Library, Users } from "lucide-react";
import { courses } from "../data/demoData";
import { DetailDrawer, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function TeacherCourses() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selected, setSelected] = React.useState<(typeof courses)[number] | null>(null);
  const { toast, showToast } = useInlineToast();

  const list = courses.filter((course) => (status === "全部" || course.status === status) && `${course.name}${course.code}`.toLowerCase().includes(query.toLowerCase()));

  const stats = [
    { label: "管理课程数", value: "3", hint: "本学期", icon: BookOpen, tone: "blue" as const },
    { label: "学生总数", value: "308", hint: "4 个班级", icon: Users, tone: "purple" as const },
    { label: "知识点数量", value: "56", hint: "已结构化", icon: Database, tone: "emerald" as const },
    { label: "已生成资源", value: "1,246", hint: "AI 生成 72%", icon: Library, tone: "cyan" as const },
    { label: "平均掌握度", value: "72%", hint: "较上周 +2%", icon: BarChart3, tone: "orange" as const },
    { label: "待审核资源", value: "12", hint: "3 个高优先级", icon: FileText, tone: "red" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow="Teacher Courses"
        title="我的课程"
        description="管理课程知识体系、学生学习进度和个性化资源生成策略。"
        icon={GraduationCap}
        action={<button onClick={() => showToast("已同步课程建设状态")} className={primaryButton}>同步课程数据</button>}
      />

      <section className="grid grid-cols-6 gap-4">
        {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
      </section>

      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索课程名称或代码" value={query} onChange={setQuery} />
          <SegmentedControl value={status} options={["全部", "活跃", "观察"]} onChange={setStatus} />
        </div>
      </section>

      <section className="grid grid-cols-3 gap-5">
        {list.map((course) => (
          <article key={course.id} className="edu-card edu-card-hover rounded-2xl p-5">
            <div className="mb-4 flex items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-black leading-6 text-slate-950">{course.name}</h2>
                <p className="mt-1 text-xs font-bold text-slate-400">{course.code} / {course.department}</p>
              </div>
              <StatusBadge status={course.status} />
            </div>
            <p className="min-h-[66px] text-sm leading-6 text-slate-600">{course.summary}</p>
            <div className="mt-4 grid grid-cols-3 gap-3">
              {[
                ["学生", course.students],
                ["知识点", course.knowledgePoints],
                ["资源", course.resources],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl bg-slate-50 p-3">
                  <div className="text-xs font-bold text-slate-400">{label}</div>
                  <div className="mt-1 text-lg font-black text-slate-900">{value}</div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <div className="mb-2 flex justify-between text-xs font-bold text-slate-500">
                <span>平均掌握度</span>
                <span>{course.mastery}%</span>
              </div>
              <ProgressBar value={course.mastery} tone={course.mastery >= 74 ? "emerald" : "orange"} />
            </div>
            <div className="mt-5 grid grid-cols-2 gap-2">
              <button onClick={() => setSelected(course)} className={secondaryButton}>查看详情</button>
              <Link to="/teacher/knowledge-base" className={secondaryButton}>进入知识库</Link>
              <Link to="/teacher/agent-workbench" className={primaryButton}>生成资源</Link>
              <Link to="/teacher/analytics" className={secondaryButton}>查看分析</Link>
            </div>
          </article>
        ))}
      </section>

      {selected && <DetailDrawer title={selected.name} subtitle={`${selected.code} / ${selected.owner}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-5">
          <p className="text-sm leading-6 text-slate-600">{selected.summary}</p>
          <div className="grid grid-cols-2 gap-3">
            {selected.chapters.map((item) => <div key={item} className="rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm font-bold text-slate-700">{item}</div>)}
          </div>
          <div>
            <h3 className="mb-3 text-sm font-black text-slate-950">薄弱点 Top 5</h3>
            <div className="space-y-2">
              {selected.weakPoints.map((item, index) => (
                <div key={item} className="flex items-center justify-between rounded-xl bg-white p-3 ring-1 ring-slate-100">
                  <span className="text-sm font-bold text-slate-700">{index + 1}. {item}</span>
                  <span className="text-xs font-black text-orange-700">{38 + index * 6}%</span>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <Link to="/teacher/knowledge-base" className={primaryButton}>知识库</Link>
            <Link to="/teacher/tasks" className={secondaryButton}>发布任务</Link>
            <Link to="/teacher/agent-workbench" className={secondaryButton}>生成资源</Link>
          </div>
        </div>
      </DetailDrawer>}
      {toast}
    </div>
  );
}
