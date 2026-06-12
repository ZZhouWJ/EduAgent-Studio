<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { ElMessage } from "element-plus"
import { statisticsApi } from "@/api/statistics"
import * as echarts from "echarts"
import type { EChartsOption } from "echarts"

const loading = ref(false)

const masteryChartRef = ref<HTMLDivElement>()
const weakPointsChartRef = ref<HTMLDivElement>()
const resourceTypeChartRef = ref<HTMLDivElement>()
const invocationTrendChartRef = ref<HTMLDivElement>()
const reviewRateChartRef = ref<HTMLDivElement>()
const costChartRef = ref<HTMLDivElement>()

let masteryChart: echarts.ECharts | null = null
let weakPointsChart: echarts.ECharts | null = null
let resourceTypeChart: echarts.ECharts | null = null
let invocationTrendChart: echarts.ECharts | null = null
let reviewRateChart: echarts.ECharts | null = null
let costChart: echarts.ECharts | null = null

const stats = ref({
  course_count: 0,
  student_count: 0,
  resource_count: 0,
  invocation_count: 0,
  avg_mastery: 0,
  review_pass_rate: 0,
})

let masteryDistData: Array<{ range: string; count: number }> = []
let weakPointsData: Array<{ name: string; mastery: number }> = []
let resourceTypeData: Array<{ name: string; value: number }> = []
let invocationTrendData: Array<{ date: string; calls: number; tokens: number }> = []
let reviewRateData: Array<{ name: string; rate: number }> = []
let costData: Array<{ name: string; value: number }> = []

onMounted(async () => {
  loading.value = true
  try {
    initCharts()
    await loadData()
  } catch (e) {
    console.error("Analytics load failed:", e)
  } finally {
    loading.value = false
  }
  window.addEventListener("resize", handleResize)
})

onUnmounted(() => {
  window.removeEventListener("resize", handleResize)
  masteryChart?.dispose()
  weakPointsChart?.dispose()
  resourceTypeChart?.dispose()
  invocationTrendChart?.dispose()
  reviewRateChart?.dispose()
  costChart?.dispose()
})

function initCharts() {
  if (masteryChartRef.value) masteryChart = echarts.init(masteryChartRef.value)
  if (weakPointsChartRef.value) weakPointsChart = echarts.init(weakPointsChartRef.value)
  if (resourceTypeChartRef.value) resourceTypeChart = echarts.init(resourceTypeChartRef.value)
  if (invocationTrendChartRef.value) invocationTrendChart = echarts.init(invocationTrendChartRef.value)
  if (reviewRateChartRef.value) reviewRateChart = echarts.init(reviewRateChartRef.value)
  if (costChartRef.value) costChart = echarts.init(costChartRef.value)
}

