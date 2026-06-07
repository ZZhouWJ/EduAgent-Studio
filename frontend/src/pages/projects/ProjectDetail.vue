<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  ArrowLeft,
  Plus,
  Edit,
  Delete,
  FolderOpened,
  UserFilled,
  List,
  Collection,
  Monitor,
  Document,
  DataLine,
  RefreshRight,
  User
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { projectsApi } from "@/api/projects"
import { artifactsApi } from "@/api/artifacts"
import { statisticsApi } from "@/api/statistics"
import { logsApi } from "@/api/logs"
import { invocationsApi } from "@/api/invocations"
import type { Artifact } from "@/api/artifacts"
import type { Invocation } from "@/api/invocations"
import type { RecentActivity } from "@/api/statistics"
import { useUserStore } from "@/stores/user"
import { useProjectRoleStore } from "@/stores/projectRole"
import {
  canManageProject,
  canManageMembers,
  canCreateTask,
  isAdmin,
  PROJECT_ROLE_LABEL
} from "@/utils/permission"
import type { ProjectRole } from "@/utils/permission"

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

const userStore = useUserStore()
const projectRoleStore = useProjectRoleStore()

const loading = ref(false)
const project = ref<any>(null)

// Tab state
const activeTab = ref("overview")

// Overview data
const recentActivities = ref<RecentActivity[]>([])

// Members data
const members = ref<any[]>([])
const addMemberDialogVisible = ref(false)
const addMemberLoading = ref(false)
const addMemberForm = ref({
  user_id: undefined as number | undefined,
  project_role: "member"
})
const roleOptions = [
  { label: "项目负责人", value: "leader" },
  { label: "成员", value: "member" },
  { label: "审核员", value: "reviewer" },
  { label: "教师", value: "teacher" }
]

// Tasks data
const tasks = ref<any[]>([])
const tasksLoading = ref(false)
const taskTotal = ref(0)
const taskPage = ref(1)
const taskPageSize = ref(10)
const taskStatusFilter = ref("")

// Artifacts data
const artifacts = ref<Artifact[]>([])
const artifactsLoading = ref(false)
const artifactsTotal = ref(0)
const artifactsPage = ref(1)
const artifactsPageSize = ref(10)

// Invocations data
const invocations = ref<Invocation[]>([])
const invocationsLoading = ref(false)
const invocationsTotal = ref(0)
const invocationsPage = ref(1)
const invocationsPageSize = ref(10)

// Operation logs data
const operationLogs = ref<any[]>([])
const operationLogsLoading = ref(false)
const operationLogsTotal = ref(0)
const operationLogsPage = ref(1)
const operationLogsPageSize = ref(10)

// Statistics data
const projectStats = ref<any>(null)

// Task types map — populated from /api/task-types on mount
const taskTypeNameMap = ref<Record<number, string>>({})

// Fallback task types (English labels, no encoding risk) — used only if API fails
const taskTypes = [
  { task_type_id: 1, type_name: "Requirement Analysis" },
  { task_type_id: 2, type_name: "DB Schema Design" },
  { task_type_id: 3, type_name: "SQL Explanation" },
  { task_type_id: 4, type_name: "Abstract Polish" },
  { task_type_id: 5, type_name: "Literature Summary" },
  { task_type_id: 6, type_name: "PPT Copywriting" },
  { task_type_id: 7, type_name: "Proposal Revision" },
  { task_type_id: 8, type_name: "Experiment Summary" },
  { task_type_id: 9, type_name: "Code Annotation" }
]

const createTaskDialogVisible = ref(false)
const createTaskLoading = ref(false)
const createTaskForm = ref({
  task_type_id: 1,
  title: "",
  description: "",
  assignee_id: undefined as number | undefined,
  priority: "normal",
  due_date: ""
})

const priorityOptions = [
  { label: "低", value: "low" },
  { label: "普通", value: "normal" },
  { label: "高", value: "high" },
  { label: "紧急", value: "urgent" }
]

// ── Permission helpers ────────────────────────────────────────────────────────

const currentUser = computed(() => userStore.userInfo)

