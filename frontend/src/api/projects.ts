import request from "@/utils/request"

export interface Project {
  project_id: number
  project_name: string
  project_type: string
  description?: string
  owner_id: number
  owner_username?: string
  owner_real_name?: string
  status: string
  created_at: string
  member_count?: number
  task_count?: number
}

export interface CreateProjectBody {
  project_name: string
  project_type: string
  description?: string
}

export interface ProjectMember {
  member_id: number
  project_id: number
  user_id: number
  username: string
  real_name?: string
  email?: string
  phone?: string
  project_role: string
  joined_at: string
  status: string
}

export interface ProjectTask {
  task_id: number
  project_id: number
  task_type_id: number
  type_name: string
  type_code: string
  title: string
  description?: string
  creator_id: number
  creator_username?: string
  assignee_id?: number
  assignee_real_name?: string
  status: string
  priority: string
  due_date?: string
  created_at: string
}

export const projectsApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string; status?: string }) {
    return request.get<{ data: { items: Project[]; total: number; page: number; page_size: number } }>(
      "/api/projects",
      { params }
    )
  },

  create(data: CreateProjectBody) {
    return request.post<{ data: Project }>("/api/projects", data)
  },

  getById(projectId: number) {
    return request.get<{ data: Project }>(`/api/projects/${projectId}`)
  },

  getMembers(projectId: number) {
    return request.get<{ data: ProjectMember[] }>(`/api/projects/${projectId}/members`)
  },

  getTasks(
    projectId: number,
    params?: { page?: number; page_size?: number; status?: string; keyword?: string }
  ) {
    return request.get<{ data: { items: ProjectTask[]; total: number; page: number; page_size: number } }>(
      `/api/projects/${projectId}/tasks`,
      { params }
    )
  },

  createTask(projectId: number, data: {
    task_type_id: number
    title: string
    description?: string
    assignee_id?: number
    priority?: string
    due_date?: string
  }) {
    return request.post<{ data: ProjectTask & { default_branch_id: number } }>(
      `/api/projects/${projectId}/tasks`,
      data
    )
  },

  addMember(projectId: number, data: { user_id: number; project_role: string }) {
    return request.post(`/api/projects/${projectId}/members`, data)
  },

  removeMember(projectId: number, userId: number) {
    return request.delete(`/api/projects/${projectId}/members/${userId}`)
  },

  updateMember(projectId: number, userId: number, data: { project_role: string }) {
    return request.put(`/api/projects/${projectId}/members/${userId}`, data)
  },

  update(projectId: number, data: { project_name?: string; project_type?: string; description?: string }) {
    return request.put<{ data: Project }>(`/api/projects/${projectId}`, data)
  },

  archive(projectId: number) {
    return request.post(`/api/projects/${projectId}/archive`)
  }
}
