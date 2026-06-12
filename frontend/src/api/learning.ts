import request from "@/utils/request"

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

export interface PagedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export const learningApi = {
  listCourses() {
    return request.get<{ data: Course[] }>("/api/learning/courses")
  },

  getCourse(courseId: number) {
    return request.get<{ data: Course }>(`/api/learning/courses/${courseId}`)
  },

  listTasks(params?: {
    page?: number
    page_size?: number
    course_id?: number
    status?: string
  }) {
    return request.get<{ data: PagedResponse<LearningTask> }>("/api/learning/tasks", { params })
  },

  getTask(taskId: number) {
    return request.get<{ data: LearningTask }>(`/api/learning/tasks/${taskId}`)
  },

  getLearningPath(courseId: number, profileId?: number) {
    return request.get<{ data: LearningPathGraph }>(`/api/learning/courses/${courseId}/learning-path`, {
      params: profileId ? { profile_id: profileId } : undefined,
    })
  }
}

export interface LearningPathNode {
  id: number
  kp_id: number
  name: string
  kp_name: string
  kp_code: string
  difficulty_level: number
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
