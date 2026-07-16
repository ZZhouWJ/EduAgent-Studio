export {
  client,
  client as default,
  getToken,
  setToken,
  clearToken,
  ApiError,
  type ApiEnvelope,
} from './client'

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
export {
  resourcesApi,
  type LearningResource,
  type LearningResourceReview,
  type CompleteResourceReviewBody,
  type ResourceReviewResult,
} from './resources'

// Feedbacks
export { feedbackApi, type LearningFeedback } from './feedbacks'

// Agents
export {
  agentsApi,
  type AgentRequest,
  type WorkflowResult,
  type SaveResourceResponse,
} from './agents'

// Prompts
export {
  promptsApi,
  type PromptTemplate,
  type PromptVersion,
  type PromptTaskType,
  type CreateTemplateBody,
  type UpdateTemplateBody,
  type CreateVersionBody,
  type PromptRenderResult,
} from './prompts'

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

// Multimodal
export { multimodalApi, type ImageUnderstandResult } from './multimodal'

// Platform settings
export {
  platformSettingsApi,
  type GovernanceSettings,
  type GovernanceSettingsUpdate,
  type BudgetAlertSettings,
  type BudgetAlertSettingsUpdate,
} from './platform-settings'

// Statistics
export {
  statisticsApi,
  type ModelCallStats,
  type CostStats,
  type LearningOverview,
  type MasteryDist,
  type WeakKnowledgePoint,
  type ResourceTypeDist,
  type InvocationTrend,
  type ReviewRateByCourse,
  type CostDistribution,
} from './statistics'
