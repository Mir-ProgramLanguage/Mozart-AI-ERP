import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatWithCentralAI, requestAITask } from '@/api'
import type { ChatRequest, ChatResponse, RequestAIRequest } from '@/api'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Array<{ role: 'user' | 'assistant'; content: string; timestamp: Date }>>([])
  const loading = ref(false)
  const currentActorId = ref<string | null>(null)

  const sendMessage = async (message: string) => {
    // 添加用户消息
    messages.value.push({
      role: 'user',
      content: message,
      timestamp: new Date()
    })

    loading.value = true
    try {
      const request: ChatRequest = {
        message,
        actor_id: currentActorId.value || undefined
      }
      
      const response: ChatResponse = await chatWithCentralAI(request)
      
      // 添加AI回复
      messages.value.push({
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      })

      return response
    } catch (error) {
      messages.value.push({
        role: 'assistant',
        content: '抱歉，处理您的请求时出现了错误。',
        timestamp: new Date()
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const requestAI = async (data: RequestAIRequest) => {
    loading.value = true
    try {
      const response = await requestAITask(data)
      messages.value.push({
        role: 'assistant',
        content: `已创建AI任务，ID: ${response.interaction_id}`,
        timestamp: new Date()
      })
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    loading,
    currentActorId,
    sendMessage,
    requestAI,
    clearMessages
  }
})
