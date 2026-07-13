import React from "react";
import { Link } from "react-router-dom";
import { BarChart3, BookOpen, Bot, Database, FileText, GraduationCap, Library, Users } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi, statisticsApi } from "@/lib/api";
import { DetailDrawer, PageHeader, ProgressBar, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

interface Course {
  id: number
  name: string
  code: string
  description: string
  teacher: string
  semester: string
  status: string
  knowledge_point_count: number
  student_count: number
  task_count: number
  cover_color: string
  tags: string[]
}

export function TeacherCourses() {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState("全部");
  const [selected, setSelected] = React.useState<Course | null>(null);
  const { toast, showToast } = useInlineToast();

  const { data: courseList, loading, refetch: reloadCourses } = useApi(() => learningApi.listCourses(), []);
  const { data: overview, refetch: reloadOverview } = useApi(() => statisticsApi.learningOverview(), []);

  // 后端返回 snake_case，映射到 UI 期望的字段
  const mappedCourses: Array<{
    id: string | number; name: string; code: string; owner: string; department: string; summary: string; students: number; knowledgePoints: number; resources: number; mastery: number; status: string; updatedAt: string; classes: string[]; chapters: string[]; weakPoints: string[]
  }> = (courseList ?? []).map((c) => ({
    id: c.id,
    name: c.name,
    code: c.code,
    owner: c.teacher,
    department: "—",
    summary: c.description,
    students: c.student_count,
    knowledgePoints: c.knowledge_point_count,
    resources: c.task_count,
    mastery: overview ? Math.round((overview.avg_mastery ?? 0) * 100) : 0,
    status: c.status,
    updatedAt: "—",
    classes: [],
    chapters: [],
    weakPoints: [],
  }));

  const list = mappedCourses.filter((course) => (status === "全部" || course.status === status) && `${course.name}${course.code}`.toLowerCase().includes(query.toLowerCase()));

  const stats = [
    { label: "管理课程数", value: overview ? `${overview.course_count}` : "—", hint: "本学期", icon: BookOpen, tone: "blue" as const },
    { label: "学生总数", value: overview ? `${overview.student_count}` : "—", hint: `${overview?.course_count ?? "—"} 个班级`, icon: Users, tone: "slate" as const },
    { label: "反馈数", value: overview ? `${overview.feedback_count}` : "—", hint: "近 7 天", icon: Database, tone: "emerald" as const },
    { label: "学习资源", value: overview ? `${overview.resource_count}` : "—", hint: `审核通过率 ${overview ? Math.round((overview.review_pass_rate ?? 0) * 100) : "—"}%`, icon: Library, tone: "cyan" as const },
    { label: "平均掌握度", value: overview ? `${Math.round((overview.avg_mastery ?? 0) * 100)}%` : "—", hint: "全班统计", icon: BarChart3, tone: "orange" as const },
    { label: "活跃任务", value: overview ? `${overview.active_tasks}` : "—", hint: "进行中", icon: FileText, tone: "red" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        eyebrow=""
        title="我的课程"
        description="管理课程知识体系、学生学习进度和个性化资源生成策略。"
        icon={GraduationCap}
        action={<button onClick={() => { reloadCourses(); reloadOverview(); showToast("课程数据已刷新"); }} className={primaryButton}>同步课程数据</button>}
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
              <Link to="/teacher/review" className={primaryButton}>去审核</Link>
              <Link to="/teacher/analytics" className={secondaryButton}>查看分析</Link>
            </div>
          </article>
        ))}
      </section>

      {selected && <DetailDrawer title={selected.name} subtitle={`${selected.code} / ${selected.owner}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-5">
          <p className="text-sm leading-6 text-slate-600">{selected.summary}</p>
          {/* TODO: 后端暂无章节(chapters)、薄弱点(weakPoints)字段，暂时留空 */}
        </div>
      </DetailDrawer>}
      {toast}
    </div>
  );
}
