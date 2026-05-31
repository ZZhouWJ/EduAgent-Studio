<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  getReviewDetailApi,
  completeReviewApi,
  getIssueTagsApi
} from "@/common/apis/reviews"
import type { ReviewDetail, IssueTag, CompleteReviewRequestData } from "@/common/apis/reviews/type"

const route = useRoute()
const router = useRouter()
const requestId = Number(route.params.requestId)

const loading = ref(false)
const detail = ref<Partial<ReviewDetail>>({})

// Complete review dialog
const completeDialogVisible = ref(false)
const completeLoading = ref(false)
const completeFormRef = ref()
const issueTags = ref<IssueTag[]>([])

const completeForm = ref<CompleteReviewRequestData>({
  review_status: "approved",
  accuracy_score: undefined,
  completeness_score: undefined,
  logic_score: undefined,
  format_score: undefined,
  usability_score: undefined,
  risk_score: undefined,
  review_comment: "",
  issue_tag_ids: []
})

const scoreValidator = (_rule: unknown, value: number | undefined, callback: (err?: Error) => void) => {
  if (value === undefined || value === null) {
    callback()
    return
  }
  if (value < 0 || value > 10) {
    callback(new Error("分数必须在 0 到 10 之间"))
  } else {
    callback()
  }
}

const completeRules = {
  review_status: [{ required: true, message: "请选择审核结论", trigger: "change" }],
  accuracy_score: [{ validator: scoreValidator, trigger: "blur" }],
  completeness_score: [{ validator: scoreValidator, trigger: "blur" }],
  logic_score: [{ validator: scoreValidator, trigger: "blur" }],
  format_score: [{ validator: scoreValidator, trigger: "blur" }],
  usability_score: [{ validator: scoreValidator, trigger: "blur" }],
  risk_score: [{ validator: scoreValidator, trigger: "blur" }],
  review_comment: [{ required: true, message: "请填写审核意见", trigger: "blur" }]
}

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getReviewDetailApi(requestId)
    detail.value = res.data
  } catch { /* shown by interceptor */ }
  finally { loading.value = false }
}

async function openCompleteDialog() {
  completeDialogVisible.value = true
  completeForm.value = {
    review_status: "approved",
    accuracy_score: undefined,
    completeness_score: undefined,
    logic_score: undefined,
    format_score: undefined,
    usability_score: undefined,
    risk_score: undefined,
    review_comment: "",
    issue_tag_ids: []
  }
  try {
    const res = await getIssueTagsApi()
    issueTags.value = res.data || []
  } catch { issueTags.value = [] }
}

async function handleComplete() {
  if (!completeFormRef.value) return
  try {
    const valid = await completeFormRef.value.validate()
    if (!valid) return
    completeLoading.value = true
    await completeReviewApi(requestId, completeForm.value)
    ElMessage.success("审核已完成")
    completeDialogVisible.value = false
    await fetchDetail()
  } catch { /* shown by interceptor */ }
  finally { completeLoading.value = false }
}

function getStatusType(status: string) {
  const m: Record<string, string> = {
    pending: "warning", approved: "success",
    rejected: "danger", revision_required: "info"
  }
  return m[status] || "info"
}

function getStatusLabel(status: string) {
  const m: Record<string, string> = {
    pending: "待审核", approved: "已通过",
    rejected: "已拒绝", revision_required: "需修改"
  }
  return m[status] || status
}

onMounted(fetchDetail)
</script>

