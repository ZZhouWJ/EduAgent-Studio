<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import {
  getProjectArtifactsApi
} from "@/common/apis/artifacts"
import { getProjectListApi } from "@/common/apis/projects"
import type { AdoptedOutput } from "@/common/apis/artifacts/type"
import type { Project } from "@/common/apis/projects/type"

const router = useRouter()
const loading = ref(false)
const listData = ref<AdoptedOutput[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const projectOptions = ref<{ label: string; value: number }[]>([])
const selectedProjectId = ref<number | undefined>(undefined)

async function loadProjects() {
  try {
    const res = await getProjectListApi({ page: 1, page_size: 200 })
    const items = res.data.items || []
    projectOptions.value = items.map((p: Project) => ({
      label: p.project_name,
      value: p.project_id
    }))
    if (items.length > 0 && selectedProjectId.value === undefined) {
      selectedProjectId.value = items[0].project_id
    }
  } catch { /* shown by interceptor */ }
}

async function fetchArtifacts() {
  if (!selectedProjectId.value) {
    listData.value = []
    total.value = 0
    return
  }
  loading.value = true
  try {
    const res = await getProjectArtifactsApi(selectedProjectId.value, {
      page: page.value,
      page_size: pageSize.value
    })
    listData.value = res.data.items || []
    total.value = res.data.total || 0
  } catch { /* shown by interceptor */ }
  finally { loading.value = false }
}

function handleProjectChange() {
  page.value = 1
  fetchArtifacts()
}

function handlePageChange(p: number) {
  page.value = p
  fetchArtifacts()
}

function handleSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  fetchArtifacts()
}

function goToDetail(row: AdoptedOutput) {
  router.push(`/artifacts/${row.adopted_id}`)
}

function getArtifactTypeLabel(type: string) {
  const m: Record<string, string> = {
    report_section: "报告章节",
    requirements: "需求分析",
    design: "设计文档",
    code: "代码",
    test: "测试文档",
    manual: "使用手册",
    other: "其他"
  }
  return m[type] || type
}

onMounted(async () => {
  await loadProjects()
  if (selectedProjectId.value) {
    fetchArtifacts()
  }
})
</script>

<template>
  <div class="artifact-list-page">
    <div class="page-header">
      <h2 class="page-title">成果库</h2>
      <div class="header-filters">
        <el-select
          v-model="selectedProjectId"
          placeholder="请选择项目"
          style="width: 260px"
          @change="handleProjectChange"
        >
          <el-option
            v-for="opt in projectOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-button :loading="loading" @click="fetchArtifacts">刷新</el-button>
      </div>
    </div>

    <el-alert
      v-if="!selectedProjectId"
      title="请先选择一个项目以查看成果列表"
      type="info"
      :closable="false"
      style="margin-bottom: 16px"
    />

    <el-card v-loading="loading">
      <el-table :data="listData" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="artifact_title" label="成果标题" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="goToDetail(row)">
              {{ row.artifact_title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="artifact_type" label="成果类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getArtifactTypeLabel(row.artifact_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="release_version" label="版本" width="80" align="center">
          <template #default="{ row }">{{ row.release_version || "-" }}</template>
        </el-table-column>
        <el-table-column prop="task_title" label="所属任务" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_title || "-" }}</template>
        </el-table-column>
        <el-table-column prop="output_title" label="原始输出" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.output_title || "-" }}</template>
        </el-table-column>
        <el-table-column prop="adopted_by_real_name" label="采用人" width="120" align="center">
          <template #default="{ row }">{{ row.adopted_by_real_name || row.adopted_by_username || "-" }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="采用时间" width="170" align="center">
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
          <el-empty
            :description="selectedProjectId ? '暂无成果数据' : '请先选择项目'"
          />
        </template>
      </el-table>

      <div v-if="total > 0" class="pagination-wrap">
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
.artifact-list-page {
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
