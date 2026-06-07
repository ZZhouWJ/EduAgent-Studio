<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { authApi, type User, type Role } from "@/api/auth"
import { UserFilled, Lock, Unlock } from "@element-plus/icons-vue"

const loading = ref(false)
const users = ref<User[]>([])
const roles = ref<Role[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref("")
const statusFilter = ref<string | undefined>(undefined)

const roleDialogVisible = ref(false)
const selectedUser = ref<User | null>(null)
const selectedRoleIds = ref<number[]>([])
const roleLoading = ref(false)

onMounted(async () => {
  await loadRoles()
  await loadUsers()
})

async function loadRoles() {
  try {
    const res = await authApi.listRoles()
    roles.value = res.data || []
  } catch {
    roles.value = []
  }
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await authApi.listUsers({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      status: statusFilter.value
    })
    users.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch {
    users.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadUsers()
}

function onStatusFilterChange() {
  page.value = 1
  loadUsers()
}

function onPageChange(p: number) {
  page.value = p
  loadUsers()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadUsers()
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    active: "success",
    inactive: "info",
    suspended: "danger"
  }
  return map[status] || "info"
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    active: "正常",
    inactive: "停用",
    suspended: "封禁"
  }
  return map[status] || status
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function openRoleDialog(user: User) {
  selectedUser.value = user
  selectedRoleIds.value = user.roles.map((r) => {
    const role = roles.value.find((role) => role.role_code === r)
    return role?.role_id || 0
  }).filter((id) => id > 0)
  roleDialogVisible.value = true
}

async function handleUpdateRoles() {
  if (!selectedUser.value) return
  roleLoading.value = true
  try {
    await authApi.updateUserRoles(selectedUser.value.user_id, selectedRoleIds.value)
    ElMessage.success("角色分配成功")
    roleDialogVisible.value = false
    loadUsers()
  } catch {
    // error handled by interceptor
  } finally {
    roleLoading.value = false
  }
}

async function handleToggleStatus(user: User) {
  const newStatus = user.status === "active" ? "inactive" : "active"
  const action = newStatus === "active" ? "启用" : "禁用"
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${user.real_name || user.username} 吗？`, "确认操作", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    })
    await authApi.updateUserStatus(user.user_id, newStatus)
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch {
    // user cancelled or error
  }
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">用户管理</h1>
      <p class="page-desc">管理系统用户账户和角色分配</p>
    </div>

    <el-card>
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span style="font-weight: 600">用户列表</span>
          <div style="display: flex; align-items: center; gap: 12px">
            <el-input
              v-model="keyword"
              placeholder="搜索用户名/姓名"
              style="width: 200px"
              clearable
              @clear="onSearch"
              @keyup.enter="onSearch"
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="statusFilter"
              placeholder="全部状态"
              clearable
              style="width: 120px"
              @change="onStatusFilterChange"
            >
              <el-option label="正常" value="active" />
              <el-option label="停用" value="inactive" />
              <el-option label="封禁" value="suspended" />
            </el-select>
            <el-button type="primary" @click="onSearch">搜索</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="username" label="用户名" min-width="100" />
        <el-table-column prop="real_name" label="姓名" min-width="100">
          <template #default="{ row }">
            {{ row.real_name || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="student_no" label="学号" min-width="120">
          <template #default="{ row }">
            {{ row.student_no || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="160">
          <template #default="{ row }">
            {{ row.email || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" min-width="130">
          <template #default="{ row }">
            {{ row.phone || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="160">
          <template #default="{ row }">
            <el-tag
              v-for="role in row.roles"
              :key="role"
              size="small"
              type="info"
              style="margin-right: 4px; margin-bottom: 2px"
            >
              {{ role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              <el-icon v-if="row.status === 'active'" style="margin-right: 2px"><Lock /></el-icon>
              <el-icon v-else style="margin-right: 2px"><Unlock /></el-icon>
              {{ row.status === "active" ? "禁用" : "启用" }}
            </el-button>
            <el-button size="small" type="primary" @click="openRoleDialog(row)">
              分配角色
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="onPageChange"
          @size-change="onPageSizeChange"
        />
      </div>
    </el-card>

    <!-- 分配角色对话框 -->
    <el-dialog v-model="roleDialogVisible" title="分配角色" width="420px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <span>{{ selectedUser?.real_name || selectedUser?.username }}</span>
        </el-form-item>
        <el-form-item label="选择角色">
          <el-select v-model="selectedRoleIds" multiple placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="role in roles"
              :key="role.role_id"
              :label="role.role_name"
              :value="role.role_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="roleLoading" @click="handleUpdateRoles">保存</el-button>
      </template>
    </el-dialog>
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

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
