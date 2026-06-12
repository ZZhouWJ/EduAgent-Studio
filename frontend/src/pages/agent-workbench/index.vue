<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { agentsApi, type WorkflowResult } from "@/api/agents"
import { profilesApi } from "@/api/profiles"
import { learningApi } from "@/api/learning"
import { marked } from "marked"
import { ElMessage } from "element-plus"
import * as Icons from "@element-plus/icons-vue"

marked.setOptions({ breaks: true, gfm: true })

const generating = ref(false)
const result = ref<WorkflowResult | null>(null)
const activeTab = ref("diagnosis")
const saveDialogVisible = ref(false)
const saveTitle = ref("")
const savedResource = ref<any>(null)

const executionLog = ref<Array<{
  step: string
  status: "pending" | "running" | "success" | "failed"
  message: string
  timestamp: string
}>>([])

const form = ref({
  student_id: undefined as number | undefined,
  course_id: undefined as number | undefined,
  knowledge_point_ids: [] as number[],
  resource_type: "lecture",
  difficulty: "intermediate"
})

const students = ref<Array<{ id: number; name: string; profile_id: number }>>([])
const courses = ref<Array<{ id: number; name: string }>>([])
const knowledgePoints = ref<Array<{ id: number; name: string }>>([])

const courseKnowledgePointsMap = ref<Record<number, Array<{ id: number; name: string }>>>({})

const route = useRoute()

onMounted(async () => {
  try {
    const [agentsRes, profilesRes, coursesRes] = await Promise.all([
      agentsApi.getAgents(),
      profilesApi.list({ page_size: 100 }),
      learningApi.listCourses()
    ])
    students.value = (profilesRes.data.data.items || []).map((p: any) => ({
      id: p.student_id,
      name: p.student_name,
      profile_id: p.profile_id
    }))
    courses.value = coursesRes.data.data || []

    const queryCourse = route.query.course
    const queryKp = route.query.kp
    if (queryCourse) {
      const courseId = Number(queryCourse)
      if (!isNaN(courseId)) {
        form.value.course_id = courseId
        await onCourseChange()
        if (queryKp) {
          const kpId = Number(queryKp)
          if (!isNaN(kpId)) {
            form.value.knowledge_point_ids = [kpId]
          }
        }
      }
    }
  } catch {
    // ignore
  }
})

function onCourseChange() {
  form.value.knowledge_point_ids = []
  const courseId = form.value.course_id
  if (!courseId) {
    knowledgePoints.value = []
    return
  }
  if (courseKnowledgePointsMap.value[courseId]) {
    knowledgePoints.value = courseKnowledgePointsMap.value[courseId]
    return
  }
  learningApi.getCourse(courseId).then(res => {
    const courseData = res.data.data
    const kps: Array<{ id: number; name: string }> = (courseData.knowledge_points || []).map((kp: any) => ({
      id: kp.id,
      name: kp.name
    }))
    courseKnowledgePointsMap.value[courseId] = kps
    knowledgePoints.value = kps
  }).catch(() => {
    knowledgePoints.value = []
  })
}

const agentSteps = computed(() => [
  { id: "diagnosis", name: "学习诊断", desc: "分析薄弱知识点" },
  { id: "planning", name: "资源规划", desc: "生成学习路径" },
  { id: "generation", name: "资源生成", desc: "生成学习资源" },
  { id: "assessment", name: "评测反馈", desc: "分析学习效果" },
  { id: "review", name: "审核建议", desc: "质量检查" }
])

function getStepStatus(stepId: string) {
  return executionLog.value.find(l => l.step === stepId)?.status || "pending"
}

function getStepMessage(stepId: string) {
  return executionLog.value.find(l => l.step === stepId)?.message || ""
}

function getStepTimestamp(stepId: string) {
  return executionLog.value.find(l => l.step === stepId)?.timestamp || ""
}

const resourceTypes = [
  { value: "lecture", label: "知识点讲义" },
  { value: "ppt", label: "PPT大纲" },
  { value: "quiz", label: "习题与答案" },
  { value: "case", label: "案例材料" },
  { value: "review", label: "复习计划" },
  { value: "test", label: "阶段测验" }
]

