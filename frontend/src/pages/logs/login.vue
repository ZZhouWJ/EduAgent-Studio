<script setup lang="ts">
import { ref, onMounted } from "vue"
import { Search, RefreshRight } from "@element-plus/icons-vue"
import { logsApi } from "@/api/logs"

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

// Filter form
const filterForm = ref({
  username: "",
  login_status: "",
  start_date: "",
  end_date: ""
})

const statusOptions = [
  { label: "全部状态", value: "" },
  { label: "成功", value: "success" },
  { label: "失败", value: "failed" }
]

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await logsApi.loginLogs({
      page: page.value,
      page_size: pageSize.value,
      login_status: filterForm.value.login_status || undefined,
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
    username: "",
    login_status: "",
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

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    success: "success",
    failed: "danger"
  }
  return map[status] || "info"
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    success: "成功",
    failed: "失败"
  }
  return map[status] || status
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function truncateUA(ua: string | undefined, maxLen = 60): string {
  if (!ua) return "-"
  return ua.length > maxLen ? ua.substring(0, maxLen) + "..." : ua
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">登录日志</h1>
      <p class="page-desc">记录所有用户登录和登出行为，支持安全审计</p>
    </div>

    <el-card>
      <!-- 筛选面板 -->
      <div class="filter-panel">
        <div class="filter-row">
          <div class="filter-item">
            <span class="filter-label">用户名</span>
            <el-input
              v-model="filterForm.username"
              placeholder="搜索用户名"
              clearable
              style="width: 180px"
              @clear="onSearch"
              @keyup.enter="onSearch"
            />
          </div>
          <div class="filter-item">
            <span class="filter-label">登录状态</span>
            <el-select v-model="filterForm.login_status" placeholder="选择状态" clearable style="width: 140px">
              <el-option
                v-for="opt in statusOptions"
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
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column label="登录状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.login_status)">
              {{ getStatusLabel(row.login_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failure_reason" label="失败原因" min-width="140">
          <template #default="{ row }">
            <span v-if="row.login_status === 'failed'" class="fail-reason">{{ row.failure_reason || "未知原因" }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column label="User Agent" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ truncateUA(row.user_agent) }}
          </template>
        </el-table-column>
        <el-table-column prop="login_time" label="登录时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.login_time) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && tableData.length === 0" description="暂无登录日志" />

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
import { Search, RefreshRight } from "@element-plus/icons-vue"
export default { components: { Search, RefreshRight } }
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

.fail-reason {
  color: #f56c6c;
  font-size: 13px;
}
</style>
