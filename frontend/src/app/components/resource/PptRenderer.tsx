import { useState } from "react"
import { Download, Loader2 } from "lucide-react"
import { agentsApi } from "@/lib/api"
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

interface RawSlide {
  page?: number
  slide_number?: number
  title?: unknown
  points?: unknown[]
  bullets?: unknown[]
  notes?: unknown
}

function parsePptContent(content: string): { slides: Slide[] } {
  try {
    const data = JSON.parse(content)
    const rawSlides: RawSlide[] = Array.isArray(data)
      ? data
      : Array.isArray(data.slides)
      ? data.slides
      : []
    return {
      slides: rawSlides.map((slide, index) => ({
        page: slide.page ?? slide.slide_number ?? index + 1,
        title: String(slide.title || `第 ${index + 1} 页`),
        points: Array.isArray(slide.points)
          ? slide.points.map(String)
          : Array.isArray(slide.bullets)
          ? slide.bullets.map(String)
          : [],
        notes: slide.notes ? String(slide.notes) : undefined,
      })),
    }
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
  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState("")

  const exportPptx = async () => {
    if (!slides.length || exporting) return
    setExporting(true)
    setExportError("")
    try {
      const blob = await agentsApi.exportPptx({
        title: resource.resource_title || "EduAgent课件",
        slides: slides.map(({ title, points, notes }) => ({ title, points, notes })),
      })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement("a")
      anchor.href = url
      anchor.download = `${(resource.resource_title || "EduAgent课件").replace(/[\\/:*?"<>|]/g, "_")}.pptx`
      anchor.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      setExportError(error instanceof Error ? error.message : "课件导出失败")
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">
          共 {slides.length} 页
        </span>
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
        {slides.length > 0 && (
          <button
            type="button"
            onClick={() => void exportPptx()}
            disabled={exporting}
            className="ml-auto inline-flex h-9 items-center gap-2 rounded-md bg-blue-700 px-3 text-xs font-bold text-white transition-colors hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {exporting ? <Loader2 className="h-4 w-4 animate-spin motion-reduce:animate-none" /> : <Download className="h-4 w-4" />}
            {exporting ? "正在导出" : "下载 PPTX"}
          </button>
        )}
      </div>
      {exportError && <p role="alert" className="text-xs font-semibold text-red-600">{exportError}</p>}

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
