<script setup lang="ts">
import { ref, onMounted } from "vue"
import {
  getStatisticsOverviewApi,
  getProjectStatisticsApi,
  getModelCallStatisticsApi,
  getCostStatisticsApi,
  getReviewStatisticsApi,
  getMemberContributionsApi,
  getRecentActivitiesApi
} from "@/common/apis/statistics"
import type {
  StatisticsOverview,
  ProjectStats,
  ModelCallStats,
  CostStats,
  ReviewStats,
  MemberContribution,
  RecentActivity
} from "@/common/apis/statistics/type"

/** 兼容后端数组返回 */
function asArray<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[]
  if (Array.isArray((data as Record<string, unknown>)?.items)) return ((data as Record<string, unknown>).items) as T[]
  return []
}

const overviewLoading = ref(false)
const overview = ref<Partial<StatisticsOverview>>({})

const projectStatsLoading = ref(false)
const projectStats = ref<ProjectStats[]>([])

const modelStatsLoading = ref(false)
const modelStats = ref<ModelCallStats[]>([])

const costStatsLoading = ref(false)
const costStats = ref<Partial<CostStats>>({})

const reviewStatsLoading = ref(false)
const reviewStats = ref<Partial<ReviewStats>>({})

const memberLoading = ref(false)
const memberStats = ref<MemberContribution[]>([])

const activityLoading = ref(false)
const activities = ref<RecentActivity[]>([])

async function fetchOverview() {
  overviewLoading.value = true
  try {
    const res = await getStatisticsOverviewApi()
    overview.value = res.data || {}
  } catch { /* shown by interceptor */ }
  finally { overviewLoading.value = false }
}

async function fetchProjectStats() {
  projectStatsLoading.value = true
  try {
    const res = await getProjectStatisticsApi()
    projectStats.value = asArray<ProjectStats>(res.data)
  } catch { /* shown by interceptor */ }
  finally { projectStatsLoading.value = false }
}

async function fetchModelStats() {
  modelStatsLoading.value = true
  try {
    const res = await getModelCallStatisticsApi()
    modelStats.value = asArray<ModelCallStats>(res.data)
  } catch { /* shown by interceptor */ }
  finally { modelStatsLoading.value = false }
}

async function fetchCostStats() {
  costStatsLoading.value = true
  try {
    const res = await getCostStatisticsApi()
    costStats.value = res.data || {}
  } catch { /* shown by interceptor */ }
  finally { costStatsLoading.value = false }
}

async function fetchReviewStats() {
  reviewStatsLoading.value = true
  try {
    const res = await getReviewStatisticsApi()
    reviewStats.value = res.data || {}
  } catch { /* shown by interceptor */ }
  finally { reviewStatsLoading.value = false }
}

async function fetchMemberStats() {
  memberLoading.value = true
  try {
    const res = await getMemberContributionsApi()
    memberStats.value = asArray<MemberContribution>(res.data)
  } catch { /* shown by interceptor */ }
  finally { memberLoading.value = false }
}

async function fetchActivities() {
  activityLoading.value = true
  try {
    const res = await getRecentActivitiesApi()
    activities.value = asArray<RecentActivity>(res.data)
  } catch { /* shown by interceptor */ }
  finally { activityLoading.value = false }
}

function getActionTypeLabel(type: string) {
  const m: Record<string, string> = {
    "task:create": "创建任务",
    "task:generate": "AI 生成",
    "output:edit": "编辑输出",
    "output:save_as": "另存版本",
    "output:submit_review": "提交审核",
    "review:complete": "审核完成",
    "output:adopt": "采用成果",
    "merge:execute": "分支合并",
    "project:create": "创建项目",
    "project:archive": "归档项目",
    "login": "登录",
    "logout": "退出登录"
  }
  return m[type] || type
}

onMounted(() => {
  fetchOverview()
  fetchProjectStats()
  fetchModelStats()
  fetchCostStats()
  fetchReviewStats()
  fetchMemberStats()
  fetchActivities()
})
</script>

