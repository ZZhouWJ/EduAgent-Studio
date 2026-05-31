import type * as Projects from "./type"
import { request } from "@/http/axios"

/** 获取项目列表 */
export function getProjectListApi(params: Projects.ProjectListParams = {}) {
  return request<ApiResponseData<Projects.ProjectListResponse>>({
    url: "api/projects",
    method: "get",
    params
  })
}

/** 创建项目 */
export function createProjectApi(data: Projects.CreateProjectRequestData) {
  return request<ApiResponseData<Projects.Project>>({
    url: "api/projects",
    method: "post",
    data
  })
}

/** 获取项目详情 */
export function getProjectDetailApi(projectId: number | string) {
  return request<ApiResponseData<Projects.Project>>({
    url: `api/projects/${projectId}`,
    method: "get"
  })
}

/** 更新项目信息 */
export function updateProjectApi(projectId: number | string, data: Partial<Projects.CreateProjectRequestData> & { status?: string }) {
  return request<ApiResponseData<Projects.Project>>({
    url: `api/projects/${projectId}`,
    method: "put",
    data
  })
}

/** 删除项目（软删除） */
export function deleteProjectApi(projectId: number | string) {
  return request<ApiResponseData<null>>({
    url: `api/projects/${projectId}`,
    method: "delete"
  })
}

/** 获取项目成员列表 */
export function getProjectMembersApi(projectId: number | string) {
  return request<ApiResponseData<Projects.ProjectMember[]>>({
    url: `api/projects/${projectId}/members`,
    method: "get"
  })
}

/** 添加项目成员 */
export function addProjectMemberApi(projectId: number | string, data: { user_id: number; project_role: string }) {
  return request<ApiResponseData<Projects.ProjectMember>>({
    url: `api/projects/${projectId}/members`,
    method: "post",
    data
  })
}

/** 更新项目成员角色 */
export function updateProjectMemberRoleApi(projectId: number | string, memberId: number | string, data: { project_role: string }) {
  return request<ApiResponseData<Projects.ProjectMember>>({
    url: `api/projects/${projectId}/members/${memberId}`,
    method: "put",
    data
  })
}

/** 移除项目成员（软删除） */
export function removeProjectMemberApi(projectId: number | string, memberId: number | string) {
  return request<ApiResponseData<null>>({
    url: `api/projects/${projectId}/members/${memberId}`,
    method: "delete"
  })
}

/** 归档项目 */
export function archiveProjectApi(projectId: number | string) {
  return request<ApiResponseData<null>>({
    url: `api/projects/${projectId}/archive`,
    method: "post"
  })
}
