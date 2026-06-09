import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

describe('API client', () => {
  beforeEach(() => {
    localStorage.clear()
    delete (window as any).location
    ;(window as any).location = { href: '' }
    vi.resetModules()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('附加 Authorization 头当 token 存在时', async () => {
    localStorage.setItem('token', 'test-token')
    const { default: client } = await import('./client')
    const handler = client.interceptors.request.handlers[0] as any
    const config = await handler.fulfilled({ headers: {} as any })
    expect(config.headers.Authorization).toBe('Bearer test-token')
  })

  it('token 不存在时不附加 Authorization 头', async () => {
    const { default: client } = await import('./client')
    const handler = client.interceptors.request.handlers[0] as any
    const config = await handler.fulfilled({ headers: {} as any })
    expect(config.headers.Authorization).toBeUndefined()
  })

  it('401 响应时清除 token 并跳转 /login', async () => {
    localStorage.setItem('token', 'expired-token')
    const { default: client } = await import('./client')
    const handler = client.interceptors.response.handlers[0] as any
    try {
      await handler.rejected({ response: { status: 401 } })
    } catch {}
    expect(localStorage.getItem('token')).toBeNull()
    expect(window.location.href).toBe('/login')
  })
})
