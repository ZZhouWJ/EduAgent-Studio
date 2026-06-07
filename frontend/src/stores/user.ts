import { defineStore } from "pinia"
import { ref } from "vue"
import request from "@/utils/request"

export interface UserInfo {
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  email?: string
  phone?: string
  roles: string[]
  permissions?: string[]
}

export const useUserStore = defineStore("user", () => {
  const token = ref(localStorage.getItem("token") || "")
  const userInfo = ref<UserInfo | null>(
    JSON.parse(localStorage.getItem("user") || "null")
  )

  const setToken = (t: string) => {
    token.value = t
    localStorage.setItem("token", t)
  }

  const setUser = (info: UserInfo) => {
    userInfo.value = info
    localStorage.setItem("user", JSON.stringify(info))
  }

  const getMe = async () => {
    const res = await request.get<{ data: UserInfo }>("/api/auth/me")
    setUser(res.data)
    return res.data
  }

  const login = async (username: string, password: string) => {
    const res = await request.post<{ data: { token: string } }>("/api/auth/login", {
      username,
      password
    })
    setToken(res.data.token)
    await getMe()
  }

  const logout = async () => {
    try {
      await request.post("/api/auth/logout")
    } catch {
      // ignore
    } finally {
      token.value = ""
      userInfo.value = null
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      window.location.href = "/login"
    }
  }

  return { token, userInfo, setToken, setUser, getMe, login, logout }
})
