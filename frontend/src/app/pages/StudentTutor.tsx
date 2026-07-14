import React, { useState, useRef, useEffect, useCallback } from "react"
import { Link } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import { BookOpenCheck, Bot, CheckCircle2, ChevronRight, Clock3, Loader2, MessageSquare, Send, ThumbsDown, ThumbsUp, XCircle } from "lucide-react"
import { useApi } from "@/lib/useApi"
import { tutorApi, profilesApi } from "@/lib/api"
import type { Citation, PracticeQuestion, RecommendedResource, ContentBlock, IntentResult, SSEEvent } from "@/lib/api/tutor"
import { PageShell, useInlineToast } from "../components/common/ProductUI"
import { marked } from "marked"
import { ContentBlockRenderer } from "../components/tutor/ContentBlockRenderer"

// 消息类型
type Message = {
  id: string
  role: "student" | "assistant"
  content: string
  citations?: Citation[]
  practice_questions?: PracticeQuestion[]
  recommended_resources?: RecommendedResource[]
  content_blocks?: ContentBlock[]
  intent?: IntentResult
}

// 执行轨迹事件
type ExecutionEvent = {
  id: string
  step: number
  tool: string
  status: "started" | "completed" | "error"
  duration_ms?: number
  result_summary?: string
}

// 建议问题（动态加载）

/* ─── 工具图标映射 ───────────────────────────────────── */
const TOOL_ICONS: Record<string, string> = {
  retrieve_knowledge: "🔍",
  quiz_agent: "📝",
  code_case_agent: "💻",
  mindmap_agent: "🧠",
  planning_agent: "🗺️",
  ppt_agent: "📊",
  tts_tool: "🔊",
  image_agent: "🖼️",
  error_analysis_agent: "❌",
  explanation_skill: "📖",
  default: "⚙️",
}

const TOOL_LABELS: Record<string, string> = {
  retrieve_knowledge: "检索知识库",
  quiz_agent: "生成练习题",
  code_case_agent: "生成代码案例",
  mindmap_agent: "生成思维导图",
  planning_agent: "规划学习路径",
  ppt_agent: "生成 PPT",
  tts_tool: "语音合成",
  image_agent: "生成图片",
  error_analysis_agent: "错因分析",
  explanation_skill: "自适应讲解",
}

