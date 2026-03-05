import { request } from './request'
import type { UUID } from './types'

// ============ 类型定义 ============

export interface ChatRequest {
  message: string
  actor_id?: UUID
  context?: Record<string, any>
}

export interface ChatResponse {
  response: string
  intent?: string
  entities?: Record<string, any>
  tasks_created?: Task[]
  confidence?: number
}

export interface RequestAIRequest {
  ai_agent_id: UUID
  task_type: string
  task_description: string
  context?: Record<string, any>
}

export interface RequestAIResponse {
  interaction_id: UUID
  status: string
  ai_response?: string
  created_at: string
}

export interface AIAgent {
  id: UUID
  display_name: string
  actor_type: 'ai_agent'
  capabilities: Record<string, number>
  ai_config: {
    model?: string
    temperature?: number
    system_prompt?: string
  }
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateAIAgentRequest {
  display_name: string
  capabilities?: Record<string, number>
  ai_config?: {
    model?: string
    temperature?: number
    system_prompt?: string
  }
}

export interface Task {
  id: UUID
  type: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: number
  assigned_to?: UUID[]
  created_at: string
  completed_at?: string
}

export interface Interaction {
  id: UUID
  interaction_type: string
  from_actor_id: UUID
  to_actor_id: UUID
  message: string
  ai_response?: string
  status: string
  created_at: string
}

// ============ API 函数 ============

/** 与核心AI对话 */
export function chatWithCentralAI(data: ChatRequest): Promise<ChatResponse> {
  return request.post('/chat', data)
}

/** 请求AI员工处理任务 */
export function requestAITask(data: RequestAIRequest): Promise<RequestAIResponse> {
  return request.post('/request-ai', data)
}

/** 请求任务 */
export function requestTask(data: {
  to_actor_id: UUID
  task_type: string
  task_description: string
}): Promise<Interaction> {
  return request.post('/request-task', data)
}

/** 获取交互历史 */
export function getInteractionHistory(actorId: UUID, limit?: number): Promise<Interaction[]> {
  return request.get(`/history/${actorId}`, { params: { limit } })
}

// ============ AI 员工管理 ============

/** 获取AI员工列表 */
export function getAIAgents(): Promise<AIAgent[]> {
  return request.get('/ai-agents')
}

/** 创建AI员工 */
export function createAIAgent(data: CreateAIAgentRequest): Promise<AIAgent> {
  return request.post('/ai-agents', data)
}

/** 更新AI员工 */
export function updateAIAgent(id: UUID, data: Partial<CreateAIAgentRequest>): Promise<AIAgent> {
  return request.post(`/ai-agents/${id}`, data)
}

/** 删除AI员工 */
export function deleteAIAgent(id: UUID): Promise<void> {
  return request.delete(`/ai-agents/${id}`)
}
