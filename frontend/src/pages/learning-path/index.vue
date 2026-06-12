<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import * as echarts from "echarts"
import { learningApi, type LearningPathGraph } from "@/api/learning"

const route = useRoute()
const router = useRouter()

const courseId = computed(() => Number(route.params.courseId))
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const loading = ref(false)
const pathData = ref<LearningPathGraph | null>(null)

// 学生选择
const selectedProfileId = ref<number | null>(null)
const profileOptions = ref<{ label: string; value: number }[]>([])

async function loadPath() {
  loading.value = true
  try {
    const res = await learningApi.getLearningPath(courseId.value, selectedProfileId.value ?? undefined)
    pathData.value = res.data.data
    renderChart()
  } catch {
    ElMessage.error("加载学习路径失败")
  } finally {
    loading.value = false
  }
}

async function loadProfileOptions() {
  try {
    const { profilesApi } = await import("@/api/profiles")
    const res = await profilesApi.list()
    const items = res.data.data?.items || []
    profileOptions.value = items.map((p: any) => ({
      label: `${p.student_name}（${p.student_no}）`,
      value: p.profile_id,
    }))
    // 默认选第一个
    if (profileOptions.value.length > 0 && !selectedProfileId.value) {
      selectedProfileId.value = profileOptions.value[0].value
    }
  } catch {
    // silently fail
  }
}

function renderChart() {
  if (!chart || !pathData.value) return
  const { nodes, edges } = pathData.value

  if (nodes.length === 0) {
    chart.clear()
    chart.setOption({ title: { text: "该课程暂无知识点数据" } })
    return
  }

  // 将节点和边转换为 ECharts 所需格式
  const echartsNodes = nodes.map(n => ({
    id: n.id,
    name: n.name,
    symbolSize: n.size,
    itemStyle: { color: n.color },
    label: {
      formatter: `{b}\n${(n.mastery_level * 100).toFixed(0)}%`,
      fontSize: 11,
      lineHeight: 16,
    },
    // 附加信息供 tooltip 使用
    mastery_level: n.mastery_level,
    status_label: n.status_label,
    difficulty_level: n.difficulty_level,
    estimated_hours: n.estimated_hours,
    description: n.description,
  }))

  const echartsEdges = edges.map(e => ({
    source: e.source,
    target: e.target,
    lineStyle: { color: "#c0c0c0", width: 1.5, type: "solid" as const },
    label: { show: true, formatter: e.label, fontSize: 10, color: "#999" },
  }))

  const option: echarts.EChartsOption = {
    title: {
      text: "学习路径图谱",
      subtext: `共 ${nodes.length} 个知识点 | 已掌握 ${pathData.value.summary.mastered} | 薄弱 ${pathData.value.summary.weak} | 平均掌握度 ${(pathData.value.summary.avg_mastery * 100).toFixed(0)}%`,
      left: "center",
    },
    tooltip: {
      trigger: "item",
      formatter: (params: any) => {
        const n = params.data
        if (!n || !n.id) return ""
        return `
          <div style="font-family:sans-serif;font-size:12px">
            <b>${n.name}</b><br/>
            状态：<span style="color:${n.itemStyle?.color}">●</span> ${n.status_label}<br/>
            掌握度：${(n.mastery_level * 100).toFixed(0)}%<br/>
            难度：${"★".repeat(n.difficulty_level || 1)}<br/>
            预计：${n.estimated_hours || 1}h<br/>
            ${n.description ? `<div style="color:#666;margin-top:4px">${n.description.substring(0, 60)}...</div>` : ""}
          </div>
        `
      },
    },
    legend: {
      data: ["已掌握", "学习中", "薄弱", "未学习"],
      top: 60,
      left: "center",
    },
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        draggable: true,
        symbol: "circle",
        categories: [
          { name: "已掌握", itemStyle: { color: "#67c23a" } },
          { name: "学习中", itemStyle: { color: "#e6a23c" } },
          { name: "薄弱", itemStyle: { color: "#f56c6c" } },
          { name: "未学习", itemStyle: { color: "#909399" } },
        ],
        label: { show: true, position: "bottom", fontSize: 10 },
        lineStyle: { curveness: 0.3 },
        emphasis: {
          focus: "adjacency",
          lineStyle: { width: 3 },
        },
        data: echartsNodes,
        links: echartsEdges,
        force: {
          repulsion: 400,
          gravity: 0.1,
          edgeLength: [80, 200],
          layoutAnimation: true,
        },
      },
    ],
  }

  chart.setOption(option, true)
}

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: "canvas" })
  window.addEventListener("resize", () => chart?.resize())
}

function handleProfileChange() {
  loadPath()
}

onMounted(async () => {
  initChart()
  await loadProfileOptions()
  await loadPath()
})

onUnmounted(() => {
  window.removeEventListener("resize", () => chart?.resize())
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div class="learning-path-page page-container" v-loading="loading">
    <el-page-header @back="router.push(`/courses/${courseId}`)" content="学习路径图谱" />

    <el-card class="mt-16">
      <template #header>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <span style="font-weight:600">知识点依赖图谱</span>
          <el-select
            v-model="selectedProfileId"
            placeholder="选择学生查看掌握情况"
            size="default"
            clearable
            style="width:240px"
            @change="handleProfileChange"
          >
            <el-option
              v-for="opt in profileOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <span style="color:#909399;font-size:12px" v-if="pathData">
            课程 {{ courseId }} | 平均掌握度 {{ ((pathData?.summary?.avg_mastery || 0) * 100).toFixed(0) }}%
          </span>
        </div>
      </template>

      <div class="chart-legend">
        <span class="legend-item"><span class="dot" style="background:#67c23a"></span>已掌握 (≥70%)</span>
        <span class="legend-item"><span class="dot" style="background:#e6a23c"></span>学习中 (40%~70%)</span>
        <span class="legend-item"><span class="dot" style="background:#f56c6c"></span>薄弱 (&lt;40%)</span>
        <span class="legend-item"><span class="dot" style="background:#909399"></span>未学习</span>
        <span class="legend-item"><span class="line"></span>前置依赖</span>
      </div>

      <div ref="chartRef" class="chart-container" />
    </el-card>

    <el-card class="mt-16" v-if="pathData && pathData.nodes.length > 0">
      <template #header>知识点列表</template>
      <el-table :data="pathData.nodes" size="small" stripe>
        <el-table-column prop="name" label="知识点" min-width="180" />
        <el-table-column prop="kp_code" label="编码" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status_label === '已掌握' ? 'success' : row.status_label === '薄弱' ? 'danger' : 'warning'" disable-transitions>
              {{ row.status_label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="掌握度" width="140">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.mastery_level * 100)"
              :color="row.color"
              :stroke-width="10"
              :show-text="true"
            />
          </template>
        </el-table-column>
        <el-table-column label="难度" width="120">
          <template #default="{ row }">
            {{ "★".repeat(row.difficulty_level || 1) }}{{ "☆".repeat(Math.max(0, 3 - (row.difficulty_level || 1))) }}
          </template>
        </el-table-column>
        <el-table-column prop="estimated_hours" label="预计学时(h)" width="100" />
        <el-table-column prop="last_test_date" label="最近测验" width="110" />
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.learning-path-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
.mt-16 {
  margin-top: 16px;
}
.chart-container {
  width: 100%;
  height: 520px;
  min-height: 400px;
}
.chart-legend {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
  align-items: center;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.line {
  display: inline-block;
  width: 24px;
  height: 2px;
  background: #c0c0c0;
}
</style>
