import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'

const TOKEN_KEY = 'eduagent_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export interface ApiEnvelope<T = unknown> {
  code: number
  message: string
  data: T
}

export class ApiError extends Error {
  code: number
  httpStatus?: number

  constructor(message: string, code: number, httpStatus?: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.httpStatus = httpStatus
  }
}

type UnwrappedAxiosInstance = Omit<AxiosInstance, 'get' | 'delete' | 'head' | 'options' | 'post' | 'put' | 'patch'> & {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  head<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  options<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
}

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
}) as UnwrappedAxiosInstance

client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error),
)

client.interceptors.response.use(
  (response) => {
    const body = response.data as ApiEnvelope
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data
      return Promise.reject(new ApiError(body.message || '请求失败', body.code, response.status))
    }
    return response.data
  },
  (error: AxiosError<ApiEnvelope>) => {
    if (error.response) {
      const { status, data } = error.response
      const message = data?.message || error.message || '请求失败'
      if (status === 401) {
        clearToken()
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(new ApiError('登录已过期，请重新登录', 401, 401))
      }
      if (status === 403) return Promise.reject(new ApiError('无访问权限', 403, 403))
      if (status === 404) return Promise.reject(new ApiError('请求地址不存在', 404, 404))
      if (status >= 500) return Promise.reject(new ApiError('服务器错误，请稍后重试', status, status))
      return Promise.reject(new ApiError(message, data?.code ?? status, status))
    }
    return Promise.reject(new ApiError('网络错误，请检查网络连接', -1))
  },
)

export default client
