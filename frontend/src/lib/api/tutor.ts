import client from '../api'

// 引用来源
export interface Citation {
  chunk_id: number
  content: string
  source: string
}

// 练习题
export interface PracticeQuestion {
  question: string
  answer: string
}

// 推荐资源
export interface RecommendedResource {
  resource_id: number
  title: string
  type: string
}

// Tutor 聊天响应
export interface TutorChatResponse {
  answer: string
  explanation_level: 'basic' | 'intermediate' | 'advanced'
  citations?: Citation[]
  practice_questions?: PracticeQuestion[]
  recommended_resources?: RecommendedResource[]
  session_id?: number
}

// 反馈请求
export interface FeedbackRequest {
  session_id: number
  helpful: boolean
  follow_up?: string
}

// 会话记录
export interface TutorSession {
  session_id: number
  profile_id: number
  course_id: number
  created_at: string
  last_message: string
  message_count: number
}

export const tutorApi = {
  chat(data: { profile_id: number; course_id: number; question: string }) {
    return client.post<TutorChatResponse>('/tutor/chat', data)
  },

  feedback(data: FeedbackRequest) {
    return client.post('/tutor/feedback', data)
  },

  getSessions(profileId: number) {
    return client.get<TutorSession[]>('/tutor/sessions', { params: { profile_id: profileId } })
  },
}