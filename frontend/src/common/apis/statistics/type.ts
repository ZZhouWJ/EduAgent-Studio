/** 统计概览（后端真实字段） */
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

/** 项目统计项（后端真实字段） */
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

/** 模型调用统计项（后端真实字段） */
export interface ModelCallStats {
  model_id: number
  model_name: string
  display_name?: string
  provider_name?: string
  call_count: number
  total_invocations: number
  success_count: number
  failed_count: number
  timeout_count?: number
  blocked_count?: number
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  avg_latency_ms: number
  success_rate?: number
}

/** 成本统计（后端真实字段） */
export interface CostStats {
  total_cost: number
  input_cost: number
  output_cost: number
  total_tokens: number
  currency: string
  cost_by_model?: CostByModel[]
  cost_by_project?: CostByProject[]
  cost_by_user?: CostByUser[]
}

/** 按模型分组的成本明细 */
export interface CostByModel {
  model_id: number
  model_name: string
  display_name?: string
  total_cost: number
  total_tokens: number
}

/** 按项目分组的成本明细 */
export interface CostByProject {
  project_id: number
  project_name: string
  total_cost: number
  total_tokens: number
}

/** 按用户分组的成本明细 */
export interface CostByUser {
  user_id: number
  real_name?: string
  total_cost: number
  total_tokens: number
}

/** 审核质量统计（后端真实字段） */
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
  top_issue_tags?: IssueTagStat[]
}

/** 问题标签统计项 */
export interface IssueTagStat {
  tag_name: string
  tag_code?: string
  severity?: string
  tag_count: number
}

/** 成员贡献项（后端真实字段） */
export interface MemberContribution {
  user_id: number
  real_name?: string
  project_count: number
  task_created_count: number
  task_assigned_count: number
  output_created_count: number
  review_count: number
  artifact_adopted_count: number
  invocation_count: number
}

/** 最近活动项（后端真实字段） */
export interface RecentActivity {
  log_id: number
  user_id: number
  real_name?: string
  action_type: string
  target_type: string
  target_id: number
  action_desc: string
  created_at: string
}
