<script setup lang="ts">
import { ref } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useUserStore } from "@/stores/user"
import { Lock, User } from "@element-plus/icons-vue"

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const loginForm = ref({
  username: "",
  password: ""
})

async function handleLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    return
  }
  loading.value = true
  try {
    await userStore.login(loginForm.value.username, loginForm.value.password)
    const redirect = (route.query.redirect as string) || "/"
    router.push(redirect)
  } catch {
    loginForm.value.password = ""
  } finally {
    loading.value = false
  }
}

function goToRegister() {
  router.push("/register")
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="title">
        <h1>智研协作 AI 项目质量审计系统</h1>
      </div>
      <div class="subtitle">面向高校项目协作的 AI 任务生成、版本管理与质量审核平台</div>
      <el-form :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-link">
        没有账号？<el-link type="primary" @click="goToRegister">注册账号</el-link>
      </div>
      <div class="test-hint">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            测试账号：admin / Admin@123456（管理员）&nbsp;&nbsp; student1 / test123（学生）
          </template>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0f2744 0%, #1e3a5f 50%, #2c5282 100%);
}

.login-card {
  width: 460px;
  max-width: 90%;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 16px;
  padding: 40px 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.title {
  text-align: center;
  margin-bottom: 8px;
}

.title h1 {
  font-size: 22px;
  font-weight: 700;
  color: #1e3a5f;
  letter-spacing: 1px;
}

.subtitle {
  text-align: center;
  font-size: 13px;
  color: #8492a6;
  margin-bottom: 32px;
}

.login-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #606266;
  margin-bottom: 16px;
}

.test-hint {
  margin-top: 16px;
}

.test-hint code {
  background: #f0f0f0;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: "Courier New", monospace;
  color: #c0392b;
}
</style>
