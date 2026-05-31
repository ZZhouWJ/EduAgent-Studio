import type * as Artifacts from "./type"
import { request } from "@/http/axios"

/** 采用成果：POST /api/outputs/{output_id}/adopt */
export function adoptOutputApi(outputId: number | string, data: Artifacts.AdoptOutputRequestData) {
  return request<Artifacts.ApiResponseData<{ adopted_id: number }>>({
    url: `api/outputs/${outputId}/adopt`,
    method: "post",
    data
  })
}

/** 获取项目成果列表：GET /api/projects/{project_id}/artifacts */
export function getProjectArtifactsApi(projectId: number | string, params?: { page?: number; page_size?: number }) {
  return request<Artifacts.ApiResponseData<{
    items: Artifacts.AdoptedOutput[]
    total: number
    page: number
    page_size: number
  }>>({
    url: `api/projects/${projectId}/artifacts`,
    method: "get",
    params
  })
}

/** 获取成果详情：GET /api/artifacts/{adopted_id} */
export function getArtifactDetailApi(adoptedId: number | string) {
  return request<Artifacts.ApiResponseData<Artifacts.AdoptedOutput>>({
    url: `api/artifacts/${adoptedId}`,
    method: "get"
  })
}

/** 分支合并：POST /api/tasks/{task_id}/branches/merge */
export function mergeTaskBranchesApi(taskId: number | string, data: Artifacts.MergeBranchesRequestData) {
  return request<Artifacts.ApiResponseData<{ merge_record_id: number; new_output_id?: number }>>({
    url: `api/tasks/${taskId}/branches/merge`,
    method: "post",
    data
  })
}
