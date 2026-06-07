<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { costsApi, type CostSummary, type ModelCostStat, type ProjectCostStat } from "@/api/costs"
import { projectsApi, type Project } from "@/api/projects"
import { modelsApi, type AIModel } from "@/api/models"

const loading = ref(false)
const activeTab = ref("by_model")

// Summary cards
const summary = ref({
  total_cost: 0,
  monthly_cost: 0,
  total_invocations: 0,
  avg_cost_per_invocation: 0,
  input_cost: 0,
  output_cost: 0,
  total_tokens: 0
})

// Filter values
const startDate = ref<string>("")
const endDate = ref<string>("")
const selectedProjectId = ref<number | null>(null)
const selectedModelId = ref<number | null>(null)

// Options
const projects = ref<Project[]>([])
const projectsLoading = ref(false)
const models = ref<AIModel[]>([])
const modelsLoading = ref(false)

// Data
const modelStats = ref<ModelCostStat[]>([])
const projectStats = ref<ProjectCostStat[]>([])

onMounted(async () => {
  await loadProjects()
  await loadModels()
  await loadCosts()
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

async function loadCosts() {
  loading.value = true
  try {
    const res = await costsApi.getCosts({
      date_from: startDate.value || undefined,
      date_to: endDate.value || undefined,
      project_id: selectedProjectId.value || undefined,
      model_id: selectedModelId.value || undefined
    })

    const data = res.data
    summary.value = {
      total_cost: data.total_cost || 0,
      monthly_cost: 0,
      total_invocations: data.total_tokens || 0,
      avg_cost_per_invocation: data.total_tokens ? data.total_cost / data.total_tokens : 0,
      input_cost: data.input_cost || 0,
      output_cost: data.output_cost || 0,
      total_tokens: data.total_tokens || 0
    }
    modelStats.value = data.cost_by_model || []
    projectStats.value = data.cost_by_project || []
  } catch {
    summary.value = {
      total_cost: 0,
      monthly_cost: 0,
      total_invocations: 0,
      avg_cost_per_invocation: 0,
      input_cost: 0,
      output_cost: 0,
      total_tokens: 0
    }
    modelStats.value = []
    projectStats.value = []
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  loadCosts()
}

function clearFilters() {
  startDate.value = ""
  endDate.value = ""
  selectedProjectId.value = null
  selectedModelId.value = null
  loadCosts()
}

function formatNumber(num: number | undefined) {
  return num != null ? num.toLocaleString() : "-"
}

function formatCost(cost: number | undefined) {
  return cost != null ? cost.toFixed(4) : "-"
}

function formatCostYuan(cost: number | undefined) {
  return cost != null ? cost.toFixed(2) : "0.00"
}

// Sorting
const modelSortKey = ref<keyof ModelCostStat | null>(null)
const modelSortOrder = ref<"asc" | "desc">("desc")
const projectSortKey = ref<keyof ProjectCostStat | null>(null)
const projectSortOrder = ref<"asc" | "desc">("desc")

function sortModelStats(key: keyof ModelCostStat) {
  if (modelSortKey.value === key) {
    modelSortOrder.value = modelSortOrder.value === "asc" ? "desc" : "asc"
  } else {
    modelSortKey.value = key
    modelSortOrder.value = "desc"
  }
  modelStats.value.sort((a, b) => {
    const aVal = a[key] as number
    const bVal = b[key] as number
    return modelSortOrder.value === "asc" ? aVal - bVal : bVal - aVal
  })
}

function sortProjectStats(key: keyof ProjectCostStat) {
  if (projectSortKey.value === key) {
    projectSortOrder.value = projectSortOrder.value === "asc" ? "desc" : "asc"
  } else {
    projectSortKey.value = key
    projectSortOrder.value = "desc"
  }
  projectStats.value.sort((a, b) => {
    const aVal = a[key] as number
    const bVal = b[key] as number
    return projectSortOrder.value === "asc" ? aVal - bVal : bVal - aVal
  })
}

function getSortIcon(key: string, currentKey: string | null, order: "asc" | "desc") {
  if (currentKey !== key) return ""
  return order === "asc" ? "↑" : "↓"
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">成本统计</h1>
      <p class="page-desc">分析 AI 模型调用成本，支持多维度统计</p>
    </div>

    <!-- Summary Cards -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value" style="color: #f56c6c">¥ {{ formatCostYuan(summary.total_cost) }}</div>
          <div class="summary-label">总成本</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value" style="color: #e6a23c">¥ {{ formatCostYuan(summary.monthly_cost) }}</div>
          <div class="summary-label">本月成本</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value" style="color: #409eff">{{ formatNumber(summary.total_invocations) }}</div>
          <div class="summary-label">总调用次数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value" style="color: #67c23a">¥ {{ formatCost(summary.avg_cost_per_invocation) }}</div>
          <div class="summary-label">平均单次成本</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <!-- Filter Panel -->
      <div class="filter-bar" style="margin-bottom: 16px">
        <el-date-picker
          v-model="startDate"
          type="date"
          placeholder="开始日期"
          style="width: 140px"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="onFilterChange"
        />

        <el-date-picker
          v-model="endDate"
          type="date"
          placeholder="结束日期"
          style="width: 140px"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="onFilterChange"
        />

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

        <el-button @click="clearFilters">重置</el-button>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab">
        <el-tab-pane label="按模型统计" name="by_model" />
        <el-tab-pane label="按项目统计" name="by_project" />
      </el-tabs>

      <!-- By Model Table -->
      <el-table v-loading="loading" :data="modelStats" stripe v-if="activeTab === 'by_model'">
        <el-table-column prop="display_name" label="模型名称" min-width="160">
          <template #default="{ row }">
            <div style="font-weight: 600">{{ row.display_name || row.model_name || `模型 #${row.model_id}` }}</div>
            <div style="font-size: 12px; color: #909399">{{ row.model_name }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="provider_name" label="供应商" width="120" />
        <el-table-column prop="call_count" label="调用次数" width="100" align="right" sortable @click="sortModelStats('call_count')">
          <template #header>
            <span @click="sortModelStats('call_count')" class="sortable-header">
              调用次数 {{ getSortIcon("call_count", modelSortKey, modelSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            {{ formatNumber(row.call_count) }}
          </template>
        </el-table-column>
        <el-table-column prop="input_tokens" label="输入Token" width="110" align="right">
          <template #header>
            <span @click="sortModelStats('input_tokens')" class="sortable-header">
              输入Token {{ getSortIcon("input_tokens", modelSortKey, modelSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            {{ formatNumber(row.input_tokens) }}
          </template>
        </el-table-column>
        <el-table-column prop="output_tokens" label="输出Token" width="110" align="right">
          <template #header>
            <span @click="sortModelStats('output_tokens')" class="sortable-header">
              输出Token {{ getSortIcon("output_tokens", modelSortKey, modelSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            {{ formatNumber(row.output_tokens) }}
          </template>
        </el-table-column>
        <el-table-column prop="input_cost" label="输入成本" width="100" align="right">
          <template #header>
            <span @click="sortModelStats('input_cost')" class="sortable-header">
              输入成本 {{ getSortIcon("input_cost", modelSortKey, modelSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            <span style="color: #f56c6c">¥ {{ formatCost(row.input_cost) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="output_cost" label="输出成本" width="100" align="right">
          <template #header>
            <span @click="sortModelStats('output_cost')" class="sortable-header">
              输出成本 {{ getSortIcon("output_cost", modelSortKey, modelSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            <span style="color: #f56c6c">¥ {{ formatCost(row.output_cost) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="总成本" width="110" align="right" sort-by="total_cost">
          <template #header>
            <span @click="sortModelStats('total_cost')" class="sortable-header">
              总成本 {{ getSortIcon("total_cost", modelSortKey, modelSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 700">¥ {{ formatCost(row.total_cost) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && activeTab === 'by_model' && modelStats.length === 0" description="暂无模型成本数据" />

      <!-- By Project Table -->
      <el-table v-loading="loading" :data="projectStats" stripe v-if="activeTab === 'by_project'">
        <el-table-column prop="project_name" label="项目名称" min-width="200" />
        <el-table-column prop="call_count" label="调用次数" width="110" align="right">
          <template #header>
            <span @click="sortProjectStats('call_count')" class="sortable-header">
              调用次数 {{ getSortIcon("call_count", projectSortKey, projectSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            {{ formatNumber(row.call_count) }}
          </template>
        </el-table-column>
        <el-table-column prop="input_tokens" label="输入Token" width="110" align="right">
          <template #header>
            <span @click="sortProjectStats('input_tokens')" class="sortable-header">
              输入Token {{ getSortIcon("input_tokens", projectSortKey, projectSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            {{ formatNumber(row.input_tokens) }}
          </template>
        </el-table-column>
        <el-table-column prop="output_tokens" label="输出Token" width="110" align="right">
          <template #header>
            <span @click="sortProjectStats('output_tokens')" class="sortable-header">
              输出Token {{ getSortIcon("output_tokens", projectSortKey, projectSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            {{ formatNumber(row.output_tokens) }}
          </template>
        </el-table-column>
        <el-table-column label="总成本" width="120" align="right">
          <template #header>
            <span @click="sortProjectStats('total_cost')" class="sortable-header">
              总成本 {{ getSortIcon("total_cost", projectSortKey, projectSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 700">¥ {{ formatCost(row.total_cost) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="平均成本/调用" width="130" align="right">
          <template #header>
            <span @click="sortProjectStats('avg_cost_per_call')" class="sortable-header">
              平均成本/调用 {{ getSortIcon("avg_cost_per_call", projectSortKey, projectSortOrder) }}
            </span>
          </template>
          <template #default="{ row }">
            <span style="color: #67c23a">¥ {{ formatCost(row.avg_cost_per_call) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && activeTab === 'by_project' && projectStats.length === 0" description="暂无项目成本数据" />
    </el-card>
  </div>
</template>

<script lang="ts">
export default {}
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

.summary-card {
  text-align: center;
  padding: 8px 0;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.4;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
}

.sortable-header:hover {
  color: #409eff;
}
</style>
