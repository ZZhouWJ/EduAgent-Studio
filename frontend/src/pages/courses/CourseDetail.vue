<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage, ElSkeleton } from "element-plus"
import { Back } from "@element-plus/icons-vue"
import { learningApi, type Course } from "@/api/learning"

const route = useRoute()
const router = useRouter()
const courseId = Number(route.params.courseId)

const course = ref<Course | null>(null)
const loading = ref(false)

function masteryColor(score: number) {
  if (score >= 0.7) return "#67c23a"
  if (score >= 0.4) return "#e6a23c"
  return "#f56c6c"
}

function difficultyTagType(d: string) {
  return d === "基础" ? "success" : d === "进阶" ? "warning" : "danger"
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await learningApi.getCourse(courseId)
    course.value = res.data.data
  } catch {
    ElMessage.error("加载课程详情失败")
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-container" style="padding: 20px; max-width: 1100px">
    <div style="margin-bottom: 16px">
      <el-button text @click="router.push('/courses')">
        <el-icon style="margin-right: 4px"><Back /></el-icon> 返回课程列表
      </el-button>
    </div>

    <div v-if="loading">
      <el-skeleton :rows="8" animated />
    </div>

    <template v-else-if="course">
      <!-- 课程头部卡片 -->
      <el-card style="margin-bottom: 16px; overflow: hidden">
        <div :style="{
          background: `linear-gradient(135deg, ${course.cover_color} 0%, ${course.cover_color}88 100%)`,
          margin: '-20px -20px 20px -20px',
          padding: '24px 20px',
          color: 'white'
        }">
          <div style="font-size: 13px; opacity: 0.85; margin-bottom: 6px">
            {{ course.code }} · {{ course.semester }}
          </div>
          <h2 style="margin: 0 0 8px; font-size: 22px; font-weight: 700">{{ course.name }}</h2>
          <div style="font-size: 14px; opacity: 0.9">{{ course.teacher }}</div>
        </div>

        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px">
          <el-tag v-for="tag in course.tags" :key="tag" type="info">{{ tag }}</el-tag>
        </div>

        <p style="color: #606266; font-size: 14px; line-height: 1.8; margin-bottom: 16px">
          {{ course.description }}
        </p>

        <el-row :gutter="16">
          <el-col :span="8">
            <div style="text-align: center; padding: 12px; background: #f5f7fa; border-radius: 8px">
              <div style="font-size: 28px; font-weight: 700; color: #409eff">{{ course.knowledge_point_count }}</div>
              <div style="font-size: 12px; color: #909399; margin-top: 4px">知识点</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div style="text-align: center; padding: 12px; background: #f5f7fa; border-radius: 8px">
              <div style="font-size: 28px; font-weight: 700; color: #67c23a">{{ course.student_count }}</div>
              <div style="font-size: 12px; color: #909399; margin-top: 4px">学生</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div style="text-align: center; padding: 12px; background: #f5f7fa; border-radius: 8px">
              <div style="font-size: 28px; font-weight: 700; color: #e6a23c">{{ course.task_count }}</div>
              <div style="font-size: 12px; color: #909399; margin-top: 4px">学习任务</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 知识点列表 -->
      <el-card>
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight: 600">课程知识点</span>
            <div style="display:flex;gap:8px;align-items:center">
              <span style="font-size: 12px; color: #909399; font-weight: normal">
                共 {{ course.knowledge_points?.length || 0 }} 个知识点
              </span>
              <el-button
                type="primary"
                size="small"
                plain
                @click="router.push(`/learning-path/${courseId}`)"
              >
                查看学习路径图谱
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="course.knowledge_points || []"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="name" label="知识点" min-width="180">
            <template #default="{ row }">
              <span style="font-weight: 500">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="100">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="row.difficulty === 'basic' ? 'success' : row.difficulty === 'intermediate' ? 'warning' : 'danger'"
              >
                {{ row.difficulty === 'basic' ? '基础' : row.difficulty === 'intermediate' ? '进阶' : '高级' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="mastery_avg" label="班级平均掌握度" width="200">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 8px">
                <el-progress
                  :percentage="Math.round(row.mastery_avg * 100)"
                  :color="masteryColor(row.mastery_avg)"
                  :stroke-width="8"
                  style="flex: 1"
                />
                <span style="font-size: 12px; color: #909399; min-width: 36px; text-align: right">
                  {{ Math.round(row.mastery_avg * 100) }}%
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                link
                @click="router.push(`/agent-workbench?kp=${row.id}&course=${course.id}`)"
              >
                AI 生成资源
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>

    <el-empty v-else description="课程不存在" />
  </div>
</template>

<style scoped>
</style>
