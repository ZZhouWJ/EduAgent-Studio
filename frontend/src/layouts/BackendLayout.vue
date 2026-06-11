<script setup lang="ts">
import { computed } from "vue"
import { useUserStore } from "@/stores/user"
import { useRouter, useRoute } from "vue-router"
import { useProjectRoleStore } from "@/stores/projectRole"
import {
  House,
  Folder,
  List,
  Cpu,
  CircleCheck,
  Collection,
  DataLine,
  Tools,
  User,
  SwitchButton,
  ArrowDown,
  UserFilled,
  Comment,
  Monitor,
  Money,
  Document,
  Key
} from "@element-plus/icons-vue"
import { isAdmin, isTeacher, GLOBAL_ROLE_LABEL } from "@/utils/permission"

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const projectRoleStore = useProjectRoleStore()

const activeMenu = computed(() => route.path)
const user = computed(() => userStore.userInfo)

/** Current project role badge shown in topbar when viewing a project */
const currentProjectRole = computed(() => {
  if (!route.path.startsWith("/projects/")) return null
  if (!user.value) return null
  const projectId = Number(route.params.projectId)
  return projectRoleStore.getCurrentUserProjectRole(projectId, user.value.user_id)
})

/** Role label for current project role */
const currentProjectRoleLabel = computed(() => {
  if (!currentProjectRole.value) return null
  const map: Record<string, string> = {
    leader: "课程创建者",
    teacher: "指导教师",
    reviewer: "审核员",
    member: "学生"
  }
  return map[currentProjectRole.value] ?? currentProjectRole.value
})

function goTo(path: string) {
  router.push(path)
}

function handleCommand(command: string) {
  if (command === "logout") {
    userStore.logout()
  } else if (command === "profile") {
    router.push("/profile")
  }
}

function formatRole(role: string) {
  return GLOBAL_ROLE_LABEL[role] ?? role
}

/** Menu items shown to all authenticated users */
const menuGroups = computed(() => {
  const adminFlag = isAdmin(user.value)
  const teacherFlag = isTeacher(user.value)
  const groups = []

  // 学习
  groups.push({
    title: "学习",
    items: [
      { path: "/dashboard", label: "首页", icon: House },
      { path: "/courses", label: "课程空间", icon: Folder },
      { path: "/tasks", label: "学习任务", icon: List }
    ]
  })

  // 智能体
  groups.push({
    title: "智能体",
    items: [
      { path: "/agent-workbench", label: "智能体工作台", icon: Cpu },
      { path: "/profiles", label: "学生画像", icon: UserFilled }
    ]
  })

  // 资源与审核
  groups.push({
    title: "资源与审核",
    items: [
      { path: "/resources", label: "学习资源库", icon: Collection },
      { path: "/reviews", label: "教师审核中心", icon: CircleCheck }
    ]
  })

  // AI能力
  groups.push({
    title: "AI能力",
    items: [
      { path: "/invocations", label: "调用审计", icon: Monitor },
      { path: "/costs", label: "成本统计", icon: Money },
      { path: "/prompts", label: "提示词模板", icon: Comment }
    ]
  })

  // 分析
  groups.push({
    title: "分析",
    items: [
      { path: "/analytics", label: "学习分析看板", icon: DataLine }
    ]
  })

  // 系统管理 — 仅 admin
  if (adminFlag) {
    groups.push({
      title: "系统",
      items: [
        { path: "/users", label: "用户管理", icon: UserFilled },
        { path: "/models", label: "模型与智能体配置", icon: Tools },
        { path: "/logs/operation", label: "操作日志", icon: Document },
        { path: "/logs/login", label: "登录日志", icon: Key }
      ]
    })
  } else if (teacherFlag) {
    groups.push({
      title: "系统",
      items: [
        { path: "/models", label: "模型与智能体配置", icon: Tools }
      ]
    })
  }

  return groups
})

/** Deduplicate menu groups by title, merging items with same title */
const mergedMenuGroups = computed(() => {
  const map = new Map<string, { title: string; items: any[] }>()
  for (const group of menuGroups.value) {
    if (map.has(group.title)) {
      map.get(group.title)!.items.push(...group.items)
    } else {
      map.set(group.title, { title: group.title, items: [...group.items] })
    }
  }
  return Array.from(map.values())
})
</script>

<template>
  <div class="app-wrapper">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-title">智学工坊</div>
        <div class="logo-subtitle">EduAgent Studio</div>
      </div>
      <el-menu
        :default-active="activeMenu"
        :router="false"
        class="sidebar-menu"
        background-color="#1e3a5f"
        text-color="#b0c4de"
        active-text-color="#ffffff"
      >
        <template v-for="group in mergedMenuGroups" :key="group.title">
          <el-menu-item-group :title="group.title">
            <el-menu-item
              v-for="item in group.items"
              :key="item.path"
              :index="item.path"
              @click="goTo(item.path)"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>{{ item.label }}</template>
            </el-menu-item>
          </el-menu-item-group>
        </template>
      </el-menu>
    </aside>

    <!-- 右侧主区域 -->
    <div class="main-area">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <span class="page-title">{{ route.meta.title as string || "" }}</span>
        </div>
        <div class="topbar-right">
          <!-- 当前项目角色标签（仅在项目详情页显示） -->
          <div v-if="currentProjectRoleLabel" class="project-role-badge">
            <el-tag size="small" type="warning">
              项目角色：{{ currentProjectRoleLabel }}
            </el-tag>
          </div>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span class="user-name">{{ user?.real_name || user?.username || "用户" }}</span>
              <el-tag
                v-for="role in (user?.roles || [])"
                :key="role"
                size="small"
                :type="role === 'admin' ? 'danger' : role === 'teacher' ? 'warning' : 'info'"
                style="margin-left: 4px; font-size: 11px"
              >
                {{ formatRole(role) }}
              </el-tag>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-wrapper {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background-color: #1e3a5f;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  height: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px 0;
}

.logo-title {
  font-size: 17px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 2px;
}

.logo-subtitle {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2px;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.sidebar-menu :deep(.el-menu-item-group__title) {
  padding: 8px 20px 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  font-size: 14px;
  padding-left: 20px !important;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f5f7fa;
}

.topbar {
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.project-role-badge {
  padding: 4px 8px;
  background: #fef0e6;
  border-radius: 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-name {
  font-weight: 500;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}
</style>
