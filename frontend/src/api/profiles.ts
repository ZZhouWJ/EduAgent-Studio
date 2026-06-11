import request from "@/utils/request"

export interface StudentProfile {
  profile_id: number
  student_id: number
  student_name: string
  course_id: number
  course_name: string
  learning_goal: string
  current_level: string
  weak_points: string[]
  preferences: string[]
  mastery_score: number
  last_updated: string
}

export interface ProfileDetail {
  profile_id: number
  student_id: number
  student_name: string
  student_no: string
  learning_goal: string
  current_level: string
  interests: string[]
  resource_preferences: string[]
  weekly_hours: number
  weak_points: Array<{ kp_id: number; kp_name: string; mastery: number; reason: string }>
  strong_points: Array<{ kp_id: number; kp_name: string; mastery: number }>
  recent_tasks: Array<{ task_id: number; title: string; status: string; completed_at: string }>
  recent_tests: Array<{ test_id: number; accuracy: number; date: string }>
  ai_suggestions: string
}

export const profilesApi = {
  list(params?: { page?: number; page_size?: number; course_id?: number; keyword?: string }) {
    return request.get<{ data: { items: StudentProfile[]; total: number } }>(
      "/api/profiles",
      { params }
    )
  },
  getById(profileId: number) {
    return request.get<{ data: ProfileDetail }>(`/api/profiles/${profileId}`)
  },
  update(profileId: number, data: Partial<ProfileDetail>) {
    return request.put(`/api/profiles/${profileId}`, data)
  },
  updateMastery(profileId: number, data: { kp_id: number; mastery: number }) {
    return request.post(`/api/profiles/${profileId}/mastery`, data)
  }
}
