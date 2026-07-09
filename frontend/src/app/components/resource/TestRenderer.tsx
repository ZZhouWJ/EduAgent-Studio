import React, { useState } from "react"
import type { LearningResource } from "@/lib/api/resources"

interface TestRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface TestQuestion {
  id: string
  type: "single" | "multiple" | "true_false" | "fill_blank"
  question: string
  options?: string[]
  correct_answer: string | string[]
  explanation?: string
  points?: number
}

function parseTestContent(content: string): { questions: TestQuestion[]; title?: string; time_limit?: number } {
  try {
    const data = JSON.parse(content)
    if (data.questions) return data
    if (data.items) return { questions: data.items }
    if (Array.isArray(data)) return { questions: data }
    return { questions: [] }
  } catch {
    return { questions: [] }
  }
}

function TestQuestionCard({ q, index }: { q: TestQuestion; index: number }) {
  const [selected, setSelected] = useState<string[]>([])
  const [submitted, setSubmitted] = useState(false)

  const correctAnswers = Array.isArray(q.correct_answer) ? q.correct_answer : [q.correct_answer]
  const isCorrect = selected.length === correctAnswers.length && selected.every(s => correctAnswers.includes(s))

  const handleSelect = (opt: string) => {
    if (submitted) return
    if (q.type === "single" || q.type === "true_false") {
      setSelected([opt])
    } else {
      setSelected(prev =>
        prev.includes(opt) ? prev.filter(s => s !== opt) : [...prev, opt]
      )
    }
  }

  const handleSubmit = () => {
    setSubmitted(true)
  }

  const typeLabel = q.type === "single" ? "单选" : q.type === "multiple" ? "多选" : q.type === "true_false" ? "判断" : "填空"
  const typeColor = q.type === "single" ? "bg-blue-100 text-blue-700" :
                    q.type === "multiple" ? "bg-purple-100 text-purple-700" :
                    q.type === "true_false" ? "bg-emerald-100 text-emerald-700" :
                    "bg-orange-100 text-orange-700"

  return (
    <div className={`rounded-xl border p-4 transition-all ${
      submitted
        ? isCorrect ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50"
        : "border-slate-200 bg-white"
    }`}>
      <div className="flex items-start gap-3">
        <div className={`flex h-7 w-7 shrink-0 place-items-center rounded-lg text-xs font-black ${
          submitted
            ? isCorrect ? "bg-emerald-500 text-white" : "bg-red-500 text-white"
            : "bg-blue-100 text-blue-700"
        }`}>
          {index + 1}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${typeColor}`}>
              {typeLabel}
            </span>
            {q.points && (
              <span className="text-[10px] text-slate-500">满分 {q.points} 分</span>
            )}
          </div>
          <p className="text-sm font-medium text-slate-800 leading-relaxed">{q.question}</p>

          {q.options && q.options.length > 0 && (
            <div className="mt-3 space-y-1.5">
              {q.options.map((opt, i) => {
                const isSelected = selected.includes(opt)
                const isCorrectOpt = correctAnswers.includes(opt)
                let optClass = "bg-slate-50 text-slate-700 border-slate-200"
                if (submitted) {
                  if (isCorrectOpt) optClass = "bg-emerald-100 text-emerald-800 border-emerald-300"
                  else if (isSelected && !isCorrectOpt) optClass = "bg-red-100 text-red-800 border-red-300"
                } else if (isSelected) {
                  optClass = "bg-blue-100 text-blue-800 border-blue-300"
                }
                return (
                  <button
                    key={i}
                    onClick={() => handleSelect(opt)}
                    disabled={submitted}
                    className={`flex w-full items-center gap-2 rounded-lg border p-2 text-sm text-left transition-all ${optClass} ${!submitted ? "hover:border-blue-300 cursor-pointer" : "cursor-default"}`}
                  >
                    <span className="text-xs font-bold text-slate-400">{String.fromCharCode(65 + i)}.</span>
                    <span className="flex-1">{opt}</span>
                    {submitted && isCorrectOpt && <span className="text-emerald-600 text-xs font-bold">✓</span>}
                    {submitted && isSelected && !isCorrectOpt && <span className="text-red-600 text-xs font-bold">✗</span>}
                  </button>
                )
              })}
            </div>
          )}

          {submitted && q.explanation && (
            <div className="mt-3 rounded-lg bg-slate-100 p-3">
              <div className="text-xs font-bold text-slate-600 mb-1">解析</div>
              <div className="text-xs text-slate-600 leading-relaxed">{q.explanation}</div>
            </div>
          )}

          {!submitted && (
            <button
              onClick={handleSubmit}
              disabled={selected.length === 0}
              className="mt-3 rounded-lg bg-blue-600 px-4 py-1.5 text-xs font-bold text-white transition-all hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              提交答案
            </button>
          )}

          {submitted && (
            <div className="mt-3 flex items-center gap-2">
              <span className={`text-sm font-bold ${isCorrect ? "text-emerald-700" : "text-red-700"}`}>
                {isCorrect ? "回答正确 ✓" : "回答错误 ✗"}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function TestRenderer({ resource }: TestRendererProps) {
  const { questions, title, time_limit } = parseTestContent(resource.content ?? "")
  const totalPoints = questions.reduce((acc, q) => acc + (q.points ?? 1), 0)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">
          共 {questions.length} 题
        </span>
        <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-700">
          满分 {totalPoints} 分
        </span>
        {time_limit && (
          <span className="rounded bg-orange-100 px-2 py-0.5 text-xs font-bold text-orange-700">
            时限 {time_limit} 分钟
          </span>
        )}
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {title && <h3 className="text-lg font-black text-slate-900">{title}</h3>}

      {questions.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          测验内容加载中...
        </div>
      ) : (
        <div className="space-y-3">
          {questions.map((q, i) => (
            <TestQuestionCard key={q.id ?? i} q={q} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
