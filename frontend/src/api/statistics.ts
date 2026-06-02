import request from "@/utils/request"

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
  cost_by_model: Array<{ model_name: string; cost: number }>
  cost_by_project: Array<{ project_name: string; cost: number }>
  cost_by_user: Array<{ real_name: string; cost: number }>
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

export const statisticsApi = {
  overview() {
    return request.get<{ data: StatisticsOverview }>("/api/statistics/overview")
  },

  projects(params?: { project_id?: number }) {
    return request.get<{ data: ProjectStats[] }>("/api/statistics/projects", { params })
  },

  modelCalls(params?: { project_id?: number; date_from?: string; date_to?: string }) {
    return request.get<{ data: ModelCallStats[] }>("/api/statistics/model-calls", { params })
  },

  costs(params?: { project_id?: number; date_from?: string; date_to?: string }) {
    return request.get<{ data: CostStats }>("/api/statistics/costs", { params })
  },

  reviews(params?: { project_id?: number }) {
    return request.get<{ data: ReviewStats }>("/api/statistics/reviews", { params })
  },

  memberContributions(params?: { project_id?: number }) {
    return request.get<{ data: MemberContribution[] }>("/api/statistics/member-contributions", { params })
  },

  recentActivities(params?: { project_id?: number; limit?: number }) {
    return request.get<{ data: RecentActivity[] }>("/api/statistics/recent-activities", { params })
  }
}
