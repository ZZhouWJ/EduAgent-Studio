import type * as Users from "./type"
import { request } from "@/http/axios"

/** 获取当前登录用户详情，对接 GET /api/auth/me */
export function getCurrentUserApi() {
  return request<Users.CurrentUserResponseData>({
    url: "api/auth/me",
    method: "get"
  })
}
