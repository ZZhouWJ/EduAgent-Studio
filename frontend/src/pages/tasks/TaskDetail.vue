<script lang="ts" setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  getTaskDetailApi,
  getTaskBranchesApi,
  getTaskOutputsApi,
  getOutputDetailApi,
  getOutputTimelineApi,
  generateTaskOutputApi,
  updateOutputApi,
  saveOutputAsNewVersionApi,
  getOutputCommentsApi,
  createOutputCommentApi,
  updateCommentStatusApi
} from "@/common/apis/tasks"
import { getModelListApi } from "@/common/apis/models"
import { getTemplateListApi, getTemplateVersionsApi } from "@/common/apis/prompts"
import type {
  Task,
  TaskBranch,
  TaskOutput,
  OutputTimeline,
  OutputComment,
  GenerateResultItem
} from "@/common/apis/tasks/type"
import type { AIModel } from "@/common/apis/models/type"
import type { PromptTemplate, PromptVersion } from "@/common/apis/prompts/type"

const route = useRoute()
const router = useRouter()
const taskId = Number(route.params.taskId)

// ─── Base Data ────────────────────────────────────────────────────────────────

const loading = ref(false)
const task = ref<Partial<Task>>({})
const branches = ref<TaskBranch[]>([])
const outputs = ref<TaskOutput[]>([])

// ─── AI Generation ──────────────────────────────────────────────────────────────

const genDialogVisible = ref(false)
const genLoading = ref(false)
const genResults = ref<GenerateResultItem[]>([])

const modelList = ref<AIModel[]>([])
const templateList = ref<PromptTemplate[]>([])
const versionList = ref<PromptVersion[]>([])
const modelsLoading = ref(false)
const templatesLoading = ref(false)
const versionsLoading = ref(false)

const genFormRef = ref()

/** 统一表单对象，所有 v-model 和 rules 都绑定此对象 */
const genForm = ref({
  model_ids: [] as number[],
  branch_id: null as number | null,
  template_id: null as number | null,
  prompt_version_id: null as number | null,
  input_text: ""
})

const genRules = {
  model_ids: [
    {
      type: "array",
      required: true,
      message: "请至少选择一个模型",
      trigger: "change"
    }
  ],
  input_text: [
    { required: true, message: "请输入生成内容描述", trigger: "blur" }
  ]
}

async function loadModels() {
  modelsLoading.value = true
  try {
    const res = await getModelListApi({ page: 1, page_size: 100 })
    modelList.value = res.data.items || []
  } catch { /* shown by interceptor */ }
  finally { modelsLoading.value = false }
}

async function loadTemplates(taskTypeId?: number) {
  templatesLoading.value = true
  genForm.value.prompt_version_id = null
  versionList.value = []
  try {
    const params: Record<string, unknown> = { page: 1, page_size: 100 }
    if (taskTypeId) params.task_type_id = taskTypeId
    const res = await getTemplateListApi(params as Record<string, string | number>)
    templateList.value = res.data.items || []
  } catch { /* shown by interceptor */ }
  finally { templatesLoading.value = false }
}

async function onTemplateChange(templateId: number) {
  versionsLoading.value = true
  try {
    const res = await getTemplateVersionsApi(templateId)
    versionList.value = res.data || []
  } catch { /* shown by interceptor */ }
  finally { versionsLoading.value = false }
}

function openGenDialog() {
  genDialogVisible.value = true
  genResults.value = []
  genForm.value = {
    model_ids: [],
    branch_id: branches.value.length > 0 ? branches.value[0].branch_id : null,
    template_id: null,
    prompt_version_id: null,
    input_text: task.value.description || ""
  }
  versionList.value = []
  loadModels()
  loadTemplates(task.value.task_type_id)
}

