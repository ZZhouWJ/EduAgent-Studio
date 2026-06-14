import client from './api'

export interface UserInfo {
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  email?: string
  phone?: string
  roles: string[]
  status?: string
}

export interface LoginResponse {
  token: string
  user: UserInfo
}

export const authApi = {
  login(username: string, password: string) {
    return client.post<LoginResponse>('/auth/login', { username, password })
  },
  register(data: { username: string; password: string; real_name?: string; email?: string; student_no?: string }) {
    return client.post('/auth/register', data)
  },
  me() {
    return client.get<UserInfo>('/auth/me')
  },
  logout() {
    return client.post('/auth/logout')
  },
  changePassword(old_password: string, new_password: string) {
    return client.put('/auth/me/password', { old_password, new_password })
  },
  updateProfile(data: { real_name?: string; student_no?: string; email?: string; phone?: string }) {
    return client.put('/auth/me', data)
  },
  listRoles() {
    return client.get<Array<{ role_id: number; role_name: string; role_code: string }>>('/auth/roles')
  },
}
