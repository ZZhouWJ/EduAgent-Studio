<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-decoration">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>

    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="logo-area">
            <el-icon class="logo-icon" :size="40"><Monitor /></el-icon>
          </div>
          <h1 class="system-name">智研协作 AI 项目质量审计系统</h1>
          <p class="system-subtitle">
            面向高校项目协作的 AI 任务生成、版本管理与质量审核平台
          </p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="test-account-hint"
          >
            <template #title>
              测试账号（请在数据库初始化后使用）：
              <code>admin</code> / <code>Admin@123456</code>
            </template>
          </el-alert>
        </div>
      </div>

      <p class="copyright">
        &copy; 2026 智研协作 AI 项目质量审计系统 — 仅供课程设计使用
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login({
      username: form.username,
      password: form.password,
    })
    await userStore.fetchCurrentUser()
    ElMessage.success('登录成功')

    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    // 错误已在 axios 拦截器中通过 ElMessage 提示
    console.error('Login failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f2744 0%, #1e3a5f 50%, #2c5282 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-decoration {
  position: absolute;
  inset: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
}

.circle-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
}

.circle-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
}

.circle-3 {
  width: 300px;
  height: 300px;
  top: 50%;
  left: 10%;
  background: rgba(255, 255, 255, 0.02);
}

.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 460px;
  padding: 0 20px;
}

.login-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 16px;
  padding: 40px 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-area {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.logo-icon {
  color: #1e3a5f;
}

.system-name {
  font-size: 22px;
  font-weight: 700;
  color: #1e3a5f;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.system-subtitle {
  font-size: 13px;
  color: #8492a6;
  line-height: 1.5;
}

.login-form {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  background: #1e3a5f;
  border-color: #1e3a5f;
}

.login-btn:hover {
  background: #2c5282;
  border-color: #2c5282;
}

.login-footer {
  margin-top: 8px;
}

.test-account-hint {
  font-size: 12px;
}

.test-account-hint code {
  background: #f0f0f0;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #c0392b;
}

.copyright {
  margin-top: 20px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
}
</style>
