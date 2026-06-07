import { createRouter, createWebHashHistory } from "vue-router"
import type { RouteRecordRaw } from "vue-router"
import { setupGuard } from "./guard"

/**
 * Route meta.roles defines which system-level roles can access the route.
 * [] (empty) means any authenticated user can access.
 * ["admin"] means only admin users can access.
 * ["admin", "teacher"] means admin or teacher can access.
 *
 * Project-scoped routes (/projects/:id, /tasks/:id) do not use meta.roles
 * because their permission depends on project_role (fetched at runtime).
 */

type Role = "admin" | "teacher" | "student_member" | "project_leader"

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/pages/login/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/pages/register/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/403",
    name: "Forbidden",
    component: () => import("@/pages/403/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/",
    component: () => import("@/layouts/BackendLayout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/pages/dashboard/index.vue"),
        meta: { title: "首页" }
      },
      {
        path: "projects",
        name: "Projects",
        component: () => import("@/pages/projects/index.vue"),
        meta: { title: "项目空间" }
      },
      {
        path: "projects/:projectId",
        name: "ProjectDetail",
        component: () => import("@/pages/projects/ProjectDetail.vue"),
        meta: { title: "项目详情", hidden: true }
      },
      {
        path: "tasks",
        name: "Tasks",
        component: () => import("@/pages/tasks/index.vue"),
        meta: { title: "任务与版本" }
      },
      {
        path: "tasks/:taskId",
        name: "TaskDetail",
        component: () => import("@/pages/tasks/TaskDetail.vue"),
        meta: { title: "任务详情", hidden: true }
      },
      {
        path: "generate",
        name: "Generate",
        component: () => import("@/pages/generate/index.vue"),
        meta: { title: "AI 生成" }
      },
      {
        path: "prompts",
        name: "Prompts",
        component: () => import("@/pages/prompts/index.vue"),
        meta: { title: "提示词管理" }
      },
      {
        path: "reviews",
        name: "Reviews",
        component: () => import("@/pages/reviews/index.vue"),
        meta: { title: "审核中心" }
      },
      {
        path: "artifacts",
        name: "Artifacts",
        component: () => import("@/pages/artifacts/index.vue"),
        meta: { title: "成果库" }
      },
      {
        path: "invocations",
        name: "Invocations",
        component: () => import("@/pages/invocations/index.vue"),
        meta: { title: "调用审计" }
      },
      {
        path: "costs",
        name: "Costs",
        component: () => import("@/pages/costs/index.vue"),
        meta: { title: "成本统计" }
      },
      {
        path: "statistics",
        name: "Statistics",
        component: () => import("@/pages/statistics/index.vue"),
        meta: { title: "统计看板" }
      },
      {
        path: "models",
        name: "Models",
        component: () => import("@/pages/models/index.vue"),
        meta: { title: "模型管理", roles: ["admin"] }
      },
      {
        path: "users",
        name: "Users",
        component: () => import("@/pages/users/index.vue"),
        meta: { title: "用户管理", roles: ["admin"] }
      },
      {
        path: "logs/operation",
        name: "OperationLogs",
        component: () => import("@/pages/logs/operation.vue"),
        meta: { title: "操作日志", roles: ["admin"] }
      },
      {
        path: "logs/login",
        name: "LoginLogs",
        component: () => import("@/pages/logs/login.vue"),
        meta: { title: "登录日志", roles: ["admin"] }
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("@/pages/profile/index.vue"),
        meta: { title: "个人中心", hidden: true }
      }
    ]
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login"
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

setupGuard(router)

export default router
