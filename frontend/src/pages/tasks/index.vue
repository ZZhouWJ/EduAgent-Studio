<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { FolderOpened } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { projectsApi } from "@/api/projects"

const router = useRouter()
const loading = ref(false)
const projects = ref<any[]>([])
const selectedProjectId = ref<number | null>(null)
const tasks = ref<any[]>([])
const tasksLoading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await projectsApi.list({ page: 1, page_size: 100 })
    projects.value = res.data.items || []
    if (projects.value.length > 0) {
      selectedProjectId.value = projects.value[0].project_id
    }
  } catch {
    projects.value = []
  } finally {
    loading.value = false
  }
})

async function loadTasks(projectId: number) {
  tasksLoading.value = true
  try {
    const res = await projectsApi.getTasks(projectId)
    tasks.value = res.data?.items || []
  } catch {
    tasks.value = []
  } finally {
    tasksLoading.value = false
  }
}

async function onProjectChange(projectId: number | null) {
  if (!projectId) {
    tasks.value = []
    return
  }
  await loadTasks(projectId)
}

function goTask(taskId: number) {
  router.push(`/tasks/${taskId}`)
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    draft: "info",
    running: "warning",
    generated: "primary",
    submitted: "warning",
    approved: "success",
    rejected: "danger",
    revision_required: "danger",
    adopted: "success",
    archived: "info",
    conflict_pending: "warning"
  }
  return map[status] || ""
}

function getPriorityType(p: string) {
  const map: Record<string, string> = {
    low: "info",
    normal: "",
    high: "warning",
    urgent: "danger"
  }
  return map[p] || ""
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">任务与版本</h1>
      <p class="page-desc">请从「项目空间」选择项目后，查看该项目的任务列表，点击任务进入详情页</p>
    </div>

    <el-card>
      <template #header>
        <div class="toolbar">
          <div style="display: flex; align-items: center; gap: 8px">
            <span style="font-weight: 600">选择项目</span>
            <el-select
              v-model="selectedProjectId"
              placeholder="请选择项目"
              style="width: 300px"
              clearable
              filterable
              :loading="loading"
              @change="onProjectChange"
            >
              <el-option
                v-for="p in projects"
                :key="p.project_id"
                :label="p.project_name"
                :value="p.project_id"
              />
            </el-select>
          </div>
          <el-tag v-if="selectedProjectId" type="info" size="small">
            {{ tasks.length }} 个任务
          </el-tag>
        </div>
      </template>

      <!-- 无项目时 -->
      <div v-if="!selectedProjectId" class="empty-tip">
        <el-icon :size="40" color="#c0c4cc"><FolderOpened /></el-icon>
        <p>请在上方选择一个项目，查看该项目的任务列表</p>
        <el-button type="primary" size="small" @click="router.push('/projects')">前往项目空间</el-button>
      </div>

      <!-- 任务表格 -->
      <el-table v-else v-loading="tasksLoading" :data="tasks" stripe>
        <el-table-column prop="title" label="任务标题" min-width="200" />
        <el-table-column prop="type_name" label="任务类型" width="130" />
        <el-table-column prop="status" label="状态" width="130">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="getPriorityType(row.priority)">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee_real_name" label="负责人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="goTask(row.task_id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="selectedProjectId && !tasksLoading && tasks.length === 0" description="该项目暂无任务" />
    </el-card>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  gap: 12px;
  color: #909399;
  font-size: 14px;
}

.empty-tip p {
  margin: 0;
}
</style>
