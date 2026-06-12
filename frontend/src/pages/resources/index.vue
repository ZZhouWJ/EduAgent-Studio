<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { resourcesApi } from "@/api/resources"

const router = useRouter()
const loading = ref(false)
const resourceList = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterCourse = ref<number | undefined>()
const filterType = ref<string | undefined>()

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await resourcesApi.list({
      page: page.value,
      page_size: pageSize.value,
      course_id: filterCourse.value,
      type: filterType.value,
    })
    if (res?.data) {
      resourceList.value = res.data.items
      total.value = res.data.total
    }
  } catch {
    ElMessage.error("加载资源列表失败")
  } finally {
    loading.value = false
  }
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    draft: "info",
    pending_review: "warning",
    approved: "success",
    rejected: "danger",
    archived: "info"
  }
  return map[status] || ""
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    draft: "草稿",
    pending_review: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
    archived: "已归档"
  }
  return map[status] || status
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    lecture: "知识点讲义",
    ppt: "PPT大纲",
    quiz: "习题与答案",
    case: "案例材料",
    review: "复习计划",
    test: "阶段测验"
  }
  return map[type] || type
}

function formatDate(dateStr: string) {
  return dateStr ? new Date(dateStr).toLocaleString("zh-CN") : "-"
}

function viewDetail(resource: any) {
  router.push(`/resources/${resource.resource_id}`)
}
</script>

<template>
  <div class="resources-page page-container" v-loading="loading">
    <h1 class="page-title">学习资源库</h1>

    <!-- 筛选栏 -->
    <el-card style="margin-bottom: 16px">
      <el-form :inline="true">
        <el-form-item label="资源类型">
          <el-select v-model="filterType" placeholder="全部" clearable style="width: 140px" @change="loadData">
            <el-option label="知识点讲义" value="lecture" />
            <el-option label="PPT大纲" value="ppt" />
            <el-option label="习题与答案" value="quiz" />
            <el-option label="案例材料" value="case" />
            <el-option label="复习计划" value="review" />
            <el-option label="阶段测验" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">筛选</el-button>
          <el-button @click="filterCourse = undefined; filterType = undefined; loadData()">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资源列表 -->
    <el-card>
      <el-table :data="resourceList" stripe style="width: 100%">
        <el-table-column prop="resource_title" label="资源标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.resource_title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="类型" width="120">
          <template #default="{ row }">
            {{ getTypeLabel(row.resource_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="course_name" label="课程" width="160" />
        <el-table-column prop="difficulty" label="难度" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="viewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="loadData"
        @current-change="loadData"
      />
    </el-card>
  </div>
</template>

<style scoped>
.resources-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}
</style>
