import request from "@/utils/request"

export interface UserListItem {
  user_id: number
  username: string
  real_name?: string
  email?: string
  phone?: string
  status: string
  last_login_at?: string
}

export const usersApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string; status?: string }) {
    return request.get<{ data: { items: UserListItem[]; total: number } }>(
      "/api/users",
      { params }
    )
  },

  update(userId: number, data: {
    real_name?: string
    email?: string
    phone?: string
    status?: string
  }) {
    return request.put(`/api/users/${userId}`, data)
  },

  updateRoles(userId: number, roles: string[]) {
    return request.put(`/api/users/${userId}/roles`, { roles })
  }
}
