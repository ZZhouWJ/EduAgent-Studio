import React from "react";
import {
  AlertCircle,
  BarChart3,
  BookOpen,
  HelpCircle,
  MessageSquare,
  RefreshCw,
  UserRound,
} from "lucide-react";
import { feedbackApi, learningApi, profilesApi } from "@/lib/api";
import type { LearningFeedback } from "@/lib/api/feedbacks";
import { useApi } from "@/lib/useApi";
import {
  DetailDrawer,
  EmptyState,
  PageHeader,
  PageShell,
  StatCard,
  secondaryButton,
} from "../components/common/ProductUI";

const FEEDBACK_TYPES = [
  { value: "", label: "全部类型" },
  { value: "self_report", label: "自评反馈" },
  { value: "quiz_result", label: "测验结果" },
  { value: "study_note", label: "学习笔记" },
  { value: "question", label: "问题提问" },
] as const;

const FEEDBACK_TYPE_LABELS: Record<string, string> = Object.fromEntries(
  FEEDBACK_TYPES.filter((item) => item.value).map((item) => [item.value, item.label]),
);

type FeedbackTypeFilter = (typeof FEEDBACK_TYPES)[number]["value"];

const DIFFICULTY_LABELS: Record<string, string> = {
  too_easy: "偏简单",
  appropriate: "适中",
  too_hard: "偏困难",
};

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("zh-CN");
}

function formatMastery(value: number | null) {
  if (value == null) return "未填写";
  return `${Math.round(value * 100)}%`;
}

