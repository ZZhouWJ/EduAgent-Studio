import client from '../api'

export interface Invocation {
  invocation_id: number
  model_id?: number
  model_name?: string
  model_display_name?: string
  provider_name?: string
  project_id?: number
  task_id?: number
  task_title?: string
  branch_id?: number
  branch_name?: string
  created_by?: number
  creator_username?: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  latency_ms: number
  status: string
  error_message?: string
  ip_address?: string
  created_at: string
}

export interface InvocationDetail extends Invocation {
  creator_real_name?: string
  input_text?: string
  output_text?: string
  cost?: number
  model_display_name?: string
  model_info?: {
    display_name?: string
    model_name?: string
    provider_name?: string
    input_price?: number
    output_price?: number
    price_unit?: string
  }
}

export const invocationsApi = {
  getInvocations(params?: {
    page?: number
    page_size?: number
    project_id?: number
    task_id?: number
    model_id?: number
    status?: string
  }) {
    return client.get<{ items: Invocation[]; total: number }>('/invocations', { params })
  },

  getInvocationById(invocation_id: number) {
    return client.get<InvocationDetail>(`/invocations/${invocation_id}`)
  },
}
