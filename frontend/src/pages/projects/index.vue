<script lang="ts" setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { getProjectListApi, createProjectApi } from "@/common/apis/projects"
import type { Project, CreateProjectRequestData, ProjectListParams } from "@/common/apis/projects/type"

const router = useRouter()
const loading = ref(false)
const projectList = ref<Project[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref("")
const selectedStatus = ref("")

const createDialogVisible = ref(false)
const createLoading = ref(false)
const createFormRef = ref()

const createForm = reactive<CreateProjectRequestData>({
  project_name: "",
  project_type: "course_project",
  description: ""
})

const projectTypeOptions = [
  { label: "课程项目", value: "course_project" },
  { label: "科研项目", value: "research_project" },
  { label: "竞赛项目", value: "competition_project" },
  { label: "企业实习", value: "internship_project" },
  { label: "毕业设计", value: "graduation_project" },
  { label: "其他", value: "other" }
]

const statusOptions = [
  { label: "进行中", value: "active", type: "success" },
  { label: "已归档", value: "archived", type: "info" },
  { label: "已暂停", value: "suspended", type: "warning" }
]

const createFormRules = {
  project_name: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
  project_type: [{ required: true, message: "请选择项目类型", trigger: "change" }]
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    active: "success",
    archived: "info",
    suspended: "warning",
    deleted: "danger"
  }
  return map[status] || "info"
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    active: "进行中",
    archived: "已归档",
    suspended: "已暂停",
    deleted: "已删除"
  }
  return map[status] || status
}

async function fetchProjects() {
  loading.value = true
  try {
    const params: ProjectListParams = {
      page: page.value,
      page_size: pageSize.value
    }
    if (keyword.value) params.keyword = keyword.value
    if (selectedStatus.value) params.status = selectedStatus.value

    const res = await getProjectListApi(params)
    projectList.value = res.data.items || []
    total.value = res.data.total || 0
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!createFormRef.value) return
  try {
    const valid = await createFormRef.value.validate()
    if (!valid) return

    createLoading.value = true
    await createProjectApi(createForm)
    ElMessage.success("项目创建成功")
    createDialogVisible.value = false
    createForm.project_name = ""
    createForm.project_type = "course_project"
    createForm.description = ""
    fetchProjects()
  } catch {
    // error shown by axios interceptor
  } finally {
    createLoading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchProjects()
}

function handleReset() {
  keyword.value = ""
  selectedStatus.value = ""
  page.value = 1
  fetchProjects()
}

function handlePageChange(newPage: number) {
  page.value = newPage
  fetchProjects()
}

function handleSizeChange(newSize: number) {
  pageSize.value = newSize
  page.value = 1
  fetchProjects()
}

function goToDetail(project: Project) {
  router.push(`/projects/${project.project_id}`)
}

fetchProjects()
</script>

<template>
  <div class="project-list-page">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">项目空间</h2>
        <span class="page-desc">管理所有参与的项目</span>
      </div>
      <el-button type="primary" @click="createDialogVisible = true">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input
            v-model="keyword"
            placeholder="搜索项目名称"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="selectedStatus" placeholder="全部状态" clearable style="width: 140px">
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="projectList"
        stripe
        style="width: 100%"
        @row-click="(row) => goToDetail(row)"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="project_name" label="项目名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click.stop="goToDetail(row)">
              {{ row.project_name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="project_type" label="项目类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">
              {{ projectTypeOptions.find(t => t.value === row.project_type)?.label || row.project_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="owner_real_name" label="负责人" width="120" align="center">
          <template #default="{ row }">
            {{ row.owner_real_name || row.owner_username || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" align="center">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="goToDetail(row)">
              查看
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无项目，点击右上角" />
        </template>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="createDialogVisible"
      title="新建项目"
      width="500px"
      :close-on-click-modal="false"
      @closed="createFormRef?.resetFields()"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="90px"
      >
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="createForm.project_name" placeholder="请输入项目名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="项目类型" prop="project_type">
          <el-select v-model="createForm.project_type" placeholder="请选择项目类型" style="width: 100%">
            <el-option
              v-for="opt in projectTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述（选填）"
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

<style lang="scss" scoped>
.project-list-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.page-desc {
  font-size: 13px;
  color: #909399;
}

.filter-card {
  margin-bottom: 16px;
}

.table-card {
  margin-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
