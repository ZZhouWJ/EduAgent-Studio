/** AI 模型相关类型定义 */

export interface AIModel {
  model_id: number
  model_name: string
  display_name: string
  provider_id?: number
  provider_name?: string
  model_type?: string
  status?: string
  description?: string
  is_deleted?: number
}

export interface ModelProvider {
  provider_id: number
  provider_name: string
  provider_type: string
  status?: string
  description?: string
  is_deleted?: number
}

export interface ModelListParams {
  page?: number
  page_size?: number
  keyword?: string
  provider_id?: number
  status?: string
}

export interface ModelListResponse {
  items: AIModel[]
  total: number
  page: number
  page_size: number
}
