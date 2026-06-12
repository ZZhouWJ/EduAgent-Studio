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
  }
}
