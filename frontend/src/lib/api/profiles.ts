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

// 对话消息结构
export interface DialogMessage {
  id: number
  role: 'student' | 'assistant'
  content: string
  created_at: string
  extraction?: ProfileExtraction
}

// 抽取结果结构
export interface ProfileExtraction {
  knowledge_base?: string
  current_level?: string
  weak_points?: string[]
  learning_goal?: string
  resource_preferences?: string[]
  cognitive_style?: string
  time_constraints?: string
  practice_level?: string
  motivation?: string
  error_prone_points?: string[]
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

  // 获取当前登录学生的画像
  getMyProfile() {
    return client.get<ProfileDetail>(`/profiles/me`)
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

  // 获取对话历史
  getDialogHistory(profileId: number) {
    return client.get<{ profile_id: number; messages: DialogMessage[]; total: number }>(`/profiles/${profileId}/dialog`)
      .then(res => res.messages)
  },

  // 发送对话消息
  sendDialogMessage(profileId: number, message: string) {
    return client.post<any>(`/profiles/${profileId}/dialog`, { message })
      .then(res => ({
        id: Date.now(),
        role: 'assistant' as const,
        content: res.reply || res.content || '',
        created_at: new Date().toISOString(),
        extraction: res.extracted,
      }))
  },

  // 应用抽取结果
  applyExtraction(profileId: number, extraction: ProfileExtraction) {
    return client.post<ProfileDetail>(`/profiles/${profileId}/apply-extraction`, extraction)
  },

  // 获取画像更新记录（学习反馈历史）
  getFeedbackHistory(profileId: number, limit = 20) {
    return client.get<Array<{
      feedback_id: number
      feedback_type: string
      feedback_type_label: string
      quiz_score: number | null
      self_mastery: number | null
      difficulty_rating: string | null
      content: string | null
      created_at: string
      resource_title: string | null
      course_name: string
    }>>(`/profiles/${profileId}/feedback-history`, { params: { limit } })
  },
}
