import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { say, ask, getMySummary } from '@/api'
import type { SayResponse, AskResponse } from '@/api'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  intent?: string
  entities?: Record<string, any>
  contribution?: Record<string, any>
  tasks?: Array<Record<string, any>>
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const currentActorId = ref<string | null>(null)
  
  // 统计信息
  const stats = ref({
    contributions: { total: 0, pending: 0, verified: 0 },
    rewards: { total: 0, pending: 0, paid: 0 },
    tasks: { pending: 0, in_progress: 0, completed: 0 }
  })

  // 发送消息 - 使用统一输入接口
  const sendMessage = async (message: string) => {
    // 添加用户消息
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date()
    }
    messages.value.push(userMsg)

    loading.value = true
    try {
      const response: SayResponse = await say({
        message,
        actor_id: currentActorId.value || undefined
      })

      // 构建AI回复内容
      let replyContent = response.message
      
      // 如果有贡献信息，添加到回复
      if (response.contribution?.estimated_value) {
        replyContent += `\n\n📊 **预估贡献值**: +${response.contribution.estimated_value}`
      }
      
      // 如果创建了任务，添加到回复
      if (response.tasks_created && response.tasks_created.length > 0) {
        replyContent += `\n\n📋 **创建任务**: ${response.tasks_created.length}个`
      }

      // 添加AI回复
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: replyContent,
        timestamp: new Date(),
        intent: response.understood?.intent,
        entities: response.understood?.entities,
        contribution: response.contribution,
        tasks: response.tasks_created
      }
      messages.value.push(assistantMsg)

      return response
    } catch (error: any) {
      // 添加错误消息
      messages.value.push({
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `❌ 处理失败: ${error.message || '请稍后重试'}`,
        timestamp: new Date()
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  // 自然语言查询
  const query = async (question: string) => {
    const userMsg: ChatMessage = {
      id: `query-${Date.now()}`,
      role: 'user',
      content: `🔍 ${question}`,
      timestamp: new Date()
    }
    messages.value.push(userMsg)

    loading.value = true
    try {
      const response: AskResponse = await ask(question, currentActorId.value || undefined)
      
      messages.value.push({
        id: `answer-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date()
      })

      return response
    } catch (error: any) {
      messages.value.push({
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `❌ 查询失败: ${error.message || '请稍后重试'}`,
        timestamp: new Date()
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取统计信息
  const fetchStats = async () => {
    try {
      const summary = await getMySummary()
      stats.value = summary
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  // 清空消息
  const clearMessages = () => {
    messages.value = []
  }

  // 设置当前 Actor
  const setCurrentActor = (actorId: string | null) => {
    currentActorId.value = actorId
  }

  return {
    messages,
    loading,
    currentActorId,
    stats,
    sendMessage,
    query,
    fetchStats,
    clearMessages,
    setCurrentActor
  }
})
