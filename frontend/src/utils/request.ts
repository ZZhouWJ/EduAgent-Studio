import axios from "axios"
import { ElMessage } from "element-plus"
import router from "@/router"

const request = axios.create({
  baseURL: "/",
  timeout: 10000
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 0) {
      return res
    }
    ElMessage.error(res.message || "请求失败")
    return Promise.reject(new Error(res.message || "请求失败"))
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        router.push("/login")
        ElMessage.error("登录已过期，请重新登录")
      } else if (status === 403) {
        ElMessage.error("无访问权限")
      } else if (status === 404) {
        ElMessage.error("请求地址不存在")
      } else if (status >= 500) {
        ElMessage.error("服务器错误，请稍后重试")
      } else {
        ElMessage.error(error.response.data?.message || "请求失败")
      }
    } else {
      ElMessage.error("网络错误，请检查网络连接")
    }
    return Promise.reject(error)
  }
)

export default request
