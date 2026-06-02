import type { NavigationGuardNext, RouteLocationNormalized } from "vue-router"

const whiteList = ["/login", "/register"]

export function setupGuard(router: ReturnType<typeof import("@/router").default>) {
  router.beforeEach(
    (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const token = localStorage.getItem("token")
      if (token) {
        if (to.path === "/login") {
          next("/")
        } else {
          next()
        }
      } else {
        if (whiteList.includes(to.path)) {
          next()
        } else {
          next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
        }
      }
    }
  )
}
