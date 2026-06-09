import { useState } from 'react'
import {
  Table, Button, Input, Select, Drawer, Descriptions, Tag, Space, Typography,
  Modal, Form, message, Breadcrumb,
} from 'antd'
import { useParams } from 'react-router-dom'
import { useTestCases, useCreateTestCase, useDeleteTestCase } from '../../hooks/useTestCases'
import { useAuth } from '../../context/AuthContext'
import type { TestCase } from '../../api/testCases'

const PRIORITY_COLOR: Record<string, string> = {
  P1: 'red', P2: 'orange', P3: 'blue', P4: 'default',
}

export default function TestCases() {
  const { appId } = useParams<{ appId: string }>()
  const { hasRole } = useAuth()
  const [filters, setFilters] = useState<{ priority?: string; category?: string }>({})
  const [search, setSearch] = useState('')
  const [drawerCase, setDrawerCase] = useState<TestCase | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()

  const { data, isLoading } = useTestCases(appId!, filters)
  const createMutation = useCreateTestCase(appId!)
  const deleteMutation = useDeleteTestCase(appId!)

  const displayed = (data?.items ?? []).filter((tc) =>
    tc.title.toLowerCase().includes(search.toLowerCase()),
  )

  const handleCreate = async (values: any) => {
    try {
      await createMutation.mutateAsync(values)
      message.success('用例创建成功')
      setCreateOpen(false)
      form.resetFields()
    } catch {
      message.error('创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id)
      message.success('删除成功')
    } catch {
      message.error('删除失败')
    }
  }

  const columns = [
    { title: '用例名称', dataIndex: 'title', key: 'title' },
    {
      title: '优先级', dataIndex: 'priority', key: 'priority',
      render: (v: string) => <Tag color={PRIORITY_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    {
      title: '分类', dataIndex: 'category', key: 'category',
      render: (v: string) => v ?? '-',
    },
    {
      title: '自动化', dataIndex: 'is_automated', key: 'is_automated',
      render: (v: boolean) => v ? <Tag color="success">是</Tag> : <Tag>否</Tag>,
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: TestCase) => (
        <Space>
          <Button type="link" size="small" onClick={() => setDrawerCase(record)}>查看</Button>
          {hasRole('admin', 'tester') && (
            <Button
              type="link" danger size="small"
              onClick={() =>
                Modal.confirm({ title: '确认删除？', onOk: () => handleDelete(record.id) })
              }
            >
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Breadcrumb
        items={[{ title: '应用列表' }, { title: '测试用例' }]}
        style={{ marginBottom: 12 }}
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={5} style={{ margin: 0 }}>测试用例</Typography.Title>
        {hasRole('admin', 'tester') && (
          <Button type="primary" size="small" onClick={() => setCreateOpen(true)}>+ 新建用例</Button>
        )}
      </div>

      <Space style={{ marginBottom: 12 }}>
        <Input.Search
          placeholder="搜索用例名称"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 220 }}
          allowClear
        />
        <Select
          placeholder="优先级"
          allowClear
          style={{ width: 100 }}
          options={['P1', 'P2', 'P3', 'P4'].map((v) => ({ label: v, value: v }))}
          onChange={(v) => setFilters((f) => ({ ...f, priority: v }))}
        />
        <Select
          placeholder="分类"
          allowClear
          style={{ width: 130 }}
          options={[
            { label: '功能测试', value: 'functional' },
            { label: '性能测试', value: 'performance' },
            { label: '接口测试', value: 'api' },
          ]}
          onChange={(v) => setFilters((f) => ({ ...f, category: v }))}
        />
      </Space>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={displayed}
        loading={isLoading}
        pagination={{ pageSize: 20, showTotal: (t) => `共 ${t} 条` }}
        size="small"
      />

      {/* 详情抽屉 */}
      <Drawer
        title={drawerCase?.title}
        open={!!drawerCase}
        onClose={() => setDrawerCase(null)}
        width={480}
      >
        {drawerCase && (
          <Descriptions column={1} size="small" bordered>
            <Descriptions.Item label="优先级">
              <Tag color={PRIORITY_COLOR[drawerCase.priority]}>{drawerCase.priority}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="分类">{drawerCase.category ?? '-'}</Descriptions.Item>
            <Descriptions.Item label="用例类型">{drawerCase.case_type}</Descriptions.Item>
            <Descriptions.Item label="自动化">
              {drawerCase.is_automated ? <Tag color="success">是</Tag> : <Tag>否</Tag>}
            </Descriptions.Item>
            <Descriptions.Item label="描述">{drawerCase.description ?? '-'}</Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {new Date(drawerCase.created_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>

      {/* 新建用例 Modal */}
      <Modal
        title="新建测试用例"
        open={createOpen}
        onCancel={() => { setCreateOpen(false); form.resetFields() }}
        onOk={form.submit}
        confirmLoading={createMutation.isPending}
        width={560}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="title" label="用例名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="priority" label="优先级" initialValue="P2">
            <Select options={[
              { label: 'P1 — 最高', value: 'P1' },
              { label: 'P2 — 高',   value: 'P2' },
              { label: 'P3 — 中',   value: 'P3' },
              { label: 'P4 — 低',   value: 'P4' },
            ]} />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Input placeholder="functional / performance / api ..." />
          </Form.Item>
          <Form.Item name="is_automated" label="是否自动化" initialValue={false}>
            <Select options={[{ label: '否', value: false }, { label: '是', value: true }]} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="expected_result" label="预期结果">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
