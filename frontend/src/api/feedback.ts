import request from "@/utils/request"

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
  list(params?: { page?: number; page_size?: number; course_id?: number; feedback_type?: string }) {
    return request.get<{ data: { items: LearningFeedback[]; total: number } }>(
      "/api/learning/feedbacks",
      { params }
    )
  },
  submit(data: {
    resource_id?: number
    feedback_type: string
    content?: string
    quiz_score?: number
    self_mastery?: number
    difficulty_rating?: string
  }) {
    return request.post("/api/learning/feedbacks", data)
  },
  updateMastery(profile_id: number, kp_id: number, mastery: number) {
    return request.post(`/api/profiles/${profile_id}/mastery`, { kp_id, mastery })
  }
}
