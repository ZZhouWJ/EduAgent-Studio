import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import DOMPurify from "dompurify";
import { marked } from "marked";
import {
  AlertCircle,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Database,
  ExternalLink,
  Eye,
  FileText,
  Gauge,
  Layers3,
  Link2,
  LoaderCircle,
  Play,
  RefreshCcw,
  RotateCcw,
  Route,
  Save,
  Settings2,
  ShieldCheck,
  Square,
  Terminal,
  XCircle,
} from "lucide-react";
import { ModalShell, PageShell } from "../components/common/ProductUI";
import { agentsApi, getToken, learningApi, profilesApi } from "@/lib/api";
import type { AgentRequest, WorkflowResult } from "@/lib/api/agents";
import type { KnowledgePoint } from "@/lib/api/learning";
import type { ProfileDetail } from "@/lib/api/profiles";
import { notify } from "@/lib/toast";
import { useApi } from "@/lib/useApi";

const RESOURCE_TYPES = [
  { label: "课程讲义", value: "lecture" },
  { label: "思维导图", value: "mindmap" },
  { label: "分层练习题", value: "quiz" },
  { label: "代码实操案例", value: "code_case" },
  { label: "PPT 大纲", value: "ppt" },
  { label: "视频/动画脚本", value: "video_script" },
  { label: "实验报告", value: "experiment_report" },
  { label: "错题解析", value: "error_analysis" },
  { label: "学习卡片", value: "learning_card" },
] as const;

const DIFFICULTIES = [
  { label: "基础", value: "basic" },
  { label: "标准", value: "intermediate" },
  { label: "进阶", value: "advanced" },
] as const;

const STEP_DEFINITIONS = [
  { key: "diagnosis", name: "学习诊断", icon: BrainCircuit },
  { key: "planning", name: "路径规划", icon: Route },
  { key: "generation", name: "资源生成", icon: Layers3 },
  { key: "assessment", name: "质量评测", icon: ClipboardCheck },
  { key: "teacher_review", name: "审核建议", icon: ShieldCheck },
  { key: "revision", name: "自适应修订", icon: RefreshCcw },
] as const;

type StepKey = (typeof STEP_DEFINITIONS)[number]["key"];
type StepState = "waiting" | "running" | "done" | "error" | "skipped";

type AgentStep = {
  key: StepKey;
  name: string;
  icon: React.ElementType;
  state: StepState;
  summary: string;
  evidence: string;
};

type StepRecord = {
  step: string;
  status: string;
  duration_ms?: number;
  error?: string;
};

type StreamEvent = {
  type?: "done" | "error";
  message?: string;
  node?: string;
  step?: string;
  result?: WorkflowResult | null;
  step_history?: StepRecord[];
  revision_count?: number;
  quality_score?: number | null;
  has_diagnosis?: boolean;
  has_plan?: boolean;
  has_resource?: boolean;
  has_assessment?: boolean;
  has_review?: boolean;
};

type LogEntry = {
  id: number;
  message: string;
  tone: "normal" | "success" | "error";
};

function initialSteps(): AgentStep[] {
  return STEP_DEFINITIONS.map((step) => ({
    ...step,
    state: "waiting",
    summary: "等待执行",
    evidence: "排队中",
  }));
}

function isStepKey(value: string): value is StepKey {
  return STEP_DEFINITIONS.some((step) => step.key === value);
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "发生未知错误";
}

function stepTone(state: StepState) {
  if (state === "done") {
    return {
      icon: "bg-emerald-50 text-emerald-700 ring-emerald-200",
      panel: "border-emerald-200 bg-emerald-50/50",
      badge: "bg-emerald-50 text-emerald-700 ring-emerald-200",
      label: "已完成",
    };
  }
  if (state === "running") {
    return {
      icon: "bg-blue-600 text-white ring-blue-200",
      panel: "border-blue-300 bg-blue-50",
      badge: "bg-blue-50 text-blue-700 ring-blue-200",
      label: "运行中",
    };
  }
  if (state === "error") {
    return {
      icon: "bg-red-50 text-red-700 ring-red-200",
      panel: "border-red-200 bg-red-50/60",
      badge: "bg-red-50 text-red-700 ring-red-200",
      label: "失败",
    };
  }
  if (state === "skipped") {
    return {
      icon: "bg-slate-100 text-slate-500 ring-slate-200",
      panel: "border-slate-200 bg-slate-50",
      badge: "bg-slate-100 text-slate-600 ring-slate-200",
      label: "无需执行",
    };
  }
  return {
    icon: "bg-slate-100 text-slate-400 ring-slate-200",
    panel: "border-slate-200 bg-white",
    badge: "bg-slate-100 text-slate-500 ring-slate-200",
    label: "等待中",
  };
}

