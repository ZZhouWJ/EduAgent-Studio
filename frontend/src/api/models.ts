import request from "@/utils/request"

export interface ModelProvider {
  provider_id: number
  provider_name: string
  provider_code: string
  base_url?: string
  website?: string
  description?: string
  status: string
}

export interface AIModel {
  model_id: number
  provider_id: number
  model_name: string
  display_name: string
  capability_tags?: string[]
  max_context?: number
  input_price: number
  output_price: number
  price_unit: string
  status: string
  created_at: string
  provider_name: string
  provider_code: string
}

export interface TaskType {
  task_type_id: number
  type_name: string
  type_code: string
  description?: string
  default_template_id?: number
  status: string
}

export const modelsApi = {
  getProviders(params?: { status?: string }) {
    return request.get<{ data: ModelProvider[] }>("/api/model-providers", { params })
  },

  getModels(params?: {
    provider_id?: number
    status?: string
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return request.get<{ data: { items: AIModel[]; total: number; page: number; page_size: number } }>(
      "/api/ai-models",
      { params }
    )
  },

  getTaskTypes() {
    return request.get<{ data: TaskType[] }>("/api/task-types")
  }
}
