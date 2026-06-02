<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ArrowLeft, Cpu, ChatLineSquare, CircleCheck, Collection, View, Edit, CopyDocument } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { tasksApi } from "@/api/tasks"
import { modelsApi } from "@/api/models"

const route = useRoute()
const router = useRouter()
const taskId = Number(route.params.taskId)

const loading = ref(false)
const task = ref<any>(null)
const branches = ref<any[]>([])
const outputs = ref<any[]>([])

// AI 生成相关
const generateDialogVisible = ref(false)
const generateLoading = ref(false)
const aiModels = ref<any[]>([])
const modelsLoading = ref(false)
const generateForm = ref({
  branch_id: undefined as number | undefined,
  model_ids: [] as number[],
  prompt_version_id: undefined as number | undefined,
  input_text: ""
})
const generateResult = ref<any[]>([])

// 输出详情抽屉
const outputDrawerVisible = ref(false)
const outputDrawerLoading = ref(false)
const currentOutput = ref<any>(null)

// 输出编辑弹窗
const editDialogVisible = ref(false)
const editLoading = ref(false)
const editForm = ref({
  content: "",
  lock_version: 0,
  edit_summary: ""
})

// 批注相关
const commentDialogVisible = ref(false)
const commentLoading = ref(false)
const commentForm = ref({
  comment_type: "comment" as "comment" | "suggestion" | "approval",
  comment_text: ""
})
const comments = ref<any[]>([])
const commentsLoading = ref(false)

// 提交审核
const reviewDialogVisible = ref(false)
const reviewLoading = ref(false)
const reviewForm = ref({
  reviewer_id: undefined as number | undefined,
  submit_note: ""
})

// 采用成果
const adoptDialogVisible = ref(false)
const adoptLoading = ref(false)
const adoptForm = ref({
  artifact_title: "",
  artifact_type: "course_report",
  release_version: "",
  adopt_note: ""
})

// 另存为新版本
const saveAsDialogVisible = ref(false)
const saveAsLoading = ref(false)
const saveAsForm = ref({
  output_title: "",
  content: "",
  edit_summary: "",
  branch_id: undefined as number | undefined
})

const artifactTypes = [
  { label: "课程报告", value: "course_report" },
  { label: "数据库设计", value: "db_design" },
  { label: "文献综述", value: "literature_review" },
  { label: "实验报告", value: "experiment_report" },
  { label: "项目提案", value: "proposal" },
  { label: "其他", value: "other" }
]

const commentTypes = [
  { label: "一般意见", value: "comment" },
  { label: "建议", value: "suggestion" },
  { label: "审批意见", value: "approval" }
]

onMounted(async () => {
  loading.value = true
  try {
    const [taskRes, branchesRes, outputsRes] = await Promise.all([
      tasksApi.getById(taskId),
      tasksApi.getBranches(taskId),
      tasksApi.getOutputs(taskId)
    ])
    task.value = taskRes.data
    branches.value = branchesRes.data || []
    outputs.value = outputsRes.data || []
  } catch {
    // error handled
  } finally {
    loading.value = false
  }
})

