/**
 * Pinia 用户状态管理
 *
 * - 保存 token（localStorage 持久化）
 * - 保存 userInfo（不含 password）
 * - 保存 roles / permissions
 * - 提供 login / fetchCurrentUser / logout actions
 * - 刷新页面后从 localStorage 恢复 token
 */

import { defineStore } from 'pinia'
import { login as apiLogin, getMe, logout as apiLogout } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
    roles: JSON.parse(localStorage.getItem('roles') || '[]'),
    permissions: JSON.parse(localStorage.getItem('permissions') || '[]'),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    currentUser: (state) => state.userInfo,
    isAdmin: (state) => state.roles.includes('admin'),
  },

  actions: {
    /** 登录 */
    async login(credentials) {
      const data = await apiLogin(credentials)
      this.setToken(data.token)
      this.setUserInfo(data.user)
      return data
    },

    /** 获取当前用户信息（刷新页面后调用）*/
    async fetchCurrentUser() {
      if (!this.token) return null
      try {
        const user = await getMe()
        this.setUserInfo(user)
        return user
      } catch {
        this.clearSession()
        return null
      }
    },

    /** 登出 */
    async logout() {
      try {
        await apiLogout()
      } catch {
        // 忽略后端错误，前端仍清除 session
      } finally {
        this.clearSession()
      }
    },

    /** 保存 token */
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },

    /** 保存用户信息及角色权限 */
    setUserInfo(user) {
      this.userInfo = user
      localStorage.setItem('userInfo', JSON.stringify(user))
      if (user.roles) {
        this.roles = user.roles
        localStorage.setItem('roles', JSON.stringify(user.roles))
      }
      if (user.permissions) {
        this.permissions = user.permissions
        localStorage.setItem('permissions', JSON.stringify(user.permissions))
      }
    },

    /** 清除会话 */
    clearSession() {
      this.token = ''
      this.userInfo = null
      this.roles = []
      this.permissions = []
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('roles')
      localStorage.removeItem('permissions')
    },
  },
})