const difficultyOptions = [
  { value: "basic", label: "基础" },
  { value: "intermediate", label: "进阶" },
  { value: "advanced", label: "高级" }
]

async function handleGenerate() {
  if (!form.value.student_id || !form.value.course_id || form.value.knowledge_point_ids.length === 0) {
    ElMessage.warning("请完整填写配置信息")
    return
  }
  generating.value = true
  result.value = null
  savedResource.value = null
  executionLog.value = []
  activeTab.value = "diagnosis"

  const steps = ["diagnosis", "planning", "generation", "assessment", "review"]
  executionLog.value = steps.map(s => ({
    step: s,
    status: "pending" as const,
    message: "",
    timestamp: ""
  }))

  try {
    const response = await fetch("/api/agents/generate/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (localStorage.getItem("token") || "")
      },
      body: JSON.stringify({
        student_id: form.value.student_id,
        course_id: form.value.course_id,
        knowledge_point_ids: form.value.knowledge_point_ids,
        resource_type: form.value.resource_type,
        difficulty: form.value.difficulty
      })
    })

    const reader = response.body?.getReader()
    if (!reader) throw new Error("Stream not available")

    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n")
      buffer = lines.pop() || ""

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === "error") {
              ElMessage.error("执行错误: " + event.message)
              break
            }
            if (event.type === "done") break

            const nodeToStep: Record<string, string> = {
              diagnosis: "diagnosis",
              planning: "planning",
              generation: "generation",
              assessment: "assessment",
              teacher_review: "review",
            }
            const stepId = nodeToStep[event.node] || event.step

            if (stepId && stepId !== "completed") {
              const logEntry = executionLog.value.find(l => l.step === stepId)
              if (logEntry && logEntry.status === "pending") {
                logEntry.status = "running"
                logEntry.message = "执行中..."
                logEntry.timestamp = new Date().toLocaleTimeString("zh-CN")
              }
            }

            const hasFlags = [
              { flag: "has_diagnosis", step: "diagnosis" },
              { flag: "has_plan", step: "planning" },
              { flag: "has_resource", step: "generation" },
              { flag: "has_assessment", step: "assessment" },
              { flag: "has_review", step: "review" },
            ]
            for (const { flag, step } of hasFlags) {
              if (event[flag]) {
                const logEntry = executionLog.value.find(l => l.step === step)
                if (logEntry) {
                  logEntry.status = "success"
                  logEntry.message = "完成"
                  logEntry.timestamp = new Date().toLocaleTimeString("zh-CN")
                }
              }
            }
          } catch {
            // ignore parse errors
          }
        }
      }
    }

    const fullRes = await agentsApi.generate({
      student_id: form.value.student_id,
      course_id: form.value.course_id,
      knowledge_point_ids: form.value.knowledge_point_ids,
      resource_type: form.value.resource_type,
      difficulty: form.value.difficulty
    })
    result.value = fullRes.data.data
    activeTab.value = "resource"

    const reviewEntry = executionLog.value.find(l => l.step === "review")
    if (reviewEntry && reviewEntry.status !== "success") {
      reviewEntry.status = "success"
      reviewEntry.message = `质量评分: ${result.value?.teacher_review_suggestion?.quality_score}/10`
      reviewEntry.timestamp = new Date().toLocaleTimeString("zh-CN")
    }

    ElMessage.success("个性化学习资源生成完成")
  } catch (e: any) {
    ElMessage.error("生成失败: " + (e?.message || "未知错误"))
    executionLog.value.forEach(l => {
      if (l.status === "pending" || l.status === "running") l.status = "failed"
    })
  } finally {
    generating.value = false
  }
}

function handleSave() {
  saveTitle.value = result.value?.resource?.title || "学习资源"
  saveDialogVisible.value = true
}

async function confirmSave() {
  if (!saveTitle.value) {
    ElMessage.warning("请输入资源标题")
    return
  }
  try {
    const res = await agentsApi.saveResource({
      result: result.value!,
      title: saveTitle.value,
      course_id: form.value.course_id!
    })
    savedResource.value = res.data.data
    ElMessage.success("资源已保存到学习资源库")
    saveDialogVisible.value = false
  } catch {
    ElMessage.error("保存失败")
  }
}

