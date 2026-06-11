<script setup lang="ts">
import { ref, onMounted } from "vue"
import { statisticsApi } from "@/api/statistics"

const loading = ref(false)
const overview = ref<any>(null)
const projectStats = ref<any[]>([])
const modelCalls = ref<any[]>([])
const costStats = ref<any>(null)
const reviewStats = ref<any>(null)
const memberContribs = ref<any[]>([])
const recentActivities = ref<any[]>([])

const sectionLoading = ref({
  overview: false,
  projects: false,
  modelCalls: false,
  costs: false,
  reviews: false,
  members: false,
  activities: false
})

onMounted(async () => {
  loading.value = true
  const promises = [
    loadOverview(),
    loadProjectStats(),
    loadModelCalls(),
    loadCostStats(),
    loadReviewStats(),
    loadMemberContribs(),
    loadRecentActivities()
  ]
  await Promise.allSettled(promises)
  loading.value = false
})

async function loadOverview() {
  sectionLoading.value.overview = true
  try {
    const res = await statisticsApi.overview()
    overview.value = res.data
  } catch {
    overview.value = {}
  } finally {
    sectionLoading.value.overview = false
  }
}

async function loadProjectStats() {
  sectionLoading.value.projects = true
  try {
    const res = await statisticsApi.projects()
    projectStats.value = res.data || []
  } catch {
    projectStats.value = []
  } finally {
    sectionLoading.value.projects = false
  }
}

async function loadModelCalls() {
  sectionLoading.value.modelCalls = true
  try {
    const res = await statisticsApi.modelCalls()
    modelCalls.value = res.data || []
  } catch {
    modelCalls.value = []
  } finally {
    sectionLoading.value.modelCalls = false
  }
}

async function loadCostStats() {
  sectionLoading.value.costs = true
  try {
    const res = await statisticsApi.costs()
    costStats.value = res.data
  } catch {
    costStats.value = null
  } finally {
    sectionLoading.value.costs = false
  }
}

async function loadReviewStats() {
  sectionLoading.value.reviews = true
  try {
    const res = await statisticsApi.reviews()
    reviewStats.value = res.data
  } catch {
    reviewStats.value = null
  } finally {
    sectionLoading.value.reviews = false
  }
}

async function loadMemberContribs() {
  sectionLoading.value.members = true
  try {
    const res = await statisticsApi.memberContributions()
    memberContribs.value = res.data || []
  } catch {
    memberContribs.value = []
  } finally {
    sectionLoading.value.members = false
  }
}

