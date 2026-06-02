<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { projectsApi } from "@/api/projects"

const router = useRouter()

const loading = ref(false)
const projects = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref("")
const statusFilter = ref("")

const createDialogVisible = ref(false)
const createLoading = ref(false)
const createForm = ref({
  project_name: "",
  project_type: "course_project",
  description: ""
})

const projectTypes = [
  { label: "课程项目", value: "course_project" },
  { label: "科研项目", value: "research_project" },
  { label: "竞赛项目", value: "competition_project" },
  { label: "企业项目", value: "enterprise_project" }
]

const statusOptions = [
  { label: "全部状态", value: "" },
  { label: "活跃", value: "active" },
  { label: "已完成", value: "completed" },
  { label: "已归档", value: "archived" }
]

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  loading.value = true
  try {
    const res = await projectsApi.list({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      status: statusFilter.value || undefined
    })
    projects.value = res.data.items || []
    total.value = res.data.total || 0
  } catch {
    projects.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadProjects()
}

function onPageChange(p: number) {
  page.value = p
  loadProjects()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadProjects()
}

function goDetail(row: any) {
  router.push(`/projects/${row.project_id}`)
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    active: "success",
    completed: "info",
    archived: "warning",
    suspended: "danger"
  }
  return map[status] || ""
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    active: "活跃",
    completed: "已完成",
    archived: "已归档",
    suspended: "已停用"
  }
  return map[status] || status
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    course_project: "课程项目",
    research_project: "科研项目",
    competition_project: "竞赛项目",
    enterprise_project: "企业项目"
  }
  return map[type] || type
}

async function handleCreate() {
  if (!createForm.value.project_name.trim()) {
    ElMessage.warning("请输入项目名称")
    return
  }
  createLoading.value = true
  try {
    await projectsApi.create(createForm.value)
    ElMessage.success("项目创建成功")
    createDialogVisible.value = false
    createForm.value = { project_name: "", project_type: "course_project", description: "" }
    loadProjects()
  } catch {
    // error handled by interceptor
  } finally {
    createLoading.value = false
  }
}

function openCreateDialog() {
  createForm.value = { project_name: "", project_type: "course_project", description: "" }
  createDialogVisible.value = true
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">项目空间</h1>
      <p class="page-desc">管理所有项目空间，查看成员和任务</p>
    </div>

    <el-card>
      <!-- 搜索和操作栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="keyword"
            placeholder="搜索项目名称"
            style="width: 220px"
            clearable
            @clear="onSearch"
            @keyup.enter="onSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="statusFilter" placeholder="状态" style="width: 140px" clearable @change="onSearch">
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <el-button type="primary" @click="onSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新建项目
          </el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="projects" stripe @row-click="goDetail" style="cursor: pointer; margin-top: 12px">
        <el-table-column prop="project_name" label="项目名称" min-width="180" />
        <el-table-column prop="project_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getTypeLabel(row.project_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner_real_name" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click.stop="goDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && projects.length === 0" description="暂无项目数据" />

      <!-- 分页 -->
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

    <!-- 新建项目弹窗 -->
    <el-dialog v-model="createDialogVisible" title="新建项目" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="createForm.project_name" placeholder="请输入项目名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="项目类型" required>
          <el-select v-model="createForm.project_type" style="width: 100%">
            <el-option
              v-for="t in projectTypes"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { Search, Plus } from "@element-plus/icons-vue"
export default { components: { Search, Plus } }
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.toolbar-right {
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
