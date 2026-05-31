/** 统计概览 */
export interface StatisticsOverview {
  total_projects: number
  active_projects: number
  total_tasks: number
  completed_tasks: number
  total_outputs: number
  approved_outputs: number
  total_invocations: number
  total_cost: number
  total_members: number
}

/** 项目统计项 */
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

/** 模型调用统计项 */
export interface ModelCallStats {
  model_id: number
  model_name: string
  display_name?: string
  call_count: number
  total_input_tokens: number
  total_output_tokens: number
  total_cost: number
  avg_latency_ms: number
}

/** 成本统计 */
export interface CostStats {
  total_input_cost: number
  total_output_cost: number
  total_cost: number
  currency: string
  period_input_cost: number
  period_output_cost: number
  period_total_cost: number
}

/** 审核质量统计 */
export interface ReviewStats {
  total_reviews: number
  approved_count: number
  rejected_count: number
  revision_required_count: number
  avg_accuracy_score: number
  avg_completeness_score: number
  avg_logic_score: number
  avg_format_score: number
  avg_usability_score: number
  avg_risk_score: number
}

/** 成员贡献项 */
export interface MemberContribution {
  user_id: number
  username: string
  real_name?: string
  project_count: number
  task_count: number
  output_count: number
  approved_output_count: number
  invocation_count: number
  total_cost: number
}

/** 最近活动项 */
export interface RecentActivity {
  log_id: number
  user_id: number
  username: string
  real_name?: string
  action_type: string
  action_desc: string
  target_type: string
  target_id: number
  target_name?: string
  project_id: number
  project_name?: string
  created_at: string
}
