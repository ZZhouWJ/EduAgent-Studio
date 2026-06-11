<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/stores/user"
import { Connection, ArrowRight, DataLine, Folder, CircleCheck, Collection, Cpu, List, UserFilled } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { statisticsApi } from "@/api/statistics"
import * as Icons from "@element-plus/icons-vue"

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const stats = ref<any>(null)

onMounted(async () => {
  if (userStore.token && !userStore.userInfo) {
    await userStore.getMe()
  }
  loading.value = true
  try {
    const res = await statisticsApi.overview()
    stats.value = res.data
  } catch {
    stats.value = {}
  } finally {
    loading.value = false
  }
})

function getIcon(name: string) {
  return (Icons as any)[name] || DataLine
}

const flowSteps = [
  { index: 1, title: "学生画像", desc: "建立学习者画像" },
  { index: 2, title: "智能体诊断", desc: "分析薄弱知识点" },
  { index: 3, title: "资源规划", desc: "生成学习路径" },
  { index: 4, title: "资源生成", desc: "生成学习资源" },
  { index: 5, title: "教师审核", desc: "质量把关" },
  { index: 6, title: "学习反馈", desc: "更新画像" },
  { index: 7, title: "分析看板", desc: "展示效果" }
]

const modules = [
  { name: "学生画像", desc: "查看和管理学生画像信息", icon: "UserFilled", path: "/profiles" },
  { name: "课程空间", desc: "管理课程、发布学习任务", icon: "Folder", path: "/courses" },
  { name: "智能体工作台", desc: "多智能体协作生成学习资源", icon: "Cpu", path: "/agent-workbench" },
  { name: "学习资源库", desc: "查看和管理学习资源", icon: "Collection", path: "/resources" },
  { name: "教师审核中心", desc: "审核学习资源质量", icon: "CircleCheck", path: "/reviews" },
  { name: "学习分析看板", desc: "学习效果数据分析", icon: "DataLine", path: "/analytics" }
]

const statCards = [
  { key: "course_count", label: "课程数", suffix: "门" },
  { key: "student_count", label: "学生数", suffix: "人" },
  { key: "resource_count", label: "学习资源", suffix: "份" },
  { key: "invocation_count", label: "智能体调用", suffix: "次" },
  { key: "avg_mastery", label: "平均掌握度", suffix: "%" },
  { key: "review_pass_rate", label: "审核通过率", suffix: "%" }
]

function getStatVal(key: string) {
  return stats.value?.[key] ?? 0
}

const roleLabelMap: Record<string, string> = {
  admin: "管理员",
  teacher: "教师",
  project_leader: "项目负责人",
  student_member: "学生"
}

function formatRole(role: string) {
  return roleLabelMap[role] || role
}
</script>

<template>
  <div class="dashboard page-container">
    <div class="page-header">
      <h1 class="page-title">欢迎使用智学工坊 EduAgent Studio</h1>
      <p class="page-desc">
        您好，
        <span style="font-weight: 600; color: #1e3a5f">
          {{ userStore.userInfo?.real_name || userStore.userInfo?.username || "用户" }}
        </span>
        <el-tag
          v-for="role in (userStore.userInfo?.roles || [])"
          :key="role"
          size="small"
          type="primary"
          style="margin-left: 6px"
        >
          {{ formatRole(role) }}
        </el-tag>
      </p>
    </div>

    <!-- 统计卡片 -->
    <div v-loading="loading" class="stat-grid">
      <div v-for="card in statCards" :key="card.key" class="stat-card">
        <div class="stat-value">{{ getStatVal(card.key) }}</div>
        <div class="stat-label">{{ card.label }}</div>
      </div>
    </div>

    <!-- 成本统计 -->
    <el-card v-if="!loading && stats?.total_cost != null" class="cost-card">
      <template #header>
        <span style="font-weight: 600">AI 调用成本</span>
      </template>
      <div class="cost-row">
        <span class="cost-item">
          <span class="cost-label">总成本</span>
          <span class="cost-val">{{ Number(stats.total_cost).toFixed(4) }} 元</span>
        </span>
        <span class="cost-item">
          <span class="cost-label">成功调用</span>
          <span class="cost-val success">{{ stats.success_invocation_count ?? 0 }} 次</span>
        </span>
        <span class="cost-item">
          <span class="cost-label">失败调用</span>
          <span class="cost-val danger">{{ stats.failed_invocation_count ?? 0 }} 次</span>
        </span>
      </div>
    </el-card>

    <el-card class="mb-20">
      <template #header>
        <div class="card-header">
          <el-icon><Connection /></el-icon>
          <span>个性化学习闭环流程</span>
        </div>
      </template>
      <div class="flow-steps">
        <div v-for="(step, idx) in flowSteps" :key="step.index" class="flow-step">
          <div class="step-num">{{ step.index }}</div>
          <div class="step-info">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.desc }}</div>
          </div>
          <el-icon v-if="idx < flowSteps.length - 1" class="step-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>

    <div class="module-grid">
      <div
        v-for="m in modules"
        :key="m.path"
        class="module-card"
        @click="router.push(m.path)"
      >
        <div class="module-icon">
          <el-icon :size="28"><component :is="getIcon(m.icon)" /></el-icon>
        </div>
        <div class="module-info">
          <div class="module-name">{{ m.name }}</div>
          <div class="module-desc">{{ m.desc }}</div>
        </div>
        <el-icon class="module-arrow"><ArrowRight /></el-icon>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e3a5f;
  margin-bottom: 6px;
}

.page-desc {
  font-size: 14px;
  color: #606266;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px 12px;
  text-align: center;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1e3a5f;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.cost-card {
  margin-bottom: 16px;
}

.cost-row {
  display: flex;
  gap: 32px;
  align-items: center;
}

.cost-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cost-label {
  font-size: 13px;
  color: #909399;
}

.cost-val {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.cost-val.success {
  color: #67c23a;
}

.cost-val.danger {
  color: #f56c6c;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  color: #1e3a5f;
}

.flow-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.flow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 140px;
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1e3a5f;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.step-desc {
  font-size: 11px;
  color: #909399;
}

.step-arrow {
  color: #c0c4cc;
  flex-shrink: 0;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: #ffffff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #1e3a5f;
}

.module-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #e6f0ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e3a5f;
  flex-shrink: 0;
}

.module-info {
  flex: 1;
  min-width: 0;
}

.module-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.module-desc {
  font-size: 12px;
  color: #909399;
}

.module-arrow {
  color: #c0c4cc;
  flex-shrink: 0;
  transition: color 0.2s;
}

.module-card:hover .module-arrow {
  color: #1e3a5f;
}

.mb-20 {
  margin-bottom: 20px;
}

@media (max-width: 1100px) {
  .stat-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
