<script setup lang="ts">
import { ref, onMounted } from "vue"
import { Search, RefreshRight } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { logsApi } from "@/api/logs"
import { usersApi } from "@/api/users"

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

// Filter form
const filterForm = ref({
  user_id: undefined as number | undefined,
  target_type: "",
  action_type: "",
  start_date: "",
  end_date: ""
})

// User list for dropdown
const userList = ref<any[]>([])
const usersLoading = ref(false)

const targetTypeOptions = [
  { label: "全部", value: "" },
  { label: "项目", value: "project" },
  { label: "任务", value: "task" },
  { label: "输出", value: "output" },
  { label: "审核", value: "review" },
  { label: "用户", value: "user" },
  { label: "模板", value: "template" },
  { label: "模型", value: "model" }
]

const actionTypeOptions = [
  { label: "全部", value: "" },
  { label: "创建", value: "create" },
  { label: "更新", value: "update" },
  { label: "删除", value: "delete" },
  { label: "登录", value: "login" },
  { label: "登出", value: "logout" },
  { label: "生成", value: "generate" },
  { label: "审核", value: "review" },
  { label: "采纳", value: "adopt" },
  { label: "合并", value: "merge" }
]

onMounted(() => {
  loadUsers()
  loadData()
})

async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await usersApi.list({ page: 1, page_size: 500 })
    userList.value = res.data?.items || []
  } catch {
    userList.value = []
  } finally {
    usersLoading.value = false
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await logsApi.operationLogs({
      page: page.value,
      page_size: pageSize.value,
      user_id: filterForm.value.user_id,
      target_type: filterForm.value.target_type || undefined,
      action_type: filterForm.value.action_type || undefined,
      start_date: filterForm.value.start_date || undefined,
      end_date: filterForm.value.end_date || undefined
    })
    tableData.value = res.data.items || []
    total.value = res.data.total || 0
  } catch {
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadData()
}

function onReset() {
  filterForm.value = {
    user_id: undefined,
    target_type: "",
    action_type: "",
    start_date: "",
    end_date: ""
  }
  page.value = 1
  loadData()
}

function onPageChange(p: number) {
  page.value = p
  loadData()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadData()
}

function getActionTypeTagType(action: string): string {
  const map: Record<string, string> = {
    create: "primary",
    update: "warning",
    delete: "danger",
    login: "info",
    logout: "info",
    generate: "",
    review: "warning",
    adopt: "success",
    merge: ""
  }
  return map[action] || "info"
}

function getActionTypeLabel(action: string): string {
  const map: Record<string, string> = {
    create: "创建",
    update: "更新",
    delete: "删除",
    login: "登录",
    logout: "登出",
    generate: "生成",
    review: "审核",
    adopt: "采纳",
    merge: "合并"
  }
  return map[action] || action
}

function getTargetTypeLabel(type: string): string {
  const map: Record<string, string> = {
    project: "项目",
    task: "任务",
    output: "输出",
    review: "审核",
    user: "用户",
    template: "模板",
    model: "模型"
  }
  return map[type] || type
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function truncateValue(val: string | undefined, maxLen = 50): string {
  if (!val) return "-"
  return val.length > maxLen ? val.substring(0, maxLen) + "..." : val
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">操作日志</h1>
      <p class="page-desc">记录所有用户在系统中的操作行为，支持追溯和审计</p>
    </div>

    <el-card>
      <!-- 筛选面板 -->
      <div class="filter-panel">
        <div class="filter-row">
          <div class="filter-item">
            <span class="filter-label">操作人</span>
            <el-select
              v-model="filterForm.user_id"
              placeholder="选择操作人"
              clearable
              filterable
              style="width: 180px"
            >
              <el-option
                v-for="u in userList"
                :key="u.user_id"
                :label="u.real_name || u.username"
                :value="u.user_id"
              />
            </el-select>
          </div>
          <div class="filter-item">
            <span class="filter-label">操作对象类型</span>
            <el-select v-model="filterForm.target_type" placeholder="选择对象类型" clearable style="width: 160px">
              <el-option
                v-for="opt in targetTypeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>
          <div class="filter-item">
            <span class="filter-label">操作类型</span>
            <el-select v-model="filterForm.action_type" placeholder="选择操作类型" clearable style="width: 140px">
              <el-option
                v-for="opt in actionTypeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>
          <div class="filter-item">
            <span class="filter-label">开始日期</span>
            <el-date-picker
              v-model="filterForm.start_date"
              type="date"
              placeholder="选择开始日期"
              style="width: 160px"
              value-format="YYYY-MM-DD"
            />
          </div>
          <div class="filter-item">
            <span class="filter-label">结束日期</span>
            <el-date-picker
              v-model="filterForm.end_date"
              type="date"
              placeholder="选择结束日期"
              style="width: 160px"
              value-format="YYYY-MM-DD"
            />
          </div>
        </div>
        <div class="filter-actions">
          <el-button type="primary" @click="onSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="onReset">
            <el-icon><RefreshRight /></el-icon> 重置
          </el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="tableData" stripe style="margin-top: 16px">
        <el-table-column prop="log_id" label="日志ID" width="80" />
        <el-table-column label="操作人" width="120">
          <template #default="{ row }">
            {{ row.real_name || row.username || "-" }}
          </template>
        </el-table-column>
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getActionTypeTagType(row.action_type)">
              {{ getActionTypeLabel(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作对象" min-width="150">
          <template #default="{ row }">
            <span>{{ getTargetTypeLabel(row.target_type) }}</span>
            <el-tag size="small" style="margin-left: 4px" type="info">#{{ row.target_id }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action_desc" label="操作描述" min-width="180" show-overflow-tooltip />
        <el-table-column label="详情摘要" min-width="200">
          <template #default="{ row }">
            <template v-if="row.old_value || row.new_value">
              <span class="value-change">
                <span class="old-value">{{ truncateValue(row.old_value) }}</span>
                <el-icon class="arrow-icon"><DArrowRight /></el-icon>
                <span class="new-value">{{ truncateValue(row.new_value) }}</span>
              </span>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && tableData.length === 0" description="暂无日志数据" />

      <!-- 分页 -->
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
  </div>
</template>

<script lang="ts">
import { Search, RefreshRight, DArrowRight } from "@element-plus/icons-vue"
export default { components: { Search, RefreshRight, DArrowRight } }
</script>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.value-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.old-value {
  color: #f56c6c;
  text-decoration: line-through;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.new-value {
  color: #67c23a;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  color: #909399;
  font-size: 12px;
}
</style>
