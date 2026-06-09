import client, { ApiResponse } from './client'

export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  roles: string[]
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export const login = (username: string, password: string) =>
  client.post<ApiResponse<TokenResponse>>('/auth/login', { username, password })

export const getMe = () =>
  client.get<ApiResponse<User>>('/auth/me')
