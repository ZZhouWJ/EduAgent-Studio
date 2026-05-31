<template>
  <el-menu
    :default-active="activeMenu"
    class="app-sidebar"
    background-color="#1e3a5f"
    text-color="#c8d6e5"
    active-text-color="#ffffff"
    :collapse="isCollapse"
    :router="false"
    @select="handleSelect"
  >
    <div class="sidebar-header">
      <h2 v-show="!isCollapse">智研协作</h2>
      <h2 v-show="isCollapse">协</h2>
    </div>

    <el-menu-item index="/dashboard">
      <el-icon><HomeFilled /></el-icon>
      <template #title>首页</template>
    </el-menu-item>

    <el-menu-item index="/projects">
      <el-icon><FolderOpened /></el-icon>
      <template #title>项目空间</template>
    </el-menu-item>

    <el-menu-item index="/tasks">
      <el-icon><List /></el-icon>
      <template #title>任务与版本</template>
    </el-menu-item>

    <el-menu-item index="/reviews">
      <el-icon><CircleCheck /></el-icon>
      <template #title>审核中心</template>
    </el-menu-item>

    <el-menu-item index="/artifacts">
      <el-icon><Collection /></el-icon>
      <template #title>成果库</template>
    </el-menu-item>

    <el-menu-item index="/statistics">
      <el-icon><DataLine /></el-icon>
      <template #title>统计看板</template>
    </el-menu-item>

    <el-menu-item index="/models">
      <el-icon><Cpu /></el-icon>
      <template #title>模型管理</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

defineProps({
  isCollapse: {
    type: Boolean,
    default: false,
  },
})

const activeMenu = computed(() => route.path)

function handleSelect(index) {
  router.push(index)
}
</script>

<style scoped>
.app-sidebar {
  height: 100%;
  border-right: none;
  user-select: none;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 2px;
}
</style>
