import request from "@/utils/request"

export interface RegisterParams {
  username: string
  real_name: string
  password: string
  confirm_password: string
  student_no?: string
  email?: string
  phone?: string
  role_ids?: number[]
}

export interface User {
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  email?: string
  phone?: string
  status: string
  roles: string[]
  created_at: string
}

export interface Role {
  role_id: number
  role_name: string
  role_code: string
  description?: string
}

export interface UpdateProfileParams {
  real_name: string
  student_no?: string
  email?: string
  phone?: string
}

export const authApi = {
  login(username: string, password: string) {
    return request.post<{ data: { token: string; user: any } }>("/api/auth/login", {
      username,
      password
    })
  },

  register(data: RegisterParams) {
    return request.post("/api/auth/register", data)
  },

  me() {
    return request.get<{ data: any }>("/api/auth/me")
  },

  logout() {
    return request.post("/api/auth/logout")
  },

  changePassword(oldPassword: string, newPassword: string) {
    return request.put("/api/auth/me/password", {
      old_password: oldPassword,
      new_password: newPassword
    })
  },

  updateProfile(data: UpdateProfileParams) {
    return request.put("/api/auth/me", data)
  },

  updateMyRoles(role_ids: number[]) {
    return request.patch("/api/auth/me/roles", { role_ids })
  },

  listUsers(params?: { page?: number; page_size?: number; keyword?: string; status?: string }) {
    return request.get<{ data: { items: User[]; total: number } }>("/api/users", { params })
  },

  updateUserStatus(userId: number, status: string) {
    return request.put(`/api/users/${userId}/status`, { status })
  },

  updateUserRoles(userId: number, role_ids: number[]) {
    return request.put(`/api/users/${userId}/roles`, { role_ids })
  },

  listRoles() {
    return request.get<{ data: Role[] }>("/api/auth/roles")
  }
}
