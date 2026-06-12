<template>
  <div class="courses-page">
    <div class="page-header">
      <h1 class="page-title">我的课程</h1>
      <p class="page-subtitle">管理您的课程和教学资源</p>
    </div>

    <div v-loading="loading" class="courses-content">
      <el-empty v-if="!loading && courses.length === 0" description="暂无课程数据" />

      <template v-else>
        <el-row :gutter="24" class="courses-grid">
          <el-col v-for="course in courses" :key="course.id" :xs="24" :sm="12" :md="12" :lg="8" class="course-col">
            <el-card class="course-card" shadow="hover">
              <template #header>
                <div class="card-header" :style="{ background: course.cover_color }">
                  <div class="course-info">
                    <h3 class="course-name">{{ course.name }}</h3>
                    <span class="course-code">{{ course.code }}</span>
                  </div>
                  <el-tag :type="getStatusType(course.status)" size="small" class="status-tag">
                    {{ course.status }}
                  </el-tag>
                </div>
              </template>

              <div class="card-body">
                <div class="meta-row">
                  <span class="meta-item">
                    <el-icon><User /></el-icon>
                    {{ course.teacher }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ course.semester }}
                  </span>
                </div>

                <p class="course-description">{{ course.description }}</p>

                <div class="tags-row">
                  <el-tag v-for="tag in course.tags" :key="tag" size="small" class="course-tag">
                    {{ tag }}
                  </el-tag>
                </div>

                <div class="knowledge-points-section">
                  <div class="section-label">
                    <span>知识点</span>
                    <span class="count-badge">{{ course.knowledge_point_count }}</span>
                  </div>
                  <div class="knowledge-tags">
                    <el-tooltip
                      v-for="kp in course.knowledge_points?.slice(0, 4)"
                      :key="kp.id"
                      :content="`掌握度: ${(kp.mastery_avg * 100).toFixed(0)}%`"
                      placement="top"
                    >
                      <el-tag :color="getDifficultyColor(kp.difficulty)" class="kp-tag" size="small">
                        {{ kp.name }}
                        <span class="mastery-percent">{{ (kp.mastery_avg * 100).toFixed(0) }}%</span>
                      </el-tag>
                    </el-tooltip>
                    <el-tag v-if="(course.knowledge_points?.length || 0) > 4" size="small" plain>
                      +{{ (course.knowledge_points?.length || 0) - 4 }}
                    </el-tag>
                  </div>
                </div>

                <div class="stats-row">
                  <div class="stat-item">
                    <span class="stat-value">{{ course.student_count }}</span>
                    <span class="stat-label">学生</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ course.task_count }}</span>
                    <span class="stat-label">任务</span>
                  </div>
                </div>

                <el-button type="primary" class="enter-btn" @click="enterCourse(course.id)">
                  进入课程
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div class="summary-stats">
          <div class="summary-card">
            <div class="summary-icon courses-icon">
              <el-icon :size="32"><Reading /></el-icon>
            </div>
            <div class="summary-content">
              <span class="summary-value">{{ courses.length }}</span>
              <span class="summary-label">课程总数</span>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon students-icon">
              <el-icon :size="32"><UserFilled /></el-icon>
            </div>
            <div class="summary-content">
              <span class="summary-value">{{ totalStudents }}</span>
              <span class="summary-label">学生总数</span>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon knowledge-icon">
              <el-icon :size="32"><Collection /></el-icon>
            </div>
            <div class="summary-content">
              <span class="summary-value">{{ totalKnowledgePoints }}</span>
              <span class="summary-label">知识点总数</span>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon tasks-icon">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="summary-content">
              <span class="summary-value">{{ totalTasks }}</span>
              <span class="summary-label">任务总数</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Calendar, ArrowRight, Reading, UserFilled, Collection, Document } from '@element-plus/icons-vue'
import { learningApi, type Course } from '@/api/learning'

const router = useRouter()
const loading = ref(false)
const courses = ref<Course[]>([])

const totalStudents = computed(() =>
  courses.value.reduce((sum, c) => sum + c.student_count, 0)
)

const totalKnowledgePoints = computed(() =>
  courses.value.reduce((sum, c) => sum + c.knowledge_point_count, 0)
)

const totalTasks = computed(() =>
  courses.value.reduce((sum, c) => sum + c.task_count, 0)
)

const getDifficultyColor = (difficulty: string): string => {
  const colorMap: Record<string, string> = {
    '基础': '#67c23a',
    '进阶': '#e6a23c',
    '高级': '#f56c6c'
  }
  return colorMap[difficulty] || '#909399'
}

const getStatusType = (status: string): '' | 'success' | 'warning' | 'info' => {
  const typeMap: Record<string, '' | 'success' | 'warning' | 'info'> = {
    '进行中': 'success',
    '已结束': 'info',
    '未开始': 'warning'
  }
  return typeMap[status] || 'info'
}

const enterCourse = (courseId: number) => {
  router.push(`/courses/${courseId}`)
}

const fetchCourses = async () => {
  loading.value = true
  try {
    const res = await learningApi.listCourses()
    courses.value = res.data.data || []
  } catch (error: any) {
    ElMessage.error(error?.message || '获取课程列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.courses-page {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.courses-content {
  min-height: 400px;
}

.courses-grid {
  margin-bottom: 32px;
}

.course-col {
  margin-bottom: 24px;
}

.course-card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.card-header {
  padding: 20px;
  color: white;
  position: relative;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.course-code {
  font-size: 13px;
  opacity: 0.9;
}

.status-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  border: none;
}

.card-body {
  padding: 16px;
}

.meta-row {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.course-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.course-tag {
  border-radius: 12px;
}

.knowledge-points-section {
  margin-bottom: 16px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.count-badge {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.knowledge-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.kp-tag {
  color: white;
  border: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.mastery-percent {
  font-size: 11px;
  opacity: 0.9;
}

.stats-row {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  border-top: 1px solid #f0f2f5;
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.enter-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 500;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 24px;
}

@media (max-width: 1200px) {
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-stats {
    grid-template-columns: 1fr;
  }
  
  .courses-page {
    padding: 16px;
  }
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.courses-icon {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.students-icon {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.knowledge-icon {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.tasks-icon {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.summary-content {
  display: flex;
  flex-direction: column;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
</style>
