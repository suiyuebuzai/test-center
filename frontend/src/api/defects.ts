import client, { ApiResponse } from './client'

export interface Defect {
  id: string
  defect_no: string
  app_id: string
  title: string
  severity: string
  priority: string
  status: string
  source: string
  reporter_id: string
  assignee_id: string | null
  found_version_id: string
  fix_version_id: string | null
  created_at: string
  comments: Comment[]
}

export interface DefectSummary {
  id: string
  defect_no: string
  title: string
  severity: string
  priority: string
  status: string
  reporter_id: string
  assignee_id: string | null
  created_at: string
}

export interface PaginatedDefects {
  items: DefectSummary[]
  total: number
  page: number
  page_size: number
}

export interface Comment {
  id: string
  author_id: string
  content: string
  created_at: string
}

export interface StatusHistory {
  id: string
  from_status: string | null
  to_status: string
  changed_by: string
  comment: string | null
  changed_at: string
}

export interface DefectCreate {
  title: string
  description?: string
  steps_to_reproduce?: string
  expected_result?: string
  actual_result?: string
  severity?: string
  priority?: string
  found_version_id: string
  assignee_id?: string
}

export const listDefects = (
  appId: string,
  params?: { page?: number; page_size?: number; status?: string; severity?: string },
) => client.get<ApiResponse<PaginatedDefects>>(`/apps/${appId}/defects`, { params })

export const createDefect = (appId: string, data: DefectCreate) =>
  client.post<ApiResponse<Defect>>(`/apps/${appId}/defects`, data)

export const getDefect = (defectId: string) =>
  client.get<ApiResponse<Defect>>(`/defects/${defectId}`)

export const transitionDefect = (
  defectId: string,
  data: { to_status: string; assignee_id?: string; comment?: string },
) => client.post<ApiResponse<Defect>>(`/defects/${defectId}/transitions`, data)

export const addComment = (defectId: string, content: string) =>
  client.post<ApiResponse<Comment>>(`/defects/${defectId}/comments`, { content })

export const getHistory = (defectId: string) =>
  client.get<ApiResponse<StatusHistory[]>>(`/defects/${defectId}/history`)
