import React from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  BookOpen,
  BookOpenCheck,
  Brain,
  CheckCircle2,
  ChevronRight,
  FileText,
  HelpCircle,
  ListTree,
  LoaderCircle,
  MessageSquare,
  PlayCircle,
  RefreshCw,
  Send,
  Target,
} from "lucide-react";
import { feedbackApi, profilesApi, resourcesApi } from "@/lib/api";
import type { MasteryChange, RecommendedResource } from "@/lib/api/learning";
import { useApi } from "@/lib/useApi";
import { notify } from "@/lib/toast";
import { PageHero } from "../components/common/PageHero";

type MasteryLevel = "high" | "medium" | "low";
type DifficultyRating = "too_easy" | "appropriate" | "too_hard";

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  quiz_result: "测验结果",
  self_report: "学习自评",
  study_note: "学习笔记",
  question: "问题提问",
};

const RESOURCE_TYPE_LABELS: Record<string, string> = {
  lecture: "课程讲义",
  mindmap: "思维导图",
  quiz: "练习题",
  case: "案例材料",
  code_case: "代码实操",
  ppt: "PPT 大纲",
  video_script: "视频脚本",
  experiment_report: "实验报告",
  error_analysis: "错题解析",
  learning_card: "学习卡片",
  review: "复习计划",
  test: "阶段测验",
  other: "其他",
};

const DIFFICULTY_OPTIONS: Array<{ value: DifficultyRating; label: string }> = [
  { value: "too_easy", label: "偏简单" },
  { value: "appropriate", label: "适中" },
  { value: "too_hard", label: "偏困难" },
];

const MASTERY_OPTIONS: Array<{ value: MasteryLevel; label: string; score: number }> = [
  { value: "high", label: "较高", score: 0.85 },
  { value: "medium", label: "一般", score: 0.6 },
  { value: "low", label: "较低", score: 0.3 },
];

function resourceIcon(type: string) {
  const normalized = (type ?? "").toLowerCase();
  if (["quiz", "test", "error_analysis", "learning_card"].includes(normalized)) return ListTree;
  if (["code_case", "case", "experiment_report"].includes(normalized)) return BookOpenCheck;
  if (normalized === "video_script") return PlayCircle;
  return FileText;
}

function formatPercent(value: number) {
  const normalized = value <= 1 ? value * 100 : value;
  return `${Math.round(normalized)}%`;
}

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("zh-CN");
}

