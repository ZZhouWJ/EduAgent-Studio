<script setup lang="ts">
import { ref, onMounted } from "vue"
import { profilesApi } from "@/api/profiles"
import { agentsApi } from "@/api/agents"
import * as echarts from "echarts"
import type { EChartsOption } from "echarts"

const loading = ref(false)

// 6 个图表的 DOM ref
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

// 统计数据
const stats = ref({
  course_count: 3,
  student_count: 12,
  resource_count: 47,
  invocation_count: 156,
  avg_mastery: 0.52,
  review_pass_rate: 0.85
})

onMounted(async () => {
  loading.value = true
  try {
    initCharts()
    await loadData()
  } finally {
    loading.value = false
  }
})

function initCharts() {
  if (masteryChartRef.value) masteryChart = echarts.init(masteryChartRef.value)
  if (weakPointsChartRef.value) weakPointsChart = echarts.init(weakPointsChartRef.value)
  if (resourceTypeChartRef.value) resourceTypeChart = echarts.init(resourceTypeChartRef.value)
  if (invocationTrendChartRef.value) invocationTrendChart = echarts.init(invocationTrendChartRef.value)
  if (reviewRateChartRef.value) reviewRateChart = echarts.init(reviewRateChartRef.value)
  if (costChartRef.value) costChart = echarts.init(costChartRef.value)
  window.addEventListener("resize", handleResize)
}

