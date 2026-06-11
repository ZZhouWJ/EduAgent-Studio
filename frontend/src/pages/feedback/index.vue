<script setup lang="ts">
import { ref, onMounted } from "vue"
import { feedbackApi, type LearningFeedback } from "@/api/feedback"
import { profilesApi } from "@/api/profiles"
import { ElMessage } from "element-plus"

const loading = ref(false)
const submitting = ref(false)
const feedbackList = ref<LearningFeedback[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const showSubmitDialog = ref(false)

const form = ref({
  resource_id: undefined as number | undefined,
  feedback_type: "self_report",
  content: "",
  quiz_score: undefined as number | undefined,
  self_mastery: undefined as number | undefined,
  difficulty_rating: ""
})

const feedbackTypes = [
  { label: "自评反馈", value: "self_report" },
  { label: "测验结果", value: "quiz_result" },
  { label: "学习笔记", value: "study_note" },
  { label: "问题反馈", value: "question" }
]

const difficultyOptions = [
  { label: "太简单", value: "too_easy" },
  { label: "难度适中", value: "appropriate" },
  { label: "太困难", value: "too_hard" }
]

const students = ref<Array<{ id: number; name: string; profile_id: number }>>([])

onMounted(async () => {
  await loadFeedbacks()
  try {
    const res = await profilesApi.list({ page_size: 100 })
    students.value = (res.data.data.items || []).map((p: any) => ({
      id: p.student_id,
      name: p.student_name,
      profile_id: p.profile_id
    }))
  } catch { /* ignore */ }
})

async function loadFeedbacks() {
  loading.value = true
  try {
    const res = await feedbackApi.list({ page: page.value, page_size: pageSize.value })
    feedbackList.value = res.data.data.items
    total.value = res.data.data.total
  } catch {
    ElMessage.error("加载反馈记录失败")
  } finally {
    loading.value = false
  }
}

function handlePageChange(p: number) {
  page.value = p
  loadFeedbacks()
}

function getTypeLabel(type: string) {
  return feedbackTypes.find(t => t.value === type)?.label || type
}

function getDifficultyLabel(rating: string) {
  return difficultyOptions.find(d => d.value === rating)?.label || rating
}

function masteryColor(score: number) {
  if (score >= 0.7) return "#67c23a"
  if (score >= 0.4) return "#e6a23c"
  return "#f56c6c"
}

function openSubmitDialog() {
  form.value = {
    resource_id: undefined,
    feedback_type: "self_report",
    content: "",
    quiz_score: undefined,
    self_mastery: undefined,
    difficulty_rating: ""
  }
  showSubmitDialog.value = true
}

async function handleSubmit() {
  if (!form.value.feedback_type) {
    ElMessage.warning("请选择反馈类型")
    return
  }
  if (form.value.feedback_type === "self_report" && !form.value.self_mastery) {
    ElMessage.warning("请填写自评掌握度")
    return
  }
  submitting.value = true
  try {
    await feedbackApi.submit({
      resource_id: form.value.resource_id,
      feedback_type: form.value.feedback_type,
      content: form.value.content || undefined,
      quiz_score: form.value.quiz_score,
      self_mastery: form.value.self_mastery,
      difficulty_rating: form.value.difficulty_rating || undefined
    })
    ElMessage.success("反馈提交成功")
    showSubmitDialog.value = false
    await loadFeedbacks()
  } catch {
    ElMessage.error("提交失败")
  } finally {
    submitting.value = false
  }
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}
</script>

<template>
  <div class="feedback-page page-container">
    <h1 class="page-title">学习反馈</h1>

    <el-card class="mb-16">
      <div style="display:flex; justify-content:space-between; align-items:center">
        <p style="margin:0; color:#606266; font-size:14px">
          提交学习反馈后，系统将根据反馈内容更新您的学生画像，智能体将生成个性化改进建议。
        </p>
        <el-button type="primary" @click="openSubmitDialog">提交反馈</el-button>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <span style="font-weight:600">反馈记录</span>
      </template>
      <el-table :data="feedbackList" v-loading="loading" stripe>
        <el-table-column prop="student_name" label="学生" width="100" />
        <el-table-column prop="course_name" label="课程" min-width="140" />
        <el-table-column label="反馈类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ getTypeLabel(row.feedback_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="自评掌握度" width="140">
          <template #default="{ row }">
            <el-progress
              v-if="row.self_mastery != null"
              :percentage="Math.round((row.self_mastery || 0) * 100)"
              :color="masteryColor(row.self_mastery || 0)"
              :stroke-width="8"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="测验得分" width="110">
          <template #default="{ row }">
            <span v-if="row.quiz_score != null">
              {{ Math.round((row.quiz_score || 0) * 100) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="难度评价" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.difficulty_rating" size="small" :type="row.difficulty_rating === 'appropriate' ? 'success' : row.difficulty_rating === 'too_hard' ? 'danger' : 'info'">
              {{ getDifficultyLabel(row.difficulty_rating) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="反馈内容" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.content || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      <div v-if="total > 0" class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
      <el-empty v-if="!loading && feedbackList.length === 0" description="暂无反馈记录" />
    </el-card>

    <!-- 提交反馈对话框 -->
    <el-dialog v-model="showSubmitDialog" title="提交学习反馈" width="560px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="反馈类型" required>
          <el-radio-group v-model="form.feedback_type">
            <el-radio v-for="t in feedbackTypes" :key="t.value" :value="t.value">{{ t.label }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="form.feedback_type === 'self_report'" label="自评掌握度" required>
          <div style="display:flex; align-items:center; gap:12px">
            <el-slider
              v-model="form.self_mastery"
              :min="0"
              :max="1"
              :step="0.05"
              style="width:300px"
            />
            <span style="width:60px; color:#606266">
              {{ form.self_mastery != null ? Math.round(form.self_mastery * 100) + '%' : '0%' }}
            </span>
          </div>
          <div style="color:#909399; font-size:12px; margin-top:4px">
            请根据本次学习效果，评估对相关知识点的掌握程度
          </div>
        </el-form-item>

        <el-form-item v-if="form.feedback_type === 'quiz_result'" label="测验得分" required>
          <div style="display:flex; align-items:center; gap:12px">
            <el-slider
              v-model="form.quiz_score"
              :min="0"
              :max="1"
              :step="0.05"
              style="width:300px"
            />
            <span style="width:60px; color:#606266">
              {{ form.quiz_score != null ? Math.round(form.quiz_score * 100) + '%' : '0%' }}
            </span>
          </div>
        </el-form-item>

        <el-form-item label="难度评价">
          <el-radio-group v-model="form.difficulty_rating">
            <el-radio v-for="d in difficultyOptions" :key="d.value" :value="d.value">{{ d.label }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="反馈内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入您的学习反馈、疑问或建议..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubmitDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交反馈</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.feedback-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}
.mb-16 {
  margin-bottom: 16px;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
