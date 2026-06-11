<script setup lang="ts">
import { useRouter } from "vue-router"
import { ArrowLeft, House } from "@element-plus/icons-vue"

const router = useRouter()

function goHome() {
  router.push("/dashboard")
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-code">403</div>
      <div class="error-title">权限不足</div>
      <div class="error-desc">
        您当前的身份无权访问该页面<br />
        如需访问权限，请联系系统管理员
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上一页
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.error-content {
  text-align: center;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #e6a23c;
  line-height: 1;
  margin-bottom: 16px;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
}

.error-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.error-desc {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 32px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