async function handleGenerate() {
  if (!genFormRef.value) return
  try {
    const valid = await genFormRef.value.validate()
    if (!valid) return

    genLoading.value = true
    genResults.value = []
    const res = await generateTaskOutputApi(taskId, {
      model_ids: genForm.value.model_ids,
      branch_id: genForm.value.branch_id || undefined,
      prompt_version_id: genForm.value.prompt_version_id || undefined,
      input_text: genForm.value.input_text
    })
    genResults.value = res.data || []

    const allSuccess = genResults.value.every(r => r.status === "success")
    if (allSuccess) {
      ElMessage.success("AI 生成完成，请在输出版本列表查看结果")
      await fetchOutputs()
    } else {
      const failed = genResults.value.filter(r => r.status !== "success")
      if (failed.length === genResults.value.length) {
        ElMessage.error("所有模型均生成失败")
      } else {
        ElMessage.warning(`${failed.length} 个模型生成失败，请查看结果`)
      }
    }
  } catch (err: unknown) {
    const code = (err as Record<string, unknown>)?.code as number | undefined
    if (code === 4004) {
      ElMessage.error("版本已被修改，请刷新后重试")
    }
  } finally {
    genLoading.value = false
  }
}

// ─── Output Detail + Comments ─────────────────────────────────────────────────

const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const outputDetail = ref<Partial<TaskOutput>>({})
const outputTimeline = ref<OutputTimeline[]>([])

const comments = ref<OutputComment[]>([])
const commentsLoading = ref(false)
const commentFormRef = ref()
const commentForm = ref({
  comment_type: "comment" as "comment" | "suggestion" | "approval",
  comment_text: ""
})
const commentRules = {
  comment_type: [{ required: true, message: "请选择批注类型", trigger: "change" }],
  comment_text: [{ required: true, message: "请输入批注内容", trigger: "blur" }]
}
const commentLoading = ref(false)

async function viewOutputDetail(output: TaskOutput) {
  detailDialogVisible.value = true
  detailLoading.value = true
  outputDetail.value = { ...output }
  outputTimeline.value = []
  comments.value = []
  try {
    const [detailRes, timelineRes] = await Promise.all([
      getOutputDetailApi(output.output_id),
      getOutputTimelineApi(output.output_id)
    ])
    outputDetail.value = { ...detailRes.data }
    outputTimeline.value = timelineRes.data || []
    loadComments(output.output_id)
  } catch { /* shown by interceptor */ }
  finally { detailLoading.value = false }
}

async function loadComments(outputId: number) {
  commentsLoading.value = true
  try {
    const res = await getOutputCommentsApi(outputId)
    comments.value = res.data || []
  } catch { /* shown by interceptor */ }
  finally { commentsLoading.value = false }
}

async function handleAddComment() {
  if (!commentFormRef.value || !outputDetail.value.output_id) return
  try {
    const valid = await commentFormRef.value.validate()
    if (!valid) return
    commentLoading.value = true
    await createOutputCommentApi(outputDetail.value.output_id, {
      comment_type: commentForm.value.comment_type,
      comment_text: commentForm.value.comment_text
    })
    ElMessage.success("批注已添加")
    commentForm.value.comment_type = "comment"
    commentForm.value.comment_text = ""
    loadComments(outputDetail.value.output_id)
  } catch { /* shown by interceptor */ }
  finally { commentLoading.value = false }
}

async function handleUpdateCommentStatus(comment: OutputComment, newStatus: "open" | "resolved" | "closed") {
  try {
    await updateCommentStatusApi(comment.comment_id, { status: newStatus })
    ElMessage.success("批注状态已更新")
    if (outputDetail.value.output_id) loadComments(outputDetail.value.output_id)
  } catch { /* shown by interceptor */ }
}

// ─── Output Edit Dialog ───────────────────────────────────────────────────────

const editDialogVisible = ref(false)
const editFormRef = ref()
const editLoading = ref(false)
const editForm = ref({
  content: "",
  lock_version: 0,
  edit_summary: ""
})
const editRules = {
  content: [{ required: true, message: "内容不能为空", trigger: "blur" }],
  lock_version: [{ required: true, message: "版本锁缺失，请刷新后重试", trigger: "blur" }],
  edit_summary: [{ required: true, message: "请填写修改说明", trigger: "blur" }]
}