async function loadRecentActivities() {
  sectionLoading.value.activities = true
  try {
    const res = await statisticsApi.recentActivities({ limit: 20 })
    recentActivities.value = res.data || []
  } catch {
    recentActivities.value = []
  } finally {
    sectionLoading.value.activities = false
  }
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function getSeverityType(severity: string) {
  const map: Record<string, string> = {
    low: "info",
    medium: "warning",
    high: "danger"
  }
  return map[severity] || ""
}
</script>

<template>
  <div class="page-container" style="padding: 20px">
    <div class="page-header" style="margin-bottom: 16px">
      <h1 class="page-title">学习分析看板</h1>
      <p class="page-desc">学习效果数据分析，覆盖掌握度、薄弱点、资源分布、调用趋势、审核率等</p>
    </div>

    <div v-loading="loading">
      <!-- 概览数字卡片 -->
      <el-row :gutter="12" class="stat-cards" style="margin-bottom: 16px">
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value primary">{{ overview?.project_count ?? 0 }}</div>
            <div class="stat-label">课程数</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value primary">{{ overview?.active_project_count ?? 0 }}</div>
            <div class="stat-label">活跃课程</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value warning">{{ overview?.task_count ?? 0 }}</div>
            <div class="stat-label">任务总数</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value danger">{{ overview?.pending_review_count ?? 0 }}</div>
            <div class="stat-label">待审核</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value success">{{ overview?.invocation_count ?? 0 }}</div>
            <div class="stat-label">总调用次数</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value">{{ (overview?.total_cost ?? 0).toFixed(4) }}</div>
            <div class="stat-label">总成本(元)</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="12" style="margin-bottom: 16px">
        <!-- AI 调用概览 -->
        <el-col :span="8">
          <el-card>
            <template #header>
              <span style="font-weight: 600">智能体调用概览</span>
            </template>
            <el-descriptions :column="1" border size="small" v-if="overview">
              <el-descriptions-item label="总调用次数">
                <span style="font-size: 20px; font-weight: 700; color: #409eff">{{ overview?.invocation_count ?? 0 }}</span>
                <span style="color: #909399; font-size: 12px; margin-left: 4px">次</span>
              </el-descriptions-item>
              <el-descriptions-item label="成功调用">{{ overview?.success_invocation_count ?? 0 }} 次</el-descriptions-item>
              <el-descriptions-item label="失败调用">{{ overview?.failed_invocation_count ?? 0 }} 次</el-descriptions-item>
              <el-descriptions-item label="总 Token">
                <span style="font-weight: 600">{{ overview?.total_tokens ?? 0 }}</span>
                <span style="color: #909399; font-size: 12px; margin-left: 4px">Tokens</span>
              </el-descriptions-item>
            </el-descriptions>
            <el-empty v-else description="暂无数据" />
          </el-card>
        </el-col>

        <!-- 成本统计 -->
        <el-col :span="8">
          <el-card>
            <template #header>
              <span style="font-weight: 600">成本统计</span>
            </template>
            <div v-if="costStats" class="cost-grid">
              <div class="cost-item">
                <div class="cost-val">{{ Number(costStats.total_cost || 0).toFixed(4) }}</div>
                <div class="cost-label">总成本 ({{ costStats.currency || "CNY" }})</div>
              </div>
              <div class="cost-item">
                <div class="cost-val">{{ costStats.total_tokens ?? 0 }}</div>
                <div class="cost-label">Token 消耗</div>
              </div>
            </div>
            <el-table
              v-if="costStats?.cost_by_model?.length"
              :data="costStats.cost_by_model"
              size="small"
              style="margin-top: 12px"
            >
              <el-table-column prop="model_name" label="模型" />
              <el-table-column prop="total_cost" label="成本">
                <template #default="{ row }">
                  {{ Number(row.total_cost || 0).toFixed(4) }} 元
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无成本数据" />
          </el-card>
        </el-col>

        <!-- 模型调用统计 -->
        <el-col :span="8">
          <el-card>
            <template #header>
              <span style="font-weight: 600">模型调用统计</span>
            </template>
            <el-table
              v-if="modelCalls.length > 0"
              :data="modelCalls"
              size="small"
              max-height="200"
            >
              <el-table-column prop="model_name" label="模型" min-width="100" />
              <el-table-column prop="call_count" label="调用次数" width="80" />
              <el-table-column prop="success_rate" label="成功率" width="80">
                <template #default="{ row }">
                  {{ (row.success_rate || 0).toFixed(1) }}%
                </template>
              </el-table-column>
              <el-table-column prop="total_tokens" label="Token" width="80" />
            </el-table>
            <el-empty v-else description="暂无模型调用数据" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 项目统计 -->
      <el-card v-loading="sectionLoading.projects" style="margin-bottom: 16px">
        <template #header>
          <span style="font-weight: 600">课程统计</span>
        </template>
        <el-table :data="projectStats" stripe size="small" v-if="projectStats.length > 0">
          <el-table-column prop="project_name" label="课程名称" min-width="180" />
          <el-table-column prop="member_count" label="成员" width="70" />
          <el-table-column prop="task_count" label="任务" width="70" />
          <el-table-column prop="output_count" label="输出" width="70" />
          <el-table-column prop="approved_output_count" label="通过输出" width="90" />
          <el-table-column prop="artifact_count" label="成果" width="70" />
          <el-table-column prop="invocation_count" label="调用" width="70" />
          <el-table-column prop="total_cost" label="成本">
            <template #default="{ row }">
              {{ Number(row.total_cost || 0).toFixed(4) }} 元
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无课程统计数据" />
      </el-card>

      <!-- 审核质量统计 -->
      <el-card v-loading="sectionLoading.reviews" style="margin-bottom: 16px">
        <template #header>
          <span style="font-weight: 600">审核质量统计</span>
        </template>
        <div v-if="reviewStats" class="review-stats-grid">
          <div class="review-stat-item">
            <div class="stat-value primary">{{ reviewStats.review_count ?? 0 }}</div>
            <div class="stat-label">审核总数</div>
          </div>
          <div class="review-stat-item">
            <div class="stat-value success">{{ reviewStats.approved_count ?? 0 }}</div>
            <div class="stat-label">通过</div>
          </div>
          <div class="review-stat-item">
            <div class="stat-value danger">{{ reviewStats.rejected_count ?? 0 }}</div>
            <div class="stat-label">拒绝</div>
          </div>
          <div class="review-stat-item">
            <div class="stat-value warning">{{ reviewStats.revision_required_count ?? 0 }}</div>
            <div class="stat-label">需修订</div>
          </div>
          <div class="review-stat-item">
            <div class="stat-value">{{ (reviewStats.avg_accuracy_score || 0).toFixed(1) }}</div>
            <div class="stat-label">平均准确性</div>
          </div>
          <div class="review-stat-item">
            <div class="stat-value">{{ (reviewStats.avg_completeness_score || 0).toFixed(1) }}</div>
            <div class="stat-label">平均完整性</div>
          </div>
        </div>

        <!-- 问题标签分布 -->
        <div v-if="reviewStats?.top_issue_tags?.length" style="margin-top: 16px">
          <div style="font-weight: 600; margin-bottom: 8px; font-size: 13px">高频问题标签</div>
          <el-tag
            v-for="tag in reviewStats.top_issue_tags"
            :key="tag.tag_name"
            :type="getSeverityType(tag.severity)"
            style="margin-right: 8px; margin-bottom: 4px"
          >
            {{ tag.tag_name }} ({{ tag.count }})
          </el-tag>
        </div>
        <el-empty v-else description="暂无审核统计数据" />
      </el-card>

      <el-row :gutter="12">
        <!-- 成员贡献统计 -->
        <el-col :span="12">
          <el-card v-loading="sectionLoading.members">
            <template #header>
              <span style="font-weight: 600">成员学习统计</span>
            </template>
            <el-table :data="memberContribs" stripe size="small">
              <el-table-column prop="real_name" label="成员" width="100" />
              <el-table-column prop="project_count" label="参与课程" width="80" />
              <el-table-column prop="task_created_count" label="创建任务" width="80" />
              <el-table-column prop="output_created_count" label="创建输出" width="80" />
              <el-table-column prop="review_count" label="审核次数" width="80" />
              <el-table-column prop="artifact_adopted_count" label="资源采用" width="80" />
              <el-table-column prop="invocation_count" label="AI 调用" width="80" />
            </el-table>
            <el-empty v-if="memberContribs.length === 0" description="暂无成员学习数据" />
          </el-card>
        </el-col>

        <!-- 最近操作动态 -->
        <el-col :span="12">
          <el-card v-loading="sectionLoading.activities">
            <template #header>
              <span style="font-weight: 600">学习动态</span>
            </template>
            <div v-if="recentActivities.length > 0" class="activity-list">
              <div v-for="act in recentActivities" :key="act.log_id" class="activity-item">
                <div class="activity-dot"></div>
                <div class="activity-content">
                  <div class="activity-desc">{{ act.action_desc }}</div>
                  <div class="activity-meta">
                    <span>{{ act.real_name }}</span>
                    <span>{{ formatDate(act.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无学习动态" />
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 4px;
}

.page-desc {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.stat-cards .el-col {
  margin-bottom: 0;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 18px 12px;
  text-align: center;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-value.primary { color: #1e3a5f; }
.stat-value.success { color: #67c23a; }
.stat-value.warning { color: #e6a23c; }
.stat-value.danger { color: #f56c6c; }

.stat-label {
  font-size: 12px;
  color: #909399;
}

.cost-grid {
  display: flex;
  gap: 32px;
}

.cost-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cost-val {
  font-size: 22px;
  font-weight: 700;
  color: #1e3a5f;
}

.cost-label {
  font-size: 12px;
  color: #909399;
}

.review-stats-grid {
  display: flex;
  gap: 0;
  flex-wrap: wrap;
}

.review-stat-item {
  flex: 1;
  min-width: 100px;
  text-align: center;
  padding: 8px 4px;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.activity-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1e3a5f;
  margin-top: 5px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-desc {
  font-size: 13px;
  color: #303133;
  line-height: 1.5;
}

.activity-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
