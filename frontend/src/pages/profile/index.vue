<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useUserStore } from "@/stores/user"
import { authApi } from "@/api/auth"
import { ElMessage } from "element-plus"
import { Lock } from "@element-plus/icons-vue"

const userStore = useUserStore()

const userInfo = ref({
  username: "",
  real_name: "",
  student_no: "",
  email: "",
  phone: "",
  roles: [] as string[]
})

const passwordForm = ref({
  old_password: "",
  new_password: "",
  confirm_password: ""
})
const passwordLoading = ref(false)

onMounted(async () => {
  userInfo.value = {
    username: userStore.userInfo?.username || "",
    real_name: userStore.userInfo?.real_name || "",
    student_no: userStore.userInfo?.student_no || "",
    email: userStore.userInfo?.email || "",
    phone: userStore.userInfo?.phone || "",
    roles: userStore.userInfo?.roles || []
  }
})

const roleLabelMap: Record<string, string> = {
  admin: "管理员",
  teacher: "教师",
  project_leader: "项目负责人",
  student_member: "学生成员"
}

function formatRole(role: string) {
  return roleLabelMap[role] || role
}

async function handleChangePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.error("两次输入的密码不一致")
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    ElMessage.error("新密码长度不能少于6个字符")
    return
  }
  passwordLoading.value = true
  try {
    await authApi.changePassword(passwordForm.value.old_password, passwordForm.value.new_password)
    ElMessage.success("密码修改成功")
    passwordForm.value = {
      old_password: "",
      new_password: "",
      confirm_password: ""
    }
  } catch {
    // error handled by interceptor
  } finally {
    passwordLoading.value = false
  }
}
</script>

<template>
  <div class="page-container" style="padding: 20px; max-width: 800px">
    <div class="page-header" style="margin-bottom: 24px">
      <h1 class="page-title">个人中心</h1>
      <p class="page-desc">查看和管理您的个人账户信息</p>
    </div>

    <!-- 用户信息卡片 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <span style="font-weight: 600">基本信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ userInfo.real_name || "-" }}</el-descriptions-item>
        <el-descriptions-item label="学号">{{ userInfo.student_no || "-" }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userInfo.email || "-" }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ userInfo.phone || "-" }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag
            v-for="role in userInfo.roles"
            :key="role"
            size="small"
            type="info"
            style="margin-right: 4px"
          >
            {{ formatRole(role) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 修改密码卡片 -->
    <el-card>
      <template #header>
        <span style="font-weight: 600">修改密码</span>
      </template>
      <el-form :model="passwordForm" label-width="120px" style="max-width: 400px">
        <el-form-item label="当前密码">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码（至少6个字符）"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
            <el-icon v-if="!passwordLoading" style="margin-right: 4px"><Lock /></el-icon>
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 4px;
}

.page-desc {
  font-size: 13px;
  color: #909399;
  margin: 0;
}
</style>
