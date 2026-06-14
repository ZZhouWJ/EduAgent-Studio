import client from '../api'

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

export interface LoginLog {
  log_id: number
  user_id: number
  username: string
  real_name: string
  login_status: 'success' | 'failed'
  failure_reason?: string
  ip_address?: string
  user_agent?: string
  login_time: string
}

export const logsApi = {
  operationLogs(params?: {
    page?: number
    page_size?: number
    user_id?: number
    target_type?: string
    action_type?: string
    start_date?: string
    end_date?: string
  }) {
    return client.get<{ items: OperationLog[]; total: number }>('/logs/operation', { params })
  },

  loginLogs(params?: {
    page?: number
    page_size?: number
    user_id?: number
    login_status?: string
    start_date?: string
    end_date?: string
  }) {
    return client.get<{ items: LoginLog[]; total: number }>('/logs/login', { params })
  },
}