/** Current user's project_role in this project */
const myProjectRole = computed<ProjectRole | null>(() => {
  if (!currentUser.value) return null
  return projectRoleStore.getCurrentUserProjectRole(projectId, currentUser.value.user_id)
})

/** Can edit/archive project settings */
const canManage = computed(() => canManageProject(currentUser.value, myProjectRole.value))

/** Can add/remove members, change roles */
const canManageMembersHere = computed(() => canManageMembers(currentUser.value, myProjectRole.value))

/** Can create tasks */
const canCreateTasks = computed(() => canCreateTask(currentUser.value, myProjectRole.value))

// ── Lifecycle ────────────────────────────────────────────────────────────────

onMounted(async () => {
  loading.value = true
  try {
    const projRes = await projectsApi.getById(projectId)
    project.value = projRes.data
    await Promise.all([
      loadMembers(),
      loadProjectStats(),
      loadTaskTypes()
    ])
  } catch {
    ElMessage.error("加载项目信息失败")
  } finally {
    loading.value = false
  }
})

async function loadTaskTypes() {
  // Already populated from API — skip
  if (Object.keys(taskTypeNameMap.value).length > 0) return
  try {
    const { modelsApi } = await import("@/api/models")
    const res = await modelsApi.getTaskTypes()
    const items = res.data || []
    // Populate the reactive map (used by getTaskTypeName)
    taskTypeNameMap.value = {}
    items.forEach((t: any) => {
      taskTypeNameMap.value[t.task_type_id] = t.type_name
    })
    // Also update the taskTypes select options array
    taskTypes.splice(0, taskTypes.length, ...items)
  } catch {
    // API failed — keep English fallback in taskTypes, taskTypeNameMap stays empty
  }
}

async function loadMembers() {
  try {
    const res = await projectsApi.getMembers(projectId)
    members.value = res.data || []
    // Cache members in project role store for permission checks
    projectRoleStore.setMembers(projectId, members.value)
  } catch {
    members.value = []
  }
}

async function loadProjectStats() {
  try {
    const res = await statisticsApi.projects({ project_id: projectId })
    projectStats.value = res.data?.[0] || null
    const activitiesRes = await statisticsApi.recentActivities({ project_id: projectId, limit: 10 })
    recentActivities.value = activitiesRes.data || []
  } catch {
    recentActivities.value = []
  }
}

async function loadTasks() {
  tasksLoading.value = true
  try {
    const res = await projectsApi.getTasks(projectId, {
      page: taskPage.value,
      page_size: taskPageSize.value,
      status: taskStatusFilter.value || undefined
    })
    tasks.value = res.data?.items || []
    taskTotal.value = res.data?.total || 0
  } catch {
    tasks.value = []
    taskTotal.value = 0
  } finally {
    tasksLoading.value = false
  }
}

async function loadArtifacts() {
  artifactsLoading.value = true
  try {
    const res = await artifactsApi.list(projectId, {
      page: artifactsPage.value,
      page_size: artifactsPageSize.value
    })
    artifacts.value = res.data?.items || []
    artifactsTotal.value = res.data?.total || 0
  } catch {
    artifacts.value = []
    artifactsTotal.value = 0
  } finally {
    artifactsLoading.value = false
  }
}

async function loadInvocations() {
  invocationsLoading.value = true
  try {
    const res = await invocationsApi.list({
      page: invocationsPage.value,
      page_size: invocationsPageSize.value,
      project_id: projectId
    })
    invocations.value = res.data?.items || []
    invocationsTotal.value = res.data?.total || 0
  } catch {
    invocations.value = []
    invocationsTotal.value = 0
  } finally {
    invocationsLoading.value = false
  }
}

async function loadOperationLogs() {
  operationLogsLoading.value = true
  try {
    const res = await logsApi.operationLogs({
      page: operationLogsPage.value,
      page_size: operationLogsPageSize.value
    })
    // Filter for this project's logs
    const allLogs = res.data?.items || []
    operationLogs.value = allLogs.filter((log: any) => log.target_type === "project" && log.target_id === projectId)
    operationLogsTotal.value = operationLogs.value.length
  } catch {
    operationLogs.value = []
    operationLogsTotal.value = 0
  } finally {
    operationLogsLoading.value = false
  }
}

