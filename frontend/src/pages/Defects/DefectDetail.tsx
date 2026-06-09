import { useState } from 'react'
import {
  Descriptions, Tag, Button, Space, Divider, Typography, List, Input, message,
  Modal, Form, Breadcrumb, Spin, Alert,
} from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { useDefect, useTransitionDefect, useAddComment } from '../../hooks/useDefects'
import { useAuth } from '../../context/AuthContext'

const SEVERITY_COLOR: Record<string, string> = {
  critical: 'red', high: 'orange', medium: 'blue', low: 'default',
}
const STATUS_COLOR: Record<string, string> = {
  new: 'processing', assigned: 'warning', fixed: 'cyan',
  verified: 'success', rejected: 'error', closed: 'default', reopened: 'volcano',
}

// 镜像自 app/defect/state_machine.py
const VALID_TRANSITIONS: Record<string, string[]> = {
  new:      ['assigned'],
  assigned: ['fixed', 'rejected'],
  fixed:    ['verified', 'reopened'],
  verified: ['closed'],
  rejected: [],
  closed:   ['reopened'],
  reopened: ['assigned'],
}

const ROLE_PERMISSIONS: Record<string, string[]> = {
  'new->assigned':      ['admin', 'tester'],
  'assigned->fixed':    ['developer'],
  'assigned->rejected': ['admin', 'tester'],
  'fixed->verified':    ['tester'],
  'fixed->reopened':    ['tester'],
  'verified->closed':   ['admin', 'tester'],
  'closed->reopened':   ['admin'],
  'reopened->assigned': ['admin', 'tester'],
}

function getAvailableTransitions(currentStatus: string, userRoles: string[]) {
  return (VALID_TRANSITIONS[currentStatus] ?? []).filter((next) => {
    const allowed = ROLE_PERMISSIONS[`${currentStatus}->${next}`] ?? []
    return userRoles.some((r) => allowed.includes(r))
  })
}

export default function DefectDetail() {
  const { appId, defectId } = useParams<{ appId: string; defectId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { data: defect, isLoading, error } = useDefect(defectId!)
  const transitionMutation = useTransitionDefect(defectId!)
  const addCommentMutation = useAddComment(defectId!)

  const [transitionTarget, setTransitionTarget] = useState<string | null>(null)
  const [commentText, setCommentText] = useState('')
  const [form] = Form.useForm()

  if (isLoading) return <Spin style={{ margin: 48 }} />
  if (error || !defect) return <Alert type="error" message="缺陷不存在或加载失败" />

  const availableTransitions = getAvailableTransitions(defect.status, user?.roles ?? [])

  const handleTransition = async (values: { comment?: string; assignee_id?: string }) => {
    if (!transitionTarget) return
    try {
      await transitionMutation.mutateAsync({ to_status: transitionTarget, ...values })
      message.success(`状态已更新为 ${transitionTarget}`)
      setTransitionTarget(null)
      form.resetFields()
    } catch {
      message.error('状态流转失败，请检查权限')
    }
  }

  const handleComment = async () => {
    if (!commentText.trim()) return
    try {
      await addCommentMutation.mutateAsync(commentText.trim())
      setCommentText('')
      message.success('评论已发布')
    } catch {
      message.error('评论失败')
    }
  }

  return (
    <div style={{ maxWidth: 800 }}>
      <Breadcrumb
        items={[
          { title: <a onClick={() => navigate(`/apps/${appId}/defects`)}>缺陷管理</a> },
          { title: defect.defect_no },
        ]}
        style={{ marginBottom: 12 }}
      />

      {/* 标题 + 状态 */}
      <Space align="center" style={{ marginBottom: 16 }}>
        <Typography.Title level={5} style={{ margin: 0 }}>
          {defect.defect_no} {defect.title}
        </Typography.Title>
        <Tag color={STATUS_COLOR[defect.status]}>{defect.status}</Tag>
      </Space>

      {/* 基本信息 */}
      <Descriptions bordered size="small" column={2} style={{ marginBottom: 16 }}>
        <Descriptions.Item label="严重度">
          <Tag color={SEVERITY_COLOR[defect.severity]}>{defect.severity}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="优先级">{defect.priority}</Descriptions.Item>
        <Descriptions.Item label="指派给">{defect.assignee_id ?? '未指派'}</Descriptions.Item>
        <Descriptions.Item label="发现版本">{defect.found_version_id}</Descriptions.Item>
        <Descriptions.Item label="来源">{defect.source}</Descriptions.Item>
        <Descriptions.Item label="创建时间">
          {new Date(defect.created_at).toLocaleString('zh-CN')}
        </Descriptions.Item>
        {defect.description && (
          <Descriptions.Item label="描述" span={2}>{defect.description}</Descriptions.Item>
        )}
        {/* @ts-expect-error — steps_to_reproduce not in type but returned by API */}
        {(defect as any).steps_to_reproduce && (
          <Descriptions.Item label="复现步骤" span={2}>
            {(defect as any).steps_to_reproduce}
          </Descriptions.Item>
        )}
      </Descriptions>

      {/* 状态流转 */}
      {availableTransitions.length > 0 && (
        <>
          <Divider orientation="left" plain>状态流转</Divider>
          <Space style={{ marginBottom: 16 }}>
            {availableTransitions.map((next) => (
              <Button key={next} size="small" onClick={() => setTransitionTarget(next)}>
                → {next}
              </Button>
            ))}
          </Space>
        </>
      )}

      {/* 评论区 */}
      <Divider orientation="left" plain>评论</Divider>
      <List
        dataSource={defect.comments}
        locale={{ emptyText: '暂无评论' }}
        renderItem={(c) => (
          <List.Item key={c.id}>
            <List.Item.Meta
              title={
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {c.author_id}
                </Typography.Text>
              }
              description={c.content}
            />
            <Typography.Text type="secondary" style={{ fontSize: 11 }}>
              {new Date(c.created_at).toLocaleString('zh-CN')}
            </Typography.Text>
          </List.Item>
        )}
      />
      <Space.Compact style={{ width: '100%', marginTop: 12 }}>
        <Input
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          placeholder="添加评论..."
          onPressEnter={handleComment}
        />
        <Button type="primary" onClick={handleComment} loading={addCommentMutation.isPending}>
          发布
        </Button>
      </Space.Compact>

      {/* 流转确认 Modal */}
      <Modal
        title={`确认流转：${defect.status} → ${transitionTarget}`}
        open={!!transitionTarget}
        onCancel={() => { setTransitionTarget(null); form.resetFields() }}
        onOk={form.submit}
        confirmLoading={transitionMutation.isPending}
      >
        <Form form={form} onFinish={handleTransition} layout="vertical">
          {transitionTarget === 'assigned' && (
            <Form.Item name="assignee_id" label="指派给（用户 ID）">
              <Input placeholder="输入被指派人的 UUID" />
            </Form.Item>
          )}
          <Form.Item name="comment" label="备注（可选）">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
