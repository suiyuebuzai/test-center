import { useState } from 'react'
import {
  Table, Button, Select, Tag, Space, Typography, Modal, Form, Input, message, Breadcrumb,
} from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { useDefects, useCreateDefect } from '../../hooks/useDefects'
import { useVersions } from '../../hooks/useApps'
import { useAuth } from '../../context/AuthContext'
import type { DefectSummary, DefectCreate } from '../../api/defects'

const SEVERITY_COLOR: Record<string, string> = {
  critical: 'red', high: 'orange', medium: 'blue', low: 'default',
}
const STATUS_COLOR: Record<string, string> = {
  new: 'processing', assigned: 'warning', fixed: 'cyan',
  verified: 'success', rejected: 'error', closed: 'default', reopened: 'volcano',
}

export default function DefectList() {
  const { appId } = useParams<{ appId: string }>()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const [filters, setFilters] = useState<{ status?: string; severity?: string }>({})
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()

  const { data, isLoading } = useDefects(appId!, filters)
  const { data: versions } = useVersions(appId!)
  const createMutation = useCreateDefect(appId!)

  const handleCreate = async (values: DefectCreate) => {
    try {
      await createMutation.mutateAsync(values)
      message.success('缺陷已提交')
      setCreateOpen(false)
      form.resetFields()
    } catch {
      message.error('提交失败')
    }
  }

  const columns = [
    {
      title: '编号', dataIndex: 'defect_no', key: 'defect_no', width: 90,
      render: (v: string, r: DefectSummary) => (
        <Button type="link" size="small" onClick={() => navigate(`/apps/${appId}/defects/${r.id}`)}>
          {v}
        </Button>
      ),
    },
    { title: '标题', dataIndex: 'title', key: 'title' },
    {
      title: '严重度', dataIndex: 'severity', key: 'severity', width: 90,
      render: (v: string) => <Tag color={SEVERITY_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (v: string) => <Tag color={STATUS_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    {
      title: '操作', key: 'action', width: 70,
      render: (_: any, r: DefectSummary) => (
        <Button type="link" size="small" onClick={() => navigate(`/apps/${appId}/defects/${r.id}`)}>
          查看
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Breadcrumb
        items={[{ title: '应用列表' }, { title: '缺陷管理' }]}
        style={{ marginBottom: 12 }}
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={5} style={{ margin: 0 }}>缺陷管理</Typography.Title>
        {hasRole('admin', 'tester') && (
          <Button type="primary" size="small" onClick={() => setCreateOpen(true)}>+ 提缺陷</Button>
        )}
      </div>

      <Space style={{ marginBottom: 12 }}>
        <Select
          placeholder="状态"
          allowClear
          style={{ width: 110 }}
          options={['new', 'assigned', 'fixed', 'verified', 'rejected', 'closed', 'reopened'].map(
            (s) => ({ label: s, value: s }),
          )}
          onChange={(v) => setFilters((f) => ({ ...f, status: v }))}
        />
        <Select
          placeholder="严重度"
          allowClear
          style={{ width: 100 }}
          options={['critical', 'high', 'medium', 'low'].map((s) => ({ label: s, value: s }))}
          onChange={(v) => setFilters((f) => ({ ...f, severity: v }))}
        />
      </Space>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data?.items ?? []}
        loading={isLoading}
        pagination={{ pageSize: 20, showTotal: (t) => `共 ${t} 条` }}
        size="small"
      />

      {/* 提缺陷 Modal */}
      <Modal
        title="提交缺陷"
        open={createOpen}
        onCancel={() => { setCreateOpen(false); form.resetFields() }}
        onOk={form.submit}
        confirmLoading={createMutation.isPending}
        width={580}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="title" label="缺陷标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="found_version_id" label="发现版本" rules={[{ required: true }]}>
            <Select
              options={(versions ?? []).map((v) => ({ label: v.name, value: v.id }))}
              placeholder="选择版本"
            />
          </Form.Item>
          <Form.Item name="severity" label="严重度" initialValue="medium">
            <Select options={[
              { label: '严重 critical', value: 'critical' },
              { label: '高 high',       value: 'high' },
              { label: '中 medium',     value: 'medium' },
              { label: '低 low',        value: 'low' },
            ]} />
          </Form.Item>
          <Form.Item name="description" label="问题描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="steps_to_reproduce" label="复现步骤">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="actual_result" label="实际结果">
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
