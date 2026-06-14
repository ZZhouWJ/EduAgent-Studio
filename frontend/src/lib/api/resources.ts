import client from '../api'

export interface LearningResource {
  resource_id: number
  course_id: number
  course_name: string
  resource_title: string
  resource_type: string
  difficulty: string
  status: string
  created_at: string
}

export const resourcesApi = {
  list(params?: {
    page?: number
    page_size?: number
    course_id?: number
    type?: string
  }) {
    return client.get<{ items: LearningResource[]; total: number }>('/learning/resources', { params })
  },

  getById(resource_id: number) {
    return client.get<LearningResource>(`/learning/resources/${resource_id}`)
  },
}
