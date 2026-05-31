import type * as Tasks from "./type"
import { request } from "@/http/axios"

/** 获取项目任务列表 */
export function getProjectTaskListApi(projectId: number | string, params: Tasks.TaskListParams = {}) {
  return request<ApiResponseData<Tasks.TaskListResponse>>({
    url: `api/projects/${projectId}/tasks`,
    method: "get",
    params
  })
}

/** 创建项目任务 */
export function createProjectTaskApi(projectId: number | string, data: Tasks.CreateTaskRequestData) {
  return request<ApiResponseData<Tasks.Task>>({
    url: `api/projects/${projectId}/tasks`,
    method: "post",
    data
  })
}

/** 获取任务详情 */
export function getTaskDetailApi(taskId: number | string) {
  return request<ApiResponseData<Tasks.Task>>({
    url: `api/tasks/${taskId}`,
    method: "get"
  })
}

/** 更新任务信息 */
export function updateTaskApi(taskId: number | string, data: Partial<Tasks.CreateTaskRequestData> & { status?: string }) {
  return request<ApiResponseData<Tasks.Task>>({
    url: `api/tasks/${taskId}`,
    method: "put",
    data
  })
}

/** 删除任务（软删除） */
export function deleteTaskApi(taskId: number | string) {
  return request<ApiResponseData<null>>({
    url: `api/tasks/${taskId}`,
    method: "delete"
  })
}

/** 获取任务分支列表 */
export function getTaskBranchesApi(taskId: number | string) {
  return request<ApiResponseData<Tasks.TaskBranch[]>>({
    url: `api/tasks/${taskId}/branches`,
    method: "get"
  })
}

/** 创建任务分支 */
export function createTaskBranchApi(taskId: number | string, data: Tasks.CreateBranchRequestData) {
  return request<ApiResponseData<Tasks.TaskBranch>>({
    url: `api/tasks/${taskId}/branches`,
    method: "post",
    data
  })
}

/** 获取任务输出版本列表 */
export function getTaskOutputsApi(taskId: number | string, params: Tasks.OutputListParams = {}) {
  return request<ApiResponseData<Tasks.OutputListResponse>>({
    url: `api/tasks/${taskId}/outputs`,
    method: "get",
    params
  })
}

/** 获取输出版本详情 */
export function getOutputDetailApi(outputId: number | string) {
  return request<ApiResponseData<Tasks.TaskOutput>>({
    url: `api/outputs/${outputId}`,
    method: "get"
  })
}

/** 获取输出版本时间线 */
export function getOutputTimelineApi(outputId: number | string) {
  return request<ApiResponseData<Tasks.OutputTimeline[]>>({
    url: `api/outputs/${outputId}/timeline`,
    method: "get"
  })
}

/** 创建人工输出版本 */
export function createManualOutputApi(taskId: number | string, data: { content: string; title?: string; branch_id?: number }) {
  return request<ApiResponseData<Tasks.TaskOutput>>({
    url: `api/tasks/${taskId}/outputs/manual`,
    method: "post",
    data
  })
}

/** AI 生成：POST /api/tasks/{task_id}/generate */
export function generateTaskOutputApi(taskId: number | string, data: Tasks.GenerateRequestData) {
  return request<ApiResponseData<Tasks.GenerateResultItem[]>>({
    url: `api/tasks/${taskId}/generate`,
    method: "post",
    data
  })
}

/** 更新输出版本（乐观锁）：PUT /api/outputs/{output_id} */
export function updateOutputApi(outputId: number | string, data: Tasks.UpdateOutputRequestData) {
  return request<ApiResponseData<Tasks.TaskOutput>>({
    url: `api/outputs/${outputId}`,
    method: "put",
    data
  })
}

/** 另存为新版本：POST /api/outputs/{output_id}/save-as-new-version */
export function saveOutputAsNewVersionApi(outputId: number | string, data: Tasks.SaveAsNewVersionRequestData) {
  return request<ApiResponseData<Tasks.TaskOutput>>({
    url: `api/outputs/${outputId}/save-as-new-version`,
    method: "post",
    data
  })
}

/** 获取输出版本批注列表：GET /api/outputs/{output_id}/comments */
export function getOutputCommentsApi(outputId: number | string) {
  return request<ApiResponseData<Tasks.OutputComment[]>>({
    url: `api/outputs/${outputId}/comments`,
    method: "get"
  })
}

/** 新增批注：POST /api/outputs/{output_id}/comments */
export function createOutputCommentApi(outputId: number | string, data: Tasks.CreateCommentRequestData) {
  return request<ApiResponseData<Tasks.OutputComment>>({
    url: `api/outputs/${outputId}/comments`,
    method: "post",
    data
  })
}

/** 更新批注状态：PUT /api/comments/{comment_id}/status */
export function updateCommentStatusApi(commentId: number | string, data: Tasks.UpdateCommentStatusRequestData) {
  return request<ApiResponseData<Tasks.OutputComment>>({
    url: `api/comments/${commentId}/status`,
    method: "put",
    data
  })
}
