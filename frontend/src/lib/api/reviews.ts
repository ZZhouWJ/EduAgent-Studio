import client from './client'

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
  severity: 'low' | 'medium' | 'high'
}

export interface CompleteReviewBody {
  review_status: 'approved' | 'rejected' | 'revision_required'
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
  getPending(params?: {
    page?: number
    page_size?: number
    project_id?: number
  }) {
    return client.get<{ items: ReviewRequest[]; total: number }>('/reviews/pending', { params })
  },

  getById(request_id: number) {
    return client.get<ReviewDetail>(`/reviews/${request_id}`)
  },

  complete(request_id: number, data: CompleteReviewBody) {
    return client.post<{ review_id: number }>(`/reviews/${request_id}/complete`, data)
  },

  getIssueTags() {
    return client.get<IssueTag[]>('/issue-tags')
  },

  submitForReview(output_id: number, data?: { reviewer_id?: number; submit_note?: string }) {
    return client.post(`/outputs/${output_id}/submit-review`, data || {})
  },
}
