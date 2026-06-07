import request from "@/utils/request"

export interface CostSummary {
  total_cost: number
  monthly_cost: number
  total_invocations: number
  avg_cost_per_invocation: number
}

export interface ModelCostStat {
  model_id: number
  model_name: string
  display_name: string
  provider_name: string
  call_count: number
  input_tokens: number
  output_tokens: number
  input_cost: number
  output_cost: number
  total_cost: number
  total_tokens: number
}

export interface ProjectCostStat {
  project_id: number
  project_name: string
  call_count: number
  input_tokens: number
  output_tokens: number
  total_cost: number
  avg_cost_per_call: number
}

export interface CostStatisticsData {
  total_cost: number
  input_cost: number
  output_cost: number
  total_tokens: number
  currency: string
  cost_by_model: ModelCostStat[]
  cost_by_project: ProjectCostStat[]
  cost_by_user?: Array<{
    user_id: number
    real_name: string
    total_cost: number
    total_tokens: number
  }>
}

export interface GetCostsParams {
  date_from?: string
  date_to?: string
  project_id?: number
  model_id?: number
}

export const costsApi = {
  getCosts(params?: GetCostsParams) {
    return request.get<{ data: CostStatisticsData }>("/api/statistics/costs", { params })
  }
}