function onTabChange(tab: string) {
  activeTab.value = tab
  if (tab === "tasks") loadTasks()
  else if (tab === "artifacts") loadArtifacts()
  else if (tab === "invocations") loadInvocations()
  else if (tab === "operationLogs") loadOperationLogs()
}

function goTask(taskId: number) {
  router.push(`/tasks/${taskId}`)
}

function goBack() {
  router.push("/projects")
}

async function handleCreateTask() {
  if (!createTaskForm.value.title.trim()) {
    ElMessage.warning("请输入任务标题")
    return
  }
  createTaskLoading.value = true
  try {
    await projectsApi.createTask(projectId, {
      task_type_id: createTaskForm.value.task_type_id,
      title: createTaskForm.value.title,
      description: createTaskForm.value.description || undefined,
      assignee_id: createTaskForm.value.assignee_id,
      priority: createTaskForm.value.priority,
      due_date: createTaskForm.value.due_date || undefined
    })
    ElMessage.success("任务创建成功")
    createTaskDialogVisible.value = false
    createTaskForm.value = { task_type_id: 1, title: "", description: "", assignee_id: undefined, priority: "normal", due_date: "" }
    loadTasks()
    loadProjectStats()
  } catch {
    // error handled by interceptor
  } finally {
    createTaskLoading.value = false
  }
}

function openCreateTaskDialog() {
  createTaskForm.value = { task_type_id: 1, title: "", description: "", assignee_id: undefined, priority: "normal", due_date: "" }
  createTaskDialogVisible.value = true
  loadTaskTypes()
}

async function handleAddMember() {
  if (!addMemberForm.value.user_id) {
    ElMessage.warning("请选择要添加的成员")
    return
  }
  addMemberLoading.value = true
  try {
    await projectsApi.addMember(projectId, {
      user_id: addMemberForm.value.user_id,
      project_role: addMemberForm.value.project_role
    })
    ElMessage.success("成员添加成功")
    addMemberDialogVisible.value = false
    addMemberForm.value = { user_id: undefined, project_role: "member" }
    loadMembers()
    loadProjectStats()
  } catch {
    // error handled by interceptor
  } finally {
    addMemberLoading.value = false
  }
}

