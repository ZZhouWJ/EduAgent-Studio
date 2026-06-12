<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { profilesApi, type ProfileDetail } from "@/api/profiles"
import { ElMessage } from "element-plus"

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref<ProfileDetail | null>(null)

const editDialogVisible = ref(false)
const editForm = ref({
  learning_goal: "",
  current_level: "",
  interests: [] as string[],
  resource_preferences: [] as string[],
  weekly_hours: 0,
})
const submittingEdit = ref(false)

function masteryColor(score: number) {
  if (score >= 0.7) return "#67c23a"
  if (score >= 0.4) return "#e6a23c"
  return "#f56c6c"
}

async function loadDetail() {
  loading.value = true
  const profileId = Number(route.params.profileId)
  try {
    const res = await profilesApi.getById(profileId)
    detail.value = res.data.data
  } catch {
    ElMessage.error("加载画像详情失败")
  } finally {
    loading.value = false
  }
}

function openEditDialog() {
  if (!detail.value) return
  editForm.value = {
    learning_goal: detail.value.learning_goal || "",
    current_level: detail.value.current_level || "",
    interests: [...(detail.value.interests || [])],
    resource_preferences: [...(detail.value.resource_preferences || [])],
    weekly_hours: detail.value.weekly_hours || 0,
  }
  editDialogVisible.value = true
}

async function submitEdit() {
  if (!detail.value) return
  submittingEdit.value = true
  try {
    await profilesApi.update(detail.value.profile_id, {
      learning_goal: editForm.value.learning_goal,
      current_level: editForm.value.current_level,
      interests: editForm.value.interests,
      resource_preferences: editForm.value.resource_preferences,
      weekly_hours: editForm.value.weekly_hours,
    } as any)
    ElMessage.success("画像更新成功")
    editDialogVisible.value = false
    await loadDetail()
  } catch {
    ElMessage.error("更新失败")
  } finally {
    submittingEdit.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<template>
  <div class="profile-detail page-container" v-loading="loading">
    <el-page-header @back="router.push('/profiles')" content="学生画像详情" />

    <div v-if="detail">
      <el-row :gutter="20" class="mt-20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span>基础信息</span>
                <el-button type="primary" size="small" @click="openEditDialog">编辑画像</el-button>
              </div>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="学生姓名">{{ detail.student_name }}</el-descriptions-item>
              <el-descriptions-item label="学号">{{ detail.student_no }}</el-descriptions-item>
              <el-descriptions-item label="学习目标">{{ detail.learning_goal }}</el-descriptions-item>
              <el-descriptions-item label="当前基础">{{ detail.current_level }}</el-descriptions-item>
              <el-descriptions-item label="兴趣方向">{{ (detail.interests || []).join('、') }}</el-descriptions-item>
              <el-descriptions-item label="资源偏好">{{ (detail.resource_preferences || []).join('、') }}</el-descriptions-item>
              <el-descriptions-item label="每周学习时间">{{ detail.weekly_hours }} 小时</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>AI 诊断建议</template>
            <el-alert type="info" :closable="false" show-icon>
              <template #title>{{ detail.ai_suggestions || '暂无诊断建议' }}</template>
            </el-alert>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20">
        <el-col :span="12">
          <el-card>
            <template #header>薄弱知识点</template>
            <div v-if="(detail.weak_points || []).length === 0">暂无薄弱知识点记录</div>
            <el-table v-else :data="detail.weak_points" size="small">
              <el-table-column prop="kp_name" label="知识点" />
              <el-table-column label="掌握度" width="180">
                <template #default="{ row }">
                  <el-progress
                    :percentage="Math.round((row.mastery || row.mastery_level || 0) * 100)"
                    :color="masteryColor(row.mastery || row.mastery_level || 0)"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>优势知识点</template>
            <div v-if="(detail.strong_points || []).length === 0">暂无优势知识点记录</div>
            <el-table v-else :data="detail.strong_points" size="small">
              <el-table-column prop="kp_name" label="知识点" />
              <el-table-column label="掌握度" width="180">
                <template #default="{ row }">
                  <el-progress
                    :percentage="Math.round((row.mastery || row.mastery_level || 0) * 100)"
                    :color="masteryColor(row.mastery || row.mastery_level || 0)"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20">
        <el-col :span="12">
          <el-card>
            <template #header>最近学习任务</template>
            <div v-if="(detail.recent_tasks || []).length === 0">暂无学习任务记录</div>
            <el-table v-else :data="detail.recent_tasks" size="small">
              <el-table-column prop="title" label="任务名称" min-width="180" show-overflow-tooltip />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :type="row.status === 'completed' ? 'success' : 'warning'"
                  >
                    {{ row.status === 'completed' ? '已完成' : '进行中' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="completed_at" label="完成时间" width="120" />
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>最近测验</template>
            <div v-if="(detail.recent_tests || []).length === 0">暂无测验记录</div>
            <el-table v-else :data="detail.recent_tests" size="small">
              <el-table-column prop="date" label="测验日期" width="120" />
              <el-table-column label="正确率" width="120">
                <template #default="{ row }">
                  <el-progress
                    :percentage="Math.round((row.accuracy || 0) * 100)"
                    :color="masteryColor(row.accuracy || 0)"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

    </div>

    <el-dialog v-model="editDialogVisible" title="编辑学生画像" width="580px" destroy-on-close>
      <el-form :model="editForm" label-width="110px">
        <el-form-item label="学习目标" required>
          <el-input
            v-model="editForm.learning_goal"
            type="textarea"
            :rows="2"
            placeholder="请输入学生的学习目标，如：掌握数据库系统原理，能够独立完成数据库设计..."
          />
        </el-form-item>
        <el-form-item label="当前基础" required>
          <el-input
            v-model="editForm.current_level"
            type="textarea"
            :rows="2"
            placeholder="请描述学生的当前基础，如：已掌握SQL基本查询，多表连接和事务管理薄弱..."
          />
        </el-form-item>
        <el-form-item label="兴趣方向">
          <el-select
            v-model="editForm.interests"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入或选择兴趣方向"
            style="width:100%"
          >
            <el-option label="数据库实践" value="数据库实践" />
            <el-option label="Web开发" value="Web开发" />
            <el-option label="项目实战" value="项目实战" />
            <el-option label="数据分析" value="数据分析" />
            <el-option label="算法竞赛" value="算法竞赛" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源偏好">
          <el-select
            v-model="editForm.resource_preferences"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入或选择资源偏好"
            style="width:100%"
          >
            <el-option label="案例讲解" value="案例讲解" />
            <el-option label="图解说明" value="图解说明" />
            <el-option label="代码实操" value="代码实操" />
            <el-option label="视频教程" value="视频教程" />
            <el-option label="理论讲解" value="理论讲解" />
          </el-select>
        </el-form-item>
        <el-form-item label="每周学习时间">
          <el-slider
            v-model="editForm.weekly_hours"
            :min="1"
            :max="40"
            :step="1"
            show-stops
            :marks="{ 5: '5h', 10: '10h', 20: '20h', 40: '40h' }"
          />
          <span style="margin-left:8px;color:#606266">{{ editForm.weekly_hours }} 小时/周</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submittingEdit" @click="submitEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
.mt-20 {
  margin-top: 20px;
}
</style>
