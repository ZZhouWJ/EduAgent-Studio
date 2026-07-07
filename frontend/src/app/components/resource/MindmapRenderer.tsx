import type { LearningResource } from "@/lib/api/resources"

interface MindmapRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface MindmapNode {
  id?: string
  label: string
  children?: MindmapNode[]
  color?: string
  icon?: string
}

function parseMindmapContent(content: string): { root?: MindmapNode } {
  try {
    const data = JSON.parse(content)
    if (data.root) return data
    if (data.center || data.nodes) return { root: data }
    return { root: data }
  } catch {
    return { root: { label: "中心主题", children: [] } }
  }
}

const NODE_COLORS: Record<string, string> = {
  red: "bg-red-100 border-red-300 text-red-800",
  orange: "bg-orange-100 border-orange-300 text-orange-800",
  amber: "bg-amber-100 border-amber-300 text-amber-800",
  green: "bg-emerald-100 border-emerald-300 text-emerald-800",
  blue: "bg-blue-100 border-blue-300 text-blue-800",
  purple: "bg-purple-100 border-purple-300 text-purple-800",
  pink: "bg-pink-100 border-pink-300 text-pink-800",
}

function MindmapNodeView({ node, depth = 0 }: { node: MindmapNode; depth?: number }) {
  const colorClass = node.color ? NODE_COLORS[node.color] ?? "bg-slate-100 border-slate-300 text-slate-800" : "bg-slate-100 border-slate-300 text-slate-800"
  const isRoot = depth === 0

  return (
    <div className="relative">
      <div className={`rounded-xl border-2 px-4 py-2 ${colorClass} ${isRoot ? "font-black text-base" : "font-semibold text-sm"}`}>
        {node.label}
      </div>
      {node.children && node.children.length > 0 && (
        <div className={`mt-2 ml-6 pl-4 border-l-2 border-slate-200 space-y-2`}>
          {node.children.map((child, i) => (
            <MindmapNodeView key={child.id ?? i} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

export function MindmapRenderer({ resource }: MindmapRendererProps) {
  const { root } = parseMindmapContent(resource.content ?? "")

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {root ? (
        <MindmapNodeView node={root} />
      ) : (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          思维导图加载中...
        </div>
      )}
    </div>
  )
}
