import { useState } from 'react'
import {
  Table, Button, Tag, Typography, Modal, Form, Select, Input,
  DatePicker, message, Breadcrumb, Descriptions, Spin, Alert, Divider,
} from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { useTestTask, useExecutions, useCreateExecution } from '../../hooks/useTestTasks'
import { useAuth } from '../../context/AuthContext'
import type { TaskExecution } from '../../api/testTasks'
import dayjs from 'dayjs'

const RESULT_COLOR: Record<string, string> = {
  pass: 'success', fail: 'error', skip: 'warning', blocked: 'default',
}

const STATUS_COLOR: Record<string, string> = {
  pending: 'default', in_progress: 'processing', completed: 'success', cancelled: 'error',
}

export default function TestTaskDetail() {
  const { appId, taskId } = useParams<{ appId: string; taskId: string }>()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()

  const { data: task, isLoading: taskLoading, error } = useTestTask(taskId!)
  const { data: executions, isLoading: execLoading } = useExecutions(taskId!)
  const createMutation = useCreateExecution(taskId!)

  const handleCreate = async (values: any) => {
    try {
      const payload = {
        ...values,
        executed_at: (values.executed_at ?? dayjs()).toISOString(),
      }
      await createMutation.mutateAsync(payload)
      message.success('执行记录已添加')
      setCreateOpen(false)
      form.resetFields()
    } catch {
      message.error('添加失败')
    }
  }

  if (taskLoading) return <Spin style={{ margin: 48 }} />
  if (error || !task) return <Alert type="error" message="任务不存在或加载失败" />

  const columns = [
    {
      title: '用例 ID', dataIndex: 'test_case_id', key: 'test_case_id',
      render: (v: string) => <Typography.Text code>{v.slice(0, 8)}…</Typography.Text>,
    },
    {
      title: '结果', dataIndex: 'result', key: 'result', width: 90,
      render: (v: string) => <Tag color={RESULT_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    {
      title: '实际结果', dataIndex: 'actual_result', key: 'actual_result',
      render: (v: string | null) => v ?? '-',
    },
    {
      title: '执行时间', dataIndex: 'executed_at', key: 'executed_at', width: 160,
      render: (v: string) => new Date(v).toLocaleString('zh-CN'),
    },
  ]

  return (
    <div style={{ maxWidth: 860 }}>
      <Breadcrumb
        items={[
          { title: <a onClick={() => navigate(`/apps/${appId}/test-tasks`)}>测试任务</a> },
          { title: task.name },
        ]}
        style={{ marginBottom: 12 }}
      />

      <Descriptions bordered size="small" column={2} style={{ marginBottom: 20 }}>
        <Descriptions.Item label="任务名称" span={2}>
          <Typography.Text strong>{task.name}</Typography.Text>
        </Descriptions.Item>
        <Descriptions.Item label="状态">
          <Tag color={STATUS_COLOR[task.status] ?? 'default'}>{task.status}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="创建时间">
          {new Date(task.created_at).toLocaleString('zh-CN')}
        </Descriptions.Item>
      </Descriptions>

      <Divider orientation="left" plain>执行记录</Divider>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
        {hasRole('admin', 'tester') && (
          <Button type="primary" size="small" onClick={() => setCreateOpen(true)}>+ 添加执行记录</Button>
        )}
      </div>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={executions ?? []}
        loading={execLoading}
        pagination={{ pageSize: 20, showTotal: (t) => `共 ${t} 条` }}
        size="small"
        locale={{ emptyText: '暂无执行记录' }}
      />

      <Modal
        title="添加执行记录"
        open={createOpen}
        onCancel={() => { setCreateOpen(false); form.resetFields() }}
        onOk={form.submit}
        confirmLoading={createMutation.isPending}
        width={480}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="test_case_id" label="用例 ID" rules={[{ required: true }]}>
            <Input placeholder="输入测试用例的 UUID" />
          </Form.Item>
          <Form.Item name="result" label="执行结果" rules={[{ required: true }]} initialValue="pass">
            <Select options={[
              { label: '通过 pass',   value: 'pass' },
              { label: '失败 fail',   value: 'fail' },
              { label: '跳过 skip',   value: 'skip' },
              { label: '阻塞 blocked', value: 'blocked' },
            ]} />
          </Form.Item>
          <Form.Item name="actual_result" label="实际结果">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="executed_at" label="执行时间" initialValue={dayjs()}>
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="duration_seconds" label="耗时（秒）">
            <Input type="number" min={0} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
