import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import AppHeader from './AppHeader'
import AppSider from './AppSider'

const { Content } = Layout

export default function AppLayout() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppHeader />
      <Layout>
        <AppSider />
        <Content style={{ padding: '16px 20px', background: '#fff' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