export function AgentWorkbench() {
  const navigate = useNavigate();
  const coursesState = useApi(() => learningApi.listCourses(), []);
  const agentsState = useApi(() => agentsApi.listAgents(), []);
  const [selectedCourseId, setSelectedCourseId] = useState(0);
  const [selectedStudentId, setSelectedStudentId] = useState(0);
  const [selectedKps, setSelectedKps] = useState<KnowledgePoint[]>([]);
  const [courseKps, setCourseKps] = useState<KnowledgePoint[]>([]);
  const [courseDetailLoading, setCourseDetailLoading] = useState(false);
  const [courseDetailError, setCourseDetailError] = useState("");
  const [resourceType, setResourceType] = useState<AgentRequest["resource_type"]>("lecture");
  const [difficulty, setDifficulty] = useState<AgentRequest["difficulty"]>("basic");
  const [generationGoal, setGenerationGoal] = useState("");
  const [workflowState, setWorkflowState] = useState<"idle" | "running" | "done" | "error">("idle");
  const [steps, setSteps] = useState<AgentStep[]>(initialSteps);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [savedResourceId, setSavedResourceId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [contentOpen, setContentOpen] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const runIdRef = useRef(0);
  const logIdRef = useRef(0);
  const loggedStepRef = useRef<Set<StepKey>>(new Set());
  const logEndRef = useRef<HTMLDivElement>(null);

  const courses = coursesState.data ?? [];
  const selectedCourse = courses.find((course) => course.id === selectedCourseId) ?? null;
  const profilesState = useApi(
    () => selectedCourseId
      ? profilesApi.list({ course_id: selectedCourseId, page_size: 100 })
      : Promise.resolve({ items: [] as ProfileDetail[], total: 0 }),
    [selectedCourseId],
  );
  const profiles = profilesState.data?.items ?? [];
  const selectedStudent = profiles.find((profile) => profile.student_id === selectedStudentId) ?? null;

  const qualityScore = result?.metadata?.quality_score;
  const qualityPercent = typeof qualityScore === "number" ? `${Math.round(qualityScore * 10)}%` : "-";
  const revisionCount = result?.metadata?.revision_count ?? 0;
  const completedCount = steps.filter((step) => step.state === "done").length;
  const canGenerate = Boolean(
    selectedCourseId
    && selectedStudentId
    && selectedKps.length
    && !courseDetailLoading
    && !courseDetailError
    && workflowState !== "running",
  );

  const renderedContent = useMemo(() => {
    const content = result?.resource?.content;
    if (!content) return "";
    const withCitations = content.replace(
      /\[引用:(\d+)\]/g,
      '<mark class="rounded bg-blue-100 px-0.5 text-blue-900">[引用:$1]</mark>',
    );
    return DOMPurify.sanitize(marked.parse(withCitations, { async: false }) as string);
  }, [result?.resource?.content]);

  const addLog = useCallback((message: string, tone: LogEntry["tone"] = "normal") => {
    logIdRef.current += 1;
    setLogs((current) => [...current, { id: logIdRef.current, message, tone }]);
  }, []);

  const updateStep = useCallback(
    (key: StepKey, state: StepState, summary?: string, evidence?: string) => {
      setSteps((current) => current.map((step) => (
        step.key === key
          ? { ...step, state, summary: summary ?? step.summary, evidence: evidence ?? step.evidence }
          : step
      )));
    },
    [],
  );

  const resetResult = useCallback(() => {
    setWorkflowState("idle");
    setSteps(initialSteps());
    setLogs([]);
    setResult(null);
    setSavedResourceId(null);
    setSaving(false);
    loggedStepRef.current = new Set();
  }, []);

  const handleReset = useCallback(() => {
    runIdRef.current += 1;
    abortRef.current?.abort();
    abortRef.current = null;
    resetResult();
  }, [resetResult]);

  useEffect(() => {
    if (!selectedCourseId && courses.length) {
      setSelectedCourseId(courses[0].id);
    }
  }, [courses, selectedCourseId]);

  useEffect(() => {
    if (!profiles.length) {
      setSelectedStudentId(0);
      return;
    }
    if (!profiles.some((profile) => profile.student_id === selectedStudentId)) {
      setSelectedStudentId(profiles[0].student_id);
    }
  }, [profiles, selectedStudentId]);

  const loadCourseDetails = useCallback(async (courseId: number) => {
    setCourseKps([]);
    setSelectedKps([]);
    setCourseDetailError("");
    if (!courseId) return;
    setCourseDetailLoading(true);
    try {
      const course = await learningApi.getCourse(courseId);
      const knowledgePoints = course.knowledge_points ?? [];
      setCourseKps(knowledgePoints);
      setSelectedKps(knowledgePoints.slice(0, 3));
    } catch (error) {
      setCourseDetailError(errorMessage(error));
    } finally {
      setCourseDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCourseDetails(selectedCourseId);
  }, [loadCourseDetails, selectedCourseId]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [logs]);

  useEffect(() => () => {
    runIdRef.current += 1;
    abortRef.current?.abort();
  }, []);

  const applyStreamEvent = useCallback((event: StreamEvent) => {
    const history = event.step_history ?? [];
    for (const record of history) {
      if (!isStepKey(record.step)) continue;
      if (record.status === "success") {
        updateStep(record.step, "done", `${STEP_DEFINITIONS.find((step) => step.key === record.step)?.name ?? record.step}已完成`, `${record.duration_ms ?? 0}ms`);
      } else if (record.status === "failed") {
        updateStep(record.step, "error", record.error || "执行失败", "需要处理");
      }
    }

    const currentStep = event.step || event.node;
    if (currentStep && isStepKey(currentStep) && !history.some((record) => record.step === currentStep && record.status === "success")) {
      updateStep(currentStep, "running", "智能体正在处理当前上下文", "流式执行中");
    }
    if (event.has_diagnosis) updateStep("diagnosis", "done", "学生薄弱点与资源需求已识别", "诊断结果就绪");
    if (event.has_plan) updateStep("planning", "done", "个性化学习路径已生成", "路径结果就绪");
    if (event.has_resource) updateStep("generation", "done", "目标资源正文已生成", "内容结果就绪");
    if (event.has_assessment) updateStep("assessment", "done", "质量评测已完成", "评测结果就绪");
    if (event.has_review) updateStep("teacher_review", "done", "审核建议已生成", `质量评分 ${event.quality_score ?? "-"}`);
    if ((event.revision_count ?? 0) > 0) {
      updateStep("revision", "running", `正在执行第 ${event.revision_count} 次质量修订`, "质量闭环");
    }
  }, [updateStep]);

  const startGeneration = useCallback(async () => {
    if (!canGenerate || !selectedCourse) {
      notify.warning("请完整选择课程、学生和知识点");
      return;
    }

    runIdRef.current += 1;
    const activeRunId = runIdRef.current;
    abortRef.current?.abort();
    resetResult();
    setWorkflowState("running");
    addLog("已建立生成上下文，开始多智能体协作");

    const controller = new AbortController();
    abortRef.current = controller;
    const request: AgentRequest = {
      student_id: selectedStudentId,
      course_id: selectedCourse.id,
      knowledge_point_ids: selectedKps.map((kp) => kp.id),
      resource_type: resourceType,
      difficulty,
      generation_goal: generationGoal.trim() || undefined,
    };

    try {
      const token = getToken();
      if (!token) throw new Error("登录状态已失效，请重新登录");
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
      const response = await fetch(`${baseUrl}/agents/generate/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });
      if (!response.ok) {
        let message = `生成请求失败 (${response.status})`;
        try {
          const payload = await response.json() as { message?: unknown; detail?: unknown };
          if (typeof payload.message === "string") message = payload.message;
          else if (typeof payload.detail === "string") message = payload.detail;
        } catch {
          // Keep the status-based message when the response is not JSON.
        }
        throw new Error(message);
      }
      if (!response.body) throw new Error("服务器未返回可读取的生成流");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let completed = false;

      while (!completed) {
        const chunk = await reader.read();
        buffer += decoder.decode(chunk.value ?? new Uint8Array(), { stream: !chunk.done });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const rawLine of lines) {
          const line = rawLine.trimEnd();
          if (!line.startsWith("data:")) continue;
          const payload = line.slice(5).trim();
          if (!payload) continue;
          let event: StreamEvent;
          try {
            event = JSON.parse(payload) as StreamEvent;
          } catch {
            throw new Error("生成流包含无法解析的数据");
          }

          if (event.type === "error") {
            throw new Error(event.message || "生成流程执行失败");
          }
          if (event.type === "done") {
            if (!event.result) throw new Error("生成流程结束但未返回资源");
            if (runIdRef.current !== activeRunId) return;
            const revisions = event.result.metadata?.revision_count ?? 0;
            setResult(event.result);
            setSteps((current) => current.map((step) => ({
              ...step,
              state: step.key === "revision" && revisions === 0 ? "skipped" : "done",
              summary: step.key === "revision" && revisions === 0 ? "质量达标，无需返工" : step.summary,
              evidence: step.key === "revision" && revisions === 0 ? "已跳过" : step.evidence,
            })));
            setWorkflowState("done");
            addLog("生成完成，资源与审核建议已就绪", "success");
            completed = true;
            break;
          }

          if (runIdRef.current !== activeRunId) return;
          applyStreamEvent(event);
          const stepName = event.step || event.node;
          if (stepName && isStepKey(stepName) && !loggedStepRef.current.has(stepName)) {
            loggedStepRef.current.add(stepName);
            addLog(`${STEP_DEFINITIONS.find((step) => step.key === stepName)?.name ?? stepName}已返回进度`);
          }
        }

        if (chunk.done && !completed) {
          throw new Error("生成连接提前结束，请重新生成");
        }
      }
    } catch (error) {
      if (runIdRef.current !== activeRunId) return;
      if (error instanceof Error && error.name === "AbortError") {
        setWorkflowState("idle");
        addLog("生成已停止");
      } else {
        const message = errorMessage(error);
        setWorkflowState("error");
        addLog(message, "error");
        notify.error(message);
      }
    } finally {
      if (runIdRef.current === activeRunId) abortRef.current = null;
    }
  }, [addLog, applyStreamEvent, canGenerate, difficulty, generationGoal, resetResult, resourceType, selectedCourse, selectedKps, selectedStudentId]);

  const stopGeneration = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const saveDraft = useCallback(async () => {
    if (!result || !selectedCourse || saving || savedResourceId) return;
    setSaving(true);
    try {
      const saved = await agentsApi.saveResource({
        result,
        title: result.resource?.title || "个性化学习资源",
        course_id: selectedCourse.id,
      });
      setSavedResourceId(saved.resource_id);
      notify.success("资源草稿已保存到学习资源库");
    } catch (error) {
      notify.error(`保存失败：${errorMessage(error)}`);
    } finally {
      setSaving(false);
    }
  }, [result, savedResourceId, saving, selectedCourse]);

  return (
    <PageShell className="pb-6">
      <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-blue-700">
            <Bot className="h-4 w-4" />
            多智能体内容生产
          </div>
          <h1 className="text-2xl font-semibold text-slate-950 sm:text-3xl">智能体工坊</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            基于学生画像、课程知识点和教材证据，完成诊断、规划、生成、评测与修订闭环。
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {[
            ["协作智能体", agentsState.loading ? "-" : String(agentsState.data?.length ?? 0)],
            ["当前课程", selectedCourse?.name || "未选择"],
            ["目标学生", selectedStudent?.student_name || "未选择"],
            ["知识点", selectedKps.length ? `${selectedKps.length} 个` : "未选择"],
          ].map(([label, value]) => (
            <div key={label} className="min-w-0 rounded-lg border border-slate-200 bg-white px-3 py-2">
              <div className="text-[11px] font-semibold text-slate-500">{label}</div>
              <div className="mt-1 max-w-[150px] truncate text-xs font-semibold text-slate-900">{value}</div>
            </div>
          ))}
        </div>
      </header>

      {(coursesState.error || agentsState.error) && (
        <div className="flex flex-col gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 sm:flex-row sm:items-center sm:justify-between">
          <span>{coursesState.error?.message || agentsState.error?.message}</span>
          <button
            onClick={() => {
              void coursesState.refetch();
              void agentsState.refetch();
            }}
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-red-200 bg-white px-3 font-semibold"
          >
            <RefreshCcw className="h-4 w-4" />
            重新加载
          </button>
        </div>
      )}

      <div className="grid min-w-0 gap-5 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
        <aside className="rounded-lg border border-slate-200 bg-white p-4 sm:p-5">
          <div className="mb-5 flex items-center gap-2 border-b border-slate-100 pb-4">
            <Settings2 className="h-5 w-5 text-slate-700" />
            <h2 className="text-base font-semibold text-slate-950">生成上下文</h2>
          </div>
          <div className="space-y-4">
            <label className="block text-sm font-semibold text-slate-700">
              课程
              <select
                value={selectedCourseId || ""}
                onChange={(event) => setSelectedCourseId(Number(event.target.value))}
                disabled={workflowState === "running" || coursesState.loading}
                className="edu-focus-ring mt-1.5 h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm font-normal disabled:opacity-60"
              >
                <option value="">请选择课程</option>
                {courses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}
              </select>
            </label>

            <label className="block text-sm font-semibold text-slate-700">
              学生
              <select
                value={selectedStudentId || ""}
                onChange={(event) => setSelectedStudentId(Number(event.target.value))}
                disabled={workflowState === "running" || profilesState.loading || !selectedCourseId}
                className="edu-focus-ring mt-1.5 h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm font-normal disabled:opacity-60"
              >
                <option value="">请选择学生</option>
                {profiles.map((profile) => (
                  <option key={profile.student_id} value={profile.student_id}>
                    {profile.student_name} · 掌握度 {Math.round(profile.mastery_score <= 1 ? profile.mastery_score * 100 : profile.mastery_score)}%
                  </option>
                ))}
              </select>
            </label>
            {profilesState.error && <p className="text-xs text-red-700">学生列表加载失败：{profilesState.error.message}</p>}

            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-700">知识点</span>
                <span className="text-xs text-slate-500">已选 {selectedKps.length}</span>
              </div>
              {courseDetailLoading ? (
                <div className="flex min-h-20 items-center justify-center text-sm text-slate-500">
                  <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />加载中
                </div>
              ) : courseDetailError ? (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-700">
                  <p>{courseDetailError}</p>
                  <button onClick={() => void loadCourseDetails(selectedCourseId)} className="mt-2 font-semibold underline">重试</button>
                </div>
              ) : courseKps.length ? (
                <div className="max-h-44 space-y-1 overflow-y-auto pr-1">
                  {courseKps.map((kp) => {
                    const checked = selectedKps.some((selected) => selected.id === kp.id);
                    return (
                      <label key={kp.id} className={`flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border px-3 text-sm ${checked ? "border-blue-200 bg-blue-50 text-blue-800" : "border-slate-200 text-slate-600 hover:bg-slate-50"}`}>
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={workflowState === "running"}
                          onChange={(event) => setSelectedKps((current) => (
                            event.target.checked
                              ? [...current, kp]
                              : current.filter((selected) => selected.id !== kp.id)
                          ))}
                          className="h-4 w-4 rounded border-slate-300 accent-blue-600"
                        />
                        <span className="min-w-0 flex-1 truncate">{kp.name}</span>
                      </label>
                    );
                  })}
                </div>
              ) : (
                <p className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-500">当前课程暂无知识点</p>
              )}
            </div>

            <label className="block text-sm font-semibold text-slate-700">
              资源类型
              <select
                value={resourceType}
                onChange={(event) => setResourceType(event.target.value as AgentRequest["resource_type"])}
                disabled={workflowState === "running"}
                className="edu-focus-ring mt-1.5 h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm font-normal"
              >
                {RESOURCE_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
              </select>
            </label>

            <div>
              <span className="text-sm font-semibold text-slate-700">难度</span>
              <div className="mt-1.5 grid grid-cols-3 rounded-lg bg-slate-100 p-1">
                {DIFFICULTIES.map((item) => (
                  <button
                    key={item.value}
                    onClick={() => setDifficulty(item.value)}
                    disabled={workflowState === "running"}
                    className={`min-h-9 rounded-md text-sm font-semibold ${difficulty === item.value ? "bg-white text-blue-700 shadow-sm" : "text-slate-500"}`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            <label className="block text-sm font-semibold text-slate-700">
              生成目标
              <textarea
                value={generationGoal}
                onChange={(event) => setGenerationGoal(event.target.value)}
                disabled={workflowState === "running"}
                maxLength={1000}
                placeholder="例如：聚焦事务隔离级别对并发异常的影响"
                className="edu-focus-ring mt-1.5 h-24 w-full resize-none rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm font-normal leading-5"
              />
            </label>

            {workflowState === "running" ? (
              <button onClick={stopGeneration} className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-red-600 text-sm font-semibold text-white hover:bg-red-700">
                <Square className="h-4 w-4" />停止生成
              </button>
            ) : (
              <button onClick={() => void startGeneration()} disabled={!canGenerate} className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-blue-600 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">
                <Play className="h-4 w-4" />启动生成
              </button>
            )}
            <button onClick={handleReset} className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg border border-slate-200 text-sm font-semibold text-slate-700 hover:bg-slate-50">
              <RotateCcw className="h-4 w-4" />重置结果
            </button>
          </div>
        </aside>

        <section className="min-w-0 space-y-5" aria-label="智能体执行状态">
          <section className="rounded-lg border border-slate-200 bg-white p-4 sm:p-5">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2">
                <Route className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-950">执行链路</h2>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ring-1 ${workflowState === "error" ? "bg-red-50 text-red-700 ring-red-200" : workflowState === "running" ? "bg-blue-50 text-blue-700 ring-blue-200" : workflowState === "done" ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-slate-100 text-slate-600 ring-slate-200"}`}>
                {workflowState === "running" ? `运行中 ${completedCount}/6` : workflowState === "done" ? "流程完成" : workflowState === "error" ? "执行失败" : "等待开始"}
              </span>
            </div>
            <div className="space-y-3">
              {steps.map((step, index) => {
                const tone = stepTone(step.state);
                const Icon = step.icon;
                return (
                  <div key={step.key} className={`flex gap-3 rounded-lg border p-3 sm:p-4 ${tone.panel}`}>
                    <div className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ring-1 ${tone.icon}`}>
                      <Icon className={`h-5 w-5 ${step.state === "running" ? "animate-pulse" : ""}`} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-semibold text-slate-400">{String(index + 1).padStart(2, "0")}</span>
                          <h3 className="text-sm font-semibold text-slate-900">{step.name}</h3>
                        </div>
                        <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ring-1 ${tone.badge}`}>{tone.label}</span>
                      </div>
                      <p className="mt-2 text-sm leading-5 text-slate-600">{step.summary}</p>
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-slate-500">
                        {step.state === "done" ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : step.state === "error" ? <XCircle className="h-3.5 w-3.5 text-red-600" /> : step.state === "running" ? <Gauge className="h-3.5 w-3.5 text-blue-600" /> : <Clock3 className="h-3.5 w-3.5" />}
                        {step.evidence}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
            <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3 text-xs text-slate-300">
              <span className="flex items-center gap-2"><Terminal className="h-4 w-4" />实时日志</span>
              <span>{workflowState === "running" ? "streaming" : workflowState}</span>
            </div>
            <div className="h-44 overflow-y-auto p-4 font-mono text-xs leading-6">
              {logs.length ? logs.map((log) => (
                <div key={log.id} className={log.tone === "error" ? "text-red-300" : log.tone === "success" ? "text-emerald-300" : "text-slate-300"}>
                  <span className="mr-2 text-slate-500">{log.tone === "error" ? "!" : ">"}</span>{log.message}
                </div>
              )) : <span className="text-slate-500">等待启动生成流程</span>}
              <div ref={logEndRef} />
            </div>
          </section>
        </section>

        <aside className="min-w-0 space-y-5">
          <section className="rounded-lg border border-slate-200 bg-white p-4 sm:p-5">
            <div className="mb-4 flex items-center gap-2 border-b border-slate-100 pb-4">
              <FileText className="h-5 w-5 text-slate-700" />
              <h2 className="text-base font-semibold text-slate-950">资源预览</h2>
            </div>
            {result ? (
              <>
                <h3 className="text-base font-semibold leading-6 text-slate-950">{result.resource?.title || "个性化学习资源"}</h3>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  {[
                    ["质量评分", qualityPercent],
                    ["返工次数", String(revisionCount)],
                    ["可信等级", result.trustworthiness === "high" ? "高" : result.trustworthiness === "medium" ? "中" : result.trustworthiness === "low" ? "低" : "草稿"],
                    ["生成耗时", result.metadata?.total_duration_ms ? `${result.metadata.total_duration_ms}ms` : "-"],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <div className="text-[11px] font-semibold text-slate-500">{label}</div>
                      <div className="mt-1 text-lg font-semibold text-slate-900">{value}</div>
                    </div>
                  ))}
                </div>
                {result.trustworthiness === "draft" && (
                  <div className="mt-4 flex gap-2 rounded-lg border border-orange-200 bg-orange-50 p-3 text-xs leading-5 text-orange-800">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    当前内容缺少充分教材证据，保存后仍为教师草稿。
                  </div>
                )}
                <div className="prose prose-sm prose-slate mt-4 max-h-72 max-w-none overflow-y-auto rounded-lg border border-slate-200 p-3" dangerouslySetInnerHTML={{ __html: renderedContent }} />
                {result.teacher_review_suggestion?.suggestions?.[0] && (
                  <div className="mt-4 rounded-lg border border-orange-200 bg-orange-50 p-3 text-sm leading-6 text-orange-900">
                    <div className="mb-1 font-semibold">审核建议</div>
                    {result.teacher_review_suggestion.suggestions[0]}
                  </div>
                )}
              </>
            ) : (
              <div className="flex min-h-48 flex-col items-center justify-center text-center text-sm text-slate-500">
                <FileText className="mb-3 h-8 w-8 text-slate-300" />
                完成生成后在此预览资源
              </div>
            )}
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-4 sm:p-5">
            <div className="mb-4 flex items-center gap-2 border-b border-slate-100 pb-4">
              <Database className="h-5 w-5 text-slate-700" />
              <h2 className="text-base font-semibold text-slate-950">证据来源</h2>
            </div>
            <div className="space-y-2">
              {result?.evidence_links?.length ? result.evidence_links.map((link, index) => (
                <div key={`${link.chunk_id ?? "chunk"}-${index}`} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="flex items-center gap-1.5 font-semibold text-blue-700"><Link2 className="h-3.5 w-3.5" />证据 {index + 1}</span>
                    <span className="text-slate-400">chunk #{link.chunk_id ?? "-"}</span>
                  </div>
                  <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">{link.quote_text || link.content || "暂无引文摘要"}</p>
                </div>
              )) : result?.diagnosis?.weak_points?.length ? result.diagnosis.weak_points.map((point) => (
                <div key={point.kp_id} className="rounded-lg border border-slate-200 p-3">
                  <div className="text-sm font-semibold text-slate-800">{point.name}</div>
                  <div className="mt-1 text-xs text-slate-500">掌握度 {Math.round(point.mastery_level * 100)}%</div>
                </div>
              )) : <p className="py-6 text-center text-sm text-slate-500">暂无证据数据</p>}
            </div>

            <div className="mt-5 grid grid-cols-2 gap-2">
              <button onClick={() => void saveDraft()} disabled={!result || saving || Boolean(savedResourceId)} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-blue-600 px-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">
                {saving ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                {savedResourceId ? "草稿已保存" : saving ? "保存中" : "保存草稿"}
              </button>
              <button onClick={() => setContentOpen(true)} disabled={!result} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50">
                <Eye className="h-4 w-4" />完整内容
              </button>
              <button onClick={() => void startGeneration()} disabled={!canGenerate} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50">
                <RefreshCcw className="h-4 w-4" />重新生成
              </button>
              <button onClick={() => navigate(`/teacher/resources?course=${selectedCourseId}`)} disabled={!savedResourceId} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50">
                <ExternalLink className="h-4 w-4" />查看草稿
              </button>
            </div>
          </section>
        </aside>
      </div>

      <ModalShell title={result?.resource?.title || "完整资源内容"} open={contentOpen} onClose={() => setContentOpen(false)}>
        {result ? (
          <div className="prose prose-sm prose-slate max-w-none" dangerouslySetInnerHTML={{ __html: renderedContent }} />
        ) : null}
      </ModalShell>
    </PageShell>
  );
}