function openEditDialog() {
  editFormRef.value?.resetFields()
  editForm.value.content = outputDetail.value.content || ""
  editForm.value.lock_version = outputDetail.value.lock_version || 0
  editForm.value.edit_summary = ""
  editDialogVisible.value = true
}

async function handleEditSave() {
  if (!editFormRef.value || !outputDetail.value.output_id) return
  try {
    const valid = await editFormRef.value.validate()
    if (!valid) return
    editLoading.value = true
    await updateOutputApi(outputDetail.value.output_id, {
      content: editForm.value.content,
      lock_version: editForm.value.lock_version,
      edit_summary: editForm.value.edit_summary
    })
    ElMessage.success("保存成功")
    editDialogVisible.value = false
    await refreshDetail()
    await fetchOutputs()
  } catch (err: unknown) {
    const code = (err as Record<string, unknown>)?.code as number | undefined
    if (code === 4004) {
      ElMessage.error("当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。")
    }
  } finally {
    editLoading.value = false
  }
}

// ─── Save As New Version Dialog ───────────────────────────────────────────────

const saveAsDialogVisible = ref(false)
const saveAsFormRef = ref()
const saveAsLoading = ref(false)
const saveAsForm = ref({
  output_title: "",
  content: "",
  edit_summary: ""
})
const saveAsRules = {
  output_title: [{ required: true, message: "请输入版本标题", trigger: "blur" }],
  content: [{ required: true, message: "内容不能为空", trigger: "blur" }]
}

function openSaveAsDialog() {
  saveAsFormRef.value?.resetFields()
  saveAsForm.value.output_title = `${outputDetail.value.output_title || "新版本"}`
  saveAsForm.value.content = outputDetail.value.content || ""
  saveAsForm.value.edit_summary = ""
  saveAsDialogVisible.value = true
}

async function handleSaveAs() {
  if (!saveAsFormRef.value || !outputDetail.value.output_id) return
  try {
    const valid = await saveAsFormRef.value.validate()
    if (!valid) return
    saveAsLoading.value = true
    const res = await saveOutputAsNewVersionApi(outputDetail.value.output_id, {
      output_title: saveAsForm.value.output_title,
      content: saveAsForm.value.content,
      edit_summary: saveAsForm.value.edit_summary,
      branch_id: outputDetail.value.branch_id || undefined
    })
    ElMessage.success(`新版本 v${res.data?.version_no} 已创建`)
    saveAsDialogVisible.value = false
    await fetchOutputs()
    if (res.data?.output_id) {
      const newOutput: TaskOutput = { ...outputDetail.value, ...res.data } as TaskOutput
      await viewOutputDetail(newOutput)
    }
  } catch { /* shown by interceptor */ }
  finally { saveAsLoading.value = false }
}

// ─── Helpers ────────────────────────────────────────────────────────────────────

async function refreshDetail() {
  if (!outputDetail.value.output_id) return
  try {
    const res = await getOutputDetailApi(outputDetail.value.output_id)
    outputDetail.value = { ...res.data }
  } catch { /* shown by interceptor */ }
}

async function fetchOutputs() {
  const res = await getTaskOutputsApi(taskId, { page: 1, page_size: 50 })
  outputs.value = getOutputList(res.data)
}

function getOutputList(data: unknown): TaskOutput[] {
  if (Array.isArray(data)) return data
  const obj = data as Record<string, unknown>
  if (obj && Array.isArray(obj.items)) return obj.items as TaskOutput[]
  return []
}

function getStatusType(status: string) {
  const m: Record<string, string> = {
    draft: "info", pending: "info", running: "primary", in_progress: "primary",
    generated: "success", submitted: "warning", approved: "success",
    rejected: "danger", revision_required: "warning", adopted: "success", deleted: "info"
  }
  return m[status] || "info"
}

