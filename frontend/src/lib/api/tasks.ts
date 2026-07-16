import client from './client'

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
  comment_type: 'comment' | 'suggestion' | 'approval'
  comment_text: string
  status: 'open' | 'resolved' | 'closed'
  created_at: string
  updated_at: string
}

export const tasksApi = {
  getById(task_id: number) {
    return client.get<unknown>(`/tasks/${task_id}`)
  },

  update(
    task_id: number,
    data: {
      title?: string
      description?: string
      assignee_id?: number
      status?: string
      priority?: string
      due_date?: string
    }
  ) {
    return client.put(`/tasks/${task_id}`, data)
  },

  delete(task_id: number) {
    return client.delete(`/tasks/${task_id}`)
  },

  getBranches(task_id: number) {
    return client.get<TaskBranch[]>(`/tasks/${task_id}/branches`)
  },

  createBranch(task_id: number, data: { branch_name: string; base_output_id?: number }) {
    return client.post<TaskBranch>(`/tasks/${task_id}/branches`, data)
  },

  getOutputs(task_id: number) {
    return client.get<TaskOutput[]>(`/tasks/${task_id}/outputs`)
  },

  createManualOutput(
    task_id: number,
    data: {
      branch_id?: number
      parent_output_id?: number
      output_title: string
      content: string
      edit_summary?: string
    }
  ) {
    return client.post<TaskOutput>(`/tasks/${task_id}/outputs/manual`, data)
  },

  getOutputById(output_id: number) {
    return client.get<TaskOutput>(`/outputs/${output_id}`)
  },

  updateOutput(
    output_id: number,
    data: {
      content: string
      lock_version: number
      edit_summary?: string
    }
  ) {
    return client.put<TaskOutput>(`/outputs/${output_id}`, data)
  },

  saveAsNewVersion(
    output_id: number,
    data: {
      output_title?: string
      content: string
      edit_summary?: string
      branch_id?: number
    }
  ) {
    return client.post<TaskOutput>(`/outputs/${output_id}/save-as-new-version`, data)
  },

  getOutputTimeline(output_id: number) {
    return client.get<TaskOutput[]>(`/outputs/${output_id}/timeline`)
  },

  getOutputComments(output_id: number, params?: { status?: string }) {
    return client.get<OutputComment[]>(`/outputs/${output_id}/comments`, { params })
  },

  addComment(
    output_id: number,
    data: { comment_type: 'comment' | 'suggestion' | 'approval'; comment_text: string }
  ) {
    return client.post<OutputComment>(`/outputs/${output_id}/comments`, data)
  },

  updateCommentStatus(comment_id: number, status: 'open' | 'resolved' | 'closed') {
    return client.put<OutputComment>(`/comments/${comment_id}/status`, { status })
  },

  submitReview(output_id: number, data?: { reviewer_id?: number; submit_note?: string }) {
    return client.post<{ request_id: number }>(`/outputs/${output_id}/submit-review`, data || {})
  },

  compareOutputs(output1_id: number, output2_id: number) {
    return client.get(`/outputs/compare`, { params: { output1_id, output2_id } })
  },

  listProjectTasks(
    project_id: number,
    params?: {
      page?: number
      page_size?: number
      status?: string
      keyword?: string
    }
  ) {
    return client.get<{ items: unknown[]; total: number }>(`/projects/${project_id}/tasks`, { params })
  },

  createProjectTask(
    project_id: number,
    data: {
      task_type_id: number
      title: string
      description?: string
      assignee_id?: number
      priority?: string
      due_date?: string
    }
  ) {
    return client.post(`/projects/${project_id}/tasks`, data)
  },
}
