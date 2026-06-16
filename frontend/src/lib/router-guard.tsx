import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'

const PUBLIC_PATHS = ['/login']

// ⚠️ 临时开关：开发期不带后端时跳过登录拦截（想看受保护页面时改为 true）
const DEV_BYPASS = true

const ROLE_ACCESS: Record<string, string[]> = {
  '/student': ['student', 'admin'],
  '/teacher': ['teacher', 'admin'],
  '/admin': ['admin'],
}

export function useRouterGuard() {
  const { token, user, initialized, fetchMe } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    if (DEV_BYPASS) {
      // 注入一个虚拟 admin 身份，让所有角色路由都放行
      useAuthStore.setState({
        token: 'dev-bypass',
        user: { id: 0, username: 'dev', full_name: 'Dev', roles: ['admin'] } as any,
        initialized: true,
      })
      return
    }
    if (initialized) return
    if (token) {
      fetchMe()
    } else {
      useAuthStore.setState({ initialized: true })
    }
  }, [initialized, token, fetchMe])

  useEffect(() => {
    if (DEV_BYPASS) return
    if (!initialized) return
    const isPublic = PUBLIC_PATHS.some((p) => location.pathname.startsWith(p))
    if (!token && !isPublic) {
      navigate(`/login?redirect=${encodeURIComponent(location.pathname + location.search)}`, { replace: true })
      return
    }
    if (token && isPublic) {
      const role = user?.roles?.[0] ?? 'student'
      const home = role === 'admin' ? '/admin' : role === 'teacher' ? '/teacher' : '/student'
      navigate(home, { replace: true })
      return
    }
    if (token && user) {
      for (const [prefix, allowed] of Object.entries(ROLE_ACCESS)) {
        if (location.pathname.startsWith(prefix)) {
          if (!user.roles?.some((r) => allowed.includes(r))) {
            navigate('/login', { replace: true })
          }
          return
        }
      }
    }
  }, [initialized, token, user, location.pathname, location.search, navigate])
}
