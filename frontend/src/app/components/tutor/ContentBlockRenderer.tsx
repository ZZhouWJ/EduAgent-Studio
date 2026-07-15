import ReactMarkdown from "react-markdown"
import type { ContentBlock } from "@/lib/api/tutor"
import { MindmapRenderer } from "../resource/MindmapRenderer"
import { CodeCaseRenderer } from "../resource/CodeCaseRenderer"
import { QuizRenderer } from "../resource/QuizRenderer"
import { ResourceRenderer } from "../resource/ResourceRenderer"

interface ContentBlockRendererProps {
  block: ContentBlock
  expanded?: boolean
  /** 嵌入模式：不显示 block 类型 badge，更融入正文 */
  embedded?: boolean
}

// 将 ContentBlock 适配为 ResourceRenderer 期望的格式
function adaptToResource(block: ContentBlock): any {
  return {
    resource_id: block.block_id,
    resource_title: block.title,
    resource_type: block.block_type,
    content: block.content,
    metadata: {
      quality_score: block.quality_score,
      trustworthiness: block.trustworthiness,
    },
  }
}

// 思维导图类型的内容块
function MindmapBlock({ block }: { block: ContentBlock }) {
  let mindmapData: any = null

  // 尝试解析 content 为 JSON（MindmapRenderer 期望的结构）
  try {
    mindmapData = JSON.parse(block.content)
  } catch {
    // 如果不是 JSON，尝试解析 Markdown 树形结构
    // 格式如 "## SQL\n- JOIN\n  - INNER\n  - LEFT"
    mindmapData = parseMarkdownTree(block.content)
  }

  if (mindmapData) {
    return <MindmapRenderer resource={{ ...adaptToResource(block), content: JSON.stringify(mindmapData) }} />
  }

  // 降级：用 Markdown 渲染
  return (
    <div className="rounded-xl border border-purple-100 bg-purple-50 p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-bold text-purple-700">{block.title}</div>
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown>{block.content}</ReactMarkdown>
      </div>
    </div>
  )
}

// 简单解析 Markdown 树形结构为 JSON
interface MindmapNode {
  label: string
  children: MindmapNode[]
}

function parseMarkdownTree(markdown: string): MindmapNode | null {
  const lines = markdown.split("\n").filter((l) => l.trim())
  if (lines.length === 0) return null

  const root: MindmapNode = { label: "根节点", children: [] }
  const stack = [{ node: root, indent: -1 }]

  for (const line of lines) {
    const indent = line.search(/\S/)
    const text = line.trim().replace(/^#+\s*/, "").replace(/^[-*]\s*/, "")
    const node: MindmapNode = { label: text, children: [] }

    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) {
      stack.pop()
    }
    stack[stack.length - 1].node.children.push(node)
    stack.push({ node, indent })
  }

  return root.children[0] || root
}

// 练习题类型的内容块
function QuizBlock({ block }: { block: ContentBlock }) {
  try {
    JSON.parse(block.content)
  } catch {
    // 降级渲染为 Markdown
    return (
      <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
        <div className="mb-2 flex items-center gap-2 text-sm font-bold text-emerald-700">{block.title}</div>
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{block.content}</ReactMarkdown>
        </div>
      </div>
    )
  }

  return <QuizRenderer resource={adaptToResource(block)} />
}

// 代码案例类型的内容块
function CodeCaseBlock({ block }: { block: ContentBlock }) {
  return <CodeCaseRenderer resource={adaptToResource(block)} />
}

// PPT 类型
function PptBlock({ block }: { block: ContentBlock }) {
  return <ResourceRenderer resource={adaptToResource(block)} />
}

// 视频脚本类型
function VideoScriptBlock({ block }: { block: ContentBlock }) {
  return (
    <div className="rounded-xl border border-cyan-100 bg-cyan-50 p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-bold text-cyan-700">{block.title}</div>
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown>{block.content}</ReactMarkdown>
      </div>
    </div>
  )
}

// 通用的 Markdown 类型块
function GenericBlock({ block }: { block: ContentBlock }) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-bold text-slate-700">{block.title}</span>
        {block.quality_score != null && (
          <span className={`text-xs font-bold ${block.quality_score >= 0.7 ? "text-emerald-600" : "text-orange-600"}`}>
            质量 {Math.round(block.quality_score * 100)}%
          </span>
        )}
      </div>
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown>{block.content}</ReactMarkdown>
      </div>
    </div>
  )
}

export function ContentBlockRenderer({ block, embedded = false }: ContentBlockRendererProps) {
  const blockClass = `content-block content-block-${block.block_type} ${embedded ? "embedded" : ""}`

  const content = (() => {
    switch (block.block_type) {
      case "mindmap":
        return <MindmapBlock block={block} />
      case "quiz":
        return <QuizBlock block={block} />
      case "code_case":
        return <CodeCaseBlock block={block} />
      case "ppt":
        return <PptBlock block={block} />
      case "video_script":
        return <VideoScriptBlock block={block} />
      default:
        return <GenericBlock block={block} />
    }
  })()

  return (
    <div className={blockClass}>
      {/* 区块标签 — 嵌入模式下隐藏 */}
      {!embedded && (
        <div className="mb-2 flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-bold ${
              block.block_type === "mindmap"
                ? "bg-purple-100 text-purple-700"
                : block.block_type === "quiz"
                ? "bg-emerald-100 text-emerald-700"
                : block.block_type === "code_case"
                ? "bg-blue-100 text-blue-700"
                : block.block_type === "ppt"
                ? "bg-orange-100 text-orange-700"
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
              ? "📊 PPT大纲"
              : block.block_type === "video_script"
              ? "🎬 视频脚本"
              : block.title}
          </span>
          {block.trustworthiness === "high" && (
            <span className="text-xs text-emerald-600">✓ 已验证</span>
          )}
          {block.trustworthiness === "draft" && (
            <span className="text-xs text-orange-600">⚠ 草稿</span>
          )}
        </div>
      )}
      {content}
    </div>
  )
}
