import request from "@/utils/request"

export interface ReviewRequest {
  request_id: number
  output_id: number
  task_id: number
  project_id: number
  project_name: string
  task_title: string
  output_title: string
  version_no: number
  submitter_id: number
  submitter_username: string
  submitter_real_name: string
  reviewer_id?: number
  reviewer_username?: string
  reviewer_real_name?: string
  request_status: string
  submit_note?: string
  created_at: string
}

export interface ReviewDetail extends ReviewRequest {
  output_content: string
  output_status: string
}

export interface IssueTag {
  tag_id: number
  tag_name: string
  tag_code: string
  description: string
  severity: "low" | "medium" | "high"
}

export interface CompleteReviewBody {
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

export const reviewsApi = {
  getPending(params?: { page?: number; page_size?: number; project_id?: number }) {
    return request.get<{ data: { items: ReviewRequest[]; total: number; page: number; page_size: number } }>(
      "/api/reviews/pending",
      { params }
    )
  },

  getById(requestId: number) {
    return request.get<{ data: ReviewDetail }>(`/api/reviews/${requestId}`)
  },

  complete(requestId: number, data: CompleteReviewBody) {
    return request.post<{ data: { review_id: number } }>(`/api/reviews/${requestId}/complete`, data)
  },

  getIssueTags() {
    return request.get<{ data: IssueTag[] }>("/api/issue-tags")
  }
}
