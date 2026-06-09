import { useState } from 'react'
import {
  Layout, Typography, Input, Card, Row, Col, Button, Modal, Form,
  Space, message, Spin, Empty,
} from 'antd'
import { useNavigate } from 'react-router-dom'
import { useApps, useCreateApp } from '../../hooks/useApps'
import { useAuth } from '../../context/AuthContext'

const { Header, Content } = Layout

export default function AppList() {
  const navigate = useNavigate()
  const { hasRole, user, logout } = useAuth()
  const { data, isLoading } = useApps()
  const createApp = useCreateApp()
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const apps = (data?.items ?? []).filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.code.toLowerCase().includes(search.toLowerCase()),
  )

  const handleCreate = async (values: { name: string; code: string; description?: string }) => {
    try {
      await createApp.mutateAsync(values)
      message.success('应用创建成功')
      setModalOpen(false)
      form.resetFields()
    } catch {
      message.error('创建失败，名称或 code 已存在')
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 16px', gap: 16 }}>
        <Typography.Text strong style={{ color: '#1890ff', fontSize: 16 }}>
          ⚡ Test Center
        </Typography.Text>
        <Space style={{ marginLeft: 'auto' }}>
          <Typography.Text style={{ color: '#aaa' }}>{user?.username}</Typography.Text>
          <Button size="small" onClick={logout}>退出</Button>
        </Space>
      </Header>

      <Content style={{ padding: '24px 32px', background: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <Typography.Title level={4} style={{ margin: 0 }}>应用列表</Typography.Title>
          {hasRole('admin') && (
            <Button type="primary" onClick={() => setModalOpen(true)}>+ 新建应用</Button>
          )}
        </div>

        <Input.Search
          placeholder="搜索应用名称或代码..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 280, marginBottom: 20 }}
          allowClear
        />

        {isLoading ? (
          <Spin />
        ) : apps.length === 0 ? (
          <Empty description="暂无应用" />
        ) : (
          <Row gutter={[16, 16]}>
            {apps.map((app) => (
              <Col key={app.id} xs={24} sm={12} lg={8}>
                <Card
                  hoverable
                  style={{ height: '100%' }}
                  actions={[
                    <Button type="link" onClick={() => navigate(`/apps/${app.id}/defects`)}>
                      进入 →
                    </Button>,
                  ]}
                >
                  <Card.Meta
                    title={app.name}
                    description={
                      <>
                        <Typography.Text code>{app.code}</Typography.Text>
                        <br />
                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                          {app.description ?? '暂无描述'}
                        </Typography.Text>
                      </>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Content>

      <Modal
        title="新建应用"
        open={modalOpen}
        onCancel={() => { setModalOpen(false); form.resetFields() }}
        onOk={form.submit}
        confirmLoading={createApp.isPending}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="应用名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item
            name="code"
            label="Code（大写字母/数字）"
            rules={[{ required: true }, { pattern: /^[A-Z0-9]+$/, message: '只允许大写字母和数字' }]}
          >
            <Input style={{ textTransform: 'uppercase' }} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  )
}