<template>
  <div class="statistics-page">
    <div class="page-header">
      <h2 class="page-title">统计看板</h2>
    </div>

    <!-- Overview Cards -->
    <div v-loading="overviewLoading" class="overview-grid">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">项目总数</div>
        <div class="stat-value">{{ overview.project_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">进行中项目</div>
        <div class="stat-value">{{ overview.active_project_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">任务总数</div>
        <div class="stat-value">{{ overview.task_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">待审核数</div>
        <div class="stat-value">{{ overview.pending_review_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">模型调用次数</div>
        <div class="stat-value">{{ overview.invocation_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">成功调用次数</div>
        <div class="stat-value">{{ overview.success_invocation_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">成果总数</div>
        <div class="stat-value">{{ overview.artifact_count ?? 0 }}</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-label">累计成本 (CNY)</div>
        <div class="stat-value">¥{{ (overview.total_cost ?? 0).toFixed(4) }}</div>
      </el-card>
    </div>

    <!-- Project Stats + Model Call Stats -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :xs="24" :sm="24" :md="12">
        <el-card v-loading="projectStatsLoading">
          <template #header>
            <div style="font-weight: 600">项目统计</div>
          </template>
          <el-table :data="projectStats" stripe size="small" style="width: 100%">
            <el-table-column prop="project_name" label="项目名称" min-width="140" show-overflow-tooltip />
            <el-table-column prop="member_count" label="成员" width="70" align="center" />
            <el-table-column prop="task_count" label="任务" width="70" align="center" />
            <el-table-column prop="output_count" label="输出" width="70" align="center" />
            <el-table-column prop="approved_output_count" label="已通过" width="80" align="center" />
            <el-table-column prop="total_cost" label="成本" width="90" align="right">
              <template #default="{ row }">¥{{ (row.total_cost || 0).toFixed(4) }}</template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无项目统计数据" />
            </template>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12">
        <el-card v-loading="modelStatsLoading">
          <template #header>
            <div style="font-weight: 600">模型调用统计</div>
          </template>
          <el-table :data="modelStats" stripe size="small" style="width: 100%">
            <el-table-column label="模型" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ row.display_name || row.model_name }}</template>
            </el-table-column>
            <el-table-column prop="call_count" label="调用次数" width="90" align="center" />
            <el-table-column prop="success_count" label="成功数" width="80" align="center" />
            <el-table-column prop="total_input_tokens" label="输入 Tokens" width="110" align="right">
              <template #default="{ row }">{{ (row.total_input_tokens || 0).toLocaleString() }}</template>
            </el-table-column>
            <el-table-column prop="total_output_tokens" label="输出 Tokens" width="110" align="right">
              <template #default="{ row }">{{ (row.total_output_tokens || 0).toLocaleString() }}</template>
            </el-table-column>
            <el-table-column prop="total_cost" label="成本" width="90" align="right">
              <template #default="{ row }">¥{{ (row.total_cost || 0).toFixed(4) }}</template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无模型调用数据" />
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Cost Stats + Review Stats -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :xs="24" :sm="24" :md="12">
        <el-card v-loading="costStatsLoading">
          <template #header>
            <div style="font-weight: 600">成本统计</div>
          </template>
          <div class="cost-grid">
            <div class="cost-item">
              <div class="cost-label">总成本 (CNY)</div>
              <div class="cost-value">¥{{ (costStats.total_cost ?? 0).toFixed(4) }}</div>
            </div>
            <div class="cost-item">
              <div class="cost-label">输入成本</div>
              <div class="cost-value">¥{{ (costStats.input_cost ?? 0).toFixed(4) }}</div>
            </div>
            <div class="cost-item">
              <div class="cost-label">输出成本</div>
              <div class="cost-value">¥{{ (costStats.output_cost ?? 0).toFixed(4) }}</div>
            </div>
            <div class="cost-item">
              <div class="cost-label">总 Tokens</div>
              <div class="cost-value">{{ (costStats.total_tokens ?? 0).toLocaleString() }}</div>
            </div>
          </div>
          <div v-if="costStats.cost_by_model && costStats.cost_by_model.length > 0" style="margin-top: 12px">
            <div class="sub-title">按模型成本明细</div>
            <el-table :data="costStats.cost_by_model" size="small" style="width: 100%">
              <el-table-column prop="model_name" label="模型" />
              <el-table-column prop="total_cost" label="成本" align="right">
                <template #default="{ row }">¥{{ (row.total_cost || 0).toFixed(4) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12">
        <el-card v-loading="reviewStatsLoading">
          <template #header>
            <div style="font-weight: 600">审核质量统计</div>
          </template>
          <div class="review-stats-grid">
            <div class="review-item">
              <div class="review-label">审核总数</div>
              <div class="review-value">{{ reviewStats.review_count ?? 0 }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">通过数</div>
              <div class="review-value" style="color: #67c23a">{{ reviewStats.approved_count ?? 0 }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">拒绝数</div>
              <div class="review-value" style="color: #f56c6c">{{ reviewStats.rejected_count ?? 0 }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">需修改数</div>
              <div class="review-value" style="color: #e6a23c">{{ reviewStats.revision_required_count ?? 0 }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">平均准确度</div>
              <div class="review-value">{{ (reviewStats.avg_accuracy_score ?? 0).toFixed(1) }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">平均完整度</div>
              <div class="review-value">{{ (reviewStats.avg_completeness_score ?? 0).toFixed(1) }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">平均逻辑性</div>
              <div class="review-value">{{ (reviewStats.avg_logic_score ?? 0).toFixed(1) }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">平均可用性</div>
              <div class="review-value">{{ (reviewStats.avg_usability_score ?? 0).toFixed(1) }}</div>
            </div>
          </div>
          <div v-if="reviewStats.top_issue_tags && reviewStats.top_issue_tags.length > 0" style="margin-top: 12px">
            <div class="sub-title">高频问题标签</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px">
              <el-tag v-for="tag in reviewStats.top_issue_tags" :key="tag.tag_name" size="small" type="info">
                {{ tag.tag_name }} ({{ tag.tag_count }})
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Member Contributions + Recent Activities -->
    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="12">
        <el-card v-loading="memberLoading">
          <template #header>
            <div style="font-weight: 600">成员贡献排行</div>
          </template>
          <el-table :data="memberStats" stripe size="small" style="width: 100%">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column label="成员" min-width="100">
              <template #default="{ row }">{{ row.real_name || `用户 #${row.user_id}` }}</template>
            </el-table-column>
            <el-table-column prop="task_created_count" label="创建任务" width="90" align="center" />
            <el-table-column prop="output_created_count" label="创建输出" width="90" align="center" />
            <el-table-column prop="review_count" label="审核数" width="80" align="center" />
            <el-table-column prop="artifact_adopted_count" label="采用成果" width="90" align="center" />
            <template #empty>
              <el-empty description="暂无成员贡献数据" />
            </template>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12">
        <el-card v-loading="activityLoading">
          <template #header>
            <div style="font-weight: 600">最近操作动态</div>
          </template>
          <div class="activity-list">
            <div v-if="activities.length === 0" style="padding: 20px; text-align: center; color: #909399">
              暂无操作记录
            </div>
            <div v-for="item in activities" :key="item.log_id" class="activity-item">
              <div class="activity-icon">
                <el-tag size="small" type="info">{{ getActionTypeLabel(item.action_type) }}</el-tag>
              </div>
              <div class="activity-content">
                <div class="activity-desc">{{ item.action_desc || "-" }}</div>
                <div class="activity-meta">
                  {{ item.real_name || `用户 #${item.user_id}` }}
                </div>
              </div>
              <div class="activity-time">
                {{ item.created_at ? new Date(item.created_at).toLocaleString("zh-CN") : "-" }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style lang="scss" scoped>
.statistics-page {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}
.page-header { margin-bottom: 16px; }
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}
.stat-card {
  text-align: center;
  .stat-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
  .stat-value { font-size: 24px; font-weight: 700; color: #1e3a5f; }
}
.cost-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 12px;
}
.cost-item {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
  .cost-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
  .cost-value { font-size: 16px; font-weight: 600; color: #303133; }
}
.review-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 12px;
}
.review-item {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  text-align: center;
  .review-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
  .review-value { font-size: 18px; font-weight: 700; color: #303133; }
}
.sub-title {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}
.activity-list {
  max-height: 400px;
  overflow-y: auto;
}
.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  &:last-child { border-bottom: none; }
}
.activity-icon { flex-shrink: 0; padding-top: 2px; }
.activity-content {
  flex: 1;
  min-width: 0;
  .activity-desc { font-size: 13px; color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .activity-meta { font-size: 12px; color: #909399; margin-top: 2px; }
}
.activity-time {
  flex-shrink: 0;
  font-size: 12px;
  color: #c0c4cc;
  white-space: nowrap;
}
</style>
