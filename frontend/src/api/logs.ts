import request from "@/utils/request"

// ============================================================================
// 操作日志
// ============================================================================

export interface OperationLog {
  log_id: number
  user_id: number
  username: string
  real_name: string
  action_type: string
  target_type: string
  target_id: number
  action_desc: string
  old_value?: string
  new_value?: string
  ip_address?: string
  created_at: string
}

// ============================================================================
// 登录日志
// ============================================================================

export interface LoginLog {
  log_id: number
  user_id: number
  username: string
  real_name: string
  login_status: "success" | "failed"
  fail_reason?: string
  ip_address?: string
  user_agent?: string
  login_time: string
}

// ============================================================================
// API
// ============================================================================

export const logsApi = {
  // 操作日志列表
  operationLogs(params?: {
    page?: number
    page_size?: number
    user_id?: number
    target_type?: string
    action_type?: string
    start_date?: string
    end_date?: string
  }) {
    return request.get<{ data: { items: OperationLog[]; total: number; page: number; page_size: number } }>(
      "/api/logs/operation",
      { params }
    )
  },

  // 登录日志列表
  loginLogs(params?: {
    page?: number
    page_size?: number
    user_id?: number
    login_status?: string
    start_date?: string
    end_date?: string
  }) {
    return request.get<{ data: { items: LoginLog[]; total: number; page: number; page_size: number } }>(
      "/api/logs/login",
      { params }
    )
  }
}