async function loadData() {
  // 1. 掌握度分布（模拟数据）
  if (masteryChart) {
    masteryChart.setOption({
      title: { text: "学生掌握度分布", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      xAxis: {
        type: "category",
        data: ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"],
        axisLabel: { fontSize: 11 }
      },
      yAxis: { type: "value", name: "学生人数", axisLabel: { fontSize: 11 } },
      series: [{
        data: [1, 3, 4, 3, 1],
        type: "bar",
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#5470c6" },
            { offset: 1, color: "#91cc75" }
          ])
        },
        barRadius: 4,
        label: { show: true, position: "top", fontSize: 11 }
      }],
      grid: { left: 50, right: 20, top: 40, bottom: 30 }
    } as EChartsOption)
  }

  // 2. 薄弱知识点 TOP10（模拟数据）
  if (weakPointsChart) {
    weakPointsChart.setOption({
      title: { text: "薄弱知识点 TOP10", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      grid: { left: 120, right: 30, top: 40, bottom: 30 },
      xAxis: { type: "value", name: "平均掌握度", axisLabel: { fontSize: 10 } },
      yAxis: {
        type: "category",
        data: [
          "事务隔离级别", "数据库范式", "索引与优化",
          "函数参数传递", "模块导入", "UML建模",
          "异常处理", "SQL多表连接", "需求分析", "视图操作"
        ].reverse(),
        axisLabel: { fontSize: 10 }
      },
      series: [{
        data: [0.20, 0.28, 0.30, 0.35, 0.38, 0.42, 0.45, 0.48, 0.52, 0.55].reverse(),
        type: "bar",
        itemStyle: { color: "#f56c6c" },
        barRadius: [0, 4, 4, 0],
        label: { show: true, position: "right", fontSize: 10, formatter: "{c}" }
      }]
    } as EChartsOption)
  }

  // 3. 资源类型分布（模拟数据）
  if (resourceTypeChart) {
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
        data: [
          { value: 18, name: "知识点讲义", itemStyle: { color: "#5470c6" } },
          { value: 8, name: "PPT大纲", itemStyle: { color: "#91cc75" } },
          { value: 12, name: "习题与答案", itemStyle: { color: "#fac858" } },
          { value: 5, name: "案例材料", itemStyle: { color: "#ee6666" } },
          { value: 3, name: "复习计划", itemStyle: { color: "#73c0de" } },
          { value: 1, name: "阶段测验", itemStyle: { color: "#3ba272" } }
        ]
      }]
    } as EChartsOption)
  }

  // 4. 智能体调用趋势（模拟数据 - 近14天）
  if (invocationTrendChart) {
    const dates = Array.from({ length: 14 }, (_, i) => {
      const d = new Date()
      d.setDate(d.getDate() - 13 + i)
      return `${d.getMonth() + 1}/${d.getDate()}`
    })
    invocationTrendChart.setOption({
      title: { text: "智能体调用趋势（近14天）", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
      tooltip: { trigger: "axis" },
      legend: { bottom: 5, textStyle: { fontSize: 11 }, data: ["调用次数", "Token消耗"] },
      grid: { left: 50, right: 20, top: 40, bottom: 50 },
      xAxis: { type: "category", data: dates, axisLabel: { fontSize: 10 } },
      yAxis: [
        { type: "value", name: "调用次数", axisLabel: { fontSize: 10 } },
        { type: "value", name: "Token(K)", axisLabel: { fontSize: 10 } }
      ],
      series: [
        {
          name: "调用次数",
          type: "line",
          smooth: true,
          itemStyle: { color: "#5470c6" },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(84,112,198,0.3)" },
            { offset: 1, color: "rgba(84,112,198,0.05)" }
          ]) },
          data: [8, 12, 11, 15, 18, 14, 16, 20, 19, 22, 18, 25, 23, 28]
        },
        {
          name: "Token消耗",
          type: "line",
          smooth: true,
          yAxisIndex: 1,
          itemStyle: { color: "#67c23a" },
          data: [3.2, 4.8, 4.4, 6.0, 7.2, 5.6, 6.4, 8.0, 7.6, 8.8, 7.2, 10.0, 9.2, 11.2]
        }
      ]
    } as EChartsOption)
  }

  // 5. 审核通过率（模拟数据）
  if (reviewRateChart) {
    reviewRateChart.setOption({
      title: { text: "各课程审核通过率", left: "center", textStyle: { fontSize: 14, fontWeight: 600 } },
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      grid: { left: 100, right: 30, top: 40, bottom: 30 },
      xAxis: { type: "value", max: 100, name: "通过率%", axisLabel: { fontSize: 10, formatter: "{value}%" } },
      yAxis: {
        type: "category",
        data: ["软件工程实践", "Python程序设计", "数据库系统原理"].reverse(),
        axisLabel: { fontSize: 11 }
      },
      series: [{
        type: "bar",
        data: [0.80, 0.88, 0.85].reverse().map((v, i) => ({
          value: Math.round(v * 100),
          itemStyle: {
            color: ["#5470c6", "#91cc75", "#fac858"][i]
          }
        })),
        barRadius: [0, 4, 4, 0],
        label: { show: true, position: "right", fontSize: 11, formatter: "{c}%" }
      }]
    } as EChartsOption)
  }

  // 6. 成本分布（模拟数据）
  if (costChart) {
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
        data: [
          { value: 45, name: "资源生成", itemStyle: { color: "#5470c6" } },
          { value: 25, name: "学习诊断", itemStyle: { color: "#91cc75" } },
          { value: 15, name: "资源规划", itemStyle: { color: "#fac858" } },
          { value: 10, name: "评测反馈", itemStyle: { color: "#ee6666" } },
          { value: 5, name: "审核建议", itemStyle: { color: "#73c0de" } }
        ]
      }]
    } as EChartsOption)
  }
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
</script>

<template>
  <div class="analytics-page page-container" v-loading="loading">
    <h1 class="page-title">学习分析看板</h1>

    <!-- 统计卡片 -->
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

    <!-- 图表区域 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <!-- 掌握度分布 -->
      <el-col :span="8">
        <el-card>
          <div ref="masteryChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <!-- 薄弱知识点 -->
      <el-col :span="8">
        <el-card>
          <div ref="weakPointsChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <!-- 资源类型分布 -->
      <el-col :span="8">
        <el-card>
          <div ref="resourceTypeChartRef" style="height: 280px" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <!-- 调用趋势 -->
      <el-col :span="12">
        <el-card>
          <div ref="invocationTrendChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <!-- 审核通过率 -->
      <el-col :span="6">
        <el-card>
          <div ref="reviewRateChartRef" style="height: 280px" />
        </el-card>
      </el-col>
      <!-- 成本分布 -->
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
.stat-cards {
  margin-bottom: 0;
}
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
.stat-label {
  font-size: 12px;
  color: #909399;
}
</style>
