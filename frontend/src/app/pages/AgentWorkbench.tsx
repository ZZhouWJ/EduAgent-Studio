import React, { useState, useRef, useEffect, useCallback } from "react";
import { marked } from "marked";
import {
  AlertCircle,
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Database,
  Eye,
  FileText,
  Gauge,
  Layers3,
  Link2,
  Network,
  Play,
  RefreshCcw,
  RotateCcw,
  Route,
  Save,
  ScanSearch,
  Send,
  Settings2,
  ShieldCheck,
  Terminal,
  Sparkles,
  StopCircle,
  XCircle,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { agentsApi, learningApi, modelsApi, client, getToken } from "@/lib/api";
import { useInlineToast } from "../components/common/ProductUI";
import type { AgentRequest, WorkflowResult } from "@/lib/api/agents";
import type { Course, KnowledgePoint } from "@/lib/api/learning";

const RESOURCE_TYPES = [
  "课程讲义", "思维导图", "分层练习题", "代码实操案例",
  "PPT 大纲", "视频/动画脚本", "实验报告", "错题解析",
  "学习卡片",
];

// 中文标签 → 后端英文 key 映射
const RESOURCE_TYPE_KEY_MAP: Record<string, string> = {
  "课程讲义": "lecture",
  "思维导图": "mindmap",
  "分层练习题": "quiz",
  "代码实操案例": "code_case",
  "PPT 大纲": "ppt",
  "视频/动画脚本": "video_script",
  "实验报告": "experiment_report",
  "错题解析": "error_analysis",
  "学习卡片": "learning_card",
};
const DIFFICULTY_MAP: Record<string, string> = {
  "基础": "basic",
  "标准": "intermediate",
  "进阶": "advanced",
};
const DIFFICULTY_REVERSE: Record<string, string> = {
  "basic": "基础",
  "intermediate": "标准",
  "advanced": "进阶",
};

// 后端 WorkflowStep 枚举映射
const STEP_ORDER = ["diagnosis", "planning", "generation", "assessment", "teacher_review", "revision"] as const;
const STEP_LABELS: Record<string, string> = {
  diagnosis: "学习诊断智能体",
  planning: "路径规划智能体",
  generation: "资源生成智能体",
  assessment: "评测反馈智能体",
  teacher_review: "教师审核智能体",
  revision: "返工修订智能体",
};
const STEP_ICONS: Record<string, React.ElementType> = {
  diagnosis: BrainCircuit,
  planning: Route,
  generation: Layers3,
  assessment: ClipboardCheck,
  teacher_review: ShieldCheck,
  revision: RefreshCcw,
};

interface AgentStep {
  name: string;
  icon: React.ElementType;
  state: "waiting" | "running" | "done" | "error";
  summary: string;
  evidence: string;
}

function stepClasses(state: string) {
  if (state === "done") {
    return {
      icon: "bg-emerald-50 text-emerald-700 ring-emerald-200",
      card: "border-emerald-100 bg-emerald-50/40",
      badge: "bg-emerald-100 text-emerald-700 ring-emerald-200",
    };
  }
  if (state === "running") {
    return {
      icon: "bg-blue-600 text-white ring-blue-200",
      card: "border-blue-200 bg-blue-50/60",
      badge: "bg-blue-100 text-blue-700 ring-blue-200",
    };
  }
  if (state === "error") {
    return {
      icon: "bg-red-50 text-red-700 ring-red-200",
      card: "border-red-100 bg-red-50/40",
      badge: "bg-red-100 text-red-700 ring-red-200",
    };
  }
  return {
    icon: "bg-slate-100 text-slate-400 ring-slate-200",
    card: "border-slate-100 bg-slate-50/70",
    badge: "bg-slate-100 text-slate-500 ring-slate-200",
  };
}

function buildInitialSteps(): AgentStep[] {
  return STEP_ORDER.map((step) => ({
    name: STEP_LABELS[step] || step,
    icon: STEP_ICONS[step] || Bot,
    state: "waiting" as const,
    summary: "等待执行",
    evidence: "排队中",
  }));
}

export function AgentWorkbench() {
  const { toast, showToast } = useInlineToast();
  const { data: courseList, refetch: refetchCourses } = useApi(() => learningApi.listCourses(), []);
  const { data: modelData } = useApi(() => modelsApi.getModels({ status: "active" }), []);

  // === 表单状态 ===
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState<number>(1);
  const [selectedKps, setSelectedKps] = useState<KnowledgePoint[]>([]);
  const [resourceType, setResourceType] = useState(RESOURCE_TYPES[0]);
  const [difficulty, setDifficulty] = useState("基础");
  const [generationGoal, setGenerationGoal] = useState("");
  const [enableReview, setEnableReview] = useState(true);

  // === 工作流状态 ===
  const [workflowState, setWorkflowState] = useState<"idle" | "running" | "done" | "error">("idle");
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>(buildInitialSteps);
  const [logs, setLogs] = useState<string[]>([]);
  const [completedCount, setCompletedCount] = useState(0);
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [currentStep, setCurrentStep] = useState<string>("");
  const abortControllerRef = useRef<AbortController | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const activeModel = modelData?.items?.[0]?.display_name ?? "讯飞星火";

  // 自动选中第一个课程
  useEffect(() => {
    if (courseList && courseList.length > 0 && !selectedCourse) {
      setSelectedCourse(courseList[0]);
    }
  }, [courseList, selectedCourse]);

  // 课程变更时加载知识点
  useEffect(() => {
    if (selectedCourse) {
      learningApi.getCourse(selectedCourse.id).then((course) => {
        if (course.knowledge_points && course.knowledge_points.length > 0) {
          setSelectedKps(course.knowledge_points.slice(0, 3));
        }
      }).catch(() => {});
    }
  }, [selectedCourse]);

  // 自动滚动日志
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const addLog = useCallback((msg: string) => {
    setLogs((prev) => [...prev, msg]);
  }, []);

  const updateStepState = useCallback((step: string, state: AgentStep["state"], summary?: string, evidence?: string) => {
    setAgentSteps((prev) =>
      prev.map((s) =>
        s.name === STEP_LABELS[step] || s.name === step
          ? { ...s, state, summary: summary ?? s.summary, evidence: evidence ?? s.evidence }
          : s
      )
    );
  }, []);

  const resetWorkflow = useCallback(() => {
    setWorkflowState("idle");
    setAgentSteps(buildInitialSteps());
    setLogs([]);
    setCompletedCount(0);
    setResult(null);
    setCurrentStep("");
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
  }, []);

  const handleStartGeneration = useCallback(async () => {
    if (!selectedCourse || selectedKps.length === 0) {
      showToast("请选择课程和至少一个知识点", "error");
      return;
    }

    resetWorkflow();
    setWorkflowState("running");
    addLog("启动多智能体生成流程...");

    const request: AgentRequest = {
      student_id: selectedStudentId,
      course_id: selectedCourse.id,
      knowledge_point_ids: selectedKps.map((kp) => kp.id),
      resource_type: RESOURCE_TYPE_KEY_MAP[resourceType] || "lecture",
      difficulty: DIFFICULTY_MAP[difficulty] || "intermediate",
    };

    abortControllerRef.current = new AbortController();

    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";
      const token = getToken();
      const url = `${baseURL}/agents/generate/stream`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(request),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`请求失败: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("无法读取响应流");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const dataStr = line.slice(6);
          if (!dataStr.trim()) continue;

          try {
            const event = JSON.parse(dataStr);

            if (event.type === "done") {
              addLog("生成流程已完成");
              setWorkflowState("done");
              break;
            }

            if (event.type === "error") {
              addLog(`错误: ${event.message}`);
              setWorkflowState("error");
              break;
            }

            // 解析工作流步骤事件
            const step = event.step || event.node;
            if (step && STEP_LABELS[step]) {
              setCurrentStep(step);

              // 更新当前步骤为 running
              updateStepState(step, "running", `${STEP_LABELS[step]} 执行中...`, "生成中");
              addLog(`开始执行: ${STEP_LABELS[step]}`);

              // 根据 step_history 判断完成的步骤
              const history = event.step_history || [];
              for (const record of history) {
                if (record.status === "success") {
                  const recordStep = record.step;
                  updateStepState(
                    recordStep,
                    "done",
                    `${STEP_LABELS[recordStep] || recordStep} 已完成`,
                    `${record.duration_ms}ms`
                  );
                } else if (record.status === "failed") {
                  updateStepState(
                    recordStep,
                    "error",
                    `${STEP_LABELS[recordStep] || recordStep} 失败: ${record.error}`,
                    record.error || "失败"
                  );
                  addLog(`失败: ${record.error}`);
                }
              }

              // 如果有诊断结果
              if (event.has_diagnosis) {
                const diagnosis = event.metadata?.diagnosis;
                if (diagnosis) {
                  updateStepState("diagnosis", "done", "学习诊断已完成", "识别薄弱点");
                }
              }

              // 如果有学习计划
              if (event.has_plan) {
                updateStepState("planning", "done", "学习路径已生成", "路径规划完成");
              }

              // 如果有资源生成
              if (event.has_resource) {
                updateStepState("generation", "done", "个性化资源已生成", "资源生成完成");
              }

              // 如果有评测结果
              if (event.has_assessment) {
                updateStepState("assessment", "done", "学习效果评测已完成", "评测完成");
              }

              // 如果有审核结果
              if (event.has_review) {
                updateStepState("teacher_review", "done", "教师审核已完成", `质量评分: ${event.quality_score}`);
                setCompletedCount(5);
              }

              // 更新返工次数
              if (event.revision_count > 0) {
                updateStepState("revision", "done", `返工已完成 (第${event.revision_count}次)`, "返工完成");
                addLog(`返工 ${event.revision_count} 次完成`);
              }

              setCompletedCount(history.filter((r: any) => r.status === "success").length);
            }
          } catch (e) {
            console.error("解析SSE事件失败:", e);
          }
        }
      }

      // 完成后获取完整结果
      if (workflowState !== "error") {
        try {
          const finalResult = await agentsApi.generate(request);
          setResult(finalResult);
          addLog("资源生成完毕，结果已就绪");
        } catch (e) {
          console.error("获取最终结果失败:", e);
        }
      }
    } catch (e: any) {
      if (e.name === "AbortError" || e.name === "CanceledError") {
        addLog("生成流程已取消");
        setWorkflowState("idle");
      } else {
        addLog(`发生错误: ${e.message}`);
        setWorkflowState("error");
      }
      console.error("SSE流式读取失败:", e);
    }
  }, [selectedCourse, selectedStudentId, selectedKps, resourceType, difficulty, addLog, resetWorkflow, updateStepState, showToast, workflowState]);

  const handleSaveResource = useCallback(async () => {
    if (!result || !selectedCourse) {
      showToast("无可保存的资源", "error");
      return;
    }
    try {
      await agentsApi.saveResource({
        result,
        title: result.resource?.title || "学习资源",
        course_id: selectedCourse.id,
      });
      showToast("资源已保存到资源库", "success");
    } catch (e: any) {
      showToast(`保存失败: ${e.message}`, "error");
    }
  }, [result, selectedCourse, showToast]);

  const handleStopGeneration = useCallback(() => {
    abortControllerRef.current?.abort();
    addLog("用户主动停止生成");
    setWorkflowState("idle");
  }, [addLog]);

  const totalSteps = STEP_ORDER.length;

  return (
    <div className="page-shell flex min-h-0 flex-col">
      <div className="flex shrink-0 flex-col items-stretch justify-between gap-4 lg:flex-row lg:items-start lg:gap-6">
        <div className="min-w-0">
          <div className="mb-2 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600">
            <Network className="h-3.5 w-3.5" />
            资源生成工作台
          </div>
          <h1 className="text-2xl font-semibold text-slate-900">资源生成工作台</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
            面向课程、班级和重点学生群体，组织班级诊断、画像聚合、知识定位、路径规划、资源生成、测评生成与教师审核辅助等环节协同工作。
          </p>
        </div>

        <div className="grid shrink-0 grid-cols-1 gap-2 text-sm sm:grid-cols-3 lg:max-w-[620px]">
          {[
            ["当前课程", selectedCourse?.name || "未选择"],
            ["知识点", selectedKps.length > 0 ? `${selectedKps.length} 个` : "未选择"],
            ["模型模式", activeModel],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <div className="text-[11px] font-bold text-slate-400">{label}</div>
              <div className="mt-1 max-w-[190px] truncate text-xs font-black text-slate-800">{value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-4 xl:flex-row xl:gap-6">
        <aside className="custom-scrollbar w-full shrink-0 xl:w-[300px] xl:overflow-y-auto xl:pb-6">
          <div className="edu-card rounded-2xl p-5">
            <div className="mb-5 flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2">
                <Settings2 className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-900">生成上下文</h2>
              </div>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-semibold text-slate-600">教师端</span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">选择课程</label>
                <select
                  className="edu-focus-ring h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700"
                  value={selectedCourse?.id || ""}
                  onChange={(e) => {
                    const id = Number(e.target.value);
                    const course = courseList?.find((c) => c.id === id);
                    setSelectedCourse(course || null);
                  }}
                >
                  <option value="">请选择课程</option>
                  {courseList?.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">指定学生 ID</label>
                <input
                  type="number"
                  className="edu-focus-ring h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700"
                  value={selectedStudentId}
                  onChange={(e) => setSelectedStudentId(Number(e.target.value))}
                  min={1}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-700">选择知识点</label>
                <div className="space-y-2">
                  {selectedKps.length > 0 ? (
                    selectedKps.map((kp) => (
                      <label key={kp.id} className="flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border border-blue-100 bg-blue-50/60 px-3">
                        <input
                          type="checkbox"
                          checked
                          onChange={() => {
                            setSelectedKps((prev) => prev.filter((k) => k.id !== kp.id));
                          }}
                          className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="flex-1 text-sm font-semibold text-slate-700">{kp.name}</span>
                        <span className="text-[11px] font-bold text-blue-700">{Math.round(kp.mastery_avg * 100)}%</span>
                      </label>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400">请先选择课程</p>
                  )}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-700">资源类型</label>
                <div className="grid grid-cols-2 gap-2">
                  {RESOURCE_TYPES.map((type) => (
                    <button
                      key={type}
                      onClick={() => setResourceType(type)}
                      className={`min-h-10 rounded-xl border px-2 text-xs font-bold transition ${
                        resourceType === type
                          ? "border-purple-200 bg-purple-50 text-purple-700"
                          : "border-slate-200 bg-white text-slate-600 hover:border-blue-200 hover:text-blue-700"
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-700">难度</label>
                <div className="grid grid-cols-3 gap-2 rounded-2xl bg-slate-100 p-1">
                  {["基础", "标准", "进阶"].map((item, index) => (
                    <button
                      key={item}
                      onClick={() => setDifficulty(item)}
                      className={`h-9 rounded-xl text-sm font-bold transition ${
                        difficulty === item ? "bg-white text-blue-700 shadow-sm" : "text-slate-500 hover:text-slate-800"
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">生成目标</label>
                <textarea
                  className="edu-focus-ring h-24 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-700"
                  value={generationGoal}
                  onChange={(e) => setGenerationGoal(e.target.value)}
                  placeholder="描述生成资源的目标和要求..."
                />
              </div>

              <label className="flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50/70 px-3">
                <input
                  type="checkbox"
                  checked={enableReview}
                  onChange={(e) => setEnableReview(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                />
                <span className="text-sm font-bold text-emerald-800">启用教师审核前置规则</span>
              </label>
            </div>

            <div className="mt-5 space-y-3 border-t border-slate-100 pt-5">
              {workflowState === "running" ? (
                <button
                  onClick={handleStopGeneration}
                  className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-red-600 text-sm font-black text-white shadow-[0_14px_30px_rgba(220,38,38,0.24)] transition hover:bg-red-700"
                >
                  <StopCircle className="h-4 w-4" />
                  停止生成
                </button>
              ) : (
                <button
                  onClick={handleStartGeneration}
                  disabled={workflowState === "running" || !selectedCourse || selectedKps.length === 0}
                  className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-[linear-gradient(110deg,#2563EB,#7C3AED)] text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.24)] transition hover:shadow-[0_18px_36px_rgba(37,99,235,0.32)] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play className="h-4 w-4" />
                  启动智能体生成
                </button>
              )}
              <button
                onClick={resetWorkflow}
                className="flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 transition hover:border-blue-200 hover:text-blue-700"
              >
                <RotateCcw className="h-4 w-4" />
                重置配置
              </button>
            </div>
          </div>
        </aside>

        <section className="flex min-w-0 flex-1 flex-col gap-4">
          <div className="edu-card flex min-h-[540px] flex-col rounded-2xl p-5 xl:min-h-0 xl:flex-1">
            <div className="mb-5 flex flex-col items-start justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
              <div className="flex items-center gap-2">
                <Route className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-900">执行链路</h2>
              </div>
              <div className="flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-black text-blue-700 ring-1 ring-blue-100">
                {workflowState === "running" && <span className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />}
                {workflowState === "idle" && `等待开始 ${completedCount}/${totalSteps}`}
                {workflowState === "running" && `运行中 ${completedCount}/${totalSteps}`}
                {workflowState === "done" && `已完成 ${completedCount}/${totalSteps}`}
                {workflowState === "error" && `出错 ${completedCount}/${totalSteps}`}
              </div>
            </div>

            <div className="custom-scrollbar relative flex-1 space-y-3 overflow-y-auto pr-0 sm:pr-2">
              <div className="absolute bottom-4 left-[21px] top-2 w-px bg-slate-200" />
              {agentSteps.map((step, index) => {
                const Icon = step.icon;
                const cls = stepClasses(step.state);
                return (
                  <div key={step.name} className="relative flex gap-3">
                    <div className={`relative z-10 grid h-11 w-11 shrink-0 place-items-center rounded-2xl ring-1 ${cls.icon}`}>
                      <Icon className={step.state === "running" ? "h-5 w-5 animate-pulse" : "h-5 w-5"} />
                    </div>
                    <div className={`min-w-0 flex-1 rounded-2xl border p-4 ${cls.card}`}>
                      <div className="mb-2 flex items-center justify-between gap-3">
                        <div className="flex min-w-0 items-center gap-2">
                          <span className="text-[11px] font-black text-slate-400">0{index + 1}</span>
                          <h3 className="truncate text-sm font-black text-slate-900">{step.name}</h3>
                        </div>
                        <span className={`shrink-0 rounded-full px-2 py-1 text-[11px] font-black ring-1 ${cls.badge}`}>
                          {step.state === "done" ? "已完成" : step.state === "running" ? "运行中" : step.state === "error" ? "失败" : "等待中"}
                        </span>
                      </div>
                      <p className="text-sm leading-6 text-slate-600">{step.summary}</p>
                      <div className="mt-3 flex items-center gap-2 text-xs font-semibold text-slate-500">
                        {step.state === "done" ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : step.state === "running" ? <Gauge className="h-3.5 w-3.5 text-blue-600" /> : step.state === "error" ? <XCircle className="h-3.5 w-3.5 text-red-600" /> : <Clock3 className="h-3.5 w-3.5 text-slate-400" />}
                        {step.evidence}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="h-48 shrink-0 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 text-xs font-semibold text-slate-500">
              <span className="flex items-center gap-2">
                <Terminal className="h-3.5 w-3.5" />
                实时生成日志
              </span>
              <span className={`rounded-full px-2 py-1 ring-1 ${workflowState === "running" ? "bg-blue-500/10 text-blue-200 ring-blue-400/20" : "bg-slate-700 text-slate-400 ring-slate-600"}`}>
                {workflowState === "running" ? "streaming" : workflowState}
              </span>
            </div>
            <div className="custom-scrollbar h-[144px] overflow-y-auto p-4 font-mono text-[13px] leading-6">
              {logs.length === 0 ? (
                <div className="text-slate-500">等待启动生成流程...</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className={index === logs.length - 1 ? "flex items-center gap-2 text-blue-200" : "text-slate-300"}>
                    <span className={index === logs.length - 1 ? "text-blue-300" : "text-emerald-300"}>{index === logs.length - 1 ? ">" : "✓"}</span>
                    <span>{log}</span>
                    {index === logs.length - 1 && workflowState === "running" && <span className="ml-1 h-4 w-1 animate-pulse bg-blue-300" />}
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        </section>

        <aside className="custom-scrollbar flex w-full shrink-0 flex-col gap-4 xl:w-[380px] xl:overflow-y-auto xl:pb-6">
          <div className="edu-card rounded-2xl p-5">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-900">资源预览</h2>
              </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  {[
                    ["可信度评分", result.metadata?.quality_score ? `${Math.round(result.metadata.quality_score * 10)}%` : "—", result.metadata?.quality_score && result.metadata.quality_score >= 7 ? "text-emerald-700" : "text-orange-700"],
                    ["返工次数", String(result.metadata?.revision_count || 0), "text-slate-700"],
                    ["风险等级", result.metadata?.quality_score && result.metadata.quality_score >= 7 ? "低" : "中", result.metadata?.quality_score && result.metadata.quality_score >= 7 ? "text-emerald-700" : "text-orange-700"],
                    ["教师复核", result.metadata?.quality_score && result.metadata.quality_score >= 7 ? "通过" : "建议", "text-orange-700"],
                  ].map(([label, value, color]) => (
                    <div key={label} className="rounded-xl border border-slate-100 bg-slate-50 p-3">
                      <div className="text-xs font-semibold text-slate-500">{label}</div>
                      <div className={`mt-1 text-xl font-black ${color}`}>{value}</div>
                    </div>
                  ))}
                </div>

                {result.teacher_review_suggestion?.suggestions && result.teacher_review_suggestion.suggestions.length > 0 && (
                  <div className="mt-4 rounded-2xl border border-orange-100 bg-orange-50 p-3">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-orange-600" />
                      <p className="text-sm leading-5 text-orange-800">
                        {result.teacher_review_suggestion.suggestions[0]}
                      </p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="rounded-2xl border border-slate-100 bg-slate-50 p-8 text-center text-slate-400">
                <p className="text-sm">生成资源将在流程完成后显示</p>
              </div>
            )}
          </div>

          <div className="edu-card flex-1 rounded-2xl p-5">
            <div className="mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-slate-700" />
              <h2 className="text-base font-black text-slate-950">证据来源</h2>
            </div>

            <div className="space-y-3">
              {result?.diagnosis?.weak_points?.length ? (
                result.diagnosis.weak_points.map((wp, index) => (
                  <button key={wp.kp_id || index} className="flex w-full items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3 text-left transition hover:border-blue-200 hover:bg-blue-50">
                    <div className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-white text-xs font-black text-blue-700 ring-1 ring-blue-100">
                      {index + 1}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-bold leading-5 text-slate-800">{wp.name}</div>
                      <div className="mt-1 flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                        掌握度 {Math.round(wp.mastery_level * 100)}%
                      </div>
                    </div>
                    <ArrowRight className="mt-1 h-4 w-4 text-slate-300" />
                  </button>
                ))
              ) : (
                selectedKps.map((kp, index) => (
                  <button key={kp.id} className="flex w-full items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3 text-left transition hover:border-blue-200 hover:bg-blue-50">
                    <div className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-white text-xs font-black text-blue-700 ring-1 ring-blue-100">
                      {index + 1}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-bold leading-5 text-slate-800">{kp.name}</div>
                      <div className="mt-1 flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                        掌握度 {Math.round(kp.mastery_avg * 100)}%
                      </div>
                    </div>
                    <ArrowRight className="mt-1 h-4 w-4 text-slate-300" />
                  </button>
                ))
              )}
            </div>

            <div className="mt-5 grid grid-cols-2 gap-2">
              <button
                onClick={handleSaveResource}
                disabled={!result}
                className="flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 text-sm font-bold text-white transition hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="h-4 w-4" />
                保存资源
              </button>
              <button
                onClick={() => setEnableReview(!enableReview)}
                className={`flex min-h-11 items-center justify-center gap-2 rounded-xl text-sm font-bold ring-1 transition ${
                  enableReview
                    ? "bg-orange-50 text-orange-700 ring-orange-200 hover:bg-orange-100"
                    : "border border-slate-200 bg-white text-slate-600 hover:border-blue-200 hover:text-blue-700"
                }`}
              >
                <Send className="h-4 w-4" />
                提交审核
              </button>
              <button
                onClick={handleStartGeneration}
                disabled={workflowState === "running"}
                className="flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 transition hover:border-blue-200 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCcw className="h-4 w-4" />
                重新生成
              </button>
              <button
                onClick={() => {
                  if (result?.resource?.content) {
                    window.prompt("完整资源内容：", result.resource.content);
                  }
                }}
                disabled={!result}
                className="flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 transition hover:border-blue-200 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Eye className="h-4 w-4" />
                完整内容
              </button>
            </div>
          </div>
        </aside>
      </div>
      {toast}
    </div>
  );
}