async function handleRemoveMember(row: any) {
  try {
    await ElMessageBox.confirm(`确定要从项目中移除成员「${row.real_name || row.username}」吗？`, "移除成员", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    })
    await projectsApi.removeMember(projectId, row.user_id)
    ElMessage.success("成员已移除")
    loadMembers()
    loadProjectStats()
  } catch {
    // cancelled
  }
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function getTaskTypeName(taskTypeId: number) {
  return taskTypeNameMap.value[taskTypeId] || taskTypes.find(t => t.task_type_id === taskTypeId)?.type_name || "未知"
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

function getRoleLabel(role: string) {
  const map: Record<string, string> = {
    leader: "项目负责人",
    member: "成员",
    reviewer: "审核员",
    teacher: "教师"
  }
  return map[role] || role
}

function getActionTypeTagType(action: string): string {
  const map: Record<string, string> = {
    create: "primary",
    update: "warning",
    delete: "danger",
    login: "info",
    logout: "info",
    generate: "",
    review: "warning",
    adopt: "success",
    merge: ""
  }
  return map[action] || "info"
}

function getActionTypeLabel(action: string): string {
  const map: Record<string, string> = {
    create: "创建",
    update: "更新",
    delete: "删除",
    login: "登录",
    logout: "登出",
    generate: "生成",
    review: "审核",
    adopt: "采纳",
    merge: "合并"
  }
  return map[action] || action
}

function getInvocationStatusType(status: string): string {
  const map: Record<string, string> = {
    success: "success",
    failed: "danger",
    pending: "warning",
    running: "warning"
  }
  return map[status] || "info"
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-wrap">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/projects' }">项目空间</el-breadcrumb-item>
        <el-breadcrumb-item>{{ project?.project_name || "项目详情" }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 页面头部 -->
    <div class="page-header" style="margin-bottom: 16px">
      <div class="header-top">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 返回项目列表
        </el-button>
        <div class="header-actions">
          <!-- 项目角色提示标签 -->
          <el-tag v-if="myProjectRole" size="small" type="warning">
            我的项目角色：{{ PROJECT_ROLE_LABEL[myProjectRole] || myProjectRole }}
          </el-tag>
          <el-button type="primary" @click="openCreateTaskDialog" v-if="activeTab === 'tasks' && canCreateTasks">
            <el-icon><Plus /></el-icon> 创建任务
          </el-button>
        </div>
      </div>
      <h1 class="page-title">{{ project?.project_name || "项目详情" }}</h1>
      <p class="page-desc">{{ project?.description || "" }}</p>
    </div>

    <!-- Tabs -->
    <el-card v-loading="loading">
      <el-tabs v-model:active-tab="activeTab" @tab-change="onTabChange">
        <!-- Tab 1: 概览 -->
        <el-tab-pane label="概览" name="overview">
          <el-row :gutter="16" style="margin-bottom: 20px">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span style="font-weight: 600">基本信息</span>
                </template>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="项目ID">{{ project?.project_id }}</el-descriptions-item>
                  <el-descriptions-item label="状态">
                    <el-tag size="small" :type="project?.status === 'active' ? 'success' : 'info'">
                      {{ project?.status === "active" ? "活跃" : project?.status }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="项目类型">{{ project?.project_type }}</el-descriptions-item>
                  <el-descriptions-item label="创建人">{{ project?.owner_real_name || project?.owner_username || "-" }}</el-descriptions-item>
                  <el-descriptions-item label="创建时间" :span="2">{{ formatDate(project?.created_at) }}</el-descriptions-item>
                  <el-descriptions-item label="描述" :span="2">{{ project?.description || "-" }}</el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span style="font-weight: 600">项目统计</span>
                </template>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="成员数量">
                    <el-statistic :value="projectStats?.member_count ?? members.length" />
                  </el-descriptions-item>
                  <el-descriptions-item label="任务数量">
                    <el-statistic :value="projectStats?.task_count ?? 0" />
                  </el-descriptions-item>
                  <el-descriptions-item label="成果数量">
                    <el-statistic :value="projectStats?.artifact_count ?? 0" />
                  </el-descriptions-item>
                  <el-descriptions-item label="调用次数">
                    <el-statistic :value="projectStats?.invocation_count ?? 0" />
                  </el-descriptions-item>
                  <el-descriptions-item label="总成本" :span="2">
                    <span class="cost-value">¥{{ (projectStats?.total_cost ?? 0).toFixed(4) }}</span>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>

          <!-- 最近活动 -->
          <el-card shadow="hover">
            <template #header>
              <div style="display: flex; align-items: center; gap: 8px">
                <span style="font-weight: 600">最近活动</span>
                <el-tag size="small">{{ recentActivities.length }} 条</el-tag>
              </div>
            </template>
            <el-timeline v-if="recentActivities.length > 0">
              <el-timeline-item
                v-for="activity in recentActivities"
                :key="activity.log_id"
                :timestamp="formatDate(activity.created_at)"
                placement="top"
              >
                <el-card size="small">
                  <p>
                    <el-tag size="small" type="primary" style="margin-right: 8px">
                      {{ activity.real_name || "未知用户" }}
                    </el-tag>
                    {{ activity.action_desc }}
                  </p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无活动记录" />
          </el-card>
        </el-tab-pane>

        <!-- Tab 2: 成员 -->
        <el-tab-pane label="成员" name="members">
          <div style="margin-bottom: 12px">
            <el-button type="primary" @click="addMemberDialogVisible = true" v-if="canManageMembersHere">
              <el-icon><Plus /></el-icon> 添加成员
            </el-button>
            <el-tag v-else-if="myProjectRole" size="small" type="info" style="margin-left: 8px">
              您是 {{ PROJECT_ROLE_LABEL[myProjectRole] || myProjectRole }}，无添加成员权限
            </el-tag>
          </div>
          <el-table :data="members" stripe>
            <el-table-column prop="real_name" label="真实姓名" min-width="120" />
            <el-table-column prop="username" label="用户名" min-width="120" />
            <el-table-column prop="project_role" label="项目角色" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ getRoleLabel(row.project_role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column prop="joined_at" label="加入时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.joined_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="canManageMembersHere && row.user_id !== currentUser?.user_id"
                  type="danger"
                  size="small"
                  link
                  @click="handleRemoveMember(row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
                <span v-else-if="row.user_id === currentUser?.user_id" style="color: #909399; font-size: 12px">本人</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="members.length === 0" description="暂无成员" />
        </el-tab-pane>

        <!-- Tab 3: 任务 -->
        <el-tab-pane label="任务" name="tasks">
          <div style="margin-bottom: 12px; display: flex; gap: 8px; align-items: center">
            <el-select v-model="taskStatusFilter" placeholder="状态筛选" clearable style="width: 150px" @change="loadTasks">
              <el-option label="全部状态" value="" />
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="running" />
              <el-option label="已生成" value="generated" />
              <el-option label="待审核" value="submitted" />
              <el-option label="已通过" value="approved" />
              <el-option label="已采纳" value="adopted" />
            </el-select>
            <el-button type="primary" @click="openCreateTaskDialog" v-if="canCreateTasks">
              <el-icon><Plus /></el-icon> 创建任务
            </el-button>
          </div>
          <el-table v-loading="tasksLoading" :data="tasks" stripe>
            <el-table-column prop="title" label="任务标题" min-width="200" />
            <el-table-column label="任务类型" width="130">
              <template #default="{ row }">
                {{ getTaskTypeName(row.task_type_id) }}
              </template>
            </el-table-column>
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
          <el-empty v-if="!tasksLoading && tasks.length === 0" description="暂无任务" />
          <div class="pagination-wrap" v-if="taskTotal > 0">
            <el-pagination
              v-model:current-page="taskPage"
              v-model:page-size="taskPageSize"
              :total="taskTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @current-change="loadTasks"
              @size-change="loadTasks"
            />
          </div>
        </el-tab-pane>

        <!-- Tab 4: 成果 -->
        <el-tab-pane label="成果" name="artifacts">
          <el-table v-loading="artifactsLoading" :data="artifacts" stripe>
            <el-table-column prop="artifact_title" label="成果标题" min-width="180" />
            <el-table-column prop="artifact_type" label="成果类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.artifact_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="task_title" label="来源任务" min-width="150" />
            <el-table-column prop="output_title" label="输出标题" min-width="150" />
            <el-table-column prop="adopted_by_name" label="采纳人" width="120" />
            <el-table-column prop="adopted_at" label="采纳时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.adopted_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link>查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!artifactsLoading && artifacts.length === 0" description="暂无成果" />
          <div class="pagination-wrap" v-if="artifactsTotal > 0">
            <el-pagination
              v-model:current-page="artifactsPage"
              v-model:page-size="artifactsPageSize"
              :total="artifactsTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @current-change="loadArtifacts"
              @size-change="loadArtifacts"
            />
          </div>
        </el-tab-pane>

        <!-- Tab 5: 调用记录 -->
        <el-tab-pane label="调用记录" name="invocations">
          <el-table v-loading="invocationsLoading" :data="invocations" stripe>
            <el-table-column prop="model_name" label="模型" width="150" />
            <el-table-column prop="task_title" label="任务" min-width="150" />
            <el-table-column label="Token" width="180">
              <template #default="{ row }">
                <span>输入: {{ row.input_tokens }} / 输出: {{ row.output_tokens }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="latency_ms" label="延迟(ms)" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getInvocationStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="调用时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!invocationsLoading && invocations.length === 0" description="暂无调用记录" />
          <div class="pagination-wrap" v-if="invocationsTotal > 0">
            <el-pagination
              v-model:current-page="invocationsPage"
              v-model:page-size="invocationsPageSize"
              :total="invocationsTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @current-change="loadInvocations"
              @size-change="loadInvocations"
            />
          </div>
        </el-tab-pane>

        <!-- Tab 6: 操作日志 -->
        <el-tab-pane label="操作日志" name="operationLogs">
          <el-table v-loading="operationLogsLoading" :data="operationLogs" stripe>
            <el-table-column prop="log_id" label="日志ID" width="80" />
            <el-table-column label="操作人" width="120">
              <template #default="{ row }">
                {{ row.real_name || row.username || "-" }}
              </template>
            </el-table-column>
            <el-table-column label="操作类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getActionTypeTagType(row.action_type)">
                  {{ getActionTypeLabel(row.action_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action_desc" label="操作描述" min-width="180" show-overflow-tooltip />
            <el-table-column prop="created_at" label="操作时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!operationLogsLoading && operationLogs.length === 0" description="暂无操作日志" />
          <div class="pagination-wrap" v-if="operationLogsTotal > 0">
            <el-pagination
              v-model:current-page="operationLogsPage"
              v-model:page-size="operationLogsPageSize"
              :total="operationLogsTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @current-change="loadOperationLogs"
              @size-change="loadOperationLogs"
            />
          </div>
        </el-tab-pane>

        <!-- Tab 7: 统计 -->
        <el-tab-pane label="统计" name="statistics">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span style="font-weight: 600">任务进度</span>
                </template>
                <div class="stat-item">
                  <div class="stat-label">总任务数</div>
                  <div class="stat-value">{{ projectStats?.task_count ?? 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">已完成</div>
                  <div class="stat-value success">{{ projectStats?.approved_output_count ?? 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">成果数</div>
                  <div class="stat-value">{{ projectStats?.artifact_count ?? 0 }}</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span style="font-weight: 600">调用统计</span>
                </template>
                <div class="stat-item">
                  <div class="stat-label">总调用次数</div>
                  <div class="stat-value">{{ projectStats?.invocation_count ?? 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">总成本</div>
                  <div class="stat-value warning">¥{{ (projectStats?.total_cost ?? 0).toFixed(4) }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">产出数</div>
                  <div class="stat-value">{{ projectStats?.output_count ?? 0 }}</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span style="font-weight: 600">团队贡献</span>
                </template>
                <div class="stat-item">
                  <div class="stat-label">成员数</div>
                  <div class="stat-value">{{ projectStats?.member_count ?? members.length }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">任务数</div>
                  <div class="stat-value">{{ projectStats?.task_count ?? 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">采纳率</div>
                  <div class="stat-value">
                    {{ projectStats?.task_count ? ((projectStats?.artifact_count / projectStats?.task_count) * 100).toFixed(1) : 0 }}%
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加成员弹窗 -->
    <el-dialog v-model="addMemberDialogVisible" title="添加成员" width="480px" destroy-on-close>
      <el-form :model="addMemberForm" label-width="100px">
        <el-form-item label="选择用户" required>
          <el-select
            v-model="addMemberForm.user_id"
            placeholder="搜索用户"
            filterable
            style="width: 100%"
          >
            <el-option label="（请在用户管理中添加用户）" :value="undefined" disabled />
          </el-select>
        </el-form-item>
        <el-form-item label="项目角色">
          <el-select v-model="addMemberForm.project_role" style="width: 100%">
            <el-option
              v-for="r in roleOptions"
              :key="r.value"
              :label="r.label"
              :value="r.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMemberDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="addMemberLoading" @click="handleAddMember">添加</el-button>
      </template>
    </el-dialog>

    <!-- 创建任务弹窗 -->
    <el-dialog v-model="createTaskDialogVisible" title="创建任务" width="540px" destroy-on-close>
      <el-form :model="createTaskForm" label-width="110px">
        <el-form-item label="任务类型" required>
          <el-select v-model="createTaskForm.task_type_id" style="width: 100%">
            <el-option
              v-for="t in taskTypes"
              :key="t.task_type_id"
              :label="t.type_name"
              :value="t.task_type_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务标题" required>
          <el-input v-model="createTaskForm.title" placeholder="请输入任务标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input
            v-model="createTaskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述（可选）"
            maxlength="500"
          />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="createTaskForm.priority" style="width: 100%">
            <el-option
              v-for="p in priorityOptions"
              :key="p.value"
              :label="p.label"
              :value="p.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="createTaskForm.due_date"
            type="datetime"
            placeholder="选择截止时间（可选）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
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

<style scoped>
.breadcrumb-wrap {
  margin-bottom: 12px;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 4px 0 0;
}

.page-desc {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.cost-value {
  color: #e6a23c;
  font-weight: 600;
  font-size: 15px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.warning {
  color: #e6a23c;
}
</style>
