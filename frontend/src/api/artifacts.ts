import request from "@/utils/request"

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
  list(projectId: number, params?: { page?: number; page_size?: number; artifact_type?: string; keyword?: string }) {
    return request.get<{ data: { items: Artifact[]; total: number; page: number; page_size: number } }>(
      `/api/projects/${projectId}/artifacts`,
      { params }
    )
  },

  getById(adoptedId: number) {
    return request.get<{ data: ArtifactDetail }>(`/api/artifacts/${adoptedId}`)
  }
}
