<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { profilesApi, type ProfileDetail } from "@/api/profiles"
import { ElMessage } from "element-plus"

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref<ProfileDetail | null>(null)

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

onMounted(() => {
  loadDetail()
})
</script>

<template>
  <div class="profile-detail page-container" v-loading="loading">
    <el-page-header @back="router.push('/profiles')" content="学生画像详情" />

    <div v-if="detail">
      <el-row :gutter="20" class="mt-20">
        <!-- 基础信息 -->
        <el-col :span="12">
          <el-card>
            <template #header>基础信息</template>
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

        <!-- AI 诊断建议 -->
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
        <!-- 薄弱知识点 -->
        <el-col :span="12">
          <el-card>
            <template #header>薄弱知识点</template>
            <div v-if="(detail.weak_points || []).length === 0">暂无薄弱知识点记录</div>
            <el-table v-else :data="detail.weak_points" size="small">
              <el-table-column prop="kp_name" label="知识点" />
              <el-table-column label="掌握度" width="180">
                <template #default="{ row }">
                  <el-progress
                    :percentage="Math.round(row.mastery * 100)"
                    :color="masteryColor(row.mastery)"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
            </el-table>
          </el-card>
        </el-col>

        <!-- 优势知识点 -->
        <el-col :span="12">
          <el-card>
            <template #header>优势知识点</template>
            <div v-if="(detail.strong_points || []).length === 0">暂无优势知识点记录</div>
            <el-table v-else :data="detail.strong_points" size="small">
              <el-table-column prop="kp_name" label="知识点" />
              <el-table-column label="掌握度" width="180">
                <template #default="{ row }">
                  <el-progress
                    :percentage="Math.round(row.mastery * 100)"
                    :color="masteryColor(row.mastery)"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20">
        <!-- 最近学习任务 -->
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

        <!-- 最近测验 -->
        <el-col :span="12">
          <el-card>
            <template #header>最近测验</template>
            <div v-if="(detail.recent_tests || []).length === 0">暂无测验记录</div>
            <el-table v-else :data="detail.recent_tests" size="small">
              <el-table-column prop="date" label="测验日期" width="120" />
              <el-table-column label="正确率" width="120">
                <template #default="{ row }">
                  <el-progress
                    :percentage="Math.round(row.accuracy * 100)"
                    :color="masteryColor(row.accuracy)"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
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
