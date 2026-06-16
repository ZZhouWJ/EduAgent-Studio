/**
 * Mock authentication — used when VITE_USE_MOCK_AUTH=true.
 * Provides instant, no-backend login for the three demo roles.
 */

import type { UserInfo } from './auth-api'

const MOCK_USERS: Record<string, { password: string; user: UserInfo }> = {
  admin: {
    password: 'Pass@1234',
    user: {
      user_id: 1,
      username: 'admin',
      real_name: '系统管理员',
      email: 'admin@eduagent.local',
      phone: '13800000000',
      roles: ['admin'],
      status: 'active',
    },
  },
  teacher_li: {
    password: 'Pass@1234',
    user: {
      user_id: 2,
      username: 'teacher_li',
      real_name: '李老师',
      email: 'teacher_li@eduagent.local',
      phone: '13800000001',
      roles: ['teacher'],
      status: 'active',
    },
  },
  student_zhang: {
    password: 'Pass@1234',
    user: {
      user_id: 3,
      username: 'student_zhang',
      real_name: '张同学',
      student_no: '20240001',
      email: 'student_zhang@eduagent.local',
      phone: '13800000002',
      roles: ['student'],
      status: 'active',
    },
  },
}

function makeMockToken(username: string): string {
  return `mock_token_${username}_${Date.now()}`
}

export const mockAuthApi = {
  login(username: string, password: string): { token: string; user: UserInfo } {
    const entry = MOCK_USERS[username.toLowerCase()]
    if (!entry || entry.password !== password) {
      const err = new Error('用户名或密码错误')
      ;(err as any).code = 401
      ;(err as any).httpStatus = 401
      throw err
    }
    return {
      token: makeMockToken(username),
      user: entry.user,
    }
  },

  me(token: string): UserInfo {
    const username = token.replace('mock_token_', '').replace(/_\d+$/, '')
    const entry = MOCK_USERS[username]
    if (!entry) throw new Error('无效 Token')
    return entry.user
  },
}
