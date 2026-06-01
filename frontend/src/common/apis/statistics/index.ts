import type * as Statistics from "./type"
import { request } from "@/http/axios"

/** 统计概览：GET /api/statistics/overview */
export function getStatisticsOverviewApi(params?: { project_id?: number }) {
  return request<Statistics.ApiResponseData<Statistics.StatisticsOverview>>({
    url: "api/statistics/overview",
    method: "get",
    params
  })
}

/** 项目维度统计：GET /api/statistics/projects
 * 后端返回数组，不是分页对象 */
export function getProjectStatisticsApi(params?: { project_id?: number }) {
  return request<Statistics.ApiResponseData<Statistics.ProjectStats[]>>({
    url: "api/statistics/projects",
    method: "get",
    params
  })
}

/** 模型调用统计：GET /api/statistics/model-calls
 * 后端返回数组，不是分页对象 */
export function getModelCallStatisticsApi(params?: { project_id?: number; date_from?: string; date_to?: string }) {
  return request<Statistics.ApiResponseData<Statistics.ModelCallStats[]>>({
    url: "api/statistics/model-calls",
    method: "get",
    params
  })
}

/** 成本统计：GET /api/statistics/costs */
export function getCostStatisticsApi(params?: { project_id?: number; date_from?: string; date_to?: string }) {
  return request<Statistics.ApiResponseData<Statistics.CostStats>>({
    url: "api/statistics/costs",
    method: "get",
    params
  })
}

/** 审核质量统计：GET /api/statistics/reviews */
export function getReviewStatisticsApi(params?: { project_id?: number }) {
  return request<Statistics.ApiResponseData<Statistics.ReviewStats>>({
    url: "api/statistics/reviews",
    method: "get",
    params
  })
}

/** 成员贡献统计：GET /api/statistics/member-contributions
 * 后端返回数组，不是分页对象 */
export function getMemberContributionsApi(params?: { project_id?: number }) {
  return request<Statistics.ApiResponseData<Statistics.MemberContribution[]>>({
    url: "api/statistics/member-contributions",
    method: "get",
    params
  })
}

/** 最近操作动态：GET /api/statistics/recent-activities
 * 后端返回数组，不是分页对象 */
export function getRecentActivitiesApi(params?: { project_id?: number; limit?: number }) {
  return request<Statistics.ApiResponseData<Statistics.RecentActivity[]>>({
    url: "api/statistics/recent-activities",
    method: "get",
    params
  })
}
