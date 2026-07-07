import { LectureRenderer } from "./LectureRenderer"
import { QuizRenderer } from "./QuizRenderer"
import { CodeCaseRenderer } from "./CodeCaseRenderer"
import { PptRenderer } from "./PptRenderer"
import { VideoScriptRenderer } from "./VideoScriptRenderer"
import { MindmapRenderer } from "./MindmapRenderer"
import { ReviewRenderer } from "./ReviewRenderer"
import { TestRenderer } from "./TestRenderer"
import type { LearningResource } from "@/lib/api/resources"

export interface ResourceRendererProps {
  resource: LearningResource & {
    metadata?: {
      quality_score?: number
      revision_count?: number
      evidence_refs?: Array<{ source: string; page: number; content: string }>
    }
  }
}

// 中文资源类型 → 英文 key 映射
const TYPE_KEY_MAP: Record<string, string> = {
  "课程讲义": "lecture",
  "讲义": "lecture",
  "分层练习题": "quiz",
  "题库": "quiz",
  "练习": "quiz",
  "代码实操案例": "code_case",
  "代码案例": "code_case",
  "代码": "code_case",
  "PPT 大纲": "ppt",
  "PPT": "ppt",
  "PPT大纲": "ppt",
  "视频/动画脚本": "video_script",
  "视频脚本": "video_script",
  "视频": "video_script",
  "思维导图": "mindmap",
  "导图": "mindmap",
  "复习计划": "review",
  "复习": "review",
  "阶段测验": "test",
  "测验": "test",
  "实验报告": "experiment_report",
  "错题解析": "error_analysis",
  "学习卡片": "learning_card",
}

const RENDERER_MAP: Record<string, React.ComponentType<ResourceRendererProps>> = {
  lecture: LectureRenderer,
  quiz: QuizRenderer,
  code_case: CodeCaseRenderer,
  ppt: PptRenderer,
  video_script: VideoScriptRenderer,
  mindmap: MindmapRenderer,
  review: ReviewRenderer,
  test: TestRenderer,
  // Fallback for experiment_report, error_analysis, learning_card use lecture renderer
  experiment_report: LectureRenderer,
  error_analysis: LectureRenderer,
  learning_card: LectureRenderer,
}

function normalizeType(resourceType: string): string {
  if (!resourceType) return "lecture"
  // Check direct match first
  if (RENDERER_MAP[resourceType]) return resourceType
  // Check mapped type
  const mapped = TYPE_KEY_MAP[resourceType]
  if (mapped && RENDERER_MAP[mapped]) return mapped
  // Try to find partial match
  const lowerType = resourceType.toLowerCase()
  for (const key of Object.keys(RENDERER_MAP)) {
    if (lowerType.includes(key) || key.includes(lowerType)) return key
  }
  // Check mapped keys
  for (const [chinese, english] of Object.entries(TYPE_KEY_MAP)) {
    if (resourceType.includes(chinese) || chinese.includes(resourceType)) {
      return english
    }
  }
  return "lecture"
}

export function ResourceRenderer({ resource }: ResourceRendererProps) {
  const normalizedType = normalizeType(resource.resource_type ?? "")
  const Renderer = RENDERER_MAP[normalizedType] ?? LectureRenderer

  return <Renderer resource={resource} />
}

// Re-export individual renderers for direct use
export {
  LectureRenderer,
  QuizRenderer,
  CodeCaseRenderer,
  PptRenderer,
  VideoScriptRenderer,
  MindmapRenderer,
  ReviewRenderer,
  TestRenderer,
}
