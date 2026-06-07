<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useUserStore } from "@/stores/user"
import { authApi, type Role } from "@/api/auth"
import { ElMessage } from "element-plus"
import { Lock } from "@element-plus/icons-vue"

const userStore = useUserStore()

// --- 基本信息编辑 ---
const profileForm = ref({
  real_name: "",
  student_no: "",
  email: "",
  phone: ""
})
const profileLoading = ref(false)
const profileEditing = ref(false)

// --- 角色修改 ---
const allRoles = ref<Role[]>([])
const selectedRoleIds = ref<number[]>([])
const roleLoading = ref(false)
const roleEditing = ref(false)

// --- 密码修改 ---
const passwordForm = ref({
  old_password: "",
  new_password: "",
  confirm_password: ""
})
const passwordLoading = ref(false)

onMounted(async () => {
  // 填充基本信息
  profileForm.value = {
    real_name: userStore.userInfo?.real_name || "",
    student_no: userStore.userInfo?.student_no || "",
    email: userStore.userInfo?.email || "",
    phone: userStore.userInfo?.phone || ""
  }

  // 加载角色列表并初始化当前用户角色
  try {
    const res = await authApi.listRoles()
    allRoles.value = (res.data as unknown as Role[]).filter((r) => r.role_code !== "admin")
    // 从 userInfo.roles 中提取 role_id
    const userRoleCodes: string[] = userStore.userInfo?.roles || []
    selectedRoleIds.value = allRoles.value
      .filter((r) => userRoleCodes.includes(r.role_code))
      .map((r) => r.role_id)
  } catch {
    // ignore
  }
})

async function handleSaveProfile() {
  if (!profileForm.value.real_name.trim()) {
    ElMessage.error("真实姓名不能为空")
    return
  }
  profileLoading.value = true
  try {
    await authApi.updateProfile({
      real_name: profileForm.value.real_name,
      student_no: profileForm.value.student_no || undefined,
      email: profileForm.value.email || undefined,
      phone: profileForm.value.phone || undefined
    })
    // 同步更新 store
    if (userStore.userInfo) {
      userStore.userInfo.real_name = profileForm.value.real_name
      userStore.userInfo.student_no = profileForm.value.student_no || undefined
      userStore.userInfo.email = profileForm.value.email || undefined
      userStore.userInfo.phone = profileForm.value.phone || undefined
    }
    ElMessage.success("基本信息更新成功")
    profileEditing.value = false
  } catch {
    // error handled by interceptor
  } finally {
    profileLoading.value = false
  }
}

async function handleSaveRoles() {
  roleLoading.value = true
  try {
    await authApi.updateMyRoles(selectedRoleIds.value)
    // 同步更新 store
    if (userStore.userInfo) {
      const newRoles = allRoles.value
        .filter((r) => selectedRoleIds.value.includes(r.role_id))
        .map((r) => r.role_code)
      userStore.userInfo.roles = newRoles
    }
    ElMessage.success("角色更新成功")
    roleEditing.value = false
  } catch {
    // error handled by interceptor
  } finally {
    roleLoading.value = false
  }
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

const roleLabelMap: Record<string, string> = {
  admin: "管理员",
  teacher: "教师",
  project_leader: "项目负责人",
  student_member: "学生成员"
}

function formatRole(role: string) {
  return roleLabelMap[role] || role
}
</script>

<template>
  <div class="page-container" style="padding: 20px; max-width: 800px">
    <div class="page-header" style="margin-bottom: 24px">
      <h1 class="page-title">个人中心</h1>
      <p class="page-desc">查看和管理您的个人账户信息</p>
    </div>

    <!-- 用户名 & 角色（只读展示） -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <span style="font-weight: 600">账户信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ userStore.userInfo?.username }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag
            v-for="role in userStore.userInfo?.roles"
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

    <!-- 基本信息（可编辑） -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">基本信息</span>
          <el-button
            v-if="!profileEditing"
            size="small"
            type="primary"
            @click="profileEditing = true"
          >
            编辑
          </el-button>
        </div>
      </template>

      <template v-if="profileEditing">
        <el-form :model="profileForm" label-width="100px" style="max-width: 500px">
          <el-form-item label="真实姓名" required>
            <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item label="学号">
            <el-input v-model="profileForm.student_no" placeholder="请输入学号" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="profileLoading" @click="handleSaveProfile">
              保存
            </el-button>
            <el-button style="margin-left: 8px" @click="profileEditing = false">
              取消
            </el-button>
          </el-form-item>
        </el-form>
      </template>

      <template v-else>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="真实姓名">{{ profileForm.real_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="学号">{{ profileForm.student_no || "-" }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ profileForm.email || "-" }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ profileForm.phone || "-" }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-card>

    <!-- 角色修改 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">角色设置</span>
          <el-button
            v-if="!roleEditing"
            size="small"
            type="primary"
            @click="roleEditing = true"
          >
            修改角色
          </el-button>
        </div>
      </template>

      <template v-if="roleEditing">
        <el-checkbox-group v-model="selectedRoleIds" style="margin-bottom: 16px">
          <el-checkbox
            v-for="role in allRoles"
            :key="role.role_id"
            :value="role.role_id"
            style="display: block; margin-bottom: 8px; margin-left: 0"
          >
            {{ role.role_name }}
          </el-checkbox>
        </el-checkbox-group>
        <div>
          <el-button type="primary" :loading="roleLoading" @click="handleSaveRoles">
            保存
          </el-button>
          <el-button style="margin-left: 8px" @click="roleEditing = false">
            取消
          </el-button>
        </div>
      </template>

      <template v-else>
        <el-tag
          v-for="role in userStore.userInfo?.roles"
          :key="role"
          size="small"
          type="info"
          style="margin-right: 8px"
        >
          {{ formatRole(role) }}
        </el-tag>
        <span v-if="!userStore.userInfo?.roles?.length" style="color: #909399">无</span>
      </template>
    </el-card>

    <!-- 修改密码 -->
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
