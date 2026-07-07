import client from '../api'

export interface Material {
  id: number
  course_id: number
  file_name: string
  file_type: string
  file_size: number
  status: 'pending' | 'parsing' | 'parsed' | 'failed'
  chunk_count: number
  page_count: number | null
  created_at: string
  updated_at: string
}

export interface MaterialChunk {
  id: number
  material_id: number
  page_num: number | null
  chunk_index: number
  content: string
  keywords: string[]
  knowledge_point_id: number | null
  knowledge_point_name: string | null
  created_at: string
}

export interface SearchResult {
  chunk_id: number
  material_id: number
  file_name: string
  page_num: number | null
  content: string
  score: number
  keywords: string[]
  knowledge_point_name: string | null
}

export const knowledgeApi = {
  // 上传资料
  uploadMaterial(formData: FormData) {
    return client.post<Material>('/knowledge/materials', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 资料列表
  listMaterials(courseId?: number) {
    return client.get<Material[]>('/knowledge/materials', { params: { course_id: courseId } })
  },

  // 资料详情
  getMaterial(materialId: number) {
    return client.get<Material>(`/knowledge/materials/${materialId}`)
  },

  // 获取资料 chunks
  getMaterialChunks(materialId: number) {
    return client.get<MaterialChunk[]>(`/knowledge/materials/${materialId}/chunks`)
  },

  // 解析资料
  parseMaterial(materialId: number) {
    return client.post<{ job_id: number; status: string }>(`/knowledge/materials/${materialId}/parse`)
  },

  // 检索
  search(query: string, courseId?: number, kpId?: number) {
    return client.get<SearchResult[]>('/knowledge/search', { params: { query, course_id: courseId, kp_id: kpId } })
  }
}
