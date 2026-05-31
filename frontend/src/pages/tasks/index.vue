<script setup lang="ts">
</script>

<template>
  <div class="tasks-page">
    <el-result
      icon="info"
      title="任务与版本"
      sub-title="任务通过项目访问，请在项目详情页查看任务列表"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/projects')">
          前往项目空间
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<style lang="scss" scoped>
.tasks-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
</style>