function getStatusLabel(status: string) {
  const m: Record<string, string> = {
    draft: "草稿", pending: "待处理", running: "进行中", in_progress: "进行中",
    generated: "已生成", submitted: "已提交", approved: "已通过",
    rejected: "已拒绝", revision_required: "需修改", adopted: "已采用", deleted: "已删除"
  }
  return m[status] || status
}

function getPriorityTagType(p: string) {
  return { high: "danger", normal: "primary", low: "info" }[p] || "info"
}

function getPriorityLabel(p: string) {
  return { high: "高", normal: "中", low: "低" }[p] || p
}

function getSourceTypeLabel(type: string) {
  return { ai_generated: "AI 生成", manual: "人工编辑" }[type] || type
}

function getCommentTypeLabel(type: string) {
  return { comment: "批注", suggestion: "修改建议", approval: "审核意见" }[type] || type
}

function getCommentStatusLabel(status: string) {
  return { open: "待处理", resolved: "已解决", closed: "已关闭" }[status] || status
}

function getCommentStatusType(status: string) {
  return { open: "warning", resolved: "success", closed: "info" }[status] || "info"
}

function getGenStatusType(status: string) {
  return status === "success" ? "success" : "danger"
}

function getModelDisplayName(modelId: number) {
  const m = modelList.value.find(m => m.model_id === modelId)
  return m?.display_name || m?.model_name || `模型 #${modelId}`
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
  } catch { /* shown by interceptor */ }
  finally { loading.value = false }
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
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="所属项目" :span="2">
              <el-link v-if="task.project_id" type="primary" :underline="false"
                @click="router.push(`/projects/${task.project_id}`)">
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

        <!-- 分支 -->
        <el-tab-pane label="分支">
          <el-table :data="branches" stripe style="width: 100%">
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="branch_name" label="分支名称" min-width="180" />
            <el-table-column prop="base_output_title" label="基准版本" width="180" show-overflow-tooltip>
              <template #default="{ row }">{{ row.base_output_title || "-" }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="creator_real_name" label="创建人" width="120" align="center">
              <template #default="{ row }">{{ row.creator_real_name || row.creator_username || "-" }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <template #empty><el-empty description="暂无分支" /></template>
          </el-table>
        </el-tab-pane>

        <!-- 输出版本 -->
        <el-tab-pane label="输出版本">
          <div style="margin-bottom: 12px; text-align: right">
            <el-button type="primary" @click="openGenDialog">
              <el-icon style="margin-right: 4px"><MagicStick /></el-icon>
              AI 生成
            </el-button>
          </div>
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
              <template #default="{ row }">{{ row.creator_real_name || row.creator_username || "-" }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" align="center">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString("zh-CN") : "-" }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click.stop="viewOutputDetail(row)">查看</el-button>
              </template>
            </el-table-column>
            <template #empty><el-empty description="暂无输出版本，点击「AI 生成」创建" /></template>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- ─── AI Generation Dialog ─────────────────────────────────────────────── -->
    <el-dialog
      v-model="genDialogVisible"
      title="AI 生成"
      width="680px"
      :close-on-click-modal="false"
    >
      <el-form ref="genFormRef" :model="genForm" :rules="genRules" label-width="100px">
        <el-form-item label="选择模型" prop="model_ids">
          <el-select
            v-model="genForm.model_ids"
            multiple
            placeholder="请选择模型（可多选）"
            style="width: 100%"
            :loading="modelsLoading"
            filterable
          >
            <el-option v-for="m in modelList" :key="m.model_id" :label="m.display_name" :value="m.model_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="提示词模板">
          <el-select
            v-model="genForm.template_id"
            placeholder="选择模板（可选）"
            style="width: 100%"
            :loading="templatesLoading"
            clearable
            @change="(val: number) => val && onTemplateChange(val)"
          >
            <el-option v-for="t in templateList" :key="t.template_id" :label="t.template_name" :value="t.template_id" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="versionList.length > 0" label="模板版本">
          <el-select
            v-model="genForm.prompt_version_id"
            placeholder="选择版本（可选）"
            style="width: 100%"
            :loading="versionsLoading"
            clearable
          >
            <el-option
              v-for="v in versionList"
              :key="v.prompt_version_id"
              :label="`v${v.version_no} - ${v.version_name || ''}`"
              :value="v.prompt_version_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="生成内容" prop="input_text">
          <el-input
            v-model="genForm.input_text"
            type="textarea"
            :rows="4"
            placeholder="请描述需要生成的内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <div v-if="genResults.length > 0" style="margin-top: 16px">
        <el-divider content-position="left">生成结果</el-divider>
        <div style="max-height: 240px; overflow-y: auto">
          <el-card
            v-for="r in genResults"
            :key="r.invocation_id"
            shadow="never"
            class="gen-result-card"
            :body-style="{ padding: '10px 12px' }"
          >
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px">
              <span style="font-weight: 600; font-size: 14px">
                {{ getModelDisplayName(r.model_id) }}
              </span>
              <el-tag size="small" :type="getGenStatusType(r.status)">
                {{ r.status === "success" ? "成功" : "失败" }}
              </el-tag>
            </div>
            <div v-if="r.status === 'success'" style="font-size: 13px; color: #67c23a">
              生成完成，版本 v{{ r.version_no }}，输出 ID: {{ r.output_id || "-" }}
            </div>
            <div v-if="r.status === 'failed' && r.error_message" style="font-size: 13px; color: #f56c6c">
              错误：{{ r.error_message }}
            </div>
            <div v-if="r.status === 'success'" style="font-size: 12px; color: #909399; margin-top: 4px">
              输入 tokens: {{ r.input_tokens || 0 }} · 输出 tokens: {{ r.output_tokens || 0 }} · 耗时: {{ r.latency_ms || 0 }}ms
            </div>
          </el-card>
        </div>
      </div>

      <template #footer>
        <el-button @click="genDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="genLoading" @click="handleGenerate">开始生成</el-button>
      </template>
    </el-dialog>

    <!-- ─── Output Detail Dialog ────────────────────────────────────────────────── -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`版本详情 - ${outputDetail.output_title || `v${outputDetail.version_no}`}`"
      width="800px"
      :close-on-click-modal="true"
    >
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border style="margin-bottom: 12px">
          <el-descriptions-item label="版本标题">{{ outputDetail.output_title || "-" }}</el-descriptions-item>
          <el-descriptions-item label="版本号">v{{ outputDetail.version_no }}</el-descriptions-item>
          <el-descriptions-item label="来源">
            <el-tag size="small">{{ getSourceTypeLabel(outputDetail.source_type || "") }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag size="small" :type="getStatusType(outputDetail.status || '')">
              {{ getStatusLabel(outputDetail.status || "") }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本锁">v{{ outputDetail.lock_version }}</el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ outputDetail.creator_real_name || outputDetail.creator_username || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ outputDetail.created_at ? new Date(outputDetail.created_at).toLocaleString("zh-CN") : "-" }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-bottom: 12px">
          <el-button type="primary" size="small" @click="openEditDialog">编辑输出</el-button>
          <el-button size="small" @click="openSaveAsDialog">另存为新版本</el-button>
        </div>

        <div v-if="outputDetail.content" class="content-preview">
          <div class="content-label">版本内容</div>
          <el-input :model-value="outputDetail.content" type="textarea" :rows="8" readonly resize="none" />
        </div>

        <!-- Comments -->
        <div class="comments-section">
          <div class="content-label">批注列表</div>
          <div v-loading="commentsLoading" style="min-height: 60px">
            <div v-if="comments.length === 0 && !commentsLoading" style="color: #909399; font-size: 13px; padding: 8px 0">
              暂无批注
            </div>
            <el-card
              v-for="c in comments"
              :key="c.comment_id"
              shadow="never"
              class="comment-card"
              :body-style="{ padding: '10px 12px' }"
            >
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px">
                <div style="display: flex; align-items: center; gap: 8px">
                  <el-tag size="small">{{ getCommentTypeLabel(c.comment_type) }}</el-tag>
                  <span style="font-size: 13px; color: #606266">
                    {{ c.commenter_real_name || c.commenter_username || "未知用户" }}
                  </span>
                  <span style="font-size: 12px; color: #909399">
                    {{ new Date(c.created_at).toLocaleString("zh-CN") }}
                  </span>
                </div>
                <el-tag size="small" :type="getCommentStatusType(c.status)">
                  {{ getCommentStatusLabel(c.status) }}
                </el-tag>
              </div>
              <div style="font-size: 13px; color: #303133; white-space: pre-wrap">{{ c.comment_text }}</div>
              <div style="margin-top: 6px">
                <el-button
                  v-if="c.status === 'open'"
                  link type="success" size="small"
                  @click="handleUpdateCommentStatus(c, 'resolved')"
                >标记为已解决</el-button>
                <el-button
                  v-if="c.status !== 'closed'"
                  link type="info" size="small"
                  @click="handleUpdateCommentStatus(c, 'closed')"
                >关闭</el-button>
              </div>
            </el-card>
          </div>

          <el-form ref="commentFormRef" :model="commentForm" :rules="commentRules" inline style="margin-top: 12px">
            <el-form-item prop="comment_type" style="margin-bottom: 0; width: 140px">
              <el-select v-model="commentForm.comment_type" placeholder="批注类型" style="width: 130px">
                <el-option label="批注" value="comment" />
                <el-option label="修改建议" value="suggestion" />
                <el-option label="审核意见" value="approval" />
              </el-select>
            </el-form-item>
            <el-form-item prop="comment_text" style="margin-bottom: 0; flex: 1">
              <el-input v-model="commentForm.comment_text" placeholder="输入批注内容" style="width: 100%" />
            </el-form-item>
            <el-form-item style="margin-bottom: 0">
              <el-button type="primary" size="small" :loading="commentLoading" @click="handleAddComment">添加</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- Timeline -->
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
                  <el-tag size="small" style="margin-left: 8px"
                    :type="item.source_type === 'ai_generated' ? 'primary' : 'success'">
                    {{ getSourceTypeLabel(item.source_type) }}
                  </el-tag>
                </p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ─── Edit Output Dialog ─────────────────────────────────────────────── -->
    <el-dialog v-model="editDialogVisible" title="编辑输出" width="680px" :close-on-click-modal="false">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="90px">
        <el-form-item label="版本锁">v{{ editForm.lock_version }}</el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="editForm.content" type="textarea" :rows="10" placeholder="请输入正文内容" />
        </el-form-item>
        <el-form-item label="修改说明" prop="edit_summary">
          <el-input
            v-model="editForm.edit_summary"
            type="textarea"
            :rows="2"
            placeholder="请描述本次修改内容（必填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- ─── Save As New Version Dialog ──────────────────────────────────── -->
    <el-dialog v-model="saveAsDialogVisible" title="另存为新版本" width="680px" :close-on-click-modal="false">
      <el-form ref="saveAsFormRef" :model="saveAsForm" :rules="saveAsRules" label-width="90px">
        <el-form-item label="版本标题" prop="output_title">
          <el-input v-model="saveAsForm.output_title" placeholder="请输入新版本标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="正文内容" prop="content">
          <el-input v-model="saveAsForm.content" type="textarea" :rows="10" placeholder="请输入内容" />
        </el-form-item>
        <el-form-item label="变更说明" prop="edit_summary">
          <el-input
            v-model="saveAsForm.edit_summary"
            type="textarea"
            :rows="2"
            placeholder="描述本次变更（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveAsDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saveAsLoading" @click="handleSaveAs">创建新版本</el-button>
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
:deep(.el-table__row) { cursor: pointer; }
.content-preview { margin-bottom: 16px; }
.content-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}
.timeline-section { margin-top: 16px; }
.comments-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
.comment-card { margin-bottom: 8px; border: 1px solid #ebeef5; }
.gen-result-card { margin-bottom: 8px; border: 1px solid #ebeef5; }
</style>
