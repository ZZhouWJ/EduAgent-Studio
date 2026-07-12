import client from '../api'

export interface KnowledgePoint {
  id: number
  name: string
  mastery_avg: number
  difficulty: string
}

export interface Course {
  id: number
  name: string
  code: string
  description: string
  teacher: string
  semester: string
  status: string
  knowledge_point_count: number
  student_count: number
  task_count: number
  cover_color: string
  tags: string[]
  knowledge_points?: KnowledgePoint[]
}

export interface LearningTask {
  id: number
  course_id: number
  course_name: string
  title: string
  type: string
  status: string
  priority: string
  due_date: string
  description: string
  student_count: number
  completion_rate: number
}

export interface LearningPathNode {
  id: number
  kp_id: number
  name: string
  kp_name: string
  kp_code: string
  difficulty_level: string
  description: string
  estimated_hours: number
  mastery_level: number
  last_test_score: number | null
  last_test_date: string | null
  status_label: string
  color: string
  size: number
}

export interface LearningPathEdge {
  source: number
  target: number
  label: string
}

export interface LearningPathSummary {
  total: number
  mastered: number
  weak: number
  avg_mastery: number
  profile_id: number | null
  course_id: number
}

export interface LearningPathGraph {
  nodes: LearningPathNode[]
  edges: LearningPathEdge[]
  summary: LearningPathSummary
}

export interface CourseUpdateRequest {
  status: string
}

export interface RecommendedResource {
  resource_id: number
  title: string
  type: string
  reason: string
  difficulty?: number
  estimated_minutes?: number
}

export interface MasteryChange {
  kp_id: number
  kp_name: string
  before: number
  after: number
}

export interface FeedbackResult {
  mastery_changes: MasteryChange[]
  next_resources: RecommendedResource[]
  path_adjustment?: string
}

export const learningApi = {
  listCourses() {
    return client.get<Course[]>('/learning/courses')
  },

  getCourse(course_id: number) {
    return client.get<Course>(`/learning/courses/${course_id}`)
  },

  updateCourse(course_id: number, data: CourseUpdateRequest) {
    return client.put<{ code: number; message: string }>(`/learning/courses/${course_id}`, data)
  },

  listTasks(params?: {
    page?: number
    page_size?: number
    course_id?: number
    status?: string
  }) {
    return client.get<{ items: LearningTask[]; total: number }>('/learning/tasks', { params })
  },

  getTask(task_id: number) {
    return client.get<LearningTask>(`/learning/tasks/${task_id}`)
  },

  getLearningPath(course_id: number, profile_id?: number) {
    return client.get<LearningPathGraph>(`/learning/courses/${course_id}/learning-path`, {
      params: profile_id !== undefined ? { profile_id } : undefined,
    })
  },

  getRecommendedResources(profile_id: number, course_id: number) {
    return client.get<RecommendedResource[]>('/learning/recommend', {
      params: { profile_id, course_id },
    })
  },
}
