export interface LoginRequestData {
  /** 用户名 */
  username: string
  /** 密码 */
  password: string
}

/** 登录响应：{ token, user } */
export type LoginResponseData = ApiResponseData<{
  token: string
  user: {
    user_id: number
    username: string
    real_name?: string
    email?: string
    roles: string[]
    permissions?: string[]
  }
}>
