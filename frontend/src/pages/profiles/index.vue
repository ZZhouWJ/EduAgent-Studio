<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { profilesApi, type StudentProfile } from "@/api/profiles"
import { ElMessage } from "element-plus"

const router = useRouter()

const loading = ref(false)
const tableData = ref<StudentProfile[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filterForm = ref({
  course_id: undefined as number | undefined,
  keyword: ""
})

const courses = [
  { id: 1, name: "数据库系统原理" },
  { id: 2, name: "Python程序设计" },
  { id: 3, name: "软件工程实践" }
]

function masteryColor(score: number) {
  if (score >= 0.7) return "#67c23a"
  if (score >= 0.4) return "#e6a23c"
  return "#f56c6c"
}

async function loadProfiles() {
  loading.value = true
  try {
    const res = await profilesApi.list({
      page: page.value,
      page_size: pageSize.value,
      course_id: filterForm.value.course_id,
      keyword: filterForm.value.keyword || undefined
    })
    tableData.value = res.data.data.items
    total.value = res.data.data.total
  } catch {
    ElMessage.error("加载学生画像失败")
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filterForm.value = { course_id: undefined, keyword: "" }
  page.value = 1
  loadProfiles()
}

function viewDetail(row: StudentProfile) {
  router.push(`/profiles/${row.profile_id}`)
}

function editProfile(row: StudentProfile) {
  router.push(`/profiles/${row.profile_id}`)
}

function handlePageChange(p: number) {
  page.value = p
  loadProfiles()
}

onMounted(() => {
  loadProfiles()
})
</script>

<template>
  <div class="profiles-page page-container">
    <h1 class="page-title">学生画像</h1>

    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="课程">
          <el-select v-model="filterForm.course_id" placeholder="选择课程" clearable>
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="学生姓名/学号" clearable style="width:200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProfiles">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="tableData" v-loading="loading" class="mt-16">
      <el-table-column prop="student_name" label="学生姓名" min-width="100" />
      <el-table-column prop="course_name" label="所属课程" min-width="140" />
      <el-table-column prop="current_level" label="当前水平" min-width="140" />
      <el-table-column label="薄弱知识点" min-width="200">
        <template #default="{ row }">
          <el-tag
            v-for="wp in (row.weak_points || [])"
            :key="wp"
            size="small"
            type="danger"
            style="margin-right: 4px; margin-bottom: 2px"
          >
            {{ wp }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="掌握度评分" width="140">
        <template #default="{ row }">
          <el-progress
            :percentage="Math.round((row.mastery_score || 0) * 100)"
            :color="masteryColor(row.mastery_score || 0)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="last_updated" label="最近更新" width="120" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">查看详情</el-button>
          <el-button size="small" @click="editProfile(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.profiles-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}
.filter-card {
  margin-bottom: 16px;
}
.mt-16 {
  margin-top: 16px;
}
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
