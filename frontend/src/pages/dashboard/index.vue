<script lang="ts" setup>
import { useUserStore } from "@/pinia/stores/user"

const userStore = useUserStore()

const modules = [
  { name: "项目空间", desc: "管理项目、添加成员、设置角色", icon: "FolderOpened", color: "#e6f0ff", path: "/projects" },
  { name: "任务与版本", desc: "创建任务、AI 生成、版本管理", icon: "List", color: "#fff3e6", path: "/tasks" },
  { name: "审核中心", desc: "提交审核、管理审核意见", icon: "CircleCheck", color: "#e6ffe6", path: "/reviews" },
  { name: "成果库", desc: "查看已采用的最终成果", icon: "Collection", color: "#f0e6ff", path: "/artifacts" },
  { name: "统计看板", desc: "查看项目统计数据和图表", icon: "DataLine", color: "#ffe6f0", path: "/statistics" },
  { name: "模型管理", desc: "管理 AI 模型和 API 配置", icon: "Cpu", color: "#e6f0ff", path: "/models" }
]

const flowSteps = [
  { index: 1, title: "创建项目", desc: "创建项目空间，添加成员" },
  { index: 2, title: "创建任务", desc: "制定任务计划，选择类型" },
  { index: 3, title: "AI 生成", desc: "调用模型生成初稿内容" },
  { index: 4, title: "人工编辑", desc: "修改完善 AI 生成内容" },
  { index: 5, title: "提交审核", desc: "提交给负责人或教师审核" },
  { index: 6, title: "采用归档", desc: "审核通过后进入成果库" }
]
</script>

<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">欢迎使用智研协作系统</h1>
      <p class="page-desc">
        您好，{{ userStore.userInfo?.real_name || userStore.username }}！
        当前角色：
        <el-tag v-for="role in userStore.roles" :key="role" size="small" type="info" style="margin-right: 4px">
          {{ role }}
        </el-tag>
      </p>
    </div>

    <el-card class="flow-card">
      <template #header>
        <div class="card-header">
          <el-icon><Connection /></el-icon>
          <span>核心业务流程</span>
        </div>
      </template>
      <div class="flow-steps">
        <div v-for="step in flowSteps" :key="step.index" class="flow-step">
          <div class="step-number">{{ step.index }}</div>
          <div class="step-info">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.desc }}</div>
          </div>
          <el-icon v-if="step.index < flowSteps.length" class="step-arrow">
            <ArrowRight />
          </el-icon>
        </div>
      </div>
    </el-card>

    <div class="module-grid">
      <div
        v-for="module in modules"
        :key="module.path"
        class="module-card"
        @click="$router.push(module.path)"
      >
        <div class="module-icon" :style="{ background: module.color }">
          <el-icon :size="28"><component :is="module.icon" /></el-icon>
        </div>
        <div class="module-info">
          <div class="module-name">{{ module.name }}</div>
          <div class="module-desc">{{ module.desc }}</div>
        </div>
        <el-icon class="module-arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <el-card class="stats-hint">
      <template #header>
        <div class="card-header">
          <el-icon><DataLine /></el-icon>
          <span>统计看板说明</span>
        </div>
      </template>
      <el-alert type="info" :closable="false" show-icon>
        <template #title>
          统计数据将在后续阶段接入。当前统计看板将展示项目总数、任务总数、AI 调用次数、审核通过率等维度数据。
        </template>
      </el-alert>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.dashboard {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
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

.flow-card {
  margin-bottom: 20px;
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

.step-number {
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: #ffffff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    border-color: #1e3a5f;
  }
}

.module-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #1e3a5f;
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
</style>
