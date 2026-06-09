import client, { ApiResponse } from './client'

export interface TestCase {
  id: string
  app_id: string
  title: string
  description: string | null
  category: string | null
  priority: string
  case_type: string
  is_automated: boolean
  created_at: string
}

export interface PaginatedTestCases {
  items: TestCase[]
  total: number
  page: number
  page_size: number
}

export interface TestCaseCreate {
  title: string
  description?: string
  preconditions?: string
  steps?: Array<{ action: string; expected?: string }>
  expected_result?: string
  category?: string
  priority?: string
  case_type?: string
  is_automated?: boolean
}

export const listTestCases = (
  appId: string,
  params?: { page?: number; page_size?: number; priority?: string; category?: string; is_automated?: boolean },
) => client.get<ApiResponse<PaginatedTestCases>>(`/apps/${appId}/test-cases`, { params })

export const createTestCase = (appId: string, data: TestCaseCreate) =>
  client.post<ApiResponse<TestCase>>(`/apps/${appId}/test-cases`, data)

export const deleteTestCase = (caseId: string) =>
  client.delete<ApiResponse<null>>(`/test-cases/${caseId}`)
