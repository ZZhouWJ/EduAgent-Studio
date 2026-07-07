import type { LearningResource } from "@/lib/api/resources"

interface PptRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface Slide {
  page: number
  title: string
  points: string[]
  notes?: string
}

function parsePptContent(content: string): { slides: Slide[] } {
  try {
    const data = JSON.parse(content)
    if (data.slides) return data
    if (Array.isArray(data)) return { slides: data }
    return { slides: [] }
  } catch {
    return { slides: [] }
  }
}

function SlideCard({ slide }: { slide: Slide }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="rounded bg-white/20 px-2 py-0.5 text-xs font-bold text-white">
            第 {slide.page} 页
          </span>
          <span className="text-sm font-black text-white">{slide.title}</span>
        </div>
      </div>
      <div className="p-4">
        <ul className="space-y-2">
          {slide.points.map((point, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />
              <span className="leading-relaxed">{point}</span>
            </li>
          ))}
        </ul>
        {slide.notes && (
          <div className="mt-3 rounded-lg bg-amber-50 p-2 text-xs text-amber-700 italic">
            备注: {slide.notes}
          </div>
        )}
      </div>
    </div>
  )
}

export function PptRenderer({ resource }: PptRendererProps) {
  const { slides } = parsePptContent(resource.content ?? "")

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">
          共 {slides.length} 页
        </span>
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {slides.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          PPT 内容加载中...
        </div>
      ) : (
        <div className="space-y-4">
          {slides.map((slide, i) => (
            <SlideCard key={slide.page ?? i} slide={slide} />
          ))}
        </div>
      )}
    </div>
  )
}
