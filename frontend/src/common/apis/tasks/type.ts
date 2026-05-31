/** 任务与版本相关类型定义 */

export interface Task {
  task_id: number
  project_id: number
  project_name?: string
  task_type_id: number
  type_name?: string
  type_code?: string
  title: string
  description?: string
  status: string
  priority: string
  assignee_id?: number
  assignee_username?: string
  assignee_real_name?: string
  created_by: number
  creator_username?: string
  creator_real_name?: string
  due_date?: string
  created_at: string
  updated_at: string
  is_deleted?: number
}

export interface TaskBranch {
  branch_id: number
  task_id: number
  branch_name: string
  status: string
  base_output_id?: number
  base_output_title?: string
  created_by: number
  creator_username?: string
  creator_real_name?: string
  created_at: string
  is_deleted?: number
}

export interface TaskOutput {
  output_id: number
  task_id: number
  branch_id: number
  output_title: string
  version_no: number
  source_type: "ai_generated" | "manual"
  content: string
  status: string
  lock_version: number
  created_by: number
  creator_username?: string
  creator_real_name?: string
  created_at: string
  updated_at: string
  is_deleted?: number
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
  is_deleted?: number
}

/** AI 生成请求体：POST /api/tasks/{task_id}/generate */
export interface GenerateRequestData {
  model_ids: number[]
  branch_id?: number
  prompt_version_id?: number
  input_text: string
}

/** AI 生成响应项（单个模型的生成结果） */
export interface GenerateResultItem {
  model_id: number
  model_name: string
  invocation_id: number
  output_id?: number
  version_no?: string | number
  status: string
  input_tokens?: number
  output_tokens?: number
  latency_ms?: number
  error_message?: string
}

/** 输出编辑请求体：PUT /api/outputs/{output_id} */
export interface UpdateOutputRequestData {
  content: string
  lock_version: number
  edit_summary?: string
}

/** 另存为新版本请求体：POST /api/outputs/{output_id}/save-as-new-version */
export interface SaveAsNewVersionRequestData {
  output_title: string
  content: string
  edit_summary?: string
  branch_id?: number
}

/** 新增批注请求体：POST /api/outputs/{output_id}/comments */
export interface CreateCommentRequestData {
  comment_type: "comment" | "suggestion" | "approval"
  comment_text: string
}

/** 更新批注状态请求体：PUT /api/comments/{comment_id}/status */
export interface UpdateCommentStatusRequestData {
  status: "open" | "resolved" | "closed"
}

export interface OutputTimeline {
  output_id: number
  output_title: string
  version_no: number
  source_type: string
  status: string
  created_at: string
  parent_output_id?: number
}

export interface TaskListParams {
  page?: number
  page_size?: number
  keyword?: string
  status?: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
  page: number
  page_size: number
}

export interface CreateTaskRequestData {
  task_type_id: number
  title: string
  description?: string
  assignee_id?: number
  priority?: string
  due_date?: string
}

export interface CreateBranchRequestData {
  branch_name: string
  base_output_id?: number
}

export interface OutputListParams {
  page?: number
  page_size?: number
}

/** 后端 GET /api/tasks/{id}/outputs 当前返回数组，兼容分页对象 */
export type OutputListResponse = TaskOutput[] | {
  items: TaskOutput[]
  total: number
  page: number
  page_size: number
}
