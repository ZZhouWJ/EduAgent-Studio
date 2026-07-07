import type { LearningResource } from "@/lib/api/resources"

interface CodeCaseRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

interface CodeBlock {
  language?: string
  code: string
}

interface Step {
  order: number
  title: string
  description: string
}

interface CodeCaseData {
  title?: string
  description?: string
  code_blocks?: CodeBlock[]
  steps?: Step[]
  output?: string
}

function parseCodeCaseContent(content: string): CodeCaseData {
  try {
    return JSON.parse(content)
  } catch {
    return { description: content }
  }
}

function CodeBlock({ block }: { block: CodeBlock }) {
  return (
    <div className="rounded-xl overflow-hidden border border-slate-200 my-3">
      {block.language && (
        <div className="bg-slate-800 text-slate-400 text-xs px-3 py-1.5 font-mono">
          {block.language}
        </div>
      )}
      <pre className="bg-[#1e1e1e] p-4 overflow-x-auto">
        <code className="text-sm text-slate-100 font-mono leading-relaxed">{block.code}</code>
      </pre>
    </div>
  )
}

function StepsList({ steps }: { steps: Step[] }) {
  return (
    <div className="mt-4 space-y-2">
      <h4 className="text-sm font-bold text-slate-700">运行步骤</h4>
      {steps.map((step, i) => (
        <div key={i} className="flex gap-3">
          <div className="flex h-6 w-6 shrink-0 place-items-center rounded-full bg-blue-100 text-xs font-black text-blue-700">
            {step.order ?? i + 1}
          </div>
          <div className="flex-1 rounded-lg bg-slate-50 p-3">
            <div className="text-sm font-bold text-slate-800">{step.title}</div>
            <div className="mt-1 text-xs text-slate-600 leading-relaxed">{step.description}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function CodeCaseRenderer({ resource }: CodeCaseRendererProps) {
  const data = parseCodeCaseContent(resource.content ?? "")

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {resource.metadata?.quality_score && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">
            质量分 {resource.metadata.quality_score.toFixed(1)}
          </span>
        )}
      </div>

      {data.title && <h3 className="text-lg font-black text-slate-900">{data.title}</h3>}
      {data.description && (
        <p className="text-sm text-slate-600 leading-relaxed">{data.description}</p>
      )}

      {data.code_blocks && data.code_blocks.length > 0 && (
        <div>
          <h4 className="text-sm font-bold text-slate-700">代码</h4>
          {data.code_blocks.map((block, i) => (
            <CodeBlock key={i} block={block} />
          ))}
        </div>
      )}

      {data.steps && data.steps.length > 0 && <StepsList steps={data.steps} />}

      {data.output && (
        <div className="mt-4">
          <h4 className="text-sm font-bold text-slate-700 mb-2">示例输出</h4>
          <pre className="rounded-xl bg-slate-900 p-4 text-sm text-emerald-400 font-mono overflow-x-auto">
            {data.output}
          </pre>
        </div>
      )}
    </div>
  )
}
