import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  listDefects, createDefect, getDefect, transitionDefect, addComment, getHistory, DefectCreate,
} from '../api/defects'

interface Filters { page?: number; page_size?: number; status?: string; severity?: string }

export function useDefects(appId: string, filters: Filters = {}) {
  return useQuery({
    queryKey: ['defects', appId, filters],
    queryFn: () => listDefects(appId, filters).then((r) => r.data.data),
    enabled: !!appId,
  })
}

export function useDefect(defectId: string) {
  return useQuery({
    queryKey: ['defect', defectId],
    queryFn: () => getDefect(defectId).then((r) => r.data.data),
    enabled: !!defectId,
  })
}

export function useCreateDefect(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: DefectCreate) => createDefect(appId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['defects', appId] }),
  })
}

export function useTransitionDefect(defectId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { to_status: string; assignee_id?: string; comment?: string }) =>
      transitionDefect(defectId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['defect', defectId] })
    },
  })
}

export function useAddComment(defectId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (content: string) => addComment(defectId, content),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['defect', defectId] }),
  })
}

export function useDefectHistory(defectId: string) {
  return useQuery({
    queryKey: ['defectHistory', defectId],
    queryFn: () => getHistory(defectId).then((r) => r.data.data),
    enabled: !!defectId,
  })
}