<template>
  <div class="review-detail-page">
    <div class="page-header">
      <el-button text @click="router.push('/reviews')">
        <el-icon style="margin-right: 4px"><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h2 class="page-title">审核详情</h2>
    </div>

    <div v-loading="loading">
      <el-card style="margin-bottom: 16px">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="审核编号">{{ detail.request_id }}</el-descriptions-item>
          <el-descriptions-item label="审核状态">
            <el-tag size="small" :type="getStatusType(detail.request_status || '')">
              {{ getStatusLabel(detail.request_status || '') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="项目名称" :span="2">
            {{ detail.project_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="任务标题">
            {{ detail.task_title || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="输出标题">
            {{ detail.output_title || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="版本号">
            v{{ detail.version_no || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="提交人">
            {{ detail.submitter_real_name || detail.submitter_username || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="审核人">
            {{ detail.reviewer_real_name || detail.reviewer_username || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="提交说明" :span="2">
            {{ detail.submit_note || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ detail.created_at ? new Date(detail.created_at).toLocaleString("zh-CN") : "-" }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card style="margin-bottom: 16px" title="输出内容">
        <template #header>
          <div style="font-weight: 600">输出内容</div>
        </template>
        <div v-if="detail.content" class="content-box">{{ detail.content }}</div>
        <el-empty v-else description="暂无输出内容" />
      </el-card>

      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center">
            <span style="font-weight: 600">审核操作</span>
            <el-button
              v-if="detail.request_status === 'pending'"
              type="primary"
              @click="openCompleteDialog"
            >
              完成审核
            </el-button>
            <el-tag v-else type="info">审核已完成</el-tag>
          </div>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="审核结论">
            <el-tag :type="getStatusType(detail.request_status || '')" size="small">
              {{ getStatusLabel(detail.request_status || '') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ detail.created_at ? new Date(detail.created_at).toLocaleString("zh-CN") : "-" }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- Complete Review Dialog -->
    <el-dialog
      v-model="completeDialogVisible"
      title="完成审核"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="completeFormRef"
        :model="completeForm"
        :rules="completeRules"
        label-width="110px"
      >
        <el-form-item label="审核结论" prop="review_status">
          <el-radio-group v-model="completeForm.review_status">
            <el-radio value="approved">通过</el-radio>
            <el-radio value="rejected">拒绝</el-radio>
            <el-radio value="revision_required">需修改</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider content-position="left">评分（可选，0-10 分）</el-divider>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="准确度" prop="accuracy_score">
              <el-input-number
                v-model="completeForm.accuracy_score"
                :min="0"
                :max="10"
                :precision="1"
                style="width: 100%"
                placeholder="0-10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="完整度" prop="completeness_score">
              <el-input-number
                v-model="completeForm.completeness_score"
                :min="0"
                :max="10"
                :precision="1"
                style="width: 100%"
                placeholder="0-10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="逻辑性" prop="logic_score">
              <el-input-number
                v-model="completeForm.logic_score"
                :min="0"
                :max="10"
                :precision="1"
                style="width: 100%"
                placeholder="0-10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="格式规范" prop="format_score">
              <el-input-number
                v-model="completeForm.format_score"
                :min="0"
                :max="10"
                :precision="1"
                style="width: 100%"
                placeholder="0-10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可用性" prop="usability_score">
              <el-input-number
                v-model="completeForm.usability_score"
                :min="0"
                :max="10"
                :precision="1"
                style="width: 100%"
                placeholder="0-10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风险等级" prop="risk_score">
              <el-input-number
                v-model="completeForm.risk_score"
                :min="0"
                :max="10"
                :precision="1"
                style="width: 100%"
                placeholder="0-10"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="问题标签">
          <el-select
            v-model="completeForm.issue_tag_ids"
            multiple
            placeholder="选择问题标签（可选）"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="tag in issueTags"
              :key="tag.tag_id"
              :label="tag.tag_name"
              :value="tag.tag_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="审核意见" prop="review_comment">
          <el-input
            v-model="completeForm.review_comment"
            type="textarea"
            :rows="3"
            placeholder="请填写审核意见（必填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="completeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="completeLoading" @click="handleComplete">提交审核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.review-detail-page {
  padding: 20px;
  max-width: 1100px;
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
.content-box {
  white-space: pre-wrap;
  font-size: 14px;
  color: #303133;
  line-height: 1.8;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}
</style>
