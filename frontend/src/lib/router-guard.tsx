import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'

const PUBLIC_PATHS = ['/login']

// ⚠️ 强制角色隔离开关：生产环境必须为 true
const ENFORCE_ROLE_ISOLATION = true

// 路由与允许角色的映射
const ROLE_ACCESS: Record<string, string[]> = {
  '/student': ['student'],
  '/teacher': ['teacher'],
  '/admin': ['admin'],
}

// 获取用户真实角色（从 user.roles 数组中匹配）
function getUserRealRole(roles: string[] | undefined): string | null {
  if (!roles || roles.length === 0) return null
  // 按优先级顺序检查：admin > teacher > student
  if (roles.includes('admin')) return 'admin'
  if (roles.includes('teacher')) return 'teacher'
  if (roles.includes('student')) return 'student'
  return roles[0]
}

// 根据角色获取默认首页
function getHomePath(role: string): string {
  switch (role) {
    case 'admin': return '/admin'
    case 'teacher': return '/teacher'
    case 'student': return '/student'
    default: return '/login'
  }
}

export function useRouterGuard() {
  const { token, user, initialized, fetchMe } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  // 初始化：获取用户信息
  useEffect(() => {
    if (initialized) return
    if (token) {
      fetchMe()
    } else {
      useAuthStore.setState({ initialized: true })
    }
  }, [initialized, token, fetchMe])

  // 路由守卫：检查登录状态和角色权限
  useEffect(() => {
    if (!initialized) return

    const isPublic = PUBLIC_PATHS.some((p) => location.pathname.startsWith(p))

    // 未登录且访问受保护路由 → 跳转登录
    if (!token && !isPublic) {
      navigate(`/login?redirect=${encodeURIComponent(location.pathname + location.search)}`, { replace: true })
      return
    }

    // 已登录且访问公共路由（登录页）→ 跳转对应角色首页
    if (token && isPublic) {
      const role = getUserRealRole(user?.roles)
      if (role) {
        navigate(getHomePath(role), { replace: true })
      }
      return
    }

    // 已登录，强制角色隔离检查
    if (token && user && ENFORCE_ROLE_ISOLATION) {
      const userRole = getUserRealRole(user.roles)
      const currentPath = location.pathname

      // 检查当前路径需要的角色
      for (const [prefix, allowedRoles] of Object.entries(ROLE_ACCESS)) {
        if (currentPath.startsWith(prefix)) {
          // 用户角色必须在允许列表中
          if (!userRole || !allowedRoles.includes(userRole)) {
            // 角色不匹配，强制跳转到用户真实角色的首页
            navigate(getHomePath(userRole!), { replace: true })
            return
          }
          break
        }
      }
    }
  }, [initialized, token, user, location.pathname, location.search, navigate])
}

// 导出工具函数供其他组件使用
export { getUserRealRole, getHomePath }
