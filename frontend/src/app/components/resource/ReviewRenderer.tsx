import type { LearningResource } from "@/lib/api/resources"

interface ReviewRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface ReviewItem {
  id?: string
  day?: number | string
  week?: number | string
  title: string
  tasks: string[]
  duration?: string
  notes?: string
}

function parseReviewContent(content: string): { items: ReviewItem[]; title?: string } {
  try {
    const data = JSON.parse(content)
    if (data.items) return data
    if (data.schedule) return { items: data.schedule }
    if (Array.isArray(data)) return { items: data }
    return { items: [] }
  } catch {
    return { items: [] }
  }
}

function TimelineItem({ item, isLast }: { item: ReviewItem; isLast: boolean }) {
  const timeLabel = item.day ? `第 ${item.day} 天` : item.week ? `第 ${item.week} 周` : ""

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className="flex h-8 w-8 shrink-0 place-items-center rounded-full bg-emerald-500 text-xs font-black text-white">
          {item.day ?? item.week ?? "?"}
        </div>
        {!isLast && <div className="w-0.5 flex-1 bg-emerald-200" />}
      </div>
      <div className="flex-1 pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-black text-slate-900">{item.title}</span>
          {timeLabel && (
            <span className="rounded bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">
              {timeLabel}
            </span>
          )}
          {item.duration && (
            <span className="text-xs text-slate-500">{item.duration}</span>
          )}
        </div>
        <div className="space-y-1.5">
          {item.tasks.map((task, i) => (
            <div key={i} className="flex items-start gap-2 rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
              <span className="leading-relaxed">{task}</span>
            </div>
          ))}
        </div>
        {item.notes && (
          <div className="mt-2 rounded-lg bg-amber-50 p-2 text-xs text-amber-700 italic">
            {item.notes}
          </div>
        )}
      </div>
    </div>
  )
}

export function ReviewRenderer({ resource }: ReviewRendererProps) {
  const { items, title } = parseReviewContent(resource.content ?? "")

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="rounded bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">
          共 {items.length} 个复习节点
        </span>
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {title && <h3 className="text-lg font-black text-slate-900">{title}</h3>}

      {items.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          复习计划加载中...
        </div>
      ) : (
        <div className="relative">
          {items.map((item, i) => (
            <TimelineItem key={item.id ?? i} item={item} isLast={i === items.length - 1} />
          ))}
        </div>
      )}
    </div>
  )
}
