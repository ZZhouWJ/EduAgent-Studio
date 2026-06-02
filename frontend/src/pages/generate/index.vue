<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { projectsApi } from "@/api/projects"
import { tasksApi } from "@/api/tasks"
import { modelsApi } from "@/api/models"

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)

// Step 1: 选择项目
const projects = ref<any[]>([])
const selectedProject = ref<number | null>(null)

// Step 2: 选择任务
const tasks = ref<any[]>([])
const tasksLoading = ref(false)
const selectedTask = ref<number | null>(null)

// Step 3: 配置生成
const aiModels = ref<any[]>([])
const modelsLoading = ref(false)
const branches = ref<any[]>([])
const branchesLoading = ref(false)
const selectedBranch = ref<number | undefined>(undefined)
const selectedModelIds = ref<number[]>([])
const inputText = ref("")

const taskTypes = [
  { label: "需求分析", value: 1 },
  { label: "数据库设计", value: 2 },
  { label: "SQL 编写", value: 3 },
  { label: "摘要润色", value: 4 },
  { label: "文献综述", value: 5 },
  { label: "PPT 撰写", value: 6 },
  { label: "提案修订", value: 7 },
  { label: "实验总结", value: 8 },
  { label: "代码注释", value: 9 }
]

const step = ref(1)
const generateResult = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const res = await projectsApi.list({ page: 1, page_size: 100 })
    projects.value = res.data.items || []
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

async function loadModels() {
  modelsLoading.value = true
  try {
    const res = await modelsApi.getModels({ status: "active", page_size: 100 })
    aiModels.value = res.data?.items || []
  } catch {
    aiModels.value = []
  } finally {
    modelsLoading.value = false
  }
}

async function loadBranches(taskId: number) {
  branchesLoading.value = true
  try {
    const res = await tasksApi.getBranches(taskId)
    branches.value = res.data || []
    const active = branches.value.find(b => b.status === "active")
    selectedBranch.value = active?.branch_id
  } catch {
    branches.value = []
  } finally {
    branchesLoading.value = false
  }
}

function onProjectChange() {
  selectedTask.value = null
  tasks.value = []
  if (selectedProject.value) {
    loadTasks(selectedProject.value)
  }
}

function goToStep2() {
  if (!selectedProject.value) {
    ElMessage.warning("请先选择项目")
    return
  }
  step.value = 2
}

function goToStep3() {
  if (!selectedTask.value) {
    ElMessage.warning("请先选择任务")
    return
  }
  step.value = 3
  loadModels()
  loadBranches(selectedTask.value)
}

async function handleGenerate() {
  if (selectedModelIds.value.length === 0) {
    ElMessage.warning("请至少选择一个 AI 模型")
    return
  }
  if (branches.length > 0 && !selectedBranch.value) {
    ElMessage.warning("请选择目标分支")
    return
  }
  if (branches.length === 0) {
    ElMessage.error("该任务没有可用分支，无法生成输出，请先创建分支")
    return
  }
  if (!inputText.value.trim()) {
    ElMessage.warning("请输入生成提示词")
    return
  }
  submitting.value = true
  try {
    const res = await tasksApi.generate(selectedTask.value!, {
      branch_id: selectedBranch.value,
      model_ids: selectedModelIds.value,
      input_text: inputText.value
    })
    generateResult.value = res.data || []
    step.value = 4
    ElMessage.success(`生成完成，共 ${generateResult.value.length} 条结果`)
  } catch {
    // error handled
  } finally {
    submitting.value = false
  }
}

function goToTask() {
  router.push(`/tasks/${selectedTask.value}`)
}

