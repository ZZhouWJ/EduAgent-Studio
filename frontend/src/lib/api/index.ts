import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'

const TOKEN_KEY = 'eduagent_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export interface ApiEnvelope<T = unknown> {
  code: number
  message: string
  data: T
}

export class ApiError extends Error {
  code: number
  httpStatus?: number
  constructor(message: string, code: number, httpStatus?: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.httpStatus = httpStatus
  }
}

/**
 * Axios is unwrapped by the response interceptor below, so callers receive
 * the API payload directly instead of AxiosResponse<T>. Keep the transport
 * methods typed to match that runtime contract.
 */
type UnwrappedAxiosInstance = Omit<AxiosInstance, 'get' | 'delete' | 'head' | 'options' | 'post' | 'put' | 'patch'> & {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  head<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  options<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
}

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
}) as UnwrappedAxiosInstance

client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

client.interceptors.response.use(
  (response) => {
    const body = response.data as ApiEnvelope
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) {
        return body.data as any
      }
      return Promise.reject(new ApiError(body.message || '请求失败', body.code, response.status))
    }
    return response.data
  },
  (error: AxiosError<ApiEnvelope>) => {
    if (error.response) {
      const { status, data } = error.response
      const message = data?.message || error.message || '请求失败'
      if (status === 401) {
        clearToken()
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(new ApiError('登录已过期，请重新登录', 401, 401))
      }
      if (status === 403) return Promise.reject(new ApiError('无访问权限', 403, 403))
      if (status === 404) return Promise.reject(new ApiError('请求地址不存在', 404, 404))
      if (status >= 500) return Promise.reject(new ApiError('服务器错误，请稍后重试', status, status))
      return Promise.reject(new ApiError(message, data?.code ?? status, status))
    }
    return Promise.reject(new ApiError('网络错误，请检查网络连接', -1))
  },
)

// Re-export default client so `import client from '../api'` (used by sibling API
// modules) keeps working after this file replaced the standalone api.ts.
export { client as default }

// API client
export { authApi, type UserInfo, type LoginResponse } from '../auth-api'

// Users
export { usersApi, type User, type Role, type Permission } from './users'

// Profiles
export { profilesApi, type ProfileDetail } from './profiles'

// Learning
export {
  learningApi,
  type Course,
  type KnowledgePoint,
  type LearningTask,
  type LearningPathNode,
  type LearningPathEdge,
  type LearningPathSummary,
  type LearningPathGraph,
} from './learning'

// Courses
export { coursesApi, type CourseUpdateBody } from './courses'

// Resources
export { resourcesApi, type LearningResource } from './resources'

// Feedbacks
export { feedbackApi, type LearningFeedback } from './feedbacks'

// Agents
export {
  agentsApi,
  type AgentRequest,
  type WorkflowResult,
  type SaveResourceResponse,
} from './agents'

// Tasks
export {
  tasksApi,
  type TaskOutput,
  type TaskBranch,
  type OutputComment,
  type GenerationResult,
} from './tasks'

// Projects
export {
  projectsApi,
  type Project,
  type ProjectMember,
  type ProjectTask,
  type CreateProjectBody,
} from './projects'

// Artifacts
export { artifactsApi, type Artifact, type ArtifactDetail } from './artifacts'

// Prompts
export {
  promptsApi,
  type PromptTemplate,
  type PromptVersion,
  type PromptTaskType,
  type CreateTemplateBody,
  type UpdateTemplateBody,
  type CreateVersionBody,
} from './prompts'

// Reviews
export {
  reviewsApi,
  type ReviewRequest,
  type ReviewDetail,
  type IssueTag,
  type CompleteReviewBody,
} from './reviews'

// Invocations
export { invocationsApi, type Invocation, type InvocationDetail } from './invocations'

// Models
export {
  modelsApi,
  type ModelProvider,
  type AIModel,
  type TaskType,
  type ApiConfig,
} from './models'

// Logs
export { logsApi, type OperationLog, type LoginLog } from './logs'

// Knowledge
export { knowledgeApi, type Material, type MaterialChunk, type SearchResult } from './knowledge'

// Tutor
export { tutorApi, type TutorChatResponse, type Citation, type PracticeQuestion, type RecommendedResource, type ContentBlock, type IntentResult, type ResourceType } from './tutor'

// Statistics
export {
  statisticsApi,
  type StatisticsOverview,
  type ProjectStats,
  type ModelCallStats,
  type CostStats,
  type ReviewStats,
  type MemberContribution,
  type RecentActivity,
  type LearningOverview,
  type MasteryDist,
  type WeakKnowledgePoint,
  type ResourceTypeDist,
  type InvocationTrend,
  type ReviewRateByCourse,
  type CostDistribution,
} from './statistics'
