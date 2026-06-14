import client from '../api'

export interface AgentRequest {
  student_id: number
  course_id: number
  knowledge_point_ids: number[]
  resource_type: string
  difficulty: string
}

export interface WorkflowResult {
  diagnosis: {
    diagnosis_id: string
    weak_points: Array<{
      kp_id: number
      name: string
      mastery_level: number
      reason: string
    }>
    strength_points: Array<{
      kp_id: number
      name: string
      mastery_level: number
    }>
    learning_difficulties: string[]
    resource_needs: string[]
    suggested_difficulty: string
  }
  plan: {
    plan_id: string
    learning_path: Array<{
      order: number
      kp_id: number
      kp_name: string
      estimated_time: string
      resource_type: string
      priority: string
    }>
    resource_combination: string[]
    learning_sequence: string
    estimated_total_time: string
  }
  resource: {
    resource_id: string
    title: string
    type: string
    content: string
    knowledge_points: number[]
    difficulty: string
    target_audience: string
    estimated_learning_time: string
    generation_metadata: { agent: string; model: string }
  }
  assessment: {
    assessment_id: string
    test_results: {
      total_questions: number
      correct_answers: number
      accuracy_rate: number
    }
    mastery_updates: Array<{
      kp_id: number
      old_mastery: number
      new_mastery: number
      change_reason: string
    }>
    feedback: string
    suggestions: string[]
    next_resource_recommendation: string
  }
  teacher_review_suggestion: {
    review_id: string
    quality_score: number
    quality_checks: Array<{ check: string; passed: boolean; note: string }>
    risk_alerts: Array<{ level: string; message: string }>
    suggestions: string[]
    overall_comment: string
  }
  metadata: {
    total_duration_ms: number
    step_history: Array<{
      step: string
      status: string
      timestamp: string
      error?: string
      duration_ms: number
    }>
    quality_score: number
    revision_count: number
  }
}

export interface SaveResourceResponse {
  resource_id: string
  title: string
  course_id: number
  type: string
  content: string
  knowledge_points: number[]
  difficulty: string
  status: string
  created_at: string
  storage_path: string
  storage_url: string
  file_size: number
}

export const agentsApi = {
  listAgents() {
    return client.get<Array<{ id: string; name: string; description: string; type: string }>>(
      '/agents/list'
    )
  },

  generate(data: AgentRequest) {
    return client.post<WorkflowResult>('/agents/generate', data)
  },

  generateStream(data: AgentRequest) {
    return client.post('/agents/generate/stream', data, {
      responseType: 'stream',
    })
  },

  getWorkflowStatus(run_id: string) {
    return client.get<WorkflowResult>(`/agents/workflow/${run_id}`)
  },

  saveResource(data: { result: WorkflowResult; title: string; course_id: number }) {
    return client.post<SaveResourceResponse>('/agents/save-resource', data)
  },
}