async function loadData() {
  const [overviewRes, modelCallsRes, costsRes, reviewsRes, learningRes] = await Promise.allSettled([
    statisticsApi.overview(),
    statisticsApi.modelCalls(),
    statisticsApi.costs(),
    statisticsApi.reviews(),
    statisticsApi.learningOverview(),
  ])

  if (learningRes.status === "fulfilled" && learningRes.value?.data) {
    const d = learningRes.value.data.data
    stats.value = {
      course_count: d.course_count,
      student_count: d.student_count,
      resource_count: d.resource_count,
      invocation_count: d.invocation_count,
      avg_mastery: d.avg_mastery,
      review_pass_rate: d.review_pass_rate,
    }
  } else if (overviewRes.status === "fulfilled" && overviewRes.value?.data) {
    const d = overviewRes.value.data.data
    stats.value = {
      course_count: 0,
      student_count: 0,
      resource_count: d.artifact_count || 0,
      invocation_count: d.invocation_count || 0,
      avg_mastery: 0,
      review_pass_rate: 0,
    }
  }

  const defaultDates = generateLast14Days().map(date => ({ date, calls: 0, tokens: 0 }))

  const [masteryRes, weakPointsRes, resourceTypeRes, invocationTrendRes, reviewRateRes, costDistRes] =
    await Promise.allSettled([
      statisticsApi.masteryDistribution(),
      statisticsApi.weakKnowledgePoints(10),
      statisticsApi.resourceTypeDistribution(),
      statisticsApi.invocationTrend(14),
      statisticsApi.reviewRateByCourse(),
      statisticsApi.costDistribution(),
    ])

  if (masteryRes.status === "fulfilled" && masteryRes.value?.data) {
    masteryDistData = masteryRes.value.data.data || []
  }

  if (weakPointsRes.status === "fulfilled" && weakPointsRes.value?.data) {
    weakPointsData = (weakPointsRes.value.data.data || []).map((d: any) => ({
      name: d.kp_name,
      mastery: d.avg_mastery,
    }))
  }

  if (resourceTypeRes.status === "fulfilled" && resourceTypeRes.value?.data) {
    resourceTypeData = (resourceTypeRes.value.data.data || []).map((d: any) => ({
      name: d.type_name,
      value: d.count,
    }))
  }

  if (invocationTrendRes.status === "fulfilled" && invocationTrendRes.value?.data) {
    invocationTrendData = (invocationTrendRes.value.data.data || []).map((d: any) => ({
      date: d.date.slice(5),
      calls: d.invocation_count,
      tokens: d.total_tokens,
    }))
  } else {
    invocationTrendData = defaultDates
  }

  if (reviewRateRes.status === "fulfilled" && reviewRateRes.value?.data) {
    reviewRateData = (reviewRateRes.value.data.data || []).map((d: any) => ({
      name: d.course_name,
      rate: Math.round((d.pass_rate || 0) * 100),
    }))
  }

  if (costDistRes.status === "fulfilled" && costDistRes.value?.data) {
    costData = (costDistRes.value.data.data || []).map((d: any) => ({
      name: d.agent_name,
      value: d.tokens,
    }))
  }

  if (learningRes.status !== "fulfilled" || !learningRes.value?.data) {
    if (modelCallsRes.status === "fulfilled" && modelCallsRes.value?.data && !invocationTrendData.length) {
      invocationTrendData = defaultDates
    }

    if (costsRes.status === "fulfilled" && costsRes.value?.data && !costData.length) {
      costData = (costsRes.value.data.data.cost_by_model || []).map((m: any) => ({
        name: m.model_name,
        value: Math.round(m.cost * 1000000),
      }))
    }

    if (reviewsRes.status === "fulfilled" && reviewsRes.value?.data && !reviewRateData.length) {
      const r = reviewsRes.value.data.data
      reviewRateData = [
        { name: "准确性", rate: Math.round((r.avg_accuracy_score || 0) * 100) },
        { name: "完整性", rate: Math.round((r.avg_completeness_score || 0) * 100) },
        { name: "逻辑性", rate: Math.round((r.avg_logic_score || 0) * 100) },
        { name: "规范性", rate: Math.round((r.avg_format_score || 0) * 100) },
        { name: "可用性", rate: Math.round((r.avg_usability_score || 0) * 100) },
      ]
    }
  }

  renderMasteryChart()
  renderWeakPointsChart()
  renderResourceTypeChart()
  renderInvocationTrendChart()
  renderReviewRateChart()
  renderCostChart()
}

function renderMasteryChart() {
  if (!masteryChart) return
  masteryChart.setOption({
    title: { text: "学生掌握度分布", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: {
      type: "category",
      data: masteryDistData.map(d => d.range),
      axisLabel: { fontSize: 11 },
    },
    yAxis: { type: "value", name: "学生人数", axisLabel: { fontSize: 11 } },
    series: [{
      data: masteryDistData.map(d => d.count),
      type: "bar",
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "#5470c6" },
          { offset: 1, color: "#91cc75" },
        ]),
      },
      barRadius: 4,
      label: { show: true, position: "top", fontSize: 11 },
    }],
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
  } as EChartsOption)
}

function renderWeakPointsChart() {
  if (!weakPointsChart) return
  const sorted = [...weakPointsData].sort((a, b) => a.mastery - b.mastery).slice(0, 10)
  weakPointsChart.setOption({
    title: { text: "薄弱知识点 TOP10", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 120, right: 30, top: 40, bottom: 30 },
    xAxis: { type: "value", name: "平均掌握度", axisLabel: { fontSize: 10 } },
    yAxis: {
      type: "category",
      data: sorted.map(d => d.name).reverse(),
      axisLabel: { fontSize: 10 },
    },
    series: [{
      data: sorted.map(d => d.mastery).reverse(),
      type: "bar",
      itemStyle: { color: "#f56c6c" },
      barRadius: [0, 4, 4, 0],
      label: { show: true, position: "right", fontSize: 10, formatter: "{c}" },
    }],
  } as EChartsOption)
}

