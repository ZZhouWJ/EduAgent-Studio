/** 项目相关类型定义 */

export interface Project {
  project_id: number
  project_name: string
  project_type: string
  description?: string
  status: string
  created_at: string
  updated_at: string
  created_by: number
  owner_id: number
  owner_username?: string
  owner_real_name?: string
  is_deleted?: number
}

export interface ProjectMember {
  member_id: number
  project_id: number
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  project_role: "member" | "leader" | "reviewer" | "teacher"
  joined_at: string
  is_deleted?: number
}

export interface ProjectListParams {
  page?: number
  page_size?: number
  keyword?: string
  status?: string
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  page_size: number
}

export interface CreateProjectRequestData {
  project_name: string
  project_type: string
  description?: string
}
