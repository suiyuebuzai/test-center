import client, { ApiResponse } from './client'

export interface TestTask {
  id: string
  app_id: string
  version_id: string
  name: string
  status: string
  created_at: string
}

export interface TaskExecution {
  id: string
  task_id: string
  test_case_id: string
  result: string
  actual_result: string | null
  executed_at: string
}

export interface TestTaskCreate {
  name: string
  version_id: string
  description?: string
  assignee_id?: string
  start_date?: string
  due_date?: string
}

export interface ExecutionCreate {
  test_case_id: string
  result: string
  actual_result?: string
  executed_at: string
  duration_seconds?: number
}

export const listTestTasks = (appId: string) =>
  client.get<ApiResponse<TestTask[]>>(`/apps/${appId}/test-tasks`)

export const createTestTask = (appId: string, data: TestTaskCreate) =>
  client.post<ApiResponse<TestTask>>(`/apps/${appId}/test-tasks`, data)

export const getTestTask = (taskId: string) =>
  client.get<ApiResponse<TestTask>>(`/test-tasks/${taskId}`)

export const listExecutions = (taskId: string) =>
  client.get<ApiResponse<TaskExecution[]>>(`/test-tasks/${taskId}/executions`)

export const createExecution = (taskId: string, data: ExecutionCreate) =>
  client.post<ApiResponse<TaskExecution>>(`/test-tasks/${taskId}/executions`, data)
