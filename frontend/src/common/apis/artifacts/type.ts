/** 成果项列表行（后端 _artifact_row_to_dict 返回） */
export interface AdoptedOutputListItem {
  adopted_id: number
  project_id: number
  task_id: number
  output_id: number
  artifact_title: string
  artifact_type: string
  release_version?: string
  adopted_by: number
  /** 后端 computed: adopted_by_real_name OR adopted_by_username */
  adopted_by_name?: string
  adopted_at: string
  task_title?: string
  output_title?: string
  version_no?: string | number
}

/** 成果项详情（后端 _artifact_detail_to_dict 返回） */
export interface AdoptedOutputDetail {
  adopted_id: number
  project_id: number
  project_name?: string
  task_id: number
  task_title?: string
  output_id: number
  output_title?: string
  version_no?: string | number
  /** 成果正文（后端真实字段为 output_content） */
  output_content?: string
  output_status?: string
  artifact_title: string
  artifact_type: string
  release_version?: string
  adopted_by: number
  adopted_by_username?: string
  adopted_by_real_name?: string
  adopted_at: string
  created_at?: string
  updated_at?: string
}

/** 成果项（列表和详情共用，兼容两种结构） */
export type AdoptedOutput = AdoptedOutputListItem & Partial<AdoptedOutputDetail>

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
