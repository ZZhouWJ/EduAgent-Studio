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

export const platformSettingsApi = {
  getGovernance() {
    return client.get<GovernanceSettings>('/platform-settings/governance')
  },

  updateGovernance(data: GovernanceSettingsUpdate) {
    return client.put<GovernanceSettings>('/platform-settings/governance', data)
  },
}
