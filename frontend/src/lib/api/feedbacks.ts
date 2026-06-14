import client from '../api'

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
    resource_id?: number
    feedback_type?: string
    content?: string
    quiz_score?: number
    self_mastery?: number
    difficulty_rating?: string
  }) {
    return client.post('/learning/feedbacks', data)
  },
}
