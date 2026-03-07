import { request } from './request'
import type { UUID } from './types'

// ============ 类型定义 ============

export interface Actor {
  id: UUID
  display_name: string
  actor_type: 'human' | 'ai_agent'
  capabilities: Record<string, number>
  capability_history: Array<{
    capability: string
    old_value: number
    new_value: number
    changed_at: string
  }>
  trust_score: number
  reputation_score: number
  total_contributions: number
  total_rewards: number
  current_tasks: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Task {
  id: UUID
  type: string
  title: string
  description: string
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'verified' | 'cancelled'
  priority: number
  required_capabilities: Record<string, number>
  assigned_to?: UUID[]
  assigned_actors?: Actor[]
  created_by: UUID
  created_at: string
  started_at?: string
  completed_at?: string
  verified_at?: string
  contribution_value?: number
}

export interface Contribution {
  id: UUID
  actor_id: UUID
  contribution_type: string
  content: string
  details: Record<string, any>
  contribution_value: number
  actual_value?: number
  confidence: number
  risk_level: string
  status: 'pending' | 'verified' | 'rejected'
  created_at: string
  verified_at?: string
}

export interface Reward {
  id: UUID
  actor_id: UUID
  contribution_id?: UUID
  reward_type: 'cash' | 'profit_share' | 'options' | 'skill_point'
  amount: number
  status: 'pending' | 'paid' | 'cancelled'
  created_at: string
  paid_at?: string
}

export interface SayRequest {
  message: string
  actor_id?: string
  attachments?: string[]
}

export interface SayResponse {
  status: string
  event_id?: string
  understood: {
    intent: string
    sub_intent?: string
    entities: any[]
    confidence: number
    reasoning?: string
  }
  contribution?: {
    type: string
    estimated_value: number
  }
  tasks_created: any[]
  message: string
}

export interface AskResponse {
  answer: string
  data?: Record<string, any>
  sources?: Array<{ id: UUID; content: string }>
}

export interface SearchResult {
  events: Contribution[]
  total: number
}

export interface AskRequest {
  actor_id: string
  question: string
  context?: Record<string, any>
}

export interface AskResponse {
  question: string
  intent?: string
  answer: string
  confidence?: number
  data?: Record<string, any>
  sources?: Array<Record<string, any>>
}

// ============ 统一接口 ============

/** 用户发言 - 统一输入接口 */
export async function say(data: SayRequest): Promise<SayResponse> {
  // 使用默认 actor_id 如果没有提供
  const payload = {
    actor_id: data.actor_id || '00000000-0000-0000-0000-000000000001',
    message: data.message,
    attachments: data.attachments || []
  }
  return request.post('/say', payload)
}

/** 自然语言查询 */
export function ask(question: string, actorId?: string): Promise<AskResponse> {
  return request.post('/ask', {
    actor_id: actorId || '00000000-0000-0000-0000-000000000001',
    question
  })
}

/** 获取我的概览 */
export function getMySummary(): Promise<{
  contributions: { total: number; pending: number; verified: number }
  rewards: { total: number; pending: number; paid: number }
  tasks: { pending: number; in_progress: number; completed: number }
  capabilities: Record<string, number>
}> {
  return request.get('/my/summary')
}

// ============ Actor 管理 ============

/** 获取 Actor 列表 */
export function getActors(params?: {
  actor_type?: string
  is_active?: boolean
  skip?: number
  limit?: number
}): Promise<{ items: Actor[]; total: number }> {
  return request.get('/actors', { params })
}

/** 获取 Actor 详情 */
export function getActor(id: UUID): Promise<Actor> {
  return request.get(`/actors/${id}`)
}

/** 创建 Actor */
export function createActor(data: {
  display_name: string
  actor_type?: string
  capabilities?: Record<string, number>
  ai_config?: Record<string, any>
}): Promise<Actor> {
  return request.post('/actors', data)
}

/** 更新 Actor */
export function updateActor(id: UUID, data: Partial<{
  display_name: string
  capabilities: Record<string, number>
  is_active: boolean
}>): Promise<Actor> {
  return request.put(`/actors/${id}`, data)
}

/** 获取 Actor 能力图谱 */
export function getActorCapabilities(id: UUID): Promise<{
  capabilities: Record<string, number>
  growth_history: Array<{ capability: string; growth: number; date: string }>
}> {
  return request.get(`/actors/${id}/capabilities`)
}

/** Actor 能力成长 */
export function growActorCapability(id: UUID, data: {
  capability: string
  value: number
  source: string
}): Promise<Actor> {
  return request.post(`/actors/${id}/grow`, data)
}

/** 更新 Actor 信任分数 */
export function updateActorTrust(id: UUID, data: {
  success: boolean
  reason?: string
}): Promise<Actor> {
  return request.post(`/actors/${id}/trust`, data)
}

/** 获取排行榜 */
export function getLeaderboard(type: 'contribution' | 'reputation' = 'contribution', limit = 10): Promise<Array<{
  actor: Actor
  value: number
  rank: number
}>> {
  return request.get('/actors/leaderboard', { params: { type, limit } })
}

// ============ 任务管理 ============

/** 获取任务列表 */
export function getTasks(params?: {
  status?: string
  type?: string
  assigned_to?: UUID
  skip?: number
  limit?: number
}): Promise<{ items: Task[]; total: number }> {
  return request.get('/tasks', { params })
}

/** 获取任务详情 */
export function getTask(id: UUID): Promise<Task> {
  return request.get(`/tasks/${id}`)
}

/** 创建任务 */
export function createTask(data: {
  type: string
  title: string
  description: string
  priority?: number
  required_capabilities?: Record<string, number>
  assigned_to?: UUID[]
}): Promise<Task> {
  return request.post('/tasks', data)
}

/** 分配任务 */
export function assignTask(id: UUID, actorIds: UUID[]): Promise<Task> {
  return request.post(`/tasks/${id}/assign`, { actor_ids: actorIds })
}

/** 自动分配任务 */
export function autoAssignTask(id: UUID): Promise<Task> {
  return request.post(`/tasks/${id}/auto-assign`)
}

/** 开始任务 */
export function startTask(id: UUID): Promise<Task> {
  return request.post(`/tasks/${id}/start`)
}

/** 完成任务 */
export function completeTask(id: UUID, data?: {
  result?: string
  actual_value?: number
}): Promise<Task> {
  return request.post(`/tasks/${id}/complete`, data)
}

/** 验证任务 */
export function verifyTask(id: UUID, data: {
  approved: boolean
  feedback?: string
}): Promise<Task> {
  return request.post(`/tasks/${id}/verify`, data)
}

/** 获取可领取任务 */
export function getAvailableTasks(): Promise<Task[]> {
  return request.get('/tasks/available')
}

/** 获取我的任务 */
export function getMyTasks(): Promise<Task[]> {
  return request.get('/tasks/my')
}

// ============ 贡献管理 ============

/** 获取贡献列表 */
export function getContributions(params?: {
  actor_id?: UUID
  status?: string
  contribution_type?: string
  skip?: number
  limit?: number
}): Promise<{ items: Contribution[]; total: number }> {
  return request.get('/contributions', { params })
}

/** 获取贡献详情 */
export function getContribution(id: UUID): Promise<Contribution> {
  return request.get(`/contributions/${id}`)
}

/** 提交贡献 */
export function createContribution(data: {
  contribution_type: string
  content: string
  details?: Record<string, any>
}): Promise<Contribution> {
  return request.post('/contributions', data)
}

/** 验证贡献 */
export function verifyContribution(id: UUID, data: {
  approved: boolean
  actual_value?: number
  feedback?: string
}): Promise<Contribution> {
  return request.post(`/contributions/${id}/verify`, data)
}

/** 获取我的贡献 */
export function getMyContributions(): Promise<Contribution[]> {
  return request.get('/my/contributions')
}

// ============ 回报管理 ============

/** 获取回报列表 */
export function getRewards(params?: {
  actor_id?: UUID
  status?: string
  skip?: number
  limit?: number
}): Promise<{ items: Reward[]; total: number }> {
  return request.get('/rewards', { params })
}

/** 获取我的回报 */
export function getMyRewards(): Promise<Reward[]> {
  return request.get('/my/rewards')
}

/** 兑现回报 */
export function redeemReward(id: UUID): Promise<Reward> {
  return request.post(`/rewards/${id}/redeem`)
}

// ============ 语义搜索 ============

/** 语义搜索 */
export function semanticSearch(data: {
  query: string
  limit?: number
  filters?: Record<string, any>
}): Promise<SearchResult> {
  return request.post('/search', data)
}

/** 查找相似事件 */
export function findSimilarEvents(eventId: UUID, limit = 5): Promise<Contribution[]> {
  return request.get(`/search/similar/${eventId}`, { params: { limit } })
}

/** 搜索建议 */
export function getSearchSuggestions(query: string): Promise<string[]> {
  return request.get('/search/suggest', { params: { query } })
}

// ============ AI 对话 (兼容旧接口) ============

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

/** 与核心 AI 对话 */
export function chat(data: ChatRequest): Promise<ChatResponse> {
  return request.post('/chat', data)
}

// ============ AI 员工管理 (兼容旧接口) ============

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

export function getAIAgents(): Promise<AIAgent[]> {
  return request.get('/ai-agents')
}

export function createAIAgent(data: {
  display_name: string
  capabilities?: Record<string, number>
  ai_config?: Record<string, any>
}): Promise<AIAgent> {
  return request.post('/ai-agents', data)
}

export function updateAIAgent(id: UUID, data: Record<string, any>): Promise<AIAgent> {
  return request.put(`/ai-agents/${id}`, data)
}

export function deleteAIAgent(id: UUID): Promise<void> {
  return request.delete(`/ai-agents/${id}`)
}

// ============ 数据导出 ============

export interface ExportParams {
  data_type: 'contributions' | 'rewards' | 'actors' | 'tasks'
  format: 'csv' | 'excel' | 'json'
  start_date?: string
  end_date?: string
  status?: string
  actor_id?: string
}

/** 导出数据 */
export async function exportData(params: ExportParams): Promise<void> {
  const queryParams = new URLSearchParams()
  queryParams.append('format', params.format)
  if (params.start_date) queryParams.append('start_date', params.start_date)
  if (params.end_date) queryParams.append('end_date', params.end_date)
  if (params.status) queryParams.append('status', params.status)
  if (params.actor_id) queryParams.append('actor_id', params.actor_id)
  
  const url = `${request.defaults.baseURL}/export/${params.data_type}?${queryParams.toString()}`
  
  // 创建一个隐藏的a标签来触发下载
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', '')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/** 导出贡献记录 */
export function exportContributions(format: 'csv' | 'excel' | 'json' = 'csv', params?: {
  start_date?: string
  end_date?: string
  status?: string
  actor_id?: string
}): Promise<void> {
  return exportData({ ...params, data_type: 'contributions', format })
}

/** 导出回报记录 */
export function exportRewards(format: 'csv' | 'excel' | 'json' = 'csv', params?: {
  start_date?: string
  end_date?: string
  status?: string
  actor_id?: string
}): Promise<void> {
  return exportData({ ...params, data_type: 'rewards', format })
}

/** 导出Actor数据 */
export function exportActors(format: 'csv' | 'excel' | 'json' = 'csv', actor_type?: string): Promise<void> {
  return exportData({ data_type: 'actors', format, status: actor_type })
}

/** 导出任务数据 */
export function exportTasks(format: 'csv' | 'excel' | 'json' = 'csv', params?: {
  start_date?: string
  end_date?: string
  status?: string
}): Promise<void> {
  return exportData({ ...params, data_type: 'tasks', format })
}
