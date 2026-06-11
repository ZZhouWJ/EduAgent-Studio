<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { agentsApi, type AgentResult } from "@/api/agents"
import { profilesApi } from "@/api/profiles"
import { ElMessage } from "element-plus"
import * as Icons from "@element-plus/icons-vue"

const generating = ref(false)
const result = ref<AgentResult | null>(null)
const activeTab = ref("diagnosis")
const saveDialogVisible = ref(false)
const saveTitle = ref("")

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

// Load initial data
onMounted(async () => {
  try {
    const agentsRes = await agentsApi.getAgents()
    const profilesRes = await profilesApi.list({ page_size: 100 })
    students.value = (profilesRes.data.data.items || []).map((p: any) => ({
      id: p.student_id,
      name: p.student_name,
      profile_id: p.profile_id
    }))
    courses.value = [
      { id: 1, name: "数据库系统原理" },
      { id: 2, name: "Python程序设计" },
      { id: 3, name: "软件工程实践" }
    ]
  } catch {
    // ignore
  }
})

// When course changes, load knowledge points
const courseKnowledgePoints: Record<number, Array<{ id: number; name: string }>> = {
  1: [
    { id: 1, name: "关系模型基础" },
    { id: 2, name: "SQL基本查询" },
    { id: 3, name: "数据定义DDL" },
    { id: 5, name: "SQL多表连接" },
    { id: 8, name: "事务隔离级别" },
    { id: 12, name: "数据库范式" }
  ],
  2: [
    { id: 20, name: "Python基础语法" },
    { id: 21, name: "函数参数传递" },
    { id: 22, name: "模块导入" },
    { id: 23, name: "异常处理" }
  ],
  3: [
    { id: 30, name: "需求分析" },
    { id: 31, name: "UML建模" }
  ]
}

function onCourseChange() {
  form.value.knowledge_point_ids = []
  knowledgePoints.value = courseKnowledgePoints[form.value.course_id!] || []
}

const agentSteps = computed(() => [
  { id: "diagnosis", name: "学习诊断", desc: "分析薄弱知识点", status: result.value ? "success" : "pending" },
  { id: "planning", name: "资源规划", desc: "生成学习路径", status: result.value ? "success" : "pending" },
  { id: "generation", name: "资源生成", desc: "生成学习资源", status: result.value ? "success" : "pending" },
  { id: "assessment", name: "评测反馈", desc: "生成反馈建议", status: result.value ? "success" : "pending" },
  { id: "review", name: "审核建议", desc: "质量检查", status: result.value ? "success" : "pending" }
])

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
  activeTab.value = "diagnosis"
  try {
    const res = await agentsApi.generate({
      student_id: form.value.student_id,
      course_id: form.value.course_id,
      knowledge_point_ids: form.value.knowledge_point_ids,
      resource_type: form.value.resource_type,
      difficulty: form.value.difficulty
    })
    result.value = res.data.data
    activeTab.value = "resource"
    ElMessage.success("个性化学习资源生成完成")
  } catch (e: any) {
    ElMessage.error("生成失败: " + (e?.message || "未知错误"))
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
    await agentsApi.saveResource({
      result: result.value!,
      title: saveTitle.value,
      course_id: form.value.course_id!
    })
    ElMessage.success("资源已保存到学习资源库")
    saveDialogVisible.value = false
  } catch {
    ElMessage.error("保存失败")
  }
}

