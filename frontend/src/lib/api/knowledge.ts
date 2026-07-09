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

export interface KpChunkLink {
  link_id: number
  chunk_id: number
  kp_id: number
  kp_name: string
  course_id: number
  material_filename: string
  material_course_id: number
  match_method: 'bm25' | 'embedding' | 'llm_verify' | 'manual'
  relevance_score: number
  status: 'pending' | 'confirmed' | 'rejected'
  created_at: string
}

export interface ResourceEvidence {
  link_id: number
  resource_id: number
  resource_title: string
  resource_type: string
  kp_name: string
  material_filename: string
  quote_text: string
  usage_type: 'direct_quote' | 'paraphrase' | 'conceptual' | 'example'
  relevance_score: number
  verified_status: 'pending' | 'verified' | 'rejected' | 'replaced'
  created_at: string
}

export const knowledgeApi = {
  // 上传资料
  uploadMaterial(formData: FormData) {
    return client.post<Material>('/knowledge/materials', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 资料列表（返回 data.materials 数组）
  listMaterials(courseId?: number) {
    return client.get<{ materials: Material[] }>('/knowledge/materials', { params: { course_id: courseId } })
      .then(r => r.materials ?? [])
  },

  // 资料详情（返回 data）
  getMaterial(materialId: number) {
    return client.get<{ material: Material }>(`/knowledge/materials/${materialId}`)
      .then(r => r.material)
  },

  // 获取资料 chunks（返回 data）
  getMaterialChunks(materialId: number) {
    return client.get<MaterialChunk[]>(`/knowledge/materials/${materialId}/chunks`)
      .then(r => r ?? [])
  },

  // 解析资料
  parseMaterial(materialId: number) {
    return client.post<{ job_id: number; status: string }>(`/knowledge/materials/${materialId}/parse`)
  },

  // 检索
  search(query: string, courseId?: number, kpId?: number) {
    return client.get<SearchResult[]>('/knowledge/search', { params: { query, course_id: courseId, kp_id: kpId } })
  },

  // === 证据链路 API ===

  // 获取待审核的知识点-Chunk匹配
  getPendingKpChunkLinks(courseId?: number) {
    return client.get<KpChunkLink[]>('/knowledge/kp-chunk-links/pending', {
      params: courseId ? { course_id: courseId } : {}
    })
  },

  // 确认/拒绝知识点-Chunk匹配
  verifyKpChunkLink(linkId: number, status: 'confirmed' | 'rejected') {
    return client.put(`/knowledge/kp-chunk-links/${linkId}/verify`, { status })
  },

  // 获取资源的证据列表
  getResourceEvidence(resourceId: number) {
    return client.get<ResourceEvidence[]>('/knowledge/resource-evidence', {
      params: { resource_id: resourceId }
    })
  },

  // 确认/拒绝资源证据
  verifyResourceEvidence(linkId: number, status: 'verified' | 'rejected') {
    return client.put(`/knowledge/resource-evidence/${linkId}/verify`, { status })
  },
}
