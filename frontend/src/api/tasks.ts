import request from "@/utils/request"

export interface TaskOutput {
  output_id: number
  task_id: number
  branch_id: number
  branch_name: string
  version_no: number
  output_title: string
  source_type: string
  parent_output_id?: number
  is_final_candidate: boolean
  status: string
  content?: string
  lock_version?: number
  edit_summary?: string
  creator_id: number
  creator_username?: string
  created_at: string
  last_modified_at?: string
}

export interface TaskBranch {
  branch_id: number
  project_id: number
  task_id: number
  branch_name: string
  base_output_id?: number
  status: string
  creator_username?: string
  created_at: string
}

export interface OutputComment {
  comment_id: number
  output_id: number
  commenter_id: number
  commenter_username?: string
  commenter_real_name?: string
  comment_type: "comment" | "suggestion" | "approval"
  comment_text: string
  status: "open" | "resolved" | "closed"
  created_at: string
  updated_at: string
}

export interface GenerationResult {
  model_id: number
  invocation_id: number
  output_id?: number
  version_no?: number
  status: string
  input_tokens?: number
  output_tokens?: number
  latency_ms?: number
  error_message?: string
}

export const tasksApi = {
  getById(taskId: number) {
    return request.get<{ data: any }>(`/api/tasks/${taskId}`)
  },

  getBranches(taskId: number) {
    return request.get<{ data: TaskBranch[] }>(`/api/tasks/${taskId}/branches`)
  },

  getOutputs(taskId: number) {
    return request.get<{ data: TaskOutput[] }>(`/api/tasks/${taskId}/outputs`)
  },

  generate(taskId: number, data: {
    branch_id?: number
    model_ids: number[]
    prompt_version_id?: number
    input_text: string
  }) {
    return request.post<{ data: GenerationResult[] }>(`/api/tasks/${taskId}/generate`, data)
  },

  getOutputById(outputId: number) {
    return request.get<{ data: TaskOutput }>(`/api/outputs/${outputId}`)
  },

  updateOutput(outputId: number, data: {
    content: string
    lock_version: number
    edit_summary?: string
  }) {
    return request.put<{ data: TaskOutput }>(`/api/outputs/${outputId}`, data)
  },

  saveAsNewVersion(outputId: number, data: {
    output_title?: string
    content: string
    edit_summary?: string
    branch_id?: number
  }) {
    return request.post<{ data: TaskOutput }>(`/api/outputs/${outputId}/save-as-new-version`, data)
  },

  submitReview(outputId: number, data?: { reviewer_id?: number; submit_note?: string }) {
    return request.post<{ data: { request_id: number } }>(`/api/outputs/${outputId}/submit-review`, data || {})
  },

  adoptOutput(outputId: number, data: {
    artifact_title: string
    artifact_type: string
    release_version?: string
    adopt_note?: string
  }) {
    return request.post<{ data: { adopted_id: number } }>(`/api/outputs/${outputId}/adopt`, data)
  },

  getOutputComments(outputId: number, params?: { status?: string }) {
    return request.get<{ data: OutputComment[] }>(`/api/outputs/${outputId}/comments`, { params })
  },

  addComment(outputId: number, data: {
    comment_type: "comment" | "suggestion" | "approval"
    comment_text: string
  }) {
    return request.post<{ data: OutputComment }>(`/api/outputs/${outputId}/comments`, data)
  },

  updateCommentStatus(commentId: number, status: "open" | "resolved" | "closed") {
    return request.put<{ data: OutputComment }>(`/api/comments/${commentId}/status`, { status })
  }
}
