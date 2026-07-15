import client from './client'
import type { MasteryChange, RecommendedResource } from './learning'

export interface LearningFeedback {
  feedback_id: number
  profile_id: number
  student_name: string
  resource_id: number | null
  resource_title: string | null
  course_id: number
  course_name: string
  feedback_type: string
  content: string | null
  quiz_score: number | null
  self_mastery: number | null
  difficulty_rating: string | null
  created_at: string
}

export interface FeedbackResult {
  mastery_changes: MasteryChange[]
  next_resources: RecommendedResource[]
  path_adjustment?: string
}

export const feedbackApi = {
  list(params?: {
    page?: number
    page_size?: number
    course_id?: number
    feedback_type?: string
  }) {
    return client.get<{ items: LearningFeedback[]; total: number }>('/learning/feedbacks', { params })
  },

  submit(data: {
    course_id?: number
    resource_id?: number
    feedback_type?: string
    content?: string
    quiz_score?: number
    self_mastery?: number
    difficulty_rating?: string
  }) {
    return client.post<FeedbackResult>('/learning/feedbacks', data)
  },
}
