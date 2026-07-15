import client from './client'

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
  list(params?: {
    page?: number
    page_size?: number
    keyword?: string
    status?: string
    project_type?: string
  }) {
    return client.get<{ items: Project[]; total: number }>('/projects', { params })
  },

  create(data: CreateProjectBody) {
    return client.post<Project>('/projects', data)
  },

  getById(project_id: number) {
    return client.get<Project>(`/projects/${project_id}`)
  },

  update(
    project_id: number,
    data: {
      project_name?: string
      project_type?: string
      description?: string
      status?: string
    }
  ) {
    return client.put<Project>(`/projects/${project_id}`, data)
  },

  delete(project_id: number) {
    return client.delete(`/projects/${project_id}`)
  },

  archive(project_id: number) {
    return client.post(`/projects/${project_id}/archive`)
  },

  getMembers(project_id: number) {
    return client.get<ProjectMember[]>(`/projects/${project_id}/members`)
  },

  addMember(project_id: number, data: { user_id: number; project_role: string }) {
    return client.post(`/projects/${project_id}/members`, data)
  },

  updateMember(project_id: number, member_id: number, data: { project_role: string }) {
    return client.put(`/projects/${project_id}/members/${member_id}`, data)
  },

  removeMember(project_id: number, member_id: number) {
    return client.delete(`/projects/${project_id}/members/${member_id}`)
  },

  getTasks(
    project_id: number,
    params?: {
      page?: number
      page_size?: number
      status?: string
      keyword?: string
    }
  ) {
    return client.get<{ items: ProjectTask[]; total: number }>(`/projects/${project_id}/tasks`, {
      params,
    })
  },

  createTask(
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
    return client.post<ProjectTask & { default_branch_id: number }>(`/projects/${project_id}/tasks`, data)
  },
}
