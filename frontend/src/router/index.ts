import type { RouteRecordRaw } from "vue-router"
import { createRouter } from "vue-router"
import { routerConfig } from "@/router/config"
import { registerNavigationGuard } from "@/router/guard"
import { flatMultiLevelRoutes } from "./helper"

const Layouts = () => import("@/layouts/index.vue")

/**
 * @name 常驻路由
 * @description 除了 redirect/403/404/login 等隐藏页面，其他页面建议设置唯一的 Name 属性
 */
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: "/redirect",
    component: Layouts,
    meta: { hidden: true },
    children: [
      {
        path: ":path(.*)",
        component: () => import("@/pages/redirect/index.vue")
      }
    ]
  },
  {
    path: "/403",
    component: () => import("@/pages/error/403.vue"),
    meta: { hidden: true }
  },
  {
    path: "/404",
    component: () => import("@/pages/error/404.vue"),
    meta: { hidden: true },
    alias: "/:pathMatch(.*)*"
  },
  {
    path: "/login",
    component: () => import("@/pages/login/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/",
    component: Layouts,
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        component: () => import("@/pages/dashboard/index.vue"),
        name: "Dashboard",
        meta: {
          title: "首页",
          svgIcon: "dashboard",
          affix: true
        }
      },
      {
        path: "projects",
        component: () => import("@/pages/projects/index.vue"),
        name: "Projects",
        meta: {
          title: "项目空间",
          svgIcon: "dashboard"
        }
      },
      {
        path: "projects/:projectId",
        component: () => import("@/pages/projects/ProjectDetail.vue"),
        name: "ProjectDetail",
        meta: {
          title: "项目详情",
          svgIcon: "dashboard",
          hidden: true
        }
      },
      {
        path: "tasks",
        component: () => import("@/pages/tasks/index.vue"),
        name: "Tasks",
        meta: {
          title: "任务与版本",
          svgIcon: "dashboard"
        }
      },
      {
        path: "tasks/:taskId",
        component: () => import("@/pages/tasks/TaskDetail.vue"),
        name: "TaskDetail",
        meta: {
          title: "任务详情",
          svgIcon: "dashboard",
          hidden: true
        }
      },
      {
        path: "reviews",
        component: () => import("@/pages/reviews/index.vue"),
        name: "Reviews",
        meta: {
          title: "审核中心",
          svgIcon: "dashboard"
        }
      },
      {
        path: "artifacts",
        component: () => import("@/pages/artifacts/index.vue"),
        name: "Artifacts",
        meta: {
          title: "成果库",
          svgIcon: "dashboard"
        }
      },
      {
        path: "statistics",
        component: () => import("@/pages/statistics/index.vue"),
        name: "Statistics",
        meta: {
          title: "统计看板",
          svgIcon: "dashboard"
        }
      },
      {
        path: "models",
        component: () => import("@/pages/models/index.vue"),
        name: "Models",
        meta: {
          title: "模型管理",
          svgIcon: "dashboard"
        }
      }
    ]
  }
]

/**
 * @name 动态路由
 * @description 本项目当前阶段不使用动态权限路由，所有登录用户均可访问全部页面
 */
export const dynamicRoutes: RouteRecordRaw[] = []

/** 路由实例 */
export const router = createRouter({
  history: routerConfig.history,
  routes: routerConfig.thirdLevelRouteCache ? flatMultiLevelRoutes(constantRoutes) : constantRoutes
})

/** 重置路由 */
export function resetRouter() {
  try {
    router.getRoutes().forEach((route) => {
      const { name, meta } = route
      if (name && meta.roles?.length) {
        router.hasRoute(name) && router.removeRoute(name)
      }
    })
  } catch {
    location.reload()
  }
}

// 注册路由导航守卫
registerNavigationGuard(router)
