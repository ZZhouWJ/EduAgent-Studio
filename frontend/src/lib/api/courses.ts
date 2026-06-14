import client from '../api'
import type { Course } from './learning'

export const coursesApi = {
  list() {
    return client.get<Course[]>('/learning/courses')
  },

  getById(course_id: number) {
    return client.get<Course>(`/learning/courses/${course_id}`)
  },
}
