<script setup lang="ts">
import { computed } from "vue"
import { useUserStore } from "@/stores/user"
import { useRouter, useRoute } from "vue-router"
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

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const menuGroups = [
  {
    title: "项目",
    items: [
      { path: "/dashboard", label: "首页", icon: House },
      { path: "/projects", label: "项目空间", icon: Folder }
    ]
  },
  {
    title: "任务",
    items: [
      { path: "/tasks", label: "任务与版本", icon: List }
    ]
  },
  {
    title: "AI能力",
    items: [
      { path: "/generate", label: "AI 生成", icon: Cpu },
      { path: "/prompts", label: "提示词管理", icon: Comment },
      { path: "/invocations", label: "调用审计", icon: Monitor },
      { path: "/costs", label: "成本统计", icon: Money }
    ]
  },
  {
    title: "协作",
    items: [
      { path: "/reviews", label: "审核中心", icon: CircleCheck },
      { path: "/artifacts", label: "成果库", icon: Collection }
    ]
  },
  {
    title: "系统",
    items: [
      { path: "/users", label: "用户管理", icon: UserFilled },
      { path: "/models", label: "模型管理", icon: Tools },
      { path: "/statistics", label: "统计看板", icon: DataLine },
      { path: "/logs/operation", label: "操作日志", icon: Document },
      { path: "/logs/login", label: "登录日志", icon: Key }
    ]
  }
]

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

const roleLabelMap: Record<string, string> = {
  admin: "管理员",
  teacher: "教师",
  project_leader: "项目负责人",
  student_member: "学生成员"
}

function formatRole(role: string) {
  return roleLabelMap[role] || role
}
</script>

<template>
  <div class="app-wrapper">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-title">智研协作</div>
        <div class="logo-subtitle">AI 项目质量审计系统</div>
      </div>
      <el-menu
        :default-active="activeMenu"
        :router="false"
        class="sidebar-menu"
        background-color="#1e3a5f"
        text-color="#b0c4de"
        active-text-color="#ffffff"
      >
        <template v-for="group in menuGroups" :key="group.title">
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
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span class="user-name">{{ userStore.userInfo?.real_name || userStore.userInfo?.username || "用户" }}</span>
              <el-tag
                v-for="role in (userStore.userInfo?.roles || [])"
                :key="role"
                size="small"
                type="info"
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
