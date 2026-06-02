<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { View, Edit, DocumentCopy, Switch, Plus, Search } from "@element-plus/icons-vue"
import { promptsApi, type PromptTemplate, type PromptVersion } from "@/api/prompts"
import { modelsApi, type TaskType } from "@/api/models"

// Tab control
const activeTab = ref("templates")

// Template list state
const loading = ref(false)
const templates = ref<PromptTemplate[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

// Filters
const searchKeyword = ref("")
const selectedTaskType = ref<number | null>(null)

// Task types for filter and form
const taskTypes = ref<TaskType[]>([])
const taskTypesLoading = ref(false)

// Create/Edit dialog
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const isEditMode = ref(false)
const editingTemplateId = ref<number | null>(null)

const formData = ref({
  template_name: "",
  task_type_id: undefined as number | undefined,
  initial_prompt_content: "",
  change_note: ""
})

// Version history dialog
const versionDialogVisible = ref(false)
const versionLoading = ref(false)
const versions = ref<PromptVersion[]>([])
const viewingTemplateId = ref<number | null>(null)
const viewingTemplateName = ref("")

// Add version dialog
const addVersionDialogVisible = ref(false)
const addVersionLoading = ref(false)
const addVersionForm = ref({
  prompt_content: "",
  change_note: ""
})

// View detail dialog
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const detailTemplate = ref<PromptTemplate | null>(null)

onMounted(async () => {
  await loadTaskTypes()
  await loadTemplates()
})

async function loadTaskTypes() {
  taskTypesLoading.value = true
  try {
    const res = await modelsApi.getTaskTypes()
    taskTypes.value = res.data || []
  } catch {
    taskTypes.value = []
  } finally {
    taskTypesLoading.value = false
  }
}

async function loadTemplates() {
  loading.value = true
  try {
    const res = await promptsApi.getTemplates({
      page: page.value,
      page_size: pageSize.value,
      task_type_id: selectedTaskType.value || undefined,
      keyword: searchKeyword.value || undefined
    })
    templates.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch {
    templates.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadTemplates()
}

function onFilterChange() {
  page.value = 1
  loadTemplates()
}

function onPageChange(p: number) {
  page.value = p
  loadTemplates()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadTemplates()
}

function openCreateDialog() {
  isEditMode.value = false
  editingTemplateId.value = null
  formData.value = {
    template_name: "",
    task_type_id: undefined,
    initial_prompt_content: "",
    change_note: ""
  }
  dialogVisible.value = true
}

function openEditDialog(template: PromptTemplate) {
  isEditMode.value = true
  editingTemplateId.value = template.template_id
  formData.value = {
    template_name: template.template_name,
    task_type_id: template.task_type_id,
    initial_prompt_content: "",
    change_note: ""
  }
  dialogVisible.value = true
}

async function handleSubmitDialog() {
  if (!formData.value.template_name.trim()) {
    ElMessage.warning("请输入模板名称")
    return
  }
  if (!formData.value.task_type_id) {
    ElMessage.warning("请选择关联任务类型")
    return
  }
  if (!isEditMode.value && !formData.value.initial_prompt_content.trim()) {
    ElMessage.warning("请输入初始提示词内容")
    return
  }

  dialogLoading.value = true
  try {
    if (isEditMode.value && editingTemplateId.value) {
      await promptsApi.updateTemplate(editingTemplateId.value, {
        template_name: formData.value.template_name,
        task_type_id: formData.value.task_type_id
      })
      ElMessage.success("模板更新成功")
    } else {
      await promptsApi.createTemplate({
        template_name: formData.value.template_name,
        task_type_id: formData.value.task_type_id,
        initial_prompt_content: formData.value.initial_prompt_content,
        change_note: formData.value.change_note || undefined
      })
      ElMessage.success("模板创建成功")
    }
    dialogVisible.value = false
    await loadTemplates()
  } catch {
    // error handled
  } finally {
    dialogLoading.value = false
  }
}

async function handleToggleActive(template: PromptTemplate) {
  const action = template.is_active ? "停用" : "启用"
  try {
    await ElMessageBox.confirm(`确定要${action}该模板吗？`, "确认", { type: "warning" })
    await promptsApi.updateTemplate(template.template_id, { is_active: !template.is_active })
    ElMessage.success(`${action}成功`)
    await loadTemplates()
  } catch {
    // cancelled or error
  }
}

async function handleDelete(template: PromptTemplate) {
  try {
    await ElMessageBox.confirm("确定要删除该模板吗？此操作不可恢复。", "确认删除", { type: "warning" })
    await promptsApi.deleteTemplate(template.template_id)
    ElMessage.success("删除成功")
    await loadTemplates()
  } catch {
    // cancelled or error
  }
}

async function openVersionHistory(template: PromptTemplate) {
  viewingTemplateId.value = template.template_id
  viewingTemplateName.value = template.template_name
  versionDialogVisible.value = true
  versionLoading.value = true
  versions.value = []
  try {
    const res = await promptsApi.getVersions(template.template_id)
    versions.value = res.data || []
  } catch {
    versions.value = []
  } finally {
    versionLoading.value = false
  }
}

function openAddVersionDialog() {
  addVersionForm.value = {
    prompt_content: "",
    change_note: ""
  }
  addVersionDialogVisible.value = true
}

async function handleAddVersion() {
  if (!addVersionForm.value.prompt_content.trim()) {
    ElMessage.warning("请输入提示词内容")
    return
  }
  if (!viewingTemplateId.value) return

  addVersionLoading.value = true
  try {
    await promptsApi.createVersion(viewingTemplateId.value, {
      prompt_content: addVersionForm.value.prompt_content,
      change_note: addVersionForm.value.change_note || undefined
    })
    ElMessage.success("版本添加成功")
    addVersionDialogVisible.value = false
    // Reload versions
    const res = await promptsApi.getVersions(viewingTemplateId.value)
    versions.value = res.data || []
    // Reload template list to update version number
    await loadTemplates()
  } catch {
    // error handled
  } finally {
    addVersionLoading.value = false
  }
}

async function handleActivateVersion(version: PromptVersion) {
  if (!viewingTemplateId.value) return
  if (version.is_active) {
    ElMessage.info("该版本已是启用状态")
    return
  }
  try {
    await ElMessageBox.confirm("确定要激活该版本吗？这将使该版本成为当前活跃版本。", "确认激活", { type: "warning" })
    await promptsApi.activateVersion(viewingTemplateId.value, version.version_id)
    ElMessage.success("版本激活成功")
    // Reload versions
    const res = await promptsApi.getVersions(viewingTemplateId.value)
    versions.value = res.data || []
    // Reload template list
    await loadTemplates()
  } catch {
    // cancelled or error
  }
}

async function viewTemplateDetail(template: PromptTemplate) {
  detailLoading.value = true
  detailDialogVisible.value = true
  detailTemplate.value = null
  try {
    const res = await promptsApi.getTemplateById(template.template_id)
    detailTemplate.value = res.data
  } catch {
    detailDialogVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function truncateContent(content: string, maxLength: number = 100) {
  if (!content) return "-"
  return content.length > maxLength ? content.slice(0, maxLength) + "..." : content
}

// All versions across all templates (for Tab 2)
const allVersions = ref<Array<PromptVersion & { template_name: string; template_id: number }>>([])
const allVersionsLoading = ref(false)
const allVersionsTotal = ref(0)
const allVersionsPage = ref(1)
const allVersionsPageSize = ref(10)

async function loadAllVersions() {
  allVersionsLoading.value = true
  try {
    // Load all templates first
    const templatesRes = await promptsApi.getTemplates({ page: 1, page_size: 100 })
    const allTemplates = templatesRes.data?.items || []

    // Then load versions for each template
    const versionPromises = allTemplates.map(async (t) => {
      try {
        const res = await promptsApi.getVersions(t.template_id)
        return (res.data || []).map((v) => ({
          ...v,
          template_name: t.template_name,
          template_id: t.template_id
        }))
      } catch {
        return []
      }
    })

    const results = await Promise.all(versionPromises)
    allVersions.value = results.flat().sort((a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    allVersionsTotal.value = allVersions.value.length
  } catch {
    allVersions.value = []
    allVersionsTotal.value = 0
  } finally {
    allVersionsLoading.value = false
  }
}

function onAllVersionsPageChange(p: number) {
  allVersionsPage.value = p
}

function onAllVersionsPageSizeChange(s: number) {
  allVersionsPageSize.value = s
  allVersionsPage.value = 1
}

async function activateVersionFromList(version: PromptVersion & { template_name: string }) {
  try {
    await ElMessageBox.confirm("确定要激活该版本吗？", "确认激活", { type: "warning" })
    await promptsApi.activateVersion(version.template_id, version.version_id)
    ElMessage.success("版本激活成功")
    await loadAllVersions()
  } catch {
    // cancelled or error
  }
}

function handleTabChange() {
  if (activeTab.value === "versions" && allVersions.value.length === 0) {
    loadAllVersions()
  }
}

// Computed for paginated all versions
function getPagedVersions() {
  const start = (allVersionsPage.value - 1) * allVersionsPageSize.value
  const end = start + allVersionsPageSize.value
  return allVersions.value.slice(start, end)
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">提示词管理</h1>
      <p class="page-desc">管理 AI 生成提示词模板及其版本历史</p>
    </div>

    <el-card>
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="模板列表" name="templates" />
            <el-tab-pane label="版本管理" name="versions" />
          </el-tabs>
          <el-button v-if="activeTab === 'templates'" type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新建模板
          </el-button>
        </div>
      </template>

      <!-- Tab 1: Template List -->
      <div v-if="activeTab === 'templates'">
        <!-- Filters -->
        <div class="filter-bar" style="margin-bottom: 16px">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索模板名称"
            style="width: 200px"
            clearable
            @keyup.enter="onSearch"
            @clear="onFilterChange"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select
            v-model="selectedTaskType"
            placeholder="任务类型"
            style="width: 160px"
            clearable
            :loading="taskTypesLoading"
            @change="onFilterChange"
          >
            <el-option
              v-for="t in taskTypes"
              :key="t.task_type_id"
              :label="t.type_name"
              :value="t.task_type_id"
            />
          </el-select>
          <el-button type="primary" @click="onSearch">搜索</el-button>
        </div>

        <!-- Table -->
        <el-table v-loading="loading" :data="templates" stripe>
          <el-table-column prop="template_name" label="模板名称" min-width="180">
            <template #default="{ row }">
              <div style="font-weight: 600">{{ row.template_name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="type_name" label="关联任务类型" width="130" />
          <el-table-column label="当前版本号" width="110">
            <template #default="{ row }">
              <el-tag size="small">v{{ row.current_version_no }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="是否启用" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'warning'" size="small">
                {{ row.is_active ? "已启用" : "已停用" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="170">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="viewTemplateDetail(row)">
                <el-icon><View /></el-icon> 详情
              </el-button>
              <el-button type="primary" size="small" link @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button type="primary" size="small" link @click="openVersionHistory(row)">
                <el-icon><DocumentCopy /></el-icon> 版本历史
              </el-button>
              <el-button type="warning" size="small" link @click="handleToggleActive(row)">
                <el-icon><Switch /></el-icon> {{ row.is_active ? "停用" : "启用" }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && templates.length === 0" description="暂无模板数据" />

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
      </div>

      <!-- Tab 2: Version Management -->
      <div v-if="activeTab === 'versions'">
        <el-table v-loading="allVersionsLoading" :data="getPagedVersions()" stripe>
          <el-table-column prop="template_name" label="模板名称" min-width="160">
            <template #default="{ row }">
              <div style="font-weight: 600">{{ row.template_name }}</div>
            </template>
          </el-table-column>
          <el-table-column label="版本号" width="90">
            <template #default="{ row }">
              <el-tag size="small">v{{ row.version_no }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="内容预览" min-width="200">
            <template #default="{ row }">
              <span style="color: #909399; font-size: 13px">{{ truncateContent(row.prompt_content, 80) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="change_note" label="变更说明" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? "活跃" : "非活跃" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="creator_real_name" label="创建人" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="170">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="!row.is_active"
                type="success"
                size="small"
                link
                @click="activateVersionFromList(row)"
              >
                激活
              </el-button>
              <span v-else style="color: #67c23a; font-size: 13px">当前版本</span>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!allVersionsLoading && allVersions.length === 0" description="暂无版本数据" />

        <div class="pagination-wrap" v-if="allVersionsTotal > 0">
          <el-pagination
            v-model:current-page="allVersionsPage"
            v-model:page-size="allVersionsPageSize"
            :total="allVersionsTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="onAllVersionsPageChange"
            @size-change="onAllVersionsPageSizeChange"
          />
        </div>
      </div>
    </el-card>

    <!-- Create/Edit Template Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑模板' : '新建模板'"
      width="560px"
      destroy-on-close
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item label="模板名称" required>
          <el-input v-model="formData.template_name" placeholder="请输入模板名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="关联任务类型" required>
          <el-select v-model="formData.task_type_id" placeholder="请选择任务类型" style="width: 100%" :loading="taskTypesLoading">
            <el-option
              v-for="t in taskTypes"
              :key="t.task_type_id"
              :label="t.type_name"
              :value="t.task_type_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isEditMode" label="初始提示词" required>
          <el-input
            v-model="formData.initial_prompt_content"
            type="textarea"
            :rows="6"
            placeholder="请输入提示词内容"
          />
        </el-form-item>
        <el-form-item v-if="!isEditMode" label="变更说明">
          <el-input
            v-model="formData.change_note"
            type="textarea"
            :rows="2"
            placeholder="请输入变更说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="handleSubmitDialog">
          {{ isEditMode ? "保存" : "创建" }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Version History Dialog -->
    <el-dialog
      v-model="versionDialogVisible"
      :title="`版本历史 - ${viewingTemplateName}`"
      width="700px"
      destroy-on-close
    >
      <div style="margin-bottom: 12px">
        <el-button type="primary" size="small" @click="openAddVersionDialog">
          <el-icon><Plus /></el-icon> 新增版本
        </el-button>
      </div>
      <el-table v-loading="versionLoading" :data="versions" stripe>
        <el-table-column label="版本号" width="90">
          <template #default="{ row }">
            <el-tag size="small">v{{ row.version_no }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提示词内容" min-width="200">
          <template #default="{ row }">
            <span style="color: #909399; font-size: 13px">{{ truncateContent(row.prompt_content, 100) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change_note" label="变更说明" min-width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? "活跃" : "非活跃" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_active"
              type="success"
              size="small"
              link
              @click="handleActivateVersion(row)"
            >
              激活
            </el-button>
            <span v-else style="color: #67c23a; font-size: 13px">当前</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!versionLoading && versions.length === 0" description="暂无版本数据" />
    </el-dialog>

    <!-- Add Version Dialog -->
    <el-dialog v-model="addVersionDialogVisible" title="新增版本" width="560px" destroy-on-close>
      <el-form :model="addVersionForm" label-width="100px">
        <el-form-item label="提示词内容" required>
          <el-input
            v-model="addVersionForm.prompt_content"
            type="textarea"
            :rows="8"
            placeholder="请输入提示词内容"
          />
        </el-form-item>
        <el-form-item label="变更说明">
          <el-input
            v-model="addVersionForm.change_note"
            type="textarea"
            :rows="3"
            placeholder="请输入本次变更说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVersionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="addVersionLoading" @click="handleAddVersion">添加</el-button>
      </template>
    </el-dialog>

    <!-- Template Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="模板详情" width="560px" destroy-on-close>
      <div v-loading="detailLoading">
        <template v-if="detailTemplate">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="模板ID">{{ detailTemplate.template_id }}</el-descriptions-item>
            <el-descriptions-item label="模板名称">{{ detailTemplate.template_name }}</el-descriptions-item>
            <el-descriptions-item label="关联任务类型">{{ detailTemplate.type_name }}</el-descriptions-item>
            <el-descriptions-item label="当前版本">v{{ detailTemplate.current_version_no }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="detailTemplate.is_active ? 'success' : 'warning'" size="small">
                {{ detailTemplate.is_active ? "已启用" : "已停用" }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(detailTemplate.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间" :span="2">{{ formatDate(detailTemplate.updated_at) }}</el-descriptions-item>
          </el-descriptions>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { View, Edit, DocumentCopy, Switch, Plus, Search } from "@element-plus/icons-vue"
export default { components: { View, Edit, DocumentCopy, Switch, Plus, Search } }
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

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
