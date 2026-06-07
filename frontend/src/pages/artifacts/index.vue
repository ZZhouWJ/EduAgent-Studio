<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { View, Download } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { artifactsApi } from "@/api/artifacts"
import { projectsApi } from "@/api/projects"
import { useUserStore } from "@/stores/user"
import { useProjectRoleStore } from "@/stores/projectRole"
import { isAdmin } from "@/utils/permission"

const userStore = useUserStore()
const projectRoleStore = useProjectRoleStore()

const loading = ref(false)
const artifacts = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const projectOptions = ref<any[]>([])
const filterProjectId = ref<number | null>(null)
const filterArtifactType = ref<string>("")
const searchKeyword = ref("")

// Detail drawer
const detailDrawerVisible = ref(false)
const detailLoading = ref(false)
const currentArtifact = ref<any>(null)

const artifactTypeOptions = [
  { label: "全部类型", value: "" },
  { label: "课程报告", value: "course_report" },
  { label: "数据库设计", value: "db_design" },
  { label: "文献综述", value: "literature_review" },
  { label: "实验报告", value: "experiment_report" },
  { label: "项目提案", value: "proposal" },
  { label: "其他", value: "other" }
]

const artifactTypeMap: Record<string, string> = {
  course_report: "课程报告",
  db_design: "数据库设计",
  literature_review: "文献综述",
  experiment_report: "实验报告",
  proposal: "项目提案",
  other: "其他"
}

// ── Permission helpers ─────────────────────────────────────────────────────────

const currentUser = computed(() => userStore.userInfo)

/** Filter artifacts so non-admin users only see artifacts from projects they are members of */
function filterByProjectMembership(items: any[]): any[] {
  if (isAdmin(currentUser.value)) return items
  return items.filter(a => {
    if (!a.project_id || !currentUser.value) return false
    const role = projectRoleStore.getCurrentUserProjectRole(a.project_id, currentUser.value.user_id)
    return role !== null
  })
}

onMounted(async () => {
  await loadProjectOptions()
  await loadArtifacts()
})

async function loadProjectOptions() {
  try {
    const res = await projectsApi.list({ page: 1, page_size: 200 })
    const allProjects = res.data?.items || []

    // Admin sees all projects; others only see projects they belong to
    if (isAdmin(currentUser.value)) {
      projectOptions.value = allProjects
    } else {
      const accessible: any[] = []
      for (const p of allProjects) {
        await ensureProjectMembers(p.project_id)
        const role = projectRoleStore.getCurrentUserProjectRole(p.project_id, currentUser.value?.user_id ?? 0)
        if (role !== null) accessible.push(p)
      }
      projectOptions.value = accessible
    }
  } catch {
    projectOptions.value = []
  }
}

async function ensureProjectMembers(projectId: number) {
  if (projectRoleStore.getMembers(projectId).length > 0) return
  try {
    const res = await projectsApi.getMembers(projectId)
    projectRoleStore.setMembers(projectId, res.data || [])
  } catch { /* ignore */ }
}

