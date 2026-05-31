/** 后端统一响应结构：{ code: number, message: string, data: T } */
export interface ApiResponseData<T = unknown> {
  code: number
  message: string
  data: T
}
