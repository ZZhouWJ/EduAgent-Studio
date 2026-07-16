import client from './client'

export interface GovernanceSettings {
  fact_consistency_threshold: number
  citation_coverage_threshold: number
  hourly_call_limit: number
  sensitive_content_enabled: boolean
  updated_by?: number | null
  updated_at?: string | null
}

export type GovernanceSettingsUpdate = Pick<
  GovernanceSettings,
  | 'fact_consistency_threshold'
  | 'citation_coverage_threshold'
  | 'hourly_call_limit'
  | 'sensitive_content_enabled'
>

export interface BudgetAlertSettings {
  monthly_budget: number
  alert_threshold_percent: number
  enabled: boolean
  updated_by?: number | null
  updated_at?: string | null
}

export type BudgetAlertSettingsUpdate = Pick<
  BudgetAlertSettings,
  'monthly_budget' | 'alert_threshold_percent' | 'enabled'
>

export const platformSettingsApi = {
  getGovernance() {
    return client.get<GovernanceSettings>('/platform-settings/governance')
  },

  updateGovernance(data: GovernanceSettingsUpdate) {
    return client.put<GovernanceSettings>('/platform-settings/governance', data)
  },

  getBudgetAlert() {
    return client.get<BudgetAlertSettings>('/platform-settings/budget-alert')
  },

  updateBudgetAlert(data: BudgetAlertSettingsUpdate) {
    return client.put<BudgetAlertSettings>('/platform-settings/budget-alert', data)
  },
}
