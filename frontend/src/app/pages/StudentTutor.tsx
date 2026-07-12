import React, { useState, useRef, useEffect } from "react"
import { Link } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import { BookOpenCheck, MessageSquare, Send, ThumbsDown, ThumbsUp } from "lucide-react"
import { useApi } from "@/lib/useApi"
import { tutorApi, profilesApi, type Citation, type PracticeQuestion, type RecommendedResource } from "@/lib/api"
import { PageShell, useInlineToast } from "../components/common/ProductUI"
import { marked } from "marked"

// 消息类型
type Message = {
  role: "student" | "assistant"
  content: string
  citations?: Citation[]
  practice_questions?: PracticeQuestion[]
  recommended_resources?: RecommendedResource[]
}

// 建议问题
const suggestions = [
  "可重复读和串行化到底有什么区别？我总是混淆。",
  "多表连接什么时候应该使用 left join？",
  "事务隔离级别和锁机制有什么关系？",
  "如何把银行转账案例写成 FastAPI 接口？",
]

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

/* ─── 消息气泡 ─────────────────────────────────────── */
function MessageBubble({ message, onFeedback }: {
  message: Message
  onFeedback?: (helpful: boolean) => void
  showFeedback?: boolean
}) {
  const isStudent = message.role === "student"
  return (
    <div className={`flex ${isStudent ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl p-4 ${
          isStudent
            ? "bg-blue-600 text-white"
            : "border border-slate-100 bg-slate-50 text-slate-700"
        }`}
      >
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {!isStudent && (
          <>
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
  const { toast, showToast } = useInlineToast()
  const chatScrollRef = useRef<HTMLDivElement>(null)

  // 获取学生画像
  const { data: profileData } = useApi(() => profilesApi.getMyProfile(), [])
  const currentProfile = profileData

  useEffect(() => {
    if (currentProfile) {
      setCurrentProfileId(currentProfile.profile_id)
      setCurrentCourseId(currentProfile.course_id)
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

  // 发送消息
  async function handleSend(question: string) {
    const text = question.trim()
    if (!text || pendingAi) return

    // 1. 添加用户消息
    setMessages((prev) => [...prev, { role: "student", content: text }])
    setInput("")
    setPendingAi(true)

    try {
      // 2. 调用 tutorApi.chat()
      const response = await tutorApi.chat({
        profile_id: currentProfileId,
        course_id: currentCourseId,
        question: text,
      })

      // 3. 添加助手回复
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          practice_questions: response.practice_questions,
          recommended_resources: response.recommended_resources,
        },
      ])

      // 保存 session_id 用于反馈
      if (response.session_id) {
        setLastSessionId(response.session_id)
      }

      showToast("已收到回复")
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "抱歉，我现在无法回答这个问题。请稍后再试或尝试其他问题。",
        },
      ])
      showToast("回复失败")
    } finally {
      setPendingAi(false)
    }
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
    setMessages([])
    setLastSessionId(null)
    showToast("对话已重置")
  }

  return (
    <PageShell>
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

      <section className="grid min-h-0 grid-cols-1 gap-4 lg:min-h-[720px] lg:grid-cols-[280px_1fr_320px] lg:gap-6">
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
                key={index}
                message={message}
                showFeedback={index === messages.length - 1 && message.role === "assistant"}
                onFeedback={handleFeedback}
              />
            ))}

            {/* 加载状态 */}
            {pendingAi && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1 rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-slate-400">
                  <span className="edu-typing-dot" />
                  <span className="edu-typing-dot" />
                  <span className="edu-typing-dot" />
                  <span className="ml-2 text-xs font-semibold text-slate-400">正在思考…</span>
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