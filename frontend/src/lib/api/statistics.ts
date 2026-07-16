import client from './client'

export interface StatisticsOverview {
  project_count: number
  active_project_count: number
  task_count: number
  pending_review_count: number
  invocation_count: number
  success_invocation_count: number
  failed_invocation_count: number
  artifact_count: number
  total_tokens: number
  total_cost: number
}

export interface ProjectStats {
  project_id: number
  project_name: string
  member_count: number
  task_count: number
  output_count: number
  approved_output_count: number
  artifact_count: number
  invocation_count: number
  total_cost: number
}

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

export interface ReviewStats {
  review_count: number
  approved_count: number
  rejected_count: number
  revision_required_count: number
  avg_accuracy_score: number
  avg_completeness_score: number
  avg_logic_score: number
  avg_format_score: number
  avg_usability_score: number
  avg_risk_score: number
  top_issue_tags: Array<{ tag_name: string; count: number; severity: string }>
}

export interface MemberContribution {
  user_id: number
  real_name: string
  project_count: number
  task_created_count: number
  task_assigned_count: number
  output_created_count: number
  review_count: number
  artifact_adopted_count: number
  invocation_count: number
}

export interface RecentActivity {
  log_id: number
  user_id: number
  real_name: string
  action_type: string
  target_type: string
  target_id: number
  action_desc: string
  created_at: string
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
  overview() {
    return client.get<StatisticsOverview>('/statistics/overview')
  },

  projects(params?: { project_id?: number }) {
    return client.get<ProjectStats[]>('/statistics/projects', { params })
  },

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

  reviews(params?: { project_id?: number }) {
    return client.get<ReviewStats>('/statistics/reviews', { params })
  },

  memberContributions(params?: { project_id?: number }) {
    return client.get<MemberContribution[]>('/statistics/member-contributions', { params })
  },

  recentActivities(params?: { project_id?: number; limit?: number }) {
    return client.get<RecentActivity[]>('/statistics/recent-activities', { params })
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
