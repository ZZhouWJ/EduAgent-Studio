<script setup lang="ts">
import { ref, onMounted } from "vue"
import { modelsApi } from "@/api/models"

const providersLoading = ref(false)
const providers = ref<any[]>([])
const modelsLoading = ref(false)
const models = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const selectedProviderId = ref<number | null>(null)

onMounted(async () => {
  await loadProviders()
  await loadModels()
})

async function loadProviders() {
  providersLoading.value = true
  try {
    const res = await modelsApi.getProviders({ status: "active" })
    providers.value = res.data || []
  } catch {
    providers.value = []
  } finally {
    providersLoading.value = false
  }
}

async function loadModels() {
  modelsLoading.value = true
  try {
    const res = await modelsApi.getModels({
      provider_id: selectedProviderId.value || undefined,
      page: page.value,
      page_size: pageSize.value
    })
    models.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch {
    models.value = []
    total.value = 0
  } finally {
    modelsLoading.value = false
  }
}

function onProviderChange() {
  page.value = 1
  loadModels()
}

function onPageChange(p: number) {
  page.value = p
  loadModels()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadModels()
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    active: "success",
    inactive: "info",
    suspended: "danger",
    disabled: "info"
  }
  return map[status] || "info"
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">模型管理</h1>
      <p class="page-desc">查看系统配置的 AI 模型供应商和模型列表</p>
    </div>

    <!-- 供应商列表 -->
    <el-card style="margin-bottom: 16px">
      <template #header>
        <span style="font-weight: 600">AI 模型供应商</span>
      </template>
      <div v-loading="providersLoading" class="provider-grid">
        <div v-for="p in providers" :key="p.provider_id" class="provider-card">
          <div class="provider-icon">
            <el-icon :size="32" color="#1e3a5f"><Cpu /></el-icon>
          </div>
          <div class="provider-info">
            <div class="provider-name">{{ p.provider_name }}</div>
            <div class="provider-code">{{ p.provider_code }}</div>
            <el-tag size="small" :type="getStatusType(p.status)" style="margin-top: 4px">{{ p.status === "active" ? "在线" : p.status }}</el-tag>
          </div>
          <div class="provider-desc">{{ p.description || "暂无描述" }}</div>
        </div>
        <el-empty v-if="providers.length === 0" description="暂无供应商数据" />
      </div>
    </el-card>

    <!-- AI 模型列表 -->
    <el-card>
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span style="font-weight: 600">AI 模型列表</span>
          <div style="display: flex; align-items: center; gap: 8px">
            <el-select
              v-model="selectedProviderId"
              placeholder="全部供应商"
              clearable
              style="width: 180px"
              @change="onProviderChange"
            >
              <el-option
                v-for="p in providers"
                :key="p.provider_id"
                :label="p.provider_name"
                :value="p.provider_id"
              />
            </el-select>
          </div>
        </div>
      </template>

      <el-table v-loading="modelsLoading" :data="models" stripe>
        <el-table-column prop="display_name" label="模型名称" min-width="180">
          <template #default="{ row }">
            <div style="font-weight: 600">{{ row.display_name || row.model_name || `模型 #${row.model_id}` }}</div>
            <div style="font-size: 12px; color: #909399">{{ row.model_name || "-" }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="provider_name" label="供应商" width="120" />
        <el-table-column prop="capability_tags" label="能力标签" min-width="180">
          <template #default="{ row }">
            <el-tag
              v-for="tag in (row.capability_tags || '').split(',').filter(Boolean)"
              :key="tag"
              size="small"
              style="margin-right: 4px; margin-bottom: 2px; white-space: normal; height: auto; line-height: 1.6"
            >
              {{ tag.trim() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="max_context" label="上下文" width="100">
          <template #default="{ row }">
            {{ row.max_context ? `${row.max_context / 1000}K` : "-" }}
          </template>
        </el-table-column>
        <el-table-column label="输入价格" width="120">
          <template #default="{ row }">
            {{ row.input_price }} 元 / {{ row.price_unit }}
          </template>
        </el-table-column>
        <el-table-column label="输出价格" width="120">
          <template #default="{ row }">
            {{ row.output_price }} 元 / {{ row.price_unit }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">
              {{ row.status === "active" ? "在线" : row.status === "disabled" ? "离线" : row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="添加时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
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
  </div>
</template>

<script lang="ts">
import { Cpu } from "@element-plus/icons-vue"
export default { components: { Cpu } }
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

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.provider-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.provider-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #e6f0ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.provider-info {
  display: flex;
  flex-direction: column;
}

.provider-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.provider-code {
  font-size: 12px;
  color: #909399;
}

.provider-desc {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