// AI 生成
async function openGenerateDialog() {
  generateForm.value = {
    branch_id: branches.value.find(b => b.status === "active")?.branch_id,
    model_ids: [],
    prompt_version_id: undefined,
    input_text: task.value?.description || ""
  }
  generateResult.value = []
  generateDialogVisible.value = true
  await loadModels()
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

async function handleGenerate() {
  if (generateForm.value.model_ids.length === 0) {
    ElMessage.warning("请至少选择一个 AI 模型")
    return
  }
  if (!generateForm.value.input_text.trim()) {
    ElMessage.warning("请输入生成提示词")
    return
  }
  generateLoading.value = true
  try {
    const res = await tasksApi.generate(taskId, {
      branch_id: generateForm.value.branch_id,
      model_ids: generateForm.value.model_ids,
      prompt_version_id: generateForm.value.prompt_version_id,
      input_text: generateForm.value.input_text
    })
    generateResult.value = res.data || []
    const outputsRes = await tasksApi.getOutputs(taskId)
    outputs.value = outputsRes.data || []
    ElMessage.success(`生成完成，共 ${generateResult.value.length} 条结果`)
  } catch {
    // error handled
  } finally {
    generateLoading.value = false
  }
}

// 查看输出详情
async function viewOutput(outputId: number) {
  outputDrawerLoading.value = true
  outputDrawerVisible.value = true
  currentOutput.value = null
  try {
    const res = await tasksApi.getOutputById(outputId)
    currentOutput.value = res.data
  } catch {
    outputDrawerVisible.value = false
  } finally {
    outputDrawerLoading.value = false
  }
  // 同时加载批注
  commentsLoading.value = true
  try {
    const res = await tasksApi.getOutputComments(outputId)
    comments.value = res.data || []
  } catch {
    comments.value = []
  } finally {
    commentsLoading.value = false
  }
}

// 编辑输出
function openEditDialog(output: any) {
  currentOutput.value = output
  editForm.value = {
    content: output.content || "",
    lock_version: output.lock_version || 0,
    edit_summary: ""
  }
  outputDrawerVisible.value = false
  editDialogVisible.value = true
}

async function handleEditOutput() {
  if (!editForm.value.content.trim()) {
    ElMessage.warning("内容不能为空")
    return
  }
  if (!editForm.value.edit_summary.trim()) {
    ElMessage.warning("请填写修改说明")
    return
  }
  editLoading.value = true
  try {
    await tasksApi.updateOutput(currentOutput.value.output_id, editForm.value)
    ElMessage.success("输出已更新")
    editDialogVisible.value = false
    const outputsRes = await tasksApi.getOutputs(taskId)
    outputs.value = outputsRes.data || []
  } catch {
    // error handled
  } finally {
    editLoading.value = false
  }
}

// 另存为新版本
function openSaveAsDialog(output: any) {
  currentOutput.value = output
  saveAsForm.value = {
    output_title: output.output_title || "",
    content: output.content || "",
    edit_summary: "",
    branch_id: output.branch_id
  }
  outputDrawerVisible.value = false
  editDialogVisible.value = false
  saveAsDialogVisible.value = true
}

async function handleSaveAsNewVersion() {
  if (!saveAsForm.value.output_title.trim()) {
    ElMessage.warning("请输入输出标题")
    return
  }
  if (!saveAsForm.value.content.trim()) {
    ElMessage.warning("内容不能为空")
    return
  }
  if (!currentOutput.value) return
  saveAsLoading.value = true
  try {
    const res = await tasksApi.saveAsNewVersion(currentOutput.value.output_id, {
      output_title: saveAsForm.value.output_title,
      content: saveAsForm.value.content,
      edit_summary: saveAsForm.value.edit_summary,
      branch_id: saveAsForm.value.branch_id
    })
    ElMessage.success("新版本已保存")
    saveAsDialogVisible.value = false
    const outputsRes = await tasksApi.getOutputs(taskId)
    outputs.value = outputsRes.data || []
    const newOutputId = res.data?.output_id
    if (newOutputId) {
      await viewOutput(newOutputId)
    }
  } catch {
    // error handled
  } finally {
    saveAsLoading.value = false
  }
}

// 添加批注
async function handleAddComment() {
  if (!commentForm.value.comment_text.trim()) {
    ElMessage.warning("请输入批注内容")
    return
  }
  if (!currentOutput.value) return
  commentLoading.value = true
  try {
    await tasksApi.addComment(currentOutput.value.output_id, commentForm.value)
    ElMessage.success("批注已添加")
    commentForm.value = { comment_type: "comment", comment_text: "" }
    const res = await tasksApi.getOutputComments(currentOutput.value.output_id)
    comments.value = res.data || []
  } catch {
    // error handled
  } finally {
    commentLoading.value = false
  }
}

// 更新批注状态
async function updateCommentStatus(commentId: number, status: string) {
  try {
    await tasksApi.updateCommentStatus(commentId, status as any)
    ElMessage.success("批注状态已更新")
    if (currentOutput.value) {
      const res = await tasksApi.getOutputComments(currentOutput.value.output_id)
      comments.value = res.data || []
    }
  } catch {
    // error handled
  }
}

// 提交审核
async function handleSubmitReview() {
  if (!currentOutput.value) return
  reviewLoading.value = true
  try {
    const res = await tasksApi.submitReview(currentOutput.value.output_id, {
      reviewer_id: reviewForm.value.reviewer_id,
      submit_note: reviewForm.value.submit_note
    })
    ElMessage.success(`提交审核成功，请求 ID: ${res.data.request_id}`)
    reviewDialogVisible.value = false
    const outputsRes = await tasksApi.getOutputs(taskId)
    outputs.value = outputsRes.data || []
  } catch {
    // error handled
  } finally {
    reviewLoading.value = false
  }
}

// 采用成果
async function handleAdopt() {
  if (!adoptForm.value.artifact_title.trim()) {
    ElMessage.warning("请输入成果标题")
    return
  }
  if (!currentOutput.value) return
  adoptLoading.value = true
  try {
    const res = await tasksApi.adoptOutput(currentOutput.value.output_id, adoptForm.value)
    ElMessage.success(`成果采用成功，成果 ID: ${res.data.adopted_id}`)
    adoptDialogVisible.value = false
    const outputsRes = await tasksApi.getOutputs(taskId)
    outputs.value = outputsRes.data || []
  } catch {
    // error handled
  } finally {
    adoptLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    draft: "info",
    generated: "primary",
    submitted: "warning",
    approved: "success",
    rejected: "danger",
    revision_required: "danger",
    adopted: "success",
    conflict_pending: "warning"
  }
  return map[status] || ""
}

function getCommentTypeLabel(type: string) {
  const map: Record<string, string> = {
    comment: "一般意见",
    suggestion: "建议",
    approval: "审批意见"
  }
  return map[type] || type
}

function getCommentTypeTag(type: string) {
  const map: Record<string, string> = {
    comment: "",
    suggestion: "warning",
    approval: "success"
  }
  return map[type] || ""
}

function getCommentStatusType(status: string) {
  const map: Record<string, string> = {
    open: "",
    resolved: "success",
    closed: "info"
  }
  return map[status] || ""
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <el-button text @click="router.push('/tasks')">
        <el-icon><ArrowLeft /></el-icon> 返回任务列表
      </el-button>
      <h1 class="page-title">{{ task?.title || "任务详情" }}</h1>
    </div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <!-- 左侧：任务信息 -->
      <el-col :span="12">
        <el-card v-loading="loading">
          <template #header>
            <span style="font-weight: 600">任务基本信息</span>
          </template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="任务ID">{{ task?.task_id }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag size="small">{{ task?.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="任务标题" :span="2">{{ task?.title }}</el-descriptions-item>
            <el-descriptions-item label="任务类型">{{ task?.type_name || task?.task_type_name || "-" }}</el-descriptions-item>
            <el-descriptions-item label="优先级">{{ task?.priority }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ task?.assignee_real_name || "-" }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ task?.description || "-" }}</el-descriptions-item>
            <el-descriptions-item label="创建时间" :span="2">{{ formatDate(task?.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右侧：AI 生成 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600">AI 生成</span>
          </template>
          <div class="generate-panel">
            <el-alert
              title="调用配置的 AI 模型为当前任务生成内容初稿，可选择多个模型对比效果"
              type="info"
              :closable="false"
              style="margin-bottom: 16px"
            />
            <el-button
              type="primary"
              size="large"
              @click="openGenerateDialog"
              style="width: 100%"
            >
              <el-icon><Cpu /></el-icon>
              发起 AI 生成
            </el-button>
            <p class="generate-tip">生成结果将出现在下方「输出版本」列表中</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分支信息 -->
    <el-card v-if="branches.length > 0" style="margin-bottom: 16px">
      <template #header>
        <span style="font-weight: 600">分支列表</span>
      </template>
      <el-tag
        v-for="b in branches"
        :key="b.branch_id"
        :type="b.status === 'active' ? 'success' : 'info'"
        style="margin-right: 8px; margin-bottom: 4px"
      >
        {{ b.branch_name }} ({{ b.status }})
      </el-tag>
    </el-card>

    <!-- 输出版本列表 -->
    <el-card>
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span style="font-weight: 600">输出版本列表</span>
          <span style="font-size: 12px; color: #909399">{{ outputs.length }} 个版本</span>
        </div>
      </template>
      <el-table :data="outputs" stripe v-loading="loading">
        <el-table-column prop="version_no" label="版本号" width="90">
          <template #default="{ row }">
            <el-tag size="small">v{{ row.version_no }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="output_title" label="标题" min-width="200" />
        <el-table-column prop="branch_name" label="分支" width="120" />
        <el-table-column prop="source_type" label="来源" width="80" />
        <el-table-column prop="status" label="状态" width="140">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_username" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewOutput(row.output_id)">
              <el-icon><View /></el-icon> 查看
            </el-button>
            <el-button
              v-if="row.status !== 'adopted'"
              type="warning"
              size="small"
              link
              @click="openEditDialog(row)"
            >
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button
              v-if="row.status === 'approved'"
              type="success"
              size="small"
              link
              @click="() => { currentOutput = row; adoptDialogVisible = true }"
            >
              <el-icon><Collection /></el-icon> 采用
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && outputs.length === 0" description="暂无输出，请先点击「发起 AI 生成」" />
    </el-card>

    <!-- AI 生成弹窗 -->
    <el-dialog v-model="generateDialogVisible" title="发起 AI 生成" width="600px" destroy-on-close>
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="选择分支">
          <el-select v-model="generateForm.branch_id" placeholder="默认主分支" clearable style="width: 100%">
            <el-option
              v-for="b in branches"
              :key="b.branch_id"
              :label="b.branch_name"
              :value="b.branch_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择模型" required>
          <el-checkbox-group v-model="generateForm.model_ids">
            <el-checkbox
              v-for="m in aiModels"
              :key="m.model_id"
              :value="m.model_id"
              :label="m.model_id"
              style="margin-right: 12px; display: block; margin-bottom: 6px"
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
            v-model="generateForm.input_text"
            type="textarea"
            :rows="5"
            placeholder="请输入生成提示词，例如：请生成数据库课程报告需求分析部分"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <!-- 生成结果 -->
      <div v-if="generateResult.length > 0" style="margin-top: 16px; border-top: 1px solid #e4e7ed; padding-top: 16px">
        <div style="font-weight: 600; margin-bottom: 8px">生成结果</div>
        <div v-for="r in generateResult" :key="r.invocation_id" style="margin-bottom: 8px">
          <el-tag size="small" :type="r.status === 'success' || r.status === 'completed' ? 'success' : 'danger'">
            {{ r.status }}
          </el-tag>
          <span style="margin-left: 8px; font-size: 13px">
            模型 #{{ r.model_id }}
            <span v-if="r.output_id" style="color: #67c23a">→ 输出 #{{ r.output_id }}</span>
            <span v-if="r.error_message" style="color: #f56c6c">，错误：{{ r.error_message }}</span>
          </span>
        </div>
      </div>

      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="generateLoading" @click="handleGenerate">
          开始生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 输出详情抽屉 -->
    <el-drawer v-model="outputDrawerVisible" title="输出详情" size="640px" direction="rtl" destroy-on-close>
      <div v-loading="outputDrawerLoading">
        <el-descriptions v-if="currentOutput" :column="2" border size="small" style="margin-bottom: 16px">
          <el-descriptions-item label="版本号">
            <el-tag size="small">v{{ currentOutput.version_no }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag size="small" :type="getStatusType(currentOutput.status)">{{ currentOutput.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分支">{{ currentOutput.branch_name }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentOutput.creator_username }}</el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">{{ formatDate(currentOutput.last_modified_at || currentOutput.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="修改说明" :span="2">{{ currentOutput.edit_summary || "-" }}</el-descriptions-item>
        </el-descriptions>

        <div style="margin-bottom: 16px">
          <div style="font-weight: 600; margin-bottom: 8px">正文内容</div>
          <div class="output-content">{{ currentOutput?.content || "暂无内容" }}</div>
        </div>

        <!-- 操作按钮 -->
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px">
          <el-button
            v-if="currentOutput?.status !== 'adopted'"
            type="warning"
            size="small"
            @click="openEditDialog(currentOutput)"
          >
            <el-icon><Edit /></el-icon> 编辑输出
          </el-button>
          <el-button
            v-if="currentOutput?.status === 'approved'"
            type="success"
            size="small"
            @click="adoptDialogVisible = true"
          >
            <el-icon><Collection /></el-icon> 采用成果
          </el-button>
          <el-button
            v-if="currentOutput?.status !== 'adopted'"
            type="primary"
            size="small"
            @click="openSaveAsDialog(currentOutput)"
          >
            <el-icon><CopyDocument /></el-icon> 另存为新版本
          </el-button>
          <el-button
            v-if="['generated', 'draft', 'revision_required'].includes(currentOutput?.status || '')"
            type="primary"
            size="small"
            @click="reviewDialogVisible = true"
          >
            <el-icon><CircleCheck /></el-icon> 提交审核
          </el-button>
        </div>

        <!-- 批注列表 -->
        <div>
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
            <div style="font-weight: 600; display: flex; align-items: center; gap: 6px">
              <el-icon><ChatLineSquare /></el-icon>
              批注列表
              <el-tag size="small">{{ comments.length }}</el-tag>
            </div>
            <el-button type="primary" size="small" @click="commentDialogVisible = true">
              添加批注
            </el-button>
          </div>

          <div v-loading="commentsLoading">
            <div v-for="c in comments" :key="c.comment_id" class="comment-item">
              <div class="comment-header">
                <div>
                  <el-tag size="small" :type="getCommentTypeTag(c.comment_type)" style="margin-right: 6px">
                    {{ getCommentTypeLabel(c.comment_type) }}
                  </el-tag>
                  <span style="font-weight: 500">{{ c.commenter_real_name || c.commenter_username }}</span>
                </div>
                <el-tag size="small" :type="getCommentStatusType(c.status)">{{ c.status }}</el-tag>
              </div>
              <div class="comment-text">{{ c.comment_text }}</div>
              <div class="comment-footer">
                <span>{{ formatDate(c.created_at) }}</span>
                <el-dropdown
                  v-if="c.status === 'open'"
                  @command="(cmd: string) => updateCommentStatus(c.comment_id, cmd)"
                >
                  <el-button size="small" link>更多</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="resolved">标记为已解决</el-dropdown-item>
                      <el-dropdown-item command="closed">关闭批注</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            <el-empty v-if="comments.length === 0 && !commentsLoading" description="暂无批注" />
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 编辑输出弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑输出" width="700px" destroy-on-close>
      <el-form :model="editForm" label-width="110px">
        <el-form-item label="正文内容" required>
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="12"
            placeholder="请输入修改后的内容"
          />
        </el-form-item>
        <el-form-item label="修改说明" required>
          <el-input
            v-model="editForm.edit_summary"
            type="textarea"
            :rows="2"
            placeholder="请简要说明本次修改的内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEditOutput">保存修改</el-button>
      </template>
    </el-dialog>

    <!-- 添加批注弹窗 -->
    <el-dialog v-model="commentDialogVisible" title="添加批注" width="500px" destroy-on-close>
      <el-form :model="commentForm" label-width="100px">
        <el-form-item label="批注类型" required>
          <el-select v-model="commentForm.comment_type" style="width: 100%">
            <el-option
              v-for="t in commentTypes"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="批注内容" required>
          <el-input
            v-model="commentForm.comment_text"
            type="textarea"
            :rows="4"
            placeholder="请输入批注内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="commentDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="commentLoading" @click="handleAddComment">提交批注</el-button>
      </template>
    </el-dialog>

    <!-- 提交审核弹窗 -->
    <el-dialog v-model="reviewDialogVisible" title="提交审核" width="480px" destroy-on-close>
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="审核说明">
          <el-input
            v-model="reviewForm.submit_note"
            type="textarea"
            :rows="3"
            placeholder="提交说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="reviewLoading" @click="handleSubmitReview">提交审核</el-button>
      </template>
    </el-dialog>

    <!-- 采用成果弹窗 -->
    <el-dialog v-model="adoptDialogVisible" title="采用为成果" width="500px" destroy-on-close>
      <el-form :model="adoptForm" label-width="100px">
        <el-form-item label="成果标题" required>
          <el-input v-model="adoptForm.artifact_title" placeholder="请输入成果标题" />
        </el-form-item>
        <el-form-item label="成果类型" required>
          <el-select v-model="adoptForm.artifact_type" style="width: 100%">
            <el-option
              v-for="t in artifactTypes"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发布版本">
          <el-input v-model="adoptForm.release_version" placeholder="例如 v1.0" />
        </el-form-item>
        <el-form-item label="采用说明">
          <el-input
            v-model="adoptForm.adopt_note"
            type="textarea"
            :rows="3"
            placeholder="采用说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adoptDialogVisible = false">取消</el-button>
        <el-button type="success" :loading="adoptLoading" @click="handleAdopt">确认采用</el-button>
      </template>
    </el-dialog>

    <!-- 另存为新版本弹窗 -->
    <el-dialog v-model="saveAsDialogVisible" title="另存为新版本" width="600px" destroy-on-close>
      <el-form :model="saveAsForm" label-width="100px">
        <el-form-item label="输出标题" required>
          <el-input v-model="saveAsForm.output_title" placeholder="请输入输出标题" />
        </el-form-item>
        <el-form-item label="目标分支">
          <el-select v-model="saveAsForm.branch_id" placeholder="默认当前分支" clearable style="width: 100%">
            <el-option
              v-for="b in branches"
              :key="b.branch_id"
              :label="b.branch_name"
              :value="b.branch_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="saveAsForm.content"
            type="textarea"
            :rows="8"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="修改说明">
          <el-input
            v-model="saveAsForm.edit_summary"
            type="textarea"
            :rows="2"
            placeholder="请简要说明本次保存的内容变更（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveAsDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saveAsLoading" @click="handleSaveAsNewVersion">保存新版本</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

.generate-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.generate-tip {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.output-content {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.comment-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  background: #fff;
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-text {
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 6px;
}

.comment-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}
</style>
