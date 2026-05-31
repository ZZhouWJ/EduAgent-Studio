/** 提示词模板相关类型定义 */

export interface PromptTemplate {
  template_id: number
  template_name: string
  task_type_id: number
  task_type_name?: string
  description?: string
  is_active?: boolean
  created_by: number
  creator_username?: string
  creator_real_name?: string
  created_at: string
  updated_at: string
  current_version_id?: number
  current_version_no?: string
  is_deleted?: number
}

export interface PromptVersion {
  prompt_version_id: number
  template_id: number
  version_no: string
  version_name?: string
  prompt_content: string
  status: "draft" | "active" | "archived"
  change_note?: string
  created_by: number
  creator_username?: string
  creator_real_name?: string
  created_at: string
  is_deleted?: number
}

export interface TemplateListParams {
  page?: number
  page_size?: number
  task_type_id?: number
  keyword?: string
}

export interface TemplateListResponse {
  items: PromptTemplate[]
  total: number
  page: number
  page_size: number
}
