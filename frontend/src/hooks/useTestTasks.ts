import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  listTestTasks, createTestTask, getTestTask,
  listExecutions, createExecution,
  TestTaskCreate, ExecutionCreate,
} from '../api/testTasks'

export function useTestTasks(appId: string) {
  return useQuery({
    queryKey: ['testTasks', appId],
    queryFn: () => listTestTasks(appId).then((r) => r.data.data),
    enabled: !!appId,
  })
}

export function useTestTask(taskId: string) {
  return useQuery({
    queryKey: ['testTask', taskId],
    queryFn: () => getTestTask(taskId).then((r) => r.data.data),
    enabled: !!taskId,
  })
}

export function useCreateTestTask(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: TestTaskCreate) => createTestTask(appId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['testTasks', appId] }),
  })
}

export function useExecutions(taskId: string) {
  return useQuery({
    queryKey: ['executions', taskId],
    queryFn: () => listExecutions(taskId).then((r) => r.data.data),
    enabled: !!taskId,
  })
}

export function useCreateExecution(taskId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ExecutionCreate) => createExecution(taskId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['executions', taskId] }),
  })
}
