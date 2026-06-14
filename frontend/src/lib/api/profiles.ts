import client from '../api'

export interface ProfileDetail {
  profile_id: number
  student_id: number
  student_name: string
  course_id: number
  course_name: string
  learning_goal: string
  current_level: string
  weak_points: Array<{
    kp_id: number
    kp_name?: string
    name?: string
    mastery: number
    mastery_level?: number
    reason?: string
  }>
  preferences: string[]
  mastery_score: number
  last_updated: string
  student_no: string
  interests: string[]
  resource_preferences: string[]
  weekly_hours: number
  ai_suggestions: string
  strong_points: Array<{
    kp_id: number
    kp_name?: string
    name?: string
    mastery: number
    mastery_level?: number
  }>
  recent_tasks: Array<{
    task_id: number
    title: string
    status: string
    completed_at?: string
  }>
  recent_tests: Array<{
    test_id: number
    accuracy: number
    date: string
  }>
}

export const profilesApi = {
  list(params?: {
    page?: number
    page_size?: number
    course_id?: number
    keyword?: string
  }) {
    return client.get<{ items: ProfileDetail[]; total: number }>('/profiles/', { params })
  },

  getById(profile_id: number) {
    return client.get<ProfileDetail>(`/profiles/${profile_id}`)
  },

  update(profile_id: number, data: Record<string, unknown>) {
    return client.put(`/profiles/${profile_id}`, data)
  },

  updateMastery(
    profile_id: number,
    data: { kp_id: number; mastery: number; update_reason?: string }
  ) {
    return client.post(`/profiles/${profile_id}/mastery`, data)
  },
}
