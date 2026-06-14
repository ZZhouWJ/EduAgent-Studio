import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router'
import { useAuthStore } from '@/stores/auth'

const PUBLIC_PATHS = ['/login']

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
    if (initialized) return
    if (token) {
      fetchMe()
    } else {
      useAuthStore.setState({ initialized: true })
    }
  }, [initialized, token, fetchMe])

  useEffect(() => {
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