export function TeacherFeedback() {
  const coursesState = useApi(() => learningApi.listCourses(), []);
  const courses = coursesState.data ?? [];
  const [courseId, setCourseId] = React.useState(0);
  const [studentId, setStudentId] = React.useState(0);
  const [feedbackType, setFeedbackType] = React.useState<FeedbackTypeFilter>("");
  const [selected, setSelected] = React.useState<LearningFeedback | null>(null);

  React.useEffect(() => {
    if (!courseId && courses.length) setCourseId(courses[0].id);
  }, [courseId, courses]);

  React.useEffect(() => {
    setStudentId(0);
    setSelected(null);
  }, [courseId]);

  React.useEffect(() => {
    setSelected(null);
  }, [studentId, feedbackType]);

  const profilesState = useApi(
    () => courseId
      ? profilesApi.list({ course_id: courseId, page_size: 100 })
      : Promise.resolve({ items: [], total: 0 }),
    [courseId],
  );

  const feedbackState = useApi(
    () => courseId
      ? feedbackApi.list({
          course_id: courseId,
          student_id: studentId || undefined,
          feedback_type: feedbackType || undefined,
          page_size: 100,
        })
      : Promise.resolve({ items: [], total: 0 }),
    [courseId, studentId, feedbackType],
  );

  const profiles = profilesState.data?.items ?? [];
  const feedbacks = feedbackState.data?.items ?? [];
  const quizScores = feedbacks
    .map((item) => item.quiz_score)
    .filter((score): score is number => typeof score === "number");
  const averageQuizScore = quizScores.length
    ? Math.round((quizScores.reduce((sum, score) => sum + score, 0) / quizScores.length) * 100)
    : null;
  const questionCount = feedbacks.filter((item) => item.feedback_type === "question").length;
  const lowMasteryCount = feedbacks.filter(
    (item) => typeof item.self_mastery === "number" && item.self_mastery < 0.5,
  ).length;
  const loadError = coursesState.error || profilesState.error || feedbackState.error;

  const retryAll = () => {
    void coursesState.refetch();
    if (courseId) {
      void profilesState.refetch();
      void feedbackState.refetch();
    }
  };

  return (
    <PageShell>
      <PageHeader
        eyebrow="学习过程反馈"
        title="学生学习反馈"
        description="按课程和学生查看自评、测验、疑问与学习笔记，为画像调整和教学干预提供依据。"
        icon={MessageSquare}
      />

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        <StatCard label="反馈总数" value={String(feedbackState.data?.total ?? "—")} hint="当前筛选范围" icon={MessageSquare} tone="blue" />
        <StatCard label="学生提问" value={String(questionCount)} hint="需要教师关注" icon={HelpCircle} tone="orange" />
        <StatCard label="低掌握度反馈" value={String(lowMasteryCount)} hint="自评低于 50%" icon={AlertCircle} tone="red" />
        <StatCard label="测验平均分" value={averageQuizScore == null ? "—" : `${averageQuizScore}%`} hint={`${quizScores.length} 条测验记录`} icon={BarChart3} tone="emerald" />
      </section>

      <section className="edu-card flex flex-col gap-3 rounded-2xl p-4 sm:flex-row sm:flex-wrap sm:items-end">
        <label className="flex-1 text-xs font-bold text-slate-500 sm:min-w-[220px]">
          课程
          <select
            aria-label="筛选反馈课程"
            value={courseId || ""}
            onChange={(event) => setCourseId(Number(event.target.value))}
            className="edu-focus-ring mt-1.5 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-medium text-slate-700"
          >
            <option value="">请选择课程</option>
            {courses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}
          </select>
        </label>
        <label className="flex-1 text-xs font-bold text-slate-500 sm:min-w-[220px]">
          学生
          <select
            aria-label="筛选反馈学生"
            value={studentId || ""}
            onChange={(event) => setStudentId(Number(event.target.value))}
            className="edu-focus-ring mt-1.5 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-medium text-slate-700"
          >
            <option value="">全部学生</option>
            {profiles.map((profile) => (
              <option key={profile.student_id} value={profile.student_id}>
                {profile.student_name} · {profile.student_no || "无学号"}
              </option>
            ))}
          </select>
        </label>
        <label className="flex-1 text-xs font-bold text-slate-500 sm:min-w-[200px]">
          反馈类型
          <select
            aria-label="筛选反馈类型"
            value={feedbackType}
            onChange={(event) => setFeedbackType(event.target.value as FeedbackTypeFilter)}
            className="edu-focus-ring mt-1.5 h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-medium text-slate-700"
          >
            {FEEDBACK_TYPES.map((item) => <option key={item.value || "all"} value={item.value}>{item.label}</option>)}
          </select>
        </label>
      </section>

      {loadError ? (
        <section role="alert" className="flex flex-col gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 sm:flex-row sm:items-center sm:justify-between">
          <span>反馈加载失败：{loadError.message}</span>
          <button onClick={retryAll} className={secondaryButton}>
            <RefreshCw className="h-4 w-4" />重试
          </button>
        </section>
      ) : feedbackState.loading || profilesState.loading || coursesState.loading ? (
        <div className="edu-card flex min-h-48 items-center justify-center rounded-2xl text-sm text-slate-400">
          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />加载反馈数据
        </div>
      ) : feedbacks.length === 0 ? (
        <EmptyState title="暂无学习反馈" description="当前课程和筛选条件下没有学生反馈记录。" />
      ) : (
        <section className="edu-card overflow-hidden rounded-2xl">
          <div className="border-b border-slate-100 px-4 py-3 text-xs font-bold text-slate-500">
            共 {feedbackState.data?.total ?? feedbacks.length} 条记录，按提交时间倒序
          </div>
          <div className="divide-y divide-slate-100">
            {feedbacks.map((item) => (
              <button
                key={item.feedback_id}
                onClick={() => setSelected(item)}
                className="grid w-full grid-cols-1 gap-3 px-4 py-4 text-left transition hover:bg-blue-50/40 sm:grid-cols-[minmax(150px,0.8fr)_minmax(160px,1fr)_minmax(220px,1.8fr)_auto] sm:items-center"
              >
                <span className="min-w-0">
                  <span className="block truncate text-sm font-black text-slate-900">{item.student_name || "未知学生"}</span>
                  <span className="mt-1 block text-xs text-slate-400">{formatDate(item.created_at)}</span>
                </span>
                <span className="min-w-0">
                  <span className="inline-flex rounded-full bg-blue-50 px-2.5 py-1 text-xs font-bold text-blue-700">
                    {FEEDBACK_TYPE_LABELS[item.feedback_type] ?? item.feedback_type}
                  </span>
                  <span className="mt-1 block truncate text-xs text-slate-500">{item.resource_title || "自主学习反馈"}</span>
                </span>
                <span className="line-clamp-2 text-sm leading-6 text-slate-600">
                  {item.content?.trim() || "未填写文字反馈"}
                </span>
                <span className="flex flex-wrap gap-2 text-xs font-bold text-slate-600 sm:justify-end">
                  {item.self_mastery != null && <span>掌握度 {formatMastery(item.self_mastery)}</span>}
                  {item.quiz_score != null && <span>测验 {Math.round(item.quiz_score * 100)}%</span>}
                </span>
              </button>
            ))}
          </div>
        </section>
      )}

      <DetailDrawer
        title={selected ? `${selected.student_name}的学习反馈` : "学习反馈"}
        subtitle={selected ? `${selected.course_name} · ${formatDate(selected.created_at)}` : undefined}
        open={selected != null}
        onClose={() => setSelected(null)}
      >
        {selected && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <UserRound className="h-4 w-4 text-blue-600" />
                <div className="mt-3 text-xs font-bold text-slate-400">自评掌握度</div>
                <div className="mt-1 text-sm font-black text-slate-900">{formatMastery(selected.self_mastery)}</div>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <BarChart3 className="h-4 w-4 text-emerald-600" />
                <div className="mt-3 text-xs font-bold text-slate-400">测验成绩</div>
                <div className="mt-1 text-sm font-black text-slate-900">
                  {selected.quiz_score == null ? "未关联测验" : `${Math.round(selected.quiz_score * 100)}%`}
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 text-sm font-black text-slate-900">
                <MessageSquare className="h-4 w-4 text-blue-600" />反馈内容
              </div>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">
                {selected.content?.trim() || "学生未填写文字反馈。"}
              </p>
            </div>
            <dl className="space-y-3 rounded-xl border border-slate-200 p-4 text-sm">
              <div className="flex justify-between gap-4"><dt className="text-slate-400">反馈类型</dt><dd className="font-bold text-slate-800">{FEEDBACK_TYPE_LABELS[selected.feedback_type] ?? selected.feedback_type}</dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-400">关联资源</dt><dd className="text-right font-bold text-slate-800">{selected.resource_title || "未关联"}</dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-400">难度评价</dt><dd className="font-bold text-slate-800">{selected.difficulty_rating ? DIFFICULTY_LABELS[selected.difficulty_rating] ?? selected.difficulty_rating : "未评价"}</dd></div>
            </dl>
            <div className="flex items-start gap-3 rounded-xl bg-blue-50 p-4 text-sm leading-6 text-blue-800">
              <BookOpen className="mt-1 h-4 w-4 shrink-0" />
              该记录已进入学生画像与教学分析链路，可结合学生画像页查看知识点掌握度变化。
            </div>
          </div>
        )}
      </DetailDrawer>
    </PageShell>
  );
}
