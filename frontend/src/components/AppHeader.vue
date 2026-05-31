<template>
  <div class="app-header">
    <div class="header-left">
      <el-button
        text
        class="collapse-btn"
        @click="$emit('toggle-collapse')"
      >
        <el-icon size="20">
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </el-button>
      <span class="system-title">智研协作 AI 项目质量审计系统</span>
    </div>

    <div class="header-right">
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-icon><UserFilled /></el-icon>
          <span class="username">{{ userStore.userInfo?.real_name || userStore.userInfo?.username || '用户' }}</span>
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon> 个人中心
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

defineProps({
  isCollapse: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-collapse'])

const router = useRouter()
const userStore = useUserStore()

async function handleCommand(command) {
  if (command === 'logout') {
    await userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    // 占位，后续阶段实现
  }
}
</script>

<style scoped>
.app-header {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  color: #606266;
}

.system-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e3a5f;
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: background 0.2s;
  color: #606266;
  font-size: 14px;
}

.user-info:hover {
  background: #f5f7fa;
}

.username {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
