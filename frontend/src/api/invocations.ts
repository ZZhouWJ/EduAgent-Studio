import request from "@/utils/request"

// ============================================================================
// API 文档
// ============================================================================
// GET /api/invocations
// GET /api/invocations/{invocation_id}

// ============================================================================
// 类型定义
// ============================================================================

export interface Invocation {
  invocation_id: number
  model_id: number
  model_name: string
  display_name: string
  provider_name: string
  project_id: number
  project_name: string
  task_id: number
  task_title: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  latency_ms: number
  status: string
  error_message?: string
  ip_address?: string
  created_at: string
}

// ============================================================================
// API
// ============================================================================

export interface InvocationDetail extends Invocation {
  invoker_real_name?: string
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
    return request.get<{ data: { items: Invocation[]; total: number; page: number; page_size: number } }>(
      "/api/invocations",
      { params }
    )
  },

  getInvocationById(invocationId: number) {
    return request.get<{ data: InvocationDetail }>(`/api/invocations/${invocationId}`)
  }
}
