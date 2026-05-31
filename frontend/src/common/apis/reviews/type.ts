/** 待审核列表项 */
export interface ReviewRequest {
  request_id: number
  output_id: number
  task_id: number
  project_id: number
  project_name?: string
  task_title?: string
  output_title?: string
  version_no?: string | number
  submitter_id: number
  submitter_username?: string
  submitter_real_name?: string
  reviewer_id: number | null
  reviewer_username?: string
  reviewer_real_name?: string
  request_status: "pending" | "approved" | "rejected" | "revision_required"
  submit_note?: string
  created_at: string
  updated_at?: string
}

/** 审核详情 */
export interface ReviewDetail extends ReviewRequest {
  content?: string
  submit_note?: string
  submitter_real_name?: string
  reviewer_real_name?: string
  reviewer_comment?: string
}

/** 完成审核请求体 */
export interface CompleteReviewRequestData {
  review_status: "approved" | "rejected" | "revision_required"
  accuracy_score?: number
  completeness_score?: number
  logic_score?: number
  format_score?: number
  usability_score?: number
  risk_score?: number
  review_comment?: string
  issue_tag_ids?: number[]
}

/** 问题标签 */
export interface IssueTag {
  tag_id: number
  tag_name: string
  description?: string
  color?: string
  created_at: string
}
