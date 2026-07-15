import client from './client'

export interface User {
  user_id: number
  username: string
  real_name?: string
  email?: string
  phone?: string
  status: string
  roles?: string[]
  last_login_at?: string
  created_at?: string
}

export interface Role {
  role_id: number
  role_name: string
  role_code: string
}

export interface Permission {
  permission_id: number
  permission_name: string
  permission_code: string
}

export const usersApi = {
  list(params?: {
    page?: number
    page_size?: number
    keyword?: string
    status?: string
  }) {
    return client.get<{ items: User[]; total: number }>('/users', { params })
  },

  updateStatus(user_id: number, status: string) {
    return client.put(`/users/${user_id}/status`, { status })
  },

  updateRoles(user_id: number, role_ids: number[]) {
    return client.put(`/users/${user_id}/roles`, { role_ids })
  },

  listRoles() {
    return client.get<Role[]>('/roles')
  },

  listPermissions() {
    return client.get<Permission[]>('/permissions')
  },
}
