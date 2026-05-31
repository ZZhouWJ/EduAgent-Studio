/**
 * Axios 封装
 *
 * - baseURL 从环境变量 VITE_API_BASE_URL 读取，默认 http://127.0.0.1:8000
 * - 请求拦截器自动附加 Authorization: Bearer <token>
 * - 响应拦截器适配后端统一返回格式 { code, message, data }
 *   - code === 0：resolve(data)
 *   - code !== 0：reject 并给出 Element Plus Message 提示
 * - 401 时自动跳转登录页
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
})

// 请求拦截器：附加 Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：适配统一格式
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 0 || res.code === undefined) {
      return res.data !== undefined ? res.data : res
    }
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(res)
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        const msg = data?.message || `请求失败 (${status})`
        ElMessage.error(msg)
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务是否启动')
    }
    return Promise.reject(error)
  }
)

export default request
