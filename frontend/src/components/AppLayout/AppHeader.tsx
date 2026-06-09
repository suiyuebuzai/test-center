import { Layout, Select, Space, Button, Typography } from 'antd'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useApps } from '../../hooks/useApps'

const { Header } = Layout

export default function AppHeader() {
  const { user, logout } = useAuth()
  const { appId } = useParams<{ appId: string }>()
  const navigate = useNavigate()
  const { data } = useApps()
  const apps = data?.items ?? []

  return (
    <Header style={{ display: 'flex', alignItems: 'center', padding: '0 16px', gap: 16 }}>
      <Typography.Text strong style={{ color: '#1890ff', fontSize: 16, whiteSpace: 'nowrap' }}>
        ⚡ Test Center
      </Typography.Text>

      <Select
        value={appId}
        onChange={(id) => navigate(`/apps/${id}/defects`)}
        style={{ width: 200 }}
        placeholder="选择应用"
        options={apps.map((a) => ({ label: `${a.name} (${a.code})`, value: a.id }))}
      />

      <Space style={{ marginLeft: 'auto' }}>
        <Typography.Text style={{ color: '#aaa' }}>{user?.username}</Typography.Text>
        <Button size="small" onClick={logout}>退出</Button>
      </Space>
    </Header>
  )
}
