import { Navigate, Outlet } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuth } from '../context/AuthContext'

export default function PrivateRoute() {
  const { user, loading } = useAuth()
  if (loading) return <Spin fullscreen />
  return user ? <Outlet /> : <Navigate to="/login" replace />
}