function reset() {
  step.value = 1
  selectedProject.value = null
  selectedTask.value = null
  selectedBranch.value = undefined
  selectedModelIds.value = []
  inputText.value = ""
  generateResult.value = []
  tasks.value = []
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">AI 生成</h1>
      <p class="page-desc">快速发起 AI 内容生成任务，选择项目、任务并配置模型即可开始生成</p>
    </div>

    <!-- 步骤指示器 -->
    <el-steps :active="step - 1" finish-status="success" style="margin-bottom: 24px">
      <el-step title="选择项目" />
      <el-step title="选择任务" />
      <el-step title="配置生成" />
      <el-step title="查看结果" />
    </el-steps>

    <!-- Step 1: 选择项目 -->
    <el-card v-if="step === 1" v-loading="loading">
      <template #header>
        <span style="font-weight: 600">Step 1：选择项目</span>
      </template>
      <div class="project-grid">
        <div
          v-for="p in projects"
          :key="p.project_id"
          class="project-card"
          :class="{ selected: selectedProject === p.project_id }"
          @click="selectedProject = p.project_id"
        >
          <div class="project-name">{{ p.project_name }}</div>
          <div class="project-desc">{{ p.description || "暂无描述" }}</div>
          <el-tag size="small" :type="p.status === 'active' ? 'success' : 'info'">
            {{ p.status === "active" ? "活跃" : p.status }}
          </el-tag>
        </div>
        <el-empty v-if="projects.length === 0" description="暂无项目，请先创建项目" />
      </div>
      <div style="margin-top: 16px; text-align: right">
        <el-button type="primary" :disabled="!selectedProject" @click="goToStep2">
          下一步：选择任务
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </el-card>

    <!-- Step 2: 选择任务 -->
    <el-card v-if="step === 2">
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span style="font-weight: 600">Step 2：选择任务</span>
          <el-button text size="small" @click="step = 1">重新选择项目</el-button>
        </div>
      </template>
      <el-table
        v-loading="tasksLoading"
        :data="tasks"
        stripe
        highlight-current-row
        @row-click="(row: any) => selectedTask = row.task_id"
        :row-class-name="(_row: any, _idx: number) => selectedTask === _row.task_id ? 'selected-row' : ''"
      >
        <el-table-column prop="title" label="任务标题" min-width="200" />
        <el-table-column prop="type_name" label="任务类型" width="130" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" />
        <el-table-column prop="assignee_real_name" label="负责人" width="100" />
      </el-table>
      <el-empty v-if="!tasksLoading && tasks.length === 0" description="该项目暂无任务" />
      <div style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center">
        <el-button @click="step = 1">上一步</el-button>
        <el-button type="primary" :disabled="!selectedTask" @click="goToStep3">
          下一步：配置生成
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </el-card>

    <!-- Step 3: 配置生成 -->
    <el-card v-if="step === 3">
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span style="font-weight: 600">Step 3：配置 AI 生成</span>
          <el-button text size="small" @click="step = 2">重新选择任务</el-button>
        </div>
      </template>

      <el-form label-width="100px">
        <el-form-item label="选择分支">
          <el-select
            v-model="selectedBranch"
            placeholder="默认主分支（自动选择 active 分支）"
            clearable
            style="width: 100%"
            :loading="branchesLoading"
          >
            <el-option
              v-for="b in branches"
              :key="b.branch_id"
              :label="`${b.branch_name} (${b.status})`"
              :value="b.branch_id"
            />
          </el-select>
          <div v-if="branches.length === 0 && !branchesLoading" style="color: #909399; font-size: 12px; margin-top: 4px">
            暂无可用分支，无法写入输出版本
          </div>
        </el-form-item>

        <el-form-item label="选择模型" required>
          <el-checkbox-group v-model="selectedModelIds">
            <el-checkbox
              v-for="m in aiModels"
              :key="m.model_id"
              :value="m.model_id"
              style="margin-right: 12px; margin-bottom: 6px; display: block"
            >
              {{ m.display_name || m.model_name || `模型 #${m.model_id}` }}
              <span style="color: #909399; font-size: 12px">
                ({{ m.provider_name }})
              </span>
            </el-checkbox>
          </el-checkbox-group>
          <div v-if="aiModels.length === 0 && !modelsLoading" style="color: #909399; font-size: 13px">
            暂无可用模型
          </div>
        </el-form-item>

        <el-form-item label="生成提示词" required>
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="6"
            placeholder="请输入生成提示词，例如：请为数据库课程报告生成需求分析初稿，包括功能需求和非功能需求"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <el-alert
        title="提示：AI 生成结果将作为新版本添加到所选任务的输出版本列表中"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <div style="display: flex; gap: 8px; justify-content: flex-end">
        <el-button @click="step = 2">上一步</el-button>
        <el-button type="primary" :loading="submitting" @click="handleGenerate">
          <el-icon><Cpu /></el-icon> 开始生成
        </el-button>
      </div>
    </el-card>

    <!-- Step 4: 查看结果 -->
    <el-card v-if="step === 4">
      <template #header>
        <span style="font-weight: 600">Step 4：生成结果</span>
      </template>

      <div v-if="generateResult.length > 0" class="result-list">
        <div v-for="(r, idx) in generateResult" :key="r.invocation_id" class="result-item">
          <div class="result-header">
            <span style="font-weight: 600">结果 {{ idx + 1 }}</span>
            <el-tag
              size="small"
              :type="r.status === 'success' || r.status === 'completed' ? 'success' : 'danger'"
            >
              {{ r.status === "success" || r.status === "completed" ? "生成成功" : "生成失败" }}
            </el-tag>
          </div>
          <div class="result-info">
            <span>模型 ID: {{ r.model_id }}</span>
            <span v-if="r.output_id">输出 ID: {{ r.output_id }}</span>
            <span v-if="r.version_no">版本: v{{ r.version_no }}</span>
            <span v-if="r.input_tokens">输入 Token: {{ r.input_tokens }}</span>
            <span v-if="r.output_tokens">输出 Token: {{ r.output_tokens }}</span>
            <span v-if="r.latency_ms">耗时: {{ r.latency_ms }}ms</span>
          </div>
          <div v-if="r.error_message" style="color: #f56c6c; font-size: 13px">
            错误信息：{{ r.error_message }}
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无生成结果" />

      <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px">
        <el-button @click="reset">继续生成</el-button>
        <el-button type="primary" @click="goToTask">
          <el-icon><Folder /></el-icon> 前往任务详情查看
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { ArrowRight, Cpu, Folder } from "@element-plus/icons-vue"
export default { components: { ArrowRight, Cpu, Folder } }
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

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.project-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.project-card:hover {
  border-color: #1e3a5f;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.project-card.selected {
  border-color: #1e3a5f;
  background: #f0f5ff;
}

.project-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.project-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.result-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: #606266;
}

:deep(.selected-row) {
  background-color: #e6f0ff;
}
</style>
