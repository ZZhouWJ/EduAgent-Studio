import type * as Models from "./type"
import { request } from "@/http/axios"

/** 获取 AI 模型列表 */
export function getModelListApi(params: Models.ModelListParams = {}) {
  return request<ApiResponseData<Models.ModelListResponse>>({
    url: "api/ai-models",
    method: "get",
    params
  })
}

/** 获取模型供应商列表 */
export function getProviderListApi() {
  return request<ApiResponseData<Models.ModelProvider[]>>({
    url: "api/model-providers",
    method: "get"
  })
}
