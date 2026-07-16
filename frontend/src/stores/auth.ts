import { create } from 'zustand'
import { getToken, setToken as saveToken, clearToken } from '@/lib/api'
import { authApi, type UserInfo } from '@/lib/auth-api'

const LEGACY_AUTH_STORE_KEY = 'eduagent-auth'
if (typeof window !== 'undefined') {
  window.localStorage.removeItem(LEGACY_AUTH_STORE_KEY)
}

interface AuthState {
  token: string | null
  user: UserInfo | null
  loading: boolean
  initialized: boolean
  login: (username: string, password: string) => Promise<UserInfo>
  logout: () => Promise<void>
  fetchMe: () => Promise<UserInfo | null>
  hasRole: (role: string) => boolean
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: getToken(),
  user: null,
  loading: false,
  initialized: false,

  async login(username, password) {
    set({ loading: true })
    try {
      const data = await authApi.login(username, password)
      saveToken(data.token)
      const me = await authApi.me()
      set({ token: data.token, user: me, loading: false, initialized: true })
      return me
    } catch (e) {
      clearToken()
      set({ token: null, user: null, loading: false })
      throw e
    }
  },

  async logout() {
    try { await authApi.logout() } catch { /* ignore */ }
    clearToken()
    set({ token: null, user: null })
  },

  async fetchMe() {
    try {
      const me = await authApi.me()
      set({ user: me, initialized: true })
      return me
    } catch {
      clearToken()
      set({ user: null, token: null, initialized: true })
      return null
    }
  },

  hasRole(role) {
    return get().user?.roles?.includes(role) ?? false
  },
}))
