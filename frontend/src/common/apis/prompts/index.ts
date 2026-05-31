import type * as Prompts from "./type"
import { request } from "@/http/axios"

/** 获取提示词模板列表 */
export function getTemplateListApi(params: Prompts.TemplateListParams = {}) {
  return request<ApiResponseData<Prompts.TemplateListResponse>>({
    url: "api/prompt-templates",
    method: "get",
    params
  })
}

/** 获取提示词模板详情 */
export function getTemplateDetailApi(templateId: number | string) {
  return request<ApiResponseData<Prompts.PromptTemplate>>({
    url: `api/prompt-templates/${templateId}`,
    method: "get"
  })
}

/** 获取提示词模板版本列表 */
export function getTemplateVersionsApi(templateId: number | string) {
  return request<ApiResponseData<Prompts.PromptVersion[]>>({
    url: `api/prompt-templates/${templateId}/versions`,
    method: "get"
  })
}

/** 获取任务类型列表 */
export function getTaskTypesApi() {
  return request<ApiResponseData<Array<{ task_type_id: number; type_name: string; type_code: string }>>>({
    url: "api/task-types",
    method: "get"
  })
}
