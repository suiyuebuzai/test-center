import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listApps, createApp, listVersions } from '../api/apps'

export function useApps(page = 1) {
  const { data, ...rest } = useQuery({
    queryKey: ['apps', page],
    queryFn: () => listApps(page).then((r) => r.data.data),
  })
  return { data, ...rest }
}

export function useVersions(appId: string) {
  return useQuery({
    queryKey: ['versions', appId],
    queryFn: () => listVersions(appId).then((r) => r.data.data),
    enabled: !!appId,
  })
}

export function useCreateApp() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createApp,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['apps'] }),
  })
}
