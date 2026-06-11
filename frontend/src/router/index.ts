import { createRouter, createWebHashHistory } from "vue-router"
import type { RouteRecordRaw } from "vue-router"
import { setupGuard } from "./guard"

type Role = "admin" | "teacher" | "student" | "project_leader"

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
        path: "courses",
        name: "Courses",
        component: () => import("@/pages/courses/index.vue"),
        meta: { title: "课程空间" }
      },
      {
        path: "courses/:courseId",
        name: "CourseDetail",
        component: () => import("@/pages/courses/CourseDetail.vue"),
        meta: { title: "课程详情", hidden: true }
      },
      {
        path: "tasks",
        name: "Tasks",
        component: () => import("@/pages/tasks/index.vue"),
        meta: { title: "学习任务" }
      },
      {
        path: "tasks/:taskId",
        name: "TaskDetail",
        component: () => import("@/pages/tasks/TaskDetail.vue"),
        meta: { title: "任务详情", hidden: true }
      },
      {
        path: "profiles",
        name: "Profiles",
        component: () => import("@/pages/profiles/index.vue"),
        meta: { title: "学生画像" }
      },
      {
        path: "profiles/:profileId",
        name: "ProfileDetail",
        component: () => import("@/pages/profiles/ProfileDetail.vue"),
        meta: { title: "画像详情", hidden: true }
      },
      {
        path: "agent-workbench",
        name: "AgentWorkbench",
        component: () => import("@/pages/agent-workbench/index.vue"),
        meta: { title: "智能体工作台" }
      },
      {
        path: "resources",
        name: "Resources",
        component: () => import("@/pages/resources/index.vue"),
        meta: { title: "学习资源库" }
      },
      {
        path: "resources/:resourceId",
        name: "ResourceDetail",
        component: () => import("@/pages/resources/ResourceDetail.vue"),
        meta: { title: "资源详情", hidden: true }
      },
      {
        path: "reviews",
        name: "Reviews",
        component: () => import("@/pages/reviews/index.vue"),
        meta: { title: "教师审核中心" }
      },
      {
        path: "analytics",
        name: "Analytics",
        component: () => import("@/pages/analytics/index.vue"),
        meta: { title: "学习分析看板" }
      },
      {
        path: "feedback",
        name: "Feedback",
        component: () => import("@/pages/feedback/index.vue"),
        meta: { title: "学习反馈" }
      },
      {
        path: "invocations",
        name: "Invocations",
        component: () => import("@/pages/invocations/index.vue"),
        meta: { title: "智能体调用审计" }
      },
      {
        path: "costs",
        name: "Costs",
        component: () => import("@/pages/costs/index.vue"),
        meta: { title: "成本统计" }
      },
      {
        path: "models",
        name: "Models",
        component: () => import("@/pages/models/index.vue"),
        meta: { title: "模型与智能体配置", roles: ["admin"] }
      },
      {
        path: "prompts",
        name: "Prompts",
        component: () => import("@/pages/prompts/index.vue"),
        meta: { title: "提示词模板" }
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
