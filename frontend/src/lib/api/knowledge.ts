import client from './client'

export interface Material {
  material_id: number
  course_id: number
  filename: string
  file_type: string
  status: 'pending' | 'parsing' | 'parsed' | 'failed'
  error_message?: string | null
  total_chunks: number
  material_version: number
  total_chars: number
  last_reparse_at?: string | null
  created_by?: number
  creator_name?: string
  created_at: string | null
  updated_at: string | null
}

export interface MaterialChunk {
  chunk_id: number
  material_id: number
  course_id: number
  kp_id: number | null
  title: string | null
  source_page: number | null
  source_paragraph: number | null
  bm25_terms: string | null
  chunk_index: number
  content: string
  created_at: string | null
}

interface MaterialDetail {
  material: Material
  chunks: MaterialChunk[]
}

export interface SearchResult {
  chunk_id: number
  material_id: number
  title: string | null
  page_num: number | null
  content: string
  relative_score: number
  keywords: string[]
}

interface SearchChunk extends MaterialChunk {
  bm25_score: number
}

interface SearchResponse {
  query: string
  total: number
  chunks: SearchChunk[]
}

function parseSearchTerms(value: string | null): string[] {
  if (!value) return []
  return value.split(/[,，\s]+/).map(term => term.trim()).filter(Boolean)
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
    return client.post<Pick<Material, 'material_id' | 'filename' | 'file_type' | 'status'>>('/knowledge/materials', formData, {
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
    return client.get<MaterialDetail>(`/knowledge/materials/${materialId}`)
      .then(r => r.material)
  },

  // 资料详情接口同时返回 chunks
  getMaterialChunks(materialId: number) {
    return client.get<MaterialDetail>(`/knowledge/materials/${materialId}`)
      .then(r => r.chunks ?? [])
  },

  // 解析资料
  parseMaterial(materialId: number) {
    return client.post<{ job_id: number; status: string }>(`/knowledge/materials/${materialId}/parse`)
  },

  // 检索
  search(query: string, courseId?: number, kpId?: number) {
    return client.get<SearchResponse>('/knowledge/search', { params: { query, course_id: courseId, kp_id: kpId } })
      .then(response => {
        const chunks = response.chunks ?? []
        const maxScore = Math.max(...chunks.map(chunk => chunk.bm25_score), 0)

        return chunks.map<SearchResult>(chunk => ({
          chunk_id: chunk.chunk_id,
          material_id: chunk.material_id,
          title: chunk.title,
          page_num: chunk.source_page,
          content: chunk.content,
          relative_score: maxScore > 0 ? chunk.bm25_score / maxScore : 0,
          keywords: parseSearchTerms(chunk.bm25_terms),
        }))
      })
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
