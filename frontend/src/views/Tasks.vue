<template>
  <div class="placeholder-page">
    <el-result
      icon="info"
      title="任务管理"
      sub-title="任务与版本页面将在下一阶段实现"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/dashboard')">
          返回首页
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
</script>

<style scoped>
.placeholder-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