function renderResourceTypeChart() {
  if (!resourceTypeChart) return
  const colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272"]
  resourceTypeChart.setOption({
    title: { text: "学习资源类型分布", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 5, textStyle: { fontSize: 11 } },
    series: [{
      type: "pie",
      radius: ["35%", "65%"],
      center: ["50%", "45%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 2 },
      label: { fontSize: 11 },
      data: resourceTypeData.map((d, i) => ({
        value: d.value,
        name: d.name,
        itemStyle: { color: colors[i % colors.length] },
      })),
    }],
  } as EChartsOption)
}

function renderInvocationTrendChart() {
  if (!invocationTrendChart) return
  invocationTrendChart.setOption({
    title: { text: "智能体调用趋势（近14天）", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: "axis" },
    legend: { bottom: 5, textStyle: { fontSize: 11 }, data: ["调用次数", "Token消耗"] },
    grid: { left: 50, right: 20, top: 40, bottom: 50 },
    xAxis: { type: "category", data: invocationTrendData.map(d => d.date), axisLabel: { fontSize: 10 } },
    yAxis: [
      { type: "value", name: "调用次数", axisLabel: { fontSize: 10 } },
      { type: "value", name: "Token(K)", axisLabel: { fontSize: 10 } },
    ],
    series: [
      {
        name: "调用次数",
        type: "line",
        smooth: true,
        itemStyle: { color: "#5470c6" },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(84,112,198,0.3)" },
          { offset: 1, color: "rgba(84,112,198,0.05)" },
        ]) },
        data: invocationTrendData.map(d => d.calls),
      },
      {
        name: "Token消耗",
        type: "line",
        smooth: true,
        yAxisIndex: 1,
        itemStyle: { color: "#67c23a" },
        data: invocationTrendData.map(d => d.tokens),
      },
    ],
  } as EChartsOption)
}

function renderReviewRateChart() {
  if (!reviewRateChart) return
  const colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272"]
  reviewRateChart.setOption({
    title: { text: "各课程审核通过率", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b}: {c}%" },
    grid: { left: 100, right: 20, top: 40, bottom: 30 },
    xAxis: { type: "value", max: 100, name: "通过率%", axisLabel: { fontSize: 10, formatter: "{value}%" } },
    yAxis: {
      type: "category",
      data: reviewRateData.map(d => d.name).reverse(),
      axisLabel: { fontSize: 10 },
    },
    series: [{
      type: "bar",
      data: reviewRateData.map((d, i) => ({
        value: d.rate,
        itemStyle: { color: colors[i % colors.length], borderRadius: [0, 4, 4, 0] },
      })).reverse(),
      barRadius: [0, 4, 4, 0],
      label: { show: true, position: "right", fontSize: 11, formatter: "{c}%" },
    }],
  } as EChartsOption)
}

function renderCostChart() {
  if (!costChart) return
  const colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"]
  costChart.setOption({
    title: { text: "Token 消耗占比", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 5, textStyle: { fontSize: 11 } },
    series: [{
      type: "pie",
      radius: ["40%", "70%"],
      center: ["50%", "45%"],
      roseType: "area",
      itemStyle: { borderRadius: 5 },
      label: { fontSize: 11 },
      data: costData.map((d, i) => ({
        value: d.value,
        name: d.name,
        itemStyle: { color: colors[i % colors.length] },
      })),
    }],
  } as EChartsOption)
}

function handleResize() {
  masteryChart?.resize()
  weakPointsChart?.resize()
  resourceTypeChart?.resize()
  invocationTrendChart?.resize()
  reviewRateChart?.resize()
  costChart?.resize()
}

function masteryColor(score: number) {
  if (score >= 0.7) return "#67c23a"
  if (score >= 0.4) return "#e6a23c"
  return "#f56c6c"
}

function generateLast14Days(): string[] {
  return Array.from({ length: 14 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - 13 + i)
    return `${d.getMonth() + 1}/${d.getDate()}`
  })
}
</script>

<template>
  <div class="analytics-page page-container" v-loading="loading">
    <h1 class="page-title">学习分析看板</h1>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.course_count }}</div>
          <div class="stat-label">课程数</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.student_count }}</div>
          <div class="stat-label">学生数</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.resource_count }}</div>
          <div class="stat-label">学习资源</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.invocation_count }}</div>
          <div class="stat-label">智能体调用</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-value" :style="{ color: masteryColor(stats.avg_mastery) }">
            {{ (stats.avg_mastery * 100).toFixed(0) }}%
          </div>
          <div class="stat-label">平均掌握度</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-value" style="color: #67c23a">
            {{ (stats.review_pass_rate * 100).toFixed(0) }}%
          </div>
          <div class="stat-label">审核通过率</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="8">
        <el-card>
          <div ref="masteryChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div ref="weakPointsChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div ref="resourceTypeChartRef" style="height: 280px" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card>
          <div ref="invocationTrendChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div ref="reviewRateChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div ref="costChartRef" style="height: 280px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.analytics-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}
.stat-cards { margin-bottom: 0; }
.stat-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 20px 12px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 6px;
}
.stat-label { font-size: 12px; color: #909399; }
</style>
