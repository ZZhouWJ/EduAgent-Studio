import { setToken as _setToken, getToken, removeToken } from "@@/utils/local-storage"
import { pinia } from "@/pinia"
import { resetRouter } from "@/router"
import { routerConfig } from "@/router/config"
import { useSettingsStore } from "./settings"
import { useTagsViewStore } from "./tags-view"
import { logoutApi } from "@@/pages/login/apis"
import { getCurrentUserApi } from "@@/common/apis/users"

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(getToken() || "")

  const roles = ref<string[]>([])

  const username = ref<string>("")

  const userInfo = ref<Record<string, unknown>>({})

  const tagsViewStore = useTagsViewStore()

  const settingsStore = useSettingsStore()

  /** 设置 Token */
  const setToken = (value: string) => {
    _setToken(value)
    token.value = value
  }

  /** 获取用户详情，对接 GET /api/auth/me */
  const getInfo = async () => {
    const { data } = await getCurrentUserApi()
    username.value = data.username
    userInfo.value = data
    // 验证返回的 roles 是否为一个非空数组
    roles.value = data.roles?.length > 0 ? data.roles : routerConfig.defaultRoles
  }

  /** 登出：调用后端 POST /api/auth/logout，然后清除本地状态 */
  const logout = async () => {
    try {
      await logoutApi()
    } catch {
      // 后端登出失败不影响前端清除 session
    } finally {
      removeToken()
      token.value = ""
      roles.value = []
      userInfo.value = {}
      resetRouter()
      resetTagsView()
    }
  }

  /** 重置 Token */
  const resetToken = () => {
    removeToken()
    token.value = ""
    roles.value = []
    userInfo.value = {}
  }

  /** 重置 Visited Views 和 Cached Views */
  const resetTagsView = () => {
    if (!settingsStore.cacheTagsView) {
      tagsViewStore.delAllVisitedViews()
      tagsViewStore.delAllCachedViews()
    }
  }

  return { token, roles, username, userInfo, setToken, getInfo, logout, resetToken }
})

/**
 * @description 在 SPA 应用中可用于在 pinia 实例被激活前使用 store
 */
export function useUserStoreOutside() {
  return useUserStore(pinia)
}
