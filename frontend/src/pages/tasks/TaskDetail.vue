<script lang="ts" setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  getTaskDetailApi,
  getTaskBranchesApi,
  getTaskOutputsApi,
  getOutputDetailApi,
  getOutputTimelineApi
} from "@/common/apis/tasks"
import type { Task, TaskBranch, TaskOutput, OutputTimeline } from "@/common/apis/tasks/type"

const route = useRoute()
const router = useRouter()
const taskId = Number(route.params.taskId)

const loading = ref(false)
const task = ref<Partial<Task>>({})
const branches = ref<TaskBranch[]>([])
const outputs = ref<TaskOutput[]>([])

const outputDetailVisible = ref(false)
const outputDetail = ref<Partial<TaskOutput>>({})
const outputTimeline = ref<OutputTimeline[]>([])
const outputDetailLoading = ref(false)

function getStatusType(status: string) {
  const map: Record<string, string> = {
    draft: "info",
    pending: "info",
    running: "primary",
    in_progress: "primary",
    generated: "success",
    submitted: "warning",
    approved: "success",
    rejected: "danger",
    revision_required: "warning",
    adopted: "success",
    deleted: "info"
  }
  return map[status] || "info"
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    draft: "草稿",
    pending: "待处理",
    running: "进行中",
    in_progress: "进行中",
    generated: "已生成",
    submitted: "已提交",
    approved: "已通过",
    rejected: "已拒绝",
    revision_required: "需修改",
    adopted: "已采用",
    deleted: "已删除"
  }
  return map[status] || status
}

function getPriorityTagType(priority: string) {
  const map: Record<string, string> = {
    high: "danger",
    normal: "primary",
    low: "info"
  }
  return map[priority] || "info"
}

function getPriorityLabel(priority: string) {
  return { high: "高", normal: "中", low: "低" }[priority] || priority
}

function getSourceTypeLabel(type: string) {
  const map: Record<string, string> = {
    ai_generated: "AI 生成",
    manual: "人工编辑"
  }
  return map[type] || type
}

function getOutputList(data: unknown) {
  if (Array.isArray(data)) return data
  const obj = data as Record<string, unknown>
  if (obj && Array.isArray(obj.items)) return obj.items as TaskOutput[]
  return []
}

