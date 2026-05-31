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
