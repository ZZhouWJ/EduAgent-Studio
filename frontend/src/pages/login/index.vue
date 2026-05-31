<script lang="ts" setup>
import type { FormRules } from "element-plus"
import type { LoginRequestData } from "./apis/type"
import ThemeSwitch from "@@/components/ThemeSwitch/index.vue"
import { Lock, User } from "@element-plus/icons-vue"
import { useSettingsStore } from "@/pinia/stores/settings"
import { useUserStore } from "@/pinia/stores/user"
import { loginApi } from "./apis"

const route = useRoute()
const router = useRouter()

const userStore = useUserStore()
const settingsStore = useSettingsStore()

/** 登录表单元素的引用 */
const loginFormRef = ref<InstanceType<typeof ElForm> | null>(null)

/** 登录按钮 Loading */
const loading = ref(false)

/** 登录表单数据（已移除验证码字段） */
const loginFormData: LoginRequestData = reactive({
  username: "",
  password: ""
})

/** 登录表单校验规则 */
const loginFormRules: FormRules<LoginRequestData> = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }]
}

/** 登录 */
function handleLogin() {
  loginFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    loginApi(loginFormData)
      .then(({ data }) => {
        userStore.setToken(data.token)
        router.push(route.query.redirect ? decodeURIComponent(route.query.redirect as string) : "/")
      })
      .catch(() => {
        loginFormData.password = ""
      })
      .finally(() => {
        loading.value = false
      })
  })
}
</script>

<template>
  <div class="login-container">
    <ThemeSwitch v-if="settingsStore.showThemeSwitch" class="theme-switch" />
    <div class="login-card">
      <div class="title">
        <h1>智研协作 AI 项目质量审计系统</h1>
      </div>
      <div class="subtitle">
        面向高校项目协作的 AI 任务生成、版本管理与质量审核平台
      </div>
      <div class="content">
        <el-form
          ref="loginFormRef"
          :model="loginFormData"
          :rules="loginFormRules"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model.trim="loginFormData.username"
              placeholder="用户名"
              type="text"
              tabindex="1"
              :prefix-icon="User"
              size="large"
              clearable
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model.trim="loginFormData.password"
              placeholder="密码"
              type="password"
              tabindex="2"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          <el-button
            :loading="loading"
            type="primary"
            size="large"
            @click.prevent="handleLogin"
          >
            登 录
          </el-button>
        </el-form>
      </div>
      <div class="test-account-hint">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            测试账号（数据库初始化后使用）：
            <code>admin</code> / <code>Admin@123456</code>
          </template>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100%;
  background: linear-gradient(135deg, #0f2744 0%, #1e3a5f 50%, #2c5282 100%);
  .theme-switch {
    position: fixed;
    top: 5%;
    right: 5%;
    cursor: pointer;
  }
  .login-card {
    width: 460px;
    max-width: 90%;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    background-color: rgba(255, 255, 255, 0.97);
    overflow: hidden;
    padding: 40px 36px;
    .title {
      text-align: center;
      margin-bottom: 8px;
      h1 {
        font-size: 22px;
        font-weight: 700;
        color: #1e3a5f;
        letter-spacing: 1px;
      }
    }
    .subtitle {
      text-align: center;
      font-size: 13px;
      color: #8492a6;
      margin-bottom: 32px;
    }
    .content {
      .el-button {
        width: 100%;
        margin-top: 10px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 4px;
      }
    }
    .test-account-hint {
      margin-top: 16px;
      code {
        background: #f0f0f0;
        padding: 1px 4px;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        color: #c0392b;
      }
    }
  }
}
</style>