async function fetchTask() {
  loading.value = true
  try {
    const [taskRes, branchesRes, outputsRes] = await Promise.all([
      getTaskDetailApi(taskId),
      getTaskBranchesApi(taskId),
      getTaskOutputsApi(taskId, { page: 1, page_size: 50 })
    ])
    task.value = taskRes.data
    branches.value = branchesRes.data || []
    outputs.value = getOutputList(outputsRes.data)
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}

async function viewOutputDetail(output: TaskOutput) {
  outputDetailVisible.value = true
  outputDetailLoading.value = true
  outputDetail.value = {}
  outputTimeline.value = []
  try {
    const [detailRes, timelineRes] = await Promise.all([
      getOutputDetailApi(output.output_id),
      getOutputTimelineApi(output.output_id)
    ])
    outputDetail.value = detailRes.data
    outputTimeline.value = timelineRes.data || []
  } catch {
    // error shown by axios interceptor
  } finally {
    outputDetailLoading.value = false
  }
}

onMounted(fetchTask)
</script>

<template>
  <div class="task-detail-page">
    <div class="page-header">
      <el-button text @click="$router.back()">
        <el-icon style="margin-right: 4px"><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2 class="page-title">{{ task.title || "任务详情" }}</h2>
    </div>

    <el-card v-loading="loading">
      <el-tabs>
        <el-tab-pane label="基本信息">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="所属项目" :span="2">
              <el-link v-if="task.project_id" type="primary" :underline="false" @click="router.push(`/projects/${task.project_id}`)">
                {{ task.project_name || `项目 #${task.project_id}` }}
              </el-link>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="任务标题" :span="2">{{ task.title || "-" }}</el-descriptions-item>
            <el-descriptions-item label="任务类型">{{ task.type_name || "-" }}</el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag size="small" :type="getPriorityTagType(task.priority || '')">
                {{ getPriorityLabel(task.priority || '') }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="任务状态">
              <el-tag size="small" :type="getStatusType(task.status || '')">
                {{ getStatusLabel(task.status || '') }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="负责人">
              {{ task.assignee_real_name || task.assignee_username || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="截止时间">
              {{ task.due_date ? new Date(task.due_date).toLocaleDateString("zh-CN") : "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="创建人">
              {{ task.creator_real_name || task.creator_username || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ task.created_at ? new Date(task.created_at).toLocaleString("zh-CN") : "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="任务描述" :span="2">
              {{ task.description || "暂无描述" }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="分支">
          <el-table :data="branches" stripe style="width: 100%">
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="branch_name" label="分支名称" min-width="180" />
            <el-table-column prop="base_output_title" label="基准版本" width="180" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.base_output_title || "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="creator_real_name" label="创建人" width="120" align="center">
              <template #default="{ row }">
                {{ row.creator_real_name || row.creator_username || "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无分支" />
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="输出版本">
          <el-table :data="outputs" stripe style="width: 100%" @row-click="(row) => viewOutputDetail(row)">
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="output_title" label="版本标题" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">
                <el-link type="primary" :underline="false">
                  {{ row.output_title || `版本 ${row.version_no}` }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="version_no" label="版本号" width="80" align="center" />
            <el-table-column prop="source_type" label="来源" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.source_type === 'ai_generated' ? 'primary' : 'success'">
                  {{ getSourceTypeLabel(row.source_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="creator_real_name" label="创建人" width="120" align="center">
              <template #default="{ row }">
                {{ row.creator_real_name || row.creator_username || "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click.stop="viewOutputDetail(row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无输出版本" />
            </template>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog
      v-model="outputDetailVisible"
      :title="`版本详情 - ${outputDetail.output_title || `v${outputDetail.version_no}`}`"
      width="720px"
      :close-on-click-modal="true"
    >
      <div v-loading="outputDetailLoading">
        <el-descriptions :column="2" border style="margin-bottom: 16px">
          <el-descriptions-item label="版本标题">{{ outputDetail.output_title || "-" }}</el-descriptions-item>
          <el-descriptions-item label="版本号">v{{ outputDetail.version_no }}</el-descriptions-item>
          <el-descriptions-item label="来源">
            <el-tag size="small">
              {{ getSourceTypeLabel(outputDetail.source_type || "") }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag size="small" :type="getStatusType(outputDetail.status || '')">
              {{ getStatusLabel(outputDetail.status || "") }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ outputDetail.creator_real_name || outputDetail.creator_username || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ outputDetail.created_at ? new Date(outputDetail.created_at).toLocaleString("zh-CN") : "-" }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="outputDetail.content" class="content-preview">
          <div class="content-label">版本内容</div>
          <el-input
            :model-value="outputDetail.content"
            type="textarea"
            :rows="12"
            readonly
            resize="none"
          />
        </div>

        <div v-if="outputTimeline.length > 0" class="timeline-section">
          <div class="content-label">版本时间线</div>
          <el-timeline>
            <el-timeline-item
              v-for="item in outputTimeline"
              :key="item.output_id"
              :timestamp="new Date(item.created_at).toLocaleString('zh-CN')"
              placement="top"
            >
              <el-card shadow="never">
                <p>
                  <strong>{{ item.output_title || `v${item.version_no}` }}</strong>
                  <el-tag size="small" style="margin-left: 8px" :type="item.source_type === 'ai_generated' ? 'primary' : 'success'">
                    {{ getSourceTypeLabel(item.source_type) }}
                  </el-tag>
                </p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="outputDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.task-detail-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

:deep(.el-table__row) {
  cursor: pointer;
}

.content-preview {
  margin-bottom: 16px;
}

.content-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.timeline-section {
  margin-top: 16px;
}
</style>
