import client from './client'

export interface ModelCallStats {
  model_id: number
  model_name: string
  display_name: string
  provider_name: string
  call_count: number
  total_invocations: number
  success_count: number
  failed_count: number
  timeout_count: number
  blocked_count: number
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  avg_latency_ms: number
  success_rate: string
}

export interface CostStats {
  total_cost: number
  input_cost: number
  output_cost: number
  total_tokens: number
  currency: string
  cost_by_model: Array<{ model_id?: number; model_name: string; display_name?: string; provider_name?: string; total_cost: number; call_count?: number; input_cost?: number; output_cost?: number; total_tokens?: number; input_tokens?: number; output_tokens?: number }>
  cost_by_project: Array<{ project_id?: number; project_name: string; total_cost: number; task_count?: number }>
  cost_by_user: Array<{ user_id?: number; real_name: string; total_cost: number }>
  cost_trend: Array<{ date: string; call_count: number; total_tokens: number; total_cost: number }>
}

export interface LearningOverview {
  course_count: number
  student_count: number
  resource_count: number
  invocation_count: number
  avg_mastery: number
  review_pass_rate: number
  feedback_count: number
  active_tasks: number
}

export interface MasteryDist {
  range: string
  count: number
}

export interface WeakKnowledgePoint {
  kp_id: number
  kp_name: string
  course_id: number
  avg_mastery: number
}

export interface ResourceTypeDist {
  resource_type: string
  type_name: string
  count: number
}

export interface InvocationTrend {
  date: string
  invocation_count: number
  total_tokens: number
  total_cost: number
}

export interface ReviewRateByCourse {
  course_id: number
  course_name: string
  total: number
  approved: number
  pass_rate: number
}

export interface CostDistribution {
  agent: string
  agent_name: string
  tokens: number
  ratio: number
}

export interface PlatformOverview {
  invocation_count: number
  total_tokens: number
  total_cost: number
  today_invocations: number
  resource_count: number
  pending_resources: number
  student_count: number
  course_count: number
  avg_latency_ms: number
  success_rate: number
}

export interface CostByModel {
  model: string
  call_count: number
  total_tokens: number
  total_cost: number
}

export interface ResourceStats {
  total: number
  approved: number
  pending: number
  rejected: number
  draft: number
  pass_rate: number
}

export const statisticsApi = {
  modelCalls(params?: {
    project_id?: number
    date_from?: string
    date_to?: string
  }) {
    return client.get<ModelCallStats[]>('/statistics/model-calls', { params })
  },

  costs(params?: {
    project_id?: number
    model_id?: number
    date_from?: string
    date_to?: string
  }) {
    return client.get<CostStats>('/statistics/costs', { params })
  },

  learningOverview() {
    return client.get<LearningOverview>('/statistics/learning-overview')
  },

  masteryDistribution() {
    return client.get<MasteryDist[]>('/statistics/mastery-distribution')
  },

  weakKnowledgePoints(top_n = 10) {
    return client.get<WeakKnowledgePoint[]>('/statistics/weak-knowledge-points', {
      params: { top_n },
    })
  },

  resourceTypeDistribution() {
    return client.get<ResourceTypeDist[]>('/statistics/resource-type-distribution')
  },

  invocationTrend(days = 14) {
    return client.get<InvocationTrend[]>('/statistics/invocation-trend', {
      params: { days },
    })
  },

  reviewRateByCourse() {
    return client.get<ReviewRateByCourse[]>('/statistics/review-rate-by-course')
  },

  costDistribution() {
    return client.get<CostDistribution[]>('/statistics/cost-distribution')
  },

  // Module 8: 平台全局统计
  getPlatformOverview() {
    return client.get<PlatformOverview>('/statistics/platform')
  },

  getCostByModel() {
    return client.get<CostByModel[]>('/statistics/cost-by-model')
  },

  getResourceStats() {
    return client.get<ResourceStats>('/statistics/resources')
  },
}
