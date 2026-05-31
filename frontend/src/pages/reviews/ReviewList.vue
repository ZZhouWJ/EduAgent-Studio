<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import {
  getPendingReviewsApi
} from "@/common/apis/reviews"
import { getProjectListApi } from "@/common/apis/projects"
import type { ReviewRequest } from "@/common/apis/reviews/type"
import type { Project } from "@/common/apis/projects/type"

const router = useRouter()
const loading = ref(false)
const listData = ref<ReviewRequest[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const projectOptions = ref<{ label: string; value: number }[]>([])
const filterProjectId = ref<number | undefined>(undefined)

async function loadProjects() {
  try {
    const res = await getProjectListApi({ page: 1, page_size: 200 })
    const items = res.data.items || []
    projectOptions.value = items.map((p: Project) => ({
      label: p.project_name,
      value: p.project_id
    }))
  } catch { /* shown by interceptor */ }
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getPendingReviewsApi({
      page: page.value,
      page_size: pageSize.value,
      project_id: filterProjectId.value
    })
    listData.value = res.data.items || []
    total.value = res.data.total || 0
  } catch { /* shown by interceptor */ }
  finally { loading.value = false }
}

function handlePageChange(p: number) {
  page.value = p
  fetchList()
}

function handleSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  fetchList()
}

function goToDetail(row: ReviewRequest) {
  router.push(`/reviews/${row.request_id}`)
}

function getStatusType(status: string) {
  const m: Record<string, string> = {
    pending: "warning", approved: "success",
    rejected: "danger", revision_required: "info"
  }
  return m[status] || "info"
}

function getStatusLabel(status: string) {
  const m: Record<string, string> = {
    pending: "待审核", approved: "已通过",
    rejected: "已拒绝", revision_required: "需修改"
  }
  return m[status] || status
}

onMounted(() => {
  loadProjects()
  fetchList()
})
</script>

<template>
  <div class="review-list-page">
    <div class="page-header">
      <h2 class="page-title">审核中心</h2>
      <div class="header-filters">
        <el-select
          v-model="filterProjectId"
          placeholder="全部项目"
          clearable
          style="width: 200px"
          @change="() => { page = 1; fetchList() }"
        >
          <el-option label="全部项目" :value="undefined" />
          <el-option
            v-for="opt in projectOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-button :loading="loading" @click="fetchList">刷新</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-table :data="listData" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="project_name" label="项目名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.project_name || "-" }}</template>
        </el-table-column>
        <el-table-column prop="task_title" label="任务标题" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_title || "-" }}</template>
        </el-table-column>
        <el-table-column prop="output_title" label="输出标题" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.output_title || "-" }}</template>
        </el-table-column>
        <el-table-column prop="submitter_real_name" label="提交人" width="120" align="center">
          <template #default="{ row }">{{ row.submitter_real_name || row.submitter_username || "-" }}</template>
        </el-table-column>
        <el-table-column prop="reviewer_real_name" label="审核人" width="120" align="center">
          <template #default="{ row }">{{ row.reviewer_real_name || row.reviewer_username || "-" }}</template>
        </el-table-column>
        <el-table-column prop="request_status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.request_status)">
              {{ getStatusLabel(row.request_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submit_note" label="提交说明" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.submit_note || "-" }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="170" align="center">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="goToDetail(row)">查看</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无待审核数据" />
        </template>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.review-list-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}
.header-filters {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
