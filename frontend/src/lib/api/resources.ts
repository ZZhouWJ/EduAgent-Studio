import client from './client'

export interface LearningResource {
  resource_id: number
  course_id: number
  course_name: string
  resource_title: string
  resource_type: string
  difficulty: string
  status: string
  content?: string
  target_kp_ids?: number[]
  target_kp_names?: string[]
  generation_model?: string
  generation_agent?: string
  review_submitted_at?: string | null
  reviewer_comment?: string | null
  review_history?: LearningResourceReview[]
  created_at: string
  updated_at?: string
}

export interface LearningResourceReview {
  review_id: number
  review_status: 'pending' | 'approved' | 'rejected'
  submit_note: string | null
  accuracy_score: number | null
  completeness_score: number | null
  logic_score: number | null
  format_score: number | null
  usability_score: number | null
  review_comment: string | null
  submitter_name: string
  reviewer_name: string | null
  submitted_at: string
  reviewed_at: string | null
}

export interface CompleteResourceReviewBody {
  decision: 'approved' | 'rejected'
  accuracy_score?: number
  completeness_score?: number
  logic_score?: number
  format_score?: number
  usability_score?: number
  review_comment?: string
}

export interface ResourceReviewResult {
  resource_id: number
  review_id: number
  status: 'pending_review' | 'approved' | 'rejected'
  course_id: number
}

export const resourcesApi = {
  list(params?: {
    page?: number
    page_size?: number
    course_id?: number
    type?: string
    kp_id?: number
    status?: string
  }) {
    return client.get<{ items: LearningResource[]; total: number }>('/learning/resources', { params })
  },

  getById(resource_id: number) {
    return client.get<LearningResource>(`/learning/resources/${resource_id}`)
  },

  submitReview(resource_id: number, submit_note?: string) {
    return client.post<ResourceReviewResult>(
      `/learning/resources/${resource_id}/submit-review`,
      { submit_note: submit_note?.trim() || null },
    )
  },

  completeReview(resource_id: number, body: CompleteResourceReviewBody) {
    return client.post<ResourceReviewResult>(
      `/learning/resources/${resource_id}/review`,
      body,
    )
  },
}
