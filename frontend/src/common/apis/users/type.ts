export type CurrentUserResponseData = ApiResponseData<{
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  email?: string
  phone?: string
  status?: string
  roles: string[]
  permissions?: string[]
}>