async function loadArtifacts() {
  loading.value = true
  try {
    let res
    // If no project filter is set, use the first accessible project as default
    const targetProjectId = filterProjectId.value ?? projectOptions.value[0]?.project_id ?? null

    if (targetProjectId) {
      res = await artifactsApi.list(targetProjectId, {
        page: page.value, page_size: pageSize.value,
        artifact_type: filterArtifactType.value || undefined
      })
      let items = res.data?.items || []
      // Apply project membership filter for non-admin users
      items = filterByProjectMembership(items)
      artifacts.value = items
      total.value = items.length
    } else {
      artifacts.value = []
      total.value = 0
    }
  } catch {
    artifacts.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function onFilterChange() {
  page.value = 1
  await loadArtifacts()
}

async function onPageChange(p: number) {
  page.value = p
  await loadArtifacts()
}

async function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  await loadArtifacts()
}

async function resetFilters() {
  filterProjectId.value = null
  filterArtifactType.value = ""
  searchKeyword.value = ""
  page.value = 1
  await loadArtifacts()
}

async function viewArtifact(adoptedId: number) {
  detailLoading.value = true
  detailDrawerVisible.value = true
  currentArtifact.value = null
  try {
    const res = await artifactsApi.getById(adoptedId)
    currentArtifact.value = res.data
  } catch {
    detailDrawerVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function exportArtifact(artifact: any) {
  const content = `# ${artifact.artifact_title}

## 基本信息
- 成果ID: ${artifact.adopted_id}
- 项目: ${artifact.project_name}
- 任务: ${artifact.task_title}
- 版本: v${artifact.version_no}
- 类型: ${artifactTypeMap[artifact.artifact_type] || artifact.artifact_type}
- 采用人: ${artifact.adopted_by_name}
- 采用时间: ${formatDate(artifact.adopted_at)}
${artifact.adopt_note ? `\n## 采用说明\n${artifact.adopt_note}\n` : ""}

---

## 成果内容

${artifact.output_content || "（无内容）"}
`
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `${artifact.artifact_title || "成果"}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success("导出成功")
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

const filteredArtifacts = computed(() => {
  if (!searchKeyword.value) return artifacts.value
  const kw = searchKeyword.value.toLowerCase()
  return artifacts.value.filter(a =>
    (a.artifact_title || "").toLowerCase().includes(kw) ||
    (a.project_name || "").toLowerCase().includes(kw) ||
    (a.task_title || "").toLowerCase().includes(kw)
  )
})
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">成果库</h1>
      <p class="page-desc">查看所有已审核通过并采用的 AI 协作成果，支持导出 Markdown 文件</p>
    </div>

    <!-- Filter bar -->
    <el-card style="margin-bottom: 16px" body-style="padding: 12px 16px">
      <el-row :gutter="12" align="middle">
        <el-col :span="6">
          <el-select v-model="filterProjectId" placeholder="按项目筛选" clearable
            @change="onFilterChange" style="width: 100%">
            <el-option v-for="p in projectOptions" :key="p.project_id"
              :label="p.project_name" :value="p.project_id" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterArtifactType" placeholder="按类型筛选" clearable
            @change="onFilterChange" style="width: 100%">
            <el-option v-for="t in artifactTypeOptions" :key="t.value"
              :label="t.label" :value="t.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-input v-model="searchKeyword" placeholder="搜索成果标题 / 项目 / 任务" clearable
            @change="onFilterChange" />
        </el-col>
        <el-col :span="8" style="text-align: right">
          <el-button @click="resetFilters">重置筛选</el-button>
          <span style="margin-left: 12px; color: #909399; font-size: 13px">
            共 {{ total }} 条成果
          </span>
        </el-col>
      </el-row>
    </el-card>

    <!-- Artifact list -->
    <el-card>
      <el-table v-loading="loading" :data="filteredArtifacts" stripe>
        <el-table-column prop="adopted_id" label="ID" width="70" />
        <el-table-column prop="artifact_title" label="成果标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="project_name" label="所属项目" min-width="140" show-overflow-tooltip />
        <el-table-column prop="task_title" label="来源任务" min-width="160" show-overflow-tooltip />
        <el-table-column label="成果类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ artifactTypeMap[row.artifact_type] || row.artifact_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="版本" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="success">v{{ row.version_no }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="adopted_by_name" label="采用人" width="100" />
        <el-table-column label="采用时间" width="170">
          <template #default="{ row }">{{ formatDate(row.adopted_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewArtifact(row.adopted_id)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button type="success" size="small" link @click="exportArtifact(row)">
              <el-icon><Download /></el-icon> 导出
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && artifacts.length === 0"
        description="暂无成果数据，请先完成任务 → 提交审核 → 通过审核后采用" />

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="page" v-model:page-size="pageSize" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
          @current-change="onPageChange" @size-change="onPageSizeChange" />
      </div>
    </el-card>

    <!-- 成果详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="成果详情" size="720px" direction="rtl" destroy-on-close>
      <div v-loading="detailLoading">
        <template v-if="currentArtifact">
          <el-descriptions :column="2" border size="small" style="margin-bottom: 16px">
            <el-descriptions-item label="成果ID">{{ currentArtifact.adopted_id }}</el-descriptions-item>
            <el-descriptions-item label="成果类型">
              <el-tag size="small">{{ artifactTypeMap[currentArtifact.artifact_type] || currentArtifact.artifact_type }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="成果标题" :span="2">{{ currentArtifact.artifact_title }}</el-descriptions-item>
            <el-descriptions-item label="所属项目">{{ currentArtifact.project_name }}</el-descriptions-item>
            <el-descriptions-item label="来源任务">{{ currentArtifact.task_title }}</el-descriptions-item>
            <el-descriptions-item label="输出版本">v{{ currentArtifact.version_no }}</el-descriptions-item>
            <el-descriptions-item label="发布版本">{{ currentArtifact.release_version || "-" }}</el-descriptions-item>
            <el-descriptions-item label="采用人">{{ currentArtifact.adopted_by_name }}</el-descriptions-item>
            <el-descriptions-item label="采用时间" :span="2">{{ formatDate(currentArtifact.adopted_at) }}</el-descriptions-item>
            <el-descriptions-item v-if="currentArtifact.adopt_note" label="采用说明" :span="2">
              {{ currentArtifact.adopt_note }}
            </el-descriptions-item>
          </el-descriptions>

          <!-- Action buttons -->
          <div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap">
            <el-button type="success" size="small" @click="exportArtifact(currentArtifact)">
              <el-icon><Download /></el-icon> 导出 Markdown
            </el-button>
          </div>

          <!-- Content -->
          <el-card shadow="never" body-style="padding: 0">
            <template #header><span style="font-weight: 600">成果正文</span></template>
            <div class="artifact-content">{{ currentArtifact.output_content || "（无内容）" }}</div>
          </el-card>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script lang="ts">
import { View, Download } from "@element-plus/icons-vue"
export default { components: { View, Download } }
</script>

<style scoped>
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
.page-title { font-size: 20px; font-weight: 700; color: #1e3a5f; margin: 0 0 4px; }
.page-desc { font-size: 13px; color: #909399; margin: 0; }
.artifact-content {
  background: #f5f7fa; border-radius: 0 0 6px 6px; padding: 16px;
  font-size: 13px; line-height: 1.8; color: #303133; white-space: pre-wrap;
  word-break: break-all; max-height: 500px; overflow-y: auto;
}
</style>
