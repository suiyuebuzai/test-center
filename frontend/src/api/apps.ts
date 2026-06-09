import client, { ApiResponse } from './client'

export interface App {
  id: string
  name: string
  code: string
  description: string | null
  is_active: boolean
  created_at: string
}

export interface Version {
  id: string
  app_id: string
  name: string
  description: string | null
  status: string
  created_at: string
}

export interface PaginatedApps {
  items: App[]
  total: number
  page: number
  page_size: number
}

export const listApps = (page = 1, pageSize = 20) =>
  client.get<ApiResponse<PaginatedApps>>('/apps', { params: { page, page_size: pageSize } })

export const createApp = (data: { name: string; code: string; description?: string }) =>
  client.post<ApiResponse<App>>('/apps', data)

export const listVersions = (appId: string) =>
  client.get<ApiResponse<Version[]>>(`/apps/${appId}/versions`)