function downloadResource() {
  if (!savedResource.value?.storage_url) {
    ElMessage.warning("请先保存资源")
    return
  }
  const url = savedResource.value.storage_url
  window.open(url, "_blank")
}

function renderMarkdown(content: string): string {
  if (!content) return ""
  try {
    return marked.parse(content) as string
  } catch {
    return `<pre>${content}</pre>`
  }
}

function accuracyPercent(assessment: WorkflowResult["assessment"]) {
  const rate = assessment?.test_results?.accuracy_rate || 0.7
  return Math.round(rate * 100)
}
</script>

<template>
  <div class="agent-workbench page-container">
    <h1 class="page-title">智能体工作台</h1>

    <el-row :gutter="20">
      <!-- 左侧：配置区 -->
      <el-col :span="6">
        <el-card class="config-card">
          <template #header>
            <span style="font-weight:600">资源配置</span>
          </template>
          <el-form label-width="90px" label-position="left">
            <el-form-item label="选择学生">
              <el-select v-model="form.student_id" placeholder="请选择学生" filterable style="width:100%">
                <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择课程">
              <el-select v-model="form.course_id" placeholder="请选择课程" style="width:100%" @change="onCourseChange">
                <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择知识点">
              <el-select v-model="form.knowledge_point_ids" multiple placeholder="请选择知识点" style="width:100%">
                <el-option v-for="kp in knowledgePoints" :key="kp.id" :label="kp.name" :value="kp.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="资源类型">
              <el-select v-model="form.resource_type" placeholder="请选择资源类型" style="width:100%">
                <el-option v-for="rt in resourceTypes" :key="rt.value" :label="rt.label" :value="rt.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="难度等级">
              <el-select v-model="form.difficulty" placeholder="请选择难度" style="width:100%">
                <el-option v-for="d in difficultyOptions" :key="d.value" :label="d.label" :value="d.value" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="generating"
                style="width:100%"
                @click="handleGenerate"
              >
                {{ generating ? "生成中..." : "生成个性化学习资源" }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="mt-16">
          <template #header>
            <span style="font-weight:600">协作智能体</span>
          </template>
          <div class="agent-list">
            <div v-for="step in agentSteps" :key="step.id" class="agent-item">
              <el-icon size="16" color="#409eff"><component :is="Icons.Cpu" /></el-icon>
              <span class="agent-name">{{ step.name }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 中间：执行链路 -->
      <el-col :span="5">
        <el-card>
          <template #header>
            <span style="font-weight:600">执行链路</span>
          </template>
          <div class="agent-chain">
            <div v-for="(step, idx) in agentSteps" :key="step.id" class="chain-step">
              <div class="step-indicator">
                <el-icon v-if="getStepStatus(step.id) === 'pending'" color="#c0c4cc"><Icons.Clock /></el-icon>
                <el-icon v-else-if="getStepStatus(step.id) === 'running'" color="#409eff" class="spinning"><Icons.Loading /></el-icon>
                <el-icon v-else-if="getStepStatus(step.id) === 'success'" color="#67c23a"><Icons.CircleCheck /></el-icon>
                <el-icon v-else-if="getStepStatus(step.id) === 'failed'" color="#f56c6c"><Icons.CircleClose /></el-icon>
              </div>
              <div class="step-info">
                <div class="step-name" :class="{ 'step-running': getStepStatus(step.id) === 'running' }">
                  {{ step.name }}
                </div>
                <div class="step-desc">{{ step.desc }}</div>
              </div>
              <el-icon v-if="idx < agentSteps.length - 1" class="chain-arrow" color="#c0c4cc"><Icons.ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top:12px">
          <template #header>
            <span style="font-weight:600">执行详情</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="log in executionLog"
              :key="log.step"
              :type="log.status === 'success' ? 'success' : log.status === 'failed' ? 'danger' : log.status === 'running' ? 'primary' : 'info'"
              :hollow="log.status === 'pending'"
            >
              <div style="font-weight:500">{{ log.step }}</div>
              <div style="font-size:12px;color:#909399">
                {{ log.message }} {{ log.timestamp }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <!-- 右侧：结果展示 -->
      <el-col :span="13">
        <el-card v-if="result">
          <template #header>
            <span style="font-weight:600">生成结果</span>
            <div style="float:right;display:flex;gap:8px">
              <el-button
                v-if="!savedResource"
                type="success"
                size="small"
                @click="handleSave"
              >
                保存到学习资源库
              </el-button>
              <template v-else>
                <el-button type="primary" size="small" @click="downloadResource">
                  下载 Markdown
                </el-button>
                <el-tag type="success" size="small">
                  已保存 · {{ (savedResource.file_size / 1024).toFixed(1) }}KB
                </el-tag>
              </template>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="诊断结果" name="diagnosis">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="薄弱知识点">
                  <el-tag
                    v-for="wp in (result.diagnosis?.weak_points || [])"
                    :key="wp.kp_id"
                    type="danger"
                    style="margin-right:4px;margin-bottom:2px"
                  >
                    {{ wp.name }}（掌握度 {{ Math.round(wp.mastery_level * 100) }}%）
                  </el-tag>
                  <span v-if="!result.diagnosis?.weak_points?.length" style="color:#909399">暂无数据</span>
                </el-descriptions-item>
                <el-descriptions-item label="强项知识点">
                  <el-tag
                    v-for="sp in (result.diagnosis?.strength_points || [])"
                    :key="sp.kp_id"
                    type="success"
                    style="margin-right:4px;margin-bottom:2px"
                  >
                    {{ sp.name }}（{{ Math.round(sp.mastery_level * 100) }}%）
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="学习难点">
                  <span v-for="d in (result.diagnosis?.learning_difficulties || [])" :key="d" style="margin-right:8px">{{ d }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="资源需求">
                  <span v-for="r in (result.diagnosis?.resource_needs || [])" :key="r" style="margin-right:8px">{{ r }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="建议难度">
                  {{ result.diagnosis?.suggested_difficulty === 'basic' ? '基础' : result.diagnosis?.suggested_difficulty === 'intermediate' ? '进阶' : result.diagnosis?.suggested_difficulty === 'advanced' ? '高级' : '-' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>

            <el-tab-pane label="学习规划" name="plan">
              <el-descriptions :column="2" border size="small" v-if="result.plan">
                <el-descriptions-item label="学习策略" :span="2">
                  {{ result.plan.learning_sequence || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="资源组合">
                  {{ (result.plan.resource_combination || []).join('、') }}
                </el-descriptions-item>
                <el-descriptions-item label="预计总时长">
                  {{ result.plan.estimated_total_time || '-' }}
                </el-descriptions-item>
              </el-descriptions>
              <el-steps direction="vertical" :space="60" :active="result.plan?.learning_path?.length || 0" style="margin-top:16px" v-if="result.plan?.learning_path?.length">
                <el-step
                  v-for="step in result.plan.learning_path"
                  :key="step.order"
                  :title="`步骤${step.order}: ${step.kp_name}`"
                  :description="`${step.resource_type} | 预计 ${step.estimated_time} | 优先级: ${step.priority === 'high' ? '高' : step.priority === 'medium' ? '中' : '低'}`"
                />
              </el-steps>
              <el-empty v-else description="暂无学习规划" />
            </el-tab-pane>

            <el-tab-pane label="生成资源" name="resource">
              <div v-if="result.resource">
                <h3 style="margin:0 0 8px;font-size:16px">{{ result.resource.title }}</h3>
                <el-tag size="small" style="margin-right:4px">{{ result.resource.type === 'lecture' ? '知识点讲义' : result.resource.type === 'quiz' ? '习题与答案' : result.resource.type === 'ppt' ? 'PPT大纲' : result.resource.type === 'case' ? '案例材料' : result.resource.type }}</el-tag>
                <el-tag size="small" type="info" style="margin-right:4px">{{ result.resource.difficulty === 'basic' ? '基础' : result.resource.difficulty === 'intermediate' ? '进阶' : result.resource.difficulty === 'advanced' ? '高级' : result.resource.difficulty }}</el-tag>
                <el-tag size="small" type="warning" style="margin-right:4px">约{{ result.resource.estimated_learning_time }}</el-tag>
                <div style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:4px;max-height:480px;overflow-y:auto;font-size:13px;line-height:1.8" v-html="renderMarkdown(result.resource.content || '')" />
              </div>
            </el-tab-pane>

            <el-tab-pane label="评测反馈" name="assessment">
              <div v-if="result.assessment">
                <div style="display:flex;align-items:center;gap:24px;margin-bottom:16px">
                  <el-progress type="circle" :percentage="accuracyPercent(result.assessment)" :width="100" />
                  <div>
                    <div style="font-size:24px;font-weight:700;color:#409eff">{{ accuracyPercent(result.assessment) }}%</div>
                    <div style="color:#909399;font-size:13px">正确率</div>
                  </div>
                  <div>
                    <div style="font-size:14px;font-weight:600;margin-bottom:4px">反馈</div>
                    <div style="color:#606266;font-size:13px">{{ result.assessment.feedback || '-' }}</div>
                  </div>
                </div>
                <div style="margin-bottom:12px">
                  <div style="font-weight:600;margin-bottom:8px">改进建议</div>
                  <el-tag v-for="s in (result.assessment.suggestions || [])" :key="s" style="margin-right:4px;margin-bottom:4px">{{ s }}</el-tag>
                </div>
                <div style="color:#909399;font-size:13px">
                  下一步推荐：{{ result.assessment.next_resource_recommendation || '-' }}
                </div>
              </div>
              <el-empty v-else description="暂无评测数据" />
            </el-tab-pane>

            <el-tab-pane label="审核建议" name="review">
              <div v-if="result.teacher_review_suggestion">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
                  <el-rate
                    :model-value="(result.teacher_review_suggestion.quality_score || 0) / 2"
                    disabled
                    show-score
                    score-template="{value} / 10"
                  />
                  <el-tag :type="(result.teacher_review_suggestion.quality_score || 0) >= 7 ? 'success' : 'warning'" size="large">
                    {{ result.teacher_review_suggestion.quality_score }}/10
                  </el-tag>
                </div>
                <el-descriptions :column="1" border size="small" style="margin-bottom:12px">
                  <el-descriptions-item label="质量检查">
                    <el-tag
                      v-for="check in (result.teacher_review_suggestion.quality_checks || [])"
                      :key="check.check"
                      :type="check.passed ? 'success' : 'danger'"
                      size="small"
                      style="margin-right:4px;margin-bottom:2px"
                    >
                      {{ check.check }}: {{ check.passed ? '通过' : '待改进' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="整体评价">
                    {{ result.teacher_review_suggestion.overall_comment || '-' }}
                  </el-descriptions-item>
                </el-descriptions>
                <div v-if="(result.teacher_review_suggestion.suggestions || []).length">
                  <div style="font-weight:600;margin-bottom:8px">修改建议</div>
                  <el-tag v-for="s in result.teacher_review_suggestion.suggestions" :key="s" style="margin-right:4px;margin-bottom:4px">{{ s }}</el-tag>
                </div>
              </div>
              <el-empty v-else description="暂无审核数据" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
        <el-empty v-else description="请先选择配置并点击生成" />
      </el-col>
    </el-row>

    <el-dialog v-model="saveDialogVisible" title="保存到学习资源库" width="420">
      <el-form>
        <el-form-item label="资源标题" required>
          <el-input v-model="saveTitle" placeholder="请输入资源标题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSave">确认保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.spinning {
  animation: spin 1s linear infinite;
}
.agent-workbench {
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
.config-card { height: fit-content; }
.mt-16 { margin-top: 16px; }
.agent-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.agent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.agent-name { color: #606266; }
.agent-chain {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.chain-step {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}
.step-indicator { flex-shrink: 0; }
.step-info { flex: 1; }
.step-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}
.step-running { color: #409eff; }
.step-desc { font-size: 12px; color: #909399; }
.chain-arrow {
  position: absolute;
  bottom: -18px;
  left: 7px;
}
</style>
