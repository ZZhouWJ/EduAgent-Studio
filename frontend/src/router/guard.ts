import type { NavigationGuardNext, RouteLocationNormalized } from "vue-router"
import { useUserStore } from "@/stores/user"

const whiteList = ["/login", "/register"]

/**
 * Route meta.roles: string[] — which system-level roles can access.
 *   undefined / []  → any authenticated user can access
 *   ["admin"]       → only admin can access
 *   ["admin", "teacher"] → admin or teacher can access
 */
function hasRequiredRole(requiredRoles: string[] | undefined, userRoles: string[]): boolean {
  if (!requiredRoles || requiredRoles.length === 0) return true
  return requiredRoles.some(r => userRoles.includes(r))
}

export function setupGuard(router: ReturnType<typeof import("@/router").default>) {
  router.beforeEach(
    async (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const token = localStorage.getItem("token")
      const userStore = useUserStore()

      // ── Unauthenticated ──────────────────────────────────────────────
      if (!token) {
        if (whiteList.includes(to.path)) {
          next()
        } else {
          next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
        }
        return
      }

      // ── Authenticated ─────────────────────────────────────────────────
      if (to.path === "/login" || to.path === "/register") {
        next("/dashboard")
        return
      }

      // ── Role check (after token is present) ──────────────────────────
      const requiredRoles = to.meta.roles as string[] | undefined
      const userRoles = userStore.userInfo?.roles ?? []

      if (!hasRequiredRole(requiredRoles, userRoles)) {
        next("/403")
        return
      }

      next()
    }
  )
}
