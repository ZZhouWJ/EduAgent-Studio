<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { Lock, User } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { authApi } from "@/api/auth"

const router = useRouter()

const loading = ref(false)
const registerForm = ref({
  username: "",
  real_name: "",
  student_no: "",
  email: "",
  phone: "",
  password: "",
  confirm_password: ""
})

async function handleRegister() {
  if (registerForm.value.password !== registerForm.value.confirm_password) {
    ElMessage.error("两次输入的密码不一致")
    return
  }
  loading.value = true
  try {
    await authApi.register({
      username: registerForm.value.username,
      real_name: registerForm.value.real_name,
      student_no: registerForm.value.student_no || undefined,
      email: registerForm.value.email || undefined,
      phone: registerForm.value.phone || undefined,
      password: registerForm.value.password,
      confirm_password: registerForm.value.confirm_password
    })
    ElMessage.success("注册成功，请登录")
    router.push("/login")
  } catch {
    // error is handled by axios interceptor
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.push("/login")
}
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <div class="title">
        <h1>注册账号</h1>
      </div>
      <div class="subtitle">加入智研协作平台</div>
      <el-form :model="registerForm" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input
            v-model="registerForm.username"
            placeholder="用户名（必填，最少3个字符）"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.real_name"
            placeholder="真实姓名（必填）"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.student_no"
            placeholder="学号（选填）"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.email"
            placeholder="邮箱（选填）"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.phone"
            placeholder="手机号（选填）"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="密码（必填，最少6个字符）"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.confirm_password"
            type="password"
            placeholder="确认密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="register-btn" @click="handleRegister">
            注 册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-link">
        已有账号？<el-link type="primary" @click="goToLogin">立即登录</el-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0f2744 0%, #1e3a5f 50%, #2c5282 100%);
}

.register-card {
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

.register-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: #606266;
  margin-top: 16px;
}
</style>
