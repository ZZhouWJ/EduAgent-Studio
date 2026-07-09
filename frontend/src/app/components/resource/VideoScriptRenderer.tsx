import type { LearningResource } from "@/lib/api/resources"

interface VideoScriptRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface Segment {
  index: number
  timestamp: string
  duration?: string
  scene: string
  narration: string
  visual?: string
  audio?: string
}

function parseVideoScriptContent(content: string): { segments: Segment[] } {
  try {
    const data = JSON.parse(content)
    if (data.segments) return data
    if (data.scenes) return { segments: data.scenes }
    if (Array.isArray(data)) return { segments: data }
    return { segments: [] }
  } catch {
    return { segments: [] }
  }
}

function SegmentCard({ segment }: { segment: Segment }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <div className="flex items-center gap-3 bg-gradient-to-r from-purple-600 to-purple-700 px-4 py-2">
        <div className="flex h-6 w-6 shrink-0 place-items-center rounded-full bg-white/20 text-xs font-black text-white">
          {segment.index ?? 1}
        </div>
        <span className="rounded bg-white/20 px-2 py-0.5 text-xs font-bold text-white">
          {segment.timestamp}
        </span>
        {segment.duration && (
          <span className="text-xs text-white/70">({segment.duration})</span>
        )}
      </div>
      <div className="p-4 space-y-3">
        <div>
          <div className="text-xs font-bold text-slate-500 mb-1">镜头描述</div>
          <p className="text-sm text-slate-800 leading-relaxed">{segment.scene}</p>
        </div>
        <div>
          <div className="text-xs font-bold text-slate-500 mb-1">讲解内容</div>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg">
            {segment.narration}
          </p>
        </div>
        {segment.visual && (
          <div>
            <div className="text-xs font-bold text-slate-500 mb-1">画面</div>
            <p className="text-xs text-slate-600">{segment.visual}</p>
          </div>
        )}
        {segment.audio && (
          <div>
            <div className="text-xs font-bold text-slate-500 mb-1">音效</div>
            <p className="text-xs text-slate-600">{segment.audio}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export function VideoScriptRenderer({ resource }: VideoScriptRendererProps) {
  const { segments } = parseVideoScriptContent(resource.content ?? "")

  const totalDuration = segments.reduce((acc, seg) => {
    if (seg.duration) {
      const match = seg.duration.match(/(\d+):(\d+)/)
      if (match) return acc + parseInt(match[1]) * 60 + parseInt(match[2])
    }
    return acc
  }, 0)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="rounded bg-purple-100 px-2 py-0.5 text-xs font-bold text-purple-700">
          共 {segments.length} 段
        </span>
        {totalDuration > 0 && (
          <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-600">
            总时长 {Math.floor(totalDuration / 60)}:{String(totalDuration % 60).padStart(2, "0")}
          </span>
        )}
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {segments.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          视频脚本加载中...
        </div>
      ) : (
        <div className="space-y-4">
          {segments.map((segment, i) => (
            <SegmentCard key={segment.index ?? i} segment={segment} />
          ))}
        </div>
      )}
    </div>
  )
}
