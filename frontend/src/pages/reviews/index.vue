<script setup lang="ts">
import { ref, onMounted } from "vue"
import { View } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { reviewsApi } from "@/api/reviews"
import { statisticsApi } from "@/api/statistics"

const activeTab = ref("pending")
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const pendingReviews = ref<any[]>([])
const mySubmittedReviews = ref<any[]>([])
const reviewHistory = ref<any[]>([])

// Filter
const filterProjectId = ref<number | null>(null)
const filterReviewerId = ref<number | null>(null)
const projectOptions = ref<any[]>([])
const reviewerOptions = ref<any[]>([])
const filterLoading = ref(false)

// Detail
const detailDrawerVisible = ref(false)
const detailLoading = ref(false)
const currentReview = ref<any>(null)

// Complete dialog
const completeDialogVisible = ref(false)
const completeLoading = ref(false)
const issueTags = ref<any[]>([])
const issueTagsLoading = ref(false)

const completeForm = ref({
  review_status: "" as "" | "approved" | "rejected" | "revision_required",
  accuracy_score: undefined as number | undefined,
  completeness_score: undefined as number | undefined,
  logic_score: undefined as number | undefined,
  format_score: undefined as number | undefined,
  usability_score: undefined as number | undefined,
  risk_score: undefined as number | undefined,
  review_comment: "",
  issue_tag_ids: [] as number[]
})

// Stats
const reviewStats = ref<any>(null)

onMounted(async () => {
  await Promise.all([loadProjectOptions(), loadReviewStats()])
  await loadData()
})

async function loadProjectOptions() {
  try {
    const { default: projectsApi } = await import("@/api/projects")
    const res = await projectsApi.list({ page: 1, page_size: 100 })
    projectOptions.value = res.data?.items || []
  } catch {
    projectOptions.value = []
  }
}

async function loadReviewStats() {
  try {
    const res = await statisticsApi.reviews({})
    reviewStats.value = res.data
  } catch {
    reviewStats.value = null
  }
}