/* ─── GPT/Gemini 风格思考动画条 ─────────────────────── */
function ThinkingBar({ events, isFirstThinking }: { events: ExecutionEvent[]; isFirstThinking: boolean }) {
  const currentEvent = events.find((e) => e.status === "started")
  const completedCount = events.filter((e) => e.status === "completed").length
  const errorCount = events.filter((e) => e.status === "error").length
  const totalCount = events.length

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-t from-white via-white to-white/95 pt-4 pb-4 shadow-[0_-4px_20px_rgba(0,0,0,0.08)] border-t border-slate-100">
      <div className="mx-auto max-w-3xl px-4">
        {/* 思考标题行 */}
        <div className="mb-3 flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600">
            <Bot className="h-3.5 w-3.5 text-white" />
          </div>
          <span className="text-sm font-bold text-slate-700">
            {isFirstThinking ? (
              <ThinkingDots />
            ) : currentEvent ? (
              <span className="flex items-center gap-1.5">
                <span className="text-blue-600">{TOOL_LABELS[currentEvent.tool] || currentEvent.tool}</span>
                <span className="text-slate-400 font-normal">执行中...</span>
              </span>
            ) : (
              <span className="text-emerald-600 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" />
                已完成 {completedCount} 个步骤
                {errorCount > 0 && <span className="text-red-500">，{errorCount} 个失败</span>}
              </span>
            )}
          </span>
          {totalCount > 0 && (
            <span className="ml-auto text-xs text-slate-400 font-mono">
              {completedCount}/{totalCount}
            </span>
          )}
        </div>

        {/* 工具步骤条 */}
        {events.length > 0 && (
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {events.map((evt, i) => (
              <div
                key={evt.id}
                className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all duration-300 ${
                  evt.status === "completed"
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    : evt.status === "error"
                    ? "bg-red-50 text-red-600 border border-red-200"
                    : evt.status === "started"
                    ? "bg-blue-50 text-blue-700 border border-blue-200 shadow-sm"
                    : "bg-slate-50 text-slate-400 border border-slate-200"
                }`}
              >
                {/* 状态图标 */}
                {evt.status === "completed" ? (
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-600" />
                ) : evt.status === "error" ? (
                  <XCircle className="h-3.5 w-3.5 shrink-0 text-red-500" />
                ) : evt.status === "started" ? (
                  <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-blue-600" />
                ) : (
                  <span className="h-3.5 w-3.5 shrink-0 flex items-center justify-center text-slate-300">
                    {TOOL_ICONS[evt.tool] || TOOL_ICONS.default}
                  </span>
                )}

                <span className="whitespace-nowrap">{TOOL_LABELS[evt.tool] || evt.tool}</span>

                {/* 耗时 */}
                {evt.duration_ms && evt.status === "completed" && (
                  <span className="text-slate-400 font-mono ml-0.5">{evt.duration_ms}ms</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/* ─── 思考中动画 ───────────────────────────────────── */
function ThinkingDots() {
  return (
    <span className="inline-flex items-center gap-0.5">
      正在思考
      <span className="edu-typing-dot" />
      <span className="edu-typing-dot" />
      <span className="edu-typing-dot" />
    </span>
  )
}

/* ─── 执行轨迹展示 ───────────────────────────────────── */
function ExecutionTrace({ events }: { events: ExecutionEvent[] }) {
  if (!events.length) return null

  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-500">
        <Bot className="h-4 w-4" />
        AI 执行轨迹
      </div>
      <div className="space-y-2">
        {events.map((evt, i) => (
          <div key={evt.id} className="flex items-center gap-3 text-sm">
            {/* 状态图标 */}
            <div className={`shrink-0 rounded-full p-1 ${
              evt.status === "completed"
                ? "bg-emerald-100 text-emerald-600"
                : evt.status === "error"
                ? "bg-red-100 text-red-600"
                : "bg-blue-100 text-blue-600"
            }`}>
              {evt.status === "completed" ? (
                <CheckCircle2 className="h-3 w-3" />
              ) : evt.status === "error" ? (
                <XCircle className="h-3 w-3" />
              ) : (
                <Loader2 className="h-3 w-3 animate-spin" />
              )}
            </div>

            {/* 步骤序号 */}
            <span className="shrink-0 text-xs font-mono text-slate-400 w-4">{evt.step + 1}</span>

            {/* 工具名称 */}
            <span className="font-semibold text-slate-700">
              {TOOL_LABELS[evt.tool] || evt.tool}
            </span>

            {/* 结果摘要 */}
            {evt.status === "completed" && evt.result_summary && (
              <>
                <ChevronRight className="h-3 w-3 shrink-0 text-slate-300" />
                <span className="truncate max-w-[200px] text-xs text-slate-500">
                  {evt.result_summary}
                </span>
              </>
            )}

            {evt.status === "error" && (
              <>
                <ChevronRight className="h-3 w-3 shrink-0 text-slate-300" />
                <span className="text-xs text-red-500">{evt.result_summary || "执行失败"}</span>
              </>
            )}

            {/* 耗时 */}
            {evt.duration_ms && evt.status === "completed" && (
              <span className="ml-auto shrink-0 text-xs text-slate-400">
                <Clock3 className="mr-0.5 inline h-3 w-3" />
                {evt.duration_ms}ms
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── 引用来源卡片 ─────────────────────────────────────── */
function CitationsCard({ citations }: { citations: Citation[] }) {
  if (!citations?.length) return null
  return (
    <div className="mt-3 rounded-xl border border-blue-100 bg-blue-50 p-3">
      <div className="mb-2 text-xs font-bold text-blue-700">引用来源</div>
      <div className="space-y-2">
        {citations.map((cite, i) => (
          <div key={i} className="rounded-lg bg-white p-2 text-xs">
            <div className="font-semibold text-slate-600">{cite.source}</div>
            <div className="mt-1 text-slate-700">{cite.content}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── 练习题卡片 ─────────────────────────────────────── */
function PracticeCard({ questions }: { questions: PracticeQuestion[] }) {
  if (!questions?.length) return null
  return (
    <div className="mt-3 rounded-xl border border-emerald-100 bg-emerald-50 p-3">
      <div className="mb-2 flex items-center gap-2 text-xs font-bold text-emerald-700">
        <BookOpenCheck className="h-4 w-4" />
        练习题
      </div>
      <div className="space-y-3">
        {questions.map((q, i) => (
          <div key={i} className="rounded-lg bg-white p-3">
            <div className="text-sm font-medium text-slate-800">{q.question}</div>
            <details className="mt-2">
              <summary className="cursor-pointer text-xs font-bold text-emerald-600">查看答案</summary>
              <div className="mt-1 rounded bg-emerald-50 p-2 text-xs text-slate-700">{q.answer}</div>
            </details>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── 推荐资源卡片 ─────────────────────────────────────── */
function ResourcesCard({ resources }: { resources: RecommendedResource[] }) {
  if (!resources?.length) return null
  return (
    <div className="mt-3 rounded-xl border border-purple-100 bg-purple-50 p-3">
      <div className="mb-2 text-xs font-bold text-purple-700">推荐学习资源</div>
      <div className="space-y-2">
        {resources.map((res) => (
          <Link
            key={res.resource_id}
            to="/student/resources"
            className="flex items-center justify-between rounded-lg bg-white p-2 text-xs transition hover:bg-purple-50"
          >
            <span className="font-medium text-slate-700">{res.title}</span>
            <span className="rounded bg-purple-100 px-2 py-0.5 text-purple-700">{res.type}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}

/* ─── 内嵌内容块解析 ──────────────────────────────── */
// 将 ":::quiz:block_abc:::这是一段文字 :::code_case:block_def:::" 解析为片段数组
type ContentSegment =
  | { type: "text"; content: string }
  | { type: "embed"; blockType: string; blockId: string }

const EMBED_REGEX = /:::(quiz|code_case|mindmap|lecture|ppt|video_script|error_analysis|learning_card):([^:]+):::/g

function parseInlineBlocks(content: string, blocks: ContentBlock[]): ContentSegment[] {
  if (!content) return []
  const segments: ContentSegment[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  EMBED_REGEX.lastIndex = 0
  while ((match = EMBED_REGEX.exec(content)) !== null) {
    // 文本片段（两个嵌入标记之间的内容）
    if (match.index > lastIndex) {
      segments.push({ type: "text", content: content.slice(lastIndex, match.index) })
    }
    // 嵌入标记：验证 block 是否存在
    const blockId = match[2]
    const block = blocks.find((b) => b.block_id === blockId)
    if (block) {
      segments.push({ type: "embed", blockType: match[1], blockId })
    }
    lastIndex = match.index + match[0].length
  }
  // 剩余文本
  if (lastIndex < content.length) {
    segments.push({ type: "text", content: content.slice(lastIndex) })
  }
  return segments
}

/* ─── 消息气泡 ─────────────────────────────────────── */
function MessageBubble({ message, onFeedback, executionEvents }: {
  message: Message
  onFeedback?: (helpful: boolean) => void
  showFeedback?: boolean
  executionEvents?: ExecutionEvent[]
}) {
  const isStudent = message.role === "student"

  // 解析内嵌块
  const segments = !isStudent && message.content && message.content_blocks
    ? parseInlineBlocks(message.content, message.content_blocks)
    : null
  // 是否使用了内嵌语法
  const hasInlineEmbeds = segments && segments.some((s) => s.type === "embed")
  // 未被引用的 content_blocks（作为兜底在末尾显示）
  const unusedBlocks = !isStudent && message.content_blocks
    ? message.content_blocks.filter((b) => {
        // 检查是否有嵌入标记引用了这个 block
        if (!segments) return true
        return !segments.some((s) => s.type === "embed" && s.blockId === b.block_id)
      })
    : []

  return (
    <div className={`flex ${isStudent ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl p-4 ${
          isStudent
            ? "bg-blue-600 text-white"
            : "border border-slate-100 bg-slate-50 text-slate-700"
        }`}
      >
        {/* 消息内容：内嵌卡片模式优先 */}
        <div className="prose prose-sm max-w-none">
          {hasInlineEmbeds && segments ? (
            // 内嵌卡片模式：交替渲染文本片段和内容块卡片
            <div className="space-y-3">
              {segments.map((seg, i) =>
                seg.type === "text" ? (
                  <ReactMarkdown key={i}>{seg.content}</ReactMarkdown>
                ) : (
                  <ContentBlockRenderer
                    key={i}
                    block={message.content_blocks!.find((b) => b.block_id === seg.blockId)!}
                    embedded
                  />
                )
              )}
            </div>
          ) : message.content && message.content.trim() ? (
            // 有 markdown 内容，正常渲染
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : null}
        </div>

        {!isStudent && (
          <>
            {/* 执行轨迹 */}
            {executionEvents && executionEvents.length > 0 && (
              <ExecutionTrace events={executionEvents} />
            )}

            {/* 已生成内容块标签 — 仅在非内嵌模式下显示 */}
            {!hasInlineEmbeds && message.content_blocks && message.content_blocks.length > 0 && (
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <span className="text-xs text-slate-500">已生成：</span>
                {message.content_blocks.map((block) => (
                  <span
                    key={block.block_id}
                    className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                      block.block_type === "mindmap"
                        ? "bg-purple-100 text-purple-700"
                        : block.block_type === "quiz"
                        ? "bg-emerald-100 text-emerald-700"
                        : block.block_type === "code_case"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {block.block_type === "mindmap"
                      ? "🗺 思维导图"
                      : block.block_type === "quiz"
                      ? "📝 练习题"
                      : block.block_type === "code_case"
                      ? "💻 代码案例"
                      : block.block_type === "ppt"
                      ? "📊 PPT"
                      : block.title}
                  </span>
                ))}
              </div>
            )}

            {/* 多模态内容块（未嵌入的兜底渲染） */}
            {unusedBlocks.length > 0 && (
              <div className="mt-4 space-y-3">
                {unusedBlocks.map((block) => (
                  <ContentBlockRenderer key={block.block_id} block={block} />
                ))}
              </div>
            )}

            <CitationsCard citations={message.citations} />
            <PracticeCard questions={message.practice_questions} />
            <ResourcesCard resources={message.recommended_resources} />
          </>
        )}

        {!isStudent && onFeedback && (
          <div className="mt-3 flex gap-2">
            <button
              onClick={() => onFeedback(true)}
              className="rounded-lg bg-white px-3 py-1.5 text-xs font-bold text-slate-600 ring-1 ring-slate-100 hover:bg-green-50 hover:text-green-700"
            >
              <ThumbsUp className="mr-1 inline h-3.5 w-3.5" />
              有帮助
            </button>
            <button
              onClick={() => onFeedback(false)}
              className="rounded-lg bg-white px-3 py-1.5 text-xs font-bold text-slate-600 ring-1 ring-slate-100 hover:bg-orange-50 hover:text-orange-700"
            >
              <ThumbsDown className="mr-1 inline h-3.5 w-3.5" />
              没理解
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

/* ─── 主页面 ─────────────────────────────────────── */
export function StudentTutor() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [pendingAi, setPendingAi] = useState(false)
  const [currentProfileId, setCurrentProfileId] = useState<number>(1)
  const [currentCourseId, setCurrentCourseId] = useState<number>(1)
  const [lastSessionId, setLastSessionId] = useState<number | null>(null)
  const [activePanel, setActivePanel] = useState<"context" | "chat" | "resources">("chat")
  // 执行轨迹状态（当前活跃消息的轨迹）
  const [activeEvents, setActiveEvents] = useState<ExecutionEvent[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  // 是否处于"正在思考"阶段（还未开始调用工具）
  const [isFirstThinking, setIsFirstThinking] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const { toast, showToast } = useInlineToast()
  const chatScrollRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<(() => void) | null>(null)

  // 获取学生画像
  const { data: profileData } = useApi(() => profilesApi.getMyProfile(), [])
  const currentProfile = profileData

  useEffect(() => {
    if (currentProfile) {
      setCurrentProfileId(currentProfile.profile_id)
      setCurrentCourseId(currentProfile.course_id)
      // 加载动态建议
      tutorApi.getSuggestions(currentProfile.course_id, currentProfile.profile_id)
        .then((res: any) => setSuggestions(res.suggestions || []))
        .catch(() => setSuggestions([]))
    }
  }, [currentProfile])

  // 配置 marked
  useEffect(() => {
    marked.setOptions({
      breaks: true,
      gfm: true,
    })
  }, [])

  // 滚动到底部
  useEffect(() => {
    const el = chatScrollRef.current
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" })
    }
  }, [messages, pendingAi])

  const lastMessage = messages[messages.length - 1]

  // 发送消息（SSE 流式）
  function handleSend(question: string) {
    const text = question.trim()
    if (!text || pendingAi) return

    const msgId = `msg_${Date.now()}`

    // 1. 添加用户消息
    setMessages((prev) => [...prev, { id: msgId, role: "student", content: text }])
    // 添加一条占位助手消息
    const assistantMsgId = `asst_${Date.now()}`
    setMessages((prev) => [...prev, {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      content_blocks: [],
      citations: [],
    }])
    setInput("")
    setPendingAi(true)
    setIsStreaming(true)
    setActiveEvents([])  // 重置轨迹
    setIsFirstThinking(true)

    // 2. SSE 流式调用
    const cancel = tutorApi.chatStream(
      {
        profile_id: currentProfileId,
        course_id: currentCourseId,
        question: text,
      },
      {
        onEvent: (event: SSEEvent) => {
          if (event.type === "supervisor.tool_choice") {
            // 模型选择了工具
            setActiveEvents((prev) => [
              ...prev,
              {
                id: `evt_${Date.now()}`,
                step: event.step,
                tool: event.chosen_tools?.join(", ") || "",
                status: "started",
              },
            ])
          } else if (event.type === "tool.started") {
            setIsFirstThinking(false) // 开始调用工具，不再显示"正在思考"
            setActiveEvents((prev) => [
              ...prev,
              {
                id: `evt_${Date.now()}_${Math.random()}`,
                step: event.step,
                tool: event.tool,
                status: "started",
              },
            ])
          } else if (event.type === "tool.completed") {
            // 更新对应事件为 completed
            setActiveEvents((prev) => {
              const updated = [...prev]
              const lastPending = [...updated].reverse().find((e) => e.tool === event.tool && e.status === "started")
              if (lastPending) {
                lastPending.status = "completed"
                lastPending.duration_ms = event.duration_ms
                lastPending.result_summary = event.result_summary || ""
              } else {
                updated.push({
                  id: `evt_${Date.now()}`,
                  step: event.step,
                  tool: event.tool,
                  status: "completed",
                  duration_ms: event.duration_ms,
                  result_summary: event.result_summary || "",
                })
              }
              return updated
            })
          } else if (event.type === "tool.error") {
            setActiveEvents((prev) => {
              const updated = [...prev]
              const lastPending = [...updated].reverse().find((e) => e.tool === event.tool && e.status === "started")
              if (lastPending) {
                lastPending.status = "error"
                lastPending.result_summary = event.result_summary || "执行失败"
              }
              return updated
            })
          }
        },

        onFinal: (answer: string, contentBlocks: ContentBlock[], citations: Citation[]) => {
          // 更新助手消息
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId
                ? { ...m, content: answer, content_blocks: contentBlocks, citations }
                : m
            )
          )
          setIsStreaming(false)
          setPendingAi(false)
          setActiveEvents([])
          setIsFirstThinking(false)
          showToast("已收到回复")
        },

        onError: (error: string) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId
                ? { ...m, content: `抱歉，发生错误：${error}` }
                : m
            )
          )
          setIsStreaming(false)
          setPendingAi(false)
          setActiveEvents([])
          setIsFirstThinking(false)
          showToast("回复失败")
        },
      }
    )

    abortRef.current = cancel
  }

  // 反馈
  async function handleFeedback(helpful: boolean) {
    if (!lastSessionId) {
      showToast(helpful ? "感谢反馈：有帮助" : "感谢反馈：没理解")
      return
    }

    try {
      await tutorApi.feedback({
        session_id: lastSessionId,
        helpful,
      })
      showToast(helpful ? "感谢反馈：回答有帮助" : "感谢反馈：后续会简化解释")
    } catch {
      showToast("反馈发送失败")
    }
  }

  // 重置对话
  function handleReset() {
    abortRef.current?.()
    setMessages([])
    setLastSessionId(null)
    setActiveEvents([])
    setIsStreaming(false)
    setPendingAi(false)
    setIsFirstThinking(false)
    showToast("对话已重置")
  }

  return (
    <PageShell>
      {/* GPT/Gemini 风格底部思考动画条 */}
      {(pendingAi || activeEvents.length > 0) && (
        <ThinkingBar events={activeEvents} isFirstThinking={isFirstThinking} />
      )}

      {/* 移动端 tab 切换 */}
      <div className="grid grid-cols-3 gap-1 rounded-2xl bg-slate-100 p-1 lg:hidden">
        {(["context", "chat", "resources"] as const).map((key) => (
          <button
            key={key}
            onClick={() => setActivePanel(key)}
            className={`min-h-11 rounded-xl text-sm font-black transition ${
              activePanel === key ? "bg-white text-blue-700 shadow-sm" : "text-slate-500"
            }`}
          >
            {key === "context" ? "上下文" : key === "chat" ? "对话" : "推荐"}
          </button>
        ))}
      </div>

      <section className={`grid min-h-0 grid-cols-1 gap-4 lg:min-h-[720px] lg:grid-cols-[280px_1fr_320px] lg:gap-6 ${pendingAi || activeEvents.length > 0 ? "pb-20" : ""}`}>
        {/* 左侧上下文面板 */}
        <aside
          className={`edu-card rounded-2xl p-5 ${
            activePanel === "context" ? "block" : "hidden lg:block"
          }`}
        >
          <h2 className="mb-4 text-base font-black text-slate-950">学习上下文</h2>
          <div className="space-y-4 text-sm">
            {/* 当前课程 */}
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="text-xs font-bold text-slate-400">当前课程</div>
              <div className="mt-1 font-black text-slate-900">
                {currentProfile?.course_name ?? "数据库系统原理"}
              </div>
            </div>

            {/* 当前学生 */}
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="text-xs font-bold text-slate-400">当前学生</div>
              <div className="mt-1 font-black text-slate-900">
                {currentProfile?.student_name ?? "李明"} /{" "}
                {currentProfile?.current_level ?? "大二"}
              </div>
            </div>

            {/* 薄弱点 */}
            {currentProfile?.weak_points?.length ? (
              <div>
                <div className="mb-2 text-xs font-bold text-slate-400">当前薄弱点</div>
                <div className="flex flex-wrap gap-2">
                  {currentProfile.weak_points.slice(0, 5).map((kp, idx) => (
                    <span
                      key={kp.kp_id ?? kp.name ?? idx}
                      className="rounded-lg bg-orange-50 px-2.5 py-1 text-xs font-bold text-orange-700 ring-1 ring-orange-100"
                    >
                      {kp.kp_name ?? kp.name ?? `知识点${kp.kp_id ?? idx}`}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            {/* 建议提问 */}
            <div>
              <div className="mb-2 text-xs font-bold text-slate-400">建议提问</div>
              <div className="space-y-2">
                {suggestions.map((item) => (
                  <button
                    key={item}
                    onClick={() => setInput(item)}
                    className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left text-xs font-semibold leading-5 text-slate-600 transition-all duration-200 hover:-translate-x-1 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* 中间对话区域 */}
        <main
          className={`edu-card min-w-0 flex-col rounded-2xl ${
            activePanel === "chat" ? "flex" : "hidden lg:flex"
          }`}
        >
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="flex items-center gap-2 text-base font-semibold text-slate-950">
              <MessageSquare className="h-5 w-5 text-slate-500" />
              对话
            </h2>
            <p className="mt-1 text-xs font-semibold text-slate-400">
              {messages.length === 0 ? "输入问题开始答疑" : `${messages.length} 条消息`}
            </p>
          </div>

          {/* 消息列表 */}
          <div ref={chatScrollRef} className="custom-scrollbar flex-1 space-y-4 overflow-y-auto p-5">
            {messages.length === 0 && !pendingAi && (
              <div className="flex h-full items-center justify-center">
                <div className="text-center text-slate-400">
                  <MessageSquare className="mx-auto h-12 w-12 opacity-20" />
                  <p className="mt-2 text-sm">输入问题，AI Tutor 帮你解答</p>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <MessageBubble
                key={message.id || index}
                message={message}
                showFeedback={index === messages.length - 1 && message.role === "assistant"}
                onFeedback={handleFeedback}
                executionEvents={
                  isStreaming && message.role === "assistant" && index === messages.length - 1
                    ? activeEvents
                    : undefined
                }
              />
            ))}

            {/* 加载状态 */}
            {pendingAi && (
              <div className="flex justify-start">
                <div className="flex items-center gap-2 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-3 text-blue-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-xs font-semibold">
                    {isStreaming && activeEvents.length > 0
                      ? `正在调用 ${activeEvents[activeEvents.length - 1]?.tool || "工具"}...`
                      : "正在分析问题..."}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* 输入框 */}
          <div className="border-t border-slate-100 p-4">
            <label className="mb-2 block text-xs font-bold text-slate-500">输入学习问题</label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleSend(input)
                  }
                }}
                placeholder="输入你的学习问题，按 Enter 发送..."
                className="edu-focus-ring h-20 flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-700"
              />
              <button
                onClick={() => handleSend(input)}
                disabled={pendingAi || !input.trim()}
                className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
                发送
              </button>
            </div>
          </div>
        </main>

        {/* 右侧推荐资源面板 */}
        <aside
          className={`flex-col gap-4 ${activePanel === "resources" ? "flex" : "hidden lg:flex"}`}
        >
          {/* 推荐资源 */}
          {lastMessage?.recommended_resources?.length ? (
            <div className="edu-card rounded-2xl p-5">
              <h2 className="mb-4 text-base font-black text-slate-950">当前推荐资源</h2>
              <div className="space-y-3">
                {lastMessage.recommended_resources.map((res) => (
                  <Link
                    key={res.resource_id}
                    to="/student/resources"
                    className="group block rounded-xl border border-slate-100 bg-white p-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:bg-blue-50 hover:shadow-md"
                  >
                    <div className="text-sm font-black text-slate-900 group-hover:text-blue-800">
                      {res.title}
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs">
                      <span className="rounded bg-purple-100 px-2 py-0.5 font-semibold text-purple-700">
                        {res.type}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ) : (
            <div className="edu-card rounded-2xl p-5">
              <h2 className="mb-4 text-base font-black text-slate-950">推荐资源</h2>
              <p className="text-sm text-slate-400">开始对话后这里会显示推荐资源</p>
            </div>
          )}

          {/* 练习题提示 */}
          {lastMessage?.practice_questions?.length ? (
            <div className="edu-card rounded-2xl p-5">
              <h2 className="mb-4 flex items-center gap-2 text-base font-black text-slate-950">
                <BookOpenCheck className="h-5 w-5 text-emerald-700" />
                练习题
              </h2>
              <p className="text-sm text-slate-600">
                当前回答包含 {lastMessage.practice_questions.length} 道练习题，请查看上方回答卡片
              </p>
            </div>
          ) : null}
        </aside>
      </section>
      {toast}
    </PageShell>
  )
}