import { Layout, Menu } from 'antd'
import { useNavigate, useParams, useLocation } from 'react-router-dom'

const { Sider } = Layout

const MENU_ITEMS = [
  { key: 'test-cases', label: '📋 测试用例' },
  { key: 'defects',    label: '🐛 缺陷管理' },
  { key: 'test-tasks', label: '✅ 测试任务' },
]

export default function AppSider() {
  const { appId } = useParams<{ appId: string }>()
  const navigate = useNavigate()
  const location = useLocation()

  const selectedKey = MENU_ITEMS.find((item) =>
    location.pathname.includes(`/${item.key}`),
  )?.key ?? ''

  return (
    <Sider width={140} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        items={MENU_ITEMS}
        onClick={({ key }) => navigate(`/apps/${appId}/${key}`)}
        style={{ height: '100%', borderRight: 0 }}
      />
    </Sider>
  )
}
