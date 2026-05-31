/**
 * 认证 API
 *
 * 接口字段与后端 auth router 对齐：
 * - POST /api/auth/login   请求体: { username, password }  响应: { token, user }
 * - GET  /api/auth/me     响应: { user_id, username, real_name, roles, permissions, ... }
 * - POST /api/auth/logout
 */

import request from './request'

/**
 * 用户登录
 * @param {{ username: string, password: string }} data
 * @returns { token: string, user: object }
 */
export function login(data) {
  return request.post('/api/auth/login', data)
}

/**
 * 获取当前登录用户信息
 * @returns { user_id, username, real_name, email, roles, permissions, ... }
 */
export function getMe() {
  return request.get('/api/auth/me')
}

/**
 * 用户登出
 */
export function logout() {
  return request.post('/api/auth/logout')
}
