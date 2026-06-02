import request from "@/utils/request"

export interface PromptTemplate {
  template_id: number
  template_name: string
  task_type_id: number
  type_name: string
  type_code: string
  current_version_no: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PromptVersion {
  version_id: number
  template_id: number
  version_no: number
  prompt_content: string
  change_note: string
  is_active: boolean
  created_by: number
  creator_real_name?: string
  created_at: string
}

export interface CreateTemplateBody {
  template_name: string
  task_type_id: number
  initial_prompt_content: string
  change_note?: string
}

export interface UpdateTemplateBody {
  template_name?: string
  task_type_id?: number
  is_active?: boolean
}

export interface CreateVersionBody {
  prompt_content: string
  change_note?: string
}

export const promptsApi = {
  getTemplates(params?: {
    page?: number
    page_size?: number
    task_type_id?: number
    keyword?: string
  }) {
    return request.get<{ data: { items: PromptTemplate[]; total: number; page: number; page_size: number } }>(
      "/api/prompt-templates",
      { params }
    )
  },

  getTemplateById(templateId: number) {
    return request.get<{ data: PromptTemplate }>(`/api/prompt-templates/${templateId}`)
  },

  createTemplate(data: CreateTemplateBody) {
    return request.post<{ data: PromptTemplate }>("/api/prompt-templates", data)
  },

  updateTemplate(templateId: number, data: UpdateTemplateBody) {
    return request.put<{ data: PromptTemplate }>(`/api/prompt-templates/${templateId}`, data)
  },

  deleteTemplate(templateId: number) {
    return request.delete(`/api/prompt-templates/${templateId}`)
  },

  getVersions(templateId: number) {
    return request.get<{ data: PromptVersion[] }>(`/api/prompt-templates/${templateId}/versions`)
  },

  createVersion(templateId: number, data: CreateVersionBody) {
    return request.post<{ data: PromptVersion }>(`/api/prompt-templates/${templateId}/versions`, data)
  },

  activateVersion(templateId: number, versionId: number) {
    return request.post(`/api/prompt-templates/${templateId}/versions/${versionId}/activate`)
  }
}
