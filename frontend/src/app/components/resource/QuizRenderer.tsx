import { useState } from "react"
import type { LearningResource } from "@/lib/api/resources"

interface QuizRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface QuizQuestion {
  id: string
  type: "single" | "multiple" | "true_false"
  question: string
  options?: string[]
  answer: string | string[]
  explanation?: string
}

function parseQuizContent(content: string): QuizQuestion[] {
  try {
    const data = JSON.parse(content)
    if (Array.isArray(data)) return data
    if (data.questions) return data.questions
    return []
  } catch {
    return []
  }
}

function QuestionCard({ q, index }: { q: QuizQuestion; index: number }) {
  const [expanded, setExpanded] = useState(false)

  const answerText = Array.isArray(q.answer) ? q.answer.join("、") : q.answer
  const typeLabel = q.type === "single" ? "单选" : q.type === "multiple" ? "多选" : "判断"

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 transition-all">
      <div className="flex items-start gap-3">
        <div className="flex h-7 w-7 shrink-0 place-items-center rounded-lg bg-blue-100 text-xs font-black text-blue-700">
          {index + 1}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
              q.type === "single" ? "bg-blue-100 text-blue-700" :
              q.type === "multiple" ? "bg-purple-100 text-purple-700" :
              "bg-emerald-100 text-emerald-700"
            }`}>
              {typeLabel}
            </span>
          </div>
          <p className="text-sm font-medium text-slate-800 leading-relaxed">{q.question}</p>

          {q.options && q.options.length > 0 && (
            <div className="mt-3 space-y-1.5">
              {q.options.map((opt, i) => (
                <div key={i} className="flex items-center gap-2 rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
                  <span className="text-xs font-bold text-slate-400">{String.fromCharCode(65 + i)}.</span>
                  <span>{opt}</span>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-3 flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800"
          >
            {expanded ? "收起答案" : "查看答案"}
            <span className={`transition-transform ${expanded ? "rotate-180" : ""}`}>▼</span>
          </button>

          {expanded && (
            <div className="mt-3 rounded-lg bg-emerald-50 p-3 border border-emerald-100">
              <div className="text-xs font-bold text-emerald-700 mb-1">正确答案</div>
              <div className="text-sm font-black text-emerald-800">{answerText}</div>
              {q.explanation && (
                <>
                  <div className="mt-2 text-xs font-bold text-slate-600 mb-1">解析</div>
                  <div className="text-xs text-slate-600 leading-relaxed">{q.explanation}</div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function QuizRenderer({ resource }: QuizRendererProps) {
  const questions = parseQuizContent(resource.content ?? "")

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">
          共 {questions.length} 题
        </span>
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {questions.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          题目内容加载中...
        </div>
      ) : (
        <div className="space-y-3">
          {questions.map((q, i) => (
            <QuestionCard key={q.id ?? i} q={q} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
