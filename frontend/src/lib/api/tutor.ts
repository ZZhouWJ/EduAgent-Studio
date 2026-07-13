import client, { getToken } from '../api'

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

// 内容块类型
export type ResourceType = 'lecture' | 'mindmap' | 'quiz' | 'code_case' | 'ppt' | 'video_script' | 'experiment_report' | 'error_analysis' | 'learning_card'

// 内容块
export interface ContentBlock {
  block_id: string
  block_type: ResourceType
  title: string
  content: string
  metadata: Record<string, any>
  quality_score?: number
  trustworthiness?: 'high' | 'medium' | 'low' | 'draft'
}

// 意图识别结果
export interface IntentResult {
  primary_intent: string
  resource_types: ResourceType[]
  kp_ids: number[]
  difficulty: 'basic' | 'intermediate' | 'advanced'
  reasoning: string
}

// Tutor 聊天响应
export interface TutorChatResponse {
  answer: string
  explanation_level: 'basic' | 'intermediate' | 'advanced'
  citations?: Citation[]
  content_blocks?: ContentBlock[]
  intent?: IntentResult
  practice_questions?: PracticeQuestion[]
  recommended_resources?: RecommendedResource[]
  profile_updates?: Record<string, number>
  session_id?: number
}

// SSE 事件类型
export type SSEEventType =
  | 'supervisor.started'
  | 'supervisor.tool_choice'
  | 'tool.started'
  | 'tool.completed'
  | 'tool.error'
  | 'supervisor.final'
  | 'supervisor.max_steps'
  | 'error'

// SSE 事件
export interface SSEEvent {
  type: SSEEventType
  [key: string]: any
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

  chatStream(
    data: { profile_id: number; course_id: number; question: string },
    callbacks: {
      onEvent: (event: SSEEvent) => void
      onFinal: (answer: string, contentBlocks: ContentBlock[], citations: Citation[]) => void
      onError: (error: string) => void
    }
  ): () => void {
    const token = getToken()
    const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
    const url = `${baseURL}/tutor/chat/stream`

    const controller = new AbortController()

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const reader = response.body!.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const dataStr = line.slice(6).trim()
            if (!dataStr) continue

            try {
              const event: SSEEvent = JSON.parse(dataStr)

              if (event.type === 'error') {
                callbacks.onError(event.message || '未知错误')
                return
              }

              if (event.type === 'supervisor.final') {
                callbacks.onFinal(
                  event.content || '',
                  event.content_blocks || [],
                  event.citations || []
                )
                return
              }

              if (event.type === 'supervisor.max_steps') {
                callbacks.onFinal(event.content || '（处理超时）', [], [])
                return
              }

              callbacks.onEvent(event)
            } catch {
              // ignore parse errors
            }
          }
        }
      })
      .catch((e) => {
        if (e.name !== 'AbortError') {
          callbacks.onError(e.message || '网络错误')
        }
      })

    return () => controller.abort()
  },

  getSuggestions(courseId: number, profileId?: number) {
    return client.get<{ suggestions: string[] }>('/tutor/suggestions', {
      params: { course_id: courseId, ...(profileId ? { profile_id: profileId } : {}) },
    })
  },

  feedback(data: FeedbackRequest) {
    return client.post('/tutor/feedback', data)
  },

  getSessions(profileId: number) {
    return client.get<TutorSession[]>('/tutor/sessions', { params: { profile_id: profileId } })
  },
}
