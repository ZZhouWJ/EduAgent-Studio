<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { View, Search } from "@element-plus/icons-vue"
import { invocationsApi, type Invocation, type InvocationDetail } from "@/api/invocations"
import { projectsApi, type Project } from "@/api/projects"
import { modelsApi, type AIModel } from "@/api/models"

const loading = ref(false)
const invocations = ref<Invocation[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

// Filters
const selectedProjectId = ref<number | null>(null)
const selectedModelId = ref<number | null>(null)
const selectedStatus = ref<string | null>(null)

// Options
const projects = ref<Project[]>([])
const projectsLoading = ref(false)
const models = ref<AIModel[]>([])
const modelsLoading = ref(false)

// Detail dialog
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const currentInvocation = ref<InvocationDetail | null>(null)

onMounted(async () => {
  await loadProjects()
  await loadModels()
  await loadInvocations()
})

async function loadProjects() {
  projectsLoading.value = true
  try {
    const res = await projectsApi.list({ page: 1, page_size: 200 })
    projects.value = res.data?.items || []
  } catch {
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
}

async function loadModels() {
  modelsLoading.value = true
  try {
    const res = await modelsApi.getModels({ page: 1, page_size: 200 })
    models.value = res.data?.items || []
  } catch {
    models.value = []
  } finally {
    modelsLoading.value = false
  }
}

async function loadInvocations() {
  loading.value = true
  try {
    const res = await invocationsApi.getInvocations({
      page: page.value,
      page_size: pageSize.value,
      project_id: selectedProjectId.value || undefined,
      model_id: selectedModelId.value || undefined,
      status: selectedStatus.value || undefined
    })
    invocations.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch {
    invocations.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  loadInvocations()
}

function onPageChange(p: number) {
  page.value = p
  loadInvocations()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadInvocations()
}

function clearFilters() {
  selectedProjectId.value = null
  selectedModelId.value = null
  selectedStatus.value = null
  page.value = 1
  loadInvocations()
}

async function viewDetail(invocation: Invocation) {
  detailLoading.value = true
  detailDialogVisible.value = true
  currentInvocation.value = null
  try {
    const res = await invocationsApi.getInvocationById(invocation.invocation_id)
    currentInvocation.value = res.data
  } catch {
    detailDialogVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    success: "success",
    failed: "danger",
    timeout: "warning",
    blocked: "info"
  }
  return map[status] || ""
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    success: "成功",
    failed: "失败",
    timeout: "超时",
    blocked: "阻断"
  }
  return map[status] || status
}

function formatNumber(num: number | undefined) {
  return num != null ? num.toLocaleString() : "-"
}

function formatCost(cost: number | undefined) {
  return cost != null ? cost.toFixed(4) : "-"
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">调用审计</h1>
      <p class="page-desc">记录所有 AI 模型调用，支持追溯和成本分析</p>
    </div>

    <el-card>
      <!-- Filters -->
      <div class="filter-bar" style="margin-bottom: 16px">
        <el-select
          v-model="selectedProjectId"
          placeholder="选择项目"
          style="width: 180px"
          clearable
          filterable
          :loading="projectsLoading"
          @change="onFilterChange"
        >
          <el-option
            v-for="p in projects"
            :key="p.project_id"
            :label="p.project_name"
            :value="p.project_id"
          />
        </el-select>

        <el-select
          v-model="selectedModelId"
          placeholder="选择模型"
          style="width: 180px"
          clearable
          filterable
          :loading="modelsLoading"
          @change="onFilterChange"
        >
          <el-option
            v-for="m in models"
            :key="m.model_id"
            :label="m.display_name || m.model_name"
            :value="m.model_id"
          />
        </el-select>

        <el-select
          v-model="selectedStatus"
          placeholder="调用状态"
          style="width: 120px"
          clearable
          @change="onFilterChange"
        >
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="超时" value="timeout" />
          <el-option label="阻断" value="blocked" />
        </el-select>

        <el-button @click="clearFilters">重置</el-button>
      </div>

      <!-- Table -->
      <el-table v-loading="loading" :data="invocations" stripe>
        <el-table-column prop="invocation_id" label="调用ID" width="80" />
        <el-table-column prop="project_name" label="项目名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="task_title" label="任务标题" min-width="160" show-overflow-tooltip />
        <el-table-column label="模型名称" min-width="160">
          <template #default="{ row }">
            <div style="font-weight: 600">{{ row.model_display_name || row.model_name }}</div>
            <div style="font-size: 12px; color: #909399">{{ row.provider_name }}</div>
          </template>
        </el-table-column>
        <el-table-column label="输入Token" width="100" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.input_tokens) }}
          </template>
        </el-table-column>
        <el-table-column label="输出Token" width="100" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.output_tokens) }}
          </template>
        </el-table-column>
        <el-table-column label="延迟(ms)" width="90" align="right">
          <template #default="{ row }">
            {{ row.latency_ms != null ? row.latency_ms.toFixed(0) : "-" }}
          </template>
        </el-table-column>
        <el-table-column label="成本(元)" width="90" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600">{{ formatCost(row.cost) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="invoked_at" label="调用时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.invoked_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewDetail(row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && invocations.length === 0" description="暂无调用记录" />

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

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="调用详情" width="640px" destroy-on-close>
      <div v-loading="detailLoading">
        <template v-if="currentInvocation">
          <el-descriptions :column="2" border size="small" style="margin-bottom: 16px">
            <el-descriptions-item label="调用ID">{{ currentInvocation.invocation_id }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(currentInvocation.status)" size="small">
                {{ getStatusLabel(currentInvocation.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="项目">{{ currentInvocation.project_name }}</el-descriptions-item>
            <el-descriptions-item label="任务">{{ currentInvocation.task_title }}</el-descriptions-item>
            <el-descriptions-item label="模型">
              <div>{{ currentInvocation.model_display_name || currentInvocation.model_name }}</div>
              <div style="font-size: 12px; color: #909399">{{ currentInvocation.provider_name }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="调用人">{{ currentInvocation.invoker_real_name || "-" }}</el-descriptions-item>
            <el-descriptions-item label="输入Token" align="right">{{ formatNumber(currentInvocation.input_tokens) }}</el-descriptions-item>
            <el-descriptions-item label="输出Token" align="right">{{ formatNumber(currentInvocation.output_tokens) }}</el-descriptions-item>
            <el-descriptions-item label="延迟" align="right">
              {{ currentInvocation.latency_ms != null ? `${currentInvocation.latency_ms.toFixed(0)} ms` : "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="成本" align="right">
              <span style="color: #f56c6c; font-weight: 600">{{ formatCost(currentInvocation.cost) }} 元</span>
            </el-descriptions-item>
            <el-descriptions-item label="调用时间" :span="2">{{ formatDate(currentInvocation.invoked_at) }}</el-descriptions-item>
          </el-descriptions>

          <!-- Model Info -->
          <div v-if="currentInvocation.model_info" style="margin-bottom: 16px">
            <div style="font-weight: 600; margin-bottom: 8px">模型定价信息</div>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="模型名称">{{ currentInvocation.model_info.display_name || currentInvocation.model_info.model_name }}</el-descriptions-item>
              <el-descriptions-item label="供应商">{{ currentInvocation.model_info.provider_name }}</el-descriptions-item>
              <el-descriptions-item label="输入价格">
                {{ currentInvocation.model_info.input_price }} 元 / {{ currentInvocation.model_info.price_unit }}
              </el-descriptions-item>
              <el-descriptions-item label="输出价格">
                {{ currentInvocation.model_info.output_price }} 元 / {{ currentInvocation.model_info.price_unit }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- Input Text -->
          <div v-if="currentInvocation.input_text" style="margin-bottom: 16px">
            <div style="font-weight: 600; margin-bottom: 8px">输入内容</div>
            <div class="content-preview">{{ currentInvocation.input_text }}</div>
          </div>

          <!-- Output Text -->
          <div v-if="currentInvocation.output_text" style="margin-bottom: 16px">
            <div style="font-weight: 600; margin-bottom: 8px">输出内容预览</div>
            <div class="content-preview">{{ currentInvocation.output_text.slice(0, 1000) }}{{ currentInvocation.output_text.length > 1000 ? "..." : "" }}</div>
          </div>

          <!-- Error Message -->
          <div v-if="currentInvocation.error_message" style="margin-bottom: 16px">
            <div style="font-weight: 600; margin-bottom: 8px; color: #f56c6c">错误信息</div>
            <div class="content-preview error">{{ currentInvocation.error_message }}</div>
          </div>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { View, Search } from "@element-plus/icons-vue"
export default { components: { View, Search } }
</script>

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

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.content-preview {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.content-preview.error {
  background: #fef0f0;
  color: #f56c6c;
}
</style>
