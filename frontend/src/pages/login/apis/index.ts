import type * as Auth from "./type"
import { request } from "@/http/axios"

/** 登录并返回 Token */
export function loginApi(data: Auth.LoginRequestData) {
  return request<Auth.LoginResponseData>({
    url: "api/auth/login",
    method: "post",
    data
  })
}

/** 获取当前登录用户详情 */
export function getCurrentUserApi() {
  return request<ApiResponseData<{
    user_id: number
    username: string
    real_name?: string
    student_no?: string
    email?: string
    phone?: string
    status?: string
    roles: string[]
    permissions?: string[]
  }>>({
    url: "api/auth/me",
    method: "get"
  })
}

/** 登出 */
export function logoutApi() {
  return request<ApiResponseData<object>>({
    url: "api/auth/logout",
    method: "post"
  })
}
