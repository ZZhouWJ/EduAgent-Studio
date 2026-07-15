import client from './client'

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
  capability_tags?: string
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

export interface ApiConfig {
  api_config_id: number
  provider_id: number
  config_name: string
  key_mask: string
  key_version?: number
  status: string
  quota_limit: number
  used_quota: number
  created_at: string
  provider_name?: string
}

export const modelsApi = {
  getProviders(params?: { status?: string }) {
    return client.get<ModelProvider[]>('/model-providers', { params })
  },

  createProvider(data: {
    provider_name: string
    provider_code: string
    base_url: string
    website?: string
    description?: string
  }) {
    return client.post<ModelProvider>('/model-providers', data)
  },

  getModels(params?: {
    provider_id?: number
    status?: string
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return client.get<{ items: AIModel[]; total: number }>('/ai-models', { params })
  },

  createModel(data: {
    provider_id: number
    model_name: string
    display_name: string
    capability_tags?: string
    max_context?: number
    input_price?: number
    output_price?: number
    price_unit?: string
    status?: string
  }) {
    return client.post<AIModel>('/ai-models', data)
  },

  getApiConfigs(params?: {
    provider_id?: number
    page?: number
    page_size?: number
  }) {
    return client.get<{ items: ApiConfig[]; total: number }>('/api-configs', { params })
  },

  createApiConfig(data: {
    provider_id: number
    config_name: string
    api_key: string
    quota_limit: number
  }) {
    return client.post<ApiConfig>('/api-configs', data)
  },
}
