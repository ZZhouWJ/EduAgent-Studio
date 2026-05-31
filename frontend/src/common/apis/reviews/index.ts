import type * as Reviews from "./type"
import { request } from "@/http/axios"

/** 获取待审核列表：GET /api/reviews/pending */
export function getPendingReviewsApi(params?: { page?: number; page_size?: number; project_id?: number }) {
  return request<ApiResponseData<{
    items: Reviews.ReviewRequest[]
    total: number
    page: number
    page_size: number
  }>>({
    url: "api/reviews/pending",
    method: "get",
    params
  })
}

/** 获取审核详情：GET /api/reviews/{request_id} */
export function getReviewDetailApi(requestId: number | string) {
  return request<ApiResponseData<Reviews.ReviewDetail>>({
    url: `api/reviews/${requestId}`,
    method: "get"
  })
}

/** 完成审核：POST /api/reviews/{request_id}/complete */
export function completeReviewApi(requestId: number | string, data: Reviews.CompleteReviewRequestData) {
  return request<ApiResponseData<null>>({
    url: `api/reviews/${requestId}/complete`,
    method: "post",
    data
  })
}

/** 获取问题标签：GET /api/issue-tags */
export function getIssueTagsApi() {
  return request<ApiResponseData<Reviews.IssueTag[]>>({
    url: "api/issue-tags",
    method: "get"
  })
}