async function loadData() {
  loading.value = true
  try {
    if (activeTab.value === "pending") {
      const res = await reviewsApi.getPending({
        page: page.value, page_size: pageSize.value,
        project_id: filterProjectId.value || undefined,
        reviewer_id: filterReviewerId.value || undefined
      })
      pendingReviews.value = res.data?.items || []
      total.value = res.data?.total || 0
    } else if (activeTab.value === "submitted") {
      // Use the same API with different params
      const res = await reviewsApi.getPending({
        page: page.value, page_size: pageSize.value,
        project_id: filterProjectId.value || undefined,
        status: "submitted"
      })
      mySubmittedReviews.value = res.data?.items || []
      total.value = res.data?.total || 0
    } else {
      // All reviews
      const res = await reviewsApi.getPending({
        page: page.value, page_size: pageSize.value,
        project_id: filterProjectId.value || undefined,
        status: "approved,rejected,revision_required"
      })
      reviewHistory.value = res.data?.items || []
      total.value = res.data?.total || 0
    }
  } catch {
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onTabChange() {
  page.value = 1
  loadData()
}

function onPageChange(p: number) {
  page.value = p
  loadData()
}

function onPageSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadData()
}

function onFilterChange() {
  page.value = 1
  loadData()
}

async function resetFilters() {
  filterProjectId.value = null
  filterReviewerId.value = null
  page.value = 1
  await loadData()
}

async function viewReview(requestId: number) {
  detailLoading.value = true
  detailDrawerVisible.value = true
  currentReview.value = null
  try {
    const res = await reviewsApi.getById(requestId)
    currentReview.value = res.data
  } catch {
    detailDrawerVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

async function openCompleteDialog(review: any) {
  currentReview.value = review
  completeForm.value = {
    review_status: "", accuracy_score: undefined, completeness_score: undefined,
    logic_score: undefined, format_score: undefined, usability_score: undefined,
    risk_score: undefined, review_comment: "", issue_tag_ids: []
  }
  completeDialogVisible.value = true
  await loadIssueTags()
}

async function loadIssueTags() {
  if (issueTags.value.length > 0) return
  issueTagsLoading.value = true
  try {
    const res = await reviewsApi.getIssueTags()
    issueTags.value = res.data || []
  } catch {
    issueTags.value = []
  } finally {
    issueTagsLoading.value = false
  }
}

async function handleCompleteReview() {
  if (!completeForm.value.review_status) {
    ElMessage.warning("请选择审核结果")
    return
  }
  completeLoading.value = true
  try {
    const body: any = { review_status: completeForm.value.review_status }
    if (completeForm.value.accuracy_score != null) body.accuracy_score = completeForm.value.accuracy_score
    if (completeForm.value.completeness_score != null) body.completeness_score = completeForm.value.completeness_score
    if (completeForm.value.logic_score != null) body.logic_score = completeForm.value.logic_score
    if (completeForm.value.format_score != null) body.format_score = completeForm.value.format_score
    if (completeForm.value.usability_score != null) body.usability_score = completeForm.value.usability_score
    if (completeForm.value.risk_score != null) body.risk_score = completeForm.value.risk_score
    if (completeForm.value.review_comment) body.review_comment = completeForm.value.review_comment
    if (completeForm.value.issue_tag_ids.length > 0) body.issue_tag_ids = completeForm.value.issue_tag_ids

    await reviewsApi.complete(currentReview.value.request_id, body)
    ElMessage.success("审核完成")
    completeDialogVisible.value = false
    await loadData()
    await loadReviewStats()
  } catch { /* error */ } finally {
    completeLoading.value = false
  }
}

function currentTableData() {
  if (activeTab.value === "pending") return pendingReviews.value
  if (activeTab.value === "submitted") return mySubmittedReviews.value
  return reviewHistory.value
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    pending: "warning", approved: "success", rejected: "danger", revision_required: "warning",
    submitted: "warning"
  }
  return map[status] || ""
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    pending: "待审核", approved: "已通过", rejected: "已拒绝",
    revision_required: "需修订", submitted: "已提交"
  }
  return map[status] || status
}

function computeAvgScore(review: any) {
  const scores = [
    review.accuracy_score, review.completeness_score, review.logic_score,
    review.format_score, review.usability_score, review.risk_score
  ].filter(s => s != null)
  if (scores.length === 0) return "-"
  return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">审核中心</h1>
      <p class="page-desc">管理 AI 输出审核请求，进行质量评分和问题标注</p>
    </div>

    <!-- Stats cards -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-num" style="color: #fa8c16">{{ reviewStats?.pending_count || 0 }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-num" style="color: #52c41a">{{ reviewStats?.approved_count || 0 }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-num" style="color: #ff4d4f">{{ reviewStats?.rejected_count || 0 }}</div>
          <div class="stat-label">已拒绝</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-num" style="color: #1890ff">{{ reviewStats?.revision_count || 0 }}</div>
          <div class="stat-label">需修订</div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter bar -->
    <el-card style="margin-bottom: 16px" body-style="padding: 12px 16px">
      <el-row :gutter="12" align="middle">
        <el-col :span="5">
          <el-select v-model="filterProjectId" placeholder="按项目筛选" clearable size="default"
            @change="onFilterChange" style="width: 100%">
            <el-option v-for="p in projectOptions" :key="p.project_id" :label="p.project_name" :value="p.project_id" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-button @click="resetFilters" size="default">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange" class="review-tabs">
        <el-tab-pane name="pending">
          <template #label>
            <span>待审核 <el-badge :value="reviewStats?.pending_count || 0" :max="99" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="我提交的" name="submitted" />
        <el-tab-pane label="审核历史" name="history" />
      </el-tabs>

      <el-table v-loading="loading" :data="currentTableData()" stripe>
        <el-table-column prop="request_id" label="请求ID" width="80" />
        <el-table-column prop="project_name" label="项目" min-width="140" show-overflow-tooltip />
        <el-table-column prop="task_title" label="任务" min-width="180" show-overflow-tooltip />
        <el-table-column prop="output_title" label="输出" min-width="140" show-overflow-tooltip />
        <el-table-column label="版本" width="70">
          <template #default="{ row }">
            <el-tag size="small">v{{ row.version_no }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.request_status)" size="small">
              {{ getStatusLabel(row.request_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="80">
          <template #default="{ row }">
            <span>{{ computeAvgScore(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="submitter_real_name" label="申请人" width="100" />
        <el-table-column prop="reviewer_real_name" label="审核人" width="100">
          <template #default="{ row }">{{ row.reviewer_real_name || "-" }}</template>
        </el-table-column>
        <el-table-column label="申请时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewReview(row.request_id)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button v-if="row.request_status === 'pending'" type="success" size="small" link
              @click="openCompleteDialog(row)">
              完成审核
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && currentTableData().length === 0" description="暂无审核数据" />

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="page" v-model:page-size="pageSize" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
          @current-change="onPageChange" @size-change="onPageSizeChange" />
      </div>
    </el-card>

    <!-- 审核详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="审核详情" size="700px" direction="rtl" destroy-on-close>
      <div v-loading="detailLoading">
        <template v-if="currentReview">
          <el-descriptions :column="2" border size="small" style="margin-bottom: 16px">
            <el-descriptions-item label="请求ID">{{ currentReview.request_id }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(currentReview.request_status)" size="small">
                {{ getStatusLabel(currentReview.request_status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="项目">{{ currentReview.project_name }}</el-descriptions-item>
            <el-descriptions-item label="申请人">{{ currentReview.submitter_real_name }}</el-descriptions-item>
            <el-descriptions-item label="任务">{{ currentReview.task_title }}</el-descriptions-item>
            <el-descriptions-item label="审核人">{{ currentReview.reviewer_real_name || "-" }}</el-descriptions-item>
            <el-descriptions-item label="输出版本">v{{ currentReview.version_no }}</el-descriptions-item>
            <el-descriptions-item label="申请时间">{{ formatDate(currentReview.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="提交说明" :span="2">{{ currentReview.submit_note || "-" }}</el-descriptions-item>
          </el-descriptions>

          <!-- Scores -->
          <el-card shadow="never" style="margin-bottom: 16px" v-if="currentReview.request_status !== 'pending'">
            <template #header><span style="font-weight: 600">评分结果</span></template>
            <el-row :gutter="12">
              <el-col :span="8" v-for="(score, label) in {
                '准确性': currentReview.accuracy_score,
                '完整性': currentReview.completeness_score,
                '逻辑性': currentReview.logic_score,
                '规范性': currentReview.format_score,
                '可用性': currentReview.usability_score,
                '风险性': currentReview.risk_score
              }" :key="label">
                <div class="score-item">
                  <div class="score-label">{{ label }}</div>
                  <div class="score-value" :class="{ 'score-high': (score ?? 0) >= 8, 'score-low': (score ?? 0) < 6 }">
                    {{ score ?? "-" }} / 10
                  </div>
                </div>
              </el-col>
            </el-row>
            <div v-if="currentReview.review_comment" style="margin-top: 12px; color: #303133; line-height: 1.6">
              <strong>审核意见：</strong>{{ currentReview.review_comment }}
            </div>
            <!-- Issue tags -->
            <div v-if="currentReview.issue_tags && currentReview.issue_tags.length > 0" style="margin-top: 12px">
              <span style="font-weight: 600; margin-right: 8px">问题标签：</span>
              <el-tag v-for="tag in currentReview.issue_tags" :key="tag.tag_id" size="small" type="danger" style="margin-right: 4px">
                {{ tag.tag_name }}
              </el-tag>
            </div>
          </el-card>

          <!-- Output content -->
          <el-card shadow="never">
            <template #header><span style="font-weight: 600">输出内容</span></template>
            <div class="output-preview">{{ currentReview.output_content || "暂无内容" }}</div>
          </el-card>

          <div v-if="currentReview.request_status === 'pending'" style="margin-top: 20px">
            <el-button type="success" size="large" @click="openCompleteDialog(currentReview)">
              完成审核
            </el-button>
          </div>
        </template>
      </div>
    </el-drawer>

    <!-- 完成审核弹窗 -->
    <el-dialog v-model="completeDialogVisible" title="完成审核" width="640px" destroy-on-close>
      <el-form :model="completeForm" label-width="110px">
        <el-form-item label="审核结果" required>
          <el-radio-group v-model="completeForm.review_status">
            <el-radio value="approved">通过</el-radio>
            <el-radio value="rejected">拒绝</el-radio>
            <el-radio value="revision_required">需修订</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider>评分（0-10 分，选填）</el-divider>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="准确性">
              <el-input-number v-model="completeForm.accuracy_score" :min="0" :max="10" :precision="1" style="width: 100%" placeholder="0-10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="完整性">
              <el-input-number v-model="completeForm.completeness_score" :min="0" :max="10" :precision="1" style="width: 100%" placeholder="0-10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="逻辑性">
              <el-input-number v-model="completeForm.logic_score" :min="0" :max="10" :precision="1" style="width: 100%" placeholder="0-10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规范性">
              <el-input-number v-model="completeForm.format_score" :min="0" :max="10" :precision="1" style="width: 100%" placeholder="0-10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可用性">
              <el-input-number v-model="completeForm.usability_score" :min="0" :max="10" :precision="1" style="width: 100%" placeholder="0-10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风险性">
              <el-input-number v-model="completeForm.risk_score" :min="0" :max="10" :precision="1" style="width: 100%" placeholder="0-10" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="问题标签">
          <el-checkbox-group v-model="completeForm.issue_tag_ids">
            <el-checkbox v-for="tag in issueTags" :key="tag.tag_id" :value="tag.tag_id"
              style="margin-right: 10px; margin-bottom: 4px">
              {{ tag.tag_name }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="审核意见">
          <el-input v-model="completeForm.review_comment" type="textarea" :rows="3" placeholder="请输入审核意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="completeDialogVisible = false">取消</el-button>
        <el-button type="success" :loading="completeLoading" @click="handleCompleteReview">确认审核结果</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { View } from "@element-plus/icons-vue"
export default { components: { View } }
</script>

<style scoped>
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
.page-title { font-size: 20px; font-weight: 700; color: #1e3a5f; margin: 0 0 4px; }
.page-desc { font-size: 13px; color: #909399; margin: 0; }
.output-preview {
  background: #f5f7fa; border-radius: 6px; padding: 12px; font-size: 13px;
  line-height: 1.8; color: #303133; white-space: pre-wrap; word-break: break-all;
  max-height: 400px; overflow-y: auto;
}
.stat-card {
  background: #fff; border: 1px solid #e4e7ed; border-radius: 10px; padding: 16px;
  text-align: center;
}
.stat-num { font-size: 28px; font-weight: 700; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.review-tabs :deep(.el-tabs__item) { font-size: 14px; padding: 0 20px; }
.score-item {
  background: #f5f7fa; border-radius: 6px; padding: 10px; margin-bottom: 8px; text-align: center;
}
.score-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.score-value { font-size: 18px; font-weight: 700; color: #303133; }
.score-value.score-high { color: #52c41a; }
.score-value.score-low { color: #ff4d4f; }
</style>
