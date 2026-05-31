/** 任务与版本相关类型定义 */

export interface Task {
  task_id: number
  project_id: number
  task_type_id: number
  task_type_name?: string
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
  branch_type: string
  status: string
  base_output_id?: number
  created_by: number
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
  created_by: number
  creator_username?: string
  creator_real_name?: string
  created_at: string
  updated_at: string
  is_deleted?: number
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
  branch_type?: string
  base_output_id?: number
}

export interface OutputListParams {
  page?: number
  page_size?: number
}

export interface OutputListResponse {
  items: TaskOutput[]
  total: number
  page: number
  page_size: number
}
