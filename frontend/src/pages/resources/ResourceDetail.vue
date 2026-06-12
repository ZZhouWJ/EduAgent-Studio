<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { resourcesApi } from "@/api/resources"

const route = useRoute()
const router = useRouter()
const loading = ref(false)

const resource = ref<any>(null)
const activeTab = ref("content")
const reviewDialogVisible = ref(false)
const reviewForm = ref({
  review_status: "approved" as "approved" | "rejected" | "revision_required",
  review_comment: ""
})
const submittingReview = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const id = Number(route.params.resourceId)
    const res = await resourcesApi.getById(id)
    if (res?.data) {
      resource.value = res.data
    } else {
      ElMessage.error("资源不存在")
      router.push("/resources")
    }
  } catch {
    ElMessage.error("加载资源详情失败")
  } finally {
    loading.value = false
  }
})

function getStatusType(status: string) {
  const map: Record<string, string> = {
    draft: "info",
    pending_review: "warning",
    approved: "success",
    rejected: "danger",
    archived: "info"
  }
  return map[status] || ""
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    draft: "草稿",
    pending_review: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
    archived: "已归档"
  }
  return map[status] || status
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    lecture: "知识点讲义",
    ppt: "PPT大纲",
    quiz: "习题与答案",
    case: "案例材料",
    review: "复习计划",
    test: "阶段测验"
  }
  return map[type] || type
}

function renderMarkdown(content: string) {
  return content
    .replace(/^# /gm, '<h2 style="margin-top:16px;font-size:18px;font-weight:600;color:#303133;border-bottom:1px solid #e4e7ed;padding-bottom:8px">')
    .replace(/^## /gm, '<h3 style="margin-top:14px;font-size:15px;font-weight:600;color:#303133">')
    .replace(/^### /gm, '<h4 style="margin-top:12px;font-size:14px;font-weight:600;color:#606266">')
    .replace(/\n\n/g, '<br>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code style="background:#f5f5f5;padding:2px 6px;border-radius:4px;font-size:13px;font-family:monospace;color:#e6a23c">$1</code>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre style="background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.6"><code>$2</code></pre>')
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function openReviewDialog() {
  reviewForm.value = { review_status: "approved", review_comment: "" }
  reviewDialogVisible.value = true
}

async function submitReview() {
  submittingReview.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    resource.value.status = reviewForm.value.review_status
    resource.value.reviewer_comment = reviewForm.value.review_comment
    ElMessage.success("审核完成")
    reviewDialogVisible.value = false
  } catch {
    ElMessage.error("提交失败")
  } finally {
    submittingReview.value = false
  }
}
</script>

<template>
  <div class="resource-detail page-container" v-loading="loading">
    <el-page-header @back="router.push('/resources')" content="资源详情" />

    <div v-if="resource" style="margin-top: 20px">
      <!-- 基础信息 -->
      <el-card style="margin-bottom: 16px">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="资源标题" :span="2">{{ resource.resource_title }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(resource.status)" size="small">
              {{ getStatusLabel(resource.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="资源类型">{{ getTypeLabel(resource.resource_type) }}</el-descriptions-item>
          <el-descriptions-item label="难度">{{ resource.difficulty }}</el-descriptions-item>
          <el-descriptions-item label="所属课程">{{ resource.course_name }}</el-descriptions-item>
          <el-descriptions-item label="关联知识点">
            <el-tag
              v-for="kp in resource.target_kp_names"
              :key="kp"
              size="small"
              style="margin-right:4px"
            >
              {{ kp }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="生成模型">{{ resource.generation_model }}</el-descriptions-item>
          <el-descriptions-item label="生成智能体">{{ resource.generation_agent }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(resource.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 操作按钮 -->
        <div style="margin-top: 12px; display: flex; gap: 8px">
          <el-button
            v-if="resource.status === 'pending_review'"
            type="primary"
            size="small"
            @click="openReviewDialog"
          >
            教师审核
          </el-button>
          <el-button
            type="success"
            size="small"
            @click="() => {
              const content = resource.content
              const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = (resource.resource_title || '学习资源') + '.md'
              a.click()
              URL.revokeObjectURL(url)
            }"
          >
            导出 Markdown
          </el-button>
        </div>
      </el-card>

      <!-- 资源正文 -->
      <el-card>
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:600">资源正文</span>
            <el-tag size="small" type="info">v{{ resource.version }}</el-tag>
          </div>
        </template>
        <div
          class="resource-content"
          v-html="renderMarkdown(resource.content || '')"
        />
      </el-card>
    </div>

    <!-- 审核对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="教师审核" width="480px" destroy-on-close>
      <el-form :model="reviewForm" label-width="90px">
        <el-form-item label="审核结果" required>
          <el-radio-group v-model="reviewForm.review_status">
            <el-radio value="approved">通过</el-radio>
            <el-radio value="rejected">拒绝</el-radio>
            <el-radio value="revision_required">需修订</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewForm.review_comment"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submittingReview" @click="submitReview">确认审核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.resource-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}
.resource-content {
  font-size: 14px;
  line-height: 2;
  color: #303133;
  padding: 8px 4px;
}
.resource-content :deep(h2) {
  margin-top: 20px;
  font-size: 18px;
}
.resource-content :deep(h3) {
  margin-top: 16px;
  font-size: 15px;
}
.resource-content :deep(pre) {
  margin: 12px 0;
}
</style>
