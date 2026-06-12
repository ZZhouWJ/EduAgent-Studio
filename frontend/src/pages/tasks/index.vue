<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { FolderOpened } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { learningApi, type Course, type LearningTask } from "@/api/learning"

const router = useRouter()
const courses = ref<Course[]>([])
const selectedCourseId = ref<number | null>(null)
const tasks = ref<LearningTask[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const tasksLoading = ref(false)

const statusOptions = [
  { value: "", label: "全部状态" },
  { value: "pending", label: "待开始" },
  { value: "in_progress", label: "进行中" },
  { value: "submitted", label: "已提交" },
  { value: "reviewed", label: "已批阅" },
  { value: "completed", label: "已完成" },
]
const selectedStatus = ref("")

onMounted(async () => {
  loading.value = true
  try {
    const res = await learningApi.listCourses()
    courses.value = res.data.data || []
    if (courses.value.length > 0) {
      selectedCourseId.value = courses.value[0].id
      await loadTasks()
    }
  } catch {
    ElMessage.error("加载课程失败")
  } finally {
    loading.value = false
  }
})

async function loadTasks() {
  if (!selectedCourseId.value) {
    tasks.value = []
    total.value = 0
    return
  }
  tasksLoading.value = true
  try {
    const res = await learningApi.listTasks({
      page: page.value,
      page_size: pageSize.value,
      course_id: selectedCourseId.value,
      status: selectedStatus.value || undefined,
    })
    tasks.value = res.data.data.items || []
    total.value = res.data.data.total
  } catch {
    ElMessage.error("加载任务失败")
  } finally {
    tasksLoading.value = false
  }
}

async function onCourseChange(courseId: number | null) {
  page.value = 1
  selectedCourseId.value = courseId
  await loadTasks()
}

async function onStatusChange() {
  page.value = 1
  await loadTasks()
}

function goTask(taskId: number) {
  router.push(`/tasks/${taskId}`)
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    pending: "info",
    in_progress: "warning",
    submitted: "primary",
    reviewed: "success",
    completed: "success",
  }
  return map[status] || "info"
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    pending: "待开始",
    in_progress: "进行中",
    submitted: "已提交",
    reviewed: "已批阅",
    completed: "已完成",
  }
  return map[status] || status
}

function getPriorityType(p: string) {
  const map: Record<string, string> = {
    low: "info",
    medium: "warning",
    high: "danger",
  }
  return map[p] || "info"
}

function getPriorityLabel(p: string) {
  const map: Record<string, string> = {
    low: "低",
    medium: "中",
    high: "高",
  }
  return map[p] || p
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    lecture: "讲义",
    exercise: "练习",
    quiz: "测验",
    project: "项目",
    review: "复习",
  }
  return map[type] || type
}

function completionPercent(rate: number) {
  return Math.round(rate * 100)
}

function isOverdue(dueDate: string, status: string) {
  if (status === "completed") return false
  return new Date(dueDate) < new Date()
}

function formatDate(dateStr: string) {
  if (!dateStr) return "-"
  return new Date(dateStr).toLocaleDateString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" })
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">学习任务</h1>
      <p class="page-desc">管理课程学习任务，查看任务进度和完成情况</p>
    </div>

    <el-card>
      <template #header>
        <div class="toolbar">
          <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap">
            <span style="font-weight: 600; font-size: 14px">选择课程</span>
            <el-select
              v-model="selectedCourseId"
              placeholder="请选择课程"
              style="width: 240px"
              clearable
              filterable
              :loading="loading"
              @change="onCourseChange"
            >
              <el-option
                v-for="c in courses"
                :key="c.id"
                :label="`${c.code} · ${c.name}`"
                :value="c.id"
              />
            </el-select>

            <el-select
              v-model="selectedStatus"
              placeholder="任务状态"
              style="width: 130px"
              @change="onStatusChange"
            >
              <el-option
                v-for="s in statusOptions"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </div>

          <div style="display: flex; align-items: center; gap: 12px">
            <el-tag v-if="selectedCourseId" type="info" size="small">
              {{ total }} 个任务
            </el-tag>
            <el-button
              type="primary"
              size="small"
              @click="router.push('/agent-workbench')"
            >
              AI 生成资源
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="!selectedCourseId && !loading" class="empty-tip">
        <el-icon :size="40" color="#c0c4cc"><FolderOpened /></el-icon>
        <p>请在上方选择一个课程，查看该课程的学习任务列表</p>
        <el-button type="primary" size="small" @click="router.push('/courses')">前往课程空间</el-button>
      </div>

      <el-table
        v-else
        v-loading="tasksLoading"
        :data="tasks"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="title" label="任务名称" min-width="220">
          <template #default="{ row }">
            <div>
              <div style="font-weight: 500; color: #303133">{{ row.title }}</div>
              <div v-if="row.description" style="font-size: 12px; color: #909399; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">
                {{ row.description }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="type" label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="getPriorityType(row.priority)">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="due_date" label="截止日期" width="110">
          <template #default="{ row }">
            <span
              :style="{ color: isOverdue(row.due_date, row.status) ? '#f56c6c' : '#606266', fontWeight: isOverdue(row.due_date, row.status) ? 600 : 400 }"
            >
              {{ formatDate(row.due_date) }}
              <span v-if="isOverdue(row.due_date, row.status)" style="font-size: 11px"> 已逾期</span>
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="completion_rate" label="完成率" width="180">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 8px">
              <el-progress
                :percentage="completionPercent(row.completion_rate)"
                :color="completionPercent(row.completion_rate) >= 80 ? '#67c23a' : completionPercent(row.completion_rate) >= 50 ? '#e6a23c' : '#f56c6c'"
                :stroke-width="6"
                style="flex: 1"
              />
              <span style="font-size: 12px; color: #909399; min-width: 36px; text-align: right">
                {{ completionPercent(row.completion_rate) }}%
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="student_count" label="参与人数" width="100">
          <template #default="{ row }">
            <span style="color: #606266; font-size: 13px">{{ row.student_count }} 人</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="goTask(row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="selectedCourseId && !tasksLoading && tasks.length === 0" description="该课程暂无学习任务" />
    </el-card>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
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
.empty-tip p { margin: 0; }
</style>
