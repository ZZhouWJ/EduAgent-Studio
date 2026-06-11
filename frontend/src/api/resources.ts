import request from "@/utils/request"

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
  list(params?: { page?: number; page_size?: number; course_id?: number; type?: string }) {
    return request.get<{ data: { items: LearningResource[]; total: number } }>(
      "/api/learning/resources",
      { params }
    )
  },
  getById(id: number) {
    return request.get<{ data: LearningResource }>(`/api/learning/resources/${id}`)
  }
}
