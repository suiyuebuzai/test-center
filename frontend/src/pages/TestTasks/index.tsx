import { useState } from 'react'
import {
  Table, Button, Tag, Typography, Modal, Form, Input, Select, DatePicker,
  Space, message, Breadcrumb, Spin,
} from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { useTestTasks, useCreateTestTask } from '../../hooks/useTestTasks'
import { useVersions } from '../../hooks/useApps'
import { useAuth } from '../../context/AuthContext'
import type { TestTask } from '../../api/testTasks'

const STATUS_COLOR: Record<string, string> = {
  pending: 'default', in_progress: 'processing', completed: 'success', cancelled: 'error',
}

export default function TestTaskList() {
  const { appId } = useParams<{ appId: string }>()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()

  const { data: tasks, isLoading } = useTestTasks(appId!)
  const { data: versions } = useVersions(appId!)
  const createMutation = useCreateTestTask(appId!)

  const handleCreate = async (values: any) => {
    try {
      const payload = {
        ...values,
        start_date: values.start_date?.format('YYYY-MM-DD'),
        due_date: values.due_date?.format('YYYY-MM-DD'),
      }
      await createMutation.mutateAsync(payload)
      message.success('测试任务已创建')
      setCreateOpen(false)
      form.resetFields()
    } catch {
      message.error('创建失败')
    }
  }

  const columns = [
    {
      title: '任务名称', dataIndex: 'name', key: 'name',
      render: (v: string, r: TestTask) => (
        <Button type="link" size="small" onClick={() => navigate(`/apps/${appId}/test-tasks/${r.id}`)}>
          {v}
        </Button>
      ),
    },
    {
      title: '版本', dataIndex: 'version_id', key: 'version_id',
      render: (id: string) => {
        const v = versions?.find((v) => v.id === id)
        return v ? v.name : <Typography.Text type="secondary">{id.slice(0, 8)}…</Typography.Text>
      },
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (v: string) => <Tag color={STATUS_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    {
      title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 160,
      render: (v: string) => new Date(v).toLocaleString('zh-CN'),
    },
    {
      title: '操作', key: 'action', width: 70,
      render: (_: any, r: TestTask) => (
        <Button type="link" size="small" onClick={() => navigate(`/apps/${appId}/test-tasks/${r.id}`)}>
          查看
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Breadcrumb
        items={[{ title: '应用列表' }, { title: '测试任务' }]}
        style={{ marginBottom: 12 }}
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={5} style={{ margin: 0 }}>测试任务</Typography.Title>
        {hasRole('admin', 'tester') && (
          <Button type="primary" size="small" onClick={() => setCreateOpen(true)}>+ 新建任务</Button>
        )}
      </div>

      {isLoading ? (
        <Spin />
      ) : (
        <Table
          rowKey="id"
          columns={columns}
          dataSource={tasks ?? []}
          pagination={{ pageSize: 20, showTotal: (t) => `共 ${t} 条` }}
          size="small"
        />
      )}

      <Modal
        title="新建测试任务"
        open={createOpen}
        onCancel={() => { setCreateOpen(false); form.resetFields() }}
        onOk={form.submit}
        confirmLoading={createMutation.isPending}
        width={520}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="任务名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="version_id" label="测试版本" rules={[{ required: true }]}>
            <Select
              options={(versions ?? []).map((v) => ({ label: v.name, value: v.id }))}
              placeholder="选择版本"
            />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Space style={{ width: '100%' }}>
            <Form.Item name="start_date" label="开始日期" style={{ marginBottom: 0 }}>
              <DatePicker />
            </Form.Item>
            <Form.Item name="due_date" label="截止日期" style={{ marginBottom: 0 }}>
              <DatePicker />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  )
}
