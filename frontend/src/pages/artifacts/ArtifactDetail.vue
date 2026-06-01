<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { getArtifactDetailApi } from "@/common/apis/artifacts"
import type { AdoptedOutput } from "@/common/apis/artifacts/type"

const route = useRoute()
const router = useRouter()
const adoptedId = Number(route.params.adoptedId)

const loading = ref(false)
const detail = ref<Partial<AdoptedOutput>>({})

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getArtifactDetailApi(adoptedId)
    detail.value = res.data
  } catch { /* shown by interceptor */ }
  finally { loading.value = false }
}

function getArtifactTypeLabel(type: string) {
  const m: Record<string, string> = {
    report_section: "报告章节",
    requirements: "需求分析",
    design: "设计文档",
    code: "代码",
    test: "测试文档",
    manual: "使用手册",
    other: "其他"
  }
  return m[type] || type
}

onMounted(fetchDetail)
</script>

<template>
  <div class="artifact-detail-page">
    <div class="page-header">
      <el-button text @click="router.push('/artifacts')">
        <el-icon style="margin-right: 4px"><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h2 class="page-title">成果详情</h2>
    </div>

    <div v-loading="loading">
      <el-card style="margin-bottom: 16px">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="成果编号">{{ detail.adopted_id }}</el-descriptions-item>
          <el-descriptions-item label="成果标题" :span="2">{{ detail.artifact_title || "-" }}</el-descriptions-item>
          <el-descriptions-item label="成果类型">
            <el-tag size="small">{{ getArtifactTypeLabel(detail.artifact_type || "") }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发布版本">{{ detail.release_version || "-" }}</el-descriptions-item>
          <el-descriptions-item label="所属项目" :span="2">
            {{ detail.project_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="所属任务">
            {{ detail.task_title || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="原始输出">
            {{ detail.output_title || "-" }}&nbsp;v{{ detail.version_no || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="采用人">
            {{ detail.adopted_by_real_name || detail.adopted_by_username || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="采用时间">
            {{ detail.adopted_at ? new Date(detail.adopted_at).toLocaleString("zh-CN") : "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="原始状态">
            <el-tag size="small">{{ detail.output_status || "-" }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card>
        <template #header>
          <div style="font-weight: 600">成果正文</div>
        </template>
        <div v-if="detail.output_content" class="content-box">{{ detail.output_content }}</div>
        <el-empty v-else description="暂无正文内容" />
      </el-card>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.artifact-detail-page {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}
.content-box {
  white-space: pre-wrap;
  font-size: 14px;
  color: #303133;
  line-height: 1.8;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
}
</style>
