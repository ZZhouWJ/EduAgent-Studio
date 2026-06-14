import client from '../api'

export interface Artifact {
  adopted_id: number
  project_id: number
  task_id: number
  output_id: number
  artifact_title: string
  artifact_type: string
  release_version?: string
  adopted_by: number
  adopted_by_name: string
  adopted_at: string
  task_title: string
  output_title: string
  version_no: number
  description?: string
}

export interface ArtifactDetail extends Artifact {
  output_content: string
  output_status: string
  project_name: string
  adopted_by_username?: string
}

export const artifactsApi = {
  list(
    project_id: number,
    params?: {
      page?: number
      page_size?: number
      artifact_type?: string
      keyword?: string
    }
  ) {
    return client.get<{ items: Artifact[]; total: number }>(`/projects/${project_id}/artifacts`, {
      params,
    })
  },

  getById(adopted_id: number) {
    return client.get<ArtifactDetail>(`/artifacts/${adopted_id}`)
  },

  adoptOutput(
    output_id: number,
    data: {
      artifact_title: string
      artifact_type: string
      release_version?: string
      adopt_note?: string
    }
  ) {
    return client.post<{ adopted_id: number }>(`/outputs/${output_id}/adopt`, data)
  },

  mergeBranches(
    task_id: number,
    data: {
      source_branch_id: number
      target_branch_id: number
      source_output_id?: number
      target_output_id?: number
      merge_strategy: string
      merged_output_title?: string
      merged_content?: string
      merge_note?: string
    }
  ) {
    return client.post(`/tasks/${task_id}/branches/merge`, data)
  },
}
