import { marked } from "marked"
import DOMPurify from "dompurify"
import type { LearningResource } from "@/lib/api/resources"

interface LectureRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

function EvidenceSources({ sources }: { sources: LectureRendererProps['resource']['metadata']['evidence_refs'] }) {
  if (!sources?.length) return null
  return (
    <div className="mt-4 p-4 bg-slate-50 rounded-xl">
      <h4 className="text-sm font-bold text-slate-700 mb-2">📚 证据来源</h4>
      {sources.map((s, i) => (
        <div key={i} className="text-xs text-slate-600 mb-1">
          <span className="font-medium">{s.source}</span> - 第{s.page}页
          {s.content && <div className="mt-1 text-slate-500 italic pl-2 border-l-2 border-slate-200">{s.content}</div>}
        </div>
      ))}
    </div>
  )
}

function DifficultyBadge({ difficulty }: { difficulty?: string }) {
  if (!difficulty) return null
  const colors: Record<string, string> = {
    basic: "bg-emerald-100 text-emerald-700",
    intermediate: "bg-blue-100 text-blue-700",
    advanced: "bg-purple-100 text-purple-700",
  }
  const labels: Record<string, string> = {
    basic: "基础",
    intermediate: "标准",
    advanced: "进阶",
  }
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-bold ${colors[difficulty] ?? "bg-slate-100 text-slate-600"}`}>
      {labels[difficulty] ?? difficulty}
    </span>
  )
}

export function LectureRenderer({ resource }: LectureRendererProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <DifficultyBadge difficulty={resource.difficulty} />
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
        {resource.metadata?.revision_count !== undefined && resource.metadata.revision_count > 0 && (
          <span className="rounded bg-orange-100 px-2 py-0.5 text-xs font-bold text-orange-700">
            修订 {resource.metadata.revision_count} 次
          </span>
        )}
      </div>

      <div
        className="prose prose-sm prose-slate max-w-none"
        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(resource.content ?? "")) }}
      />

      <EvidenceSources sources={resource.metadata?.evidence_refs} />
    </div>
  )
}
