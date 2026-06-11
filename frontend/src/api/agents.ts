import request from "@/utils/request"

export interface AgentRequest {
  student_id: number
  course_id: number
  knowledge_point_ids: number[]
  resource_type: string
  difficulty: string
}

export interface AgentResult {
  diagnosis: {
    weak_points: Array<{ kp_id: number; name: string; mastery_level: number; reason: string }>
    learning_difficulties: string[]
    resource_needs: string[]
  }
  plan: {
    learning_path: Array<{ order: number; kp_name: string; estimated_time: string; resource_type: string; priority: string }>
    resource_combination: string[]
  }
  resource: {
    resource_id: string
    title: string
    type: string
    content: string
    knowledge_points: number[]
    difficulty: string
  }
  assessment: {
    accuracy_rate: number
    suggestions: string[]
  }
  teacher_review_suggestion: {
    quality_score: number
    quality_checks: Array<{ check: string; passed: boolean; note: string }>
    suggestions: string[]
    overall_comment: string
  }
}

export const agentsApi = {
  generate(data: AgentRequest) {
    return request.post<{ data: AgentResult }>("/api/agents/generate", data)
  },
  getAgents() {
    return request.get<{ data: Array<{ id: string; name: string; description: string; type: string }> }>(
      "/api/agents/list"
    )
  },
  saveResource(data: { result: AgentResult; title: string; course_id: number }) {
    return request.post("/api/agents/save-resource", data)
  }
}
