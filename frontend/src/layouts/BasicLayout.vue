<template>
  <div class="basic-layout">
    <div class="layout-sidebar" :class="{ collapsed: isCollapse }">
      <AppSidebar :is-collapse="isCollapse" />
    </div>

    <div class="layout-main">
      <div class="layout-header">
        <AppHeader :is-collapse="isCollapse" @toggle-collapse="isCollapse = !isCollapse" />
      </div>

      <div class="layout-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

const isCollapse = ref(false)
</script>

<style scoped>
.basic-layout {
  display: flex;
  width: 100%;
  height: 100%;
}

.layout-sidebar {
  width: 220px;
  height: 100%;
  transition: width 0.3s;
  flex-shrink: 0;
}

.layout-sidebar.collapsed {
  width: 64px;
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-header {
  flex-shrink: 0;
}

.layout-content {
  flex: 1;
  overflow-y: auto;
  background: #f2f5f9;
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
