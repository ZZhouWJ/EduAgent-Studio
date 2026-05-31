<script lang="ts" setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  getProjectDetailApi,
  getProjectMembersApi
} from "@/common/apis/projects"
import { getProjectTaskListApi, createProjectTaskApi } from "@/common/apis/tasks"
import type { Project, ProjectMember } from "@/common/apis/projects/type"
import type { Task, CreateTaskRequestData } from "@/common/apis/tasks/type"

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

const loading = ref(false)
const project = ref<Partial<Project>>({})
const members = ref<ProjectMember[]>([])
const tasks = ref<Task[]>([])
const taskTotal = ref(0)

const createTaskDialogVisible = ref(false)
const createTaskLoading = ref(false)
const createTaskFormRef = ref()
const createTaskForm = ref<CreateTaskRequestData>({
  task_type_id: 1,
  title: "",
  description: "",
  assignee_id: undefined,
  priority: "normal",
  due_date: ""
})

const createTaskRules = {
  title: [{ required: true, message: "请输入任务标题", trigger: "blur" }],
  task_type_id: [{ required: true, message: "请选择任务类型", trigger: "change" }]
}

const taskTypeOptions = [
  { label: "需求分析", value: 1 },
  { label: "概要设计", value: 2 },
  { label: "详细设计", value: 3 },
  { label: "编码实现", value: 4 },
  { label: "测试验证", value: 5 },
  { label: "文档撰写", value: 6 }
]

const priorityOptions = [
  { label: "高", value: "high" },
  { label: "中", value: "normal" },
  { label: "低", value: "low" }
]

async function handleCreateTask() {
  if (!createTaskFormRef.value) return
  try {
    const valid = await createTaskFormRef.value.validate()
    if (!valid) return
    createTaskLoading.value = true
    await createProjectTaskApi(projectId, createTaskForm.value)
    ElMessage.success("任务创建成功")
    createTaskDialogVisible.value = false
    createTaskForm.value = {
      task_type_id: 1,
      title: "",
      description: "",
      assignee_id: undefined,
      priority: "normal",
      due_date: ""
    }
    fetchAll()
  } catch {
    // error shown by axios interceptor
  } finally {
    createTaskLoading.value = false
  }
}

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

function getProjectStatusLabel(status: string) {
  const map: Record<string, string> = {
    active: "进行中",
    archived: "已归档",
    suspended: "已暂停",
    deleted: "已删除"
  }
  return map[status] || status
}

async function fetchAll() {
  loading.value = true
  try {
    const [projectRes, membersRes, tasksRes] = await Promise.all([
      getProjectDetailApi(projectId),
      getProjectMembersApi(projectId),
      getProjectTaskListApi(projectId, { page: 1, page_size: 20 })
    ])
    project.value = projectRes.data
    members.value = membersRes.data || []
    tasks.value = tasksRes.data.items || []
    taskTotal.value = tasksRes.data.total || 0
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}

function goToTask(task: Task) {
  router.push(`/tasks/${task.task_id}`)
}

onMounted(fetchAll)
</script>

<template>
  <div class="project-detail-page">
    <div class="page-header">
      <el-button text @click="$router.push('/projects')">
        <el-icon style="margin-right: 4px"><ArrowLeft /></el-icon>
        返回项目列表
      </el-button>
      <h2 class="page-title">{{ project.project_name || "项目详情" }}</h2>
    </div>

    <el-card v-loading="loading">
      <el-tabs>
        <el-tab-pane label="项目概览">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目名称">{{ project.project_name || "-" }}</el-descriptions-item>
            <el-descriptions-item label="项目类型">
              <el-tag size="small">{{ project.project_type || "-" }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="项目状态">
              <el-tag size="small" type="success">{{ getProjectStatusLabel(project.status || "") }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="负责人">
              {{ project.owner_real_name || project.owner_username || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间" :span="2">
              {{ project.created_at ? new Date(project.created_at).toLocaleString("zh-CN") : "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="项目描述" :span="2">
              {{ project.description || "暂无描述" }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="成员">
          <el-table :data="members" stripe style="width: 100%">
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="real_name" label="姓名" width="120">
              <template #default="{ row }">
                {{ row.real_name || row.username }}
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="student_no" label="学号" width="140" />
            <el-table-column prop="project_role" label="角色" width="120" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.project_role === 'leader' ? 'warning' : 'info'">
                  {{ row.project_role === "leader" ? "项目负责人" : row.project_role === "teacher" ? "指导教师" : row.project_role === "reviewer" ? "审核员" : "成员" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="joined_at" label="加入时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.joined_at ? new Date(row.joined_at).toLocaleString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无成员" />
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="任务">
          <div style="margin-bottom: 12px; text-align: right">
            <el-button type="primary" size="small" @click="createTaskDialogVisible = true">
              <el-icon style="margin-right: 4px"><Plus /></el-icon>
              新建任务
            </el-button>
          </div>
          <el-table :data="tasks" stripe style="width: 100%" @row-click="goToTask">
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="title" label="任务标题" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <el-link type="primary" :underline="false">
                  {{ row.title }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="type_name" label="任务类型" width="120" align="center">
              <template #default="{ row }">
                {{ row.type_name || "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getPriorityTagType(row.priority)">
                  {{ row.priority === "high" ? "高" : row.priority === "normal" ? "中" : "低" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assignee_real_name" label="负责人" width="120" align="center">
              <template #default="{ row }">
                {{ row.assignee_real_name || row.assignee_username || "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="截止时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.due_date ? new Date(row.due_date).toLocaleDateString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无任务" />
            </template>
          </el-table>
          <div v-if="taskTotal > 20" style="margin-top: 12px; text-align: right;">
            <span style="color: #909399; font-size: 13px">共 {{ taskTotal }} 条任务</span>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog
      v-model="createTaskDialogVisible"
      title="新建任务"
      width="500px"
      :close-on-click-modal="false"
      @closed="createTaskFormRef?.resetFields()"
    >
      <el-form
        ref="createTaskFormRef"
        :model="createTaskForm"
        :rules="createTaskRules"
        label-width="90px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="createTaskForm.title" placeholder="请输入任务标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type_id">
          <el-select v-model="createTaskForm.task_type_id" placeholder="请选择任务类型" style="width: 100%">
            <el-option
              v-for="opt in taskTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="createTaskForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option
              v-for="opt in priorityOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间" prop="due_date">
          <el-date-picker
            v-model="createTaskForm.due_date"
            type="datetime"
            placeholder="选择截止时间（选填）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="createTaskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTaskDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createTaskLoading" @click="handleCreateTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.project-detail-page {
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
</style>
