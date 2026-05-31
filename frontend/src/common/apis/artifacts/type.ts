/** 成果项 */
export interface AdoptedOutput {
  adopted_id: number
  project_id: number
  project_name?: string
  task_id: number
  task_title?: string
  output_id: number
  output_title?: string
  version_no?: string | number
  artifact_title: string
  artifact_type: string
  release_version?: string
  content?: string
  adopt_note?: string
  adopted_by: number
  adopted_by_username?: string
  adopted_by_real_name?: string
  created_at: string
}

/** 采用成果请求体：POST /api/outputs/{output_id}/adopt */
export interface AdoptOutputRequestData {
  artifact_title: string
  artifact_type: string
  release_version?: string
  adopt_note?: string
}

/** 分支合并请求体：POST /api/tasks/{task_id}/branches/merge */
export interface MergeBranchesRequestData {
  source_branch_id: number
  target_branch_id: number
  source_output_id?: number
  target_output_id?: number
  merge_strategy: "adopt_source" | "adopt_target" | "manual_merge" | "adopt_separately"
  merged_output_title?: string
  merged_content?: string
  merge_note?: string
}