export function LearningFeedback() {
  const [selfMastery, setSelfMastery] = React.useState<MasteryLevel>("medium");
  const [difficultyRating, setDifficultyRating] = React.useState<DifficultyRating>("appropriate");
  const [hasDoubt, setHasDoubt] = React.useState(false);
  const [notes, setNotes] = React.useState("");
  const [selectedResourceId, setSelectedResourceId] = React.useState(0);
  const [submitting, setSubmitting] = React.useState(false);
  const [masteryChanges, setMasteryChanges] = React.useState<MasteryChange[]>([]);
  const [nextResources, setNextResources] = React.useState<RecommendedResource[] | null>(null);

  const profileState = useApi(() => profilesApi.getMyProfile(), []);
  const profile = profileState.data;
  const feedbackState = useApi(
    () => profile?.course_id
      ? feedbackApi.list({ course_id: profile.course_id, page: 1, page_size: 20 })
      : Promise.resolve({ items: [], total: 0 }),
    [profile?.course_id],
  );
  const resourcesState = useApi(
    () => profile?.course_id
      ? resourcesApi.list({ course_id: profile.course_id, page_size: 100 })
      : Promise.resolve({ items: [], total: 0 }),
    [profile?.course_id],
  );

  const approvedResources = resourcesState.data?.items ?? [];
  React.useEffect(() => {
    if (approvedResources.length === 0) {
      setSelectedResourceId(0);
      return;
    }
    if (!approvedResources.some((resource) => resource.resource_id === selectedResourceId)) {
      setSelectedResourceId(approvedResources[0].resource_id);
    }
  }, [approvedResources, selectedResourceId]);

  const latestFeedback = feedbackState.data?.items?.[0] ?? null;
  const weakPoints = profile?.weak_points ?? [];
  const loadError = profileState.error || feedbackState.error || resourcesState.error;

  const displayedResources = React.useMemo(() => {
    if (nextResources !== null) {
      return nextResources.slice(0, 4).map((resource) => ({
        id: resource.resource_id,
        title: resource.title,
        type: resource.type,
        reason: resource.reason,
      }));
    }
    return approvedResources.slice(0, 4).map((resource) => ({
      id: resource.resource_id,
      title: resource.resource_title,
      type: resource.resource_type,
      reason: "课程推荐",
    }));
  }, [approvedResources, nextResources]);

  const handleSubmit = async () => {
    if (!profile?.course_id) {
      notify.warning("未找到可提交反馈的课程画像");
      return;
    }
    if (hasDoubt && !notes.trim()) {
      notify.warning("请描述仍未解决的具体问题");
      return;
    }

    const mastery = MASTERY_OPTIONS.find((item) => item.value === selfMastery)?.score ?? 0.6;
    setSubmitting(true);
    try {
      const result = await feedbackApi.submit({
        course_id: profile.course_id,
        resource_id: selectedResourceId || undefined,
        feedback_type: hasDoubt ? "question" : "self_report",
        content: notes.trim() || undefined,
        self_mastery: mastery,
        difficulty_rating: difficultyRating,
      });
      const changes = result.mastery_changes ?? [];
      setMasteryChanges(changes);
      setNextResources(result.next_resources ?? []);
      setNotes("");
      setHasDoubt(false);
      await Promise.all([feedbackState.refetch(), profileState.refetch()]);
      notify.success(changes.length > 0 ? "反馈已提交，知识点掌握度已更新" : "反馈已提交并记录");
    } catch (error) {
      notify.error(error instanceof Error ? error.message : "反馈提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  const retry = () => {
    void profileState.refetch();
    if (profile?.course_id) {
      void feedbackState.refetch();
      void resourcesState.refetch();
    }
  };

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 pb-6">
      <PageHero
        eyebrow="学习反馈"
        title="测评与反馈"
        description="记录本次学习效果和具体疑问，系统会据此更新知识点掌握度并调整后续资源推荐。"
        icon={MessageSquare}
        role="student"
        action={(
          <Link
            to="/student/profile"
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
          >
            <Brain className="h-4 w-4" /> 查看我的画像
          </Link>
        )}
      />

      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
        <div className="border-b border-slate-100 bg-slate-50/70 p-5 sm:p-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-blue-700">
              <MessageSquare className="h-4 w-4" /> 学习反馈闭环
            </div>
            <h2 className="mt-2 text-xl font-black text-slate-900">{profile?.course_name ?? "当前课程"}</h2>
            <p className="mt-1 text-sm text-slate-500">{profile ? `${profile.student_name} · 画像掌握度 ${formatPercent(profile.mastery_score)}` : "正在读取学生画像"}</p>
          </div>
        </div>

        {latestFeedback ? (
          <div className="grid grid-cols-2 gap-px bg-slate-100 sm:grid-cols-4">
            {[
              ["最近反馈", FEEDBACK_TYPE_LABELS[latestFeedback.feedback_type] ?? latestFeedback.feedback_type],
              ["关联资源", latestFeedback.resource_title || "自主反馈"],
              ["自评掌握度", latestFeedback.self_mastery == null ? "未填写" : formatPercent(latestFeedback.self_mastery)],
              ["提交时间", formatDate(latestFeedback.created_at)],
            ].map(([label, value]) => (
              <div key={label} className="min-w-0 bg-white p-4">
                <div className="text-xs font-bold text-slate-400">{label}</div>
                <div className="mt-1 truncate text-sm font-black text-slate-800" title={value}>{value}</div>
              </div>
            ))}
          </div>
        ) : !feedbackState.loading && (
          <div className="p-5 text-sm text-slate-500">尚未提交学习反馈，完成一次资源学习后可在下方记录掌握情况。</div>
        )}
      </section>

      {loadError && (
        <section role="alert" className="flex flex-col gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 sm:flex-row sm:items-center sm:justify-between">
          <span>反馈数据加载失败：{loadError.message}</span>
          <button type="button" onClick={retry} className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-red-300 bg-white px-4 font-bold">
            <RefreshCw className="h-4 w-4" /> 重试
          </button>
        </section>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] sm:p-6">
          <h3 className="flex items-center gap-2 text-lg font-black text-slate-900">
            <MessageSquare className="h-5 w-5 text-blue-600" /> 提交本次学习反馈
          </h3>

          {profileState.loading || resourcesState.loading ? (
            <div className="flex min-h-64 items-center justify-center gap-2 text-sm text-slate-400">
              <LoaderCircle className="h-4 w-4 animate-spin" /> 加载反馈上下文
            </div>
          ) : (
            <div className="mt-6 space-y-6">
              <label className="block text-sm font-medium text-slate-700">
                本次学习资源
                <select
                  value={selectedResourceId || ""}
                  onChange={(event) => setSelectedResourceId(Number(event.target.value))}
                  aria-label="本次学习资源"
                  className="edu-focus-ring mt-2 h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm"
                >
                  <option value="">未关联具体资源</option>
                  {approvedResources.map((resource) => (
                    <option key={resource.resource_id} value={resource.resource_id}>
                      {resource.resource_title} · {RESOURCE_TYPE_LABELS[resource.resource_type] ?? resource.resource_type}
                    </option>
                  ))}
                </select>
              </label>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <fieldset>
                  <legend className="mb-3 text-sm font-medium text-slate-700">理解程度自评</legend>
                  <div className="grid grid-cols-3 gap-2">
                    {MASTERY_OPTIONS.map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        aria-pressed={selfMastery === option.value}
                        onClick={() => setSelfMastery(option.value)}
                        className={`min-h-10 rounded-lg border text-sm font-bold transition ${
                          selfMastery === option.value
                            ? "border-blue-500 bg-blue-50 text-blue-700"
                            : "border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </fieldset>

                <fieldset>
                  <legend className="mb-3 text-sm font-medium text-slate-700">资源难度评价</legend>
                  <div className="grid grid-cols-3 gap-2">
                    {DIFFICULTY_OPTIONS.map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        aria-pressed={difficultyRating === option.value}
                        onClick={() => setDifficultyRating(option.value)}
                        className={`min-h-10 rounded-lg border text-sm font-bold transition ${
                          difficultyRating === option.value
                            ? "border-emerald-500 bg-emerald-50 text-emerald-700"
                            : "border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </fieldset>
              </div>

              <fieldset>
                <legend className="mb-3 text-sm font-medium text-slate-700">是否仍有疑问</legend>
                <div className="flex flex-col gap-3 sm:flex-row sm:gap-6">
                  {[
                    { label: "已经基本掌握", value: false },
                    { label: "仍有问题需要跟进", value: true },
                  ].map((option) => (
                    <label key={option.label} className="flex min-h-10 cursor-pointer items-center gap-2">
                      <input
                        type="radio"
                        name="has-doubt"
                        checked={hasDoubt === option.value}
                        onChange={() => setHasDoubt(option.value)}
                        className="h-4 w-4 accent-blue-600"
                      />
                      <span className="text-sm text-slate-700">{option.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              <label className="block text-sm font-medium text-slate-700">
                {hasDoubt ? "具体问题（必填）" : "学习备注（可选）"}
                <textarea
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                  maxLength={4000}
                  rows={4}
                  placeholder={hasDoubt ? "请描述卡住的位置、已尝试的方法和希望获得的帮助" : "记录本次学习中的收获、易错点或后续计划"}
                  className="edu-focus-ring mt-2 w-full resize-none rounded-lg border border-slate-300 bg-slate-50 p-3 text-sm"
                />
              </label>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => void handleSubmit()}
                  disabled={submitting || !profile?.course_id}
                  className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  {submitting ? "提交中..." : "提交反馈"}
                </button>
              </div>

              {masteryChanges.length > 0 && (
                <div className="border-t border-slate-200 pt-5" aria-live="polite">
                  <h4 className="flex items-center gap-2 text-sm font-black text-emerald-800">
                    <CheckCircle2 className="h-4 w-4" /> 知识点掌握度已更新
                  </h4>
                  <div className="mt-3 space-y-2">
                    {masteryChanges.map((change) => (
                      <div key={change.kp_id} className="flex flex-wrap items-center justify-between gap-2 text-sm">
                        <span className="font-medium text-slate-700">{change.kp_name}</span>
                        <span className="font-bold text-emerald-700">{formatPercent(change.before)} → {formatPercent(change.after)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <h3 className="flex items-center gap-2 text-base font-black text-slate-900">
              <Target className="h-5 w-5 text-red-500" /> 我的薄弱知识点
            </h3>
            <span className="rounded bg-slate-100 px-2 py-1 text-xs font-bold text-slate-500">自动同步</span>
          </div>
          {weakPoints.length > 0 ? (
            <ul className="mt-5 space-y-4">
              {weakPoints.slice(0, 5).map((point) => (
                <li key={point.kp_id} className="border-l-2 border-red-200 pl-3">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="font-bold text-slate-800">{point.kp_name || point.name || "未命名知识点"}</span>
                    <span className="font-black text-red-600">{formatPercent(point.mastery_level ?? point.mastery)}</span>
                  </div>
                  {point.reason && <p className="mt-1 text-xs leading-5 text-slate-500">{point.reason}</p>}
                </li>
              ))}
            </ul>
          ) : (
            <div className="mt-5 flex min-h-32 flex-col items-center justify-center text-center text-sm text-slate-400">
              <CheckCircle2 className="mb-2 h-7 w-7 text-emerald-500" /> 当前画像暂无薄弱知识点
            </div>
          )}
          <Link to="/student/profile" className="mt-6 flex min-h-10 items-center justify-center gap-1 border-t border-slate-100 pt-4 text-sm font-bold text-blue-700">
            查看画像详情 <ChevronRight className="h-4 w-4" />
          </Link>
        </aside>
      </div>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)] sm:p-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <h3 className="flex items-center gap-2 text-lg font-black text-slate-900">
            <BookOpen className="h-5 w-5 text-emerald-600" /> 下一步推荐资源
          </h3>
          <span className="text-xs font-medium text-slate-500">{nextResources === null ? "基于当前画像" : "已根据本次反馈重新排序"}</span>
        </div>

        {displayedResources.length > 0 ? (
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {displayedResources.map((resource) => {
              const Icon = resourceIcon(resource.type);
              return (
                <Link
                  key={resource.id}
                  to={`/student/resources?resource=${resource.id}`}
                  className="group rounded-lg border border-slate-200 bg-white p-4 transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="rounded bg-emerald-50 px-2 py-1 text-[11px] font-bold text-emerald-700">{resource.reason}</span>
                  </div>
                  <h4 className="mt-4 line-clamp-2 min-h-10 text-sm font-black leading-5 text-slate-800 group-hover:text-emerald-700">{resource.title}</h4>
                  <p className="mt-3 text-xs font-medium text-slate-500">{RESOURCE_TYPE_LABELS[resource.type] ?? resource.type}</p>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="mt-5 flex min-h-36 flex-col items-center justify-center text-center text-sm text-slate-400">
            {nextResources !== null ? <HelpCircle className="mb-2 h-8 w-8" /> : <AlertCircle className="mb-2 h-8 w-8" />}
            当前没有可推荐的已审核资源
          </div>
        )}
      </section>
    </div>
  );
}