function renderMarkdown(content: string) {
  return content
    .replace(/^# /gm, '<h2 style="margin-top:12px;font-size:16px;font-weight:600">')
    .replace(/^## /gm, '<h3 style="margin-top:10px;font-size:14px;font-weight:600">')
    .replace(/^### /gm, '<h4 style="margin-top:8px;font-size:13px;font-weight:600">')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code style="background:#f5f5f5;padding:2px 4px;border-radius:3px;font-size:12px">$1</code>')
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
              <el-button type="primary" :loading="generating" style="width:100%" @click="handleGenerate">
                {{ generating ? "生成中..." : "生成个性化学习资源" }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 智能体列表说明 -->
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
                <el-icon v-if="step.status === 'pending'" color="#c0c4cc"><Icons.Clock /></el-icon>
                <el-icon v-else color="#67c23a"><Icons.CircleCheck /></el-icon>
              </div>
              <div class="step-info">
                <div class="step-name">{{ step.name }}</div>
                <div class="step-desc">{{ step.desc }}</div>
              </div>
              <el-icon v-if="idx < agentSteps.length - 1" class="chain-arrow" color="#c0c4cc"><Icons.ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：结果展示 -->
      <el-col :span="13">
        <el-card v-if="result">
          <template #header>
            <span style="font-weight:600">生成结果</span>
            <el-button type="success" size="small" style="float:right" @click="handleSave">
              保存到学习资源库
            </el-button>
          </template>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="诊断结果" name="diagnosis">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="薄弱知识点">
                  <el-tag
                    v-for="wp in (result.diagnosis?.weak_points || [])"
                    :key="wp.kp_id"
                    type="danger"
                    style="margin-right:4px"
                  >
                    {{ wp.name }}（掌握度 {{ Math.round(wp.mastery_level * 100) }}%）
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="学习难点">
                  <span v-for="d in (result.diagnosis?.learning_difficulties || [])" :key="d" style="margin-right:8px">{{ d }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="资源需求">{{ (result.diagnosis?.resource_needs || []).join('、') }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>

            <el-tab-pane label="学习规划" name="plan">
              <el-steps direction="vertical" :space="60" v-if="result.plan?.learning_path?.length">
                <el-step
                  v-for="step in result.plan.learning_path"
                  :key="step.order"
                  :title="`步骤${step.order}: ${step.kp_name}`"
                  :description="`预计${step.estimated_time}，使用${step.resource_type}`"
                />
              </el-steps>
              <el-empty v-else description="暂无学习规划" />
            </el-tab-pane>

            <el-tab-pane label="生成资源" name="resource">
              <div v-if="result.resource">
                <h3 style="margin:0 0 8px;font-size:16px">{{ result.resource.title }}</h3>
                <el-tag size="small" style="margin-right:4px">{{ result.resource.type }}</el-tag>
                <el-tag size="small" type="info">{{ result.resource.difficulty }}</el-tag>
                <div class="resource-content" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:4px;max-height:500px;overflow-y:auto;font-size:13px;line-height:1.8" v-html="renderMarkdown(result.resource.content || '')" />
              </div>
            </el-tab-pane>

            <el-tab-pane label="评测反馈" name="assessment">
              <div v-if="result.assessment">
                <el-progress type="circle" :percentage="Math.round((result.assessment.accuracy_rate || 0) * 100)" :width="100" />
                <el-divider />
                <el-tag v-for="s in (result.assessment.suggestions || [])" :key="s" style="margin-right:4px;margin-bottom:4px">{{ s }}</el-tag>
              </div>
            </el-tab-pane>

            <el-tab-pane label="审核建议" name="review">
              <div v-if="result.teacher_review_suggestion">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="质量评分">{{ result.teacher_review_suggestion.quality_score }}/10</el-descriptions-item>
                  <el-descriptions-item label="整体评价">{{ result.teacher_review_suggestion.overall_comment }}</el-descriptions-item>
                </el-descriptions>
                <el-divider />
                <el-tag v-for="s in (result.teacher_review_suggestion.suggestions || [])" :key="s" style="margin-right:4px;margin-bottom:4px">{{ s }}</el-tag>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        <el-empty v-else description="请先选择配置并点击生成" />
      </el-col>
    </el-row>

    <!-- 保存对话框 -->
    <el-dialog v-model="saveDialogVisible" title="保存到学习资源库" width="400">
      <el-form>
        <el-form-item label="资源标题">
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
.config-card {
  height: fit-content;
}
.mt-16 {
  margin-top: 16px;
}
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
.agent-name {
  color: #606266;
}
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
.step-indicator {
  flex-shrink: 0;
}
.step-info {
  flex: 1;
}
.step-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}
.step-desc {
  font-size: 12px;
  color: #909399;
}
.chain-arrow {
  position: absolute;
  bottom: -18px;
  left: 7px;
}
</style>
