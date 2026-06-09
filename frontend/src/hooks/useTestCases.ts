import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listTestCases, createTestCase, deleteTestCase, TestCaseCreate } from '../api/testCases'

interface Filters {
  page?: number
  page_size?: number
  priority?: string
  category?: string
  is_automated?: boolean
}

export function useTestCases(appId: string, filters: Filters = {}) {
  return useQuery({
    queryKey: ['testCases', appId, filters],
    queryFn: () => listTestCases(appId, filters).then((r) => r.data.data),
    enabled: !!appId,
  })
}

export function useCreateTestCase(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: TestCaseCreate) => createTestCase(appId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['testCases', appId] }),
  })
}

export function useDeleteTestCase(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteTestCase,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['testCases', appId] }),
  })
}
