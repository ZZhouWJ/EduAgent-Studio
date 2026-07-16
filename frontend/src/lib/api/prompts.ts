import client from './client'

export interface PromptTaskType {
  task_type_id: number
  type_name: string
  type_code: string
  description?: string
  default_template_id?: number
  status: string
}

export interface PromptTemplate {
  template_id: number
  template_name: string
  task_type_id: number
  type_name: string
  type_code: string
  current_version_id?: number
  current_version_no?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface PromptVersion {
  prompt_version_id: number
  template_id: number
  version_no: string
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
  description?: string
  initial_prompt_content?: string
  change_note?: string
  activate?: boolean
}

export interface UpdateTemplateBody {
  template_name?: string
  task_type_id?: number
  is_active?: boolean
}

export interface CreateVersionBody {
  version_no?: string
  prompt_content: string
  change_note?: string
}

export interface PromptRenderResult {
  template_id: number
  version_id: number
  version_no: string
  required_variables: string[]
  missing_variables: string[]
  rendered_content: string
}

export const promptsApi = {
  getTaskTypes() {
    return client.get<PromptTaskType[]>('/task-types')
  },

  getTemplates(params?: {
    page?: number
    page_size?: number
    task_type_id?: number
    keyword?: string
  }) {
    return client.get<{ items: PromptTemplate[]; total: number }>('/prompt-templates', { params })
  },

  getTemplateById(template_id: number) {
    return client.get<PromptTemplate>(`/prompt-templates/${template_id}`)
  },

  createTemplate(data: CreateTemplateBody) {
    return client.post<PromptTemplate>('/prompt-templates', data)
  },

  updateTemplate(template_id: number, data: UpdateTemplateBody) {
    return client.put<PromptTemplate>(`/prompt-templates/${template_id}`, data)
  },

  deleteTemplate(template_id: number) {
    return client.delete(`/prompt-templates/${template_id}`)
  },

  getVersions(template_id: number) {
    return client.get<PromptVersion[]>(`/prompt-templates/${template_id}/versions`)
  },

  createVersion(template_id: number, data: CreateVersionBody) {
    return client.post<PromptVersion>(`/prompt-templates/${template_id}/versions`, data)
  },

  activateVersion(template_id: number, version_id: number) {
    return client.post(`/prompt-templates/${template_id}/versions/${version_id}/activate`)
  },

  renderTemplate(template_id: number, data: { version_id?: number; variables: Record<string, string> }) {
    return client.post<PromptRenderResult>(`/prompt-templates/${template_id}/render`, data)
  },
}
