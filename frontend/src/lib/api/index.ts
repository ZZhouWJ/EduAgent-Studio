// API client
export { default as client } from '../api'
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
export { coursesApi } from './courses'

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
