import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import PrivateRoute from './PrivateRoute'
import { AuthContext } from '../context/AuthContext'
import type { User } from '../api/auth'

const makeWrapper = (user: User | null) =>
  ({ children }: { children: React.ReactNode }) => (
    <AuthContext.Provider
      value={{
        user,
        loading: false,
        login: async () => {},
        logout: () => {},
        hasRole: () => false,
      }}
    >
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<PrivateRoute />}>
            <Route path="/protected" element={<div>Protected Content</div>} />
          </Route>
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
      {children}
    </AuthContext.Provider>
  )

describe('PrivateRoute', () => {
  it('已登录时渲染子路由', () => {
    const { getByText } = render(<></>, {
      wrapper: makeWrapper({ id: '1', username: 'admin', email: 'a@b.com', is_active: true, roles: ['admin'] }),
    })
    expect(getByText('Protected Content')).toBeInTheDocument()
  })

  it('未登录时重定向到 /login', () => {
    const { getByText } = render(<></>, { wrapper: makeWrapper(null) })
    expect(getByText('Login Page')).toBeInTheDocument()
  })
})
