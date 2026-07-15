import client from './client'
import type { Course } from './learning'

export interface CourseUpdateBody {
  status: string
}

export const coursesApi = {
  list() {
    return client.get<Course[]>('/learning/courses')
  },

  getById(course_id: number) {
    return client.get<Course>(`/learning/courses/${course_id}`)
  },

  updateCourse(course_id: number, data: CourseUpdateBody) {
    return client.put(`/learning/courses/${course_id}`, data)
  },
}
